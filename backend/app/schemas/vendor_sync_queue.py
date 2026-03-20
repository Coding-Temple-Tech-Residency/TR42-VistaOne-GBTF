from marshmallow import Schema, fields, post_load, validate

from app.models.enums import VendorSyncStatus
from app.models.vendor_sync_queue import VendorSyncQueue


class VendorSyncQueueSchema(Schema):
    sync_id = fields.UUID(dump_only=True)
    vendor_id = fields.UUID(required=True)
    direction = fields.Str(
        required=True, validate=validate.OneOf(["inbound", "outbound"])
    )
    entity_type = fields.Str(required=True)
    entity_id = fields.UUID()
    vendor_entity_id = fields.Str()
    payload = fields.Raw(required=True)
    transformed_payload = fields.Raw()
    sync_status = fields.Enum(VendorSyncStatus, by_value=True)
    attempts = fields.Int()
    last_attempt_at = fields.DateTime()
    next_attempt_at = fields.DateTime()
    error_message = fields.Str()
    processed_at = fields.DateTime()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = VendorSyncQueue

    @post_load
    def make_vendor_sync_queue(self, data, **kwargs):
        return VendorSyncQueue(**data)
