"""Tests for vendor_sync_service.process_vendor_sync_queue."""

import uuid
from unittest.mock import MagicMock, patch


def test_process_queue_empty(app):
    """No-op when queue is empty."""
    from app.services.vendor_sync_service import process_vendor_sync_queue

    with app.app_context():
        with patch("app.services.vendor_sync_service.VendorSyncQueue") as MockQueue:
            MockQueue.query.filter_by.return_value.order_by.return_value.all.return_value = []
            # Should complete without error
            process_vendor_sync_queue()


def test_process_queue_success(app):
    """Successful HTTP 200 response sets sync_status to 'synced'."""
    from app.extensions import db
    from app.services.vendor_sync_service import process_vendor_sync_queue

    vendor_id = uuid.uuid4()
    mock_item = MagicMock()
    mock_item.vendor_id = vendor_id
    mock_item.entity_type = "job"
    mock_item.payload = {"job_id": "123"}
    mock_item.sync_status = "pending"
    mock_item.attempts = 0

    with app.app_context():
        # Create a real vendor so Vendor.query.get returns something
        from app.models.vendors import Vendor

        vendor = Vendor(
            vendor_id=vendor_id,
            vendor_code=f"V-{uuid.uuid4().hex[:8].upper()}",
            vendor_name="Test Vendor",
            vendor_api_config={
                "endpoint": "http://vendor.example.com",
                "apiKey": "key",
            },
        )
        db.session.add(vendor)
        db.session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with (
            patch("app.services.vendor_sync_service.VendorSyncQueue") as MockQueue,
            patch(
                "app.services.vendor_sync_service.requests.post",
                return_value=mock_response,
            ),
        ):
            MockQueue.query.filter_by.return_value.order_by.return_value.all.return_value = [
                mock_item
            ]

            with patch("app.services.vendor_sync_service.db.session.commit"):
                process_vendor_sync_queue()

        assert mock_item.sync_status == "synced"

        # Cleanup
        db.session.delete(vendor)
        db.session.commit()


def test_process_queue_http_failure(app):
    """Non-200 HTTP response sets sync_status to 'failed'."""
    from app.extensions import db
    from app.services.vendor_sync_service import process_vendor_sync_queue

    vendor_id = uuid.uuid4()
    mock_item = MagicMock()
    mock_item.vendor_id = vendor_id
    mock_item.entity_type = "job"
    mock_item.payload = {}
    mock_item.sync_status = "pending"
    mock_item.attempts = 0

    with app.app_context():
        from app.models.vendors import Vendor

        vendor = Vendor(
            vendor_id=vendor_id,
            vendor_code=f"V-{uuid.uuid4().hex[:8].upper()}",
            vendor_name="Fail Vendor",
            vendor_api_config={
                "endpoint": "http://vendor.example.com",
                "apiKey": "key",
            },
        )
        db.session.add(vendor)
        db.session.commit()

        mock_response = MagicMock()
        mock_response.status_code = 500

        with (
            patch("app.services.vendor_sync_service.VendorSyncQueue") as MockQueue,
            patch(
                "app.services.vendor_sync_service.requests.post",
                return_value=mock_response,
            ),
            patch("app.services.vendor_sync_service.db.session.commit"),
        ):
            MockQueue.query.filter_by.return_value.order_by.return_value.all.return_value = [
                mock_item
            ]
            process_vendor_sync_queue()

        assert mock_item.sync_status == "failed"
        assert "500" in mock_item.error_message

        db.session.delete(vendor)
        db.session.commit()


def test_process_queue_exception(app):
    """Exception during requests.post sets sync_status to 'failed'."""
    import uuid as _uuid

    from app.extensions import db
    from app.services.vendor_sync_service import process_vendor_sync_queue

    vendor_id = _uuid.uuid4()
    mock_item = MagicMock()
    mock_item.vendor_id = vendor_id
    mock_item.entity_type = "job"
    mock_item.payload = {}
    mock_item.sync_status = "pending"
    mock_item.attempts = 0

    with app.app_context():
        from app.models.vendors import Vendor

        vendor = Vendor(
            vendor_id=vendor_id,
            vendor_code=f"V-{_uuid.uuid4().hex[:8].upper()}",
            vendor_name="Exc Vendor",
            vendor_api_config={
                "endpoint": "http://vendor.example.com",
                "apiKey": "key",
            },
        )
        db.session.add(vendor)
        db.session.commit()

        with (
            patch("app.services.vendor_sync_service.VendorSyncQueue") as MockQueue,
            patch(
                "app.services.vendor_sync_service.requests.post",
                side_effect=ConnectionError("network down"),
            ),
            patch("app.services.vendor_sync_service.db.session.commit"),
        ):
            MockQueue.query.filter_by.return_value.order_by.return_value.all.return_value = [
                mock_item
            ]
            process_vendor_sync_queue()

        assert mock_item.sync_status == "failed"
        assert mock_item.error_message == "Sync request failed"

        db.session.delete(vendor)
        db.session.commit()


def test_process_queue_vendor_not_found(app):
    """Item with unknown vendor_id is skipped (logs warning, no crash)."""
    from app.services.vendor_sync_service import process_vendor_sync_queue

    mock_item = MagicMock()
    mock_item.vendor_id = uuid.uuid4()  # Does not exist in DB
    mock_item.entity_type = "job"
    mock_item.payload = {}
    mock_item.sync_status = "pending"
    mock_item.attempts = 0

    with app.app_context():
        with patch("app.services.vendor_sync_service.VendorSyncQueue") as MockQueue:
            MockQueue.query.filter_by.return_value.order_by.return_value.all.return_value = [
                mock_item
            ]
            # Should not raise
            process_vendor_sync_queue()

        # sync_status must be unchanged (item was skipped via `continue`)
        assert mock_item.sync_status == "pending"
