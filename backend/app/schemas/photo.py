from marshmallow import Schema, fields, post_load, validate

from app.models.photos import Photo


class PhotoSchema(Schema):
    photo_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    visit_id = fields.UUID()
    task_id = fields.UUID()
    issue_id = fields.UUID()

    photo_url = fields.Str(required=True)
    photo_thumbnail_url = fields.Str()
    photo_filename = fields.Str()
    photo_timestamp = fields.DateTime()
    photo_location = fields.Raw()
    photo_direction_degrees = fields.Int(validate=validate.Range(min=0, max=359))

    photo_category = fields.Str(
        validate=validate.OneOf(
            [
                "before",
                "during",
                "after",
                "issue",
                "progress",
                "delivery",
                "safety",
                "signature",
                "general",
            ]
        )
    )
    photo_tags = fields.Raw()
    photo_description = fields.Str()

    uploaded_by_id = fields.UUID()
    uploaded_by_biometric = fields.Bool()
    uploaded_by_biometric_id = fields.UUID()
    uploaded_at = fields.DateTime()
    photo_size_bytes = fields.Int(validate=validate.Range(min=0))
    photo_metadata = fields.Raw()

    ai_processed = fields.Bool()
    ai_analysis = fields.Raw()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()
    vendor_photo_url = fields.Str()

    created_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Photo

    @post_load
    def make_photo(self, data, **kwargs):
        return Photo(**data)
