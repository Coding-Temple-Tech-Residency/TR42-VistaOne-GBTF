from marshmallow import Schema, fields, post_load, validate

from app.models.enums import SyncStatus
from app.models.local_sync_queue import LocalSyncQueue


class LocalSyncQueueSchema(Schema):
    sync_item_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    device_id = fields.Str()
    session_id = fields.UUID()

    table_name = fields.Str(required=True)
    record_id = fields.UUID(required=True)
    operation = fields.Str(required=True, validate=validate.OneOf(["INSERT", "UPDATE", "DELETE"]))
    data = fields.Raw()

    sync_status = fields.Enum(SyncStatus, by_value=True)
    sync_attempts = fields.Int()
    last_attempt_at = fields.DateTime()
    next_attempt_at = fields.DateTime()
    error_message = fields.Str()

    priority = fields.Int(validate=validate.Range(min=0))

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = LocalSyncQueue

    @post_load
    def make_local_sync_queue(self, data, **kwargs):
        return LocalSyncQueue(**data)
