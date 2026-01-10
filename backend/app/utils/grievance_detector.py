REJECTION_KEYWORDS = [
    "rejected",
    "rejection",
    "not approved",
    "application failed",
    "declined",
    "deny",
    "not accepted",
    "rejected",
        "application rejected",
        "not accepted",
        "got rejected",
        "form rejected",
        "application failed",
        "documents rejected",
]

def is_rejection_message(text: str) -> bool:
    text = text.lower()
    return any(word in text for word in REJECTION_KEYWORDS)