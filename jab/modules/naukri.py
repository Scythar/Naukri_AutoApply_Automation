import time
import re
import threading
import sys
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
    find_preferred_hybrid_work_model_option,
    find_preferred_notice_option,
    find_preferred_marital_status_option,
    find_preferred_positive_preference_option,
    find_preferred_title_option,
    is_career_break_prompt,
    is_hybrid_work_model_prompt,
    is_last_working_day_prompt,
    is_marital_status_prompt,
    is_notice_period_prompt,
    is_positive_preference_mode_enabled,
    is_positive_preference_prompt,
    is_title_prompt,
    preferred_hybrid_work_model_text,
    preferred_last_working_day_text,
    preferred_marital_status_text,
    preferred_notice_period_text,
    preferred_positive_preference_text,
    preferred_title_text,
    normalize_text,
)

NLTK_RESOURCES = {
    "tokenizers/punkt": "punkt",
    "tokenizers/punkt_tab": "punkt_tab",
    "corpora/wordnet": "wordnet",
    "corpora/omw-1.4": "omw-1.4",
}

JAVA_TITLE_PATTERNS = (
    r"\bjava\b",
    r"\bspring(?:\s+boot)?\b",
    r"\bhibernate\b",
    r"\bj2ee\b",
    r"\bj2se\b",
)

DISALLOWED_BACKEND_TITLE_PATTERNS = (
    r"\bpython\b",
    r"\bphp\b",
    r"\bdot\s*net\b",
    r"(?<!\w)\.net\b",
    r"(?<!\w)c#(?!\w)",
    r"(?<!\w)c\+\+(?!\w)",
    r"\bnode(?:\.js)?\b",
    r"\bgolang\b",
    r"\bgo\s+developer\b",
    r"\bgo\s+engineer\b",
    r"\bruby\b",
    r"\brails\b",
    r"\bdjango\b",
    r"\bflask\b",
    r"\blaravel\b",
    r"\bscala\b",
    r"\bkotlin\b",
    r"\brust\b",
    r"\bperl\b",
)

CONDITIONAL_NON_JAVA_LANGUAGE_TITLE_PATTERNS = (
    r"\bjavascript\b",
    r"\btypescript\b",
)

JOB_TITLE_SELECTORS = (
    'h1[class*="jd-header-title"]',
    'header h1',
    "main h1",
    "h1",
)

JOB_COMPANY_SELECTORS = (
    '[class*="jd-header-comp-name"]',
    '[class*="comp-name"]',
    '.comp-name',
    'a[href*="/company/"]',
)

JOB_DESCRIPTION_SELECTORS = (
    '[class*="dang-inner-html"]',
    'section[class*="job-desc"]',
    'div[class*="job-desc"]',
    '.job-desc',
)


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
        with open("./jab/data/user_data.json", "r", encoding="utf-8") as json_file:
            self.profile_data = json.load(json_file)
        self.positive_preference_mode = is_positive_preference_mode_enabled(self.profile_data)
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
        if is_last_working_day_prompt(question):
            return preferred_last_working_day_text()
        if is_title_prompt(question):
            return preferred_title_text()
        if is_marital_status_prompt(question):
            return preferred_marital_status_text()
        if is_hybrid_work_model_prompt(question):
            return preferred_hybrid_work_model_text()
        if is_career_break_prompt(question):
            return "No"
        if normalized.startswith("how many years of experience"):
            return "3"
        if self._is_previous_employee_question(question):
            return "No"
        if self.positive_preference_mode and is_positive_preference_prompt(question):
            return preferred_positive_preference_text()
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
                    elif is_title_prompt(question):
                        selected_option = find_preferred_title_option(options, label_getter=lambda option: option["label"])
                    elif is_marital_status_prompt(question):
                        selected_option = find_preferred_marital_status_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif is_hybrid_work_model_prompt(question):
                        selected_option = find_preferred_hybrid_work_model_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif self.positive_preference_mode and is_positive_preference_prompt(question):
                        selected_option = find_preferred_positive_preference_option(
                            options, label_getter=lambda option: option["label"]
                        )
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
                    elif is_title_prompt(question):
                        finnas = find_preferred_title_option(options)
                    elif is_marital_status_prompt(question):
                        finnas = find_preferred_marital_status_option(options)
                    elif is_hybrid_work_model_prompt(question):
                        finnas = find_preferred_hybrid_work_model_option(options)
                    elif self.positive_preference_mode and is_positive_preference_prompt(question):
                        finnas = find_preferred_positive_preference_option(options)
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
        with open("./jab/data/user_data.json", "r", encoding="utf-8") as json_file:
            self.profile_data = json.load(json_file)
        blocked_companies = self.profile_data.get("Blocked companies", [])
        if isinstance(blocked_companies, str):
            blocked_companies = [blocked_companies]
        self.blocked_companies = [company for company in blocked_companies if company]
        self._pause_event = threading.Event()
        self._pause_event.set()  # running by default
        self._stop_listener = False
        self._listener_thread = None

    def _start_pause_listener(self):
        self._stop_listener = False
        self._listener_thread = threading.Thread(target=self._key_listener, daemon=True)
        self._listener_thread.start()

    def _key_listener(self):
        print("Press 'P' at any time to pause/resume the automation.")
        try:
            import msvcrt
            while not self._stop_listener:
                if msvcrt.kbhit():
                    key = msvcrt.getch().decode('utf-8', errors='ignore').lower()
                    if key == 'p':
                        self._toggle_pause()
                time.sleep(0.1)
        except ImportError:
            import tty, termios, select
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while not self._stop_listener:
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1).lower()
                        if key == 'p':
                            self._toggle_pause()
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def _toggle_pause(self):
        if self._pause_event.is_set():
            self._pause_event.clear()
            print("\n[PAUSED] Press 'P' again to resume...")
        else:
            self._pause_event.set()
            print("\n[RESUMED] Continuing...")

    def _check_pause(self):
        if not self._pause_event.is_set():
            self._pause_event.wait()

    def _extract_job_title_from_page(self):
        for selector in JOB_TITLE_SELECTORS:
            try:
                nodes = self.page.locator(selector)
                for i in range(min(nodes.count(), 3)):
                    node = nodes.nth(i)
                    if not node.is_visible():
                        continue
                    title_text = (node.inner_text() or "").strip()
                    if title_text:
                        return title_text
            except Exception:
                continue
        return ""

    def _extract_company_name_from_page(self):
        for selector in JOB_COMPANY_SELECTORS:
            try:
                nodes = self.page.locator(selector)
                for i in range(min(nodes.count(), 3)):
                    node = nodes.nth(i)
                    if not node.is_visible():
                        continue
                    company_text = (node.inner_text() or "").strip()
                    if company_text:
                        return company_text
            except Exception:
                continue
        return ""

    def _extract_job_description(self):
        best_text = ""
        for selector in JOB_DESCRIPTION_SELECTORS:
            try:
                nodes = self.page.locator(selector)
                for i in range(min(nodes.count(), 4)):
                    node = nodes.nth(i)
                    if not node.is_visible():
                        continue
                    description_text = (node.inner_text() or "").strip()
                    if len(description_text) > len(best_text):
                        best_text = description_text
            except Exception:
                continue

        if best_text:
            return best_text

        try:
            main_text = (self.page.locator("main").inner_text() or "").strip()
            if main_text:
                return main_text
        except Exception:
            pass

        try:
            return (self.page.locator("body").inner_text() or "").strip()
        except Exception:
            return ""

    def _title_has_java_backend(self, title):
        lowered_title = " ".join(str(title or "").lower().split())
        return any(re.search(pattern, lowered_title) for pattern in JAVA_TITLE_PATTERNS)

    def _title_has_disallowed_backend(self, title):
        lowered_title = " ".join(str(title or "").lower().split())
        return any(re.search(pattern, lowered_title) for pattern in DISALLOWED_BACKEND_TITLE_PATTERNS)

    def _title_has_conditional_non_java_language(self, title):
        lowered_title = " ".join(str(title or "").lower().split())
        return any(re.search(pattern, lowered_title) for pattern in CONDITIONAL_NON_JAVA_LANGUAGE_TITLE_PATTERNS)

    def _is_blocked_company(self, company_name):
        normalized_company = normalize_text(company_name)
        if not normalized_company:
            return False
        for blocked_company in self.blocked_companies:
            normalized_blocked_company = normalize_text(blocked_company)
            if not normalized_blocked_company:
                continue
            if (
                normalized_blocked_company in normalized_company
                or normalized_company in normalized_blocked_company
            ):
                return True
        return False

    def _is_java_job(self, title, description):
        normalized_title = normalize_text(title)
        normalized_description = normalize_text(description)

        if not normalized_title:
            return False, "missing job title"

        if self._title_has_disallowed_backend(title):
            return False, "title mentions non-Java backend technology"

        if self._title_has_conditional_non_java_language(title):
            allows_full_stack_java = (
                any(keyword in normalized_title for keyword in ["full stack", "fullstack", "sdet"])
                and (self._title_has_java_backend(title) or re.search(r"\bjava\b", normalized_description))
            )
            if not allows_full_stack_java:
                return False, "title mentions a non-Java programming language"

        if not re.search(r"\bjava\b", normalized_description):
            return False, "job description does not mention Java"

        return True, "matches Java job filters"

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
            '''elements => elements
                .map(element => ({
                    href: element.getAttribute("href"),
                    title: (element.textContent || "").trim(),
                    company: (
                        (
                            (element.closest("article") || element.closest("div") || element.parentElement)
                            ?.querySelector('[class*="comp-name"], .comp-name')
                        )?.textContent || ""
                    ).trim(),
                }))
                .filter(item => item.href !== null)'''
        )
        if not job_links:
            print(f"No job links found on page {self.page_no}.")
            return

        for job in job_links:
            self._check_pause()
            if self.applied_count >= self.applno:
                print(f"Applied to {self.applied_count} jobs.")
                break
            try:
                jl = job["href"]
                listing_title = (job.get("title") or "").strip()
                listing_company = (job.get("company") or "").strip()
                self.page.wait_for_timeout(2000)
                self.page.goto(jl)
                self.page.wait_for_load_state('networkidle')
                page_title = self._extract_job_title_from_page()
                page_company = self._extract_company_name_from_page()
                job_title = page_title or listing_title
                company_name = page_company or listing_company
                if self._is_blocked_company(company_name):
                    print(f"Skipping blocked company ({company_name}): {job_title or jl}")
                    continue
                job_description = self._extract_job_description()
                should_apply, reason = self._is_java_job(job_title, job_description)
                if not should_apply:
                    print(f"Skipping job due to filter ({reason}): {job_title or jl}")
                    continue
                apply = self.page.query_selector('#apply-button')
                if not apply:
                    print(f"Skipping job without apply button: {job_title or jl}")
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
                        print(f"Skipping job (not applied): {job_title or jl}")
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

    def filter_apply(self,s,e='',l='',ja='1'):
        self.search = s
        if not self.search:
            print("Search keyword required")
            return
        self.experience = e
        self.location = l
        self.jobage = ja
        self.init_browser()
        self.login()
        self._start_pause_listener()
        time.sleep(1)
        max_restarts = 5
        for attempt in range(max_restarts + 1):
            if attempt > 0:
                print(f"\nRestarting search (attempt {attempt}/{max_restarts})...")
                self.page_no = 1
            self.filter_()
            self.base_page_url = self.page.url
            self.apply_()
            if self.applied_count >= self.applno:
                break
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
        # Apply Freshness filter "Last 1 day" via left panel UI
        try:
            freshness = self.page.locator('label:has-text("Last 1 day")').first
            freshness.scroll_into_view_if_needed()
            freshness.click()
            self.page.wait_for_load_state('load')
            print("Freshness filter set to: Last 1 day")
        except Exception as e:
            print(f"Could not click Freshness filter via UI, falling back to URL param: {e}")
            curl = self.page.url
            if self.jobage:
                nurl = curl + f"&jobAge={self.jobage}"
                self.page.goto(nurl)

    def start_apply(self,tab):
        self.tabIndex = 0
        self.tab = tab
        self.init_browser()
        if self.login():
            self._start_pause_listener()
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
        self._stop_listener = True
        self.browser.close()

