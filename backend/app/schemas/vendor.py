from marshmallow import Schema, fields, post_load

from app.models.enums import VendorSyncStatus
from app.models.vendors import Vendor


class VendorSchema(Schema):
    vendor_id = fields.UUID(dump_only=True)
    vendor_code = fields.Str(required=True)
    vendor_name = fields.Str(required=True)
    vendor_api_config = fields.Raw()
    webhook_url = fields.Str()
    sync_frequency_minutes = fields.Int()
    last_sync_at = fields.DateTime()
    last_sync_status = fields.Enum(VendorSyncStatus, by_value=True)
    sync_error_message = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Vendor

    @post_load
    def make_vendor(self, data, **kwargs):
        return Vendor(**data)
