def find_alternate_schemes(
    schemes,
    rejected_scheme,
    user_profile,
    limit=3
):
    """
    Finds alternate schemes the user may be eligible for
    based on intent, state, and broad tags.
    """

    intent = (user_profile.get("intent") or "").lower()
    user_state = user_profile.get("state")

    alternatives = []

    for scheme in schemes:
        # Skip the rejected scheme itself
        if scheme.get("name") == rejected_scheme.get("name"):
            continue

        # Intent / tag match (loose)
        tag_set = scheme.get("_tag_set", set())
        if intent and not any(intent in tag for tag in tag_set):
            continue

        # State applicability check
        scheme_state = scheme.get("state", "ALL")
        if scheme_state != "ALL" and user_state:
            if user_state.lower() not in scheme_state.lower():
                continue

        alternatives.append(scheme)

        if len(alternatives) >= limit:
            break

    return alternatives
