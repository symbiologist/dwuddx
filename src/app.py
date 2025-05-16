import dash
from dash import dcc, html, callback_context
from dash.dependencies import Input, Output, State
import litellm
from litellm import completion
import os
import sys
import json
from dash import clientside_callback, ClientsideFunction
from dotenv import load_dotenv

# Add the parent directory to sys.path to import prompts.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from prompts import prompt1, prompt2 # Import prompts from prompts.py

# Load API keys from environment variables
load_dotenv()
# litellm automatically reads environment variables like GEMINI_API_KEY and ANTHROPIC_API_KEY

# Set up the app with external stylesheets
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ]
)

# App layout with modern ChatGPT-inspired styling
app.layout = html.Div(style={
    'maxWidth': '900px',
    'margin': '0 auto',
    'height': '100vh',
    'display': 'flex',
    'flexDirection': 'column',
    'backgroundColor': '#FFFFFF',
    'boxShadow': '0 0 20px rgba(0, 0, 0, 0.05)',
    'fontFamily': 'Helvetica, Arial, sans-serif',
}, children=[
    # Store for streaming response
    dcc.Store(id='streaming-response', data=''),
    # Store for current message ID
    dcc.Store(id='current-message-id', data=0),
    # Store for streaming content
    dcc.Store(id='streaming-content', data=''),
    # Interval for polling streaming updates
    dcc.Interval(id='streaming-interval', interval=100, disabled=True),
    # Header
    html.Div(style={
        'padding': '16px 0',
        'borderBottom': '1px solid #E5E5E5',
        'backgroundColor': '#FFFFFF',
        'position': 'sticky',
        'top': 0,
        'zIndex': 10,
        'boxShadow': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'textAlign': 'center',
    }, children=[
        html.H1("Medical AI Assistant", style={
            'margin': 0,
            'fontSize': '1.3em',
            'fontWeight': 600,
            'color': '#10A37F',
        }),
    ]),
    
    # Chat area
    html.Div(style={
        'flexGrow': 1,
        'overflowY': 'auto',
        'padding': 0,
        'display': 'flex',
        'flexDirection': 'column',
        'marginBottom': '140px',  # Space for input area
    }, children=[
        html.Div(id='chat-area', style={
            'display': 'flex',
            'flexDirection': 'column',
            'width': '100%',
        }, children=[
            # Welcome message with AI icon
            html.Div([
                html.Div("AI", style={
                    'width': '30px',
                    'height': '30px',
                    'borderRadius': '50%',
                    'backgroundColor': '#10A37F',
                    'marginRight': '15px',
                    'flexShrink': 0,
                    'display': 'flex',
                    'alignItems': 'center',
                    'justifyContent': 'center',
                    'color': 'white',
                    'fontWeight': 'bold',
                    'fontSize': '14px',
                }),
                html.Div("Hello! I'm your medical AI assistant. How can I help you today?", style={
                    'flexGrow': 1,
                }),
            ], style={
                'padding': '24px',
                'borderBottom': '1px solid #E5E5E5',
                'backgroundColor': '#FFFFFF',
                'position': 'relative',
                'lineHeight': 1.8,
                'display': 'flex',
                'alignItems': 'flex-start',
            }, className='assistant-message')
        ]),
    ]),

    # Input area
    html.Div(style={
        'display': 'flex',
        'flexDirection': 'column',
        'gap': '12px',
        'padding': '16px 24px',
        'backgroundColor': '#FFFFFF',
        'position': 'fixed',
        'bottom': 0,
        'left': 0,
        'right': 0,
        'zIndex': 100,
        'borderTop': '1px solid #E5E5E5',
        'maxWidth': '900px',
        'margin': '0 auto',
        'boxShadow': '0 -5px 20px rgba(0,0,0,0.1)',
    }, children=[
        # Dropdown row
        html.Div(style={
            'display': 'flex',
            'width': '100%',
            'gap': '16px',
            'marginBottom': '12px',
        }, children=[
            # Model dropdown
            html.Div(style={'flex': 1}, children=[
                html.Label("Model", style={"fontSize": "0.8em", "marginBottom": "4px", "display": "block"}),
                dcc.Dropdown(
                    id='model-dropdown',
                    options=[
                        {'label': 'Gemini 2.0 Flash', 'value': 'gemini/gemini-2.0-flash'},
                        {'label': 'Claude 3 Opus', 'value': 'claude-3-opus-20240229'},
                    ],
                    value='gemini/gemini-2.0-flash',
                    clearable=False,
                    style={
                        'borderRadius': '8px',
                        'border': '1px solid #E5E5E5',
                    }
                )
            ]),
            # Prompt dropdown
            html.Div(style={'flex': 1}, children=[
                html.Label("System Prompt", style={"fontSize": "0.8em", "marginBottom": "4px", "display": "block"}),
                dcc.Dropdown(
                    id='prompt-dropdown',
                    options=[
                        {'label': 'Differential Diagnosis', 'value': 'prompt1'},
                        {'label': 'Medical Information', 'value': 'prompt2'},
                    ],
                    value='prompt1',
                    clearable=False,
                    style={
                        'borderRadius': '8px',
                        'border': '1px solid #E5E5E5',
                    }
                )
            ]),
        ]),
        # Input and button row
        html.Div(style={
            'display': 'flex',
            'width': '100%',
            'gap': '12px',
            'alignItems': 'center',
        }, children=[
            # Text input
            html.Div(style={'flexGrow': 1}, children=[
                dcc.Input(
                    id='user-input', 
                    type='text', 
                    placeholder='Message the AI assistant...',
                    n_submit=0,  # Allow Enter key to submit
                    style={
                        'width': '100%',
                        'padding': '14px 16px',
                        'borderRadius': '8px',
                        'border': '1px solid #E5E5E5',
                        'boxSizing': 'border-box',
                        'boxShadow': '0 2px 6px rgba(0,0,0,0.05)',
                        'fontSize': '1em',
                    }
                ),
            ]),
            # Send button
            html.Button(
                'Send', 
                id='submit-button', 
                n_clicks=0,
                style={
                    'backgroundColor': '#10A37F',
                    'color': 'white',
                    'border': 'none',
                    'padding': '14px 28px',
                    'borderRadius': '8px',
                    'cursor': 'pointer',
                    'fontSize': '1em',
                    'fontWeight': 600,
                    'boxShadow': '0 2px 6px rgba(0,0,0,0.1)',
                    'whiteSpace': 'nowrap',
                    'minWidth': '100px',
                    'height': '48px',
                    'marginLeft': '10px',
                }
            ),
        ]),
    ]),
])

# Callback to start streaming process
@app.callback(
    [Output('streaming-response', 'data'),
     Output('streaming-interval', 'disabled'),
     Output('current-message-id', 'data'),
     Output('chat-area', 'children')],
    [Input('submit-button', 'n_clicks'),
     Input('user-input', 'n_submit')],  # Allow Enter key to submit
    [State('user-input', 'value'),
     State('model-dropdown', 'value'),
     State('prompt-dropdown', 'value'),
     State('chat-area', 'children'),
     State('current-message-id', 'data')] # Get current chat messages
)
def start_streaming(n_clicks, n_submit, user_message, model_name, prompt_name, current_messages, current_id):
    # Check if callback was triggered by a button click or Enter key
    triggered = callback_context.triggered[0]['prop_id']
    
    if (triggered == 'submit-button.n_clicks' or triggered == 'user-input.n_submit') and user_message:
        # Add user message to the chat
        user_msg_style = {
            'padding': '24px',
            'borderBottom': '1px solid #E5E5E5',
            'backgroundColor': '#F7F7F8',
            'position': 'relative',
            'lineHeight': 1.8,
            'display': 'flex',
            'alignItems': 'flex-start',
        }
        
        # User icon styling
        user_icon_style = {
            'width': '30px',
            'height': '30px',
            'borderRadius': '50%',
            'backgroundColor': '#5436DA',
            'marginRight': '15px',
            'flexShrink': 0,
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '14px',
        }
        
        user_content_style = {
            'flexGrow': 1,
        }
        
        new_messages = current_messages + [
            html.Div([
                html.Div("U", style=user_icon_style),
                html.Div(user_message, style=user_content_style),
            ], style=user_msg_style, className='user-message')
        ]

        # Select the prompt based on the dropdown
        system_prompt = ""
        if prompt_name == 'prompt1':
            system_prompt = prompt1
        elif prompt_name == 'prompt2':
            system_prompt = prompt2
        else:
            system_prompt = prompt1  # Default to prompt1 if something goes wrong

        # Add assistant message with empty content that will be filled by streaming
        assistant_msg_style = {
            'padding': '24px',
            'borderBottom': '1px solid #E5E5E5',
            'backgroundColor': '#FFFFFF',
            'position': 'relative',
            'lineHeight': 1.8,
            'display': 'flex',
            'alignItems': 'flex-start',
        }
        
        # Assistant icon styling
        assistant_icon_style = {
            'width': '30px',
            'height': '30px',
            'borderRadius': '50%',
            'backgroundColor': '#10A37F',
            'marginRight': '15px',
            'flexShrink': 0,
            'display': 'flex',
            'alignItems': 'center',
            'justifyContent': 'center',
            'color': 'white',
            'fontWeight': 'bold',
            'fontSize': '14px',
        }
        
        assistant_content_style = {
            'flexGrow': 1,
        }
        
        # Increment message ID for this new message
        new_id = current_id + 1
        
        # Create a unique ID for the streaming content div
        streaming_div_id = f'streaming-content-{new_id}'
        
        new_messages.append(
            html.Div([
                html.Div("AI", style=assistant_icon_style),
                html.Div(id=streaming_div_id, children="", style=assistant_content_style),
            ], style=assistant_msg_style, className='assistant-message')
        )

        # Create a data object with all the information needed for streaming
        stream_data = {
            'user_message': user_message,
            'model_name': model_name,
            'system_prompt': system_prompt,
            'message_id': new_id,
            'content': "",
            'status': 'starting',
            'div_id': streaming_div_id
        }
        
        # Return the data to start streaming, enable the interval, update message ID, and update chat area
        return json.dumps(stream_data), False, new_id, new_messages
    
    # If no new input, return current state
    return dash.no_update, True, current_id, current_messages

# Callback to handle streaming updates
@app.callback(
    [Output('streaming-response', 'data', allow_duplicate=True),
     Output('streaming-content', 'data')],
    [Input('streaming-interval', 'n_intervals')],
    [State('streaming-response', 'data'),
     State('current-message-id', 'data')],
    prevent_initial_call=True
)
def update_streaming(n_intervals, stream_data_json, current_id):
    if not stream_data_json:
        return [dash.no_update, dash.no_update]
    
    stream_data = json.loads(stream_data_json)
    
    # If streaming is complete, disable interval and return
    if stream_data['status'] == 'complete':
        return [dash.no_update, dash.no_update]
    
    # If streaming is just starting, initiate the API call
    if stream_data['status'] == 'starting':
        try:
            messages = [{"role": "system", "content": stream_data['system_prompt']},
                        {"role": "user", "content": stream_data['user_message']}]
            
            # Start streaming response
            stream_data['status'] = 'streaming'
            stream_data['content'] = ""  # Initialize empty content
            
            # Make a non-blocking call to get the first chunk
            response_chunk = completion(
                model=stream_data['model_name'],
                messages=messages,
                stream=True  # Enable streaming
            )
            
            # Get the first chunk
            for chunk in response_chunk:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    # Extract delta content from the chunk
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        stream_data['content'] += delta.content
                    break  # Just get the first chunk for now
            
            # Return updated stream data and content
            return [json.dumps(stream_data), json.dumps({
                'content': stream_data['content'],
                'div_id': stream_data['div_id']
            })]
            
        except Exception as e:
            # Handle errors
            stream_data['status'] = 'complete'
            stream_data['content'] = f"Error: {str(e)}"
            return [json.dumps(stream_data), json.dumps({
                'content': stream_data['content'],
                'div_id': stream_data['div_id']
            })]
    
    # If already streaming, continue getting more chunks
    elif stream_data['status'] == 'streaming':
        try:
            messages = [{"role": "system", "content": stream_data['system_prompt']},
                        {"role": "user", "content": stream_data['user_message']}]
            
            # Continue streaming where we left off
            response_chunk = completion(
                model=stream_data['model_name'],
                messages=messages,
                stream=True
            )
            
            # Skip chunks we've already processed
            current_content = stream_data['content']
            new_content = ""
            
            # Process new chunks
            for chunk in response_chunk:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    # Check if this is the end of the stream
                    if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                        stream_data['status'] = 'complete'
                        break
                    
                    # Extract delta content
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        new_content += delta.content
            
            # Update the content with new chunks
            stream_data['content'] = current_content + new_content
            
            # If we've reached the end, mark as complete
            if not new_content or stream_data['status'] == 'complete':
                stream_data['status'] = 'complete'
            
            # Return updated stream data and content
            return [json.dumps(stream_data), json.dumps({
                'content': stream_data['content'],
                'div_id': stream_data['div_id']
            })]
            
        except Exception as e:
            # Handle errors
            stream_data['status'] = 'complete'
            if not stream_data['content']:  # Only show error if we haven't received any content yet
                stream_data['content'] = f"Error: {str(e)}"
            return [json.dumps(stream_data), json.dumps({
                'content': stream_data['content'],
                'div_id': stream_data['div_id']
            })]
    
    return [dash.no_update, dash.no_update]

# Callback to clear input after submission
@app.callback(
    Output('user-input', 'value'),
    [Input('submit-button', 'n_clicks'),
     Input('user-input', 'n_submit')]
)
def clear_input(n_clicks, n_submit):
    triggered = dash.callback_context.triggered[0]['prop_id']
    if triggered == 'submit-button.n_clicks' or triggered == 'user-input.n_submit':
        return ''
    return dash.no_update

# Register clientside callback to update streaming content
app.clientside_callback(
    """
    function(streamingContent) {
        if (!streamingContent) return window.dash_clientside.no_update;
        
        try {
            const data = JSON.parse(streamingContent);
            const contentElement = document.getElementById(data.div_id);
            
            if (contentElement && data.content) {
                contentElement.textContent = data.content;
                
                // Scroll to the bottom of the chat area
                const chatArea = document.querySelector('.chat-area') || 
                                document.getElementById('chat-area').parentElement;
                if (chatArea) {
                    chatArea.scrollTop = chatArea.scrollHeight;
                }
            }
        } catch (error) {
            console.error('Error updating streaming content:', error);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('streaming-content', 'data', allow_duplicate=True),
    [Input('streaming-content', 'data')],
    prevent_initial_call=True
)

# Clientside callback to disable interval when streaming is complete
app.clientside_callback(
    """
    function(streamData) {
        if (!streamData) return window.dash_clientside.no_update;
        
        try {
            const data = JSON.parse(streamData);
            
            // If streaming is complete, disable the interval
            if (data.status === 'complete') {
                return true;
            }
        } catch (error) {
            console.error('Error checking streaming status:', error);
        }
        
        return window.dash_clientside.no_update;
    }
    """,
    Output('streaming-interval', 'disabled', allow_duplicate=True),
    [Input('streaming-response', 'data')],
    prevent_initial_call=True
)

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8054)  # Use a different port
