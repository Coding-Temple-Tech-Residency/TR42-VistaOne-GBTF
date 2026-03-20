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
