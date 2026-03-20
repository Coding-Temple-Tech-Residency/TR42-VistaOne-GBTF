from marshmallow import Schema, fields, post_load, validate

from app.models.site_visits import SiteVisit


class SiteVisitSchema(Schema):
    visit_id = fields.UUID(dump_only=True)
    job_id = fields.UUID(required=True)
    contractor_id = fields.UUID(required=True)
    visit_number = fields.Int()

    visit_status = fields.Str(
        validate=validate.OneOf(["scheduled", "in_progress", "completed", "cancelled"])
    )
    visit_type = fields.Str(
        validate=validate.OneOf(["regular", "emergency", "inspection", "delivery_only"])
    )

    check_in_time = fields.DateTime(required=True)
    check_in_location = fields.Raw()
    check_in_accuracy_meters = fields.Decimal(as_string=True, places=2)
    check_in_altitude_meters = fields.Decimal(as_string=True, places=2)
    check_in_photo_url = fields.Str()
    check_in_biometric_verified = fields.Bool()
    check_in_biometric_id = fields.UUID()
    check_in_notes = fields.Str()
    on_site_contact_person = fields.Str()
    site_conditions_on_arrival = fields.Str()
    equipment_brought = fields.Raw()

    check_out_time = fields.DateTime()
    check_out_location = fields.Raw()
    check_out_accuracy_meters = fields.Decimal(as_string=True, places=2)
    check_out_altitude_meters = fields.Decimal(as_string=True, places=2)
    check_out_photo_url = fields.Str()
    check_out_biometric_verified = fields.Bool()
    check_out_biometric_id = fields.UUID()
    check_out_notes = fields.Str()
    site_conditions_on_departure = fields.Str()
    equipment_used = fields.Raw()
    equipment_returned = fields.Raw()

    total_hours_on_site = fields.Decimal(as_string=True, places=2)
    total_break_minutes = fields.Int()
    productive_hours = fields.Decimal(as_string=True, places=2)
    travel_time_minutes = fields.Int()
    travel_distance_miles = fields.Decimal(as_string=True, places=2)

    device_id = fields.Str()
    device_model = fields.Str()
    app_version = fields.Str()
    offline_mode = fields.Bool()
    data_synced_at = fields.DateTime()

    synced_to_vendor = fields.Bool()
    synced_to_vendor_at = fields.DateTime()

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = SiteVisit

    @post_load
    def make_site_visit(self, data, **kwargs):
        return SiteVisit(**data)
