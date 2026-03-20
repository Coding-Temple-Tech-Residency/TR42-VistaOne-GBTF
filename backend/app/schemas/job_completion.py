from marshmallow import Schema, fields, post_load, validate

from app.models.job_completions import JobCompletion


class JobCompletionSchema(Schema):
    completion_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)

    job_completed = fields.Bool()
    job_completed_at = fields.DateTime()
    job_completed_biometric = fields.Bool()
    job_completed_biometric_id = fields.UUID()
    job_completed_location = fields.Raw()

    job_completed_photos = fields.Raw()
    job_completed_documents = fields.Raw()
    job_completed_notes = fields.Str()

    final_completion_percentage = fields.Int(validate=validate.Range(min=0, max=100))
    punch_list_items = fields.Raw()
    punch_list_completed = fields.Bool()
    punch_list_completed_at = fields.DateTime()

    total_job_duration_hours = fields.Decimal(as_string=True, places=2)
    total_labor_hours = fields.Decimal(as_string=True, places=2)
    total_overtime_hours = fields.Decimal(as_string=True, places=2)

    vendor_confirmed = fields.Bool()
    vendor_confirmed_at = fields.DateTime()
    vendor_confirmation_data = fields.Raw()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()
    vendor_completion_id = fields.Str()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore[override]
        model = JobCompletion

    @post_load
    def make_job_completion(self, data, **kwargs):
        return JobCompletion(**data)
