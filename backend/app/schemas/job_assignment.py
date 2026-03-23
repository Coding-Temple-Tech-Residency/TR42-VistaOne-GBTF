from marshmallow import Schema, fields, post_load, validate

from app.models.job_assignments import JobAssignment


class JobAssignmentSchema(Schema):
    assignment_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    assigned_at = fields.DateTime()
    assigned_role = fields.Str()
    is_primary = fields.Bool()
    assignment_status = fields.Str(validate=validate.OneOf(["active", "completed", "removed"]))
    unassigned_at = fields.DateTime()
    unassigned_reason = fields.Str()
    notes = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = JobAssignment

    @post_load
    def make_job_assignment(self, data, **kwargs):
        return JobAssignment(**data)
