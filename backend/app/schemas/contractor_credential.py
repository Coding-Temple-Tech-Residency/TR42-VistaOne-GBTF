from marshmallow import Schema, fields, post_load

from app.models.contractor_credentials import ContractorCredential
from app.models.enums import CredentialType


class ContractorCredentialSchema(Schema):
    credential_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    credential_type = fields.Enum(CredentialType, by_value=True, required=True)
    credential_name = fields.Str(required=True)
    issuing_organization = fields.Str()
    credential_number = fields.Str()
    issue_date = fields.Date()
    expiration_date = fields.Date()
    state = fields.Str()
    document_url = fields.Str()
    credential_data = fields.Raw()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = ContractorCredential

    @post_load
    def make_contractor_credential(self, data, **kwargs):
        return ContractorCredential(**data)
