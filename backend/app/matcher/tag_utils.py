def normalize_tag(word: str) -> str:
    word = word.lower().strip()

    # 🔥 Employment / Job normalization
    if word in [
        "employement", "employment", "job", "jobs",
        "unemployment", "self", "self-employment"
    ]:
        return "employment"

    # 🔥 Skill / Training normalization
    if word in [
        "training", "skill", "skills", "skilling",
        "apprenticeship", "placement"
    ]:
        return "skill"

    # 🔥 Education normalization
    if word in [
        "education", "school", "college",
        "student", "scholarship"
    ]:
        return "education"

    # 🔥 Farmer normalization
    if word in [
        "farmer", "farming", "agriculture", "kisan"
    ]:
        return "farmer"

    # Default: ignore useless noise words
    if len(word) <= 2:
        return None

    return word


def extract_tag_set(scheme: dict) -> set:
    tags = scheme.get("tags", "")
    category = scheme.get("schemeCategory", "")

    combined = f"{tags} {category}"

    raw_words = (
        combined.lower()
        .replace("&", " ")
        .replace(",", " ")
        .replace("/", " ")
        .split()
    )

    tag_set = set()

    for word in raw_words:
        normalized = normalize_tag(word)
        if normalized:
            tag_set.add(normalized)

    return tag_set
