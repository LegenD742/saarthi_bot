def get_missing_fields(user_profile: dict):
    missing = []

    if user_profile.get("age") is None:
        missing.append("age")

    if user_profile.get("gender") is None:
        missing.append("gender")

    if user_profile.get("category") is None:
        missing.append("category")

    if user_profile.get("state") is None:
        missing.append("state")

    if user_profile.get("income_level") is None:
        missing.append("income")

    return missing
