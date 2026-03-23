"""Tests for /api/vendors endpoints."""

from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clear_vendor_cache(app):
    from app.extensions import cache

    with app.app_context():
        cache.clear()


def test_get_vendors_empty(client, contractor_headers):
    """GET /api/vendors/ with no vendors returns empty list."""
    resp = client.get("/api/vendors/", headers=contractor_headers)
    assert resp.status_code == 200
    assert isinstance(resp.get_json(), list)


def test_get_vendors(client, contractor_headers, test_vendor):
    """GET /api/vendors/ returns active vendors."""
    resp = client.get("/api/vendors/", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    ids = [v["vendor_id"] for v in data]
    assert str(test_vendor.vendor_id) in ids


def test_get_vendor_by_id(client, contractor_headers, test_vendor):
    """GET /api/vendors/<id> returns the vendor."""
    resp = client.get(f"/api/vendors/{test_vendor.vendor_id}", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["vendor_id"] == str(test_vendor.vendor_id)
    assert data["vendor_name"] == test_vendor.vendor_name


def test_get_vendor_not_found(client, contractor_headers):
    """GET /api/vendors/<nonexistent-id> returns 404."""
    resp = client.get(
        "/api/vendors/00000000-0000-0000-0000-000000000000",
        headers=contractor_headers,
    )
    assert resp.status_code == 404


def test_create_vendor(client, contractor_headers):
    """POST /api/vendors/ creates a new vendor."""
    import uuid

    resp = client.post(
        "/api/vendors/",
        headers=contractor_headers,
        json={
            "vendor_code": f"NEW-{uuid.uuid4().hex[:6].upper()}",
            "vendor_name": "New Vendor",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "vendor_id" in data
    assert data["vendor_name"] == "New Vendor"


def test_update_vendor(client, contractor_headers, test_vendor):
    """PUT /api/vendors/<id> updates the vendor."""
    resp = client.put(
        f"/api/vendors/{test_vendor.vendor_id}",
        headers=contractor_headers,
        json={"vendor_name": "Updated Vendor Name"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["vendor_name"] == "Updated Vendor Name"


def test_update_vendor_not_found(client, contractor_headers):
    """PUT /api/vendors/<nonexistent-id> returns 404."""
    resp = client.put(
        "/api/vendors/00000000-0000-0000-0000-000000000000",
        headers=contractor_headers,
        json={"vendor_name": "X"},
    )
    assert resp.status_code == 404


def test_delete_vendor(client, contractor_headers, test_vendor):
    """DELETE /api/vendors/<id> soft-deletes the vendor."""
    resp = client.delete(f"/api/vendors/{test_vendor.vendor_id}", headers=contractor_headers)
    assert resp.status_code == 204

    # Verify it is no longer in the active vendor list
    list_resp = client.get("/api/vendors/", headers=contractor_headers)
    ids = [v["vendor_id"] for v in list_resp.get_json()]
    assert str(test_vendor.vendor_id) not in ids


def test_delete_vendor_not_found(client, contractor_headers):
    """DELETE /api/vendors/<nonexistent-id> returns 404."""
    resp = client.delete(
        "/api/vendors/00000000-0000-0000-0000-000000000000",
        headers=contractor_headers,
    )
    assert resp.status_code == 404


def test_sync_vendor(client, contractor_headers, test_vendor):
    """POST /api/vendors/<id>/sync triggers async sync task."""
    with patch("app.api.vendors.trigger_vendor_sync_task") as mock_task:
        mock_task.delay.return_value = None
        resp = client.post(
            f"/api/vendors/{test_vendor.vendor_id}/sync",
            headers=contractor_headers,
        )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["message"] == "Sync started"
    mock_task.delay.assert_called_once_with(str(test_vendor.vendor_id))


def test_sync_vendor_not_found(client, contractor_headers):
    """POST /api/vendors/<nonexistent-id>/sync returns 404."""
    resp = client.post(
        "/api/vendors/00000000-0000-0000-0000-000000000000/sync",
        headers=contractor_headers,
    )
    assert resp.status_code == 404


def test_get_vendors_unauthenticated(client):
    """GET /api/vendors/ without token returns 401."""
    resp = client.get("/api/vendors/")
    assert resp.status_code == 401


def test_create_vendor_unauthenticated(client):
    """POST /api/vendors/ without token returns 401."""
    resp = client.post("/api/vendors/", json={"vendor_code": "X", "vendor_name": "Y"})
    assert resp.status_code == 401
