"""Tests for /api/tasks endpoints."""


def test_execute_task(client, contractor_headers, test_task):
    """POST /api/tasks/<id>/execute creates a task execution."""
    resp = client.post(
        f"/api/tasks/{test_task.task_id}/execute",
        headers=contractor_headers,
        json={"execution_status": "started"},
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert "execution_id" in data
    assert str(data["task_id"]) == str(test_task.task_id)
    assert str(data["job_id"]) == str(test_task.job_id)


def test_execute_task_not_found(client, contractor_headers):
    """POST /api/tasks/<nonexistent-id>/execute returns 404."""
    resp = client.post(
        "/api/tasks/00000000-0000-0000-0000-000000000000/execute",
        headers=contractor_headers,
        json={},
    )
    assert resp.status_code == 404


def test_execute_task_unauthenticated(client, test_task):
    """POST /api/tasks/<id>/execute without token returns 401."""
    resp = client.post(
        f"/api/tasks/{test_task.task_id}/execute",
        json={"execution_status": "started"},
    )
    assert resp.status_code == 401
