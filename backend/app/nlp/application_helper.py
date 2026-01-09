from app.utils.gemini_client import client


def help_with_application(
    user_message: str,
    language: str = "English",
    scheme_name: str | None = None,
    documents_text: str | None = None
):
    """
    Uses Gemini to explain application steps.
    If scheme documents are available, uses them directly.
    """

    if documents_text:
        prompt = f"""
You are a government welfare assistant.

The user needs help filling the application form for the scheme:
"{scheme_name}"

These are the REQUIRED DOCUMENTS for this scheme:
{documents_text}

Your task:
- Explain HOW to use these documents while filling the form
- Explain in SIMPLE step-by-step language
- Assume the user is NOT tech-savvy
- Mention CSC (Common Service Centre) as an offline option
- Do NOT ask for sensitive details
- Respond ONLY in {language}

User message:
"{user_message}"
"""
    else:
        prompt = f"""
You are a government welfare assistant.

The user is confused about filling a government application form.

Your task:
- Explain the GENERAL application process
- Mention common documents usually required
- Keep steps very simple
- Mention CSC as an option
- Respond ONLY in {language}

User message:
"{user_message}"
"""

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    try:
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print("❌ Application help error:", e)
        return (
            "Please visit the nearest CSC (Common Service Centre). "
            "They can help you fill the application form and upload documents."
        )
