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

    with db.session() as session:
        updated = session.get(Contractor, test_contractor.contractor_id)
        assert updated.first_name == new_name  # type: ignore
