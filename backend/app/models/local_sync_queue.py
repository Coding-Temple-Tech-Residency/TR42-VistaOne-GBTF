import uuid

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.enums import SyncStatus
from app.models.mixins import TimestampMixin


class LocalSyncQueue(db.Model, TimestampMixin):
    __tablename__ = "local_sync_queue"

    sync_item_id = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    device_id = db.Column(db.String(255))
    session_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractor_sessions.session_id", ondelete="SET NULL"),
    )

    table_name = db.Column(db.String(100), nullable=False)
    record_id = db.Column(UUID(as_uuid=True), nullable=False)
    operation = db.Column(db.String(10), nullable=False)
    data = db.Column(JSONB)

    sync_status = db.Column(db.Enum(SyncStatus), default=SyncStatus.pending)
    sync_attempts = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime(timezone=True))
    next_attempt_at = db.Column(db.DateTime(timezone=True))
    error_message = db.Column(db.Text)

    priority = db.Column(db.Integer, default=0)

    # Relationships
    contractor = db.relationship("Contractor", back_populates="sync_queue")
    session = db.relationship("ContractorSession", back_populates="sync_queue")

    __table_args__ = (
        db.Index(
            "idx_local_sync_status",
            "sync_status",
            "next_attempt_at",
            "priority",
            postgresql_where=text("sync_status = 'pending'"),
        ),
        db.Index(
            "idx_local_sync_contractor",
            "contractor_id",
            "sync_status",
            "created_at",
        ),
        db.Index("idx_local_sync_session", "session_id"),
        db.CheckConstraint(
            "operation IN ('INSERT', 'UPDATE', 'DELETE')",
            name="valid_operation",
        ),
        db.CheckConstraint(
            "sync_attempts >= 0",
            name="attempts_positive",
        ),
        db.CheckConstraint("priority >= 0", name="priority_positive"),
        db.PrimaryKeyConstraint("sync_item_id", "created_at"),
        {"postgresql_partition_by": "RANGE (created_at)"},
    )

    def __repr__(self):
        return f"<LocalSyncQueue {self.sync_item_id}>"
