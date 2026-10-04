def test_register(client):

    response = client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_login(client):

    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "login@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_invalid_login(client):

    client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": "invalid@example.com",
            "password": "password123"
        }
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "invalid@example.com",
            "password": "wrongpassword"
        }
    )

    assert response.status_code == 401


def test_me(client):

    client.post(
        "/auth/register",
        json={
            "name": "Me User",
            "email": "me@example.com",
            "password": "password123"
        }
    )

    login = client.post(
        "/auth/login",
        json={
            "email": "me@example.com",
            "password": "password123"
        }
    )

    token = login.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


def test_me_without_token(client):

    response = client.get("/auth/me")

    assert response.status_code == 401