from app.models import ContractorDevice


class NotificationService:
    def send_push(self, contractor_id, title, body, data=None):
        """Send push notification to contractor's devices."""
        devices = ContractorDevice.query.filter_by(
            contractor_id=contractor_id, is_active=True
        ).all()
        for device in devices:
            if device.push_token:
                # Implement actual push sending (FCM/APNS)
                pass

    def send_sms(self, phone_number, message):
        """Send SMS via provider."""

    def send_email(self, email, subject, body):
        """Send email via SMTP or service."""


notification_service = NotificationService()
