def retrieve_candidates(schemes, user_profile, limit=50):
    """
    Retrieve candidate schemes based on beneficiary group (farmer / student).
    Intent keywords are NOT used for hard filtering.
    """

    occupation = user_profile.get("occupation")
    user_state = user_profile.get("state")

    candidates = []

    for scheme in schemes:
        tag_set = scheme.get("_tag_set", set())

        if occupation == "farmer":
            if "farmer" not in tag_set and "agriculture" not in tag_set:
                continue

        elif occupation == "student":
            if "student" not in tag_set and "education" not in tag_set:
                continue

        else:
            continue

        scheme_state = scheme.get("state", "ALL")
        if user_state:
            if scheme_state != "ALL" and user_state.lower() not in scheme_state.lower():
                continue

        candidates.append(scheme)

        if len(candidates) >= limit:
            break

    return candidates
