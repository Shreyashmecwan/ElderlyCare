import json

def test_register_elderly_success(client):
    payload = {
        "email": "new.senior@example.com",
        "password": "Password123!",
        "full_name": "Henry Higgins",
        "role": "ELDERLY",
        "timezone": "America/New_York"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]
    assert data["data"]["user"]["role"] == "ELDERLY"
    assert data["data"]["user"]["has_profile"] is True

def test_register_duplicate_email_fails(client, elderly_user):
    payload = {
        "email": elderly_user["email"],
        "password": "Password123!",
        "full_name": "Another Person",
        "role": "FAMILY"
    }
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "EMAIL_EXISTS"

def test_login_success(client, elderly_user):
    payload = {
        "email": elderly_user["email"],
        "password": "TestPass123!"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert "access_token" in data["data"]

def test_login_invalid_password(client, elderly_user):
    payload = {
        "email": elderly_user["email"],
        "password": "WrongPassword!"
    }
    res = client.post("/api/auth/login", json=payload)
    assert res.status_code == 401
    data = res.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "INVALID_CREDENTIALS"

def test_get_me_authenticated(client, elderly_auth_headers, elderly_user):
    res = client.get("/api/auth/me", headers=elderly_auth_headers)
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert data["data"]["email"] == elderly_user["email"]

def test_get_me_unauthorized(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401
