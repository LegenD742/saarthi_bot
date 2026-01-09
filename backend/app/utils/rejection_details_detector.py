def looks_like_rejection_details(message: str) -> bool:
    """
    Detects if message looks like rejection details:
    scheme name + personal details + documents
    """
    if not message:
        return False

    msg = message.lower()

    indicators = [
        "scheme",
        "male", "female",
        "sc", "st", "obc", "general",
        "aadhaar", "aadhar",
        "certificate",
        "card",
        "documents",
        "state",
    ]

    score = sum(1 for word in indicators if word in msg)

    return score >= 3
