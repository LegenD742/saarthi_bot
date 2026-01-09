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

def normalize_income(income):
    """
    Normalizes income into: low / medium / high
    Accepts numbers or text.
    """

    if income is None:
        return None

    # If already numeric
    if isinstance(income, (int, float)):
        if income <= 72000:
            return "low"
        elif income <= 120000:
            return "medium"
        else:
            return "high"

    # If string
    income_str = str(income).lower().strip()

    # Text-based inputs
    if income_str in ["low", "poor", "below poverty"]:
        return "low"

    if income_str in ["medium", "middle"]:
        return "medium"

    if income_str in ["high", "rich"]:
        return "high"

    # Numeric string
    if income_str.isdigit():
        value = int(income_str)
        if value <= 72000:
            return "low"
        elif value <= 120000:
            return "medium"
        else:
            return "high"

    return None

