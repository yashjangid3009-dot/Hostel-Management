"""Unit tests for utils/validators.py."""
import datetime
import pytest

from hostel_app.models.exceptions import ValidationError
from hostel_app.utils.validators import (
    validate_date,
    validate_email,
    validate_non_empty,
    validate_phone,
    validate_positive_int,
)


class TestValidateNonEmpty:
    def test_valid_string_passes(self):
        validate_non_empty("hello", "name")  # no exception

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            validate_non_empty("", "name")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            validate_non_empty("   ", "name")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_non_empty(None, "name")  # type: ignore


class TestValidatePositiveInt:
    def test_one_passes(self):
        validate_positive_int(1, "capacity")

    def test_large_number_passes(self):
        validate_positive_int(100, "capacity")

    def test_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_positive_int(0, "capacity")

    def test_negative_raises(self):
        with pytest.raises(ValidationError):
            validate_positive_int(-5, "capacity")

    def test_non_numeric_string_raises(self):
        with pytest.raises(ValidationError):
            validate_positive_int("abc", "capacity")  # type: ignore

    def test_numeric_string_passes(self):
        validate_positive_int("3", "capacity")  # coercible to int


class TestValidatePhone:
    def test_ten_digits_passes(self):
        validate_phone("9876543210")

    def test_nine_digits_raises(self):
        with pytest.raises(ValidationError):
            validate_phone("987654321")

    def test_eleven_digits_raises(self):
        with pytest.raises(ValidationError):
            validate_phone("98765432101")

    def test_letters_raise(self):
        with pytest.raises(ValidationError):
            validate_phone("98765abcde")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_phone("")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_phone(None)  # type: ignore


class TestValidateEmail:
    def test_valid_email_passes(self):
        validate_email("user@example.com")

    def test_none_passes(self):
        validate_email(None)

    def test_empty_string_passes(self):
        validate_email("")

    def test_whitespace_passes(self):
        validate_email("   ")

    def test_missing_at_sign_raises(self):
        with pytest.raises(ValidationError):
            validate_email("userexample.com")

    def test_missing_domain_raises(self):
        with pytest.raises(ValidationError):
            validate_email("user@")

    def test_missing_tld_raises(self):
        with pytest.raises(ValidationError):
            validate_email("user@example")


class TestValidateDate:
    def test_today_passes(self):
        validate_date(datetime.date.today())

    def test_past_date_passes(self):
        validate_date(datetime.date(2020, 1, 1))

    def test_future_date_raises(self):
        future = datetime.date.today() + datetime.timedelta(days=1)
        with pytest.raises(ValidationError):
            validate_date(future)
