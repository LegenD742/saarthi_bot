import json
from app.utils.gemini_client import client


def check_eligibility_with_ai(user_profile, scheme):
    prompt = f"""
You are evaluating POSSIBLE eligibility for an Indian government scheme.

USER PROFILE (may be incomplete):
{user_profile}

SCHEME ELIGIBILITY TEXT:
{scheme.get("eligibility_text", "")}

DECISION RULES (FOLLOW STRICTLY):
1. If the user CLEARLY does not meet a requirement stated in the text → eligible = false
2. If the user MAY meet the requirements but some information is missing → eligible = true
3. If the text does not contradict the user profile → eligible = true

IMPORTANT:
- DO NOT return eligible=false just because information is missing
- DO NOT say "unable to determine eligibility"
- When in doubt, mark eligible = true with low confidence

Respond ONLY in valid JSON (no markdown):

{{
  "eligible": true or false,
  "confidence": "high" or "medium" or "low",
  "reason": "short explanation referring to the scheme text"
}}
"""


    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    try:
        text = response.candidates[0].content.parts[0].text
        return json.loads(text)
    except Exception:
        return {
            "eligible": False,
            "confidence": "low",
            "reason": "Unable to determine eligibility"
        }
