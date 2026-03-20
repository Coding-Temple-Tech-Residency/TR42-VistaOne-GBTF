import uuid

from sqlalchemy.dialects.postgresql import INET, JSONB, UUID

from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_log"

    audit_id = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(UUID(as_uuid=True), nullable=False)
    action = db.Column(db.String(10), nullable=False)

    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="SET NULL"),
    )
    session_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractor_sessions.session_id", ondelete="SET NULL"),
    )
    ip_address = db.Column(INET)

    old_data = db.Column(JSONB)
    new_data = db.Column(JSONB)
    changed_fields = db.Column(JSONB)

    changed_at = db.Column(
        db.DateTime(timezone=True),
        default=db.func.current_timestamp(),
    )

    __table_args__ = (
        db.PrimaryKeyConstraint("audit_id", "changed_at"),
        db.Index(
            "idx_audit_record",
            table_name,
            record_id,
            changed_at,
        ),
        db.Index(
            "idx_audit_contractor",
            contractor_id,
            changed_at,
        ),
        db.Index("idx_audit_session", session_id),
        db.CheckConstraint(
            "action IN ('INSERT', 'UPDATE', 'DELETE')",
            name="valid_action",
        ),
        {"postgresql_partition_by": "RANGE (changed_at)"},
    )

    def __repr__(self):
        return f"<AuditLog {self.audit_id}>"
