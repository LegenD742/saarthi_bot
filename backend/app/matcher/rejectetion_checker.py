def analyze_rejection(user_input: dict, scheme: dict):
    """
    Compares user details & submitted documents with scheme requirements
    """

    issues = []

    # ---- AGE CHECK ----
    eligibility = scheme.get("eligibility_structured", {})
    min_age = eligibility.get("min_age")
    max_age = eligibility.get("max_age")

    user_age = user_input.get("age")

    if min_age and user_age and user_age < min_age:
        issues.append(f"Minimum age required is {min_age}")

    if max_age and user_age and user_age > max_age:
        issues.append(f"Maximum age allowed is {max_age}")

    # ---- CATEGORY CHECK ----
    scheme_category = eligibility.get("category")
    user_category = user_input.get("category")

    if scheme_category and user_category:
        if user_category not in scheme_category:
            issues.append(
                f"Scheme is for {scheme_category}, but you applied as {user_category}"
            )

    # ---- STATE CHECK ----
    scheme_states = eligibility.get("residence_state", [])
    user_state = user_input.get("state")

    if scheme_states and user_state:
        if "ALL" not in scheme_states and user_state not in scheme_states:
            issues.append(
                f"Scheme is not applicable in {user_state}"
            )

    # ---- DOCUMENT CHECK ----
    required_docs_text = scheme.get("documents_text", "").lower()
    submitted_docs = user_input.get("submitted_documents", [])

    missing_docs = []
    for doc in ["income certificate", "caste certificate", "aadhaar", "bank account"]:
        if doc in required_docs_text:
            if not any(doc in d.lower() for d in submitted_docs):
                missing_docs.append(doc)

    if missing_docs:
        issues.append(
            "Missing required documents: " + ", ".join(missing_docs)
        )

    return issues
