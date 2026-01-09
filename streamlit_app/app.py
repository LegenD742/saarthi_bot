import streamlit as st
import requests
from speech_to_text import speech_to_text

st.set_page_config(page_title="Saarthi Bot", page_icon="🤖")

st.title("🤖 Saarthi Bot")
st.write("Describe your situation in any language (Hindi / English).")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "voice_text" not in st.session_state:
    st.session_state.voice_text = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

input_container = st.container()

with input_container:
    text_input = st.chat_input("Type your message here...")

    col1, col2 = st.columns([5, 1])
    with col2:
        if st.button("🎤 Speak"):
            with st.spinner("Listening..."):
                st.session_state.voice_text = speech_to_text()
                st.rerun()  # 🔑 THIS IS THE FIX

user_input = None
if text_input:
    user_input = text_input
elif st.session_state.voice_text:
    user_input = st.session_state.voice_text
    st.session_state.voice_text = None

if user_input:
    # Add user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.write(user_input)

    # Call backend
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input},
            timeout=30
        )
        reply = response.json().get("reply", "No response from backend.")
    except Exception:
        reply = "⚠️ Backend not connected."

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    with st.chat_message("assistant"):
        st.write(reply)

    st.rerun()  
