from marshmallow import Schema, fields, post_load, validate

from app.models.enums import IssueSeverity, IssueStatus
from app.models.issues import Issue


class IssueSchema(Schema):
    issue_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    visit_id = fields.UUID()
    task_id = fields.UUID()

    issue_number = fields.Str()
    issue_title = fields.Str(required=True)
    issue_description = fields.Str()
    issue_category = fields.Str(
        validate=validate.OneOf(
            [
                "safety",
                "quality",
                "delay",
                "equipment",
                "material",
                "site",
                "personnel",
                "design",
                "other",
            ]
        )
    )
    issue_subcategory = fields.Str()
    issue_severity = fields.Enum(IssueSeverity, by_value=True)
    issue_priority = fields.Int(validate=validate.Range(min=1, max=5))

    issue_reported_at = fields.DateTime()
    issue_reported_by_id = fields.UUID()
    issue_reported_biometric = fields.Bool()
    issue_reported_biometric_id = fields.UUID()
    issue_reported_location = fields.Raw()
    issue_photos = fields.Raw()

    issue_status = fields.Enum(IssueStatus, by_value=True)
    issue_status_updated_at = fields.DateTime()

    issue_resolved = fields.Bool()
    issue_resolved_at = fields.DateTime()
    issue_resolution_notes = fields.Str()
    issue_resolution_photos = fields.Raw()

    impact_on_schedule_minutes = fields.Int()
    impact_on_cost = fields.Decimal(as_string=True, places=2)
    impact_description = fields.Str()

    root_cause_category = fields.Str()
    root_cause_description = fields.Str()
    preventive_actions = fields.Str()

    vendor_issue_id = fields.Str()
    vendor_data = fields.Raw()
    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Issue

    @post_load
    def make_issue(self, data, **kwargs):
        return Issue(**data)
