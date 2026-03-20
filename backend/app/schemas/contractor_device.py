from marshmallow import Schema, fields, post_load, validate

from app.models.contractor_devices import ContractorDevice
from app.models.enums import DeviceType


class ContractorDeviceSchema(Schema):
    device_registration_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    device_id = fields.Str(required=True)
    device_name = fields.Str()
    device_type = fields.Enum(DeviceType, by_value=True)
    device_model = fields.Str()
    os_version = fields.Str()
    app_version = fields.Str()
    first_registered_at = fields.DateTime()
    last_used_at = fields.DateTime()
    biometric_enabled_on_device = fields.Bool()
    biometric_type = fields.Str(
        validate=validate.OneOf(["fingerprint", "face_id", "voice", "none"])
    )
    push_token = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = ContractorDevice

    @post_load
    def make_contractor_device(self, data, **kwargs):
        return ContractorDevice(**data)
