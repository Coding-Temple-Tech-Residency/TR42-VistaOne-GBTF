from marshmallow import Schema, fields, post_load, validate

from app.models.contractors import Contractor
from app.models.enums import AccountStatus


class ContractorSchema(Schema):
    contractor_id = fields.UUID(dump_only=True)
    first_name = fields.Str(required=True, validate=validate.Length(max=100))
    last_name = fields.Str(required=True, validate=validate.Length(max=100))
    middle_initial = fields.Str(validate=validate.Length(max=1))
    date_of_birth = fields.Date()
    ssn_last_four = fields.Str(validate=validate.Regexp(r"^[0-9]{4}$"))
    email = fields.Email(required=True)
    personal_phone = fields.Str(validate=validate.Regexp(r"^\+?[0-9\-\(\)\s]{10,20}$"))
    alternate_phone = fields.Str(validate=validate.Regexp(r"^\+?[0-9\-\(\)\s]{10,20}$"))
    address_street = fields.Str()
    address_city = fields.Str()
    address_state = fields.Str()
    address_zip = fields.Str()
    address_country = fields.Str()
    profile_photo_url = fields.Str()

    years_experience = fields.Int()
    previous_projects_count = fields.Int()
    average_rating = fields.Decimal(as_string=True, places=2)
    total_reviews = fields.Int()

    background_check_passed = fields.Bool()
    background_check_date = fields.Date()
    background_check_provider = fields.Str()
    background_check_document_url = fields.Str()
    drug_test_passed = fields.Bool()
    drug_test_date = fields.Date()
    drug_test_document_url = fields.Str()
    safety_record_score = fields.Int(validate=validate.Range(min=0, max=100))

    account_status = fields.Enum(AccountStatus, by_value=True)
    account_verified = fields.Bool()
    account_verified_at = fields.DateTime()
    last_login_at = fields.DateTime()

    language_preference = fields.Str()
    work_hours_preference = fields.Raw()
    preferred_job_types = fields.Raw()
    max_travel_distance_miles = fields.Int()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = Contractor

    @post_load
    def make_contractor(self, data, **kwargs):
        return Contractor(**data)
