import uuid

from sqlalchemy import Index, func, text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID

from app.extensions import db
from app.models.enums import AccountStatus
from app.models.mixins import SoftDeleteMixin, TimestampMixin
from app.models.types import Email, PercentValue, PhoneNumber, RatingValue, SSNLastFour


class Contractor(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "contractors"

    contractor_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(64), nullable=False, unique=True)
    email = db.Column(Email, nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_initial = db.Column(db.String(1))
    date_of_birth = db.Column(db.Date)
    ssn_last_four = db.Column(SSNLastFour)
    personal_phone = db.Column(PhoneNumber)
    alternate_phone = db.Column(PhoneNumber)
    address_street = db.Column(db.String(255))
    address_city = db.Column(db.String(100))
    address_state = db.Column(db.String(50))
    address_zip = db.Column(db.String(20))
    address_country = db.Column(db.String(100), default="USA")
    profile_photo_url = db.Column(db.Text)
    company_name = db.Column(db.String(255))
    employee_id = db.Column(db.String(64))

    # Professional info
    years_experience = db.Column(db.Integer)
    previous_projects_count = db.Column(db.Integer, default=0)
    average_rating = db.Column(RatingValue)
    total_reviews = db.Column(db.Integer, default=0)

    # Background & safety
    background_check_passed = db.Column(db.Boolean, default=False)
    background_check_date = db.Column(db.Date)
    background_check_provider = db.Column(db.String(255))
    background_check_document_url = db.Column(db.Text)
    drug_test_passed = db.Column(db.Boolean, default=False)
    drug_test_date = db.Column(db.Date)
    drug_test_document_url = db.Column(db.Text)
    safety_record_score = db.Column(PercentValue)

    # Account status
    account_status = db.Column(db.Enum(AccountStatus), default=AccountStatus.active)
    account_verified = db.Column(db.Boolean, default=False)
    account_verified_at = db.Column(db.DateTime, server_default=func.now())
    last_login_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # Preferences
    language_preference = db.Column(db.String(50), default="en")
    work_hours_preference = db.Column(JSONB)
    preferred_job_types = db.Column(JSONB)
    max_travel_distance_miles = db.Column(db.Integer)

    # Search vector (managed by DB, we don't need to set it)
    from sqlalchemy import FetchedValue

    search_vector = db.Column(TSVECTOR, server_default=FetchedValue())

    # Relationships
    credentials = db.relationship(
        "ContractorCredential",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    insurance_policies = db.relationship(
        "ContractorInsurance",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    devices = db.relationship(
        "ContractorDevice",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    notification_preference = db.relationship(
        "NotificationPreference",
        uselist=False,
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    job_assignments = db.relationship(
        "JobAssignment",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    biometric_verifications = db.relationship(
        "BiometricVerification",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    job_responses = db.relationship(
        "JobResponse",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    site_visits = db.relationship(
        "SiteVisit", back_populates="contractor", cascade="all, delete-orphan"
    )
    progress_updates = db.relationship(
        "ProgressUpdate",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    task_executions = db.relationship(
        "TaskExecution",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    issues = db.relationship(
        "Issue",
        foreign_keys="Issue.contractor_id",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    assigned_issues = db.relationship(
        "Issue",
        foreign_keys="Issue.assigned_contractor_id",
        back_populates="assignee",
    )
    issues_reported = db.relationship(
        "Issue",
        foreign_keys="Issue.issue_reported_by_id",
        back_populates="reported_by",
        cascade="all, delete-orphan",
    )
    photos = db.relationship(
        "Photo",
        foreign_keys="Photo.contractor_id",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    photos_uploaded = db.relationship(
        "Photo",
        foreign_keys="Photo.uploaded_by_id",
        back_populates="uploaded_by",
    )
    job_completions = db.relationship(
        "JobCompletion",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    submissions = db.relationship(
        "Submission",
        foreign_keys="Submission.contractor_id",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    submissions_submitted = db.relationship(
        "Submission",
        foreign_keys="Submission.submitted_by_id",
        back_populates="submitted_by",
        cascade="all, delete-orphan",
    )
    sessions = db.relationship(
        "ContractorSession",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )
    sync_queue = db.relationship(
        "LocalSyncQueue",
        back_populates="contractor",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index(
            "idx_contractors_email",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_contractors_phone",
            "personal_phone",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_contractors_status",
            "account_status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_contractors_location",
            "address_state",
            "address_city",
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "idx_contractors_search",
            "search_vector",
            postgresql_using="gin",
        ),
    )
