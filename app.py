import streamlit as st
import requests
import json
import sseclient

# Set up the API endpoint
API_URL = "https://api.together.xyz/v1/chat/completions"

# Use Streamlit's secrets management to get the API key
API_KEY = st.secrets["TOGETHER_API_KEY"]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_ai_response(messages):
    data = {
        "model": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "messages": messages,
        "max_tokens": 2512,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": ["<|eot_id|>"],
        "stream": True
    }

    response = requests.post(API_URL, headers=headers, json=data, stream=True)
    client = sseclient.SSEClient(response)

    full_response = ""
    for event in client.events():
        if event.data != "[DONE]":
            try:
                chunk = json.loads(event.data)
                content = chunk['choices'][0]['delta'].get('content', '')
                full_response += content
                yield content
            except json.JSONDecodeError:
                pass

st.title("AI Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is your question?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in get_ai_response(st.session_state.messages):
            full_response += response
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
