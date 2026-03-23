"""Tests for /api/submissions endpoints."""


def test_create_submission(client, contractor_headers, test_job):
    """POST /api/submissions/ creates a submission."""
    resp = client.post(
        "/api/submissions/",
        headers=contractor_headers,
        json={"job_id": str(test_job.job_id)},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "submission_id" in data
    assert data["job_id"] == str(test_job.job_id)


def test_create_submission_unauthenticated(client, test_job):
    """POST /api/submissions/ without token returns 401."""
    resp = client.post(
        "/api/submissions/",
        json={"job_id": str(test_job.job_id)},
    )
    assert resp.status_code == 401
