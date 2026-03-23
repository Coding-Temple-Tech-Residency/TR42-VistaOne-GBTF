"""Tests for /api/visits endpoints."""

from datetime import datetime, timezone


def test_create_visit(client, contractor_headers, test_job):
    """POST /api/visits/ creates a new site visit."""
    resp = client.post(
        "/api/visits/",
        headers=contractor_headers,
        json={
            "job_id": str(test_job.job_id),
            "check_in_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "visit_id" in data
    assert data["job_id"] == str(test_job.job_id)


def test_update_visit(client, contractor_headers, test_visit):
    """PUT /api/visits/<id> updates the visit."""
    resp = client.put(
        f"/api/visits/{test_visit.visit_id}",
        headers=contractor_headers,
        json={"visit_status": "completed"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["visit_id"] == str(test_visit.visit_id)


def test_update_visit_not_found(client, contractor_headers):
    """PUT /api/visits/<nonexistent-id> returns 404."""
    resp = client.put(
        "/api/visits/00000000-0000-0000-0000-000000000000",
        headers=contractor_headers,
        json={"visit_status": "completed"},
    )
    assert resp.status_code == 404


def test_checkout(client, contractor_headers, test_visit):
    """POST /api/visits/<id>/checkout records check-out."""
    resp = client.post(
        f"/api/visits/{test_visit.visit_id}/checkout",
        headers=contractor_headers,
        json={"check_out_time": datetime.now(timezone.utc).isoformat()},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["visit_id"] == str(test_visit.visit_id)


def test_checkout_not_found(client, contractor_headers):
    """POST /api/visits/<nonexistent-id>/checkout returns 404."""
    resp = client.post(
        "/api/visits/00000000-0000-0000-0000-000000000000/checkout",
        json={"check_out_time": datetime.now(timezone.utc).isoformat()},
        headers=contractor_headers,
    )
    assert resp.status_code == 404


def test_create_visit_unauthenticated(client, test_job):
    """POST /api/visits/ without token returns 401."""
    resp = client.post(
        "/api/visits/",
        json={
            "job_id": str(test_job.job_id),
            "check_in_time": datetime.now(timezone.utc).isoformat(),
        },
    )
    assert resp.status_code == 401


def test_update_visit_unauthenticated(client, test_visit):
    """PUT /api/visits/<id> without token returns 401."""
    resp = client.put(
        f"/api/visits/{test_visit.visit_id}",
        json={"visit_status": "completed"},
    )
    assert resp.status_code == 401
