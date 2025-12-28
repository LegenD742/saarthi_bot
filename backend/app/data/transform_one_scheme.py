import re


def extract_age_range(text):
    """
    Extracts age range like '18-60 years' from eligibility text
    """
    match = re.search(r"(\d{1,2})\s*-\s*(\d{1,2})\s*years", text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None


def extract_state(text):
    """
    Extract state from text (basic version)
    """
    states = ["puducherry", "andhra pradesh", "uttar pradesh", "madhya pradesh"]
    for state in states:
        if state in text.lower():
            return state.title()
    return None


def extract_occupation(tags):
    if "fisherman" in tags.lower():
        return ["fisherman"]
    return []


def transform_scheme(raw):
    min_age, max_age = extract_age_range(raw.get("eligibility", ""))
    state = extract_state(raw.get("eligibility", ""))
    occupation = extract_occupation(raw.get("tags", ""))

    transformed = {
        "id": raw.get("slug"),
        "name": raw.get("scheme_name"),
        "level": raw.get("level"),
        "state": state or "ALL",

        "sector": ["social_welfare"],
        "beneficiary_type": occupation or ["citizen"],

        "eligibility_structured": {
            "min_age": min_age,
            "max_age": max_age,
            "gender": "any",
            "category": None,
            "occupation": occupation,
            "income_level": None,
            "residence_state": [state] if state else ["ALL"]
        },

        "benefits_text": raw.get("benefits"),
        "eligibility_text": raw.get("eligibility"),
        "details_text": raw.get("details"),
        "documents_text": raw.get("documents", ""),
        "tags": raw.get("tags")
    }

    return transformed
