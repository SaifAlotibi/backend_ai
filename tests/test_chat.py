from unittest.mock import patch


@patch("agent.chat_with_ollama")
def test_chat(mock_ollama, client):

    mock_ollama.return_value = {
        "message": {
            "content": "Fake AI response"
        }
    }

    # your existing register → login → conversation → /chat code