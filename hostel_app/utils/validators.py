"""Pure validation functions for the Hostel Management System.

All functions raise ValidationError on invalid input and return None on success.
They have no side effects and no state.
"""
from __future__ import annotations
import datetime
import re
from typing import Optional

from hostel_app.models.exceptions import ValidationError


def validate_non_empty(value: str, field_name: str) -> None:
    """Raise ValidationError if *value* is empty or whitespace-only."""
    if not value or not str(value).strip():
        raise ValidationError(f"{field_name} must not be empty.")


def validate_positive_int(value: int, field_name: str) -> None:
    """Raise ValidationError if *value* is not a positive integer (>= 1)."""
    try:
        v = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field_name} must be a whole number.")
    if v < 1:
        raise ValidationError(f"{field_name} must be at least 1.")


def validate_phone(phone: str) -> None:
    """Raise ValidationError if *phone* is not exactly 10 numeric digits."""
    if not phone or not str(phone).strip():
        raise ValidationError("Phone number must not be empty.")
    if not re.fullmatch(r"\d{10}", str(phone).strip()):
        raise ValidationError("Phone number must be exactly 10 numeric digits.")


def validate_email(email: Optional[str]) -> None:
    """Raise ValidationError if *email* is provided but not in a valid format.

    Empty string and None are treated as 'not provided' and always pass.
    """
    if not email or not str(email).strip():
        return  # optional field — skip validation when blank
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    if not re.fullmatch(pattern, str(email).strip()):
        raise ValidationError("Email address is not in a valid format (e.g. user@example.com).")


def validate_date(date_value: datetime.date) -> None:
    """Raise ValidationError if *date_value* is in the future."""
    if date_value > datetime.date.today():
        raise ValidationError("Admission date must not be in the future.")
