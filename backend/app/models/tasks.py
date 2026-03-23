import uuid

from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID

from app.extensions import db
from app.models.enums import TaskStatus
from app.models.mixins import TimestampMixin


class Task(db.Model, TimestampMixin):
    __tablename__ = "tasks"

    task_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("jobs.job_id", ondelete="CASCADE"),
        nullable=False,
    )
    task_name = db.Column(db.String(255), nullable=False)
    task_code = db.Column(db.String(50))
    task_description = db.Column(db.Text)
    task_category = db.Column(db.String(100))

    estimated_duration_minutes = db.Column(db.Integer)
    actual_duration_minutes = db.Column(db.Integer)
    sequence_order = db.Column(db.Integer)
    parent_task_id = db.Column(UUID(as_uuid=True), db.ForeignKey("tasks.task_id"))
    dependent_task_ids = db.Column(JSONB)
    is_required = db.Column(db.Boolean, default=True)
    is_milestone = db.Column(db.Boolean, default=False)

    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey("contractors.contractor_id"))
    assigned_at = db.Column(db.DateTime(timezone=True))

    task_status = db.Column(db.Enum(TaskStatus), default=TaskStatus.pending)
    started_at = db.Column(db.DateTime(timezone=True))
    completed_at = db.Column(db.DateTime(timezone=True))

    quality_check_required = db.Column(db.Boolean, default=False)
    quality_check_passed = db.Column(db.Boolean)
    quality_check_notes = db.Column(db.Text)

    safety_required = db.Column(db.Boolean, default=False)
    safety_checklist = db.Column(JSONB)
    safety_verified = db.Column(db.Boolean, default=False)

    materials_needed = db.Column(JSONB)
    tools_needed = db.Column(JSONB)

    from sqlalchemy import FetchedValue

    search_vector = db.Column(TSVECTOR, server_default=FetchedValue())

    vendor_task_id = db.Column(db.String(255))
    vendor_data = db.Column(JSONB)

    # Relationships
    job = db.relationship("Job", back_populates="tasks")
    parent_task = db.relationship("Task", remote_side=[task_id])
    assignee = db.relationship("Contractor", foreign_keys=[assigned_to])
    executions = db.relationship(
        "TaskExecution", back_populates="task", cascade="all, delete-orphan"
    )
    issues = db.relationship("Issue", back_populates="task")
    photos = db.relationship("Photo", back_populates="task")

    __table_args__ = (
        db.Index("idx_tasks_job", job_id, sequence_order),
        db.Index("idx_tasks_status", task_status, assigned_to),
        db.Index(
            "idx_tasks_search",
            search_vector,
            postgresql_using="gin",
        ),
        db.Index("idx_tasks_parent", parent_task_id),
        db.Index("idx_tasks_assigned", assigned_to),
        db.CheckConstraint("estimated_duration_minutes >= 0", name="estimated_duration_positive"),
        db.CheckConstraint("actual_duration_minutes >= 0", name="actual_duration_positive"),
        db.CheckConstraint(
            "(started_at IS NULL OR " "completed_at IS NULL OR " "started_at <= completed_at)",
            name="valid_task_dates",
        ),
    )

    def __repr__(self):
        return f"<Task {self.task_name}>"
