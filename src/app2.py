import streamlit as st
import litellm
from litellm import completion
import os
import sys
from dotenv import load_dotenv
import time

# Add the parent directory to sys.path to import prompts.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import prompt1, prompt2  # Import prompts from prompts.py

# Load API keys from environment variables
load_dotenv()
# litellm automatically reads environment variables like GEMINI_API_KEY and ANTHROPIC_API_KEY

# Set page config
st.set_page_config(
    page_title="Medical AI Assistant",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS to make the app look more like the Dash version
st.markdown("""
<style>
    /* Main container styling */
    .main {
        max-width: 900px;
        margin: 0 auto;
        background-color: #FFFFFF;
        box-shadow: 0 0 20px rgba(0, 0, 0, 0.05);
        font-family: Helvetica, Arial, sans-serif;
        display: flex;
        flex-direction: column;
        height: 100vh;
    }
    
    /* Header styling */
    header {
        padding: 16px 0;
        border-bottom: 1px solid #E5E5E5;
        background-color: #FFFFFF;
        position: sticky;
        top: 0;
        z-index: 10;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #F7F7F8;
        padding: 24px;
        border-bottom: 1px solid #E5E5E5;
        position: relative;
        line-height: 1.8;
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.3s ease-out;
    }
    
    .assistant-message {
        background-color: #FFFFFF;
        padding: 24px;
        border-bottom: 1px solid #E5E5E5;
        position: relative;
        line-height: 1.8;
        display: flex;
        align-items: flex-start;
        animation: fadeIn 0.3s ease-out;
    }
    
    /* User icon styling */
    .user-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #5436DA;
        margin-right: 15px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    
    /* Assistant icon styling */
    .assistant-icon {
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background-color: #10A37F;
        margin-right: 15px;
        flex-shrink: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    
    /* Message content styling */
    .message-content {
        flex-grow: 1;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Streamlit component styling */
    div.stButton > button {
        background-color: #10A37F;
        color: white;
        border: none;
        padding: 14px 28px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 1em;
        font-weight: 600;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        width: 100%;
    }
    
    div.stButton > button:hover {
        background-color: #0E8E6D;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    div.stSelectbox > div > div {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E5E5E5;
    }
    
    /* Code block styling for markdown content */
    pre {
        background-color: #f6f8fa;
        border-radius: 6px;
        padding: 16px;
        overflow-x: auto;
        margin: 16px 0;
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.9em;
        line-height: 1.5;
        border: 1px solid #e1e4e8;
    }
    
    code {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        background-color: rgba(0, 0, 0, 0.05);
        padding: 0.2em 0.4em;
        border-radius: 3px;
        font-size: 0.9em;
    }
    
    /* Table styling for markdown content */
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 16px 0;
    }
    
    th, td {
        border: 1px solid #e1e4e8;
        padding: 8px 12px;
        text-align: left;
    }
    
    th {
        background-color: #f6f8fa;
        font-weight: 600;
    }
    
    tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    /* Streamlit default element adjustments */
    .stTextInput > div > div > input {
        padding: 14px 16px;
        border-radius: 8px;
        border: 1px solid #E5E5E5;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
        font-size: 1em;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #10A37F;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2);
    }
    
    /* Fixed bottom input area */
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 20px;
        border-top: 1px solid #E5E5E5;
        z-index: 100;
        max-width: 900px;
        margin: 0 auto;
        box-shadow: 0 -5px 20px rgba(0,0,0,0.1);
    }
    
    /* Add padding to the bottom of the chat area to prevent content from being hidden behind the fixed input */
    .chat-container {
        padding-bottom: 180px;
        overflow-y: auto;
        flex-grow: 1;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Title styling */
    h1 {
        color: #10A37F;
        font-size: 1.3em;
        font-weight: 600;
        margin: 0;
        padding: 16px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# Initialize session state for user input
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
    
# Function to handle sending messages
def send_message():
    user_input = st.session_state.user_input_widget
    
    if user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Create a placeholder for the assistant's response
        response_placeholder = st.empty()
        
        # Display a loading message
        with response_placeholder:
            display_chat_message("assistant", "Generating response...")
        
        try:
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": st.session_state.selected_prompt},
                {"role": "user", "content": user_input}
            ]
            
            # Make API call with streaming
            response_content = ""
            
            # Create a placeholder for streaming content
            stream_placeholder = st.empty()
            
            # Make the API call with streaming
            for chunk in completion(
                model=st.session_state.model,
                messages=messages,
                stream=True
            ):
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    # Extract delta content from the chunk
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        response_content += delta.content
                        # Update the placeholder with the current content
                        with stream_placeholder:
                            display_chat_message("assistant", response_content)
                        time.sleep(0.01)  # Small delay to make streaming visible
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": response_content})
            
            # Clear the user input
            st.session_state.user_input_widget = ""
            
        except Exception as e:
            # Display error message
            error_message = f"Error: {str(e)}"
            with response_placeholder:
                display_chat_message("assistant", error_message)
            
            # Add error message to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": error_message})
        
        # Force a rerun to update the UI
        st.rerun()

# Function to display chat messages
def display_chat_message(role, content):
    if role == "user":
        st.markdown(f"""
        <div class="user-message">
            <div class="user-icon">U</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <div class="assistant-icon">AI</div>
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

# Title
st.markdown("<h1>Medical AI Assistant</h1>", unsafe_allow_html=True)

# Create a container for the chat area with scrolling
chat_container = st.container()

# Create a container for the fixed bottom input area
with st.container():
    st.markdown('<div class="fixed-bottom">', unsafe_allow_html=True)
    
    # Dropdowns for model and prompt selection
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.model = st.selectbox(
            "Model",
            options=["gemini/gemini-2.0-flash", "claude-3-opus-20240229"],
            index=0,
            key="model_dropdown"
        )

    with col2:
        prompt_option = st.selectbox(
            "System Prompt",
            options=["Differential Diagnosis", "Medical Information"],
            index=0,
            key="prompt_dropdown"
        )

    # Map prompt options to actual prompts
    prompt_mapping = {
        "Differential Diagnosis": prompt1,
        "Medical Information": prompt2
    }

    st.session_state.selected_prompt = prompt_mapping[prompt_option]

    # User input with Enter key handling
    st.text_input(
        "Message the AI assistant...", 
        key="user_input_widget",
        on_change=send_message
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display chat history in the chat container
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        display_chat_message(message["role"], message["content"])
    
    # Display a welcome message if chat history is empty
    if not st.session_state.chat_history:
        display_chat_message("assistant", "Hello! I'm your medical AI assistant. How can I help you today?")
    
    st.markdown('</div>', unsafe_allow_html=True)
