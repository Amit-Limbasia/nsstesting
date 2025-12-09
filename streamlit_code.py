import streamlit as st
import requests
from datetime import datetime
import json

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
    /* Main container */
    .main {
        background-color: #e5ddd5;
    }
    
    /* Chat header */
    .chat-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px 15px 0 0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .chat-header h1 {
        margin: 0;
        font-size: 24px;
        font-weight: 600;
    }
    
    .chat-header p {
        margin: 5px 0 0 0;
        opacity: 0.9;
        font-size: 14px;
    }
    
    /* Message container */
    .message-container {
        display: flex;
        margin: 15px 0;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        justify-content: flex-end;
    }
    
    .bot-message {
        justify-content: flex-start;
    }
    
    /* Message bubble */
    .message-bubble {
        max-width: 70%;
        padding: 12px 16px;
        border-radius: 18px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        position: relative;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-bottom-right-radius: 4px;
        margin-left: auto;
    }
    
    .bot-bubble {
        background: white;
        color: #303030;
        border-bottom-left-radius: 4px;
    }
    
    .message-text {
        font-size: 15px;
        line-height: 1.5;
        margin-bottom: 5px;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    .message-time {
        font-size: 11px;
        opacity: 0.7;
        text-align: right;
        margin-top: 5px;
    }
    
    /* Classification badge */
    .classification-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        margin-top: 8px;
        backdrop-filter: blur(10px);
    }
    
    .bot-classification {
        background: #f0f0f0;
        color: #666;
    }
    
    /* Classification details */
    .classification-details {
        font-size: 12px;
        margin-top: 8px;
        padding: 8px 12px;
        background: rgba(0,0,0,0.05);
        border-radius: 10px;
        border-left: 3px solid #667eea;
    }
    
    .classification-label {
        font-weight: 600;
        color: #667eea;
        margin-right: 5px;
    }
    
    /* Message image */
    .message-image {
        max-width: 100%;
        max-height: 400px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: block;
    }
    
    /* Input area */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #667eea;
        padding: 12px 20px;
        font-size: 15px;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 25px;
        padding: 12px 30px;
        border: none;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: #f8f9fa;
    }
    
    /* Info boxes */
    .info-box {
        background: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    
    .info-box h3 {
        color: #667eea;
        font-size: 16px;
        margin-bottom: 10px;
    }
    
    /* Typing indicator */
    .typing-indicator {
        display: flex;
        gap: 4px;
        padding: 10px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite;
    }
    
    .typing-dot:nth-child(2) { animation-delay: 0.2s; }
    .typing-dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-10px); }
    }
    
    /* Empty div styles */
    .empty-start, .empty-end {
        height: 0;
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
    
    # API Configuration
    st.markdown('<div class="info-box">', unsafe_allow_html=True)
    st.markdown("### ⚙️ API Configuration")
    api_url = st.text_input(
        "Backend API URL",
        value="http://localhost:10000/message",
        help="URL of your backend API"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
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
    <h1>🙏 Narayan Seva Sansthan</h1>
    <p>AI Sadhak - Your helpful assistant</p>
</div>
""", unsafe_allow_html=True)

# Display messages
chat_container = st.container()
with chat_container:
    if not st.session_state.messages:
        st.info("👋 Welcome! Start a conversation by typing a message below.")
    
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        timestamp = message.get("timestamp", datetime.now().strftime("%I:%M %p"))
        classification = message.get("classification", "")
        sub_classification = message.get("sub_classification", "")
        confidence = message.get("confidence", "")
        has_image = message.get("has_image", False)
        image_url = message.get("image_url", "")
        
        if role == "user":
            # Start user message bubble
            st.markdown('<div class="message-container user-message"><div class="message-bubble user-bubble">', unsafe_allow_html=True)
            
            # Display image if present
            if has_image and image_url:
                st.markdown(f'<img src="{image_url}" class="message-image" />', unsafe_allow_html=True)
            
            # Display message text using st.write (safe from HTML injection)
            st.markdown(f'<div class="message-text">', unsafe_allow_html=True)
            st.write(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display timestamp
            st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)
            
            # End user message bubble
            st.markdown('</div></div>', unsafe_allow_html=True)
        else:
            # Start bot message bubble
            st.markdown('<div class="message-container bot-message"><div class="message-bubble bot-bubble">', unsafe_allow_html=True)
            
            # Display message text using st.write (safe from HTML injection)
            st.markdown(f'<div class="message-text">', unsafe_allow_html=True)
            st.write(content)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Display timestamp
            st.markdown(f'<div class="message-time">{timestamp}</div>', unsafe_allow_html=True)
            
            # Display classification details
            if classification:
                st.markdown(f'<div class="classification-details"><span class="classification-label">📋 Classification:</span>{classification}</div>', unsafe_allow_html=True)
            if sub_classification:
                st.markdown(f'<div class="classification-details"><span class="classification-label">📌 Sub-Classification:</span>{sub_classification}</div>', unsafe_allow_html=True)
            if confidence:
                st.markdown(f'<div class="classification-details"><span class="classification-label">✅ Confidence:</span>{confidence}</div>', unsafe_allow_html=True)
            
            # End bot message bubble
            st.markdown('</div></div>', unsafe_allow_html=True)

# Input area
st.markdown("---")
col1, col2 = st.columns([5, 1])

with col1:
    user_input = st.text_input(
        "Type your message...",
        key="user_input",
        placeholder="Type your message or image URL (https://...)...",
        label_visibility="collapsed"
    )

with col2:
    send_button = st.button("Send 📤", use_container_width=True)

# Handle message sending
if send_button and user_input:
    if not st.session_state.mobile_no:
        st.error("⚠️ Please enter your mobile number in the sidebar first!")
    else:
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
                    "WA_Auto_Id": None,
                    "WA_In_Out": "In",
                    "Account_Code": None,
                    "WA_Received_At": datetime.now().isoformat(),
                    "NGCode": st.session_state.ng_code,
                    "Wa_Name": st.session_state.donor_name,
                    "MobileNo": st.session_state.mobile_no,
                    "WA_Msg_To": st.session_state.mobile_no,
                    "WA_Msg_Text": user_input if not is_image_url else "",
                    "WA_Msg_Type": message_type,
                    "Integration_Type": "streamlit",
                    "WA_Message_Id": None,
                    "WA_Url": image_url if is_image_url else None,
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
        
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px; padding: 20px;'>
    <p>🙏 Narayan Seva Sansthan - AI-Powered Chat Assistant</p>
    <p>Powered by Gemini AI | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)