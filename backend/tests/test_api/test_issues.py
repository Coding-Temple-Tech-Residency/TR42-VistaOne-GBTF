"""Tests for /api/issues endpoints."""


def test_create_issue(client, contractor_headers, test_job):
    """POST /api/issues/ creates an issue."""
    resp = client.post(
        "/api/issues/",
        headers=contractor_headers,
        json={
            "job_id": str(test_job.job_id),
            "issue_title": "Test Issue via API",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "issue_id" in data
    assert data["issue_title"] == "Test Issue via API"
    assert data["job_id"] == str(test_job.job_id)


def test_create_issue_unauthenticated(client, test_job):
    """POST /api/issues/ without token returns 401."""
    resp = client.post(
        "/api/issues/",
        json={"job_id": str(test_job.job_id), "issue_title": "Unauthorized"},
    )
    assert resp.status_code == 401
