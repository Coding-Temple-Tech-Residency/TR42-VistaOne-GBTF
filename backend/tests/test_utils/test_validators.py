"""Tests for app.utils.validators."""

from app.utils.validators import validate_email, validate_phone, validate_ssn_last_four


class TestValidatePhone:
    def test_valid_us_number(self):
        assert validate_phone("+15550001234") is True

    def test_valid_number_with_dashes(self):
        assert validate_phone("555-000-1234") is True

    def test_valid_number_with_parens(self):
        assert validate_phone("(555) 000-1234") is True

    def test_invalid_too_short(self):
        assert validate_phone("12345") is False

    def test_invalid_letters(self):
        assert validate_phone("abcdefghij") is False

    def test_invalid_empty(self):
        assert validate_phone("") is False


class TestValidateEmail:
    def test_valid_simple(self):
        assert validate_email("user@example.com") is True

    def test_valid_subdomain(self):
        assert validate_email("user@mail.example.com") is True

    def test_valid_plus_addressing(self):
        assert validate_email("user+tag@example.com") is True

    def test_invalid_missing_at(self):
        assert validate_email("userexample.com") is False

    def test_invalid_missing_tld(self):
        assert validate_email("user@example") is False

    def test_invalid_empty(self):
        assert validate_email("") is False


class TestValidateSsnLastFour:
    def test_valid_four_digits(self):
        assert validate_ssn_last_four("1234") is True

    def test_valid_zeros(self):
        assert validate_ssn_last_four("0000") is True

    def test_invalid_three_digits(self):
        assert validate_ssn_last_four("123") is False

    def test_invalid_five_digits(self):
        assert validate_ssn_last_four("12345") is False

    def test_invalid_letters(self):
        assert validate_ssn_last_four("abcd") is False

    def test_invalid_empty(self):
        assert validate_ssn_last_four("") is False
