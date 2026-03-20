from app.extensions import db
from app.models import BiometricVerification


class BiometricService:
    def verify(self, contractor_id, verification_type, data):
        """Perform biometric verification and store result."""
        # In a real implementation, call an external biometric service
        verification = BiometricVerification(
            contractor_id=contractor_id,
            verification_type=verification_type,
            verification_status="success",  # or 'failed'
            biometric_type=data.get("biometric_type"),
            biometric_confidence_score=data.get("confidence"),
            liveness_detection_passed=data.get("liveness", False),
            biometric_device_id=data.get("device_id"),
            ip_address=data.get("ip_address"),
            location=data.get("location"),
        )
        db.session.add(verification)
        db.session.commit()
        return verification


biometric_service = BiometricService()
