def test_create_and_list_conversation(client):

    client.post(
        "/auth/register",
        json={
            "name": "Conversation User",
            "email": "conversation@example.com",
            "password": "password123"
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "conversation@example.com",
            "password": "password123"
        }
    )

    token = login.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    create = client.post(
        "/conversations",
        headers=headers,
        json={
            "title": "My Conversation"
        }
    )

    assert create.status_code == 200

    response = client.get(
        "/conversations",
        headers=headers
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "My Conversation"