import re


COMMON_DOCUMENTS = [
    "aadhaar", "aadhar",
    "income certificate",
    "caste certificate",
    "birth certificate",
    "death certificate",
    "ration card",
    "bank passbook",
    "domicile certificate",
    "residence proof",
]


def extract_scheme_and_docs(message: str):
    """
    Extract scheme name and submitted documents from free text
    """
    msg = message.lower()

    # ---- Extract documents ----
    documents = []
    for doc in COMMON_DOCUMENTS:
        if doc in msg:
            documents.append(doc)

    # ---- Extract scheme name (everything before first comma) ----
    scheme_name = message.split(",")[0].strip()

    return scheme_name, documents
