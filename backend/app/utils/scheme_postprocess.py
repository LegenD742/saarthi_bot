def group_duplicate_schemes(schemes):
    """
    Groups duplicate schemes for clean output.
    """
    grouped = {}
    result = []

    for s in schemes:
        key = s.get("duplicate_of") or s.get("name")

        if key not in grouped:
            grouped[key] = {
                "main": s,
                "duplicates": []
            }
        else:
            grouped[key]["duplicates"].append(s)

    for item in grouped.values():
        main = item["main"]
        duplicates = item["duplicates"]

        if duplicates:
            main["duplicate_variants"] = [
                d.get("name") for d in duplicates
            ]

        result.append(main)

    return result