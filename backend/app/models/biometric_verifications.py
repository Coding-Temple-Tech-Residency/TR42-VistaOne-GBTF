import uuid

from geoalchemy2 import Geography
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.enums import VerificationType


class BiometricVerification(db.Model):
    __tablename__ = "biometric_verifications"

    biometric_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id = db.Column(UUID(as_uuid=True), db.ForeignKey("jobs.job_id", ondelete="SET NULL"))
    verification_type = db.Column(db.Enum(VerificationType), nullable=False)
    verification_status = db.Column(db.String(20), default="success")
    biometric_type = db.Column(db.String(50))
    biometric_timestamp = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )
    biometric_confidence_score = db.Column(db.Integer)
    biometric_device_id = db.Column(db.String(255))
    biometric_method_used = db.Column(db.String(100))
    biometric_failed_attempts = db.Column(db.Integer, default=0)
    biometric_error_message = db.Column(db.Text)
    biometric_image_hash = db.Column(db.String(255))
    biometric_template_match = db.Column(db.Boolean)
    multi_factor_completed = db.Column(db.Boolean, default=False)
    multi_factor_methods = db.Column(JSONB)
    liveness_detection_passed = db.Column(db.Boolean, default=False)
    liveness_score = db.Column(db.Integer)
    location = db.Column(Geography(geometry_type="POINT", srid=4326))
    ip_address = db.Column(db.String(45))  # INET type could be used
    verification_duration_ms = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())

    # Relationships
    contractor = db.relationship("Contractor", back_populates="biometric_verifications")
    job = db.relationship("Job", back_populates="biometric_verifications")
    # Reverse relations for various foreign keys
    check_in_site_visits = db.relationship(
        "SiteVisit",
        foreign_keys="SiteVisit.check_in_biometric_id",
        back_populates="check_in_biometric",
    )
    check_out_site_visits = db.relationship(
        "SiteVisit",
        foreign_keys="SiteVisit.check_out_biometric_id",
        back_populates="check_out_biometric",
    )
    task_executions = db.relationship("TaskExecution", back_populates="completion_biometric")
    job_completions = db.relationship("JobCompletion", back_populates="completion_biometric")
    issues_reported = db.relationship(
        "Issue",
        foreign_keys="Issue.issue_reported_biometric_id",
        back_populates="reported_biometric",
    )
    photos_uploaded = db.relationship(
        "Photo",
        foreign_keys="Photo.uploaded_by_biometric_id",
        back_populates="uploaded_biometric",
    )

    __table_args__ = (
        db.Index(
            "idx_biometric_contractor",
            contractor_id,
            biometric_timestamp,
        ),
        db.Index(
            "idx_biometric_job",
            job_id,
            biometric_timestamp,
        ),
        db.CheckConstraint(
            "verification_status IN " "('success', 'failed', 'timeout', 'canceled')",
            name="valid_verification_status",
        ),
        db.CheckConstraint(
            "biometric_type IN ('fingerprint', " "'face_id', 'voice', 'iris', 'multi_factor')",
            name="valid_biometric_type",
        ),
        db.CheckConstraint(
            "biometric_confidence_score BETWEEN 0 AND 100",
            name="confidence_range",
        ),
        db.CheckConstraint(
            "liveness_score BETWEEN 0 AND 100",
            name="liveness_range",
        ),
    )

    def __repr__(self):
        return f"<BiometricVerification {self.biometric_id}>"
