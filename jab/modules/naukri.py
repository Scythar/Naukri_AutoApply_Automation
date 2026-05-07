import time
import re
import threading
import sys
import os
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
    DIRECT_QUESTION_ANSWERS,
    find_preferred_disability_option,
    find_preferred_highest_degree_option,
    find_preferred_hybrid_work_model_option,
    find_preferred_notice_option,
    find_preferred_marital_status_option,
    find_preferred_positive_preference_option,
    find_preferred_title_option,
    is_career_break_prompt,
    is_conditional_followup_prompt,
    is_current_company_prompt,
    is_email_prompt,
    is_academic_score_prompt,
    is_genai_tool_prompt,
    is_graduation_year_prompt,
    is_holding_offer_prompt,
    is_interview_availability_prompt,
    is_jd_rating_prompt,
    is_location_ok_prompt,
    is_location_prompt,
    is_pan_prompt,
    is_previous_company_prompt,
    is_postal_code_prompt,
    is_previously_interviewed_prompt,
    is_relative_at_company_prompt,
    is_sponsorship_prompt,
    is_tech_yesno_prompt,
    is_years_of_experience_prompt,
    is_yymm_experience_prompt,
    is_current_ctc_prompt,
    is_disability_prompt,
    is_dob_prompt,
    is_employee_id_prompt,
    is_expected_ctc_prompt,
    is_highest_degree_prompt,
    is_hybrid_work_model_prompt,
    is_last_working_day_prompt,
    is_marital_status_prompt,
    is_notice_period_buyout_prompt,
    is_notice_period_prompt,
    is_relocation_prompt,
    is_tech_experience_prompt,
    is_positive_preference_mode_enabled,
    is_positive_preference_prompt,
    is_title_prompt,
    preferred_current_ctc_text,
    preferred_disability_text,
    preferred_dob_text,
    preferred_expected_ctc_text,
    preferred_highest_degree_text,
    preferred_hybrid_work_model_text,
    preferred_last_working_day_text,
    preferred_notice_period_buyout_text,
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
    # Stacks
    r"\bmern\b",
    r"\bmean\b",
    # Languages
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
    r"\bswift\b",
    r"\bcobol\b",
    r"\brpg\s+developer\b",
    r"\brpg\s+engineer\b",
    # Platforms / Low-code / CRM / ERP
    r"\bmedia\s*cloud\b",
    r"\bservicenow\b",
    r"\bsalesforce\b",
    r"\bmulesoft\b",
    r"\bsap\b",
    r"\babap\b",
    r"\bsiebel\b",
    r"\bsitecore\b",
    r"\bsharepoint\b",
    r"\bworkday\b",
    r"\bdynamics\b",
    r"\bpega\b",
    r"\bappian\b",
    r"\boutsystems\b",
    r"\bmendix\b",
    r"\btibco\b",
    r"\bboomi\b",
    # Data / ETL tools
    r"\binformatica\b",
    r"\bdatastage\b",
    r"\btalend\b",
    r"\bpentaho\b",
    # BI / Visualisation
    r"\bpower\s*bi\b",
    r"\btableau\b",
    r"\blooker\b",
    r"\bqlik\b",
    # Mobile
    r"\bandroid\b",
    r"\bios\b",
    r"\bflutter\b",
    r"\bxamarin\b",
    # Mainframe
    r"\bmainframe\b",
    r"\bcics\b",
    r"\bjcl\b",
    # DevOps / Infrastructure
    r"\bdevops\b",
    # Security roles
    r"\bsecurity\s+(?:developer|engineer|analyst)\b",
    r"\bcybersecurity\b",
    r"\bdevsecops\b",
    r"\bpentester\b",
    r"\bpenetration\s+test(?:er|ing)?\b",
    # Frontend roles
    r"\bfront[\s\-]?end\s+(?:developer|engineer)\b",
    r"\bfrontend\s+(?:developer|engineer)\b",
    r"\bui\s+developer\b",
    r"\bui\s+engineer\b",
    # QA / Testing roles
    r"\btest\b",
    r"\bqa\b",
    r"\bquality\s+assurance\b",
    r"\bsdet\b",
    # GenAI / AI/ML roles
    r"\bgenai\b",
    r"\bgen\s*ai\b",
    r"\bgenerative\s+ai\b",
    r"\bprompt\s+engineer\b",
    r"\bml\s+engineer\b",
    r"\bmachine\s+learning\s+engineer\b",
    r"\bai\s+(?:developer|engineer|scientist)\b",
    # Data roles
    r"\bdata\s+engineer\b",
    r"\bdata\s+scientist\b",
    r"\bdata\s+analyst\b",
    r"\bdata\s+developer\b",
)

CONDITIONAL_NON_JAVA_LANGUAGE_TITLE_PATTERNS = (
    r"\bjavascript\b",
    r"\btypescript\b",
    r"\breact(?:\.js)?\b",
    r"\bangular\b",
    r"\bvue(?:\.js)?\b",
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
        skills = self.profile_data.get("Skills", {})
        self.tech_keywords = tuple(normalize_text(s) for s in skills.keys() if normalize_text(s))
        self._question_overridden = False
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
        self._question_overridden = True
        if normalized in DIRECT_QUESTION_ANSWERS:
            return DIRECT_QUESTION_ANSWERS[normalized]
        if is_notice_period_buyout_prompt(question):
            return preferred_notice_period_buyout_text()
        if is_last_working_day_prompt(question):
            return preferred_last_working_day_text()
        if is_notice_period_prompt(question):
            return preferred_notice_period_text()
        if is_relocation_prompt(question):
            return "Yes"
        if is_current_ctc_prompt(question):
            return preferred_current_ctc_text(question)
        if is_expected_ctc_prompt(question):
            return preferred_expected_ctc_text(question)
        if is_title_prompt(question):
            return preferred_title_text()
        if is_marital_status_prompt(question):
            return preferred_marital_status_text()
        if is_hybrid_work_model_prompt(question):
            return preferred_hybrid_work_model_text()
        if is_graduation_year_prompt(question):
            return self.profile_data.get("Graduation Year", "2017")
        if is_academic_score_prompt(question):
            t = self.profile_data.get("10th Percentage", "78")
            tw = self.profile_data.get("12th Percentage", "75")
            g = self.profile_data.get("Graduation Percentage", "70")
            return f"10th: {t}%, 12th: {tw}%, B.Tech: {g}%"
        if is_dob_prompt(question):
            return preferred_dob_text()
        if is_career_break_prompt(question):
            return "No"
        if is_disability_prompt(question):
            return preferred_disability_text()
        if is_interview_availability_prompt(question):
            return "Yes"
        if is_relative_at_company_prompt(question):
            return "No"
        if is_previously_interviewed_prompt(question):
            return "No"
        if is_genai_tool_prompt(question):
            return "Yes, Claude - code optimization and code review"
        if is_email_prompt(question):
            if any(kw in normalized for kw in ("phone", "mobile", "contact number", "phone number", "cell")):
                return f"{self.profile_data.get('Email', '')} {self.profile_data.get('Mobile', '')}"
            return self.profile_data.get("Email", "")
        if is_location_ok_prompt(question):
            return "Yes"
        if is_location_prompt(question):
            return self.profile_data.get("Location", "Bengaluru")
        if is_postal_code_prompt(question):
            return self.profile_data.get("Address", {}).get("Pin Code", "")
        if is_pan_prompt(question):
            return self.profile_data.get("PAN", "")
        if is_sponsorship_prompt(question):
            return "No"
        if is_holding_offer_prompt(question):
            return "No"
        if is_conditional_followup_prompt(question) or is_employee_id_prompt(question):
            return "NA"
        if is_highest_degree_prompt(question):
            return preferred_highest_degree_text()
        if is_jd_rating_prompt(question):
            return "8.5"
        if is_tech_yesno_prompt(question):
            return "Yes"
        if is_yymm_experience_prompt(question):
            return "03/05"
        if is_years_of_experience_prompt(question):
            return "3.5"
        if normalized.startswith("how many years of experience") or normalized.startswith("relevant experience"):
            return "3.5"
        if is_tech_experience_prompt(question, self.tech_keywords):
            return "3.5"
        if is_current_company_prompt(question):
            return self.profile_data.get("Current company", "")
        if self._is_previous_employee_question(question):
            return "No"
        if is_previous_company_prompt(question):
            return "No"
        if self.positive_preference_mode and is_positive_preference_prompt(question):
            return preferred_positive_preference_text()
        self._question_overridden = False
        return answer

    def _log_new_question(self, question, reason, answer=""):
        filepath = "./newQuestions.txt"
        question_clean = " ".join(question.strip().split())
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                if question_clean in f.read():
                    return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        answer_str = f" | A: {answer}" if answer else ""
        entry = f"[{timestamp}] | {reason} | Q: {question_clean}{answer_str}\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Logged to newQuestions.txt [{reason}]: {question_clean[:80]}")

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
                print('answer', answer)
                log_reason = "NEW (no override matched)" if not self._question_overridden else "answered"

                checkboxes = cbcn.query_selector_all('input[type="checkbox"]')
                radio_buttons = cbcn.query_selector_all('input[type="radio"]')
                text_input = page.locator('.chatbot_MessageContainer .textArea, .chatbot_MessageContainer input[type="text"], .chatbot_MessageContainer input[type="number"]').first
                chips = cbcn.query_selector_all('.chipsContainer .chatbot_Chip')
                suggs = cbcn.query_selector_all('.ssc__heading')
                dob = cbcn.query_selector(".dob__container")
                if chips:
                    answer_lower = answer.strip().lower()
                    selected_chip = None
                    chip_labels = [(c, (c.inner_text() or "").strip()) for c in chips]
                    if is_notice_period_prompt(question):
                        best = find_preferred_notice_option(
                            [t for _, t in chip_labels]
                        )
                        if best:
                            selected_chip = next((c for c, t in chip_labels if t == best), None)
                        if not selected_chip:
                            for c, t in chip_labels:
                                nt = normalize_text(t)
                                if any(kw in nt for kw in ("immediate", "0 day", "0day", "no notice", "immediately", "zero")):
                                    selected_chip = c
                                    break
                        if not selected_chip:
                            # Pick shortest duration chip; skip any "skip this question" chip
                            best_days, best_chip, first_non_skip = float('inf'), None, None
                            for c, t in chip_labels:
                                nt = normalize_text(t)
                                if "skip" in nt:
                                    continue
                                if first_non_skip is None:
                                    first_non_skip = c
                                nums = [float(n) for n in re.findall(r'\d+', t)]
                                if nums and min(nums) < best_days:
                                    best_days = min(nums)
                                    best_chip = c
                            selected_chip = best_chip or first_non_skip
                    elif is_last_working_day_prompt(question):
                        # Find chip matching Oct/31/2025
                        for c, t in chip_labels:
                            nt = normalize_text(t)
                            if "skip" in nt:
                                continue
                            if re.search(r'\boct(?:ober)?\b', nt) or re.search(r'\b31\b.*\b2025\b', nt) or re.search(r'\b2025\b.*\b31\b', nt):
                                selected_chip = c
                                break
                        if not selected_chip:
                            for c, t in chip_labels:
                                if "skip" not in normalize_text(t):
                                    selected_chip = c
                                    break
                    elif is_location_ok_prompt(question):
                        selected_chip = next(
                            (c for c, t in chip_labels if re.search(r'\byes\b', normalize_text(t))), None
                        )
                    elif is_disability_prompt(question):
                        best = find_preferred_disability_option(
                            [t for _, t in chip_labels]
                        )
                        if best:
                            selected_chip = next((c for c, t in chip_labels if t == best), None)
                    elif is_years_of_experience_prompt(question) or is_tech_experience_prompt(question, self.tech_keywords):
                        target = 3.5
                        best_chip, best_diff = None, float('inf')
                        for c, t in chip_labels:
                            nums = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', t)]
                            if nums:
                                mid = sum(nums) / len(nums)
                                if abs(mid - target) < best_diff:
                                    best_diff = abs(mid - target)
                                    best_chip = c
                        if not best_chip:
                            for c, t in chip_labels:
                                if re.search(r'\byes\b', normalize_text(t)):
                                    best_chip = c
                                    break
                        if not best_chip:
                            # Semantic level fallback (e.g. "Beginner/Intermediate/Expert" chips)
                            for level in ("intermediate", "advanced", "mid level", "mid-level", "senior", "3"):
                                for c, t in chip_labels:
                                    nt = normalize_text(t)
                                    if level in nt and "skip" not in nt:
                                        best_chip = c
                                        break
                                if best_chip:
                                    break
                        if not best_chip:
                            # Last resort: first non-skip chip
                            for c, t in chip_labels:
                                if "skip" not in normalize_text(t):
                                    best_chip = c
                                    break
                        if best_chip:
                            selected_chip = best_chip
                    if not selected_chip:
                        for c in chips:
                            chip_text = (c.inner_text() or "").strip().lower()
                            if chip_text == answer_lower or chip_text in answer_lower or answer_lower in chip_text:
                                selected_chip = c
                                break
                    if not selected_chip:
                        best_label = self.match_by_sentiment(answer, [t for _, t in chip_labels])[0]
                        selected_chip = next((c for c, t in chip_labels if t == best_label), chips[0])
                    selected_chip_text = (selected_chip.inner_text() or "").strip()
                    print(f"Chip selected: {selected_chip_text}")
                    self._log_new_question(question, log_reason, f"[chip] {selected_chip_text}")
                    selected_chip.click()
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
                        if not selected_option:
                            # Yes/No style (e.g., "Are you available to join immediately?") → Yes
                            selected_option = find_preferred_positive_preference_option(
                                options, label_getter=lambda option: option["label"]
                            )
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
                    elif is_interview_availability_prompt(question):
                        selected_option = find_preferred_positive_preference_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif is_disability_prompt(question):
                        selected_option = find_preferred_disability_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif (is_career_break_prompt(question)
                          or is_holding_offer_prompt(question)
                          or is_sponsorship_prompt(question)):
                        selected_option = next(
                            (o for o in options if re.search(r'\bno\b', normalize_text(o["label"]))), None
                        )
                    elif (self._is_previous_employee_question(question)
                          or is_previous_company_prompt(question)
                          or is_relative_at_company_prompt(question)
                          or is_previously_interviewed_prompt(question)):
                        selected_option = next(
                            (o for o in options if re.search(r'\bno\b', normalize_text(o["label"]))), None
                        )
                    elif is_location_ok_prompt(question):
                        selected_option = find_preferred_positive_preference_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif is_highest_degree_prompt(question):
                        selected_option = find_preferred_highest_degree_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    elif is_tech_experience_prompt(question, self.tech_keywords) or is_years_of_experience_prompt(question):
                        # Numeric nearest-match: pick the option whose midpoint is closest to 3.5 years
                        _target = 3.5
                        _best_opt, _best_diff = None, float('inf')
                        for opt in options:
                            _lbl = normalize_text(opt["label"])
                            if "skip" in _lbl:
                                continue
                            _nums = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', opt["label"])]
                            if _nums:
                                _mid = sum(_nums) / len(_nums)
                                if abs(_mid - _target) < _best_diff:
                                    _best_diff = abs(_mid - _target)
                                    _best_opt = opt
                        selected_option = _best_opt
                    elif self.positive_preference_mode and is_positive_preference_prompt(question):
                        selected_option = find_preferred_positive_preference_option(
                            options, label_getter=lambda option: option["label"]
                        )
                    # General catch-all: yes/no radio → always pick Yes
                    if not selected_option:
                        _norms = [normalize_text(o["label"]) for o in options]
                        if (all(re.search(r'\byes\b', n) or re.search(r'\bno\b', n) for n in _norms)
                                and any(re.search(r'\byes\b', n) for n in _norms)):
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
                    if not selected_option:
                        selected_option = next((opt for opt in options if opt["id"] == finnas), None)
                    final_label = selected_option["label"] if selected_option else finnas
                    print('FINALANSWER', final_label)
                    self._log_new_question(question, log_reason, f"[radio] {final_label}")
                    if selected_option and selected_option["id"]:
                        page.locator(f'label[for="{selected_option["id"]}"]').click(force=True)
                    else:
                        (selected_option or options[0])["el"].click(force=True)
                elif text_input.is_visible():
                    print("The new question requires text input.")
                    self._log_new_question(question, log_reason, f"[text] {answer}")
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
                    self._log_new_question(question, log_reason, f"[sugg] {finnas}")
                    page.click(f'text="{finnas}"')
                elif dob:
                    self._log_new_question(question, log_reason, f"[dob] {answer}")
                    dob = answer.strip().split("/")
                    page.locator("input[name='day']").type(dob[0],delay=100)
                    page.locator("input[name='month']").type(dob[1],delay=100)
                    page.locator("input[name='year']").type(dob[2],delay=100)

                else:
                    self._log_new_question(question, "SKIPPED (no input element found)")
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
        self._playwright = None
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
        self.max_pages = None
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

    def _clean_company_name(self, raw):
        # Take only the first line (AmbitionBox rating appears on subsequent lines)
        name = (raw or "").split("\n")[0].strip()
        # Strip trailing rating/review noise like "3.3", "12.5K Reviews", "4.1K Reviews"
        name = re.sub(r'\s*\d[\d.]*[KkMm]?\s*reviews?.*$', '', name, flags=re.IGNORECASE).strip()
        name = re.sub(r'\s*\d[\d.]*\s*$', '', name).strip()
        return name

    def _extract_company_name_from_page(self):
        for selector in JOB_COMPANY_SELECTORS:
            try:
                nodes = self.page.locator(selector)
                for i in range(min(nodes.count(), 3)):
                    node = nodes.nth(i)
                    if not node.is_visible():
                        continue
                    company_text = self._clean_company_name(node.inner_text())
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

    def _is_already_applied(self):
        try:
            page_text = self.page.locator('#apply-button, [class*="apply"]').first.inner_text().strip().lower()
            if "applied" in page_text:
                return True
        except Exception:
            pass
        try:
            indicators = [
                '[class*="already-applied"]',
                '[class*="alreadyApplied"]',
                '[class*="applied-status"]',
                '[class*="appliedStatus"]',
            ]
            for selector in indicators:
                if self.page.query_selector(selector):
                    return True
        except Exception:
            pass
        try:
            body = self.page.locator("body").inner_text().lower()
            if "already applied" in body or "you have applied" in body:
                return True
        except Exception:
            pass
        return False

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
            if not self._title_has_java_backend(title):
                return False, "title mentions non-Java backend technology"

        if self._title_has_conditional_non_java_language(title):
            if not self._title_has_java_backend(title):
                return False, "title mentions a non-Java programming language"

        java_desc_count = len(re.findall(r"\bjava\b", normalized_description))

        if java_desc_count == 0:
            return False, "job description does not mention Java"

        if not self._title_has_java_backend(title) and java_desc_count < 2:
            return False, "Java only mentioned incidentally in description (not a primary requirement)"

        return True, "matches Java job filters"

    def _wait_for_page_ready(self, timeout=15000):
        """Wait for page load without blocking on networkidle (Naukri keeps background requests open)."""
        try:
            self.page.wait_for_load_state('load', timeout=timeout)
        except Exception:
            pass
        self.page.wait_for_timeout(500)

    def init_browser(self):
        self._playwright = sync_playwright().start()
        args = [
            "--disable-blink-features=AutomationControlled",
            "--disable-notifications",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        try:
            # Use installed Chrome — matches your other project's behaviour, no taskbar blinking
            self.browser = self._playwright.chromium.launch(
                headless=False, channel="chrome", args=args
            )
        except Exception:
            # Fallback to bundled Chromium if Chrome is not installed
            self.browser = self._playwright.chromium.launch(headless=False, args=args)
        self.page = self.browser.new_page()
        self.cba = ChatbotAgent(self.page, self.username)

    def login(self):
        try:
            self.page.goto("http://www.naukri.com",timeout=40000)            
            self.page.click('//*[@id="login_Layer"]')
            self.page.type('input[type="text"]', self.usr[0],delay=100)
            self.page.type('input[type="password"]', self.usr[1],delay=100)
            self.page.click('button[type="submit"]')
            try:
                self.page.wait_for_url("**/mnjuser/homepage", timeout=15000)
            except Exception:
                pass
            self.page.wait_for_timeout(2000)
            current_url = self.page.url
            if "naukri.com" in current_url and "login" not in current_url.lower():
                print("Login successful.")
                return True
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
        
    def _get_company_site_apply_url(self):
        """Return company-site apply URL by reading href (no navigation)."""
        selectors = [
            'a[href*="applyredirect"]',
            'a:has-text("Apply on Company Site")',
            'a:has-text("Apply on company site")',
            'a:has-text("company site")',
            'button:has-text("Apply on Company Site")',
            '[class*="company-btn"]',
            '[class*="companyBtn"]',
        ]
        for selector in selectors:
            try:
                el = self.page.query_selector(selector)
                if el:
                    href = el.get_attribute("href") or el.get_attribute("data-href")
                    if href:
                        return href
            except Exception:
                continue
        return None

    def _click_and_get_company_apply_url(self):
        """Click Apply on Company Site, capture URL from new tab, close tab, return URL."""
        btn_selectors = [
            'a[href*="applyredirect"]',
            'a:has-text("Apply on Company Site")',
            'a:has-text("Apply on company site")',
            'a:has-text("Apply on Company Website")',
            'a:has-text("company site")',
            'a:has-text("company website")',
            'button:has-text("Apply on Company Site")',
            'button:has-text("Apply on Company Website")',
            '[class*="company-btn"]',
            '[class*="companyBtn"]',
            '[class*="apply-btn"]',
            '[class*="applyBtn"]',
        ]
        for selector in btn_selectors:
            try:
                el = self.page.query_selector(selector)
                if not el:
                    continue
                # Return href directly if already a real external URL
                href = el.get_attribute("href") or el.get_attribute("data-href")
                if href and not href.startswith("javascript") and not self._is_naukri_url(href):
                    return href
                # Click and capture the new tab that opens
                try:
                    with self.page.context.expect_page(timeout=5000) as new_page_info:
                        el.click()
                    new_page = new_page_info.value
                    try:
                        new_page.wait_for_load_state('load', timeout=10000)
                    except Exception:
                        pass
                    url = new_page.url
                    new_page.close()
                    if url and not self._is_naukri_url(url):
                        return url
                except Exception:
                    # No new tab opened — check if same-tab navigated
                    self._wait_for_page_ready()
                    url = self.page.url
                    if url and not self._is_naukri_url(url):
                        return url
                return None
            except Exception:
                continue
        return None

    def _parse_job_age_days(self, age_text):
        """Convert '2 Days Ago', '1 Day Ago', 'Just Now', etc. to number of days."""
        normalized = (age_text or "").lower().strip()
        if not normalized:
            return 999
        if any(k in normalized for k in ("just now", "today", "hour", "minute", "second")):
            return 0
        m = re.search(r'(\d+)\s*(day|week|month)', normalized)
        if m:
            value = int(m.group(1))
            unit = m.group(2)
            if unit == "week":
                return value * 7
            if unit == "month":
                return value * 30
            return value
        return 999

    def _save_did_not_apply(self, reason, url):
        filepath = "./DidNotApply.txt"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] | {reason} | {url}\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)

    def _is_naukri_url(self, url):
        return bool(url and "naukri.com" in url)

    def _save_external_apply(self, job_title, company, naukri_url, apply_url):
        filepath = "./external_apply.txt"
        # Treat any naukri.com URL as "no real external URL"
        real_apply_url = apply_url if (apply_url and apply_url != naukri_url and not self._is_naukri_url(apply_url)) else None
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                existing = f.read()
            if naukri_url in existing or (real_apply_url and real_apply_url in existing):
                print(f"Already in external_apply.txt, skipping: {job_title} @ {company}")
                return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        if real_apply_url:
            entry = f"[{timestamp}] | Apply: {real_apply_url} | Naukri: {naukri_url} | {job_title} @ {company} |\n"
        else:
            entry = f"[{timestamp}] | Naukri: {naukri_url} | {job_title} @ {company} |\n"
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"Saved to external_apply.txt: {job_title} @ {company}")

    def apply_(self):
        self._wait_for_page_ready()
        # Wait for job cards to render (React SPA needs time after load)
        for sel in ['.title', 'article.jobTuple', '[class*="jobCard"]', '[class*="job-card"]']:
            try:
                self.page.wait_for_selector(sel, timeout=8000)
                break
            except Exception:
                continue
        job_links = self._extract_job_links_from_page()
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
                self._wait_for_page_ready()
                page_title = self._extract_job_title_from_page()
                page_company = self._extract_company_name_from_page()
                job_title = page_title or listing_title
                company_name = page_company or listing_company
                if self._is_blocked_company(company_name):
                    print(f"Skipping blocked company ({company_name}): {job_title or jl}")
                    self._save_did_not_apply(f"Blocked company: {company_name}", jl)
                    continue
                job_description = self._extract_job_description()
                should_apply, reason = self._is_java_job(job_title, job_description)
                if not should_apply:
                    print(f"Skipping job due to filter ({reason}): {job_title or jl}")
                    self._save_did_not_apply(reason, jl)
                    continue
                apply = self.page.query_selector('#apply-button')
                if not apply:
                    if self._is_already_applied():
                        print(f"Already applied, skipping: {job_title or jl}")
                        self._save_did_not_apply("Already applied", jl)
                        continue
                    if not re.search(r"\bjava\b", normalize_text(job_description)):
                        print(f"Skipping external apply (no Java in description): {job_title or jl}")
                        self._save_did_not_apply("No Java in description (external)", jl)
                        continue
                    external_url = self._click_and_get_company_apply_url() or jl
                    self._save_external_apply(job_title or "Unknown", company_name or "Unknown", jl, external_url)
                    continue

                if self._is_already_applied():
                    print(f"Already applied, skipping: {job_title or jl}")
                    self._save_did_not_apply("Already applied", jl)
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
                        self._save_did_not_apply("Apply failed", jl)
                        continue
            except Exception as e:
                print(jl, "_______", e)
                continue

        if self.applied_count < self.applno:
            if self.max_pages and self.page_no >= self.max_pages:
                print(f"Reached page limit ({self.max_pages}). Stopping this phase.")
                return
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

    def _extract_job_links_from_page(self):
        """Try multiple selector strategies to collect job links from the current page."""
        strategies = [
            # Search results page: anchors with class "title"
            (
                '.title',
                '''elements => elements
                    .map(el => ({
                        href: el.getAttribute('href'),
                        title: (el.textContent || '').trim(),
                        company: (
                            (el.closest('article') || el.closest('div') || el.parentElement)
                            ?.querySelector('[class*="comp-name"], .comp-name')?.textContent || ''
                        ).trim(),
                    }))
                    .filter(i => i.href)''',
            ),
            # Card-based pages (recommended jobs): pick the job-title anchor from each card
            (
                '[class*="tuple"], [class*="jobCard"], [class*="job-card"], article',
                '''elements => {
                    const seen = new Set();
                    const NON_JOB = ['/company', '/companies', 'ambitionbox', '/reviews', '/salaries', '/interviews', 'mailto:', 'javascript:'];
                    function isNonJob(href) {
                        return NON_JOB.some(p => href.includes(p));
                    }
                    return elements.map(el => {
                        const anchors = [...el.querySelectorAll('a[href]')];
                        let ta = null;
                        // 1. anchor with "title" in className
                        ta = anchors.find(a => /title/i.test(a.className || ''));
                        // 2. anchor whose href looks like a job detail URL
                        if (!ta) {
                            ta = anchors.find(a => {
                                const h = a.getAttribute('href') || '';
                                return !isNonJob(h) && (
                                    h.includes('/job-listings') ||
                                    /-JD-/i.test(h) ||
                                    /\\/[a-z][a-z0-9-]+-\\d{6,}/.test(h)
                                );
                            });
                        }
                        // 3. anchor with most text that is not a rating/short label
                        if (!ta) {
                            const candidates = anchors.filter(a => {
                                const h = a.getAttribute('href') || '';
                                const txt = (a.textContent || '').trim();
                                return !isNonJob(h) && txt.length > 5 && !/^\\d/.test(txt);
                            });
                            candidates.sort((a, b) => (b.textContent||'').length - (a.textContent||'').length);
                            ta = candidates[0] || null;
                        }
                        if (!ta) return null;
                        const h = ta.getAttribute('href');
                        if (!h || seen.has(h)) return null;
                        seen.add(h);
                        const comp = el.querySelector('[class*="comp"], [class*="company"]');
                        return {
                            href: h,
                            title: (ta.textContent || '').trim(),
                            company: (comp ? comp.textContent : '').trim(),
                        };
                    }).filter(Boolean);
                }''',
            ),
            # Anchor whose class contains "title"
            (
                'a[class*="title"]',
                '''elements => elements
                    .map(el => ({
                        href: el.getAttribute('href'),
                        title: (el.textContent || '').trim(),
                        company: (
                            (el.closest('article') || el.closest('li') || el.closest('div'))
                            ?.querySelector('[class*="comp-name"], [class*="company"], .comp-name')?.textContent || ''
                        ).trim(),
                    }))
                    .filter(i => i.href)''',
            ),
            # Broad URL-pattern fallback: /job-listings or -JD-
            (
                'a[href]',
                '''elements => {
                    const seen = new Set();
                    return elements
                        .filter(el => {
                            const h = el.getAttribute('href') || '';
                            return h.includes('/job-listings') || /-JD-[A-Z0-9]/i.test(h);
                        })
                        .filter(el => {
                            const h = el.getAttribute('href');
                            if (seen.has(h)) return false;
                            seen.add(h);
                            return true;
                        })
                        .map(el => ({
                            href: el.getAttribute('href'),
                            title: (el.textContent || '').trim(),
                            company: '',
                        }));
                }''',
            ),
        ]
        for selector, script in strategies:
            try:
                links = self.page.eval_on_selector_all(selector, script)
                if links:
                    print(f"Found {len(links)} job links via selector: {selector}")
                    return links
            except Exception:
                continue
        return []

    def _click_recommended_section_tab(self, section_name):
        """Click a section tab on the Recommended Jobs page. Returns True if clicked."""
        # Give React time to render the tab list
        self.page.wait_for_timeout(2000)

        # Strategy 1: scoped inside a known tab-container (avoids matching job-card text)
        container_selectors = [
            '[role="tablist"]',
            '[class*="tabList"]', '[class*="tab-list"]',
            '[class*="sectionTab"]', '[class*="filterTab"]',
            '[class*="leftSection"]', '[class*="left-section"]',
            '[class*="sidebar"]', '[class*="leftPanel"]',
        ]
        for container_sel in container_selectors:
            try:
                containers = self.page.locator(container_sel)
                for i in range(min(containers.count(), 3)):
                    container = containers.nth(i)
                    if not container.is_visible():
                        continue
                    for tag in ['button', '[role="tab"]', 'li', 'a', 'span', 'div']:
                        try:
                            tab = container.locator(f'{tag}:has-text("{section_name}")').first
                            if tab.count() > 0 and tab.is_visible():
                                tab.click()
                                self.page.wait_for_timeout(1500)
                                print(f"Clicked section tab '{section_name}' inside {container_sel}/{tag}")
                                return True
                        except Exception:
                            continue
            except Exception:
                continue

        # Strategy 2: tab-specific tags page-wide (less likely to hit job cards)
        for selector in [
            f'[role="tab"]:has-text("{section_name}")',
            f'button:has-text("{section_name}")',
            f'li[class*="tab"]:has-text("{section_name}")',
            f'li[class*="Tab"]:has-text("{section_name}")',
            f'li[class*="filter"]:has-text("{section_name}")',
            f'li[class*="section"]:has-text("{section_name}")',
        ]:
            try:
                el = self.page.locator(selector).first
                if el.count() > 0 and el.is_visible():
                    el.click()
                    self.page.wait_for_timeout(1500)
                    print(f"Clicked section tab '{section_name}' via {selector}")
                    return True
            except Exception:
                continue

        print(f"Section tab not found: '{section_name}' — skipping section")
        return False

    def _collect_recommended_cards(self):
        """Wait for cards to render, scroll to load all, return card metadata list."""
        for wait_sel in ['article.jobTuple', 'article[data-job-id]', 'p.title']:
            try:
                self.page.wait_for_selector(wait_sel, timeout=8000)
                break
            except Exception:
                continue
        else:
            time.sleep(3)
        try:
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1200)
            self.page.evaluate("window.scrollTo(0, 0)")
            self.page.wait_for_timeout(500)
        except Exception:
            pass
        return self.page.eval_on_selector_all(
            'article.jobTuple[data-job-id]',
            '''elements => elements.map(el => ({
                jobId: el.getAttribute('data-job-id'),
                title: (el.querySelector('p.title') || {getAttribute: ()=>''}).getAttribute('title')
                        || (el.querySelector('p.title') || {textContent: ''}).textContent.trim(),
                company: (el.querySelector('.subTitle') || {getAttribute: ()=>''}).getAttribute('title')
                         || (el.querySelector('.subTitle') || {textContent: ''}).textContent.trim(),
                age: ((el.querySelector('.plcHolder .fw500') || el.querySelector('.jobAge') || {textContent: ''}).textContent || '').trim(),
            }))'''
        )

    def _apply_card(self, card, rec_page_url, section_name):
        """Navigate to one recommended job card and apply/save. Returns True if applied."""
        job_id = card.get('jobId', '')
        listing_title = card.get('title', '')
        listing_company = card.get('company', '')
        age_text = card.get('age', '')
        if not job_id:
            return False
        age_days = self._parse_job_age_days(age_text)
        max_age = int(self.jobage) if hasattr(self, 'jobage') and self.jobage else 1
        if age_days > max_age:
            print(f"Skipping recommended job (age {age_days}d > {max_age}d): {listing_title}")
            self._save_did_not_apply(f"Too old ({age_days}d > {max_age}d): {listing_title}", f"{rec_page_url}#{job_id}")
            return False
        try:
            # Return to recommended page + re-select section if we navigated away
            if rec_page_url not in self.page.url:
                self.page.goto(rec_page_url)
                self._wait_for_page_ready()
                self._click_recommended_section_tab(section_name)
                try:
                    self.page.wait_for_selector(f'article[data-job-id="{job_id}"]', timeout=8000)
                except Exception:
                    time.sleep(2)

            self.page.wait_for_timeout(1500)
            title_el = self.page.locator(f'article[data-job-id="{job_id}"] p.title').first
            # Force same-tab navigation — prevents new-tab taskbar flash
            try:
                self.page.evaluate(
                    "window.open = (url) => { window.location.href = url; return window; };"
                    "document.querySelectorAll('a[target=\"_blank\"]').forEach(a => a.target = '_self');"
                )
            except Exception:
                pass
            title_el.click()
            self._wait_for_page_ready()

            jl = self.page.url
            page_title = self._extract_job_title_from_page()
            page_company = self._extract_company_name_from_page()
            job_title = page_title or listing_title
            company_name = page_company or listing_company

            if self._is_blocked_company(company_name):
                print(f"Skipping blocked company ({company_name}): {job_title or jl}")
                self._save_did_not_apply(f"Blocked company: {company_name}", jl)
                return False
            job_description = self._extract_job_description()
            should_apply, reason = self._is_java_job(job_title, job_description)
            if not should_apply:
                print(f"Skipping job due to filter ({reason}): {job_title or jl}")
                self._save_did_not_apply(reason, jl)
                return False
            apply = self.page.query_selector('#apply-button')
            if not apply:
                if self._is_already_applied():
                    print(f"Already applied, skipping: {job_title or jl}")
                    self._save_did_not_apply("Already applied", jl)
                    return False
                if not re.search(r"\bjava\b", normalize_text(job_description)):
                    print(f"Skipping external apply (no Java in description): {job_title or jl}")
                    self._save_did_not_apply("No Java in description (external)", jl)
                    return False
                external_url = self._click_and_get_company_apply_url() or jl
                self._save_external_apply(job_title or "Unknown", company_name or "Unknown", jl, external_url)
                return False
            if self._is_already_applied():
                print(f"Already applied, skipping: {job_title or jl}")
                self._save_did_not_apply("Already applied", jl)
                return False
            apply.click()
            try:
                expect(self.page.locator(".chatbot_MessageContainer")).to_be_visible(timeout=3000)
                self.cba.classify_new_question()
                self.applied_count += 1
                return True
            except Exception:
                try:
                    expect(self.page).to_have_url(self.pattern)
                    self.applied_count += 1
                    return True
                except Exception:
                    print(f"Skipping job (not applied): {job_title or jl}")
                    self._save_did_not_apply("Apply failed", jl)
                    return False
        except Exception as e:
            print(f"Error on recommended job {job_id} ({listing_title}): {e}")
            return False

    def _apply_recommended_jobs(self, sections=None):
        sections = sections or ["Profile"]
        print(f"\n--- Applying to Recommended Jobs | sections: {sections} ---")
        try:
            jobs_tab_selectors = [
                '.nI-gNb-menuItems__anchor:has-text("Jobs")',
                'a.nI-gNb-menuItems__anchor:has-text("Jobs")',
                '.nI-gNb-header a:has-text("Jobs")',
                'nav a:has-text("Jobs")',
            ]
            hovered = False
            for selector in jobs_tab_selectors:
                try:
                    el = self.page.locator(selector).first
                    if el.count() > 0 and el.is_visible():
                        el.hover()
                        hovered = True
                        print(f"Hovered Jobs tab via: {selector}")
                        break
                except Exception:
                    continue
            if not hovered:
                print("Could not hover over Jobs tab — skipping Recommended Jobs step.")
                return
            time.sleep(0.6)
            rec_selectors = [
                'a:has-text("Recommended Jobs")',
                '.nI-gNb-menuItems__anchorDropdown:has-text("Recommended")',
                'a[href*="recommended"]',
            ]
            clicked = False
            for selector in rec_selectors:
                try:
                    el = self.page.locator(selector).first
                    if el.is_visible():
                        el.click()
                        clicked = True
                        print(f"Clicked Recommended Jobs via: {selector}")
                        break
                except Exception:
                    continue
            if not clicked:
                print("Could not click Recommended Jobs — skipping.")
                return
            self._wait_for_page_ready()
            self.page.wait_for_timeout(2000)
            rec_page_url = self.page.url
            print(f"Recommended Jobs page: {rec_page_url}")

            for section_name in sections:
                if self.applied_count >= self.applno:
                    break
                print(f"\n  -- Section: {section_name} --")
                # Navigate back to recommended page before clicking each section tab
                if rec_page_url not in self.page.url:
                    self.page.goto(rec_page_url)
                    self._wait_for_page_ready()
                if not self._click_recommended_section_tab(section_name):
                    continue
                cards = self._collect_recommended_cards()
                print(f"Found {len(cards)} cards in section '{section_name}'")
                for card in cards:
                    self._check_pause()
                    if self.applied_count >= self.applno:
                        break
                    self._apply_card(card, rec_page_url, section_name)
        except Exception as e:
            print(f"Error during Recommended Jobs step: {e}")

    def _apply_jobs_from_current_page(self):
        """Apply to all jobs listed on the current page using extracted job links."""
        self._wait_for_page_ready()
        for sel in ['.title', 'article.jobTuple', '[class*="jobCard"]', '[class*="job-card"]']:
            try:
                self.page.wait_for_selector(sel, timeout=8000)
                break
            except Exception:
                continue
        job_links = self._extract_job_links_from_page()
        if not job_links:
            print("No job links found on this page.")
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
                self._wait_for_page_ready()
                page_title = self._extract_job_title_from_page()
                page_company = self._extract_company_name_from_page()
                job_title = page_title or listing_title
                company_name = page_company or listing_company
                if self._is_blocked_company(company_name):
                    print(f"Skipping blocked company ({company_name}): {job_title or jl}")
                    self._save_did_not_apply(f"Blocked company: {company_name}", jl)
                    continue
                job_description = self._extract_job_description()
                should_apply, reason = self._is_java_job(job_title, job_description)
                if not should_apply:
                    print(f"Skipping job due to filter ({reason}): {job_title or jl}")
                    self._save_did_not_apply(reason, jl)
                    continue
                apply = self.page.query_selector('#apply-button')
                if not apply:
                    if self._is_already_applied():
                        print(f"Already applied, skipping: {job_title or jl}")
                        self._save_did_not_apply("Already applied", jl)
                        continue
                    if not re.search(r"\bjava\b", normalize_text(job_description)):
                        print(f"Skipping external apply (no Java in description): {job_title or jl}")
                        self._save_did_not_apply("No Java in description (external)", jl)
                        continue
                    external_url = self._click_and_get_company_apply_url() or jl
                    self._save_external_apply(job_title or "Unknown", company_name or "Unknown", jl, external_url)
                    continue
                if self._is_already_applied():
                    print(f"Already applied, skipping: {job_title or jl}")
                    self._save_did_not_apply("Already applied", jl)
                    continue
                apply.click()
                try:
                    expect(self.page.locator(".chatbot_MessageContainer")).to_be_visible(timeout=3000)
                    self.cba.classify_new_question()
                    self.applied_count += 1
                except Exception:
                    try:
                        expect(self.page).to_have_url(self.pattern)
                        self.applied_count += 1
                    except Exception:
                        print(f"Skipping job (not applied): {job_title or jl}")
                        self._save_did_not_apply("Apply failed", jl)
                        continue
            except Exception as e:
                print(jl, "_______", e)
                continue

    def filter_apply(self, s, e='', l='', ja='1', max_pages=None, recommended_sections=None, skip_search=False):
        self.search = s
        if not self.search:
            print("Search keyword required")
            return
        self.experience = e
        self.location = l
        self.jobage = ja
        self.max_pages = max_pages
        self.init_browser()
        self.login()
        self._start_pause_listener()
        time.sleep(1)
        try:
            if recommended_sections is not None:
                self._apply_recommended_jobs(sections=recommended_sections)
            if not skip_search:
                max_restarts = 0 if max_pages else 5
                for attempt in range(max_restarts + 1):
                    if attempt > 0:
                        print(f"\nRestarting search (attempt {attempt}/{max_restarts})...")
                        self.page_no = 1
                    prev_count = self.applied_count
                    self.filter_()
                    self.base_page_url = self.page.url
                    self.apply_()
                    if self.applied_count >= self.applno:
                        break
                    if self.applied_count == prev_count:
                        print("Search exhausted, no new jobs found.")
                        break
        except KeyboardInterrupt:
            print(f"\nStopped by user. Total jobs applied: {self.applied_count}")
        except Exception as e:
            print(f"\nUnexpected error (applied {self.applied_count} so far): {e}")
        finally:
            self.close()
        return {"response": "applied successfully", "applied": self.applied_count}

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
            try:
                botactions = self.bot_actions()
            except KeyboardInterrupt:
                print(f"\nStopped by user. Total jobs applied: {self.applied_count}")
                botactions = {"response": "stopped by user", "applied": self.applied_count}
            finally:
                self._stop_listener = True
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
        try:
            self.browser.close()
        except Exception:
            pass
        try:
            self._playwright.stop()
        except Exception:
            pass

