from marshmallow import Schema, fields, post_load, validate

from app.models.task_executions import TaskExecution


class TaskExecutionSchema(Schema):
    execution_id = fields.UUID(dump_only=True)
    task_id = fields.UUID(required=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    visit_id = fields.UUID()

    execution_status = fields.Str(
        validate=validate.OneOf(["pending", "started", "paused", "completed", "failed"])
    )
    started_at = fields.DateTime()
    paused_at = fields.DateTime()
    resumed_at = fields.DateTime()
    completed_at = fields.DateTime()

    task_completed = fields.Bool()
    task_completed_at = fields.DateTime()
    task_completed_biometric = fields.Bool()
    task_completed_biometric_id = fields.UUID()

    task_duration_minutes = fields.Int(validate=validate.Range(min=0))
    task_quantity_completed = fields.Decimal(as_string=True, places=2)
    task_unit_of_measure = fields.Str()

    task_quality_rating = fields.Int(validate=validate.Range(min=1, max=5))
    task_quality_notes = fields.Str()

    issues_encountered = fields.Bool()
    issue_ids = fields.Raw()

    task_notes = fields.Str()
    contractor_notes = fields.Str()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = TaskExecution

    @post_load
    def make_task_execution(self, data, **kwargs):
        return TaskExecution(**data)
