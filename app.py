import streamlit as st
import requests
import json
from datetime import datetime
import time

API_BASE = "https://calender-agent-backend-render-3.onrender.com"

# Page config
st.set_page_config(
    page_title="📅 Smart Calendar Assistant",
    layout="wide",
    page_icon="🧠"
)

# Enhanced CSS styling
st.markdown("""
    <style>
    html, body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .main-header {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .suggestion-chip {
        display: inline-block;
        background: rgba(90, 98, 242, 0.3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.25rem;
        cursor: pointer;
        border: 1px solid rgba(90, 98, 242, 0.5);
        transition: all 0.3s ease;
    }
    
    .suggestion-chip:hover {
        background: rgba(90, 98, 242, 0.5);
        transform: translateY(-2px);
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background-color: #4CAF50; }
    .status-offline { background-color: #f44336; }
    
    input, textarea {
        background-color: rgba(43, 42, 51, 0.8) !important;
        color: white !important;
        border: 1px solid rgba(92, 92, 122, 0.5) !important;
        border-radius: 12px !important;
        padding: 0.8em !important;
        backdrop-filter: blur(10px);
    }
    
    button {
        background: linear-gradient(45deg, #5A62F2, #7C3AED) !important;
        color: white !important;
        padding: 0.7em 2em !important;
        border-radius: 12px !important;
        font-weight: bold !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(90, 98, 242, 0.4);
    }
    
    .stChatMessage {
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .stChatMessage.user {
        background: linear-gradient(135deg, rgba(90, 98, 242, 0.2), rgba(124, 58, 237, 0.2));
        border: 1px solid rgba(90, 98, 242, 0.3);
    }
    
    .stChatMessage.assistant {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.2));
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .error-message {
        background: rgba(239, 68, 68, 0.2);
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-message {
        background: rgba(34, 197, 94, 0.2);
        border: 1px solid rgba(34, 197, 94, 0.3);
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Predefined suggestions
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

def check_backend_status():
    """Check if backend is online"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_calendar_events(user_id):
    """Fetch user's calendar events"""
    try:
        response = requests.get(f"{API_BASE}/calendar/events", params={"user_id": user_id})
        if response.status_code == 200:
            return response.json().get("events", [])
        return []
    except:
        return []

def main():
    # Header with status indicator
    backend_status = check_backend_status()
    status_color = "status-online" if backend_status else "status-offline"
    status_text = "Online" if backend_status else "Offline"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📅 Smart Calendar Assistant</h1>
        <p>Your AI-powered calendar management companion</p>
        <div style="display: flex; align-items: center; margin-top: 1rem;">
            <span class="status-indicator {status_color}"></span>
            <span>Backend: {status_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Query params
    query_params = st.query_params
    user_id = query_params.get("user_id")
    auth_success = query_params.get("auth_success") == "true"

    # Session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "suggestions_clicked" not in st.session_state:
        st.session_state.suggestions_clicked = set()

    # --- AUTH FLOW ---
    if not user_id:
        st.markdown("""
        <div class="chat-container">
            <h2>🔐 Welcome to Smart Calendar Assistant</h2>
            <p>Please authenticate with your Google Calendar to get started.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        
        with col1:
            email = st.text_input(
                "Enter your Google Email:",
                placeholder="your.email@gmail.com",
                key="email"
            )
            
            if st.button("🔐 Connect Google Calendar", type="primary"):
                if email and "@" in email:
                    try:
                        with st.spinner("Checking authentication status..."):
                            check = requests.get(f"{API_BASE}/auth/check", params={"user_id": email})
                            
                        if check.status_code == 200 and check.json().get("authenticated"):
                            st.success("✅ Already authenticated! Redirecting...")
                            redirect_url = f"https://calender-agent-frontend-synv22yjhxvmcwhajarhte.streamlit.app/?user_id={email}&auth_success=true"
                            st.markdown(f"<meta http-equiv='refresh' content='2; URL={redirect_url}' />", unsafe_allow_html=True)
                        else:
                            st.info("🔗 Redirecting to Google OAuth...")
                            response = requests.get(f"{API_BASE}/auth/url", params={"user_id": email})
                            auth_url = response.json().get("auth_url")
                            if auth_url:
                                st.markdown(f"<meta http-equiv='refresh' content='2; URL={auth_url}' />", unsafe_allow_html=True)
                            else:
                                st.error("⚠️ Failed to get authentication URL.")
                    except Exception as e:
                        st.error(f"❌ Connection error: {str(e)}")
                else:
                    st.error("⚠️ Please enter a valid email address.")
        
        with col2:
            st.markdown("""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;">
                <h4>🔒 Privacy & Security</h4>
                <ul style="font-size: 0.9em;">
                    <li>Your data is encrypted</li>
                    <li>We only access your calendar</li>
                    <li>No data is stored permanently</li>
                    <li>You can revoke access anytime</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.stop()
    
    else:
        # Success message for new auth
        if auth_success:
            st.success(f"🎉 Successfully connected as `{user_id}`! You can now start managing your calendar.")
            time.sleep(2)
            st.rerun()

        # User info and quick actions
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div class="success-message">
                <h4>👋 Welcome back, {user_id.split('@')[0]}!</h4>
                <p>Your calendar is connected and ready.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📅 View Events", key="view_events"):
                events = get_calendar_events(user_id)
                if events:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar events"})
                    st.session_state.messages.append({"role": "assistant", "content": "📅 **Your upcoming events:**\n\n" + "\n".join([f"• {e['summary']} - {e['start']}" for e in events[:5]])})
                else:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar events"})
                    st.session_state.messages.append({"role": "assistant", "content": "📅 You have no upcoming events scheduled."})
                st.rerun()
        
        with col3:
            if st.button("🔄 Refresh", key="refresh"):
                st.rerun()

        # Suggestions section
        st.markdown("### 💡 Quick Actions")
        suggestion_cols = st.columns(4)
        
        for i, suggestion in enumerate(SUGGESTIONS):
            col_idx = i % 4
            with suggestion_cols[col_idx]:
                if st.button(suggestion, key=f"suggestion_{i}"):
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
                                    st.session_state.messages.append({"role": "assistant", "content": reply})
                                else:
                                    error_msg = f"❌ Server error: {res.status_code}"
                                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                            except Exception as e:
                                error_msg = f"❌ Connection error: {str(e)}"
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        st.rerun()

        # Chat interface
        st.markdown("### 💬 Chat with Your Assistant")
        
        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input
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
                            st.markdown(reply)
                            st.session_state.messages.append({"role": "assistant", "content": reply})
                        else:
                            error_msg = f"❌ Server error ({res.status_code}): {res.text}"
                            st.markdown(error_msg)
                            st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    except requests.exceptions.Timeout:
                        error_msg = "⏰ Request timed out. Please try again."
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    except Exception as e:
                        error_msg = f"❌ Connection error: {str(e)}"
                        st.markdown(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: rgba(255,255,255,0.7); font-size: 0.8em;">
            <p>Powered by AI • Secure • Private</p>
            <p>Built with Streamlit and FastAPI</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()