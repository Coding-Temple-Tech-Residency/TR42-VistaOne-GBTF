import uuid

from sqlalchemy.dialects.postgresql import UUID

from app.extensions import db
from app.models.mixins import TimestampMixin
from app.models.types import PhoneNumber


class ContractorInsurance(db.Model, TimestampMixin):
    __tablename__ = "contractor_insurance"

    insurance_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("contractors.contractor_id", ondelete="CASCADE"),
        nullable=False,
    )
    insurance_type = db.Column(db.String(50), nullable=False)  # checked in SQL
    policy_number = db.Column(db.String(100), nullable=False)
    provider_name = db.Column(db.String(255))
    provider_phone = db.Column(PhoneNumber)
    coverage_amount = db.Column(db.Numeric(12, 2))
    deductible = db.Column(db.Numeric(12, 2))
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    insurance_document_url = db.Column(db.Text)
    additional_insured_required = db.Column(db.Boolean, default=False)
    additional_insured_certificate_url = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationships
    contractor = db.relationship("Contractor", back_populates="insurance_policies")

    __table_args__ = (
        db.Index("idx_insurance_contractor", contractor_id),
        db.Index("idx_insurance_expiration", expiration_date),
        db.CheckConstraint(
            "insurance_type IN ('general_liability', "
            "'workers_comp', 'auto', 'professional', "
            "'tools')",
            name="valid_insurance_type",
        ),
        db.CheckConstraint(
            "effective_date <= expiration_date",
            name="valid_insurance_dates",
        ),
        db.CheckConstraint(
            "coverage_amount >= 0",
            name="coverage_amount_positive",
        ),
        db.CheckConstraint("deductible >= 0", name="deductible_positive"),
    )

    def __repr__(self):
        return f"<ContractorInsurance {self.policy_number}>"
