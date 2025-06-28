import streamlit as st
import requests

API_BASE = "https://calender-agent-backend-render-3.onrender.com"

# Page config
st.set_page_config(
    page_title="📅 Smart Calendar Assistant",
    layout="wide",
    page_icon="🧠"
)

# Stylish background and elements
st.markdown("""
    <style>
    html, body {
        background: linear-gradient(to bottom right, #1f1c2c, #928dab);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    input, textarea {
        background-color: #2b2a33 !important;
        color: white !important;
        border: 1px solid #5c5c7a !important;
        border-radius: 8px !important;
        padding: 0.6em !important;
    }
    button {
        background-color: #5A62F2 !important;
        color: white !important;
        padding: 0.5em 1.5em !important;
        border-radius: 8px !important;
        font-weight: bold !important;
    }
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage.user {
        background-color: #3b3b4f;
    }
    .stChatMessage.assistant {
        background-color: #44475a;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("📅 Smart Calendar Assistant")

# Query params
query_params = st.query_params
user_id = query_params.get("user_id")
auth_success = query_params.get("auth_success") == "true"

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- AUTH FLOW ---
if not user_id:
    st.warning("🔐 Please authenticate with Google Calendar")

    email = st.text_input("Enter your Google Email (used for calendar auth):", key="email")

    if st.button("Continue"):
        try:
            check = requests.get(f"{API_BASE}/auth/check", params={"user_id": email})
            if check.status_code == 200 and check.json().get("authenticated"):
                redirect_url = f"https://calender-agent-frontend-synv22yjhxvmcwhajarhte.streamlit.app/?user_id={email}&auth_success=true"
                st.markdown(f"<meta http-equiv='refresh' content='0; URL={redirect_url}' />", unsafe_allow_html=True)
                st.stop()
            else:
                response = requests.get(f"{API_BASE}/auth/url", params={"user_id": email})
                auth_url = response.json().get("auth_url")
                if auth_url:
                    st.markdown(f"<meta http-equiv='refresh' content='0; URL={auth_url}' />", unsafe_allow_html=True)
                    st.stop()
                else:
                    st.error("⚠️ Failed to get auth URL.")
        except Exception as e:
            st.error(f"❌ Error during auth check: {e}")
    st.stop()
else:
    st.success(f"🔐 Logged in as `{user_id}`")

# Chat input
prompt = st.chat_input("What would you like to schedule or ask?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(f"{API_BASE}/chat", json={"message": prompt, "user_id": user_id})
                if res.status_code == 200:
                    reply = res.json().get("reply")
                else:
                    reply = f"❌ Server error: {res.text}"
            except Exception as e:
                reply = f"❌ Failed to reach server: {e}"
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
