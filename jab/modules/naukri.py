import time
import re
import numpy as np
import nltk 
import time
import json
from urllib.parse import urlparse, urlunparse
from playwright.sync_api import sync_playwright , expect
import tensorflow as tf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from .answer_utils import (
    find_preferred_notice_option,
    is_career_break_prompt,
    is_notice_period_prompt,
    preferred_notice_period_text,
)

NLTK_RESOURCES = {
    "tokenizers/punkt": "punkt",
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/wordnet": "wordnet",
    "corpora/omw-1.4": "omw-1.4",
}


def ensure_nltk_data():
    for resource_path, package_name in NLTK_RESOURCES.items():
        try:
            nltk.data.find(resource_path)
        except LookupError:
            nltk.download(package_name, quiet=True)


class ChatbotModel():
    def __init__(self, user_data):
        ensure_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.ignore_words = ['?', '!', '.', ',']
        self.user_data = user_data
        self.words = []
        self.classes = []
        self.load_data()
        self.load_model()

    def load_data(self):
        for intent in self.user_data:
            for pattern in intent['patterns']:
                word_list = nltk.word_tokenize(pattern)
                self.words.extend(word_list)
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])
        self.words = sorted(set([self.lemmatizer.lemmatize(w.lower()) for w in self.words if w not in self.ignore_words]))
        self.classes = sorted(set(self.classes))
    
    def load_model(self):
        model_path = f"./jab/data/{user}/model.keras"
        self.model = tf.keras.models.load_model(model_path)

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [self.lemmatizer.lemmatize(word.lower()) for word in sentence_words]
        return sentence_words

    def bow(self, sentence, show_details=True):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        for s in sentence_words:
            for i, w in enumerate(self.words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        print("found in bag: %s" % w)
        return np.array(bag)

    def predict_class(self, sentence):
        p = self.bow(sentence, show_details=False)
        res = self.model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return_list = []
        for r in results:
            return_list.append({"intent": self.classes[r[0]], "probability": str(r[1])})
        return return_list

    def get_response(self, ints):
        tag = ints[0]['intent']
        for intent in self.user_data:
            if intent['tag'] == tag:
                result = intent['answer']
                break
        res = lambda y: y if y not in " " else "3"
        return res(result)

    def chatbot_response(self, msg):
        try:
            ints = self.predict_class(msg)
            res = self.get_response(ints)
        except:
            res = '3'
        return res

class ChatbotAgent:
    def __init__(self,page,username):
        global user
        user = username
        self.page = page
        with open(f"./jab/data/{user}/training_data.json", 'r') as json_file:
            user_data = json.load(json_file)    
        self.model = ChatbotModel(user_data)
        self.analyzer = SentimentIntensityAnalyzer()

    def sentiment_score(self,text):
        score = self.analyzer.polarity_scores(text)
        return score['compound'] 
    
    def match_by_sentiment(self,target, strings):
        target_sentiment = self.sentiment_score(target)
        sentiment_diffs = []
        for string in strings:
            string_sentiment = self.sentiment_score(string)
            diff = abs(target_sentiment - string_sentiment)
            sentiment_diffs.append((string, diff))
        
        best_match = min(sentiment_diffs, key=lambda x: x[1])
        return best_match[0], best_match[1]

    def _extract_first_number(self, text):
        if text is None:
            return None
        m = re.search(r"\d+(?:\.\d+)?", str(text))
        return float(m.group()) if m else None

    def _match_option_by_answer(self, answer, options):
        answer_text = str(answer or "").strip().lower()
        answer_num = self._extract_first_number(answer_text)
        if not options:
            return None

        if answer_num is not None:
            exact_candidates = []
            for option in options:
                label = option["label"].lower()
                label_numbers = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", label)]
                if label_numbers and answer_num in label_numbers:
                    exact_candidates.append(option)
            if exact_candidates:
                exact_candidates.sort(key=lambda x: len(x["label"]))
                return exact_candidates[0]["id"]

            for option in options:
                label = option["label"].lower()
                range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)", label)
                if range_match:
                    start = float(range_match.group(1))
                    end = float(range_match.group(2))
                    if start <= answer_num <= end:
                        return option["id"]

            plus_matches = []
            for option in options:
                label = option["label"].lower()
                plus_match = re.search(r"(\d+(?:\.\d+)?)\s*\+", label)
                if plus_match:
                    threshold = float(plus_match.group(1))
                    if answer_num >= threshold:
                        plus_matches.append((threshold, option["id"]))
            if plus_matches:
                plus_matches.sort(key=lambda x: x[0], reverse=True)
                return plus_matches[0][1]

        for option in options:
            label = option["label"].lower()
            if answer_text and answer_text in label:
                return option["id"]
        return None

    def _is_previous_employee_question(self, question):
        normalized = " ".join(str(question or "").lower().split())
        return (
            "previous employee" in normalized
            and "intern" in normalized
            and "contractor" in normalized
        )

    def _override_answer(self, question, answer):
        normalized = " ".join(str(question or "").lower().split())
        if is_notice_period_prompt(question):
            return preferred_notice_period_text()
        if is_career_break_prompt(question):
            return "No"
        if normalized.startswith("how many years of experience"):
            return "3"
        if self._is_previous_employee_question(question):
            return "No"
        return answer

    def classify_new_question(self):
        page=self.page
        cbcn = page.wait_for_selector(".chatbot_MessageContainer",timeout = 3000)
        time.sleep(2)
        try:
            while cbcn:
                question_element = page.locator(".botMsg").last
                self.page.wait_for_timeout(1000)
                
                print("New question appeared:", question_element.inner_text())
                question = question_element.inner_text()
                answer = self.model.chatbot_response(question)
                answer = self._override_answer(question, answer)
                print('answer',answer)

                checkboxes = cbcn.query_selector_all('input[type="checkbox"]')
                radio_buttons = cbcn.query_selector_all('input[type="radio"]')
                text_input = page.locator('.chatbot_MessageContainer .textArea')
                chip = page.query_selector('.chatbot_MessageContainer .chipsContainer .chatbot_Chip')
                suggs = cbcn.query_selector_all('.ssc__heading')
                dob = cbcn.query_selector(".dob__container")
                if chip:
                    print("skipping")
                    chip.click()
                    continue
                elif radio_buttons or checkboxes:
                    _buttons = radio_buttons or checkboxes
                    print("The new question requires a radio button selection.")
                    options = []
                    for el in _buttons:
                        option_id = el.evaluate("el => el.id")
                        label_text = ""
                        if option_id:
                            label_locator = page.locator(f'label[for="{option_id}"]')
                            if label_locator.count() > 0:
                                label_text = label_locator.first.inner_text().strip()
                        if not label_text:
                            label_text = el.evaluate("el => el.value || el.getAttribute('aria-label') || el.id || ''").strip()
                        options.append({"id": option_id, "label": label_text, "el": el})
                    print("Options:", [opt["label"] for opt in options])
                    selected_option = None
                    if is_notice_period_prompt(question):
                        selected_option = find_preferred_notice_option(options, label_getter=lambda option: option["label"])
                    finnas = None if selected_option else self._match_option_by_answer(answer, options)
                    if not finnas and not selected_option:
                        labels = [opt["label"] for opt in options]
                        best_label = self.match_by_sentiment(answer, labels)[0]
                        finnas = next((opt["id"] for opt in options if opt["label"] == best_label), None)
                    if not finnas and not selected_option:
                        finnas = options[0]["id"]
                    print('FINALANSWER', selected_option["label"] if selected_option else finnas)
                    if not selected_option:
                        selected_option = next((opt for opt in options if opt["id"] == finnas), None)
                    if selected_option and selected_option["id"]:
                        page.locator(f'label[for="{selected_option["id"]}"]').click(force=True)
                    else:
                        (selected_option or options[0])["el"].click(force=True)
                elif text_input.is_visible():
                    print("The new question requires text input.")
                    text_input.type(answer,delay=100)
                elif suggs:
                    print("found suggs")
                    options = [el.evaluate('el => el.innerText') for el in suggs]
                    finnas = None
                    if is_notice_period_prompt(question):
                        finnas = find_preferred_notice_option(options)
                    if not finnas:
                        finnas = self.match_by_sentiment(answer,options)[0]
                    print(finnas)
                    page.click(f'text="{finnas}"')
                elif dob:
                    dob = answer.strip().split("/")
                    page.locator("input[name='day']").type(dob[0],delay=100)
                    page.locator("input[name='month']").type(dob[1],delay=100)
                    page.locator("input[name='year']").type(dob[2],delay=100)

                else:
                    return 
                send = page.locator('.sendMsg')
                try:
                    expect(send).to_be_enabled()
                    time.sleep(0.5)
                    send.click(timeout=3000)
                except:
                    return
                time.sleep(1)
        except Exception as e:
            print(e)
            return {"response":'error occured on classify_new_question',"error":str(e)}

class NaukriBot:
    def __init__(self, usreml, usrpas,username,number=10):
        self.browser = None
        self.page = None
        self.usr = [usreml, usrpas]
        self.username = username
        self.applno = number
        self.applied_count = 0
        self.page_no = 1
        self.tabs = ["profile","apply","preference","similar_jobs"]
        self.pattern = re.compile(r'https://.*/myapply/saveApply\?strJobsarr=')

    def init_browser(self):
        playwright = sync_playwright().start()
        args = ["--disable-blink-features=AutomationControlled"]
        self.browser =  playwright.chromium.launch(headless=False,args=args)
        self.page = self.browser.new_page()
        self.cba = ChatbotAgent(self.page,self.username)

    def login(self):
        try:
            self.page.goto("http://www.naukri.com",timeout=40000)            
            self.page.click('//*[@id="login_Layer"]')
            self.page.type('input[type="text"]', self.usr[0],delay=100)
            self.page.type('input[type="password"]', self.usr[1],delay=100)
            self.page.click('button[type="submit"]')
            try:
                self.page.wait_for_url(url="https://www.naukri.com/mnjuser/homepage",wait_until="networkidle")
                print("Login successful.")
                return True
            except:
                print("Login failed.")
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False
        
    def checkbox_apply(self):
        try:
            checkboxes = self.page.locator('.naukicon-ot-checkbox').element_handles()
            print(f"Found {len(checkboxes)} checkboxes.")
            if not len(checkboxes)==0:          
                lcbxs = 0
                for checkbox in checkboxes[:5]:
                    checkbox.click()
                    lcbxs += 1                
                apply_button = self.page.locator('.multi-apply-button')
                apply_button.click()
                try:
                    expect(self.page.locator(".chatbot_MessageContainer")).to_be_visible(timeout=3000)
                except:
                    try:
                        expect(self.page).to_have_url(self.pattern)
                        return {"status":"done","clicked":lcbxs}
                    except:
                        raise
                return {"status":"underway","found":len(checkboxes),"clicked":lcbxs}
            else:
                return {"status":"finished","found":len(checkboxes),"clicked":0}
        except Exception:
            return {"status":"failed"}
        
    def apply_(self):
        self.page.wait_for_load_state('networkidle')
        job_links = self.page.eval_on_selector_all(
            '.title',
            'elements => elements.map(element => element.getAttribute("href")) .filter(href => href !== null)'
        )
        if not job_links:
            print(f"No job links found on page {self.page_no}.")
            return

        for jl in job_links:
            if self.applied_count >= self.applno:
                print(f"Applied to {self.applied_count} jobs.")
                break
            try:
                self.page.wait_for_timeout(2000)
                self.page.goto(jl)
                self.page.wait_for_load_state('networkidle')
                apply = self.page.query_selector('#apply-button')
                if not apply:
                    print(f"Skipping job without apply button: {jl}")
                    continue

                apply.click()
                try:
                    expect(self.page.locator(".chatbot_MessageContainer")).to_be_visible(timeout=3000)
                    self.cba.classify_new_question()
                    self.applied_count += 1
                except:
                    try:
                        expect(self.page).to_have_url(self.pattern)
                        self.applied_count += 1
                    except:
                        print(f"Skipping job (not applied): {jl}")
                        continue
            except Exception as e:
                print(jl, "_______", e)
                continue

        if self.applied_count < self.applno:
            self.page_no += 1
            parsed = urlparse(self.base_page_url)
            new_path = parsed.path + f"-{self.page_no}"
            modified_url = urlunparse(parsed._replace(path=new_path))
            try:
                self.page.goto(modified_url)
            except:
                print(f"Could not open results page {self.page_no}. Stopping at {self.applied_count} applications.")
                return
            print(f'going to page {self.page_no}')
            self.apply_()

    def filter_apply(self,s,e='',l='',ja='3'):
        self.search = s
        if not self.search:
            print("Search keyword required")
            return
        self.experience = e
        self.location = l
        self.jobage = ja
        self.init_browser()
        self.login()
        time.sleep(1)
        self.filter_()
        self.base_page_url = self.page.url
        self.apply_()
        self.page.close()
        return {"response":"applied successfully","applied":self.applied_count}

    def filter_(self):
        serch = self.page.locator(".nI-gNb-sb__icon-wrapper")
        serch.click() 
        self.page.locator('input[placeholder="Enter keyword / designation / companies"]').type(self.search,delay=100)
        if self.location:
            self.page.locator('input[placeholder="Enter location"]').type(self.location,delay=100)
        if self.experience:
            self.page.locator('#experienceDD').click()
            self.page.locator(f'li[index="{self.experience}"]').click()
        serch.click()
        self.page.wait_for_load_state('load')
        curl = self.page.url 
        if self.jobage:
            nurl = curl+f"&jobAge={self.jobage}"
            self.page.goto(nurl)

    def start_apply(self,tab):
        self.tabIndex = 0
        self.tab = tab
        self.init_browser()
        if self.login():
            botactions = self.bot_actions()
            return botactions
        
    def bot_actions(self):
        try:
            time.sleep(2)
            self.page.click('.nI-gNb-menuItems__anchorDropdown')
            if not self.tab=="profile":
                self.page.click(f"#{self.tab}")
            self.page.wait_for_load_state("networkidle")
            if self.applied_count >= self.applno:
                print(f"applied {self.applied_count} jobs")
                return {"response":"applied successfully","applied":self.applied_count}
            else:
                cbapl = self.checkbox_apply()
            if cbapl["status"] == 'failed':
                print(f"finished daily quota with {self.applied_count} jobs")
                self.close()
                return {"response":"quota finished","applied":self.applied_count}
            elif cbapl["status"] == 'done':
                self.applied_count += cbapl["clicked"]
                self.bot_actions()
            elif cbapl["status"] == 'underway':
                self.cba.classify_new_question()
                try:
                    expect(self.page).to_have_url(self.pattern)
                    self.applied_count += cbapl["clicked"]
                    self.bot_actions()
                except Exception as e:
                    print("An error occured answering naukri questions :===>",e)
                    self.close()
                    return {"response":"error on botactions","error":str(e)}
            elif cbapl['status']=="finished":
                self.tabIndex += 1
                self.tab = self.tabs[self.tabIndex]
                self.bot_actions()
        except Exception as e:
            self.close()
            print(f"applied {self.applied_count} jobs but an error occured :===>{str(e)}")
        
    def close(self):
        self.browser.close()

