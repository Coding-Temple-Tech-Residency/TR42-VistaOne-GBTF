import uuid

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

from app.extensions import db
from app.models.mixins import TimestampMixin


class JobAssignment(db.Model, TimestampMixin):
    __tablename__ = "job_assignments"

    assignment_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    assigned_at = db.Column(
        db.DateTime(timezone=True), default=db.func.current_timestamp()
    )
    assigned_role = db.Column(db.String(100))
    is_primary = db.Column(db.Boolean, default=False)
    assignment_status = db.Column(db.String(50), default="active")
    unassigned_at = db.Column(db.DateTime(timezone=True))
    unassigned_reason = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationships
    job = db.relationship("Job", back_populates="assignments")
    contractor = db.relationship("Contractor", back_populates="job_assignments")

    __table_args__ = (
        db.Index(
            "unique_active_assignment",
            "job_id",
            "contractor_id",
            "assignment_status",
            unique=True,
            postgresql_where=text("assignment_status = 'active'"),
        ),
        db.Index(
            "idx_assignments_job",
            "job_id",
            postgresql_include=["contractor_id"],
            postgresql_where=text("assignment_status = 'active'"),
        ),
        db.Index(
            "idx_assignments_contractor",
            "contractor_id",
            postgresql_include=["job_id"],
            postgresql_where=text("assignment_status = 'active'"),
        ),
        db.CheckConstraint(
            "assignment_status IN ('active', 'completed', 'removed')",
            name="valid_assignment_status",
        ),
    )

    def __repr__(self):
        return f"<JobAssignment job={self.job_id}" f" contractor={self.contractor_id}>"
