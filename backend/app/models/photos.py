import uuid

from geoalchemy2 import Geography
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.extensions import db


class Photo(db.Model):
    __tablename__ = "photos"

    photo_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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
    task_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("tasks.task_id", ondelete="SET NULL"),
    )
    issue_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("issues.issue_id", ondelete="SET NULL"),
    )

    photo_url = db.Column(db.Text, nullable=False)
    photo_thumbnail_url = db.Column(db.Text)
    photo_filename = db.Column(db.String(255))
    photo_timestamp = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    photo_location = db.Column(Geography(geometry_type="POINT", srid=4326))
    photo_direction_degrees = db.Column(db.Integer)

    photo_category = db.Column(db.String(50))
    photo_tags = db.Column(JSONB)
    photo_description = db.Column(db.Text)

    uploaded_by_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id"),
    )
    uploaded_by_biometric = db.Column(db.Boolean, default=False)
    uploaded_by_biometric_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("biometric_verifications.biometric_id"),
    )
    uploaded_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())
    photo_size_bytes = db.Column(db.BigInteger)
    photo_metadata = db.Column(JSONB)

    ai_processed = db.Column(db.Boolean, default=False)
    ai_analysis = db.Column(JSONB)

    synced_to_vendor = db.Column(db.Boolean, default=False)
    synced_to_vendor_at = db.Column(db.DateTime(timezone=True))
    vendor_photo_url = db.Column(db.Text)

    created_at = db.Column(db.DateTime(timezone=True), default=db.func.current_timestamp())

    # Relationships
    job = db.relationship("Job", back_populates="photos")
    # In photos.py, should already have something like:
    contractor = db.relationship(
        "Contractor", foreign_keys=[contractor_id], back_populates="photos"
    )
    uploaded_by = db.relationship(
        "Contractor",
        foreign_keys=[uploaded_by_id],
        back_populates="photos_uploaded",
    )
    visit = db.relationship("SiteVisit", back_populates="photos")
    task = db.relationship("Task", back_populates="photos")
    issue = db.relationship("Issue", back_populates="photos")
    uploaded_by = db.relationship("Contractor", foreign_keys=[uploaded_by_id])
    uploaded_biometric = db.relationship(
        "BiometricVerification", foreign_keys=[uploaded_by_biometric_id]
    )

    __table_args__ = (
        db.Index(
            "idx_photos_job",
            "job_id",
            "photo_category",
            "photo_timestamp",
        ),
        db.Index(
            "idx_photos_sync",
            "synced_to_vendor",
            postgresql_where=text("synced_to_vendor = false"),
        ),
        db.Index("idx_photos_contractor", "contractor_id"),
        db.Index("idx_photos_visit", "visit_id"),
        db.Index("idx_photos_task", "task_id"),
        db.Index("idx_photos_issue", "issue_id"),
        db.Index("idx_photos_uploaded_by", "uploaded_by_id"),
        db.Index("idx_photos_biometric", "uploaded_by_biometric_id"),
        db.CheckConstraint(
            "photo_category IN ('before', 'during', "
            "'after', 'issue', 'progress', 'delivery', "
            "'safety', 'signature', 'general')",
            name="valid_photo_category",
        ),
        db.CheckConstraint("photo_direction_degrees BETWEEN 0 AND 359", name="direction_range"),
        db.CheckConstraint("photo_size_bytes >= 0", name="size_positive"),
    )

    def __repr__(self):
        return f"<Photo {self.photo_filename}>"
