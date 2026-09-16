"""Unit tests for the Student model."""
import datetime
import pytest
from hostel_app.models.student import Student


def make_student(**overrides) -> Student:
    defaults = dict(
        student_id="S001",
        name="Riya Sharma",
        phone="9876543210",
        gender="Female",
        room_number=101,
        admission_date=datetime.date(2024, 6, 1),
        is_staying=True,
        email="riya@example.com",
    )
    defaults.update(overrides)
    return Student(**defaults)


class TestStudentToDict:
    def test_all_fields_present(self):
        s = make_student()
        d = s.to_dict()
        assert d["student_id"] == "S001"
        assert d["name"] == "Riya Sharma"
        assert d["phone"] == "9876543210"
        assert d["email"] == "riya@example.com"
        assert d["gender"] == "Female"
        assert d["room_number"] == 101
        assert d["admission_date"] == "2024-06-01"
        assert d["is_staying"] is True

    def test_email_none_serialises_to_empty_string(self):
        s = make_student(email=None)
        assert s.to_dict()["email"] == ""


class TestStudentFromDict:
    def test_round_trip(self):
        original = make_student()
        restored = Student.from_dict(original.to_dict())
        assert restored.student_id == original.student_id
        assert restored.name == original.name
        assert restored.phone == original.phone
        assert restored.email == original.email
        assert restored.gender == original.gender
        assert restored.room_number == original.room_number
        assert restored.admission_date == original.admission_date
        assert restored.is_staying == original.is_staying

    def test_empty_email_becomes_none(self):
        d = make_student(email=None).to_dict()
        restored = Student.from_dict(d)
        assert restored.email is None

    def test_is_staying_default_is_true(self):
        s = make_student(is_staying=True)
        assert s.is_staying is True

    def test_checkout_flag_preserved(self):
        s = make_student(is_staying=False)
        d = s.to_dict()
        restored = Student.from_dict(d)
        assert restored.is_staying is False

    def test_admission_date_type(self):
        s = make_student()
        restored = Student.from_dict(s.to_dict())
        assert isinstance(restored.admission_date, datetime.date)
