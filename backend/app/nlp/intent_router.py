def route_intent(user_profile: dict) -> str:
    """
    Decides which conversational flow to use
    """

    intent = (user_profile.get("intent") or "").lower()

    if intent in ["applicationhelp", "form_help", "apply_help"]:
        return "APPLICATION_HELP"

    return "SCHEME_DISCOVERY"
