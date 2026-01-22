import streamlit as st
import requests
from datetime import datetime

# ===============================
# Page configuration
# ===============================
st.set_page_config(
    page_title="Narayan Seva Sansthan Chat",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# Custom CSS
# ===============================
st.markdown("""
<style>
.main { background-color: #e5ddd5; }
.chat-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 15px 15px 0 0;
    margin-bottom: 10px;
}
.message-container { display: flex; margin: 15px 0; }
.user-message { justify-content: flex-end; }
.bot-message { justify-content: flex-start; }
.message-bubble {
    max-width: 70%;
    padding: 12px 16px;
    border-radius: 18px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.user-bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}
.bot-bubble { background: white; color: #303030; }
.message-time { font-size: 11px; opacity: 0.7; text-align: right; }
.message-image {
    max-width: 100%;
    max-height: 350px;
    border-radius: 10px;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# Session State
# ===============================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mobile_no" not in st.session_state:
    st.session_state.mobile_no = ""
if "donor_name" not in st.session_state:
    st.session_state.donor_name = ""
if "ng_code" not in st.session_state:
    st.session_state.ng_code = 0
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# ===============================
# Helper
# ===============================
def is_url(text):
    return text.startswith(("http://", "https://"))

# ===============================
# Sidebar
# ===============================
with st.sidebar:
    st.markdown("### 🙏 Chat Configuration")

    st.session_state.mobile_no = st.text_input(
        "Mobile Number",
        value=st.session_state.mobile_no,
        placeholder="+919876543210"
    )

    st.session_state.donor_name = st.text_input(
        "Your Name",
        value=st.session_state.donor_name
    )

    st.session_state.ng_code = st.number_input(
        "NG Code",
        min_value=0,
        value=st.session_state.ng_code
    )

    st.markdown("---")
    st.markdown("### ⚙️ API Configuration")

    api_url = st.text_input(
        "Backend API URL",
        value="https://nss-agent-testing-app.onrender.com/message"
    )

    st.markdown("---")
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# ===============================
# Header
# ===============================
st.markdown("""
<div class="chat-header">
    <h1>🙏 Narayan Seva Sansthan</h1>
    <p>AI Sadhak - Your helpful assistant</p>
</div>
""", unsafe_allow_html=True)

# ===============================
# Model Info + Architecture
# ===============================
st.write("🔍 **Current Model:** `gemini-2.0-flash` | ⚙️ **Mode:** `Event-Driven with Local API`")

with st.expander("ℹ️ System Architecture & Workflow"):
    st.graphviz_chart("""
    digraph {
        rankdir=LR;
        node [shape=box style=filled fillcolor=lightblue];
        U [label="User" shape=circle fillcolor=gold];
        P [label="Perception" fillcolor=lightgreen];
        Pl [label="Planner" fillcolor=salmon];
        E [label="Executor" fillcolor=lightyellow];
        DB [label="Local API / DB" shape=cylinder fillcolor=lightgrey];
        U -> P [label="Text/Image"];
        P -> Pl [label="Analysis"];
        Pl -> E [label="Intent"];
        E -> DB [label="Fetch/Store"];
        DB -> E [label="Data"];
        E -> U [label="Response"];
    }
    """)

# ===============================
# Chat Area
# ===============================
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown('<div class="message-container user-message"><div class="message-bubble user-bubble">', unsafe_allow_html=True)
        if msg.get("image_url"):
            st.markdown(f'<img src="{msg["image_url"]}" class="message-image">', unsafe_allow_html=True)
        st.write(msg["content"])
        st.markdown(f'<div class="message-time">{msg["time"]}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="message-container bot-message"><div class="message-bubble bot-bubble">', unsafe_allow_html=True)
        st.write(msg["content"])
        st.markdown(f'<div class="message-time">{msg["time"]}</div>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# ===============================
# Input Area
# ===============================
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Message",
        key="user_input",
        label_visibility="collapsed",
        placeholder="Type message or image URL..."
    )

with col2:
    send = st.button("Send 📤")

# ===============================
# Send Logic
# ===============================
if send and user_input:
    if not st.session_state.mobile_no:
        st.error("Please enter mobile number")
    else:
        image_url = user_input if is_url(user_input) else None

        st.session_state.messages.append({
            "role": "user",
            "content": "[Image]" if image_url else user_input,
            "image_url": image_url,
            "time": datetime.now().strftime("%I:%M %p")
        })

        payload = {
            "MobileNo": st.session_state.mobile_no,
            "Donor_Name": st.session_state.donor_name,
            "NGCode": st.session_state.ng_code,
            "WA_Msg_Text": "" if image_url else user_input,
            "WA_Msg_Type": "image" if image_url else "text",
            "WA_Url": image_url,
            "Integration_Type": "streamlit"
        }

        with st.spinner("AI Sadhak is typing..."):
            try:
                res = requests.post(api_url, json=payload, timeout=90)
                if res.status_code == 200:
                    data = res.json()
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": data.get("ai_response", "No response"),
                        "time": datetime.now().strftime("%I:%M %p")
                    })
                else:
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "API Error occurred",
                        "time": datetime.now().strftime("%I:%M %p")
                    })
            except Exception as e:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": str(e),
                    "time": datetime.now().strftime("%I:%M %p")
                })

        # 🔥 CLEAR INPUT AFTER SEND
        st.session_state.user_input = ""
        st.rerun()

# ===============================
# Footer
# ===============================
st.markdown("---")
st.markdown(
    "<center><small>🙏 Narayan Seva Sansthan | AI Sadhak | Powered by Gemini & Streamlit</small></center>",
    unsafe_allow_html=True
)
