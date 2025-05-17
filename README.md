# Medical AI Assistant

A Dash-based web application that provides a chat interface for interacting with medical AI models. The application uses LiteLLM to connect to various LLM providers and offers a modern, responsive UI similar to ChatGPT.

## Features

- **Modern Chat Interface**: Clean, responsive design with user and AI messages clearly distinguished
- **Streaming Responses**: Real-time streaming of AI responses for a more interactive experience
- **Multiple Model Support**: Switch between different AI models (currently supports Gemini and Claude)
- **Customizable System Prompts**: Choose between different system prompts for specialized medical assistance
- **Responsive Design**: Works well on both desktop and mobile devices

## Getting Started

### Prerequisites

- Python 3.8+
- API keys for supported models (Gemini, Claude)
- Docker (optional, for containerized deployment)

### Installation

#### Local Development

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies using UV:
   ```
   uv pip install -r requirements.txt
   ```

### Environment Setup

Create a `.env` file in the project root with your API keys:

```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### Running the Application

#### Local Development

Start the application with:

```
python src/app.py  # For Dash version
python src/app2.py  # For Streamlit version
python src/app3.py  # For FastAPI version
```

The applications will be available at:
- Dash: http://localhost:8054
- Streamlit: http://localhost:8501
- FastAPI: http://localhost:8000

#### Using Docker

1. Build and run the Docker container:
   ```
   docker-compose up --build
   ```

2. The application will be available at http://localhost:8000

### Deployment on Render

This application can be easily deployed on Render using the included `render.yaml` configuration:

1. Push your code to a Git repository (GitHub, GitLab, etc.)
2. Create a new Web Service on Render and connect your repository
3. Select "Use render.yaml from repository"
4. Add your API keys as environment variables in the Render dashboard
5. Deploy the service

The application will be available at your Render URL (e.g., https://medical-ai-assistant.onrender.com)

## Usage

1. Type your medical question in the input field
2. Select your preferred model from the dropdown
3. Choose an appropriate system prompt based on your needs:
   - **Differential Diagnosis**: For generating potential diagnoses based on symptoms
   - **Medical Information**: For general medical information and research
4. Press Enter or click the Send button
5. View the AI's response as it streams in real-time

## Project Structure

- `src/app.py`: Main application file with Dash layout and callbacks
- `prompts.py`: Contains system prompts for different medical scenarios
- `assets/`: Contains CSS and JavaScript files for styling and client-side functionality
  - `style.css`: Main stylesheet for the application
  - `streaming.js`: Client-side JavaScript for handling streaming responses

## Technical Details

### Streaming Implementation

The application implements streaming responses using:

1. Server-side streaming with LiteLLM's streaming capability
2. Client-side updates using Dash's clientside callbacks
3. Interval-based polling to update the UI with new content chunks

This approach provides a smooth, interactive experience while maintaining compatibility with various LLM providers.

## License

[MIT License](LICENSE)
