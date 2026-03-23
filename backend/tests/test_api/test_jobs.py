def test_get_jobs(client, contractor_headers, test_job_with_assignment):
    """Test GET /api/jobs/ returns jobs assigned to contractor."""
    resp = client.get("/api/jobs/", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) >= 1
    job = data[0]
    assert job["job_number"] == test_job_with_assignment.job_number


def test_get_job_by_id(client, contractor_headers, test_job_with_assignment):
    """Test GET /api/jobs/<id> returns the specific job."""
    job_id = test_job_with_assignment.job_id
    resp = client.get(f"/api/jobs/{job_id}", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["job_id"] == str(job_id)


def test_get_job_assignments(client, contractor_headers, test_job_with_assignment):
    """Test GET /api/jobs/<id>/assignments returns assignments."""
    job_id = test_job_with_assignment.job_id
    resp = client.get(f"/api/jobs/{job_id}/assignments", headers=contractor_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_jobs_unauthenticated(client):
    """Test GET /api/jobs/ without token returns 401."""
    resp = client.get("/api/jobs/")
    assert resp.status_code == 401


def test_get_job_by_id_unauthenticated(client, test_job_with_assignment):
    """Test GET /api/jobs/<id> without token returns 401."""
    job_id = test_job_with_assignment.job_id
    resp = client.get(f"/api/jobs/{job_id}")
    assert resp.status_code == 401
