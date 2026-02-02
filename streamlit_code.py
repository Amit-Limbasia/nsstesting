

import streamlit as st
import requests
from datetime import datetime
import json
import uuid

# Page configuration
st.set_page_config(
    page_title="Narayan Seva Sansthan Chat",
    page_icon="🙏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for WhatsApp-like UI
st.markdown("""
<style>
    .main {
        background-color: #e5ddd5;
    }
    
    .chat-header {
        background: linear-gradient(135deg, #128C7E 0%, #075E54 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        display: flex;
        align-items: center;
        gap: 15px;
    }
    
    .chat-header-avatar {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
    }
    
    .chat-header-info h1 {
        margin: 0;
        font-size: 18px;
        font-weight: 500;
    }
    
    .chat-header-info p {
        margin: 2px 0 0 0;
        opacity: 0.85;
        font-size: 13px;
    }
    
    .stButton > button {
        background: #128C7E;
        color: white;
        border-radius: 25px;
        padding: 10px 25px;
        border: none;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background: #075E54;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "mobile_no" not in st.session_state:
    st.session_state.mobile_no = ""
if "donor_name" not in st.session_state:
    st.session_state.donor_name = ""
if "ng_code" not in st.session_state:
    st.session_state.ng_code = 0
if "input_counter" not in st.session_state:
    st.session_state.input_counter = 0

# Helper function to check if string is a URL
def is_url(text):
    """Check if the given text is a URL"""
    if not text:
        return False
    return text.startswith(('http://', 'https://'))

# Sidebar
with st.sidebar:
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 🙏 Chat Configuration")
    
    mobile_no = st.text_input(
        "Mobile Number",
        value=st.session_state.mobile_no,
        placeholder="+919876543210",
        help="Enter mobile number with country code"
    )
    
    donor_name = st.text_input(
        "Your Name",
        value=st.session_state.donor_name,
        placeholder="Enter your name"
    )
    
    ng_code = st.number_input(
        "NG Code",
        value=st.session_state.ng_code,
        min_value=0,
        step=1,
        help="Enter your NG Code (Donor ID). Use 0 if you don't have one."
    )
    
    if st.button("💾 Save Details", use_container_width=True):
        st.session_state.mobile_no = mobile_no
        st.session_state.donor_name = donor_name
        st.session_state.ng_code = int(ng_code)
        st.success("Details saved!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fixed Backend API URL (hidden from UI)
    api_url = "https://nss-agent-testing-app.onrender.com/message"

    # Stats
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### 📊 Chat Statistics")
    st.metric("Total Messages", len(st.session_state.messages))
    st.metric("Your Messages", len([m for m in st.session_state.messages if m["role"] == "user"]))
    st.metric("AI Responses", len([m for m in st.session_state.messages if m["role"] == "assistant"]))
    
    # Display current configuration
    if st.session_state.mobile_no or st.session_state.donor_name or st.session_state.ng_code:
        st.markdown("---")
        st.markdown("**Current Configuration:**")
        if st.session_state.mobile_no:
            st.text(f"📱 {st.session_state.mobile_no}")
        if st.session_state.donor_name:
            st.text(f"👤 {st.session_state.donor_name}")
        if st.session_state.ng_code:
            st.text(f"🔢 NG Code: {st.session_state.ng_code}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Clear chat
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.markdown("""
<div class="chat-header">
    <div class="chat-header-avatar">🙏</div>
    <div class="chat-header-info">
        <h1>Narayan Seva Sansthan</h1>
        <p>AI Sadhak - Your helpful assistant</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Display messages
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.info("👋 Welcome! Start a conversation by typing a message below.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            content = message["content"]
            timestamp = message.get("timestamp", datetime.now().strftime("%I:%M %p"))
            has_image = message.get("has_image", False)
            image_url = message.get("image_url", "")

            if has_image and image_url:
                st.image(image_url, caption="User Image", width=200)
            
            st.markdown(content)
            st.caption(timestamp)

            if message["role"] == "assistant":
                classification = message.get("classification", "")
                sub_classification = message.get("sub_classification", "")
                confidence = message.get("confidence", "")
                
                if classification:
                    st.markdown(f'<div style="font-size: 0.85em; color: #555; margin-top: 8px;">📋 <strong>Classification:</strong> {classification}</div>', unsafe_allow_html=True)
                if sub_classification:
                    st.markdown(f'<div style="font-size: 0.85em; color: #555; margin-top: 4px;">📌 <strong>Sub-Classification:</strong> {sub_classification}</div>', unsafe_allow_html=True)
                if confidence:
                    st.markdown(f'<div style="font-size: 0.85em; color: #555; margin-top: 4px;">✅ <strong>Confidence:</strong> {confidence}</div>', unsafe_allow_html=True)



# Function to handle message sending
def send_message(user_input):
    if not user_input:
        return
        
    if not st.session_state.mobile_no:
        st.error("⚠️ Please enter your mobile number in the sidebar first!")
        return
    
    # Check if input is a URL (image)
    is_image_url = is_url(user_input)
    
    # Prepare message content
    if is_image_url:
        message_content = "[Image]"
        message_type = "image"
        image_url = user_input
    else:
        message_content = user_input
        message_type = "text"
        image_url = None
    
    # Add user message
    user_message = {
        "role": "user",
        "content": message_content if is_image_url else user_input,
        "timestamp": datetime.now().strftime("%I:%M %p")
    }
    
    if image_url:
        user_message["image_url"] = image_url
        user_message["has_image"] = True
    
    st.session_state.messages.append(user_message)
    
    # Show typing indicator
    with st.spinner("AI Sadhak is typing..."):
        try:
            # Prepare API request
            payload = {
                "WA_Auto_Id": 0,
                "WA_In_Out": "In",
                "Account_Code": 0,
                "WA_Received_At": datetime.now().isoformat(),
                "NGCode": st.session_state.ng_code,
                "Wa_Name": st.session_state.donor_name,
                "MobileNo": st.session_state.mobile_no,
                "WA_Msg_To": st.session_state.mobile_no,
                "WA_Msg_Text": user_input if not is_image_url else "",
                "WA_Msg_Type": message_type,
                "Integration_Type": "streamlit",
                "WA_Message_Id": str(uuid.uuid4()),
                "WA_Url": image_url if is_image_url else "",
                "Status": "success",
                "Donor_Name": st.session_state.donor_name
            }
            
            # Make API call
            response = requests.post(api_url, json=payload, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                
                # Parse classification
                ai_reason = result.get("ai_reason", "")
                classification_parts = ai_reason.split("|")
                main_class = classification_parts[0] if len(classification_parts) > 0 else ""
                sub_class = classification_parts[1] if len(classification_parts) > 1 else ""
                
                # Add bot response
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result.get("ai_response", "Sorry, I couldn't process your request."),
                    "timestamp": datetime.now().strftime("%I:%M %p"),
                    "classification": main_class,
                    "sub_classification": sub_class,
                    "confidence": "HIGH"
                })
            else:
                st.error(f"❌ API Error: {response.status_code}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Sorry, I encountered an error. Please try again.",
                    "timestamp": datetime.now().strftime("%I:%M %p")
                })
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Please try again.")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Request timed out. Please try again.",
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Error: {str(e)}",
                "timestamp": datetime.now().strftime("%I:%M %p")
            })
    
    # Increment counter to force input clear
    st.session_state.input_counter += 1
    st.rerun()

# Input area
st.markdown("---")

# Create a form to enable Enter key submission
with st.form(key="message_form", clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Type your message...",
            key=f"user_input_{st.session_state.input_counter}",
            placeholder="Type your message or image URL (https://...)...",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.form_submit_button("Send 📤", use_container_width=True)
    
    # Handle message sending
    if send_button and user_input:
        send_message(user_input)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
    <p>🙏 Narayan Seva Sansthan - AI-Powered Chat Assistant</p>
    <p>Powered by Gemini AI | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
