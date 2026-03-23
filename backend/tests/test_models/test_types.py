"""Tests for custom SQLAlchemy TypeDecorators in app.models.types."""

import pytest

from app.models.types import Coordinate, Email, PercentValue, PhoneNumber, RatingValue, SSNLastFour


class TestPhoneNumber:
    def test_valid_phone(self):
        assert PhoneNumber().process_bind_param("+15550001234", None) == "+15550001234"

    def test_valid_phone_dashes(self):
        assert PhoneNumber().process_bind_param("555-000-1234", None) == "555-000-1234"

    def test_none_passthrough(self):
        assert PhoneNumber().process_bind_param(None, None) is None

    def test_invalid_phone_raises(self):
        with pytest.raises(ValueError, match="Invalid phone number format"):
            PhoneNumber().process_bind_param("bad", None)

    def test_process_result_value(self):
        assert PhoneNumber().process_result_value("+15550001234", None) == "+15550001234"


class TestEmail:
    def test_valid_email(self):
        result = Email().process_bind_param("user@example.com", None)
        assert result == "user@example.com"

    def test_none_passthrough(self):
        assert Email().process_bind_param(None, None) is None

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError, match="Invalid email format"):
            Email().process_bind_param("not-an-email", None)


class TestSSNLastFour:
    def test_valid_ssn(self):
        assert SSNLastFour().process_bind_param("1234", None) == "1234"

    def test_none_passthrough(self):
        assert SSNLastFour().process_bind_param(None, None) is None

    def test_invalid_too_short(self):
        with pytest.raises(ValueError, match="4 digits"):
            SSNLastFour().process_bind_param("123", None)

    def test_invalid_letters(self):
        with pytest.raises(ValueError, match="4 digits"):
            SSNLastFour().process_bind_param("abcd", None)


class TestPercentValue:
    def test_valid_zero(self):
        assert PercentValue().process_bind_param(0, None) == 0

    def test_valid_hundred(self):
        assert PercentValue().process_bind_param(100, None) == 100

    def test_valid_midpoint(self):
        assert PercentValue().process_bind_param(50, None) == 50

    def test_none_passthrough(self):
        assert PercentValue().process_bind_param(None, None) is None

    def test_below_zero_raises(self):
        with pytest.raises(ValueError, match="0 and 100"):
            PercentValue().process_bind_param(-1, None)

    def test_above_hundred_raises(self):
        with pytest.raises(ValueError, match="0 and 100"):
            PercentValue().process_bind_param(101, None)


class TestRatingValue:
    def test_valid_zero(self):
        assert RatingValue().process_bind_param(0, None) == 0

    def test_valid_five(self):
        assert RatingValue().process_bind_param(5, None) == 5

    def test_valid_fractional(self):
        assert RatingValue().process_bind_param(4.5, None) == 4.5

    def test_none_passthrough(self):
        assert RatingValue().process_bind_param(None, None) is None

    def test_above_five_raises(self):
        with pytest.raises(ValueError, match="0 and 5"):
            RatingValue().process_bind_param(5.1, None)

    def test_below_zero_raises(self):
        with pytest.raises(ValueError, match="0 and 5"):
            RatingValue().process_bind_param(-0.1, None)


class TestCoordinate:
    def test_valid_lat(self):
        assert Coordinate().process_bind_param(45.0, None) == 45.0

    def test_none_passthrough(self):
        assert Coordinate().process_bind_param(None, None) is None

    def test_out_of_range_raises(self):
        with pytest.raises(ValueError, match="out of range"):
            Coordinate().process_bind_param(181.0, None)
