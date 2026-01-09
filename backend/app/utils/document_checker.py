def check_documents(submitted_docs, scheme):
    required = scheme.get("documents_text", "").lower()

    missing = []
    incorrect = []

    for doc in ["aadhaar", "income", "caste", "bonafide", "domicile"]:
        if doc in required and doc not in submitted_docs.lower():
            missing.append(doc)

    for doc in submitted_docs.lower().split(","):
        if doc.strip() and doc.strip() not in required:
            incorrect.append(doc.strip())

    return missing, incorrect