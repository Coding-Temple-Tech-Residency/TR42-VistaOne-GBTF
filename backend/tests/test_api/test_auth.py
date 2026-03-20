def test_login_missing_fields(client):
    """Test login with missing email or password."""
    resp = client.post("/api/auth/login", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_login_invalid_credentials(client, test_contractor):
    """Test login with wrong password."""
    resp = client.post(
        "/api/auth/login",
        json={"email": test_contractor.email, "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert "error" in data


def test_login_success(client, test_contractor, test_contractor_password):
    """Test successful login returns access and refresh tokens."""
    resp = client.post(
        "/api/auth/login",
        json={
            "email": test_contractor.email,
            "password": test_contractor_password,
        },
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token(client, refresh_headers):
    """Test refresh endpoint returns a new access token."""
    resp = client.post("/api/auth/refresh", headers=refresh_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "access_token" in data
