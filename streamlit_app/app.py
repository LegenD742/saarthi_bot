import streamlit as st
import requests
from speech_to_text import speech_to_text
from gtts import gTTS
import tempfile

st.set_page_config(page_title="Saarthi Bot", page_icon="🤖")

st.title("🤖 Saarthi Bot")
st.write("Describe your situation in any language (Hindi / English).")

# -------------------------
# Session State
# -------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_input_was_voice" not in st.session_state:
    st.session_state.last_input_was_voice = False

# -------------------------
# Display chat history
# -------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -------------------------
# 🎤 Voice button (ABOVE input)
# -------------------------
if st.button("🎤 Speak"):
    with st.spinner("Listening..."):
        voice_text = speech_to_text()

        if voice_text:
            st.session_state.last_input_was_voice = True

            # User message
            st.session_state.messages.append(
                {"role": "user", "content": voice_text}
            )

            try:
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"message": voice_text},
                    timeout=30
                )
                reply = response.json().get("reply", "No response from backend.")
            except Exception:
                reply = "⚠️ Backend not connected."

            # Assistant message
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )

            # 🔊 Audio reply
            lang = "hi" if any('\u0900' <= c <= '\u097F' for c in reply) else "en"
            tts = gTTS(text=reply, lang=lang)
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(temp_audio.name)

            st.audio(temp_audio.name)
            st.rerun()

# -------------------------
# 💬 TEXT INPUT — MUST BE LAST
# -------------------------
user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.last_input_was_voice = False

    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input},
            timeout=30
        )
        reply = response.json().get("reply", "No response from backend.")
    except Exception:
        reply = "⚠️ Backend not connected."

    # Assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()
