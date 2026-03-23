"""Tests for app.utils.helpers."""

from app.utils.helpers import generate_job_number, generate_submission_number


def test_generate_job_number_returns_string():
    result = generate_job_number()
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_job_number_unique():
    result1 = generate_job_number()
    result2 = generate_job_number()
    assert result1 != result2


def test_generate_submission_number_returns_string():
    result = generate_submission_number()
    assert isinstance(result, str)
    assert len(result) > 0


def test_generate_submission_number_unique():
    result1 = generate_submission_number()
    result2 = generate_submission_number()
    assert result1 != result2
