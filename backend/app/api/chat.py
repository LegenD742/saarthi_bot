# from fastapi import APIRouter, Request
# from pydantic import BaseModel

# # ===============================
# # NLP (ONLY entity extraction)
# # ===============================
# from app.nlp.gemini_extractor import extract_entities_with_gemini

# # ===============================
# # Normalization
# # ===============================
# from app.utils.normalization import (
#     normalize_occupation,
#     normalize_intent,
# )

# # ===============================
# # Session + Missing Info
# # ===============================
# from app.utils.profile_merge import merge_profiles
# from app.utils.missing_info import get_missing_fields

# # ===============================
# # Scheme Engine
# # ===============================
# from app.matcher.load_schemes import load_schemes
# from app.matcher.preprocess import preprocess_schemes
# from app.matcher.retrieve_candidates import retrieve_candidates

# # ===============================
# # Rejection Utilities (NO GEMINI)
# # ===============================
# from app.utils.grievance_detector import is_rejection_message
# from app.utils.rejection_details_parser import extract_scheme_and_docs
# from app.matcher.rejection_analyzer import analyze_rejection
# from app.matcher.alternate_schemes import find_alternate_schemes


# router = APIRouter()
# schemes = preprocess_schemes(load_schemes())

# # In-memory session store
# USER_SESSIONS = {}


# class ChatRequest(BaseModel):
#     message: str


# class ChatResponse(BaseModel):
#     reply: str


# # ===============================
# # Language Detection
# # ===============================
# def detect_language(text: str):
#     if any("\u0900" <= c <= "\u097F" for c in text):
#         return "hi"

#     hinglish_words = ["hai", "mujhe", "naukri", "madad", "chahiye"]
#     if any(w in text.lower() for w in hinglish_words):
#         return "hinglish"

#     return "en"


# # ===============================
# # Income Band
# # ===============================
# def normalize_income_band(income):
#     try:
#         income = int(income)
#     except Exception:
#         return None

#     if income <= 72000:
#         return "low"
#     if income <= 400000:
#         return "medium"
#     return "high"


# # ===============================
# # Basic Eligibility
# # ===============================
# def basic_eligibility(user, scheme):
#     es = scheme.get("eligibility_structured", {}) or {}

#     if es.get("min_age") and user.get("age") is not None:
#         if user["age"] < es["min_age"]:
#             return False

#     if es.get("max_age") and user.get("age") is not None:
#         if user["age"] > es["max_age"]:
#             return False

#     if es.get("category") and user.get("category"):
#         if es["category"].lower() != user["category"].lower():
#             return False

#     if es.get("income_level") and user.get("income_level"):
#         if es["income_level"] != user["income_level"]:
#             return False

#     return True


# # ===============================
# # MAIN CHAT ENDPOINT
# # ===============================
# @router.post("/chat", response_model=ChatResponse)
# def chat_endpoint(request: Request, body: ChatRequest):
#     try:
#         session_id = request.client.host if request.client else "anonymous"
#         text = body.message
#         lang = detect_language(text)

#         print("\n========== NEW CHAT ==========")
#         print("User message:", text)

#         session = USER_SESSIONS.get(session_id, {})
#         session["lang"] = lang

#         # ==================================================
#         # 🔴 HARD REJECTION TRIGGER (NO GEMINI)
#         # ==================================================
#         if is_rejection_message(text):
#             USER_SESSIONS[session_id] = {
#                 "intent": "rejectiondetails",
#                 "lang": lang,
#             }

#             if lang == "hi":
#                 return ChatResponse(
#                     reply=(
#                         "Main aapki application rejection samajhne mein madad kar sakta hoon.\n\n"
#                         "Kripya batayein:\n"
#                         "• Scheme ka naam\n"
#                         "• Aapne kaun-kaun se documents submit kiye"
#                     )
#                 )

#             if lang == "hinglish":
#                 return ChatResponse(
#                     reply=(
#                         "Main aapki application rejection check kar sakta hoon.\n\n"
#                         "Please batao:\n"
#                         "• Scheme ka naam\n"
#                         "• Kaunse documents submit kiye the"
#                     )
#                 )

#             return ChatResponse(
#                 reply=(
#                     "I can help you understand why your application was rejected.\n\n"
#                     "Please provide:\n"
#                     "• Scheme name\n"
#                     "• Documents you submitted"
#                 )
#             )

#         # ==================================================
#         # 🔒 LOCK REJECTION MODE (CRITICAL FIX)
#         # ==================================================
#         locked_rejection = session.get("intent") == "rejectiondetails"

#         # ==================================================
#         # 1️⃣ NLP Extraction (facts only)
#         # ==================================================
#         new_profile = extract_entities_with_gemini(text)
#         new_profile["occupation"] = normalize_occupation(new_profile.get("occupation"))
#         new_profile["intent"] = normalize_intent(new_profile.get("intent"))

#         # ==================================================
#         # 2️⃣ Merge Session
#         # ==================================================
#         user = merge_profiles(session, new_profile)
#         user["lang"] = lang

#         # 🔒 Override intent if locked
#         if locked_rejection:
#             user["intent"] = "rejectiondetails"

#         # Normalize income
#         if user.get("income") is not None:
#             user["income_level"] = normalize_income_band(user.get("income"))

#         USER_SESSIONS[session_id] = user

#         print("🧠 Merged user profile:", user)

#         # ==================================================
#         # 🚫 CHILD LABOUR CHECK
#         # ==================================================
#         if user.get("intent") == "employment" and user.get("age") is not None:
#             if user["age"] < 18:
#                 if lang == "hi":
#                     return ChatResponse(
#                         reply=(
#                             "⚠️ 18 saal se kam umar ke bachchon ke liye naukri karna "
#                             "Bharat mein kanooni nahi hai.\n\n"
#                             "Main madad kar sakta hoon:\n"
#                             "• Education schemes\n"
#                             "• Scholarships\n"
#                             "• Skill training"
#                         )
#                     )

#                 if lang == "hinglish":
#                     return ChatResponse(
#                         reply=(
#                             "⚠️ India mein 18 se kam age ke liye job illegal hai.\n\n"
#                             "Main madad kar sakta hoon:\n"
#                             "• Education schemes\n"
#                             "• Scholarships\n"
#                             "• Skill training"
#                         )
#                     )

#                 return ChatResponse(
#                     reply=(
#                         "⚠️ Employment for minors is illegal in India.\n\n"
#                         "I can help with education, scholarships, or skill training."
#                     )
#                 )

#         # ==================================================
#         # 🟥 REJECTION MODE (STATEFUL + DOC CHECK)
#         # ==================================================
#         if user.get("intent") == "rejectiondetails":

#             scheme_name, docs = extract_scheme_and_docs(text)

#             if scheme_name and not user.get("rejection_scheme"):
#                 user["rejection_scheme"] = scheme_name

#             if docs:
#                 existing = set(user.get("submitted_documents", []))
#                 user["submitted_documents"] = list(existing.union(docs))

#             USER_SESSIONS[session_id] = user

#             if not user.get("rejection_scheme"):
#                 return ChatResponse(reply="Please tell me the scheme name you applied for.")

#             if not user.get("submitted_documents"):
#                 return ChatResponse(reply="Please list the documents you submitted.")

#             scheme = next(
#                 (
#                     s for s in schemes
#                     if user["rejection_scheme"].lower() in s["name"].lower()
#                 ),
#                 None
#             )

#             if not scheme:
#                 return ChatResponse(reply="I could not find this scheme in my database.")

#             # 🔍 Compare with documents_text ONLY
#             issues = analyze_rejection(user, scheme)

#             reply = "Your application may have been rejected due to:\n\n"
#             for i, issue in enumerate(issues, 1):
#                 reply += f"{i}. {issue}\n"

#             alternates = find_alternate_schemes(schemes, scheme, user)
#             if alternates:
#                 reply += "\nYou may also consider:\n"
#                 for s in alternates[:3]:
#                     reply += f"• {s['name']}\n"

#             # 🔓 EXIT rejection mode
#             user["intent"] = None
#             USER_SESSIONS[session_id] = user

#             return ChatResponse(reply=reply)

#         # ==================================================
#         # 🟡 APPLICATION HELP
#         # ==================================================
#         if user.get("intent") == "applicationhelp":
#             return ChatResponse(
#                 reply=(
#                     "I can help you fill your application.\n\n"
#                     "Please tell me:\n"
#                     "• Scheme name\n"
#                     "• Documents you currently have"
#                 )
#             )

#         # ==================================================
#         # ❓ Missing Information
#         # ==================================================
#         missing = get_missing_fields(user)
#         if missing:
#             reply = "I need a few more details:\n\n"
#             for f in missing:
#                 reply += f"• Your {f.replace('_', ' ')}\n"
#             return ChatResponse(reply=reply)

#         # ==================================================
#         # 🟢 NORMAL SCHEME DISCOVERY
#         # ==================================================
#         candidates = retrieve_candidates(schemes, user)
#         eligible = [s for s in candidates if basic_eligibility(user, s)][:3]

#         if not eligible:
#             return ChatResponse(reply="No schemes match your profile.")

#         reply = "Here are some schemes you may be eligible for:\n\n"
#         for i, s in enumerate(eligible, 1):
#             reply += f"{i}. {s['name']}\n"
#             reply += f"   • Benefit: {s.get('benefits_text','')}\n"
#             reply += f"   • Documents: {s.get('documents_text','Check official portal')}\n\n"

#         return ChatResponse(reply=reply)

#     except Exception as e:
#         print("❌ Chat endpoint error:", e)
#         return ChatResponse(reply="Something went wrong.")




from fastapi import APIRouter, Request
from pydantic import BaseModel

# ===============================
# NLP (ONLY entity extraction)
# ===============================
from app.nlp.gemini_extractor import extract_entities_with_gemini

# ===============================
# Normalization
# ===============================
from app.utils.normalization import (
    normalize_occupation,
    normalize_intent,
)

# ===============================
# Session + Missing Info
# ===============================
from app.utils.profile_merge import merge_profiles
from app.utils.missing_info import get_missing_fields

# ===============================
# Scheme Engine
# ===============================
from app.matcher.load_schemes import load_schemes
from app.matcher.preprocess import preprocess_schemes
from app.matcher.retrieve_candidates import retrieve_candidates

# ===============================
# Rejection Utilities (NO GEMINI)
# ===============================
from app.utils.grievance_detector import is_rejection_message
from app.utils.rejection_details_parser import extract_scheme_and_docs
from app.matcher.rejection_analyzer import analyze_rejection
from app.matcher.alternate_schemes import find_alternate_schemes


router = APIRouter()
schemes = preprocess_schemes(load_schemes())

# In-memory session store
USER_SESSIONS = {}


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


# ===============================
# Language Detection
# ===============================
def detect_language(text: str):
    if any("\u0900" <= c <= "\u097F" for c in text):
        return "hi"

    hinglish_words = ["hai", "mujhe", "naukri", "madad", "chahiye"]
    if any(w in text.lower() for w in hinglish_words):
        return "hinglish"

    return "en"


# ===============================
# Income Band
# ===============================
def normalize_income_band(income):
    try:
        income = int(income)
    except Exception:
        return None

    if income <= 72000:
        return "low"
    if income <= 400000:
        return "medium"
    return "high"


# ===============================
# Basic Eligibility
# ===============================
def basic_eligibility(user, scheme):
    es = scheme.get("eligibility_structured", {}) or {}

    if es.get("min_age") and user.get("age") is not None:
        if user["age"] < es["min_age"]:
            return False

    if es.get("max_age") and user.get("age") is not None:
        if user["age"] > es["max_age"]:
            return False

    if es.get("category") and user.get("category"):
        if es["category"].lower() != user["category"].lower():
            return False

    if es.get("income_level") and user.get("income_level"):
        if es["income_level"] != user["income_level"]:
            return False

    return True


# ===============================
# MAIN CHAT ENDPOINT
# ===============================
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: Request, body: ChatRequest):
    try:
        session_id = getattr(
            request.state,
            "session_override",
            request.client.host if request.client else "anonymous"
        )
        text = body.message
        lang = detect_language(text)

        print("\n========== NEW CHAT ==========")
        print("User message:", text)

        session = USER_SESSIONS.get(session_id, {})
        session["lang"] = lang

        # ==================================================
        # 🔴 HARD REJECTION TRIGGER (NO GEMINI)
        # ==================================================
        if is_rejection_message(text):
            USER_SESSIONS[session_id] = {
                "intent": "rejectiondetails",
                "lang": lang,
            }

            if lang == "hi":
                return ChatResponse(
                    reply=(
                        "Main aapki application rejection samajhne mein madad kar sakta hoon.\n\n"
                        "Kripya batayein:\n"
                        "• Scheme ka naam\n"
                        "• Aapne kaun-kaun se documents submit kiye"
                    )
                )

            if lang == "hinglish":
                return ChatResponse(
                    reply=(
                        "Main aapki application rejection check kar sakta hoon.\n\n"
                        "Please batao:\n"
                        "• Scheme ka naam\n"
                        "• Kaunse documents submit kiye the"
                    )
                )

            return ChatResponse(
                reply=(
                    "I can help you understand why your application was rejected.\n\n"
                    "Please provide:\n"
                    "• Scheme name\n"
                    "• Documents you submitted"
                )
            )

        # ==================================================
        # 🔒 LOCK REJECTION MODE (CRITICAL FIX)
        # ==================================================
        locked_rejection = session.get("intent") == "rejectiondetails"

        # ==================================================
        # 1️⃣ NLP Extraction (facts only)
        # ==================================================
        new_profile = extract_entities_with_gemini(text)
        new_profile["occupation"] = normalize_occupation(new_profile.get("occupation"))
        new_profile["intent"] = normalize_intent(new_profile.get("intent"))

        # ==================================================
        # 2️⃣ Merge Session
        # ==================================================
        user = merge_profiles(session, new_profile)
        user["lang"] = lang

        # 🔒 Override intent if locked
        if locked_rejection:
            user["intent"] = "rejectiondetails"

        # Normalize income
        if user.get("income") is not None:
            user["income_level"] = normalize_income_band(user.get("income"))

        USER_SESSIONS[session_id] = user

        print("🧠 Merged user profile:", user)

        # ==================================================
        # 🚫 CHILD LABOUR CHECK
        # ==================================================
        if user.get("intent") == "employment" and user.get("age") is not None:
            if user["age"] < 18:
                if lang == "hi":
                    return ChatResponse(
                        reply=(
                            "⚠️ 18 saal se kam umar ke bachchon ke liye naukri karna "
                            "Bharat mein kanooni nahi hai.\n\n"
                            "Main madad kar sakta hoon:\n"
                            "• Education schemes\n"
                            "• Scholarships\n"
                            "• Skill training"
                        )
                    )

                if lang == "hinglish":
                    return ChatResponse(
                        reply=(
                            "⚠️ India mein 18 se kam age ke liye job illegal hai.\n\n"
                            "Main madad kar sakta hoon:\n"
                            "• Education schemes\n"
                            "• Scholarships\n"
                            "• Skill training"
                        )
                    )

                return ChatResponse(
                    reply=(
                        "⚠️ Employment for minors is illegal in India.\n\n"
                        "I can help with education, scholarships, or skill training."
                    )
                )

        # ==================================================
        # 🟥 REJECTION MODE (STATEFUL + DOC CHECK)
        # ==================================================
        if user.get("intent") == "rejectiondetails":

            scheme_name, docs = extract_scheme_and_docs(text)

            if scheme_name and not user.get("rejection_scheme"):
                user["rejection_scheme"] = scheme_name

            if docs:
                existing = set(user.get("submitted_documents", []))
                user["submitted_documents"] = list(existing.union(docs))

            USER_SESSIONS[session_id] = user

            if not user.get("rejection_scheme"):
                return ChatResponse(reply="Please tell me the scheme name you applied for.")

            if not user.get("submitted_documents"):
                return ChatResponse(reply="Please list the documents you submitted.")

            scheme = next(
                (
                    s for s in schemes
                    if user["rejection_scheme"].lower() in s["name"].lower()
                ),
                None
            )

            if not scheme:
                return ChatResponse(reply="I could not find this scheme in my database.")

            # 🔍 Compare with documents_text ONLY
            issues = analyze_rejection(user, scheme)

            reply = "Your application may have been rejected due to:\n\n"
            for i, issue in enumerate(issues, 1):
                reply += f"{i}. {issue}\n"

            alternates = find_alternate_schemes(schemes, scheme, user)
            if alternates:
                reply += "\nYou may also consider:\n"
                for s in alternates[:3]:
                    reply += f"• {s['name']}\n"

            # 🔓 EXIT rejection mode
            user["intent"] = None
            USER_SESSIONS[session_id] = user

            return ChatResponse(reply=reply)

        # ==================================================
        # 🟡 APPLICATION HELP
        # ==================================================
        if user.get("intent") == "applicationhelp":
            return ChatResponse(
                reply=(
                    "I can help you fill your application.\n\n"
                    "Please tell me:\n"
                    "• Scheme name\n"
                    "• Documents you currently have"
                )
            )

        # ==================================================
        # ❓ Missing Information
        # ==================================================
        missing = get_missing_fields(user)
        if missing:
            reply = "I need a few more details:\n\n"
            for f in missing:
                reply += f"• Your {f.replace('_', ' ')}\n"
            return ChatResponse(reply=reply)

        # ==================================================
        # 🟢 NORMAL SCHEME DISCOVERY
        # ==================================================
        candidates = retrieve_candidates(schemes, user)
        eligible = [s for s in candidates if basic_eligibility(user, s)][:3]

        if not eligible:
            return ChatResponse(reply="No schemes match your profile.")

        reply = "Here are some schemes you may be eligible for:\n\n"
        for i, s in enumerate(eligible, 1):
            reply += f"{i}. {s['name']}\n"
            reply += f"   • Benefit: {s.get('benefits_text','')}\n"
            reply += f"   • Documents: {s.get('documents_text','Check official portal')}\n\n"

        return ChatResponse(reply=reply)

    except Exception as e:
        print("❌ Chat endpoint error:", e)
        return ChatResponse(reply="Something went wrong.")




