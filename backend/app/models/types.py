import re

from sqlalchemy import Integer, Numeric, String, TypeDecorator


class PhoneNumber(TypeDecorator):
    impl = String(20)
    cache_ok = True  # stateless, safe to cache

    def process_bind_param(self, value, dialect):
        if value is not None and not re.match(r"^\+?[0-9\-\(\)\s]{10,20}$", value):
            raise ValueError("Invalid phone number format")
        return value

    def process_result_value(self, value, dialect):
        return value


class Email(TypeDecorator):
    impl = String(255)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and not re.match(
            r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", value
        ):
            raise ValueError("Invalid email format")
        return value


class SSNLastFour(TypeDecorator):
    impl = String(4)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and not re.match(r"^[0-9]{4}$", value):
            raise ValueError("SSN last four must be exactly 4 digits")
        return value


class PercentValue(TypeDecorator):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and not (0 <= value <= 100):
            raise ValueError("Percent value must be between 0 and 100")
        return value


class RatingValue(TypeDecorator):
    impl = Numeric(3, 2)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and not (0 <= value <= 5):
            raise ValueError("Rating must be between 0 and 5")
        return value


class Coordinate(TypeDecorator):
    impl = Numeric(10, 8)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None and not (-180 <= value <= 180):
            raise ValueError("Coordinate out of range")
        return value
