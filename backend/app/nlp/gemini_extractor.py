import json
import re
from app.utils.gemini_client import client


def clean_json(text: str):
    """
    Removes ```json ``` wrappers if present
    """
    text = text.strip()

    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = text.replace("```", "")

    return text.strip()


def extract_entities_with_gemini(user_text: str):
    prompt = f"""
        You are an AI assistant extracting user details for a government welfare assistant.

        IMPORTANT INTENT RULES:
    - If the user is asking for money, help, fees, or support for education → intent = "Scholarship"(capital S)
    - If the user is talking about education in general without money → intent = "education"
    - If the user is a farmer or mentions agriculture → intent = "farmer"
    - if the person is asking for job/employement the tag is "Employment"
    - if the user is asking the help for any help for the application filling or form filling or documentation help the intent is "applicationhelp"
    - if a person says that there application got rejected or that they were sent back by the government officer then intent is "rejectioncheck" 

Return ONLY valid JSON. No markdown.

Fields:
age, gender, category, state, income_level, occupation, intent

User message:
"{user_text}"

JSON:
"""


    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )

    try:
        raw_text = response.candidates[0].content.parts[0].text
        cleaned = clean_json(raw_text)
        return json.loads(cleaned)

    except Exception as e:
        print("❌ Gemini parsing error:", e)
        print("Raw Gemini text:", raw_text)

        return {
            "age": None,
            "gender": None,
            "category": None,
            "state": None,
            "income_level": None,
            "occupation": None,
            "intent": None
        }
