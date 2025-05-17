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

# Template generation is now disabled to use the manually edited template file
# This prevents overwriting our custom changes to the template
# @app.on_event("startup")
# async def create_template():
#     # Template generation code removed to prevent overwriting custom template
#     pass

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
