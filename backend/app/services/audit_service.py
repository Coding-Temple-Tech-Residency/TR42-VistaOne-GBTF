from flask import request
from flask_jwt_extended import get_jwt_identity

from app.extensions import db
from app.models import AuditLog
from app.utils.logger import get_logger

logger = get_logger("services.audit")


class AuditService:
    def log(self, table_name, record_id, action, old_data=None, new_data=None):
        """Create an audit log entry."""
        contractor_id = get_jwt_identity() or None
        ip_address = request.remote_addr if request else None
        session_id = None  # Could be extracted from JWT

        changed_fields = {}
        if old_data and new_data:
            for key in new_data:
                if old_data.get(key) != new_data.get(key):
                    changed_fields[key] = {
                        "old": old_data.get(key),
                        "new": new_data.get(key),
                    }

        log = AuditLog(
            table_name=table_name,
            record_id=record_id,
            action=action,
            contractor_id=contractor_id,
            ip_address=ip_address,
            session_id=session_id,
            old_data=old_data,
            new_data=new_data,
            changed_fields=changed_fields,
        )
        db.session.add(log)
        db.session.commit()


audit_service = AuditService()
