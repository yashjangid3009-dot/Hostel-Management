"""Unit tests for HostelManager — room and student operations."""
import datetime
from unittest.mock import MagicMock
import pytest

from hostel_app.models.exceptions import (
    DuplicateRoomError,
    DuplicateStudentError,
    RoomFullError,
    RoomNotFoundError,
    StudentNotFoundError,
    ValidationError,
)
from hostel_app.models.room import Room
from hostel_app.models.student import Student
from hostel_app.services.hostel_manager import HostelManager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_dm_stub(students=None, rooms=None):
    """Return a DataManager mock that pre-loads the given lists."""
    dm = MagicMock()
    dm.load_students.return_value = students or []
    dm.load_rooms.return_value = rooms or []
    return dm


def make_manager(students=None, rooms=None) -> HostelManager:
    return HostelManager(make_dm_stub(students=students, rooms=rooms))


def sample_room(num: int = 101, cap: int = 3, restriction: str = "Any") -> Room:
    return Room(room_number=num, capacity=cap, gender_restriction=restriction)


def sample_student(
    sid: str = "S001",
    room: int = 101,
    is_staying: bool = True,
    gender: str = "Male",
) -> Student:
    return Student(
        student_id=sid,
        name="John Doe",
        phone="9876543210",
        gender=gender,
        room_number=room,
        admission_date=datetime.date(2024, 1, 1),
        is_staying=is_staying,
        email=None,
    )


# ---------------------------------------------------------------------------
# Room operations
# ---------------------------------------------------------------------------

class TestAddRoom:
    def test_add_valid_room(self):
        mgr = make_manager()
        room = mgr.add_room(101, 3)
        assert room.room_number == 101
        assert room.capacity == 3

    def test_duplicate_room_raises(self):
        mgr = make_manager(rooms=[sample_room(101)])
        with pytest.raises(DuplicateRoomError):
            mgr.add_room(101, 2)

    def test_zero_capacity_raises(self):
        mgr = make_manager()
        with pytest.raises(ValidationError):
            mgr.add_room(101, 0)

    def test_invalid_gender_restriction_raises(self):
        mgr = make_manager()
        with pytest.raises(ValidationError):
            mgr.add_room(101, 3, gender_restriction="Unknown")

    def test_save_rooms_called(self):
        dm = make_dm_stub()
        mgr = HostelManager(dm)
        mgr.add_room(101, 3)
        dm.save_rooms.assert_called_once()


class TestUpdateRoom:
    def test_update_capacity(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        mgr.update_room(101, 5, "Any")
        assert mgr._find_room(101).capacity == 5

    def test_reduce_below_occupancy_raises(self):
        room = sample_room(101, 3)
        students = [sample_student("S001", 101), sample_student("S002", 101)]
        mgr = make_manager(students=students, rooms=[room])
        with pytest.raises(ValidationError):
            mgr.update_room(101, 1, "Any")

    def test_reduce_to_exact_occupancy_allowed(self):
        room = sample_room(101, 3)
        students = [sample_student("S001", 101), sample_student("S002", 101)]
        mgr = make_manager(students=students, rooms=[room])
        mgr.update_room(101, 2, "Any")  # exactly at occupancy — should not raise
        assert mgr._find_room(101).capacity == 2

    def test_nonexistent_room_raises(self):
        mgr = make_manager()
        with pytest.raises(RoomNotFoundError):
            mgr.update_room(999, 3, "Any")


class TestDeleteRoom:
    def test_delete_empty_room(self):
        mgr = make_manager(rooms=[sample_room(101)])
        mgr.delete_room(101)
        assert mgr.get_all_rooms() == []

    def test_delete_room_with_students_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101)],
        )
        with pytest.raises(ValidationError):
            mgr.delete_room(101)

    def test_delete_nonexistent_room_raises(self):
        mgr = make_manager()
        with pytest.raises(RoomNotFoundError):
            mgr.delete_room(999)


class TestGetRoomSummary:
    def test_summary_counts_active_occupancy(self):
        rooms = [sample_room(101, 3)]
        students = [
            sample_student("S001", 101, is_staying=True),
            sample_student("S002", 101, is_staying=False),
        ]
        mgr = make_manager(students=students, rooms=rooms)
        summary = mgr.get_room_summary()
        assert len(summary) == 1
        assert summary[0]["occupancy"] == 1  # only 1 is_staying=True
        assert summary[0]["available"] == 2

    def test_empty_rooms_returns_empty_list(self):
        mgr = make_manager()
        assert mgr.get_room_summary() == []


# ---------------------------------------------------------------------------
# Student operations
# ---------------------------------------------------------------------------

class TestAddStudent:
    def test_add_valid_student(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        s = mgr.add_student(
            student_id="S001",
            name="Alice",
            phone="9876543210",
            gender="Female",
            room_number=101,
            admission_date=datetime.date(2024, 1, 1),
        )
        assert s.student_id == "S001"
        assert s.is_staying is True

    def test_duplicate_student_id_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101, 3)],
        )
        with pytest.raises(DuplicateStudentError):
            mgr.add_student("S001", "Bob", "1234567890", "Male", 101, datetime.date(2024, 1, 1))

    def test_room_not_found_raises(self):
        mgr = make_manager()
        with pytest.raises(RoomNotFoundError):
            mgr.add_student("S001", "Bob", "1234567890", "Male", 999, datetime.date(2024, 1, 1))

    def test_room_full_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101, 1)],
        )
        with pytest.raises(RoomFullError):
            mgr.add_student("S002", "Carol", "9998887770", "Female", 101, datetime.date(2024, 1, 1))

    def test_invalid_phone_raises(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        with pytest.raises(ValidationError):
            mgr.add_student("S001", "Dave", "123", "Male", 101, datetime.date(2024, 1, 1))

    def test_empty_name_raises(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        with pytest.raises(ValidationError):
            mgr.add_student("S001", "  ", "9876543210", "Male", 101, datetime.date(2024, 1, 1))

    def test_future_date_raises(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        future = datetime.date.today() + datetime.timedelta(days=1)
        with pytest.raises(ValidationError):
            mgr.add_student("S001", "Eve", "9876543210", "Female", 101, future)

    def test_invalid_gender_raises(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        with pytest.raises(ValidationError):
            mgr.add_student("S001", "Frank", "9876543210", "Unknown", 101, datetime.date(2024, 1, 1))

    def test_empty_student_id_raises(self):
        mgr = make_manager(rooms=[sample_room(101, 3)])
        with pytest.raises(ValidationError):
            mgr.add_student("", "Grace", "9876543210", "Female", 101, datetime.date(2024, 1, 1))


class TestGetStudent:
    def test_get_existing_student(self):
        s = sample_student("S001")
        mgr = make_manager(students=[s], rooms=[sample_room(101)])
        found = mgr.get_student_by_id("S001")
        assert found.student_id == "S001"

    def test_get_nonexistent_student_raises(self):
        mgr = make_manager()
        with pytest.raises(StudentNotFoundError):
            mgr.get_student_by_id("GHOST")


class TestUpdateStudent:
    def test_update_name_and_phone(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101)],
        )
        mgr.update_student("S001", "New Name", "1112223330", "Male")
        s = mgr.get_student_by_id("S001")
        assert s.name == "New Name"
        assert s.phone == "1112223330"

    def test_update_nonexistent_raises(self):
        mgr = make_manager()
        with pytest.raises(StudentNotFoundError):
            mgr.update_student("GHOST", "Name", "9876543210", "Male")

    def test_invalid_phone_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101)],
        )
        with pytest.raises(ValidationError):
            mgr.update_student("S001", "Name", "bad", "Male")


class TestDeleteStudent:
    def test_delete_existing_student(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101)],
        )
        mgr.delete_student("S001")
        assert mgr.get_all_students() == []

    def test_delete_nonexistent_raises(self):
        mgr = make_manager()
        with pytest.raises(StudentNotFoundError):
            mgr.delete_student("GHOST")


class TestCheckOutIn:
    def test_check_out_staying_student(self):
        mgr = make_manager(
            students=[sample_student("S001", 101, is_staying=True)],
            rooms=[sample_room(101)],
        )
        s = mgr.check_out_student("S001")
        assert s.is_staying is False

    def test_check_out_already_checked_out_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101, is_staying=False)],
            rooms=[sample_room(101)],
        )
        with pytest.raises(ValidationError):
            mgr.check_out_student("S001")

    def test_check_in_checked_out_student(self):
        mgr = make_manager(
            students=[sample_student("S001", 101, is_staying=False)],
            rooms=[sample_room(101, 3)],
        )
        s = mgr.check_in_student("S001")
        assert s.is_staying is True

    def test_check_in_already_staying_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101, is_staying=True)],
            rooms=[sample_room(101)],
        )
        with pytest.raises(ValidationError):
            mgr.check_in_student("S001")

    def test_check_in_full_room_raises(self):
        students = [
            sample_student("S001", 101, is_staying=True),
            sample_student("S002", 101, is_staying=False),
        ]
        mgr = make_manager(students=students, rooms=[sample_room(101, 1)])
        with pytest.raises(RoomFullError):
            mgr.check_in_student("S002")


class TestChangeRoom:
    def test_change_to_valid_room(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101, 3), sample_room(102, 3)],
        )
        s = mgr.change_room("S001", 102)
        assert s.room_number == 102

    def test_change_to_same_room_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101, 3)],
        )
        with pytest.raises(ValidationError):
            mgr.change_room("S001", 101)

    def test_change_to_nonexistent_room_raises(self):
        mgr = make_manager(
            students=[sample_student("S001", 101)],
            rooms=[sample_room(101, 3)],
        )
        with pytest.raises(RoomNotFoundError):
            mgr.change_room("S001", 999)

    def test_change_to_full_room_raises(self):
        mgr = make_manager(
            students=[
                sample_student("S001", 101),
                sample_student("S002", 102),
            ],
            rooms=[sample_room(101, 3), sample_room(102, 1)],
        )
        with pytest.raises(RoomFullError):
            mgr.change_room("S001", 102)


class TestFilterStudents:
    def setup_method(self):
        students = [
            sample_student("S001", 101, gender="Male", is_staying=True),
            sample_student("S002", 101, gender="Female", is_staying=False),
            sample_student("S003", 102, gender="Male", is_staying=True),
        ]
        rooms = [sample_room(101, 3), sample_room(102, 3)]
        self.mgr = make_manager(students=students, rooms=rooms)

    def test_no_filter_returns_all(self):
        assert len(self.mgr.filter_students()) == 3

    def test_filter_by_room(self):
        result = self.mgr.filter_students(room_number=101)
        assert len(result) == 2
        assert all(s.room_number == 101 for s in result)

    def test_filter_by_gender(self):
        result = self.mgr.filter_students(gender="Female")
        assert len(result) == 1
        assert result[0].student_id == "S002"

    def test_filter_by_is_staying(self):
        result = self.mgr.filter_students(is_staying=True)
        assert len(result) == 2

    def test_filter_by_room_and_gender(self):
        result = self.mgr.filter_students(room_number=101, gender="Male")
        assert len(result) == 1
        assert result[0].student_id == "S001"

    def test_filter_with_no_matches_returns_empty(self):
        result = self.mgr.filter_students(room_number=999)
        assert result == []
