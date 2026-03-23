from marshmallow import Schema, fields, post_load, validate

from app.models.progress_updates import ProgressUpdate


class ProgressUpdateSchema(Schema):
    progress_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    visit_id = fields.UUID()

    completion_percentage = fields.Int(required=True, validate=validate.Range(min=0, max=100))
    completion_percentage_before = fields.Int(validate=validate.Range(min=0, max=100))
    # completion_percentage_after is generated, not needed to set
    work_description = fields.Str(required=True)
    tasks_completed = fields.Int()
    total_tasks = fields.Int()
    hours_worked = fields.Decimal(as_string=True, places=2)
    materials_used = fields.Raw()
    materials_delivered = fields.Raw()
    progress_photos = fields.Raw()
    next_steps = fields.Str()
    blockers = fields.Str()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        model = ProgressUpdate

    @post_load
    def make_progress_update(self, data, **kwargs):
        return ProgressUpdate(**data)
