import uuid

from sqlalchemy import FetchedValue, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db
from app.models.mixins import TimestampMixin
from app.models.types import PercentValue


class ProgressUpdate(db.Model, TimestampMixin):
    __tablename__ = "progress_updates"

    progress_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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

    completion_percentage_after = db.Column(PercentValue, server_default=FetchedValue())

    # completion_percentage_after is generated column, handled by DB
    work_description = db.Column(db.Text, nullable=False)
    tasks_completed = db.Column(db.Integer, default=0)
    total_tasks = db.Column(db.Integer, default=0)
    hours_worked = db.Column(db.Numeric(5, 2))
    materials_used = db.Column(JSONB)
    materials_delivered = db.Column(JSONB)
    progress_photos = db.Column(JSONB)
    next_steps = db.Column(db.Text)
    blockers = db.Column(db.Text)

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))

    # Relationships
    job = db.relationship("Job", back_populates="progress_updates")
    contractor = db.relationship("Contractor", back_populates="progress_updates")
    visit = db.relationship("SiteVisit", back_populates="progress_updates")

    __table_args__ = (
        db.Index("idx_progress_job", "job_id", "created_at"),
        db.Index(
            "idx_progress_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_progress_contractor", "contractor_id"),
        db.Index("idx_progress_visit", "visit_id"),
        db.CheckConstraint(
            "hours_worked >= 0",
            name="hours_worked_positive",
        ),
        db.CheckConstraint(
            "tasks_completed >= 0",
            name="tasks_completed_positive",
        ),
        db.CheckConstraint("total_tasks >= 0", name="total_tasks_positive"),
    )

    def __repr__(self):
        return f"<ProgressUpdate {self.progress_id}>"
