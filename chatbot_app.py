import streamlit as st
import requests
from typing import Dict, Any

# Configuration
@st.cache_resource
def get_config() -> Dict[str, Any]:
    return {
        "API_URL": "https://api.together.xyz/v1/chat/completions",
        "MODEL_NAME": "mistralai/Mistral-7B-Instruct-v0.1",
        "DEFAULT_PROMPT": "Ask me anything about books or self-publishing!",
        "MAX_HISTORY": 5
    }

# Initialize session state
def init_session_state():
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "api_key" not in st.session_state:
        # Retrieve API key from secrets
        st.session_state.api_key = st.secrets["TOGETHER_API_KEY"]

# Query Together.ai API
def query_together_api(messages: list, config: Dict[str, Any]) -> str:
    headers = {
        "Authorization": f"Bearer {st.session_state.api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": config["MODEL_NAME"],
        "messages": messages,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        response = requests.post(config["API_URL"], headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {str(e)}")
        return "⚠️ Something went wrong. Please try again."

# UI Components
def render_chat_interface(config: Dict[str, Any]):
    st.title("📚 BookBot by Publy")
    st.subheader("Your AI Assistant for Books & Self-Publishing")

    # Display chat history
    for msg in st.session_state.chat_history[-config["MAX_HISTORY"]:]:
        st.chat_message("You" if msg["role"] == "user" else "BookBot").markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input(config["DEFAULT_PROMPT"]):
        if not st.session_state.api_key:
            st.warning("API key is missing")
            return

        st.session_state.chat_history.append({"role": "user", "content": prompt})
        st.chat_message("You").markdown(prompt)

        with st.spinner("BookBot is thinking..."):
            response_text = query_together_api(st.session_state.chat_history, config)
            st.session_state.chat_history.append({"role": "assistant", "content": response_text})
            st.chat_message("BookBot").markdown(response_text)

# Main
def main():
    config = get_config()
    init_session_state()
    render_chat_interface(config)

if __name__ == "__main__":
    main()
