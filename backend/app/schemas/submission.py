from marshmallow import Schema, fields, post_load, validate

from app.models.submissions import Submission


class SubmissionSchema(Schema):
    submission_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    completion_id = fields.UUID()

    submission_number = fields.Str()
    submitted_at = fields.DateTime()
    submitted_by_id = fields.UUID()
    submitted_by_biometric = fields.Bool()
    submitted_biometric_id = fields.UUID()
    submitted_location = fields.Raw()

    submission_status = fields.Str(
        validate=validate.OneOf(
            [
                "draft",
                "partial",
                "complete",
                "pending_vendor",
                "confirmed_by_vendor",
                "rejected",
            ]
        )
    )
    status_updated_at = fields.DateTime()

    data_complete = fields.Bool()
    data_completeness_percentage = fields.Int(validate=validate.Range(min=0, max=100))
    missing_required_fields = fields.Raw()

    total_photos_submitted = fields.Int(validate=validate.Range(min=0))
    total_documents_submitted = fields.Int(validate=validate.Range(min=0))
    total_signatures_submitted = fields.Int(validate=validate.Range(min=0))
    total_tasks_completed = fields.Int(validate=validate.Range(min=0))
    total_issues_reported = fields.Int(validate=validate.Range(min=0))

    submission_package_url = fields.Str()
    submission_package_hash = fields.Str()

    version_number = fields.Int(validate=validate.Range(min=1))
    previous_submission_id = fields.UUID()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()
    vendor_submission_id = fields.Str()
    vendor_confirmation_data = fields.Raw()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Submission

    @post_load
    def make_submission(self, data, **kwargs):
        return Submission(**data)
