

# import json
# from app.utils.gemini_client import client


# def extract_entities_with_gemini(user_text: str):
#     prompt = f"""
#     You are a system extracting structured information for a government welfare assistant. only extract these fields,
#     Extract the following fields fron the message:
#     - age (number or null)
#     - gender (male/female/transgender or null)
#     - category (SC/ST/OBC/GENERAL or null)
#     - state (Indian state/union territory or null)
#     - income_level (low/middle/high or any number given or null)
#     - occupation (string or null)
#     - marital status(married/single/widow/widower or null)
#     - intent (Medicine/Scholarship/Senior Citizen/Award/Crime/Women/Violence/Harrassment/LIC/Insurance Coverage/Financial/Security/education/health/agriculture/employment/housing/pension/etc. basically what he wants from the government scheme)

#     Return ONLY a valid JSON. nothing else at all no explanations nothing.

#     User message:
#         \"\"\"{user_text}\"\"\"
#         """

#     response = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=prompt,
#     )

#     # 🔹 SAFE TEXT EXTRACTION
#     try:
#         text = response.candidates[0].content.parts[0].text
#         return json.loads(text)
#     except Exception as e:
#         print("❌ Gemini parsing error:", e)
#         print("Raw response:", response)

#         # Fallback (never crash API)
#         return {
#             "age": None,
#             "gender": None,
#             "category": None,
#             "state": None,
#             "income_level": None,
#             "occupation": None,
#             "intent": None
#         }


import json
import re
from app.utils.gemini_client import client


def clean_json(text: str):
    """
    Removes ```json ``` wrappers if present
    """
    text = text.strip()

    # Remove ```json and ``` if present
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*", "", text)
        text = text.replace("```", "")

    return text.strip()


def extract_entities_with_gemini(user_text: str):
    prompt = f"""
Extract user details from the message below.
Return ONLY JSON. Do not add markdown.No explanations
Required fields:- age (number or null)
    - gender (male/female/transgender or null)
    - category (SC/ST/OBC/GENERAL or null)
    - state (Indian state/union territory or null)
    - income_level (low/middle/high or any number given or null)
    - occupation (string or null)
    - marital status(married/single/widow/widower or null)
    - intent (Medicine/Scholarship/Senior Citizen/Award/Crime/Women/Violence/Harrassment/LIC/Insurance Coverage/Financial/Security/education/health/agriculture/employment/housing/pension/etc. basically what he wants from the government scheme)



User message:
\"\"\"{user_text}\"\"\"
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
