from unittest.mock import AsyncMock, patch


def test_chat(client):
    with (
        patch(
            "services.chat_service.run_agent",
            new_callable=AsyncMock,
        ) as mock_run_agent,
        patch(
            "services.chat_service.maybe_summarize_conversation",
            new_callable=AsyncMock,
        ),
    ):
        mock_run_agent.return_value = "Fake AI response"

        # Register a user
        client.post(
            "/auth/register",
            json={
                "name": "Chat User",
                "email": "chat@example.com",
                "password": "password123",
            },
        )

        # Log in
        login = client.post(
            "/auth/login",
            json={
                "email": "chat@example.com",
                "password": "password123",
            },
        )

        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Create a conversation
        conversation = client.post(
            "/conversations",
            headers=headers,
            json={"title": "Test Chat"},
        )

        assert conversation.status_code == 200
        conversation_id = conversation.json()["id"]

        # Send a chat message
        response = client.post(
            "/chat",
            headers=headers,
            json={
                "conversation_id": conversation_id,
                "message": "Hello!",
            },
        )

        assert response.status_code == 200, response.text
        assert response.json()["answer"] == "Fake AI response"
        mock_run_agent.assert_awaited_once()