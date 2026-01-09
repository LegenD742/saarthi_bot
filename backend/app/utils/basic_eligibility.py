def check_basic_eligibility(user_profile, scheme):
    reasons = []

    rules = scheme.get("eligibility_structured", {})

    age = user_profile.get("age")
    category = user_profile.get("category")
    state = user_profile.get("state")

    min_age = rules.get("min_age")
    max_age = rules.get("max_age")
    allowed_states = rules.get("residence_state", [])

    if age is not None:
        if min_age and age < min_age:
            reasons.append("Age is below the minimum requirement")
        if max_age and age > max_age:
            reasons.append("Age exceeds the maximum limit")

    if allowed_states and state:
        if "ALL" not in allowed_states and state not in allowed_states:
            reasons.append("Scheme is not applicable in your state")

    if reasons:
        return False, reasons

    return True, []