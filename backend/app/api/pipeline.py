from app.matcher.retrieve_candidates import retrieve_candidates
from app.matcher.ai_eligibility import check_eligibility_with_ai


def find_eligible_schemes(user_profile, schemes):
    candidates = retrieve_candidates(schemes, user_profile)

    results = []

    for scheme in candidates:
        decision = check_eligibility_with_ai(user_profile, scheme)

        if decision["eligible"]:
            results.append({
                "scheme_name": scheme["name"],
                "benefits": scheme.get("benefits_text"),
                "reason": decision["reason"],
                "confidence": decision["confidence"],
                "apply_link": scheme.get("apply_link")
            })

        if len(results) >= 3:
            break

    return results
