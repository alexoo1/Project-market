def _register_payload(**overrides):
    payload = {
        "first_name": "Alex",
        "display_name": "alex_lions",
        "phone": "+2250700000099",
        "email": "alex.test@example.com",
        "password": "SuperSecret123",
        "city": "Abidjan",
        "district": "Cocody",
    }
    payload.update(overrides)
    return payload


def test_register_returns_tokens(client):
    response = client.post("/api/v1/auth/register", json=_register_payload())
    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


def test_register_duplicate_phone_fails(client):
    client.post("/api/v1/auth/register", json=_register_payload())
    response = client.post(
        "/api/v1/auth/register", json=_register_payload(email="other@example.com")
    )
    assert response.status_code == 409


def test_login_with_correct_credentials(client):
    client.post("/api/v1/auth/register", json=_register_payload())
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "+2250700000099", "password": "SuperSecret123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_with_wrong_password_fails(client):
    client.post("/api/v1/auth/register", json=_register_payload())
    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "+2250700000099", "password": "wrongpass"},
    )
    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


def test_me_returns_current_user(client):
    register_response = client.post("/api/v1/auth/register", json=_register_payload())
    access_token = register_response.json()["access_token"]
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["phone"] == "+2250700000099"


def test_refresh_token_issues_new_pair(client):
    register_response = client.post("/api/v1/auth/register", json=_register_payload())
    refresh_token = register_response.json()["refresh_token"]
    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_forgot_password_never_reveals_account_existence(client):
    client.post("/api/v1/auth/register", json=_register_payload())
    response_existing = client.post(
        "/api/v1/auth/forgot-password", json={"identifier": "+2250700000099"}
    )
    response_missing = client.post(
        "/api/v1/auth/forgot-password", json={"identifier": "+2250799999999"}
    )
    assert response_existing.status_code == 202
    assert response_missing.status_code == 202
    assert response_existing.json() == response_missing.json()
