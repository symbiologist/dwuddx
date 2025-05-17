import os
import sys
import json
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from litellm import completion
import uvicorn

# Add the parent directory to sys.path to import prompts.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import prompt1, prompt2  # Import prompts from prompts.py

# Load API keys from environment variables
load_dotenv()
# litellm automatically reads environment variables like GEMINI_API_KEY and ANTHROPIC_API_KEY

# Create FastAPI app
app = FastAPI(title="Medical AI Assistant")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up templates and static files
# Use absolute paths for templates and static files
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(base_dir, "templates")
assets_dir = os.path.join(base_dir, "assets")

templates = Jinja2Templates(directory=templates_dir)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

# Create templates directory if it doesn't exist
os.makedirs(templates_dir, exist_ok=True)

# Define models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    user_message: str
    model_name: str
    prompt_name: str

# In-memory chat history (in a real app, this would be stored in a database)
chat_history: Dict[str, List[Message]] = {}

# Create HTML template
@app.on_event("startup")
async def create_template():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Medical AI Assistant</title>
        <link rel="stylesheet" href="/assets/style.css">
        <!-- Add Marked.js for Markdown rendering -->
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <script>
            // Function to handle form submission
            async function submitMessage(event) {
                event.preventDefault();
                
                const userInput = document.getElementById('user-input');
                const userMessage = userInput.value.trim();
                
                if (!userMessage) return;
                
                // Get selected model and prompt
                const modelSelect = document.getElementById('model-dropdown');
                const promptSelect = document.getElementById('prompt-dropdown');
                const modelName = modelSelect.value;
                const promptName = promptSelect.value;
                
                // Add user message to chat
                addMessageToChat('user', userMessage);
                
                // Clear input and reset height
                userInput.value = '';
                userInput.style.height = '48px'; // Reset to min-height
                
                // Add temporary assistant message
                const assistantMsgId = 'assistant-msg-' + Date.now();
                addMessageToChat('assistant', 'Generating response...', assistantMsgId);
                
                // Start SSE connection for streaming response
                const eventSource = new EventSource(`/stream?user_message=${encodeURIComponent(userMessage)}&model_name=${encodeURIComponent(modelName)}&prompt_name=${encodeURIComponent(promptName)}`);
                
                let responseContent = '';
                
                eventSource.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    
                    if (data.content) {
                        responseContent = data.content;
                        
                        // Update the assistant message with the current content
                        const assistantMsg = document.getElementById(assistantMsgId);
                        if (assistantMsg) {
                            // Render markdown content
                            assistantMsg.innerHTML = marked.parse(responseContent);
                        }
                        
                        // Scroll to bottom
                        scrollToBottom();
                    }
                    
                    if (data.status === 'complete') {
                        eventSource.close();
                    }
                };
                
                eventSource.onerror = function(error) {
                    console.error('SSE Error:', error);
                    eventSource.close();
                    
                    // Update with error message if no content received
                    if (!responseContent) {
                        const assistantMsg = document.getElementById(assistantMsgId);
                        if (assistantMsg) {
                            assistantMsg.innerHTML = "Error: Failed to generate response. Please try again.";
                        }
                    }
                };
            }
            
            // Function to add a message to the chat
            function addMessageToChat(role, content, id = null) {
                const chatArea = document.getElementById('chat-area');
                
                // Remove margin-bottom from previous last message if it exists
                const lastMessage = chatArea.lastElementChild;
                if (lastMessage) {
                    lastMessage.style.marginBottom = '0';
                }
                
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${role}-message`;
                messageDiv.style.width = "100%"; // Ensure full width
                messageDiv.style.marginBottom = '70px'; // Add significant bottom margin to the last message
                messageDiv.style.padding = '16px 24px'; // Add padding
                
                // Create avatar element
                const avatarDiv = document.createElement('div');
                avatarDiv.style.width = '32px';
                avatarDiv.style.height = '32px';
                avatarDiv.style.borderRadius = '50%';
                avatarDiv.style.marginRight = '12px';
                avatarDiv.style.flexShrink = '0';
                avatarDiv.style.display = 'flex';
                avatarDiv.style.alignItems = 'center';
                avatarDiv.style.justifyContent = 'center';
                avatarDiv.style.color = 'white';
                avatarDiv.style.fontWeight = 'bold';
                avatarDiv.style.fontSize = '14px';
                
                // Create message container with avatar and content
                const messageContainer = document.createElement('div');
                messageContainer.style.display = 'flex';
                messageContainer.style.alignItems = 'flex-start';
                messageContainer.style.width = '100%';
                
                const contentDiv = document.createElement('div');
                contentDiv.style.width = "100%"; // Ensure content takes full width
                contentDiv.style.maxWidth = "100%"; // Maximum width
                contentDiv.style.borderRadius = '12px';
                contentDiv.style.padding = '12px 16px';
                contentDiv.style.boxShadow = '0 1px 2px rgba(0,0,0,0.05)';
                
                if (role === 'user') {
                    // User message styling
                    messageDiv.style.backgroundColor = '#f8f9fa';
                    avatarDiv.style.backgroundColor = '#4361EE';
                    avatarDiv.textContent = 'U';
                    contentDiv.style.backgroundColor = '#f0f7ff';
                    contentDiv.style.border = '1px solid #e6f0ff';
                    contentDiv.textContent = content;
                } else {
                    // Assistant message styling
                    messageDiv.style.backgroundColor = 'white';
                    avatarDiv.style.backgroundColor = '#3A0CA3';
                    avatarDiv.textContent = 'AI';
                    contentDiv.style.backgroundColor = 'white';
                    contentDiv.style.border = '1px solid #eaeaea';
                    contentDiv.innerHTML = marked.parse(content);
                }
                
                if (id) {
                    contentDiv.id = id;
                }
                
                messageContainer.appendChild(avatarDiv);
                messageContainer.appendChild(contentDiv);
                messageDiv.appendChild(messageContainer);
                chatArea.appendChild(messageDiv);
                
                scrollToBottom();
            }
            
            // Function to scroll to the bottom of the chat
            function scrollToBottom() {
                const chatArea = document.getElementById('chat-area');
                // Use setTimeout to ensure scrolling happens after DOM updates
                setTimeout(() => {
                    chatArea.scrollTop = chatArea.scrollHeight;
                    
                    // Ensure the last message is fully visible and not covered by the input area
                    const lastMessage = chatArea.lastElementChild;
                    if (lastMessage) {
                        const lastMessageRect = lastMessage.getBoundingClientRect();
                        const chatAreaRect = chatArea.getBoundingClientRect();
                        const inputArea = document.querySelector('.input-area');
                        const inputAreaRect = inputArea.getBoundingClientRect();
                        
                        // Check if the last message is partially covered by the input area
                        if (lastMessageRect.bottom > inputAreaRect.top) {
                            // Adjust scroll to ensure the last message is fully visible
                            chatArea.scrollTop += (lastMessageRect.bottom - inputAreaRect.top + 20); // Add extra padding
                        }
                    }
                }, 10);
            }
            
            // Function to auto-resize textarea as user types
            function autoResizeTextarea(textarea) {
                // Reset height to auto to get the correct scrollHeight
                textarea.style.height = 'auto';
                // Set the height to match the content (scrollHeight)
                textarea.style.height = textarea.scrollHeight + 'px';
            }
            
            // Set focus to input field when page loads and set up auto-resize
            document.addEventListener('DOMContentLoaded', function() {
                const textarea = document.getElementById('user-input');
                textarea.focus();
                
                // Auto-resize textarea as user types
                textarea.addEventListener('input', function() {
                    autoResizeTextarea(this);
                });
                
                // Handle Enter key to submit form (but allow Shift+Enter for new line)
                textarea.addEventListener('keydown', function(event) {
                    if (event.key === 'Enter' && !event.shiftKey) {
                        event.preventDefault(); // Prevent new line
                        document.getElementById('chat-form').dispatchEvent(new Event('submit'));
                    }
                });
                
                // Initialize height
                autoResizeTextarea(textarea);
                
                // Add welcome message
                addMessageToChat('assistant', 'Hello! I am your medical AI assistant. How can I help you today?');
            });
        </script>
    </head>
    <body style="width: 100%; margin: 0; padding: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; color: #1A1A2E; background-color: #f8f9fa;">
        <div class="container" style="max-width: 1200px; width: 100%; margin: 0 auto; display: flex; flex-direction: column; height: 100vh; overflow: hidden; background-color: white; box-shadow: 0 0 20px rgba(0,0,0,0.05);">
            <header style="padding: 16px 0; border-bottom: 1px solid #eaeaea; background: linear-gradient(to right, #4361EE, #3A0CA3); color: white;">
                <h1 style="text-align: center; margin: 0; font-size: 1.5em; font-weight: 600; letter-spacing: -0.5px;">Medical AI Assistant</h1>
            </header>
            
            <main style="width: 100%; flex: 1; overflow: hidden; display: flex; flex-direction: column;">
                <div id="chat-area" class="chat-area" style="width: 100%; flex: 1; overflow-y: auto; padding-bottom: 20px;">
                    <!-- Chat messages will be added here dynamically -->
                </div>
            </main>
            
            <footer class="input-area" style="max-width: 1100px; width: 100%; flex-shrink: 0; position: relative; z-index: 100; box-shadow: 0 -5px 20px rgba(0,0,0,0.05); background-color: white; padding: 16px 24px; border-top: 1px solid #eaeaea;">
                <div class="dropdown-row" style="display: flex; gap: 16px; margin-bottom: 16px;">
                    <div class="dash-dropdown-container" style="flex: 1;">
                        <label for="model-dropdown" style="display: block; margin-bottom: 6px; font-size: 0.8em; color: #666; font-weight: 500;">Model</label>
                        <select id="model-dropdown" class="dropdown" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid #ddd; background-color: #f9f9f9; font-size: 0.9em; color: #333; appearance: none; background-repeat: no-repeat; background-position: right 12px center; cursor: pointer; transition: all 0.2s ease;">
                            <option value="gemini/gemini-2.0-flash">Gemini 2.0 Flash</option>
                            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                        </select>
                    </div>
                    
                    <div class="dash-dropdown-container" style="flex: 1;">
                        <label for="prompt-dropdown" style="display: block; margin-bottom: 6px; font-size: 0.8em; color: #666; font-weight: 500;">System Prompt</label>
                        <select id="prompt-dropdown" class="dropdown" style="width: 100%; padding: 8px 12px; border-radius: 8px; border: 1px solid #ddd; background-color: #f9f9f9; font-size: 0.9em; color: #333; appearance: none; background-repeat: no-repeat; background-position: right 12px center; cursor: pointer; transition: all 0.2s ease;">
                            <option value="prompt1">Differential Diagnosis</option>
                            <option value="prompt2">Medical Information</option>
                        </select>
                    </div>
                </div>
                
                <form id="chat-form" onsubmit="submitMessage(event)" class="input-row" style="width: 100%; gap: 16px; display: flex; align-items: flex-start;">
                    <div class="dash-input-container" style="width: 100%; flex: 1; position: relative;">
                        <textarea id="user-input" placeholder="Enter message..." autocomplete="off" rows="1" style="width: 100%; font-size: 1em; font-family: inherit; border-radius: 12px; border: 1px solid #ddd; padding: 12px 16px; resize: none; min-height: 24px; max-height: 120px; overflow-y: auto; box-shadow: 0 2px 6px rgba(0,0,0,0.05); transition: border-color 0.2s ease, box-shadow 0.2s ease; outline: none;"></textarea>
                        <style>
                            #user-input:focus {
                                border-color: #4361EE;
                                box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
                            }
                            .send-button:hover {
                                transform: translateY(-1px);
                                box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                            }
                            .send-button:active {
                                transform: translateY(0);
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            }
                            select.dropdown:hover {
                                border-color: #4361EE;
                            }
                            select.dropdown:focus {
                                border-color: #4361EE;
                                box-shadow: 0 0 0 2px rgba(67, 97, 238, 0.2);
                                outline: none;
                            }
                        </style>
                    </div>
                    
                    <button type="submit" class="send-button" style="align-self: flex-start; border-radius: 12px; border: none; padding: 10px 16px; font-size: 0.9em; font-weight: 500; height: 40px; min-width: 80px; background: linear-gradient(to right, #4361EE, #3A0CA3); color: white; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">Send</button>
                </form>
            </footer>
        </div>
    </body>
    </html>
    """
    
    # Write the HTML template to the templates directory
    template_file = os.path.join(templates_dir, "index.html")
    with open(template_file, "w") as f:
        f.write(html_content)

# Define routes
@app.get("/", response_class=HTMLResponse)
async def get_html(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# SSE endpoint for streaming responses
@app.get("/stream")
async def stream_response(
    user_message: str,
    model_name: str,
    prompt_name: str
):
    async def event_generator():
        try:
            # Select the prompt based on the dropdown
            system_prompt = ""
            if prompt_name == "prompt1":
                system_prompt = prompt1
            elif prompt_name == "prompt2":
                system_prompt = prompt2
            else:
                system_prompt = prompt1  # Default to prompt1 if something goes wrong
            
            # Prepare messages for the API call
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Initialize response content
            content = ""
            
            # Start streaming response
            response_stream = completion(
                model=model_name,
                messages=messages,
                stream=True  # Enable streaming
            )
            
            # Stream each chunk as an SSE event
            for chunk in response_stream:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    # Extract delta content from the chunk
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        content += delta.content
                        
                        # Send the current content as an SSE event
                        yield f"data: {json.dumps({'content': content, 'status': 'streaming'})}\n\n"
                        
                        # Add a small delay to control the stream rate
                        await asyncio.sleep(0.01)
            
            # Send a final event to indicate completion
            yield f"data: {json.dumps({'content': content, 'status': 'complete'})}\n\n"
            
        except Exception as e:
            # Send error message
            error_msg = f"Error: {str(e)}"
            yield f"data: {json.dumps({'content': error_msg, 'status': 'complete'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )

# Run the app
if __name__ == "__main__":
    uvicorn.run("app3:app", host="0.0.0.0", port=8055, reload=True)
