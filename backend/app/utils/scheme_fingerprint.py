import re

def scheme_signature(scheme):
    """
    Create a semantic fingerprint for a scheme.
    Used to detect duplicates.
    """
    beneficiary = tuple(sorted(scheme.get("beneficiary_type", [])))
    outcome = scheme.get("policy_outcome", "OTHER")
    state = scheme.get("state", "ALL")

    return (outcome, beneficiary, state)


def detect_ghost_scheme(scheme):
    """
    Heuristic check for possibly outdated (ghost) schemes.
    """
    text = (
        (scheme.get("benefits_text", "") + " " +
         scheme.get("eligibility_text", ""))
        .lower()
    )

    # Look for old years
    years = re.findall(r"\b(19\d{2}|20\d{2})\b", text)
    if years:
        max_year = max(map(int, years))
        if max_year < 2022:
            return True

    # Deprecated wording
    deprecated_terms = ["discontinued", "merged", "no longer applicable"]
    if any(term in text for term in deprecated_terms):
        return True

    return False