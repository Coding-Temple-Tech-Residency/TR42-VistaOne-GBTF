"""Tests for BiometricService."""

from app.models.enums import VerificationType


def test_biometric_verify(app, test_contractor):
    """verify() creates a BiometricVerification record."""
    from app.models.biometric_verifications import BiometricVerification
    from app.services.biometric_service import biometric_service

    with app.app_context():
        verification = biometric_service.verify(
            contractor_id=test_contractor.contractor_id,
            verification_type=VerificationType.check_in,
            data={
                "biometric_type": "fingerprint",
                "confidence": 95,
                "liveness": True,
                "device_id": "device-001",
            },
        )

        assert verification.biometric_id is not None
        assert str(verification.contractor_id) == str(test_contractor.contractor_id)
        assert verification.verification_status == "success"
        assert verification.biometric_type == "fingerprint"
        assert verification.biometric_confidence_score == 95
        assert verification.liveness_detection_passed is True

        # Verify persisted in DB
        from app.extensions import db

        saved = db.session.get(BiometricVerification, verification.biometric_id)
        assert saved is not None


def test_biometric_verify_minimal_data(app, test_contractor):
    """verify() works with minimal data dict."""
    from app.services.biometric_service import biometric_service

    with app.app_context():
        verification = biometric_service.verify(
            contractor_id=test_contractor.contractor_id,
            verification_type=VerificationType.task,
            data={},
        )
        assert verification.biometric_id is not None
        assert verification.liveness_detection_passed is False
