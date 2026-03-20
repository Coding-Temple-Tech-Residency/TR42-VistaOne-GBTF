from sqlalchemy import func

from app.extensions import db


class TimestampMixin:
    created_at = db.Column(db.DateTime, server_default=func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, server_default=None, nullable=True)
