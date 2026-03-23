from marshmallow import Schema, fields, post_load, validate

from app.models.audit_log import AuditLog


class AuditLogSchema(Schema):
    audit_id = fields.UUID(dump_only=True)
    table_name = fields.Str(required=True)
    record_id = fields.UUID(required=True)
    action = fields.Str(required=True, validate=validate.OneOf(["INSERT", "UPDATE", "DELETE"]))

    contractor_id = fields.UUID()
    session_id = fields.UUID()
    ip_address = fields.Str()

    old_data = fields.Raw()
    new_data = fields.Raw()
    changed_fields = fields.Raw()

    changed_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = AuditLog

    @post_load
    def make_audit_log(self, data, **kwargs):
        return AuditLog(**data)
