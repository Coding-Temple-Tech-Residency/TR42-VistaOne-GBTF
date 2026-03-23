from marshmallow import Schema, fields, post_load, validate

from app.models.enums import JobStatus, PriorityLevel, VendorSyncStatus
from app.models.jobs import Job


class JobSchema(Schema):
    job_id = fields.UUID(dump_only=True)
    job_number = fields.Str(required=True)
    vendor_job_id = fields.Str()
    vendor_id = fields.UUID()

    job_name = fields.Str()
    job_description = fields.Str()
    job_location = fields.Str()
    job_location_geography = fields.Raw()  # GeoAlchemy2 type; simplified as Raw here
    site_address_street = fields.Str()
    site_address_city = fields.Str()
    site_address_state = fields.Str()
    site_address_zip = fields.Str()
    site_contact_name = fields.Str()
    site_contact_phone = fields.Str(validate=validate.Regexp(r"^\+?[0-9\-\(\)\s]{10,20}$"))
    site_contact_email = fields.Email()

    scheduled_start_date = fields.DateTime()
    scheduled_end_date = fields.DateTime()
    actual_start_date = fields.DateTime()
    actual_end_date = fields.DateTime()
    estimated_hours = fields.Decimal(as_string=True, places=2)

    job_type = fields.Str()
    job_category = fields.Str()
    priority = fields.Enum(PriorityLevel, by_value=True)
    status = fields.Enum(JobStatus, by_value=True)

    vendor_name = fields.Str()
    vendor_contact_name = fields.Str()
    vendor_contact_phone = fields.Str(validate=validate.Regexp(r"^\+?[0-9\-\(\)\s]{10,20}$"))
    vendor_contact_email = fields.Email()
    vendor_instructions = fields.Str()

    po_number = fields.Str()
    quote_number = fields.Str()
    contract_number = fields.Str()
    documents_attached = fields.Raw()
    materials_needed = fields.Str()
    special_requirements = fields.Str()
    safety_requirements = fields.Str()

    last_synced_with_vendor_at = fields.DateTime()
    vendor_sync_status = fields.Enum(VendorSyncStatus, by_value=True)
    vendor_data = fields.Raw()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)

    class Meta:
        model = Job

    @post_load
    def make_job(self, data, **kwargs):
        return Job(**data)
