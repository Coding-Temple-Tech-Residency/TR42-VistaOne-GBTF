from marshmallow import Schema, fields, post_load, validate

from app.models.contractor_insurance import ContractorInsurance


class ContractorInsuranceSchema(Schema):
    insurance_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    insurance_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            [
                "general_liability",
                "workers_comp",
                "auto",
                "professional",
                "tools",
            ]
        ),
    )
    policy_number = fields.Str(required=True)
    provider_name = fields.Str()
    provider_phone = fields.Str(validate=validate.Regexp(r"^\+?[0-9\-\(\)\s]{10,20}$"))
    coverage_amount = fields.Decimal(as_string=True, places=2)
    deductible = fields.Decimal(as_string=True, places=2)
    effective_date = fields.Date()
    expiration_date = fields.Date()
    insurance_document_url = fields.Str()
    additional_insured_required = fields.Bool()
    additional_insured_certificate_url = fields.Str()
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = ContractorInsurance

    @post_load
    def make_contractor_insurance(self, data, **kwargs):
        return ContractorInsurance(**data)
