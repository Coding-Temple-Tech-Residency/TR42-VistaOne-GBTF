def test_get_me(client, contractor_headers, test_contractor):
    """Test GET /api/contractors/me returns the authenticated contractor."""
    resp = client.get("/api/contractors/me", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["email"] == test_contractor.email
    assert data["first_name"] == test_contractor.first_name


def test_update_me(client, contractor_headers, test_contractor):
    """Test PUT /api/contractors/me updates contractor fields."""
    new_name = "Updated"
    resp = client.put(
        "/api/contractors/me",
        headers=contractor_headers,
        json={"first_name": new_name},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["first_name"] == new_name
    # Verify in DB (use a fresh session)
    from app.extensions import db
    from app.models.contractors import Contractor

    db.session.expire_all()
    updated = db.session.get(Contractor, test_contractor.contractor_id)
    assert updated.first_name == new_name  # type: ignore


def test_update_me_nonexistent_field(client, contractor_headers):
    resp = client.put(
        "/api/contractors/me",
        headers=contractor_headers,
        json={"not_a_field": "value"},
    )
    # Should ignore or not error
    assert resp.status_code == 200


def test_get_me_unauthenticated(client):
    """Test GET /api/contractors/me without auth returns 401."""
    resp = client.get("/api/contractors/me")
    assert resp.status_code == 401


def test_update_me_unauthenticated(client):
    """Test PUT /api/contractors/me without auth returns 401."""
    resp = client.put("/api/contractors/me", json={"first_name": "X"})
    assert resp.status_code == 401
