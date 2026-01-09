import re


def extract_required_documents(doc_text: str):
    """
    Extract required documents from scheme.documents_text
    """
    if not doc_text:
        return []

    text = doc_text.lower()

    # Common cleanup
    text = text.replace(":", " ")
    text = text.replace("(", " ").replace(")", " ")

    # Split on bullets, commas, newlines, semicolons
    parts = re.split(r"[•,\n;/]", text)

    required_docs = []
    for p in parts:
        p = p.strip()
        if len(p) > 3:
            required_docs.append(p)

    return required_docs


def normalize_doc_name(doc: str):
    """
    Normalize document names for comparison
    """
    doc = doc.lower().strip()

    replacements = {
        "aadhar": "aadhaar",
        "aadhaar card": "aadhaar",
        "pan card": "pan",
        "voter id": "voter",
        "birth certificate": "birth",
        "income certificate": "income",
        "caste certificate": "caste",
        "domicile certificate": "domicile",
        "disability certificate": "disability",
        "passport size photo": "photo",
    }

    for k, v in replacements.items():
        if k in doc:
            return v

    return doc


def analyze_rejection(user_profile, scheme):
    """
    Compare user submitted documents against scheme.documents_text.
    Returns list of rejection reasons.
    """
    issues = []

    submitted_docs = user_profile.get("submitted_documents", [])
    if not submitted_docs:
        return ["No documents were submitted."]

    submitted_norm = [
        normalize_doc_name(d) for d in submitted_docs
    ]

    required_docs_raw = extract_required_documents(
        scheme.get("documents_text", "")
    )

    if not required_docs_raw:
        # Scheme does not specify documents clearly
        return []

    required_norm = [
        normalize_doc_name(d) for d in required_docs_raw
    ]

    missing = []
    for req in required_norm:
        if not any(req in s for s in submitted_norm):
            missing.append(req)

    if missing:
        issues.append(
            "Missing required documents: " + ", ".join(missing)
        )

    return issues
