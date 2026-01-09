def retrieve_candidates(schemes, user_profile, limit=50):
    """
    Retrieve candidate schemes with intent-aware filtering.
    """

    occupation = user_profile.get("occupation")
    intent = user_profile.get("intent")
    user_state = user_profile.get("state")

    candidates = []

    for scheme in schemes:
        tag_set = scheme.get("_tag_set", set())

        # -----------------------------
        # 🔹 Occupation-based filtering
        # -----------------------------
        if occupation == "farmer":
            if not {"farmer", "agriculture"}.intersection(tag_set):
                continue

        elif occupation == "student":
            if not {"student", "education", "scholarship"}.intersection(tag_set):
                continue

        # -----------------------------
        # 🔹 Intent-based filtering
        # -----------------------------
        if intent == "employment":
            if not {
                "employment",
                "unemployed",
                "job",
                "jobs",
                "skill",
                "training",
                "youth",
                "entrepreneur"
            }.intersection(tag_set):
                continue

        elif intent == "Scholarship":
            if not {"education", "student", "scholarship"}.intersection(tag_set):
                continue

        # -----------------------------
        # 🌍 State filter (ALL always allowed)
        # -----------------------------
        scheme_state = scheme.get("state", "ALL")
        if scheme_state and scheme_state.upper() != "ALL":
            if user_state and user_state.lower() not in scheme_state.lower():
                continue

        candidates.append(scheme)

        # 🔍 Debug (safe to remove later)
        print(scheme["name"], scheme["_tag_set"], scheme.get("state"))

        if len(candidates) >= limit:
            break

    return candidates
