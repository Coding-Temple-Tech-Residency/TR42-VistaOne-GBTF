def test_sync_endpoint(client, contractor_headers):
    """Test POST /api/sync/ with empty changes returns server changes."""
    payload = {"lastPulledAt": None, "changes": {}}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "changes" in data
    assert "timestamp" in data
    assert "conflicts" in data

    def test_sync_with_last_pulled_at(client, contractor_headers):
        """Test sync with a lastPulledAt timestamp (non-None path)."""
        payload = {"lastPulledAt": 1000, "changes": {}}
        resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "changes" in data

    def test_sync_with_push_created(client, contractor_headers, test_job):
        """Test sync that pushes a created site visit."""
        import uuid
        from datetime import datetime, timezone

        payload = {
            "lastPulledAt": None,
            "changes": {
                "site_visits": {
                    "created": [
                        {
                            "visit_id": str(uuid.uuid4()),
                            "job_id": str(test_job.job_id),
                            "check_in_time": datetime.now(timezone.utc).isoformat(),
                        }
                    ],
                    "updated": [],
                    "deleted": [],
                }
            },
        }
        resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
        assert resp.status_code == 200

    def test_sync_with_push_updated_and_deleted(client, contractor_headers, test_job, test_visit):
        """Test sync pushes an update and deletion of existing visits."""
        from datetime import datetime, timezone

        payload = {
            "lastPulledAt": None,
            "changes": {
                "site_visits": {
                    "created": [],
                    "updated": [
                        {
                            "visit_id": str(test_visit.visit_id),
                            "job_id": str(test_job.job_id),
                            "check_in_time": datetime.now(timezone.utc).isoformat(),
                        }
                    ],
                    "deleted": [],
                }
            },
        }
        resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
        assert resp.status_code == 200

    def test_sync_unauthenticated(client):
        """Test POST /api/sync/ without token returns 401."""
        resp = client.post("/api/sync/", json={"lastPulledAt": None, "changes": {}})
        assert resp.status_code == 401


def test_sync_missing_changes(client, contractor_headers):
    """Test POST /api/sync/ with missing 'changes' field returns 200 (default empty dict)."""
    payload = {"lastPulledAt": None}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    assert resp.status_code == 200


def test_sync_missing_last_pulled_at(client, contractor_headers):
    """Test POST /api/sync/ with missing 'lastPulledAt' field returns 200 (default 0)."""
    payload = {"changes": {}}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    assert resp.status_code == 200


def test_sync_changes_not_dict(client, contractor_headers):
    """Test POST /api/sync/ with 'changes' not a dict returns 500 (unhandled)."""
    payload = {"lastPulledAt": None, "changes": "notadict"}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    # Should raise 500 because push_changes expects dict
    assert resp.status_code == 500


def test_sync_malformed_json(client, contractor_headers):
    """Test POST /api/sync/ with malformed JSON returns 400."""
    resp = client.post(
        "/api/sync/", headers=contractor_headers, data="{notjson}", content_type="application/json"
    )
    assert resp.status_code == 400


def test_sync_internal_error(monkeypatch, client, contractor_headers):
    """Test POST /api/sync/ when push_changes raises exception returns 500."""

    def raise_error(*args, **kwargs):
        raise Exception("Simulated error")

    import app.api.sync as sync_api

    monkeypatch.setattr(sync_api, "push_changes", raise_error)
    payload = {"lastPulledAt": None, "changes": {}}
    resp = client.post("/api/sync/", headers=contractor_headers, json=payload)
    assert resp.status_code == 500
