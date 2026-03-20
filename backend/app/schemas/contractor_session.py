from marshmallow import Schema, fields, post_load, validate

from app.models.contractor_sessions import ContractorSession
from app.models.enums import DeviceType


class ContractorSessionSchema(Schema):
    session_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    job_id = fields.UUID()
    visit_id = fields.UUID()

    session_token = fields.Str()
    session_type = fields.Str(validate=validate.OneOf(["mobile", "web", "api"]))

    device_id = fields.Str()
    device_name = fields.Str()
    device_type = fields.Enum(DeviceType, by_value=True)
    device_model = fields.Str()
    app_version = fields.Str()
    os_version = fields.Str()
    ip_address = fields.Str()

    battery_level_at_start = fields.Int(validate=validate.Range(min=0, max=100))
    network_type = fields.Str(
        validate=validate.OneOf(["wifi", "4G", "5G", "3G", "offline", "unknown"])
    )
    offline_mode_active = fields.Bool()

    data_synced = fields.Bool()
    last_sync_at = fields.DateTime()
    pending_sync_items = fields.Int(validate=validate.Range(min=0))

    started_at = fields.DateTime()
    ended_at = fields.DateTime()
    # session_duration_minutes is generated, not set

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = ContractorSession

    @post_load
    def make_contractor_session(self, data, **kwargs):
        return ContractorSession(**data)
