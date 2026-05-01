import re


NOTICE_PERIOD_BUYOUT_KEYWORDS = (
    "buy out",
    "buyout",
    "buy-out",
)

NOTICE_PERIOD_KEYWORDS = (
    "notice period",
    "when can you join",
    "when can you start",
    "availability to join",
    "available to join",
    "available to start",
    "how soon can you start",
    "how soon can you join",
    "joining availability",
    "can you join",
    "can you start",
    "join immediately",
    "start immediately",
)

CAREER_BREAK_KEYWORDS = (
    "career break",
    "career gap",
    "employment gap",
)

TITLE_KEYWORDS = (
    "title",
    "salutation",
    "address you",
    "prefer to be addressed",
)

MARITAL_STATUS_KEYWORDS = (
    "marital status",
)

HYBRID_WORK_MODEL_KEYWORDS = (
    "hybrid work model",
    "hybrid model",
    "comfortable with hybrid",
    "comfortable with hybrid work",
)

POSITIVE_PREFERENCE_QUESTION_PHRASES = (
    "comfortable with",
    "okay with",
    "ok with",
    "willing to",
    "open to",
    "flexible with",
    "able to work",
    "can work",
    "available for",
)

POSITIVE_PREFERENCE_TOPICS = (
    "hybrid",
    "remote",
    "onsite",
    "on site",
    "work from office",
    "office",
    "wfo",
    "relocate",
    "relocation",
    "travel",
    "travelling",
    "commute",
    "shift",
    "night shift",
    "rotational",
    "weekend",
    "weekends",
    "work model",
    "work arrangement",
    "contractual",
    "contract basis",
    "usd",
    "part time",
    "part-time",
    "hourly",
    "hourly basis",
)

CURRENT_CTC_KEYWORDS = (
    "current ctc",
    "currect ctc",   # typo variant
    "current salary",
    "present ctc",
    "present salary",
    "current cost to company",
    "existing ctc",
    "current annual",
    "current package",
    "currect salary",  # typo variant
)

EXPECTED_CTC_KEYWORDS = (
    "expected ctc",
    "expected annual ctc",
    "expected salary",
    "expected annual salary",
    "expected cost to company",
    "expected annual",
    "expected package",
    "ctc in inr",
    "salary in inr",
    "desired ctc",
    "desired salary",
)

DIRECT_QUESTION_ANSWERS = {
    "are you available to attend one mandatory round of face-to-face interviews?": "Yes",
    "are you available to attend one mandatory round of face-to-face interviews": "Yes",
    "relevant experience in core java (in years) and java version used (java 8 or higher)?": "3.5 years Java 17",
    "relevant experience in core java (in years) and java version used (java 8 or higher)": "3.5 years Java 17",
    "what is your expected annual ctc in inr": "1800000",
    "what is your expected annual ctc in inr ?": "1800000",
    "what is your expected ctc in lacs per annum": "18",
    "what is your expected ctc in lacs per annum ?": "18",
    "what is your current annual ctc in inr": "1400000",
    "what is your current annual ctc in inr ?": "1400000",
    "what is your current ctc in lacs per annum": "14",
    "what is your current ctc in lacs per annum ?": "14",
    "do you have pf for all the companies worked?": "Yes UAN NO - 101848140497",
    "do you have pf for all the companies worked": "Yes UAN NO - 101848140497",
    "variable pay (numeric input only)": "0",
    "variable pay (numeric input only)?": "0",
    "variable pay": "0",
    "how many hours per week are you available to work": "40",
    "how many hours per week are you available to work?": "40",
    "how many hours per week can you work": "40",
    "how many hours per week can you work?": "40",
    "how many years of experience do you have in java and mention java version": "3.5 years, Java 17",
    "how many years of experience do you have in java and mention java version?": "3.5 years, Java 17",
    "reason for job change": "Better growth opportunities and learning exposure",
    "reason for job change?": "Better growth opportunities and learning exposure",
    "reason for change": "Better growth opportunities and learning exposure",
    "reason for change?": "Better growth opportunities and learning exposure",
}

TECH_EXPERIENCE_KEYWORDS = (
    "hibernate",
    "jpa",
)

DISABILITY_KEYWORDS = (
    "disability",
    "disabled",
    "differently abled",
    "special needs",
    "physically challenged",
    "kind of disability",
    "type of disability",
    "do you have any disability",
    "person with disability",
)

DOB_KEYWORDS = (
    "date of birth",
    "birth date",
    "dob",
    "date of birth dd",
    "date of birth mm",
)

RELOCATION_KEYWORDS = (
    "relocate",
    "relocation",
    "willing to move",
    "move to",
    "shift to another",
)

LAST_WORKING_DAY_KEYWORDS = (
    "last working day",
    "last working date",
    "expected last working day",
    "expected last working date",
    "last day of work",
    "last date of employment",
    "relieving date",
    "expected relieving date",
    "last date in",
    "last date at",
    "select last working",
)

POSITIVE_PREFERENCE_BLOCKERS = (
    "experience",
    "notice period",
    "salary",
    "ctc",
    "compensation",
    "bond",
    "buyout",
    "career break",
    "employment gap",
    "previous employee",
    "contractor",
    "intern",
    "authorized",
    "authorization",
    "sponsorship",
    "visa",
    "work permit",
    "citizenship",
    "criminal",
    "convicted",
    "disability",
    "gender",
    "marital status",
    "date of birth",
    "dob",
    "last working day",
    "relieving date",
)

INTERVIEW_AVAILABILITY_KEYWORDS = (
    "face to face",
    "face-to-face",
    "in person interview",
    "in-person interview",
    "inperson interview",
    "available for interview",
    "attend an interview",
    "attend interview",
    "come for interview",
    "appear for interview",
    "walk in interview",
    "walk-in interview",
    "comfortable taking",
    "comfortable attending",
    "online test",
    "aptitude test",
    "assessment test",
    "technical test",
    "coding test",
    "coding round",
)

LOCATION_KEYWORDS = (
    "current location",
    "your location",
    "present location",
    "current city",
    "preferred location",
    "work location",
    "residing city",
    "city of residence",
    "where are you located",
    "where are you based",
    "base location",
    "current base",
    "current loaction",   # common typo
    "your loaction",      # common typo
    "loaction",           # common typo
)

LOCATION_OK_PHRASES = (
    "is it ok",
    "ok for you",
    "okay for you",
    "is that ok",
    "fine for you",
    "fine with you",
    "work for you",
    "suitable for you",
    "comfortable with location",
    "ok with location",
    "ok with",
    "acceptable to you",
)

PAN_KEYWORDS = (
    "pan number",
    "pan card",
    "pan no",
    "pancard",
    "pancard number",
    "share pancard",
    "permanent account number",
    "share your pan",
    "your pan",
    "pan is mandatory",
    "pan mandatory",
)

HOLDING_OFFER_KEYWORDS = (
    "holding any offer",
    "do you have any offer",
    "any offer in hand",
    "have any offer",
    "offers in hand",
    "holding offer",
    "current offer",
    "offer letter",
)

# Yes/No skill questions — "have you used X", "do you know X"
TECH_YESNO_PHRASES = (
    "do you know",
    "have you used",
    "have you worked with",
    "are you familiar with",
    "do you have knowledge",
    "do you have experience with",
    "have you implemented",
    "have you built",
    "can you code",
    "do you code",
    "have you coded",
    "do you understand",
    "have you written",
    "have you developed",
    "are you experienced in",
    "have you used java",
    "have you experience",
    "do you have hands",
    "are you majorly",
    "are you primarily",
    "are you mainly",
    "majorly working in",
    "primarily working in",
    "mainly working in",
)

# If these appear alongside a tech keyword, it's a quantity question not yes/no
EXPERIENCE_QUANTITY_MARKERS = (
    "in years",
    "how many",
    "how long",
    "years of",
    "years exp",
    "months of",
    "number of years",
    "total exp",
    "overall exp",
    "relevant exp",
    "total experience",
    "overall experience",
    "years have you",
)

PREVIOUS_COMPANY_KEYWORDS = (
    "earlier have you worked",
    "have you previously worked",
    "previously worked at",
    "previously worked in",
    "worked at your previous",
    "have you ever worked for",
    "ex employee of",
    "former employee",
    "have you worked in",
    "have you worked at",
    "have you worked with us",
    "worked with us before",
    "have you worked with",
    "worked here before",
)

CURRENT_COMPANY_KEYWORDS = (
    "in which company are you currently",
    "which company are you currently",
    "which company are you working",
    "currently employed at",
    "currently employed in",
    "where are you currently working",
    "your current organization",
    "your current organisation",
    "your current company",
    "current employer",
    "name of your current company",
    "current company name",
    "company you are currently working",
)

JD_RATING_KEYWORDS = (
    "rate yourself",
    "rating on",
    "rate on",
    "scale of 1 to 10",
    "scale of 10",
    "self rating",
    "self-rating",
    "rate yourself on",
    "how do you rate",
    "your rating as per",
    "rate yourself as per jd",
    "rate as per jd",
)

YYMM_FORMAT_KEYWORDS = (
    "in yy mm",
    "yy mm format",
    "format yy mm",
    "yymm",
)

EMAIL_KEYWORDS = (
    "mail id",
    "email id",
    "email address",
    "your email",
    "e mail",
    "mail address",
)

CONDITIONAL_FOLLOWUP_PREFIXES = (
    "if yes,",
    "if yes ",
    "if yes-",
    "if applicable,",
    "if applicable ",
)

EMPLOYEE_ID_KEYWORDS = (
    "employee id",
    "employee number",
    "emp id",
    "staff id",
)

RELATIVE_AT_COMPANY_KEYWORDS = (
    "relative working",
    "relative employed",
    "relative in",
    "any relative",
    "relatives working",
    "family member working",
    "family member employed",
    "do you have relative",
    "do you have any relative",
    "known person working",
    "acquaintance working",
    "know anyone working",
)

PREVIOUSLY_INTERVIEWED_KEYWORDS = (
    "have you interviewed",
    "interviewed before",
    "interviewed with",
    "interviewed in past",
    "interviewed in the past",
    "previously interviewed",
    "applied before",
    "applied previously",
    "applied with us before",
)

GENAI_TOOL_KEYWORDS = (
    "gen ai tool",
    "generative ai tool",
    "ai tool",
    "chatgpt",
    "llm tool",
    "copilot",
    "ai assistant",
    "have you used ai",
    "have you worked on ai",
    "worked on any gen ai",
    "worked on gen ai",
)

HIGHEST_DEGREE_KEYWORDS = (
    "highest degree",
    "highest qualification",
    "highest education",
    "educational qualification",
    "highest level of education",
    "highest academic",
)

# Each inner list is one priority level; earlier lists win.
# normalize_text("M.Tech") → "m tech", ("MSc") → "msc", ("B.Tech") → "b tech", ("BE/Btech") → "be btech"
HIGHEST_DEGREE_PREFERRED_PATTERN_GROUPS = [
    [r"\bm\s*tech\b"],                  # M.Tech / MTech
    [r"\bm\s+s\b", r"\bms\b"],         # M.S — \bms\b won't match "msc" (no word boundary after s)
    [r"\bb\s*tech\b"],                  # B.Tech / Btech (also matches "be btech")
    [r"\bb\s*e\b", r"\bbe\b"],          # B.E / BE
]

IMMEDIATE_NOTICE_KEYWORDS = (
    "immediate joiner",
    "join immediately",
    "available immediately",
    "immediate availability",
    "immediate joining",
    "can join immediately",
    "immediate",
)


def normalize_text(text):
    raw_text = re.sub(r"([a-z])([A-Z])", r"\1 \2", str(text or ""))
    raw_text = raw_text.replace("_", " ")
    raw_text = re.sub(r"(?<=\D)-(?=\D)", " ", raw_text)
    normalized = re.sub(r"[^a-z0-9+\-]+", " ", raw_text.lower())
    return " ".join(normalized.split())


def is_notice_period_buyout_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in NOTICE_PERIOD_BUYOUT_KEYWORDS)


def is_notice_period_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in NOTICE_PERIOD_KEYWORDS)


def is_career_break_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in CAREER_BREAK_KEYWORDS)


def is_title_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in TITLE_KEYWORDS)


def is_marital_status_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in MARITAL_STATUS_KEYWORDS)


def is_hybrid_work_model_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in HYBRID_WORK_MODEL_KEYWORDS)


def is_positive_preference_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    if any(keyword in normalized for keyword in POSITIVE_PREFERENCE_BLOCKERS):
        return False
    has_question_phrase = any(keyword in normalized for keyword in POSITIVE_PREFERENCE_QUESTION_PHRASES)
    has_topic = any(keyword in normalized for keyword in POSITIVE_PREFERENCE_TOPICS)
    return has_question_phrase and has_topic


def is_current_ctc_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in CURRENT_CTC_KEYWORDS)


def is_expected_ctc_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in EXPECTED_CTC_KEYWORDS)


def is_tech_experience_prompt(text, keywords=None):
    normalized = normalize_text(text)
    if not normalized:
        return False
    kw = keywords if keywords is not None else TECH_EXPERIENCE_KEYWORDS
    for keyword in kw:
        if len(keyword) <= 2:
            if re.search(rf'\b{re.escape(keyword)}\b', normalized):
                return True
        else:
            if keyword in normalized:
                return True
    return False


def is_tech_yesno_prompt(text):
    """Yes/No skill questions: 'do you know X', 'have you used X', etc."""
    normalized = normalize_text(text)
    if not normalized:
        return False
    has_phrase = any(phrase in normalized for phrase in TECH_YESNO_PHRASES)
    if not has_phrase:
        return False
    # If the question is asking for a quantity, treat as experience prompt not yes/no
    has_quantity = any(marker in normalized for marker in EXPERIENCE_QUANTITY_MARKERS)
    return not has_quantity


def is_location_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in LOCATION_KEYWORDS)


def is_location_ok_prompt(text):
    """Questions asking if a specific work/office location is acceptable (Yes/No)."""
    normalized = normalize_text(text)
    if not normalized:
        return False
    has_location = "location" in normalized or "office" in normalized
    has_ok = any(phrase in normalized for phrase in LOCATION_OK_PHRASES)
    return has_location and has_ok


def is_pan_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in PAN_KEYWORDS)


def is_holding_offer_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in HOLDING_OFFER_KEYWORDS)


def is_previous_company_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in PREVIOUS_COMPANY_KEYWORDS)


def is_disability_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in DISABILITY_KEYWORDS)


def preferred_disability_text():
    return "No"


def is_dob_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in DOB_KEYWORDS)


def preferred_dob_text():
    return "11/09/1995"


def is_relocation_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in RELOCATION_KEYWORDS)


def is_last_working_day_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    if re.search(r'\blwd\b', normalized):
        return True
    return any(keyword in normalized for keyword in LAST_WORKING_DAY_KEYWORDS)


def is_positive_preference_mode_enabled(user_data):
    raw_value = user_data.get("Positive preference mode", "No")
    return normalize_text(raw_value) in {"yes", "true", "1", "on"}


def preferred_title_text():
    return "Mr."


def preferred_marital_status_text():
    return "Single"


def preferred_hybrid_work_model_text():
    return "Yes"


def preferred_positive_preference_text():
    return "Yes"


def _is_lacs_format(question):
    normalized = normalize_text(question)
    return "lac" in normalized


def preferred_current_ctc_text(question=""):
    return "14" if _is_lacs_format(question) else "1400000"


def preferred_expected_ctc_text(question=""):
    return "18" if _is_lacs_format(question) else "1800000"


def preferred_notice_period_buyout_text():
    return "Yes"


def preferred_last_working_day_text():
    return "31/10/2025"


def preferred_notice_period_text():
    return "0"


def _estimate_notice_days(value, unit):
    normalized_unit = normalize_text(unit)
    if normalized_unit.startswith("week"):
        return value * 7
    if normalized_unit.startswith("month"):
        return value * 30
    return value


def _notice_option_rank(label):
    normalized = normalize_text(label)
    if not normalized:
        return None

    if normalized in {"0", "zero"}:
        return (0, 0.0)
    if any(keyword in normalized for keyword in IMMEDIATE_NOTICE_KEYWORDS):
        return (0, 0.0)
    if re.search(r"\b0\s*days?\b", normalized):
        return (0, 0.0)

    explicit_patterns = (
        r"\b15\s*days?\s*(?:or less|or fewer|or below|at most|maximum|max)?\b",
        r"\bless than\s*15\s*days?\b",
        r"\bwithin\s*15\s*days?\b",
        r"\bup to\s*15\s*days?\b",
        r"\bunder\s*15\s*days?\b",
        r"\b0\s*(?:to|-)\s*15\s*days?\b",
        r"\b1\s*(?:to|-)\s*15\s*days?\b",
        r"\b2\s*weeks?\b",
        r"\btwo\s+weeks?\b",
    )
    if any(re.search(pattern, normalized) for pattern in explicit_patterns):
        return (1, 15.0)

    range_match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months)?\b",
        normalized,
    )
    if range_match:
        upper_bound = float(range_match.group(2))
        unit = range_match.group(3) or ("weeks" if "week" in normalized else "days")
        upper_bound_days = _estimate_notice_days(upper_bound, unit)
        if upper_bound_days <= 15:
            return (1, upper_bound_days)

    bounded_match = re.search(
        r"\b(?:less than|within|up to|under|at most|max(?:imum)?)\s*(\d+(?:\.\d+)?)\s*(day|days|week|weeks)\b",
        normalized,
    )
    if bounded_match:
        value = float(bounded_match.group(1))
        unit = bounded_match.group(2)
        days = _estimate_notice_days(value, unit)
        if days <= 15:
            return (1, days)

    single_match = re.search(r"\b(\d+(?:\.\d+)?)\s*(day|days|week|weeks)\b", normalized)
    if single_match and not re.search(r"\+", normalized):
        if any(marker in normalized for marker in ["more than", "greater than", "at least", "minimum", "or more", "and above"]):
            return None
        value = float(single_match.group(1))
        unit = single_match.group(2)
        days = _estimate_notice_days(value, unit)
        if days <= 15:
            return (2, days)

    return None


def find_preferred_notice_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    best_option = None
    best_rank = None

    for index, option in enumerate(options):
        rank = _notice_option_rank(label_getter(option))
        if rank is None:
            continue

        candidate_rank = (rank[0], rank[1], index)
        if best_rank is None or candidate_rank < best_rank:
            best_rank = candidate_rank
            best_option = option

    return best_option


def find_preferred_title_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    for option in options:
        if re.search(r"\bmr\b", normalize_text(label_getter(option))):
            return option
    return None


def find_preferred_marital_status_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    for pattern in [r"\bsingle\b", r"\bunmarried\b"]:
        for option in options:
            if re.search(pattern, normalize_text(label_getter(option))):
                return option
    return None


def find_preferred_hybrid_work_model_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    for pattern in [r"\byes\b", r"\bagree\b"]:
        for option in options:
            if re.search(pattern, normalize_text(label_getter(option))):
                return option
    for option in options:
        normalized = normalize_text(label_getter(option))
        if re.search(r"\bcomfortable\b", normalized) and "not comfortable" not in normalized:
            return option
    for option in options:
        normalized = normalize_text(label_getter(option))
        if re.search(r"\bopen\b", normalized) and "not open" not in normalized:
            return option
    return None


def find_preferred_positive_preference_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    positive_patterns = [
        r"\byes\b",
        r"\bagree\b",
        r"\bwilling\b",
        r"\bcomfortable\b",
        r"\bopen\b",
        r"\bflexible\b",
        r"\bokay\b",
        r"\bok\b",
        r"\bavailable\b",
    ]
    negative_markers = (
        "no",
        "not",
        "disagree",
        "unwilling",
        "unable",
        "cannot",
        "cant",
        "can't",
        "not comfortable",
        "not open",
        "not available",
        "inflexible",
    )

    for pattern in positive_patterns:
        for option in options:
            normalized = normalize_text(label_getter(option))
            if not re.search(pattern, normalized):
                continue
            if any(marker in normalized for marker in negative_markers):
                continue
            return option
    return None


def is_interview_availability_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in INTERVIEW_AVAILABILITY_KEYWORDS)


def is_conditional_followup_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(normalized.startswith(prefix.strip()) for prefix in CONDITIONAL_FOLLOWUP_PREFIXES)


def is_employee_id_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in EMPLOYEE_ID_KEYWORDS)


def is_highest_degree_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in HIGHEST_DEGREE_KEYWORDS)


def preferred_highest_degree_text():
    return "M.Tech"


def find_preferred_highest_degree_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    for pattern_group in HIGHEST_DEGREE_PREFERRED_PATTERN_GROUPS:
        for option in options:
            norm = normalize_text(label_getter(option))
            if any(re.search(p, norm) for p in pattern_group):
                return option
    return None


def is_yymm_experience_prompt(text):
    """Detects experience questions that ask for answer in YY/MM format."""
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in YYMM_FORMAT_KEYWORDS)


def is_years_of_experience_prompt(text):
    """Detects experience quantity questions regardless of the technology."""
    normalized = normalize_text(text)
    if not normalized:
        return False
    return (
        normalized.startswith("years of experience")
        or normalized.startswith("years of exp")
        or normalized.startswith("how many years of experience")
        or normalized.startswith("how many years of exp")
    )


def is_current_company_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in CURRENT_COMPANY_KEYWORDS)


def is_jd_rating_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in JD_RATING_KEYWORDS)


def is_email_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in EMAIL_KEYWORDS)


def is_relative_at_company_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in RELATIVE_AT_COMPANY_KEYWORDS)


def is_previously_interviewed_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in PREVIOUSLY_INTERVIEWED_KEYWORDS)


def is_genai_tool_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in GENAI_TOOL_KEYWORDS)


def find_preferred_disability_option(options, label_getter=None):
    label_getter = label_getter or (lambda option: option)
    negative_patterns = [r"\bno\b", r"\bnone\b", r"\bnot\b", r"\bdon.?t\b", r"\bwithout\b", r"\bnever\b"]
    for pattern in negative_patterns:
        for option in options:
            norm = normalize_text(label_getter(option))
            if re.search(pattern, norm) and not re.search(r"\byes\b", norm):
                return option
    return None
