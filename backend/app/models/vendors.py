import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.enums import VendorSyncStatus
from app.models.mixins import TimestampMixin


class Vendor(db.Model, TimestampMixin):
    __tablename__ = "vendors"

    vendor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_code = db.Column(db.String(50), nullable=False, unique=True)
    vendor_name = db.Column(db.String(255), nullable=False)
    vendor_api_config = db.Column(JSONB)
    webhook_url = db.Column(db.Text)
    sync_frequency_minutes = db.Column(db.Integer, default=60)
    last_sync_at = db.Column(db.DateTime(timezone=True))
    last_sync_status = db.Column(
        db.Enum(VendorSyncStatus), default=VendorSyncStatus.pending
    )
    sync_error_message = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    sync_queue = db.relationship(
        "VendorSyncQueue",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )
    jobs = db.relationship(
        "Job",
        back_populates="vendor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        db.Index(
            "idx_vendors_code",
            vendor_code,
            postgresql_where=(is_active.is_(True)),
        ),
        db.Index(
            "idx_vendors_sync",
            last_sync_status,
            last_sync_at,
            postgresql_where=(is_active.is_(True)),
        ),
    )

    def __repr__(self):
        return f"<Vendor {self.vendor_code}>"
