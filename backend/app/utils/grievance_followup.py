from app.utils.gemini_client import client

def generate_rejection_followup(user_text: str):
    prompt = f"""
The user says their application was rejected.

Ask them politely to provide:
1. Scheme name
2. Age
3. Gender
4. Category (SC/ST/OBC/General)
5. State
6. List of documents they submitted

IMPORTANT:
- Ask in the SAME language as the user
- Keep it simple
- Do NOT add explanations

User message:
"{user_text}"
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.candidates[0].content.parts[0].text.strip()