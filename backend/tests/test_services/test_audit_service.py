"""Tests for AuditService."""

import uuid
from unittest.mock import patch


def test_audit_log_no_data(app, test_contractor):
    """log() creates an audit entry with no old/new data."""
    from app.models.audit_log import AuditLog
    from app.services.audit_service import audit_service

    record_id = uuid.uuid4()
    with app.test_request_context("/"):
        with patch("app.services.audit_service.get_jwt_identity", return_value=None):
            audit_service.log(
                table_name="contractors",
                record_id=record_id,
                action="INSERT",
            )

    with app.app_context():
        log = AuditLog.query.filter_by(table_name="contractors", record_id=record_id).first()
        assert log is not None
        assert log.action == "INSERT"
        assert log.changed_fields == {}


def test_audit_log_with_changed_fields(app, test_contractor):
    """log() computes changed_fields diff from old_data and new_data."""
    from app.models.audit_log import AuditLog
    from app.services.audit_service import audit_service

    record_id = uuid.uuid4()
    old_data = {"first_name": "Old", "last_name": "Name"}
    new_data = {"first_name": "New", "last_name": "Name"}

    with app.test_request_context("/"):
        with patch("app.services.audit_service.get_jwt_identity", return_value=None):
            audit_service.log(
                table_name="contractors",
                record_id=record_id,
                action="UPDATE",
                old_data=old_data,
                new_data=new_data,
            )

    with app.app_context():
        log = AuditLog.query.filter_by(table_name="contractors", record_id=record_id).first()
        assert log is not None
        assert "first_name" in log.changed_fields
        assert log.changed_fields["first_name"]["old"] == "Old"
        assert log.changed_fields["first_name"]["new"] == "New"
        # last_name is unchanged so should NOT be in changed_fields
        assert "last_name" not in log.changed_fields
