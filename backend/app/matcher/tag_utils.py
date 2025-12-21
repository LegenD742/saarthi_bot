def normalize_text(text: str):
    return text.lower().strip()


def extract_tag_set(scheme):
    tags = scheme.get("tags", "")
    category = scheme.get("schemeCategory", "")

    combined = f"{tags} {category}"
    words = combined.lower().replace("&", " ").replace(",", " ").split()

    return set(words)
