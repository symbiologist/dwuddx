# Key Notes
-I am using VSCode and have created a venv in this project directory under .venv.
-I am using uv to manage my package dependencies. Please use uv to add dependencies when necessary (uv add).
-My API keys are stored via environment variables GEMINI_API_KEY and ANTHROPIC_API_KEY.
-Use gemini (Google AI Studio) and not vertex
-For this app, do not write unit tests

-Here is the directory structure:
root/
├── input/
├── output/
├── src/

* `input/`: Directory is used to store any input data, files, or external resources
* `output/`: Directory is where results, generated files, or output data will be stored.
* `src/`: Directory where all scripts should be saved

# Overarching Goals
The goal of this project is to create Dash and streamlit apps that host a simple LLM chatbot interface (using litellm)

## Step-wise plan
Create python scripts that do the following
 Web app that has a simple chat interface and imports one of multiple system prompts stored in prompts.py that is provided to the LLM. These are stored as string variables (i.e., prompt1, prompt2, etc)
 Use gemini-2.0-flash as the default model and include a dropdown menu for selecting models. 

app.py should be the above using dash
app2.py should be the above using streamlit