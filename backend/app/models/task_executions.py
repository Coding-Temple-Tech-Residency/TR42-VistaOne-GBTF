import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin


class TaskExecution(db.Model, TimestampMixin):
    __tablename__ = "task_executions"

    execution_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
    )
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
    visit_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("site_visits.visit_id", ondelete="SET NULL"),
    )

    execution_status = db.Column(db.String(50), default="pending")
    started_at = db.Column(db.DateTime(timezone=True))
    paused_at = db.Column(db.DateTime(timezone=True))
    resumed_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))

    task_completed = db.Column(db.Boolean, default=False)
    task_completed_at = db.Column(db.DateTime(timezone=True))
    task_completed_biometric = db.Column(db.Boolean, default=False)
    task_completed_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )

    task_duration_minutes = db.Column(db.Integer)
    task_quantity_completed = db.Column(db.Numeric(10, 2))
    task_unit_of_measure = db.Column(db.String(20))

    task_quality_rating = db.Column(db.Integer)
    task_quality_notes = db.Column(db.Text)

    issues_encountered = db.Column(db.Boolean, default=False)
    issue_ids = db.Column(JSONB)

    task_notes = db.Column(db.Text)
    contractor_notes = db.Column(db.Text)

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    task = db.relationship("Task", back_populates="executions")
    job = db.relationship("Job", back_populates="task_executions")
    contractor = db.relationship("Contractor", back_populates="task_executions")
    visit = db.relationship("SiteVisit", back_populates="task_executions")
    completion_biometric = db.relationship(
        "BiometricVerification",
        foreign_keys=[task_completed_biometric_id],
    )

    __table_args__ = (
        db.Index("idx_executions_task", task_id, completed_at),
        db.Index(
            "idx_executions_sync",
            synced_to_vendor,
            postgresql_where=(synced_to_vendor.is_(False)),
        ),
        db.Index("idx_executions_job", job_id),
        db.Index("idx_executions_contractor", contractor_id),
        db.Index("idx_executions_visit", visit_id),
        db.Index("idx_executions_biometric", task_completed_biometric_id),
        db.CheckConstraint(
            "execution_status IN ('pending', " "'started', 'paused', 'completed', 'failed')",
            name="valid_execution_status",
        ),
        db.CheckConstraint(
            "task_duration_minutes >= 0",
            name="duration_positive",
        ),
        db.CheckConstraint(
            "task_quantity_completed >= 0",
            name="quantity_positive",
        ),
        db.CheckConstraint("task_quality_rating BETWEEN 1 AND 5", name="quality_rating_range"),
        db.CheckConstraint(
            "(started_at IS NULL OR " "completed_at IS NULL OR " "started_at <= completed_at)",
            name="valid_execution_times",
        ),
        db.CheckConstraint(
            "(paused_at IS NULL OR " "resumed_at IS NULL OR " "paused_at <= resumed_at)",
            name="valid_pause_resume",
        ),
    )

    def __repr__(self):
        return f"<TaskExecution {self.execution_id}>"
