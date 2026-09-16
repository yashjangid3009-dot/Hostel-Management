"""Unit tests for DataManager."""
import datetime
import pytest

from hostel_app.models.student import Student
from hostel_app.models.room import Room
from hostel_app.services.data_manager import DataManager


def make_student(sid: str = "S001", room: int = 101) -> Student:
    return Student(
        student_id=sid,
        name="Test Student",
        phone="9876543210",
        gender="Male",
        room_number=room,
        admission_date=datetime.date(2024, 1, 15),
        is_staying=True,
        email="test@example.com",
    )


def make_room(num: int = 101, cap: int = 3) -> Room:
    return Room(room_number=num, capacity=cap, gender_restriction="Any")


class TestDataManagerStudents:
    def test_load_returns_empty_list_when_file_missing(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        assert dm.load_students() == []

    def test_save_and_reload_round_trip(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        students = [make_student("S001"), make_student("S002", room=102)]
        dm.save_students(students)
        loaded = dm.load_students()
        assert len(loaded) == 2
        ids = {s.student_id for s in loaded}
        assert ids == {"S001", "S002"}

    def test_all_fields_preserved(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        original = make_student()
        dm.save_students([original])
        restored = dm.load_students()[0]
        assert restored.student_id == original.student_id
        assert restored.name == original.name
        assert restored.phone == original.phone
        assert restored.gender == original.gender
        assert restored.room_number == original.room_number
        assert restored.admission_date == original.admission_date
        assert restored.is_staying == original.is_staying
        assert restored.email == original.email

    def test_save_empty_list(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        dm.save_students([])
        assert dm.load_students() == []

    def test_overwrite_replaces_previous_data(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        dm.save_students([make_student("S001")])
        dm.save_students([make_student("S099")])
        loaded = dm.load_students()
        assert len(loaded) == 1
        assert loaded[0].student_id == "S099"


class TestDataManagerRooms:
    def test_load_returns_empty_list_when_file_missing(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        assert dm.load_rooms() == []

    def test_save_and_reload_round_trip(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        rooms = [make_room(101, 3), make_room(102, 4)]
        dm.save_rooms(rooms)
        loaded = dm.load_rooms()
        assert len(loaded) == 2
        numbers = {r.room_number for r in loaded}
        assert numbers == {101, 102}

    def test_all_fields_preserved(self, tmp_path):
        dm = DataManager(data_dir=tmp_path)
        original = make_room(201, 5)
        original.gender_restriction = "Female"
        dm.save_rooms([original])
        restored = dm.load_rooms()[0]
        assert restored.room_number == original.room_number
        assert restored.capacity == original.capacity
        assert restored.gender_restriction == original.gender_restriction

    def test_data_dir_created_automatically(self, tmp_path):
        nested = tmp_path / "deep" / "nested"
        dm = DataManager(data_dir=nested)
        assert nested.exists()
