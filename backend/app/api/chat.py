from fastapi import APIRouter, Request
from pydantic import BaseModel

# NLP (Gemini only for extraction)
from app.nlp.gemini_extractor import extract_entities_with_gemini

# Normalization
from app.utils.normalization import (
    normalize_occupation,
    normalize_intent,
    normalize_income,
)

# Session helpers
from app.utils.profile_merge import merge_profiles
from app.utils.missing_info import get_missing_fields

# Scheme engine
from app.matcher.load_schemes import load_schemes
from app.matcher.preprocess import preprocess_schemes
from app.matcher.retrieve_candidates import retrieve_candidates

# Rejection / grievance
from app.utils.grievance_detector import is_rejection_message
from app.utils.grievance_followup import generate_rejection_followup
from app.utils.rejection_details_parser import extract_scheme_and_docs
from app.matcher.rejection_analyzer import analyze_rejection
from app.matcher.alternate_schemes import find_alternate_schemes


router = APIRouter()

# Load schemes once at startup
schemes = preprocess_schemes(load_schemes())

# In-memory session store (hackathon safe)
USER_SESSIONS = {}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# --------------------------------------------------
# BASIC RULE-BASED ELIGIBILITY (NO AI)
# --------------------------------------------------
def basic_eligibility(user, scheme):
    es = scheme.get("eligibility_structured", {}) or {}

    # Age
    if es.get("min_age") and user.get("age"):
        if user["age"] < es["min_age"]:
            return False

    if es.get("max_age") and user.get("age"):
        if user["age"] > es["max_age"]:
            return False

    # Category
    if es.get("category") and user.get("category"):
        if es["category"] != user["category"]:
            return False

    # Income
    if es.get("income_level") and user.get("income_level"):
        if es["income_level"] != user["income_level"]:
            return False

    return True


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: Request, body: ChatRequest):
    try:
        print("\n========== NEW CHAT ==========")
        print("User message:", body.message)

        session_id = request.client.host if request.client else "anonymous"
        session = USER_SESSIONS.get(session_id, {})

        # --------------------------------------------------
        # 🔴 STEP 0: REJECTION TRIGGER (LOCK MODE)
        # --------------------------------------------------
        if is_rejection_message(body.message):
            USER_SESSIONS[session_id] = {
                "intent": "rejectiondetails"
            }
            return ChatResponse(
                reply=generate_rejection_followup(body.message)
            )

        # --------------------------------------------------
        # 1️⃣ Extract entities (Gemini = NLP only)
        # --------------------------------------------------
        new_profile = extract_entities_with_gemini(body.message)

        new_profile["occupation"] = normalize_occupation(
            new_profile.get("occupation")
        )
        new_profile["intent"] = normalize_intent(
            new_profile.get("intent")
        )

        # --------------------------------------------------
        # 2️⃣ Merge with session profile
        # --------------------------------------------------
        old_profile = USER_SESSIONS.get(session_id, {})
        user_profile = merge_profiles(old_profile, new_profile)
        USER_SESSIONS[session_id] = user_profile

        # --------------------------------------------------
        # 3️⃣ Normalize income (0 is valid)
        # --------------------------------------------------
        if "income_level" in user_profile:
            norm_income = normalize_income(user_profile.get("income_level"))
            if norm_income is not None:
                user_profile["income_level"] = norm_income

        # --------------------------------------------------
        # 🔒 LOCK REJECTION MODE (CRITICAL FIX)
        # --------------------------------------------------
        if session.get("intent") == "rejectiondetails":
            user_profile["intent"] = "rejectiondetails"

        print("🧠 Merged user profile:", user_profile)

        # --------------------------------------------------
        # 🟥 REJECTION ANALYSIS MODE (STATEFUL)
        # --------------------------------------------------
        if user_profile.get("intent") == "rejectiondetails":

            scheme_name, submitted_docs = extract_scheme_and_docs(body.message)

            # 🔐 Persist rejection data in session
            if scheme_name:
                user_profile["rejection_scheme"] = scheme_name

            if submitted_docs:
                existing = user_profile.get("submitted_documents", [])
                user_profile["submitted_documents"] = list(
                    set(existing + submitted_docs)
                )

            # 🔁 Read from session (NOT current message)
            scheme_name = user_profile.get("rejection_scheme")
            submitted_docs = user_profile.get("submitted_documents", [])

            # Ask ONLY for what is missing
            if not scheme_name:
                return ChatResponse(
                    reply="Please tell me the scheme name you applied for."
                )

            if not submitted_docs:
                return ChatResponse(
                    reply="Please list the documents you submitted."
                )

            scheme = next(
                (s for s in schemes if scheme_name.lower() in s.get("name", "").lower()),
                None
            )

            if not scheme:
                return ChatResponse(
                    reply="I could not find this scheme in my database."
                )

            # Analyze rejection
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

            # Suggest alternates
            alternates = find_alternate_schemes(
                schemes, scheme, user_profile
            )

            if alternates:
                reply += "\nYou may also consider these alternate schemes:\n"
                for idx, s in enumerate(alternates, 1):
                    reply += f"{idx}. {s.get('name')}\n"

            return ChatResponse(reply=reply)

        # --------------------------------------------------
        # 🟢 NORMAL SCHEME DISCOVERY
        # --------------------------------------------------
        candidates = retrieve_candidates(schemes, user_profile)

        if not candidates:
            missing = get_missing_fields(user_profile)

            if missing:
                reply = (
                    "I need a bit more information to find suitable schemes.\n\n"
                    "Please tell me:\n"
                )
                for f in missing:
                    reply += f"• Your {f}\n"

                return ChatResponse(reply=reply)

            return ChatResponse(
                reply="There are currently no schemes applicable to your profile."
            )

        # --------------------------------------------------
        # 4️⃣ RULE-BASED ELIGIBILITY FILTER
        # --------------------------------------------------
        eligible = [
            s for s in candidates
            if basic_eligibility(user_profile, s)
        ][:3]

        if not eligible:
            return ChatResponse(
                reply="Based on official eligibility rules, no schemes apply."
            )

        # --------------------------------------------------
        # 5️⃣ FINAL RESPONSE
        # --------------------------------------------------
        reply = "Here are some schemes that match your profile:\n\n"

        for idx, s in enumerate(eligible, 1):
            reply += (
                f"{idx}. {s.get('name')}\n"
                f"   • Benefit: {s.get('benefits_text', '')}\n"
            )

            if s.get("documents_text"):
                reply += f"   • Documents Required: {s['documents_text']}\n\n"
            else:
                reply += "   • Documents Required: Check official portal or CSC\n\n"

        return ChatResponse(reply=reply)

    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return ChatResponse(
            reply="Sorry, something went wrong while processing your request."
        )
