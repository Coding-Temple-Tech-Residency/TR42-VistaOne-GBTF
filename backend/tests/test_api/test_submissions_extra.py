import uuid


def test_create_submission_missing_job_id(client, contractor_headers):
    resp = client.post(
        "/api/submissions/",
        headers=contractor_headers,
        json={},
    )
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.get_json()
    assert "error" in data or "job_id" in str(data)


def test_create_submission_invalid_job_id(client, contractor_headers):
    resp = client.post(
        "/api/submissions/",
        headers=contractor_headers,
        json={"job_id": "not-a-uuid"},
    )
    assert resp.status_code == 400 or resp.status_code == 422
    data = resp.get_json()
    assert "error" in data or "job_id" in str(data)


def test_create_submission_nonexistent_job_id(client, contractor_headers):
    fake_job_id = str(uuid.uuid4())
    resp = client.post(
        "/api/submissions/",
        headers=contractor_headers,
        json={"job_id": fake_job_id},
    )
    # Should fail with 400 or 404 due to FK constraint or custom error
    assert resp.status_code in (400, 404, 500)


def test_create_submission_with_extra_fields(client, contractor_headers, test_job):
    from app.extensions import db
    from app.models.contractors import Contractor
    from app.models.job_completions import JobCompletion

    # Create a JobCompletion for the test job and contractor
    contractor = db.session.query(Contractor).first()
    completion = JobCompletion(job_id=test_job.job_id, contractor_id=contractor.contractor_id)
    db.session.add(completion)
    db.session.commit()
    payload = {
        "job_id": str(test_job.job_id),
        "completion_id": str(completion.completion_id),
        "submission_status": "complete",
        "data_complete": True,
        "total_photos_submitted": 5,
        "total_documents_submitted": 2,
        "total_signatures_submitted": 1,
        "total_tasks_completed": 3,
    }
    resp = client.post(
        "/api/submissions/",
        headers=contractor_headers,
        json=payload,
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["job_id"] == str(test_job.job_id)
    assert data["submission_status"] == "complete"
    assert data["data_complete"] is True
    assert data["total_photos_submitted"] == 5
    assert data["total_documents_submitted"] == 2
    assert data["total_signatures_submitted"] == 1
    assert data["total_tasks_completed"] == 3
