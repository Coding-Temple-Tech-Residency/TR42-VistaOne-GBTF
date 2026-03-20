from marshmallow import Schema, fields, post_load

from app.models.notification_preferences import NotificationPreference


class NotificationPreferenceSchema(Schema):
    preference_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    email_notifications = fields.Bool()
    sms_notifications = fields.Bool()
    push_notifications = fields.Bool()
    job_alerts = fields.Bool()
    job_alerts_radius_miles = fields.Int()
    job_alerts_types = fields.Raw()
    payment_notifications = fields.Bool()
    schedule_notifications = fields.Bool()
    issue_notifications = fields.Bool()
    marketing_notifications = fields.Bool()
    notification_schedule = fields.Raw()
    quiet_hours_start = fields.Time()
    quiet_hours_end = fields.Time()
    quiet_hours_timezone = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = NotificationPreference

    @post_load
    def make_notification_preference(self, data, **kwargs):
        return NotificationPreference(**data)
