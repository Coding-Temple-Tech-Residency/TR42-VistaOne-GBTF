import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID

from app.extensions import db
from app.models.enums import JobStatus, PriorityLevel, VendorSyncStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin
from app.models.types import Email, PhoneNumber


class Job(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "jobs"

    job_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_number = db.Column(db.String(100), nullable=False)
    vendor_job_id = db.Column(db.String(255))
    vendor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("vendors.vendor_id"),
    )

    # Job details
    job_name = db.Column(db.String(255))
    job_description = db.Column(db.Text)
    job_location = db.Column(db.Text)
    job_location_geography = db.Column(Geography(geometry_type="POINT", srid=4326))
    site_address_street = db.Column(db.String(255))
    site_address_city = db.Column(db.String(100))
    site_address_state = db.Column(db.String(50))
    site_address_zip = db.Column(db.String(20))
    site_contact_name = db.Column(db.String(255))
    site_contact_phone = db.Column(PhoneNumber)
    site_contact_email = db.Column(Email)

    # Scheduling
    scheduled_start_date = db.Column(db.DateTime(timezone=True))
    scheduled_end_date = db.Column(db.DateTime(timezone=True))
    actual_start_date = db.Column(db.DateTime(timezone=True))
    actual_end_date = db.Column(db.DateTime(timezone=True))
    estimated_hours = db.Column(db.Numeric(5, 2))

    # Details
    job_type = db.Column(db.String(100))
    job_category = db.Column(db.String(100))
    priority = db.Column(db.Enum(PriorityLevel), default=PriorityLevel.medium)
    status = db.Column(db.Enum(JobStatus), default=JobStatus.scheduled)

    # Vendor info (denormalized)
    vendor_name = db.Column(db.String(255))
    vendor_contact_name = db.Column(db.String(255))
    vendor_contact_phone = db.Column(PhoneNumber)
    vendor_contact_email = db.Column(Email)
    vendor_instructions = db.Column(db.Text)

    # Documentation
    po_number = db.Column(db.String(100))
    quote_number = db.Column(db.String(100))
    contract_number = db.Column(db.String(100))
    documents_attached = db.Column(JSONB)
    materials_needed = db.Column(db.Text)
    special_requirements = db.Column(db.Text)
    safety_requirements = db.Column(db.Text)

    # Sync tracking
    last_synced_with_vendor_at = db.Column(db.DateTime(timezone=True))
    vendor_sync_status = db.Column(
        db.Enum(VendorSyncStatus), default=VendorSyncStatus.pending
    )
    vendor_data = db.Column(JSONB)

    # Search vector (managed by DB)
    from sqlalchemy import FetchedValue

    search_vector = db.Column(TSVECTOR, server_default=FetchedValue())

    # Relationships
    vendor = db.relationship("Vendor", back_populates="jobs")
    assignments = db.relationship(
        "JobAssignment", back_populates="job", cascade="all, delete-orphan"
    )
    biometric_verifications = db.relationship(
        "BiometricVerification",
        back_populates="job",
    )
    job_responses = db.relationship(
        "JobResponse", back_populates="job", cascade="all, delete-orphan"
    )
    site_visits = db.relationship(
        "SiteVisit", back_populates="job", cascade="all, delete-orphan"
    )
    progress_updates = db.relationship(
        "ProgressUpdate", back_populates="job", cascade="all, delete-orphan"
    )
    tasks = db.relationship(
        "Task",
        back_populates="job",
        cascade="all, delete-orphan",
    )
    task_executions = db.relationship(
        "TaskExecution", back_populates="job", cascade="all, delete-orphan"
    )
    issues = db.relationship(
        "Issue", back_populates="job", cascade="all, delete-orphan"
    )
    photos = db.relationship(
        "Photo", back_populates="job", cascade="all, delete-orphan"
    )
    job_completion = db.relationship(
        "JobCompletion",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )
    submissions = db.relationship(
        "Submission", back_populates="job", cascade="all, delete-orphan"
    )
    contractor_sessions = db.relationship("ContractorSession", back_populates="job")

    __table_args__ = (
        db.Index(
            "unique_vendor_job",
            "vendor_id",
            "vendor_job_id",
            unique=True,
            postgresql_where=text("vendor_job_id IS NOT NULL"),
        ),
        db.Index(
            "idx_jobs_number",
            "job_number",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        db.Index(
            "idx_jobs_status",
            "status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        db.Index(
            "idx_jobs_dates",
            "scheduled_start_date",
            "scheduled_end_date",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        db.Index(
            "idx_jobs_vendor",
            "vendor_id",
            "vendor_sync_status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        db.Index(
            "idx_jobs_location",
            "job_location_geography",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        db.Index("idx_jobs_search", "search_vector", postgresql_using="gin"),
        db.Index(
            "idx_jobs_vendor_lookup",
            "vendor_id",
            "vendor_job_id",
            postgresql_where=text("vendor_job_id IS NOT NULL"),
        ),
        db.CheckConstraint(
            "estimated_hours > 0",
            name="estimated_hours_positive",
        ),
        db.CheckConstraint(
            "scheduled_start_date <= scheduled_end_date",
            name="valid_scheduled_dates",
        ),
        db.CheckConstraint(
            "(actual_start_date IS NULL OR "
            "actual_end_date IS NULL OR "
            "actual_start_date <= actual_end_date)",
            name="valid_actual_dates",
        ),
    )

    def __repr__(self):
        return f"<Job {self.job_number}>"
