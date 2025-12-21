from app.matcher.tag_utils import extract_tag_set


def preprocess_schemes(schemes):
    for scheme in schemes:
        scheme["_tag_set"] = extract_tag_set(scheme)
    return schemes
