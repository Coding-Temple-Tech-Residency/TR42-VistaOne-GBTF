import uuid

from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin
from app.models.types import PercentValue


class JobCompletion(db.Model, TimestampMixin):
    __tablename__ = "job_completions"

    completion_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )

    job_completed = db.Column(db.Boolean, default=False)
    job_completed_at = db.Column(db.DateTime(timezone=True))
    job_completed_biometric = db.Column(db.Boolean, default=False)
    job_completed_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    job_completed_location = db.Column(Geography(geometry_type="POINT", srid=4326))

    job_completed_photos = db.Column(JSONB)
    job_completed_documents = db.Column(JSONB)
    job_completed_notes = db.Column(db.Text)

    final_completion_percentage = db.Column(PercentValue)
    punch_list_items = db.Column(JSONB)
    punch_list_completed = db.Column(db.Boolean, default=False)
    punch_list_completed_at = db.Column(db.DateTime(timezone=True))

    total_job_duration_hours = db.Column(db.Numeric(8, 2))
    total_labor_hours = db.Column(db.Numeric(8, 2))
    total_overtime_hours = db.Column(db.Numeric(8, 2))

    vendor_confirmed = db.Column(db.Boolean, default=False)
    vendor_confirmed_at = db.Column(db.DateTime(timezone=True))
    vendor_confirmation_data = db.Column(JSONB)

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))
    vendor_completion_id = db.Column(db.String(255))

    # Relationships
    job = db.relationship("Job", back_populates="job_completion")
    contractor = db.relationship("Contractor", back_populates="job_completions")
    completion_biometric = db.relationship(
        "BiometricVerification",
        foreign_keys=[job_completed_biometric_id],
    )
    submissions = db.relationship("Submission", back_populates="completion")

    __table_args__ = (
        db.Index("idx_completions_job", job_id),
        db.Index(
            "idx_completions_sync",
            synced_to_vendor,
            postgresql_where=(synced_to_vendor.is_(False)),
        ),
        db.Index("idx_completions_contractor", contractor_id),
        db.Index("idx_completions_biometric", job_completed_biometric_id),
        db.CheckConstraint(
            "total_job_duration_hours >= 0",
            name="duration_positive",
        ),
        db.CheckConstraint(
            "total_labor_hours >= 0",
            name="labor_hours_positive",
        ),
        db.CheckConstraint(
            "total_overtime_hours >= 0",
            name="overtime_positive",
        ),
    )

    def __repr__(self):
        return f"<JobCompletion for job {self.job_id}>"
