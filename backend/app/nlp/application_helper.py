from app.nlp.gemini_client import get_gemini_response


def help_with_application(user_message: str, language: str = "English"):
    """
    Uses AI to explain application form steps in simple language
    """

    prompt = f"""
You are a government scheme assistant.

The user is asking for help with filling an application form.
Explain the process in SIMPLE, step-by-step language.
Assume the user is NOT tech-savvy.

Rules:
- Do NOT ask for Aadhaar numbers or sensitive data
- Mention CSC (Common Service Centre) as an option
- Keep language very simple
- Respond in {language}

User message:
"{user_message}"
"""

    return get_gemini_response(prompt)
