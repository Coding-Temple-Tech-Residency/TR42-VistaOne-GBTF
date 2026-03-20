import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin


class NotificationPreference(db.Model, TimestampMixin):
    __tablename__ = "notification_preferences"

    preference_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    push_notifications = db.Column(db.Boolean, default=True)
    job_alerts = db.Column(db.Boolean, default=True)
    job_alerts_radius_miles = db.Column(db.Integer)
    job_alerts_types = db.Column(JSONB)
    payment_notifications = db.Column(db.Boolean, default=True)
    schedule_notifications = db.Column(db.Boolean, default=True)
    issue_notifications = db.Column(db.Boolean, default=True)
    marketing_notifications = db.Column(db.Boolean, default=False)
    notification_schedule = db.Column(JSONB)
    quiet_hours_start = db.Column(db.Time)
    quiet_hours_end = db.Column(db.Time)
    quiet_hours_timezone = db.Column(db.String(50))

    # Relationships
    contractor = db.relationship(
        "Contractor",
        back_populates="notification_preference",
    )

    __table_args__ = (
        db.CheckConstraint(
            "job_alerts_radius_miles >= 0",
            name="radius_positive",
        ),
    )

    def __repr__(self):
        return f"<NotificationPreference for contractor {self.contractor_id}>"
