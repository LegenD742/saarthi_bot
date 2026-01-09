import re


def extract_required_documents(documents_text: str):
    """
    Extracts document names from documents_text (simple heuristic)
    """
    if not documents_text:
        return []

    common_docs = [
        "aadhaar",
        "income certificate",
        "caste certificate",
        "bank account",
        "domicile",
        "residence proof",
        "age proof",
        "ration card",
        "death certificate"
    ]

    text = documents_text.lower()
    return [doc for doc in common_docs if doc in text]


def analyze_rejection(user_profile: dict, scheme: dict):
    """
    Returns list of issues found
    """
    issues = []

    eligibility = scheme.get("eligibility_structured", {})

    # ---- AGE ----
    age = user_profile.get("age")
    min_age = eligibility.get("min_age")
    max_age = eligibility.get("max_age")

    if age:
        if min_age and age < min_age:
            issues.append(f"Minimum age required is {min_age}")
        if max_age and age > max_age:
            issues.append(f"Maximum age allowed is {max_age}")

    # ---- CATEGORY ----
    scheme_category = eligibility.get("category")
    user_category = user_profile.get("category")

    if scheme_category and user_category:
        if user_category not in scheme_category:
            issues.append(
                f"Scheme is for {scheme_category}, but you applied as {user_category}"
            )

    # ---- STATE ----
    allowed_states = eligibility.get("residence_state", [])
    user_state = user_profile.get("state")

    if allowed_states and user_state:
        if "ALL" not in allowed_states and user_state not in allowed_states:
            issues.append(
                f"Scheme not applicable in {user_state}"
            )

    # ---- DOCUMENTS ----
    submitted_docs = user_profile.get("submitted_documents", [])
    required_docs = extract_required_documents(
        scheme.get("documents_text", "")
    )

    missing_docs = []
    for doc in required_docs:
        if not any(doc in d.lower() for d in submitted_docs):
            missing_docs.append(doc)

    if missing_docs:
        issues.append(
            "Missing required documents: " + ", ".join(missing_docs)
        )

    return issues
