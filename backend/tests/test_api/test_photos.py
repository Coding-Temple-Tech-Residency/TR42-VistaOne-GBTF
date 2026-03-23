"""Tests for /api/photos endpoints."""


def test_upload_photo(client, contractor_headers, test_job):
    """POST /api/photos/ creates a photo record."""
    resp = client.post(
        "/api/photos/",
        headers=contractor_headers,
        json={
            "job_id": str(test_job.job_id),
            "photo_url": "https://example.com/photo.jpg",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "photo_id" in data
    assert data["photo_url"] == "https://example.com/photo.jpg"
    assert data["job_id"] == str(test_job.job_id)


def test_upload_photo_unauthenticated(client, test_job):
    """POST /api/photos/ without token returns 401."""
    resp = client.post(
        "/api/photos/",
        json={
            "job_id": str(test_job.job_id),
            "photo_url": "https://example.com/photo.jpg",
        },
    )
    assert resp.status_code == 401
