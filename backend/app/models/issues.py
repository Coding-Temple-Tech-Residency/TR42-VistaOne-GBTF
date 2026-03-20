import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID

from app.extensions import db
from app.models.enums import IssueSeverity, IssueStatus
from app.models.mixins import TimestampMixin


class Issue(db.Model, TimestampMixin):
    __tablename__ = "issues"

    issue_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
    )
    contractor_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("contractors.contractor_id")
    )
    assigned_contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id"),
    )
    visit_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("site_visits.visit_id", ondelete="SET NULL"),
    )
    task_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("tasks.task_id", ondelete="SET NULL")
    )

    issue_number = db.Column(db.String(50), unique=True)
    issue_title = db.Column(db.String(255), nullable=False)
    issue_description = db.Column(db.Text)
    issue_category = db.Column(db.String(50))
    issue_subcategory = db.Column(db.String(50))
    issue_severity = db.Column(
        db.Enum(IssueSeverity),
        default=IssueSeverity.medium,
    )
    issue_priority = db.Column(db.Integer)

    issue_reported_at = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )
    issue_reported_by_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id"),
    )
    issue_reported_biometric = db.Column(db.Boolean, default=False)
    issue_reported_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    issue_reported_location = db.Column(Geography(geometry_type="POINT", srid=4326))
    issue_photos = db.Column(JSONB)

    issue_status = db.Column(db.Enum(IssueStatus), default=IssueStatus.open)
    issue_status_updated_at = db.Column(db.DateTime(timezone=True))

    issue_resolved = db.Column(db.Boolean, default=False)
    issue_resolved_at = db.Column(db.DateTime(timezone=True))
    issue_resolution_notes = db.Column(db.Text)
    issue_resolution_photos = db.Column(JSONB)

    impact_on_schedule_minutes = db.Column(db.Integer)
    impact_on_cost = db.Column(db.Numeric(10, 2))
    impact_description = db.Column(db.Text)

    root_cause_category = db.Column(db.String(50))
    root_cause_description = db.Column(db.Text)
    preventive_actions = db.Column(db.Text)

    from sqlalchemy import FetchedValue

    search_vector = db.Column(TSVECTOR, server_default=FetchedValue())

    vendor_issue_id = db.Column(db.String(255))
    vendor_data = db.Column(JSONB)
    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    job = db.relationship("Job", back_populates="issues")
    contractor = db.relationship(
        "Contractor", foreign_keys=[contractor_id], back_populates="issues"
    )
    assignee = db.relationship(
        "Contractor",
        foreign_keys=[assigned_contractor_id],
        back_populates="assigned_issues",
    )
    visit = db.relationship("SiteVisit", back_populates="issues")
    task = db.relationship("Task", back_populates="issues")
    reported_by = db.relationship(
        "Contractor",
        foreign_keys=[issue_reported_by_id],
        back_populates="issues_reported",
    )
    reported_biometric = db.relationship(
        "BiometricVerification", foreign_keys=[issue_reported_biometric_id]
    )
    photos = db.relationship("Photo", back_populates="issue")

    __table_args__ = (
        db.Index("idx_issues_job", job_id, issue_status),
        db.Index("idx_issues_status", issue_status, issue_severity),
        db.Index("idx_issues_search", search_vector, postgresql_using="gin"),
        db.Index(
            "idx_issues_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_issues_contractor", contractor_id),
        db.Index("idx_issues_assigned", assigned_contractor_id),
        db.Index("idx_issues_visit", visit_id),
        db.Index("idx_issues_task", task_id),
        db.Index("idx_issues_reporter", issue_reported_by_id),
        db.Index("idx_issues_biometric", issue_reported_biometric_id),
        db.CheckConstraint(
            "issue_category IN ('safety', 'quality', "
            "'delay', 'equipment', 'material', 'site', "
            "'personnel', 'design', 'other')",
            name="valid_issue_category",
        ),
        db.CheckConstraint(
            "issue_priority BETWEEN 1 AND 5",
            name="priority_range",
        ),
    )

    def __repr__(self):
        return f"<Issue {self.issue_title}>"
