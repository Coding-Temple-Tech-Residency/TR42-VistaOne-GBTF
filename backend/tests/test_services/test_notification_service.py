"""Tests for notification_service.NotificationService."""

import uuid


def test_send_push_no_devices(app, test_contractor):
    """send_push is a no-op when the contractor has no registered devices."""
    from app.services.notification_service import notification_service

    with app.app_context():
        # Should not raise even when there are no devices
        notification_service.send_push(
            test_contractor.contractor_id,
            title="Test",
            body="Hello",
        )


def test_send_push_device_with_token(app, test_contractor):
    """send_push iterates devices that have a push_token (covers inner branch)."""
    from app.extensions import db
    from app.models.contractor_devices import ContractorDevice
    from app.services.notification_service import notification_service

    with app.app_context():
        device = ContractorDevice(
            contractor_id=test_contractor.contractor_id,
            device_id=f"dev-{uuid.uuid4().hex}",
            push_token="ExponentPushToken[xxxx]",
            is_active=True,
        )
        db.session.add(device)
        db.session.commit()

        # Should not raise — inner `pass` covers the real push logic
        notification_service.send_push(
            test_contractor.contractor_id,
            title="Title",
            body="Body",
            data={"key": "value"},
        )

        # Cleanup
        db.session.delete(device)
        db.session.commit()


def test_send_push_device_without_token(app, test_contractor):
    """send_push skips devices that have no push_token."""
    from app.extensions import db
    from app.models.contractor_devices import ContractorDevice
    from app.services.notification_service import notification_service

    with app.app_context():
        device = ContractorDevice(
            contractor_id=test_contractor.contractor_id,
            device_id=f"dev-{uuid.uuid4().hex}",
            push_token=None,  # no token
            is_active=True,
        )
        db.session.add(device)
        db.session.commit()

        # Should complete without error
        notification_service.send_push(
            test_contractor.contractor_id,
            title="Title",
            body="Body",
        )

        db.session.delete(device)
        db.session.commit()


def test_send_sms(app):
    """send_sms is callable (stub implementation)."""
    from app.services.notification_service import notification_service

    with app.app_context():
        # No-op stub — just confirm it doesn't raise
        notification_service.send_sms("+15550001234", "Test message")


def test_send_email(app):
    """send_email is callable (stub implementation)."""
    from app.services.notification_service import notification_service

    with app.app_context():
        notification_service.send_email("test@example.com", "Subject", "Body text")
