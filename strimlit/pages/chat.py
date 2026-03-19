import streamlit as st
import requests

print(st.session_state)
#from  app import store_value, load_value
OLLAMA_URL = "http://132.72.112.48:11434/api/chat"
MODEL_NAME = "llama3.2"  # change to your installed model
st.title("🦜🔗 ollama Quickstart App")
if "stage" not in st.session_state:
    st.session_state.stage = "user"
    st.session_state.history = []
    st.session_state.pending = None
    st.session_state.validation = {}
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("What is up?"):
    # Show user message
    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # Prepare messages for Ollama
    ollama_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    # Call Ollama
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "messages": ollama_messages,
            "stream": False
        }
    )

    result = response.json()
    assistant_reply = result["message"]["content"]

    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_reply
    })