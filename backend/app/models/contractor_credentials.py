import uuid

from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import text

from app.extensions import db
from app.models.enums import CredentialType
from app.models.mixins import TimestampMixin


class ContractorCredential(db.Model, TimestampMixin):
    __tablename__ = "contractor_credentials"

    credential_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    credential_type = db.Column(db.Enum(CredentialType), nullable=False)
    credential_name = db.Column(db.String(255), nullable=False)
    issuing_organization = db.Column(db.String(255))
    credential_number = db.Column(db.String(100))
    issue_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    state = db.Column(db.String(50))
    document_url = db.Column(db.Text)
    credential_data = db.Column(JSONB)

    # Relationships
    contractor = db.relationship("Contractor", back_populates="credentials")

    __table_args__ = (
        db.Index(
            "unique_contractor_credential",
            "contractor_id",
            "credential_type",
            "credential_number",
            "state",
            unique=True,
            postgresql_where=text("credential_number IS NOT NULL"),
        ),
        db.Index("idx_credentials_contractor", "contractor_id"),
        db.Index("idx_credentials_type", "credential_type"),
        db.Index("idx_credentials_expiration", "expiration_date"),
        db.CheckConstraint(
            "issue_date <= expiration_date",
            name="valid_dates",
        ),
    )

    def __repr__(self):
        return f"<ContractorCredential {self.credential_name}>"
