from marshmallow import Schema, fields, post_load, validate

from app.models.job_responses import JobResponse


class JobResponseSchema(Schema):
    response_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    response_type = fields.Str(
        required=True,
        validate=validate.OneOf(["accept", "decline", "counter", "pending"]),
    )
    job_accepted = fields.Bool()
    job_accepted_at = fields.DateTime()
    job_accepted_biometric_verified = fields.Bool()
    job_accepted_biometric_id = fields.UUID()
    job_accepted_location = fields.Raw()
    estimated_arrival_time = fields.DateTime()
    job_declined = fields.Bool()
    job_declined_reason = fields.Str()
    job_declined_category = fields.Str(
        validate=validate.OneOf(["schedule", "distance", "skills", "equipment", "other"])
    )
    job_declined_at = fields.DateTime()
    counter_offer_amount = fields.Decimal(as_string=True, places=2)
    counter_offer_schedule = fields.DateTime()
    counter_offer_notes = fields.Str()
    contractor_notes = fields.Str()
    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = JobResponse

    @post_load
    def make_job_response(self, data, **kwargs):
        return JobResponse(**data)
