import streamlit as st
import os
import sys
import time
from dotenv import load_dotenv
from litellm import completion

# Add the parent directory to sys.path to import prompts.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import prompt1, prompt2

# Load environment variables for API keys
load_dotenv()

# Standard input function without auto-focus attempts
def create_input():
    # Create a container for our input
    container = st.container()
    
    # Add the standard text input with a clear label
    with container:
        text_input = st.text_input(
            "Message the AI assistant...",
            key="user_input"
        )
    
    return text_input

# Page configuration
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Initialize session state for chat history and settings
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm your medical AI assistant. How can I help you today?"}
    ]

if "model" not in st.session_state:
    st.session_state.model = "gemini/gemini-2.0-flash"

if "prompt" not in st.session_state:
    st.session_state.prompt = prompt1

# Initialize user_input if not already in session state
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Custom CSS for styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Chat message styling */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
    }
    
    .user-message {
        background-color: #F7F7F8;
    }
    
    .assistant-message {
        background-color: #FFFFFF;
        border: 1px solid #E5E5E5;
    }
    
    /* Avatar styling */
    .avatar {
        width: 2.5rem;
        height: 2.5rem;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 1rem;
        font-weight: bold;
        color: white;
        flex-shrink: 0;
    }
    
    .user-avatar {
        background-color: #5436DA;
    }
    
    .assistant-avatar {
        background-color: #10A37F;
    }
    
    /* Message content */
    .message-content {
        flex-grow: 1;
        overflow-wrap: break-word;
    }
    
    /* Title styling */
    h1 {
        color: #10A37F;
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 1rem;
        text-align: center;
    }
    
    /* Focus the input field */
    .stTextInput input {
        border-radius: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1>Medical AI Assistant</h1>", unsafe_allow_html=True)

# Model and prompt selection dropdowns
col1, col2 = st.columns(2)

with col1:
    model = st.selectbox(
        "Model",
        options=["gemini/gemini-2.0-flash", "claude-3-opus-20240229"],
        index=0 if st.session_state.model == "gemini/gemini-2.0-flash" else 1,
        key="model_selector"
    )
    st.session_state.model = model

with col2:
    prompt_option = st.selectbox(
        "System Prompt",
        options=["Differential Diagnosis", "Medical Information"],
        index=0 if st.session_state.prompt == prompt1 else 1,
        key="prompt_selector"
    )
    
    # Map prompt options to actual prompts
    prompt_mapping = {
        "Differential Diagnosis": prompt1,
        "Medical Information": prompt2
    }
    
    st.session_state.prompt = prompt_mapping[prompt_option]

# Display chat messages from history
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    
    avatar_letter = "U" if role == "user" else "AI"
    avatar_class = "user-avatar" if role == "user" else "assistant-avatar"
    message_class = "user-message" if role == "user" else "assistant-message"
    
    st.markdown(f"""
    <div class="chat-message {message_class}">
        <div class="avatar {avatar_class}">{avatar_letter}</div>
        <div class="message-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)

# Add a spacer to ensure chat messages are visible above the input area
st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)

# Function to handle message submission
def handle_submit():
    if st.session_state.user_input.strip():
        user_message = st.session_state.user_input
        
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # Add a temporary message
        st.session_state.messages.append({"role": "assistant", "content": "Generating response..."})
        
        # Clear the input
        st.session_state.user_input = ""
        
        # Force a rerun to update the UI
        st.rerun()

# Add a note about clicking in the input field
st.info("⚠️ Please click in the input field below to start typing. Auto-focus is not supported in this Streamlit app.", icon="ℹ️")

# Use our standard input approach with a more visible design
col1, col2 = st.columns([6, 1])

with col1:
    # Use our function for the input
    user_input = create_input()
    
    # The input value is already in session state via the key="user_input"

with col2:
    if st.button("Send", on_click=handle_submit, use_container_width=True):
        pass  # The actual logic is in the handle_submit function

# Process AI response generation
if (st.session_state.messages and 
    st.session_state.messages[-1]["role"] == "assistant" and 
    st.session_state.messages[-1]["content"] == "Generating response..."):
    
    # Get the last user message
    user_message = None
    for msg in reversed(st.session_state.messages[:-1]):
        if msg["role"] == "user":
            user_message = msg["content"]
            break
    
    if user_message:
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": st.session_state.prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Remove the "Generating response..." message
            st.session_state.messages.pop()
            
            # Create a placeholder for the streaming response
            placeholder = st.empty()
            response_content = ""
            
            # Stream the response
            for chunk in completion(
                model=st.session_state.model,
                messages=messages,
                stream=True
            ):
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        response_content += delta.content
                        
                        # Update the placeholder with the current content
                        with placeholder:
                            st.markdown(f"""
                            <div class="chat-message assistant-message">
                                <div class="avatar assistant-avatar">AI</div>
                                <div class="message-content">{response_content}</div>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Add the final response to the session state
            if response_content:
                st.session_state.messages.append({"role": "assistant", "content": response_content})
            else:
                st.session_state.messages.append({"role": "assistant", "content": "I'm sorry, I couldn't generate a response. Please try again."})
                
        except Exception as e:
            # Add error message
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})
        
        # Rerun to update the UI with the final state
        st.rerun()

# Add a note about the limitation
st.markdown("""
<div style="text-align: center; margin-top: 10px; color: #666; font-size: 0.8em;">
    Note: Due to Streamlit limitations, auto-focus is not supported. Please click in the input field to type.
</div>
""", unsafe_allow_html=True)
