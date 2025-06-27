import streamlit as st
import requests
import json
import time

# Rasa server endpoint
RASA_API_URL = "http://localhost:5005/webhooks/rest/webhook"

# Page config
st.set_page_config(
    page_title="AI Career Counsellor",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)
# CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
    color: #C9D1D9;
}

.stApp {
    background-color: #0D1117;
    color: #C9D1D9;
}

.main-header {
    font-size: 2.8em;
    font-weight: bold;
    color: #58A6FF;
    text-align: center;
    margin-bottom: 25px;
    text-shadow: 1px 1px 8px rgba(88, 166, 255, 0.4);
}

.message-row {
    display: flex;
    margin-bottom: 12px;
    width: 100%;
}

.user-message, .bot-message {
    backdrop-filter: blur(10px);
    background-color: #161B22;
    padding: 12px 18px;
    border-radius: 18px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: transform 0.3s ease;
}

.user-message {
    border: 1px solid #238636;
    align-self: flex-end;
}

.bot-message {
    border: 1px solid rgba(200, 200, 200, 0.3);
    align-self: flex-start;
}

.user-message:hover, .bot-message:hover {
    transform: scale(1.02);
}

.stTextInput > div > div > input {
    border-radius: 15px;
    border: 2px solid #238636;
    padding: 15px;
    font-size: 1.1em;
    background-color: #161B22;
    color: #C9D1D9;
}
            
.stTextInput > div > div > input:focus {
    border: 2px solid #2ea043; 
    outline: none; /* Remove default browser outline */
    box-shadow: 0 0 0 2px rgba(46, 160, 67, 0.5); 
}
            
.stButton > button {
    background-color: #238636;
    color: white;
    border-radius: 15px;
    padding: 12px 30px;
    font-weight: bold;
    font-size: 1.1em;
    cursor: pointer;
}

.stButton > button:hover {
    background-color: #2ea043;
}

strong {
    color: #58A6FF; 
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# Title + intro
st.markdown('<h1 class="main-header">🎓 AI Virtual Career Counsellor</h1>', unsafe_allow_html=True)
st.write("I'm here to help you explore career paths based on your interests. Ask me anything!")

# Initialize chat memory
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display chat history
chat_history_container = st.container()
with chat_history_container:
    for msg_type, msg_content in st.session_state["messages"]:
        if msg_type == "user":
            st.markdown(f'<div class="message-row" style="justify-content: flex-end;"><div class="user-message">{msg_content}</div></div>', unsafe_allow_html=True)
        else:
            formatted_content = msg_content.replace('**', '<bold>').replace('##', '<bold>')
            formatted_content = formatted_content.replace('<bold>', '</bold>', 1) # Close the first ** or ##
            formatted_content = formatted_content.replace('<bold>', '</bold>') # Close any remaining ones
            st.markdown(f'<div class="message-row" style="justify-content: flex-start;"><div class="bot-message">{formatted_content}</div></div>', unsafe_allow_html=True)

# Send message to Rasa
def send_message_to_rasa(message):
    try:
        headers = {"Content-Type": "application/json"}
        payload = {"sender": "user", "message": message}
        response = requests.post(RASA_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"⚠️ Connection error: {e}")
        return []

# Handle message when user presses Enter
def handle_user_message():
    user_message = st.session_state.user_message_input.strip()
    if user_message:
        # Save user message
        st.session_state["messages"].append(("user", user_message))

        with st.spinner("CareerBot is typing..."):
            time.sleep(0.5)
            bot_responses = send_message_to_rasa(user_message)

        # Save bot response
        if bot_responses:
            for response in bot_responses:
                if "text" in response:
                    st.session_state["messages"].append(("bot", response["text"]))
        else:
            st.session_state["messages"].append(("bot", "⚠️ I'm having trouble connecting."))

        # Clear the input box
        st.session_state.user_message_input = ""

# Input field with Enter-to-send
st.text_input(
    "Type your message here...",
    key="user_message_input",
    on_change=handle_user_message,
    placeholder="Ask me anything about your career... 🎯"
)