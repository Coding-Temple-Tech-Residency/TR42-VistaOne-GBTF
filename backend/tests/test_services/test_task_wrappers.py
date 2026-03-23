"""Tests for small service/task wrappers used only for coverage closure."""

from unittest.mock import patch

import pytest


def test_hash_password_returns_hash():
    from app.services.auth_service import hash_password

    hashed = hash_password("secret")
    assert hashed != "secret"
    assert isinstance(hashed, str)


def test_trigger_vendor_sync_task_success():
    from app.tasks.vendor_tasks import trigger_vendor_sync_task

    with patch("app.services.vendor_sync_service.process_vendor_sync_queue") as mock_process:
        trigger_vendor_sync_task.run("vendor-123")

    mock_process.assert_called_once_with()


def test_trigger_vendor_sync_task_retries_on_error():
    from app.tasks.vendor_tasks import trigger_vendor_sync_task

    with (
        patch(
            "app.services.vendor_sync_service.process_vendor_sync_queue",
            side_effect=Exception("boom"),
        ),
        patch.object(
            trigger_vendor_sync_task,
            "retry",
            side_effect=RuntimeError("retry-called"),
        ) as mock_retry,
    ):
        with pytest.raises(RuntimeError, match="retry-called"):
            trigger_vendor_sync_task.run("vendor-123")

    mock_retry.assert_called_once()
