def normalize_occupation(occupation):
    """
    Normalize occupation ONLY for farmers.
    Students are NOT normalized.
    """
    if not occupation:
        return None

    occupation = occupation.lower().strip()

    FARMER_WORDS = [
        "farmer",
        "kisan",
        "kisaan",
        "agriculturist",
        "agriculture worker"
    ]

    if occupation in FARMER_WORDS:
        return "farmer"

    return occupation


def normalize_intent(intent):
    """
    Normalize intent ONLY when it clearly refers to farmer-related needs.
    Student intents are left untouched.
    """
    if not intent:
        return None

    intent = intent.lower().strip()

    FARMER_INTENTS = [
        "insurance",
        "insurance coverage",
        "life insurance",
        "death cover",
        "accident insurance",
        "financial",
        "money",
        "monetary"
    ]

    if intent in FARMER_INTENTS:
        return "farmer"

    return intent
