import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin


class SiteVisit(db.Model, TimestampMixin):
    __tablename__ = "site_visits"

    visit_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
    )
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    visit_number = db.Column(db.Integer)

    visit_status = db.Column(db.String(50), default="in_progress")
    visit_type = db.Column(db.String(50), default="regular")

    # Check-in
    check_in_time = db.Column(db.DateTime(timezone=True), nullable=False)
    check_in_location = db.Column(Geography(geometry_type="POINT", srid=4326))
    check_in_accuracy_meters = db.Column(db.Numeric(10, 2))
    check_in_altitude_meters = db.Column(db.Numeric(10, 2))
    check_in_photo_url = db.Column(db.Text)
    check_in_biometric_verified = db.Column(db.Boolean, default=False)
    check_in_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    check_in_notes = db.Column(db.Text)
    on_site_contact_person = db.Column(db.String(255))
    site_conditions_on_arrival = db.Column(db.Text)
    equipment_brought = db.Column(JSONB)

    # Check-out
    check_out_time = db.Column(db.DateTime(timezone=True))
    check_out_location = db.Column(Geography(geometry_type="POINT", srid=4326))
    check_out_accuracy_meters = db.Column(db.Numeric(10, 2))
    check_out_altitude_meters = db.Column(db.Numeric(10, 2))
    check_out_photo_url = db.Column(db.Text)
    check_out_biometric_verified = db.Column(db.Boolean, default=False)
    check_out_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    check_out_notes = db.Column(db.Text)
    site_conditions_on_departure = db.Column(db.Text)
    equipment_used = db.Column(JSONB)
    equipment_returned = db.Column(JSONB)

    # Calculations
    total_hours_on_site = db.Column(db.Numeric(5, 2))
    total_break_minutes = db.Column(db.Integer, default=0)
    productive_hours = db.Column(db.Numeric(5, 2))
    travel_time_minutes = db.Column(db.Integer)
    travel_distance_miles = db.Column(db.Numeric(8, 2))

    # Metadata
    device_id = db.Column(db.String(255))
    device_model = db.Column(db.String(100))
    app_version = db.Column(db.String(50))
    offline_mode = db.Column(db.Boolean, default=False)
    data_synced_at = db.Column(db.DateTime(timezone=True))

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    job = db.relationship("Job", back_populates="site_visits")
    contractor = db.relationship("Contractor", back_populates="site_visits")
    check_in_biometric = db.relationship(
        "BiometricVerification",
        foreign_keys=[check_in_biometric_id],
    )
    check_out_biometric = db.relationship(
        "BiometricVerification",
        foreign_keys=[check_out_biometric_id],
    )
    progress_updates = db.relationship("ProgressUpdate", back_populates="visit")
    task_executions = db.relationship("TaskExecution", back_populates="visit")
    issues = db.relationship("Issue", back_populates="visit")
    photos = db.relationship("Photo", back_populates="visit")
    sessions = db.relationship("ContractorSession", back_populates="visit")

    __table_args__ = (
        db.Index("idx_visits_job", job_id, check_in_time),
        db.Index("idx_visits_contractor", contractor_id, check_in_time),
        db.Index(
            "idx_visits_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_visits_checkin_bio", check_in_biometric_id),
        db.Index("idx_visits_checkout_bio", check_out_biometric_id),
        db.CheckConstraint(
            "visit_status IN ('scheduled', " "'in_progress', 'completed', 'cancelled')",
            name="valid_visit_status",
        ),
        db.CheckConstraint(
            "visit_type IN ('regular', 'emergency', " "'inspection', 'delivery_only')",
            name="valid_visit_type",
        ),
        db.CheckConstraint(
            "check_in_accuracy_meters >= 0",
            name="check_in_accuracy_positive",
        ),
        db.CheckConstraint(
            "check_out_accuracy_meters >= 0",
            name="check_out_accuracy_positive",
        ),
        db.CheckConstraint(
            "total_break_minutes >= 0",
            name="break_minutes_positive",
        ),
        db.CheckConstraint(
            "productive_hours >= 0",
            name="productive_hours_positive",
        ),
        db.CheckConstraint(
            "travel_time_minutes >= 0",
            name="travel_time_positive",
        ),
        db.CheckConstraint(
            "travel_distance_miles >= 0",
            name="travel_distance_positive",
        ),
        db.CheckConstraint(
            "check_out_time IS NULL OR check_out_time >= check_in_time",
            name="valid_check_times",
        ),
    )

    def __repr__(self):
        return f"<SiteVisit {self.visit_id}>"
