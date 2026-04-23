import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright
from .answer_utils import (
    find_preferred_hybrid_work_model_option,
    find_preferred_notice_option,
    find_preferred_marital_status_option,
    find_preferred_positive_preference_option,
    find_preferred_title_option,
    is_career_break_prompt,
    is_hybrid_work_model_prompt,
    is_marital_status_prompt,
    is_notice_period_prompt,
    is_positive_preference_mode_enabled,
    is_positive_preference_prompt,
    is_title_prompt,
    preferred_hybrid_work_model_text,
    preferred_marital_status_text,
    preferred_notice_period_text,
    preferred_positive_preference_text,
    preferred_title_text,
)


class CompanySiteBot:
    def __init__(
        self,
        email,
        password=None,
        resume_path=None,
        headless=False,
        linkedin_email=None,
        linkedin_password=None,
    ):
        self.email = email
        self.password = password
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.user_data = self._load_user_data()
        resume_candidate = resume_path or self.user_data.get("Resume path") or os.getenv("JAB_RESUME_PATH")
        self.resume_path = str(Path(resume_candidate).resolve()) if resume_candidate else None
        self.linkedin_email = linkedin_email or os.getenv("JAB_LINKEDIN_EMAIL") or self.email
        self.linkedin_password = linkedin_password or os.getenv("JAB_LINKEDIN_PASSWORD") or self.password
        self.clicked_actions = set()
        self.progress_actions = 0
        self.positive_preference_mode = is_positive_preference_mode_enabled(self.user_data)

    def _load_user_data(self):
        with open("./jab/data/user_data.json", "r", encoding="utf-8") as f:
            return json.load(f)

    def _notice_period_input_value(self, input_type="text"):
        return "15" if input_type in ["number", "tel"] else preferred_notice_period_text()

    def _value_from_label(self, label_text, input_type="text"):
        label = (label_text or "").strip().lower()
        if not label:
            return None
        if is_title_prompt(label):
            return preferred_title_text()
        if is_marital_status_prompt(label):
            return preferred_marital_status_text()
        if is_hybrid_work_model_prompt(label):
            return preferred_hybrid_work_model_text()
        if is_career_break_prompt(label):
            return "No"
        if self.positive_preference_mode and is_positive_preference_prompt(label):
            return preferred_positive_preference_text()

        key_values = {
            "full name": self.user_data.get("Full name"),
            "first name": self.user_data.get("First name"),
            "last name": self.user_data.get("Last name"),
            "email": self.user_data.get("Email", self.email),
            "phone": self.user_data.get("Mobile"),
            "mobile": self.user_data.get("Mobile"),
            "contact number": self.user_data.get("Mobile"),
            "location": self.user_data.get("Location"),
            "city": self.user_data.get("Location"),
            "salary": self.user_data.get("Current salary"),
            "ctc": self.user_data.get("Current CTC"),
            "expected salary": self.user_data.get("Expected salary"),
            "notice period": self.user_data.get("Notice period"),
            "experience": self.user_data.get("Total experience"),
            "gender": self.user_data.get("Gender"),
            "dob": self.user_data.get("Date of birth"),
            "date of birth": self.user_data.get("Date of birth"),
            "preferred work location": self.user_data.get("Preferred work location"),
            "career break": self.user_data.get("Are you on a career break?", "No"),
            "previous employee": self.user_data.get("Are you a Previous Employee, Intern, Or Contractor?", "No"),
            "password": self.password,
            "linkedin email": self.linkedin_email,
            "linkedin password": self.linkedin_password,
        }

        for key, value in key_values.items():
            if key in label and value not in [None, ""]:
                return str(value)

        if input_type == "email":
            return str(self.user_data.get("Email", self.email))
        if input_type in ["tel", "number"]:
            return str(self.user_data.get("Mobile", ""))
        if "name" in label:
            return str(self.user_data.get("Full name", ""))
        return None

    def _safe_label(self, page, el):
        attrs = []
        for attr in ["aria-label", "placeholder", "name", "id"]:
            value = el.get_attribute(attr)
            if value:
                attrs.append(value)
        label_text = " ".join(attrs)

        el_id = el.get_attribute("id")
        if el_id:
            label_node = page.locator(f'label[for="{el_id}"]').first
            if label_node.count() > 0:
                try:
                    label_text = f"{label_text} {label_node.inner_text().strip()}".strip()
                except Exception:
                    pass
        return label_text

    def _fill_file_inputs(self, page):
        if not self.resume_path:
            return
        file_inputs = page.locator('input[type="file"]')
        count = file_inputs.count()
        for i in range(count):
            try:
                node = file_inputs.nth(i)
                node.set_input_files(self.resume_path)
            except Exception:
                continue

    def _fill_textual_inputs(self, page):
        fields = page.locator(
            'input:not([type="hidden"]):not([type="file"]):not([type="checkbox"]):not([type="radio"]), textarea'
        )
        count = fields.count()
        for i in range(count):
            try:
                node = fields.nth(i)
                if not node.is_visible() or node.is_disabled():
                    continue

                input_type = (node.get_attribute("type") or "text").lower()
                label_text = self._safe_label(page, node)
                if is_notice_period_prompt(label_text):
                    value = self._notice_period_input_value(input_type=input_type)
                else:
                    value = self._value_from_label(label_text, input_type=input_type)
                if not value:
                    continue

                current = node.input_value().strip()
                if current:
                    continue
                node.fill(value)
            except Exception:
                continue

    def _fill_selects(self, page):
        selects = page.locator("select")
        for i in range(selects.count()):
            try:
                sel = selects.nth(i)
                if not sel.is_visible() or sel.is_disabled():
                    continue
                label = self._safe_label(page, sel)

                options = sel.locator("option")
                special_option = None
                if is_notice_period_prompt(label):
                    notice_options = []
                    for j in range(options.count()):
                        option = options.nth(j)
                        notice_options.append(
                            {
                                "label": (option.inner_text() or "").strip(),
                                "value": option.get_attribute("value"),
                            }
                        )
                    special_option = find_preferred_notice_option(notice_options, label_getter=lambda option: option["label"])
                elif is_title_prompt(label):
                    title_options = []
                    for j in range(options.count()):
                        option = options.nth(j)
                        title_options.append(
                            {
                                "label": (option.inner_text() or "").strip(),
                                "value": option.get_attribute("value"),
                            }
                        )
                    special_option = find_preferred_title_option(title_options, label_getter=lambda option: option["label"])
                elif is_marital_status_prompt(label):
                    marital_options = []
                    for j in range(options.count()):
                        option = options.nth(j)
                        marital_options.append(
                            {
                                "label": (option.inner_text() or "").strip(),
                                "value": option.get_attribute("value"),
                            }
                        )
                    special_option = find_preferred_marital_status_option(
                        marital_options, label_getter=lambda option: option["label"]
                    )
                elif is_hybrid_work_model_prompt(label):
                    hybrid_options = []
                    for j in range(options.count()):
                        option = options.nth(j)
                        hybrid_options.append(
                            {
                                "label": (option.inner_text() or "").strip(),
                                "value": option.get_attribute("value"),
                            }
                        )
                    special_option = find_preferred_hybrid_work_model_option(
                        hybrid_options, label_getter=lambda option: option["label"]
                    )
                elif self.positive_preference_mode and is_positive_preference_prompt(label):
                    positive_options = []
                    for j in range(options.count()):
                        option = options.nth(j)
                        positive_options.append(
                            {
                                "label": (option.inner_text() or "").strip(),
                                "value": option.get_attribute("value"),
                            }
                        )
                    special_option = find_preferred_positive_preference_option(
                        positive_options, label_getter=lambda option: option["label"]
                    )
                if special_option:
                    if special_option["value"] not in [None, ""]:
                        sel.select_option(special_option["value"])
                    elif special_option["label"]:
                        sel.select_option(label=special_option["label"])
                    continue

                target = (self._value_from_label(label) or "").strip().lower()
                if not target:
                    continue

                matched = False
                for j in range(options.count()):
                    txt = (options.nth(j).inner_text() or "").strip().lower()
                    if target and target in txt:
                        option_value = options.nth(j).get_attribute("value")
                        if option_value:
                            sel.select_option(option_value)
                            matched = True
                            break
                if not matched and options.count() > 1:
                    fallback = options.nth(1).get_attribute("value")
                    if fallback:
                        sel.select_option(fallback)
            except Exception:
                continue

    def _toggle_checkboxes_and_radios(self, page):
        checks = page.locator('input[type="checkbox"]')
        for i in range(checks.count()):
            try:
                c = checks.nth(i)
                if not c.is_visible() or c.is_disabled():
                    continue
                label = self._safe_label(page, c).lower()
                should_check = any(k in label for k in ["agree", "consent", "privacy", "terms"])
                if should_check and not c.is_checked():
                    c.check(force=True)
            except Exception:
                continue

        radios = page.locator('input[type="radio"]')
        radio_groups = {}
        for i in range(radios.count()):
            try:
                r = radios.nth(i)
                if not r.is_visible() or r.is_disabled():
                    continue
                group_name = r.get_attribute("name") or f"radio-{i}"
                radio_groups.setdefault(group_name, []).append(
                    {"el": r, "label": self._safe_label(page, r), "group_name": group_name}
                )
            except Exception:
                continue

        handled_groups = set()
        for group_name, options in radio_groups.items():
            try:
                preferred_option = None
                option_context = lambda option: f"{option['group_name']} {option['label']}".strip()
                if any(is_notice_period_prompt(option_context(option)) for option in options):
                    preferred_option = find_preferred_notice_option(options, label_getter=option_context)
                elif any(is_title_prompt(option_context(option)) for option in options):
                    preferred_option = find_preferred_title_option(options, label_getter=option_context)
                elif any(is_marital_status_prompt(option_context(option)) for option in options):
                    preferred_option = find_preferred_marital_status_option(
                        options, label_getter=option_context
                    )
                elif any(is_hybrid_work_model_prompt(option_context(option)) for option in options):
                    preferred_option = find_preferred_hybrid_work_model_option(
                        options, label_getter=option_context
                    )
                elif self.positive_preference_mode and any(
                    is_positive_preference_prompt(option_context(option)) for option in options
                ):
                    preferred_option = find_preferred_positive_preference_option(
                        options, label_getter=option_context
                    )
                if preferred_option:
                    handled_groups.add(group_name)
                if preferred_option and not preferred_option["el"].is_checked():
                    preferred_option["el"].check(force=True)
            except Exception:
                continue

        for group_name, options in radio_groups.items():
            if group_name in handled_groups:
                continue
            for option in options:
                try:
                    label = option["label"].lower()
                    option_context = f"{option['group_name']} {option['label']}".strip().lower()
                    if any(k in label for k in ["no", "not", "false"]) and is_career_break_prompt(option_context):
                        option["el"].check(force=True)
                    if (
                        any(k in label for k in ["no", "not", "false"])
                        and "previous employee" in option_context
                        and "intern" in option_context
                        and "contractor" in option_context
                    ):
                        option["el"].check(force=True)
                except Exception:
                    continue

    def _click_by_text(self, page, patterns):
        compiled = [re.compile(p, re.I) for p in patterns]
        candidates = page.locator('button, a, [role="button"], input[type="submit"], input[type="button"]')
        for i in range(candidates.count()):
            try:
                c = candidates.nth(i)
                if not c.is_visible() or c.is_disabled():
                    continue
                txt = ((c.inner_text() or "").strip() or (c.get_attribute("value") or "").strip()).lower()
                if not txt:
                    continue
                if not any(r.search(txt) for r in compiled):
                    continue
                action_key = f"{page.url}|{txt}"
                if action_key in self.clicked_actions:
                    continue
                self.clicked_actions.add(action_key)
                c.click(timeout=3000)
                page.wait_for_timeout(1200)
                self.progress_actions += 1
                return True
            except Exception:
                continue
        return False

    def _maybe_login_linkedin(self, page):
        url = (page.url or "").lower()
        on_linkedin = "linkedin.com" in url
        has_login_form = page.locator("#username").count() > 0 and page.locator("#password").count() > 0
        if not on_linkedin and not has_login_form:
            return False
        if not self.linkedin_email or not self.linkedin_password:
            return False
        try:
            user = page.locator("#username")
            pwd = page.locator("#password")
            if user.count() > 0 and user.first.is_visible():
                if not user.first.input_value().strip():
                    user.first.fill(self.linkedin_email)
            if pwd.count() > 0 and pwd.first.is_visible():
                if not pwd.first.input_value().strip():
                    pwd.first.fill(self.linkedin_password)
            self._click_by_text(page, [r"sign in", r"log in", r"continue"])
            return True
        except Exception:
            return False

    def _prefer_linkedin_apply(self, page):
        return self._click_by_text(
            page,
            [
                r"apply with linkedin",
                r"apply via linkedin",
                r"linkedin easy apply",
                r"linkedin",
            ],
        )

    def _fill_page_once(self, page):
        self._fill_textual_inputs(page)
        self._fill_selects(page)
        self._fill_file_inputs(page)
        self._toggle_checkboxes_and_radios(page)

    def _process_page(self, page):
        try:
            page.bring_to_front()
        except Exception:
            pass
        try:
            page.wait_for_load_state("domcontentloaded", timeout=7000)
        except Exception:
            pass

        self._prefer_linkedin_apply(page)
        self._maybe_login_linkedin(page)
        self._fill_page_once(page)
        self._click_by_text(page, [r"sign[\s-]?up", r"register", r"create account"])
        self._fill_page_once(page)
        self._click_by_text(page, [r"apply", r"easy apply", r"continue", r"next", r"proceed"])
        self._maybe_login_linkedin(page)
        self._fill_page_once(page)
        self._click_by_text(page, [r"submit", r"send application", r"finish", r"complete application"])

    def apply_in_context(self, context, cycles=6):
        before = self.progress_actions
        for _ in range(cycles):
            pages = list(context.pages)
            for p in pages:
                if p.is_closed():
                    continue
                self._process_page(p)
            if pages:
                pages[0].wait_for_timeout(1500)
        return self.progress_actions > before

    def apply_on_url(self, url, cycles=6):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, args=["--disable-blink-features=AutomationControlled"]
        )
        self.context = self.browser.new_context()
        page = self.context.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_timeout(1200)

        return self.apply_in_context(self.context, cycles=cycles)

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
