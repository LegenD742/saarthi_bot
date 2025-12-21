from fastapi import APIRouter
from pydantic import BaseModel
from app.nlp.gemini_extractor import extract_entities_with_gemini

from app.matcher.load_schemes import load_schemes
from app.matcher.preprocess import preprocess_schemes
from app.matcher.retrieve_candidates import retrieve_candidates
from app.matcher.ai_eligibility import check_eligibility_with_ai


router = APIRouter()

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
        # 1️⃣ Understand user using Gemini (REAL AI)
        user_profile = extract_entities_with_gemini(request.message)
        print("🧠 Extracted user profile:", user_profile)

        # Safety check
        if not user_profile or not isinstance(user_profile, dict):
            return ChatResponse(
                reply="I couldn't understand your details clearly. Please try rephrasing."
            )

        # 2️⃣ Reduce 4000 → ~50 schemes using intent + tags
        candidates = retrieve_candidates(schemes, user_profile)
        print(f"🔍 Candidates after intent+state filter: {len(candidates)}")

        # DEBUG: show first 3 candidate tags
        for i, s in enumerate(candidates[:3]):
            print(f"   Candidate {i+1}: {s.get('name')}")
            print("   Tags:", s.get("_tag_set"))

        if not candidates:
            return ChatResponse(
                reply="I couldn't find relevant schemes for your request."
            )

        results = []

        # 3️⃣ AI-based eligibility reasoning (few schemes only)
        MAX_AI_CHECKS = 2  # 🔒 SAFETY LIMIT

        for idx, scheme in enumerate(candidates):
            if idx >= MAX_AI_CHECKS:
                break
            print("\n➡️ Sending scheme to Gemini:")
            print("Scheme:", scheme.get("name"))
            print("Eligibility text:", scheme.get("eligibility_text")[:300], "...")

            decision = check_eligibility_with_ai(user_profile, scheme)
            print("🤖 Gemini decision:", decision)

            if decision.get("eligible"):
                results.append({
                    "Scheme": scheme.get("name"),
                    "Benefit": scheme.get("benefits_text", "See scheme details"),
                    "Why you may be eligible": decision.get("reason"),
                    "Confidence": decision.get("confidence")
                })
            print("✅ Final eligible schemes:", results)

            if len(results) >= 3:
                break


        # 4️⃣ Final response
        if not results:
            return ChatResponse(
                reply="Based on the information you provided, I could not find a scheme you are eligible for."
            )

        # Convert result list to readable text
        formatted_reply = "Here are some schemes you may be eligible for:\n\n"
        for idx, r in enumerate(results, start=1):
            formatted_reply += (
                f"{idx}. {r['Scheme']}\n"
                f"   • Benefit: {r['Benefit']}\n"
                f"   • Reason: {r['Why you may be eligible']}\n"
                f"   • Confidence: {r['Confidence']}\n\n"
            )

        return ChatResponse(reply=formatted_reply)

    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return ChatResponse(
            reply="Sorry, something went wrong while processing your request."
        )

