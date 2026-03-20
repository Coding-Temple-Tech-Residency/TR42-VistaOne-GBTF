import uuid

from sqlalchemy import FetchedValue, text
from sqlalchemy.dialects.postgresql import INET, UUID

from app.extensions import db
from app.models.enums import DeviceType
from app.models.mixins import TimestampMixin


class ContractorSession(db.Model, TimestampMixin):
    __tablename__ = "contractor_sessions"

    session_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.job_id", ondelete="SET NULL"),
    )
    visit_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("site_visits.visit_id", ondelete="SET NULL"),
    )

    session_token = db.Column(db.String(255), unique=True)
    session_type = db.Column(db.String(50))

    device_id = db.Column(db.String(255))
    device_name = db.Column(db.String(255))
    device_type = db.Column(db.Enum(DeviceType))
    device_model = db.Column(db.String(100))
    app_version = db.Column(db.String(50))
    os_version = db.Column(db.String(50))
    ip_address = db.Column(INET)

    battery_level_at_start = db.Column(db.Integer)
    network_type = db.Column(db.String(20))
    offline_mode_active = db.Column(db.Boolean, default=False)

    data_synced = db.Column(db.Boolean, default=False)
    last_sync_at = db.Column(db.DateTime(timezone=True))
    pending_sync_items = db.Column(db.Integer, default=0)

    started_at = db.Column(
        db.DateTime(timezone=True),
        default=db.func.current_timestamp(),
    )
    ended_at = db.Column(db.DateTime(timezone=True))
    session_duration_minutes = db.Column(db.Integer, server_default=FetchedValue())

    # Relationships
    contractor = db.relationship("Contractor", back_populates="sessions")
    job = db.relationship("Job", back_populates="contractor_sessions")
    visit = db.relationship("SiteVisit", back_populates="sessions")
    sync_queue = db.relationship("LocalSyncQueue", back_populates="session")

    __table_args__ = (
        db.Index("idx_sessions_contractor", "contractor_id", "started_at"),
        db.Index(
            "idx_sessions_token",
            "session_token",
            postgresql_where=text("ended_at IS NULL"),
        ),
        db.Index("idx_sessions_job", "job_id"),
        db.Index("idx_sessions_visit", "visit_id"),
        db.CheckConstraint(
            "session_type IN ('mobile', 'web', 'api')",
            name="valid_session_type",
        ),
        db.CheckConstraint(
            "battery_level_at_start BETWEEN 0 AND 100",
            name="battery_range",
        ),
        db.CheckConstraint(
            "network_type IN " "('wifi', '4G', '5G', '3G', 'offline', 'unknown')",
            name="valid_network_type",
        ),
        db.CheckConstraint(
            "pending_sync_items >= 0",
            name="pending_sync_positive",
        ),
    )

    def __repr__(self):
        return f"<ContractorSession {self.session_id}>"
