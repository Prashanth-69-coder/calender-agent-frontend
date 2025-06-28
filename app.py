import streamlit as st
import requests
import json
from datetime import datetime
import time

API_BASE = "https://calender-agent-backend-render-3.onrender.com"

# Set page config
st.set_page_config(
    page_title="Smart Calendar Assistant",
    layout="wide",
    page_icon="🧠"
)

# Custom CSS
st.markdown("""
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        min-height: 100vh;
    }
    .welcome-title {
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        text-shadow: 0 2px 16px rgba(0,0,0,0.15);
    }
    .suggestions-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        justify-content: center;
        margin: 1.5rem 0 2rem 0;
    }
    .suggestion-card {
        background: rgba(255,255,255,0.12);
        border-radius: 20px;
        padding: 1rem 1.5rem;
        color: #fff;
        font-weight: 500;
        font-size: 1.05rem;
        cursor: pointer;
        border: none;
        transition: background 0.2s, transform 0.2s;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .suggestion-card:hover {
        background: rgba(255,255,255,0.22);
        transform: translateY(-2px) scale(1.04);
    }
    .chat-container {
        max-width: 700px;
        margin: 0 auto;
        background: rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 2rem 1.5rem 1rem 1.5rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.10);
    }
    .footer {
        text-align: center;
        color: rgba(255,255,255,0.7);
        margin-top: 3rem;
        font-size: 1rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

SUGGESTIONS = [
    "📅 Schedule a meeting tomorrow at 2pm",
    "🔍 Am I free Monday at 10am?",
    "📋 What's on my calendar today?",
    "⏰ Book a 30-minute call next Tuesday",
    "🍽️ Schedule lunch meeting Friday 12pm",
    "🏥 Book doctor appointment next week",
    "📊 Schedule team standup tomorrow 9am",
    "🎯 Check my availability this afternoon"
]

# Helper: Get calendar events (if needed)
def get_calendar_events(user_id):
    try:
        response = requests.get(f"{API_BASE}/calendar/events", params={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("events", [])
        return []
    except:
        return []

# --- MAIN ---
def main():
    st.markdown('<div class="welcome-title">Welcome to Smart Calendar Assistant</div>', unsafe_allow_html=True)

    # Robust Query Params Handling
    query_params = st.experimental_get_query_params()
    user_id = query_params.get("user_id", [None])[0]
    auth_success = query_params.get("auth_success", ["false"])[0] == "true"

    # Session State Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "suggestions_clicked" not in st.session_state:
        st.session_state.suggestions_clicked = set()

    # --- AUTH FLOW ---
    if not user_id:
        email = st.text_input("Enter your Google Email:", placeholder="your.email@gmail.com", key="email")
        if st.button("🔐 Connect Google Calendar", type="primary"):
            if email and "@" in email:
                try:
                    with st.spinner("Checking authentication status..."):
                        check = requests.get(f"{API_BASE}/auth/check", params={"user_id": email})
                    if check.status_code == 200 and check.json().get("authenticated"):
                        redirect_url = f"https://calender-agent-frontend-synv22yjhxvmcwhajarhte.streamlit.app/?user_id={email}&auth_success=true"
                        st.markdown(f"<meta http-equiv='refresh' content='2; URL={redirect_url}' />", unsafe_allow_html=True)
                    else:
                        response = requests.get(f"{API_BASE}/auth/url", params={"user_id": email})
                        auth_url = response.json().get("auth_url")
                        if auth_url:
                            st.markdown(f"<meta http-equiv='refresh' content='2; URL={auth_url}' />", unsafe_allow_html=True)
                        else:
                            st.error("Failed to get authentication URL.")
                except Exception as e:
                    st.error(f"Connection error: {str(e)}")
            else:
                st.error("Please enter a valid email address.")
        st.stop()

    # Auth success feedback and refresh button
    if auth_success:
        st.success(f'Successfully connected as `{user_id}`! You can now start managing your calendar.')
        if st.button("🔄 Refresh to start using the assistant"):
            st.rerun()
        time.sleep(2)

    # --- SUGGESTIONS SECTION ---
    st.markdown('<div class="suggestions-grid">', unsafe_allow_html=True)
    for i, suggestion in enumerate(SUGGESTIONS):
        if st.button(suggestion, key=f"suggestion_{i}", help=suggestion):
            if suggestion not in st.session_state.suggestions_clicked:
                st.session_state.suggestions_clicked.add(suggestion)
                st.session_state.messages.append({"role": "user", "content": suggestion})
                with st.spinner("Processing..."):
                    try:
                        res = requests.post(
                            f"{API_BASE}/chat",
                            json={"message": suggestion, "user_id": user_id},
                            timeout=30
                        )
                        if res.status_code == 200:
                            reply = res.json().get("reply")
                        else:
                            reply = f"❌ Server error: {res.status_code}"
                    except Exception as e:
                        reply = f"❌ Connection error: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown('</div>', unsafe_allow_html=True)

    # --- CHAT CONTAINER ---
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
    prompt = st.chat_input("What would you like to schedule or ask?")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    res = requests.post(
                        f"{API_BASE}/chat",
                        json={"message": prompt, "user_id": user_id},
                        timeout=30
                    )
                    if res.status_code == 200:
                        reply = res.json().get("reply")
                    else:
                        reply = f"❌ Server error ({res.status_code}): {res.text}"
                except requests.exceptions.Timeout:
                    reply = "⏰ Request timed out. Please try again."
                except Exception as e:
                    reply = f"❌ Connection error: {str(e)}"
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
    st.markdown('</div>', unsafe_allow_html=True)

    # Footer
    st.markdown('<div class="footer">Powered by AI • Secure • Private</div>', unsafe_allow_html=True)

# --- Run App ---
if __name__ == "__main__":
    main()