import re


def validate_phone(phone):
    """Validate phone number format."""
    return re.match(r"^\+?[0-9\-\(\)\s]{10,20}$", phone) is not None


def validate_email(email):
    """Validate email format."""
    return (
        re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
            email,
        )
        is not None
    )


def validate_ssn_last_four(ssn):
    """Validate SSN last four digits."""
    return re.match(r"^[0-9]{4}$", ssn) is not None
