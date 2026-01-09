from fastapi import APIRouter
from pydantic import BaseModel

from app.nlp.gemini_extractor import extract_entities_with_gemini
from app.utils.normalization import normalize_occupation, normalize_intent

from app.matcher.load_schemes import load_schemes
from app.matcher.preprocess import preprocess_schemes
from app.matcher.retrieve_candidates import retrieve_candidates
from app.matcher.ai_eligibility import check_eligibility_with_ai

from app.utils.grievance_detector import is_rejection_message
from app.utils.grievance_followup import generate_rejection_followup

from app.matcher.rejection_analyzer import analyze_rejection
from app.matcher.alternate_schemes import find_alternate_schemes
from app.utils.rejection_details_detector import looks_like_rejection_details
from app.utils.rejection_details_parser import extract_scheme_and_docs



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

        # 🔴 STEP 0: If user says they were rejected → ask for details
        if is_rejection_message(request.message):
            return ChatResponse(
                reply=generate_rejection_followup(request.message)
            )

        # 1️⃣ Extract user profile using Gemini
        user_profile = extract_entities_with_gemini(request.message)

        # 🔧 Normalize
        user_profile["occupation"] = normalize_occupation(
            user_profile.get("occupation")
        )
        user_profile["intent"] = normalize_intent(
            user_profile.get("intent")
        )

        if user_profile.get("intent") == "scholarship":
            user_profile["intent"] = "Scholarship"

        # 🔑 FORCE rejectiondetails if message looks like rejection data
        if looks_like_rejection_details(request.message):
            user_profile["intent"] = "rejectiondetails"

        print("🧠 Extracted user profile:", user_profile)

        if not user_profile or not isinstance(user_profile, dict):
            return ChatResponse(
                reply="I couldn't understand your details clearly. Please try rephrasing."
            )

        # 🟥 REJECTION ANALYSIS MODE
        if user_profile.get("intent") == "rejectiondetails":
            scheme_name, submitted_docs = extract_scheme_and_docs(request.message)

            user_profile["scheme_name"] = scheme_name
            user_profile["submitted_documents"] = submitted_docs


            if not scheme_name or not submitted_docs:
                return ChatResponse(
                    reply=(
                        "Please provide:\n"
                        "• Scheme name\n"
                        "• Your age, category, state\n"
                        "• Documents you submitted"
                    )
                )

            scheme = next(
                (s for s in schemes if scheme_name.lower() in s.get("name", "").lower()),
                None
            )

            if not scheme:
                return ChatResponse(
                    reply="I could not find this scheme in my database."
                )

            user_profile["submitted_documents"] = submitted_docs

            issues = analyze_rejection(user_profile, scheme)

            reply = ""
            if issues:
                reply += "Your application may have been rejected due to:\n\n"
                for i, issue in enumerate(issues, 1):
                    reply += f"{i}. {issue}\n"
            else:
                reply += (
                    "Your details and documents match the scheme requirements.\n"
                    "The rejection may be due to verification or technical reasons.\n"
                )

            alternates = find_alternate_schemes(
                schemes, scheme, user_profile
            )

            if alternates:
                reply += "\nYou may also consider these alternate schemes:\n"
                for idx, s in enumerate(alternates, 1):
                    reply += f"{idx}. {s.get('name')}\n"

            return ChatResponse(reply=reply)

        # 2️⃣ Normal scheme discovery
        candidates = retrieve_candidates(schemes, user_profile)
        print(f"🔍 Candidates after intent+state filter: {len(candidates)}")

        if not candidates:
            return ChatResponse(
                reply="I couldn't find relevant schemes for your request."
            )

        # 3️⃣ Farmer insurance shortcut
        if user_profile.get("occupation") == "farmer":
            insurance_schemes = [
                s for s in candidates
                if "insurance" in s.get("_tag_set", set())
                or "life" in s.get("_tag_set", set())
            ]

            if insurance_schemes:
                reply = "You may be eligible for the following farmer insurance schemes:\n\n"
                for idx, s in enumerate(insurance_schemes[:3], start=1):
                    reply += (
                        f"{idx}. {s.get('name')}\n"
                        f"   • Benefit: {s.get('benefits_text', '')[:150]}...\n"
                    )

                    if s.get("documents_text"):
                        reply += f"   • Documents Required: {s.get('documents_text')}\n\n"
                    else:
                        reply += "   • Documents Required: Please check official portal or CSC\n\n"

                return ChatResponse(reply=reply)

        # 4️⃣ AI eligibility (limited)
        results = []
        MAX_AI_CHECKS = 2

        for idx, scheme in enumerate(candidates):
            if idx >= MAX_AI_CHECKS:
                break

            decision = check_eligibility_with_ai(user_profile, scheme)

            if decision.get("eligible"):
                results.append({
                    "Scheme": scheme.get("name"),
                    "Benefit": scheme.get("benefits_text", "See scheme details"),
                    "Reason": decision.get("reason"),
                    "Documents": scheme.get("documents_text"),
                })

            if len(results) >= 3:
                break

        if not results:
            return ChatResponse(
                reply=(
                    "Based on the information you provided, additional details may be required. "
                    "Please check with the nearest CSC or official portal."
                )
            )

        # 5️⃣ Final response
        reply = "Here are some schemes you may be eligible for:\n\n"
        for idx, r in enumerate(results, start=1):
            reply += (
                f"{idx}. {r['Scheme']}\n"
                f"   • Benefit: {r['Benefit']}\n"
                f"   • Reason: {r['Reason']}\n"
            )

            if r.get("Documents"):
                reply += f"   • Documents Required: {r['Documents']}\n\n"
            else:
                reply += "   • Documents Required: Please check official portal or CSC\n\n"

        return ChatResponse(reply=reply)

    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return ChatResponse(
            reply="Sorry, something went wrong while processing your request."
        )
