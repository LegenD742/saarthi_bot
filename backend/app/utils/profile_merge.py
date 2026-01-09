def merge_profiles(old: dict, new: dict) -> dict:
    """
    Merge non-null values from new profile into old profile
    """
    if not old:
        return new

    merged = old.copy()

    for key, value in new.items():
        if value not in [None, "", []]:
            merged[key] = value

    return merged
