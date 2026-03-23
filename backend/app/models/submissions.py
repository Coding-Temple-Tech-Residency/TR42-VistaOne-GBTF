import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin
from app.models.types import PercentValue


class Submission(db.Model, TimestampMixin):
    __tablename__ = "submissions"

    submission_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    completion_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("job_completions.completion_id", ondelete="SET NULL"),
    )

    submission_number = db.Column(db.String(50), unique=True)
    submitted_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    submitted_by_id = db.Column(UUID(as_uuid=True), db.ForeignKey("contractors.contractor_id"))
    submitted_by_biometric = db.Column(db.Boolean, default=False)
    submitted_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    submitted_location = db.Column(Geography(geometry_type="POINT", srid=4326))

    submission_status = db.Column(db.String(50), default="draft")
    status_updated_at = db.Column(db.DateTime(timezone=True))

    data_complete = db.Column(db.Boolean, default=False)
    data_completeness_percentage = db.Column(PercentValue)
    missing_required_fields = db.Column(JSONB)

    total_photos_submitted = db.Column(db.Integer, default=0)
    total_documents_submitted = db.Column(db.Integer, default=0)
    total_signatures_submitted = db.Column(db.Integer, default=0)
    total_tasks_completed = db.Column(db.Integer, default=0)
    total_issues_reported = db.Column(db.Integer, default=0)

    submission_package_url = db.Column(db.Text)
    submission_package_hash = db.Column(db.String(255))

    version_number = db.Column(db.Integer, default=1)
    previous_submission_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("submissions.submission_id")
    )

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))
    vendor_submission_id = db.Column(db.String(255))
    vendor_confirmation_data = db.Column(JSONB)

    # Relationships
    job = db.relationship("Job", back_populates="submissions")
    contractor = db.relationship(
        "Contractor",
        foreign_keys=[contractor_id],
        back_populates="submissions",
    )
    completion = db.relationship("JobCompletion", back_populates="submissions")
    submitted_by = db.relationship(
        "Contractor",
        foreign_keys=[submitted_by_id],
        back_populates="submissions_submitted",
    )
    submitted_biometric = db.relationship(
        "BiometricVerification",
        foreign_keys=[submitted_biometric_id],
    )
    previous_submission = db.relationship("Submission", remote_side=[submission_id])

    __table_args__ = (
        db.Index("idx_submissions_job", job_id, submission_status),
        db.Index(
            "idx_submissions_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_submissions_contractor", contractor_id),
        db.Index("idx_submissions_completion", completion_id),
        db.Index("idx_submissions_submitted_by", submitted_by_id),
        db.Index("idx_submissions_biometric", submitted_biometric_id),
        db.Index("idx_submissions_previous", previous_submission_id),
        db.CheckConstraint(
            "submission_status IN ('draft', 'partial', "
            "'complete', 'pending_vendor', "
            "'confirmed_by_vendor', 'rejected')",
            name="valid_submission_status",
        ),
        db.CheckConstraint(
            "version_number >= 1",
            name="version_positive",
        ),
        db.CheckConstraint(
            "total_photos_submitted >= 0",
            name="photos_positive",
        ),
        db.CheckConstraint(
            "total_documents_submitted >= 0",
            name="documents_positive",
        ),
        db.CheckConstraint("total_signatures_submitted >= 0", name="signatures_positive"),
        db.CheckConstraint("total_tasks_completed >= 0", name="tasks_completed_positive"),
        db.CheckConstraint(
            "total_issues_reported >= 0",
            name="issues_positive",
        ),
    )

    def __repr__(self):
        return f"<Submission {self.submission_number}>"
