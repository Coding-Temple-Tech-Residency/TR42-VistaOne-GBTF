from marshmallow import Schema, fields, post_load, validate

from app.models.enums import TaskStatus
from app.models.tasks import Task


class TaskSchema(Schema):
    task_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    task_name = fields.Str(required=True)
    task_code = fields.Str()
    task_description = fields.Str()
    task_category = fields.Str()

    estimated_duration_minutes = fields.Int(validate=validate.Range(min=0))
    actual_duration_minutes = fields.Int(validate=validate.Range(min=0))
    sequence_order = fields.Int()
    parent_task_id = fields.UUID()
    dependent_task_ids = fields.Raw()
    is_required = fields.Bool()
    is_milestone = fields.Bool()

    assigned_to = fields.UUID()
    assigned_at = fields.DateTime()

    task_status = fields.Enum(TaskStatus, by_value=True)
    started_at = fields.DateTime()
    completed_at = fields.DateTime()

    quality_check_required = fields.Bool()
    quality_check_passed = fields.Bool()
    quality_check_notes = fields.Str()

    safety_required = fields.Bool()
    safety_checklist = fields.Raw()
    safety_verified = fields.Bool()

    materials_needed = fields.Raw()
    tools_needed = fields.Raw()

    vendor_task_id = fields.Str()
    vendor_data = fields.Raw()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Task

    @post_load
    def make_task(self, data, **kwargs):
        return Task(**data)
