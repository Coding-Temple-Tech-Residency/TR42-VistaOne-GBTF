import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models.enums import DeviceType
from app.models.mixins import TimestampMixin


class ContractorDevice(db.Model, TimestampMixin):
    __tablename__ = "contractor_devices"

    device_registration_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    device_id = db.Column(db.String(255), nullable=False)
    device_name = db.Column(db.String(255))
    device_type = db.Column(db.Enum(DeviceType))
    device_model = db.Column(db.String(100))
    os_version = db.Column(db.String(50))
    app_version = db.Column(db.String(50))
    first_registered_at = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )
    last_used_at = db.Column(db.DateTime(timezone=True))
    biometric_enabled_on_device = db.Column(db.Boolean, default=False)
    biometric_type = db.Column(db.String(50))  # checked in SQL
    push_token = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    contractor = db.relationship("Contractor", back_populates="devices")

    __table_args__ = (
        db.UniqueConstraint("contractor_id", "device_id", name="unique_contractor_device"),
        db.Index("idx_devices_contractor", contractor_id, is_active),
        db.Index(
            "idx_devices_last_used",
            last_used_at,
            postgresql_where=(is_active.is_(True)),
        ),
        db.CheckConstraint(
            "biometric_type IN ('fingerprint', 'face_id', 'voice', 'none')",
            name="valid_biometric_type",
        ),
    )

    def __repr__(self):
        return f"<ContractorDevice {self.device_name}>"
