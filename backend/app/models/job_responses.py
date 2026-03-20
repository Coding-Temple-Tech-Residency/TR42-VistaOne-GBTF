import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models.mixins import TimestampMixin


class JobResponse(db.Model, TimestampMixin):
    __tablename__ = "job_responses"

    response_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    response_type = db.Column(db.String(20), nullable=False)
    job_accepted = db.Column(db.Boolean, default=False)
    job_accepted_at = db.Column(db.DateTime(timezone=True))
    job_accepted_biometric_verified = db.Column(db.Boolean, default=False)
    job_accepted_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    job_accepted_location = db.Column(Geography(geometry_type="POINT", srid=4326))
    estimated_arrival_time = db.Column(db.DateTime(timezone=True))

    job_declined = db.Column(db.Boolean, default=False)
    job_declined_reason = db.Column(db.Text)
    job_declined_category = db.Column(db.String(50))
    job_declined_at = db.Column(db.DateTime(timezone=True))

    counter_offer_amount = db.Column(db.Numeric(10, 2))
    counter_offer_schedule = db.Column(db.DateTime(timezone=True))
    counter_offer_notes = db.Column(db.Text)

    contractor_notes = db.Column(db.Text)

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    job = db.relationship("Job", back_populates="job_responses")
    contractor = db.relationship("Contractor", back_populates="job_responses")
    accepted_biometric = db.relationship(
        "BiometricVerification", foreign_keys=[job_accepted_biometric_id]
    )

    __table_args__ = (
        db.UniqueConstraint(
            "job_id", "contractor_id", name="unique_job_contractor_response"
        ),
        db.Index("idx_responses_job", job_id, response_type),
        db.Index("idx_responses_contractor", contractor_id),
        db.Index(
            "idx_responses_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_responses_biometric", job_accepted_biometric_id),
        db.CheckConstraint(
            "response_type IN ('accept', 'decline', 'counter', 'pending')",
            name="valid_response_type",
        ),
        db.CheckConstraint(
            "job_declined_category IN "
            "('schedule', 'distance', 'skills', "
            "'equipment', 'other')",
            name="valid_decline_category",
        ),
        db.CheckConstraint(
            "counter_offer_amount >= 0",
            name="counter_offer_positive",
        ),
    )

    def __repr__(self):
        return f"<JobResponse {self.response_id}>"
