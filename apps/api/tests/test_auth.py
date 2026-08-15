from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "email": "patrick@example.com",
    "display_name": "Patrick",
    "password": "correct-horse-battery-staple",
}


async def _register(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201


async def test_register_creates_user(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert "hashed_password" not in body


async def test_register_duplicate_email_conflicts(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 409


async def test_login_returns_access_token_and_sets_refresh_cookie(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.cookies


async def test_login_wrong_password_rejected(client: AsyncClient) -> None:
    await _register(client)
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


async def test_me_requires_valid_access_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


async def test_me_returns_current_user_with_valid_token(client: AsyncClient) -> None:
    await _register(client)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_refresh_rotates_token_and_old_one_is_rejected(client: AsyncClient) -> None:
    await _register(client)
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    old_refresh_cookie = login_response.cookies["refresh_token"]

    client.cookies.set("refresh_token", old_refresh_cookie)
    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()

    # Replaying the now-rotated-out old refresh token must be rejected.
    client.cookies.set("refresh_token", old_refresh_cookie)
    replay_response = await client.post("/api/v1/auth/refresh")
    assert replay_response.status_code == 401
