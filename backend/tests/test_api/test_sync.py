def test_sync_endpoint(client, contractor_headers):
    """Test POST /api/sync/ with empty changes returns server changes."""
    payload = {"lastPulledAt": None, "changes": {}}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "changes" in data
    assert "timestamp" in data
    assert "conflicts" in data
