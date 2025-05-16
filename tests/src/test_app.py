import pytest
from unittest.mock import patch
from src.app import update_output

# Mock the litellm.completion function
@patch('src.app.completion')
def test_update_output_with_input(mock_completion):
    # Configure the mock to return a predefined response
    mock_completion.return_value = type('obj', (object,), {'choices': [{'message': type('obj', (object,), {'content': 'Mocked LLM response'})}]})()

    n_clicks = 1
    user_input = "Hello, bot!"
    selected_model = "gemini/gemini-2.0-flash"
    chat_history = []

    updated_chat_history = update_output(n_clicks, user_input, selected_model, chat_history)

    # Assert that the chat history is updated correctly
    assert len(updated_chat_history) == 2
    assert updated_chat_history[0].children == "You: Hello, bot!"
    assert updated_chat_history[1].children == "Bot: Mocked LLM response"
    mock_completion.assert_called_once_with(
        model=selected_model,
        messages=[{"content": "''' \nYou are an expert medical AI diagnostician assisting a human physician in generating a broad differential diagnosis. \nPlease provide a succinct differential diagnosis based on the the patient summary provided. \nProvide three categories of diagnoses: \"Most likely\", \"Can't Miss\", and \"Broader Differential.\" \nInclude at least 3 diagnoses in each category. \nInclude a short table comparing and contrasting the items in the differential, including a column for next treatment step of each condition.\nInclude a section with additional diagnostic steps that would be most helpful for distinguishing between the items on the differential. \nFinally, summarize the single most helpful next diagnostic step, whether it be a lab test or additional information to obtain from the patient.\n\n'''", "role": "system"}, {"content": user_input, "role": "user"}]
    )

@patch('src.app.completion')
def test_update_output_no_input(mock_completion):
    n_clicks = 1
    user_input = ""
    selected_model = "gemini/gemini-2.0-flash"
    chat_history = []

    updated_chat_history = update_output(n_clicks, user_input, selected_model, chat_history)

    # Assert that the chat history is not updated and litellm.completion is not called
    assert len(updated_chat_history) == 0
    mock_completion.assert_not_called()

@patch('src.app.completion')
def test_update_output_no_clicks(mock_completion):
    n_clicks = 0
    user_input = "Hello, bot!"
    selected_model = "gemini/gemini-2.0-flash"
    chat_history = []

    updated_chat_history = update_output(n_clicks, user_input, selected_model, chat_history)

    # Assert that the chat history is not updated and litellm.completion is not called
    assert len(updated_chat_history) == 0
    mock_completion.assert_not_called()

@patch('src.app.completion')
def test_update_output_with_existing_history(mock_completion):
    mock_completion.return_value = type('obj', (object,), {'choices': [{'message': type('obj', (object,), {'content': 'Another mocked response'})}]})()

    n_clicks = 1
    user_input = "How are you?"
    selected_model = "gemini/gemini-2.0-flash"
    chat_history = [html.Div("You: Hi"), html.Div("Bot: Hello")]

    updated_chat_history = update_output(n_clicks, user_input, selected_model, chat_history)

    # Assert that the new messages are appended to the existing history
    assert len(updated_chat_history) == 4
    assert updated_chat_history[2].children == "You: How are you?"
    assert updated_chat_history[3].children == "Bot: Another mocked response"
    mock_completion.assert_called_once()

@patch('src.app.completion')
def test_update_output_error_handling(mock_completion):
    mock_completion.side_effect = Exception("API Error")

    n_clicks = 1
    user_input = "Test error"
    selected_model = "gemini/gemini-2.0-flash"
    chat_history = []

    updated_chat_history = update_output(n_clicks, user_input, selected_model, chat_history)

    # Assert that an error message is added to the chat history
    assert len(updated_chat_history) == 2
    assert updated_chat_history[0].children == "You: Test error"
    assert "Error: API Error" in updated_chat_history[1].children
    mock_completion.assert_called_once()
