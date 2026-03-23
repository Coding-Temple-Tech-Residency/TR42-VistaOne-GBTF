import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import text

from app.extensions import db
from app.models.enums import VendorSyncStatus
from app.models.mixins import TimestampMixin


class VendorSyncQueue(db.Model, TimestampMixin):
    __tablename__ = "vendor_sync_queue"

    # sync_id is no longer a primary key alone
    sync_id = db.Column(UUID(as_uuid=True), nullable=False, default=uuid.uuid4)
    # created_at from TimestampMixin is now part of the composite primary key
    vendor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("vendors.vendor_id", ondelete="CASCADE"),
        nullable=False,
    )
    direction = db.Column(db.String(10), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(UUID(as_uuid=True))
    vendor_entity_id = db.Column(db.String(255))
    payload = db.Column(JSONB, nullable=False)
    transformed_payload = db.Column(JSONB)
    sync_status = db.Column(
        db.Enum(VendorSyncStatus),
        default=VendorSyncStatus.pending,
    )
    attempts = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime(timezone=True))
    next_attempt_at = db.Column(db.DateTime(timezone=True))
    error_message = db.Column(db.Text)
    processed_at = db.Column(db.DateTime(timezone=True))

    vendor = db.relationship("Vendor", back_populates="sync_queue")

    __table_args__ = (
        # Composite primary key includes the partition column
        db.PrimaryKeyConstraint("sync_id", "created_at"),
        db.Index(
            "idx_vendor_sync_status",
            "vendor_id",
            "sync_status",
            "next_attempt_at",
        ),
        db.Index(
            "idx_vendor_sync_entity",
            "entity_type",
            "vendor_entity_id",
            postgresql_where=text("vendor_entity_id IS NOT NULL"),
        ),
        # Partitioning clause
        {"postgresql_partition_by": "RANGE (created_at)"},
    )

    def __repr__(self):
        return (
            f"<VendorSyncQueue {self.sync_id} - {self.created_at}"
            f" - {self.direction} - {self.entity_type}>"
        )
