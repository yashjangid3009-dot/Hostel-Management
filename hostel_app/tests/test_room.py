"""Unit tests for the Room model."""
import pytest
from hostel_app.models.room import Room


def make_room(**overrides) -> Room:
    defaults = dict(room_number=101, capacity=3, gender_restriction="Any")
    defaults.update(overrides)
    return Room(**defaults)


class TestRoomToDict:
    def test_all_fields_present(self):
        r = make_room()
        d = r.to_dict()
        assert d["room_number"] == 101
        assert d["capacity"] == 3
        assert d["gender_restriction"] == "Any"

    def test_female_restriction(self):
        r = make_room(gender_restriction="Female")
        assert r.to_dict()["gender_restriction"] == "Female"


class TestRoomFromDict:
    def test_round_trip(self):
        original = make_room(room_number=202, capacity=4, gender_restriction="Male")
        restored = Room.from_dict(original.to_dict())
        assert restored.room_number == original.room_number
        assert restored.capacity == original.capacity
        assert restored.gender_restriction == original.gender_restriction

    def test_missing_gender_restriction_defaults_to_any(self):
        data = {"room_number": 303, "capacity": 2}
        r = Room.from_dict(data)
        assert r.gender_restriction == "Any"

    def test_numeric_strings_are_coerced(self):
        data = {"room_number": "404", "capacity": "5", "gender_restriction": "Female"}
        r = Room.from_dict(data)
        assert r.room_number == 404
        assert r.capacity == 5
