from marshmallow import Schema, fields, post_load, validate

from app.models.biometric_verifications import BiometricVerification
from app.models.enums import VerificationType


class BiometricVerificationSchema(Schema):
    biometric_id = fields.UUID(dump_only=True)
    contractor_id = fields.UUID(required=True)
    job_id = fields.UUID()
    verification_type = fields.Enum(VerificationType, by_value=True, required=True)
    verification_status = fields.Str(
        validate=validate.OneOf(["success", "failed", "timeout", "canceled"])
    )
    biometric_type = fields.Str(
        validate=validate.OneOf(["fingerprint", "face_id", "voice", "iris", "multi_factor"])
    )
    biometric_timestamp = fields.DateTime()
    biometric_confidence_score = fields.Int(validate=validate.Range(min=0, max=100))
    biometric_device_id = fields.Str()
    biometric_method_used = fields.Str()
    biometric_failed_attempts = fields.Int()
    biometric_error_message = fields.Str()
    biometric_image_hash = fields.Str()
    biometric_template_match = fields.Bool()
    multi_factor_completed = fields.Bool()
    multi_factor_methods = fields.Raw()
    liveness_detection_passed = fields.Bool()
    liveness_score = fields.Int(validate=validate.Range(min=0, max=100))
    location = fields.Raw()  # GeoJSON or WKT
    ip_address = fields.Str()
    verification_duration_ms = fields.Int()
    created_at = fields.DateTime(dump_only=True)

    class Meta:  # type: ignore
        model = BiometricVerification

    @post_load
    def make_biometric_verification(self, data, **kwargs):
        return BiometricVerification(**data)
