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
)

CURRENT_CTC_KEYWORDS = (
    "current ctc",
    "current salary",
    "present ctc",
    "present salary",
    "current cost to company",
    "existing ctc",
    "current annual",
    "current package",
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
    "what is your expected annual ctc in inr": "2000000",
    "what is your expected annual ctc in inr ?": "2000000",
    "what is your expected ctc in lacs per annum": "20",
    "what is your expected ctc in lacs per annum ?": "20",
    "what is your current annual ctc in inr": "1350000",
    "what is your current annual ctc in inr ?": "1350000",
    "what is your current ctc in lacs per annum": "13.5",
    "what is your current ctc in lacs per annum ?": "13.5",
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
    "expected last working day",
    "last day of work",
    "last date of employment",
    "relieving date",
    "expected relieving date",
    "last date in",
    "last date at",
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
    return any(keyword in normalized for keyword in kw)


def is_disability_prompt(text):
    normalized = normalize_text(text)
    if not normalized:
        return False
    return any(keyword in normalized for keyword in DISABILITY_KEYWORDS)


def preferred_disability_text():
    return "No disability"


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
    return "13.5" if _is_lacs_format(question) else "1350000"


def preferred_expected_ctc_text(question=""):
    return "20" if _is_lacs_format(question) else "2000000"


def preferred_notice_period_buyout_text():
    return "Yes"


def preferred_last_working_day_text():
    return "31/10/2025"


def preferred_notice_period_text():
    return "15 days or less"


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
