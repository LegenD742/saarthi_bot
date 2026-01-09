from app.utils.gemini_client import client


def generate_rejection_followup(user_text: str) -> str:
    """
    Asks the user to provide scheme + personal details + submitted documents
    in a structured format for rejection analysis.
    """

    prompt = f"""
You are a government welfare assistant.

The user says their application was rejected.

Ask them politely to provide the following details
IN ONE MESSAGE and IN A STRUCTURED FORMAT.

You must:
- Ask in the SAME language as the user
- Keep it short and simple
- Do NOT explain reasons
- Do NOT add extra text
- Do NOT ask for sensitive numbers

Ask for exactly these fields:

REJECTION DETAILS:
Scheme:
Age:
Gender:
Category (SC/ST/OBC/General):
State:
Documents submitted:

User message:
"{user_text}"
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.candidates[0].content.parts[0].text.strip()

    except Exception as e:
        print("❌ Rejection followup error:", e)

        return (
            "Please reply in this format:\n\n"
            "REJECTION DETAILS:\n"
            "Scheme:\n"
            "Age:\n"
            "Gender:\n"
            "Category (SC/ST/OBC/General):\n"
            "State:\n"
            "Documents submitted:"
        )
