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

# Enhanced CSS styling with beautiful gradients and better alignment
st.markdown("""
    <style>
    /* Main background with animated gradient */
    .main {
        background: linear-gradient(-45deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        min-height: 100vh;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Global styles */
    .stApp {
        background: transparent !important;
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Header styling */
    .main-header {
        background: rgba(255, 255, 255, 0.15);
        padding: 2rem;
        border-radius: 20px;
        backdrop-filter: blur(20px);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(45deg, #fff, #f0f0f0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 1rem;
    }
    
    /* Status indicator */
    .status-container {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.1);
        padding: 0.5rem 1rem;
        border-radius: 25px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-online { 
        background-color: #4CAF50; 
        box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
    }
    
    .status-offline { 
        background-color: #f44336; 
        box-shadow: 0 0 10px rgba(244, 67, 54, 0.5);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    /* Card containers */
    .card-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Auth container */
    .auth-container {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        border-radius: 20px;
        padding: 2rem;
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        text-align: center;
        margin: 2rem 0;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 2px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.2);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2) !important;
        color: white !important;
        padding: 1rem 2rem !important;
        border-radius: 15px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        background: linear-gradient(45deg, #5a6fd8, #6a4190) !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stChatMessage.user {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2), rgba(118, 75, 162, 0.2));
        border: 1px solid rgba(102, 126, 234, 0.3);
        margin-left: 2rem;
    }
    
    .stChatMessage.assistant {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.2));
        border: 1px solid rgba(34, 197, 94, 0.3);
        margin-right: 2rem;
    }
    
    /* Suggestions grid */
    .suggestions-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .suggestion-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
        cursor: pointer;
        text-align: center;
    }
    
    .suggestion-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.1));
    }
    
    /* Success/Error messages */
    .message-box {
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .success-box {
        background: linear-gradient(135deg, rgba(34, 197, 94, 0.2), rgba(16, 185, 129, 0.2));
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .error-box {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(220, 38, 38, 0.2));
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .card-container {
            padding: 1rem;
        }
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
    # Header with animated gradient background
    backend_status = check_backend_status()
    status_color = "status-online" if backend_status else "status-offline"
    status_text = "Online" if backend_status else "Offline"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>📅 Smart Calendar Assistant</h1>
        <p>Your AI-powered calendar management companion</p>
        <div class="status-container">
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
        <div class="auth-container">
            <h2>🔐 Welcome to Smart Calendar Assistant</h2>
            <p>Please authenticate with your Google Calendar to get started.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown('<div class="card-container">', unsafe_allow_html=True)
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
                            st.markdown('<div class="success-box message-box">✅ Already authenticated! Redirecting...</div>', unsafe_allow_html=True)
                            redirect_url = f"https://calender-agent-frontend-synv22yjhxvmcwhajarhte.streamlit.app/?user_id={email}&auth_success=true"
                            st.markdown(f"<meta http-equiv='refresh' content='2; URL={redirect_url}' />", unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="message-box">🔗 Redirecting to Google OAuth...</div>', unsafe_allow_html=True)
                            response = requests.get(f"{API_BASE}/auth/url", params={"user_id": email})
                            auth_url = response.json().get("auth_url")
                            if auth_url:
                                st.markdown(f"<meta http-equiv='refresh' content='2; URL={auth_url}' />", unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="error-box message-box">⚠️ Failed to get authentication URL.</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-box message-box">❌ Connection error: {str(e)}</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-box message-box">⚠️ Please enter a valid email address.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="card-container">
                <h4>🔒 Privacy & Security</h4>
                <ul style="font-size: 0.9em; text-align: left;">
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
            st.markdown(f'<div class="success-box message-box">🎉 Successfully connected as `{user_id}`! You can now start managing your calendar.</div>', unsafe_allow_html=True)
            time.sleep(2)
            st.rerun()

        # User info and quick actions
        st.markdown(f"""
        <div class="card-container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
                <div>
                    <h3>👋 Welcome back, {user_id.split('@')[0]}!</h3>
                    <p>Your calendar is connected and ready.</p>
                </div>
                <div style="display: flex; gap: 1rem;">
                    <button onclick="window.location.reload()" style="background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 0.5rem 1rem; border: none; border-radius: 10px; cursor: pointer;">🔄 Refresh</button>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Quick actions
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 View Events", key="view_events"):
                events = get_calendar_events(user_id)
                if events:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar events"})
                    st.session_state.messages.append({"role": "assistant", "content": "📅 **Your upcoming events:**\n\n" + "\n".join([f"• {e['summary']} - {e['start']}" for e in events[:5]])})
                else:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar events"})
                    st.session_state.messages.append({"role": "assistant", "content": "📅 You have no upcoming events scheduled."})
                st.rerun()
        
        with col2:
            if st.button("📊 Quick Stats", key="quick_stats"):
                events = get_calendar_events(user_id)
                if events:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar stats"})
                    st.session_state.messages.append({"role": "assistant", "content": f"📊 **Calendar Stats:**\n• Total events: {len(events)}\n• Next event: {events[0]['summary'] if events else 'None'}"})
                else:
                    st.session_state.messages.append({"role": "user", "content": "Show my calendar stats"})
                    st.session_state.messages.append({"role": "assistant", "content": "📊 **Calendar Stats:**\n• No events scheduled"})
                st.rerun()
        
        with col3:
            if st.button("🧹 Clear Chat", key="clear_chat"):
                st.session_state.messages = []
                st.rerun()

        # Suggestions section with better layout
        st.markdown("### 💡 Quick Actions")
        st.markdown('<div class="suggestions-grid">', unsafe_allow_html=True)
        
        # Create a grid of suggestion buttons
        for i, suggestion in enumerate(SUGGESTIONS):
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
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Chat interface
        st.markdown("### 💬 Chat with Your Assistant")
        st.markdown('<div class="card-container">', unsafe_allow_html=True)
        
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
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Footer
        st.markdown("""
        <div class="footer">
            <p style="margin: 0; color: rgba(255,255,255,0.7);">Powered by AI • Secure • Private</p>
            <p style="margin: 0; color: rgba(255,255,255,0.5); font-size: 0.9em;">Built with Streamlit and FastAPI</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 