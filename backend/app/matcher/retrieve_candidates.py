from app.data.intent_map import INTENT_KEYWORDS


def intent_matches(intent, tag_set):
    """
    Checks if user intent loosely matches scheme tags
    """
    if not intent:
        return True

    if not tag_set:
        return False

    keywords = INTENT_KEYWORDS.get(intent, [])
    return any(keyword in tag_set for keyword in keywords)


def retrieve_candidates(schemes, user_profile, limit=50):
    """
    Filters schemes using intent + state + tags
    """
    intent = (user_profile.get("intent") or "").lower()

    user_state = user_profile.get("state")

    candidates = []

    for scheme in schemes:
        tag_set = scheme.get("_tag_set", set())

        # 1️⃣ Intent match (LOOSE, IMPORTANT)
        if not intent_matches(intent, tag_set):
            continue

        # 2️⃣ State match (relaxed for central schemes)
        scheme_state = scheme.get("state", "ALL")
        if scheme_state != "ALL" and user_state:
            if user_state.lower() not in scheme_state.lower():
                continue

        candidates.append(scheme)

        if len(candidates) >= limit:
            break

    return candidates
