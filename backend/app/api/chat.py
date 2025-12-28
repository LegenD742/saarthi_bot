from fastapi import APIRouter
from pydantic import BaseModel

from app.nlp.gemini_extractor import extract_entities_with_gemini
from app.utils.normalization import normalize_occupation, normalize_intent

from app.matcher.load_schemes import load_schemes
from app.matcher.preprocess import preprocess_schemes
from app.matcher.retrieve_candidates import retrieve_candidates
from app.matcher.ai_eligibility import check_eligibility_with_ai


router = APIRouter()

# Load & preprocess schemes once
schemes = preprocess_schemes(load_schemes())


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    try:
        print("\n========== NEW CHAT ==========")
        print("User message:", request.message)

        # 1️⃣ Extract user profile using Gemini (REAL AI)
        user_profile = extract_entities_with_gemini(request.message)

        # 🔧 Normalize ONLY farmer-related fields
        user_profile["occupation"] = normalize_occupation(
            user_profile.get("occupation")
        )

        user_profile["intent"] = normalize_intent(
            user_profile.get("intent")
        )

        if user_profile.get("intent") == "scholarship":
            user_profile["intent"] = "Scholarship"

        print("🧠 Extracted user profile:", user_profile)

        if not user_profile or not isinstance(user_profile, dict):
            return ChatResponse(
                reply="I couldn't understand your details clearly. Please try rephrasing."
            )

        candidates = retrieve_candidates(schemes, user_profile)
        print(f"🔍 Candidates after intent+state filter: {len(candidates)}")

        for i, s in enumerate(candidates[:3]):
            print(f"   Candidate {i+1}: {s.get('name')}")
            print("   Tags:", s.get("_tag_set"))

        if not candidates:
            return ChatResponse(
                reply="I couldn't find relevant schemes for your request."
            )

        if user_profile.get("occupation") == "farmer":
            insurance_schemes = [
                s for s in candidates
                if "insurance" in s.get("_tag_set", set())
                   or "life" in s.get("_tag_set", set())
            ]

            if insurance_schemes:
                formatted_reply = (
                    "You may be eligible for the following farmer insurance schemes:\n\n"
                )
                for idx, s in enumerate(insurance_schemes[:3], start=1):
                    formatted_reply += (
                        f"{idx}. {s.get('name')}\n"
                        f"   • Benefit: {s.get('benefits_text', '')[:150]}...\n\n"
                    )

                return ChatResponse(reply=formatted_reply)

        results = []
        MAX_AI_CHECKS = 2  

        for idx, scheme in enumerate(candidates):
            if idx >= MAX_AI_CHECKS:
                break

            print("\nSending scheme to Gemini:")
            print("Scheme:", scheme.get("name"))
            print("Eligibility text:", scheme.get("eligibility_text", "")[:300], "...")

            decision = check_eligibility_with_ai(user_profile, scheme)
            print("Gemini decision:", decision)

            if decision.get("eligible"):
                results.append({
                    "Scheme": scheme.get("name"),
                    "Benefit": scheme.get("benefits_text", "See scheme details"),
                    "Reason": decision.get("reason"),
                    "Confidence": decision.get("confidence")
                })

            if len(results) >= 3:
                break

        
        if not results:
            return ChatResponse(
                reply=(
                    "Based on the information you provided, you may be eligible for "
                    "some schemes, but additional details are required. "
                    "Please check with the nearest CSC or official portal."
                )
            )

        
        formatted_reply = "Here are some schemes you may be eligible for:\n\n"
        for idx, r in enumerate(results, start=1):
            formatted_reply += (
                f"{idx}. {r['Scheme']}\n"
                f"   • Benefit: {r['Benefit']}\n"
                f"   • Reason: {r['Reason']}\n\n"
            )

        return ChatResponse(reply=formatted_reply)

    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return ChatResponse(
            reply="Sorry, something went wrong while processing your request."
        )
