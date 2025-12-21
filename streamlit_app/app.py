import streamlit as st
import requests

st.set_page_config(page_title="Gov Scheme AI", page_icon="")

st.title("Government Scheme Assistant")
st.write("Describe your situation in English or Hindi.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message here...")

if user_input:
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat",
            json={"message": user_input}
        )

        reply = response.json().get("reply", "No response from backend.")

    except Exception:
        reply = "Backend not connected yet."

    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
