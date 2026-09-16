"""HostelManager — all business logic for the Hostel Management System.

This class is the single source of truth for all operations.
It enforces every business rule and delegates persistence to DataManager.
The Streamlit UI must NEVER contain business logic — it only calls methods here.
"""
from __future__ import annotations
import datetime
from typing import List, Optional, Dict, Any

from hostel_app.models.student import Student, GENDERS
from hostel_app.models.room import Room, GENDER_RESTRICTIONS
from hostel_app.models.exceptions import (
    DuplicateRoomError,
    DuplicateStudentError,
    RoomFullError,
    RoomNotFoundError,
    StudentNotFoundError,
    ValidationError,
)
from hostel_app.services.data_manager import DataManager
from hostel_app.utils.validators import (
    validate_date,
    validate_email,
    validate_non_empty,
    validate_phone,
    validate_positive_int,
)


class HostelManager:
    """Manages all hostel operations with full business-rule enforcement."""

    def __init__(self, data_manager: DataManager) -> None:
        self._dm = data_manager
        self._students: List[Student] = self._dm.load_students()
        self._rooms: List[Room] = self._dm.load_rooms()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _active_occupancy(self, room_number: int) -> int:
        """Count students with is_staying=True in *room_number*."""
        return sum(
            1 for s in self._students
            if s.room_number == room_number and s.is_staying
        )

    def _find_room(self, room_number: int) -> Room:
        for r in self._rooms:
            if r.room_number == room_number:
                return r
        raise RoomNotFoundError(f"Room {room_number} does not exist.")

    def _find_student(self, student_id: str) -> Student:
        for s in self._students:
            if s.student_id == student_id:
                return s
        raise StudentNotFoundError(f"Student '{student_id}' not found.")

    # ------------------------------------------------------------------
    # Room operations
    # ------------------------------------------------------------------

    def add_room(self, room_number: int, capacity: int, gender_restriction: str = "Any") -> Room:
        """Add a new room. Raises DuplicateRoomError if room_number exists."""
        validate_positive_int(room_number, "Room number")
        validate_positive_int(capacity, "Capacity")
        if gender_restriction not in GENDER_RESTRICTIONS:
            raise ValidationError(
                f"Gender restriction must be one of {GENDER_RESTRICTIONS}."
            )
        if any(r.room_number == room_number for r in self._rooms):
            raise DuplicateRoomError(f"Room {room_number} already exists.")
        room = Room(room_number=room_number, capacity=capacity, gender_restriction=gender_restriction)
        self._rooms.append(room)
        self._dm.save_rooms(self._rooms)
        return room

    def get_all_rooms(self) -> List[Room]:
        """Return a copy of all rooms."""
        return list(self._rooms)

    def update_room(self, room_number: int, capacity: int, gender_restriction: str) -> Room:
        """Update capacity and/or gender_restriction of an existing room.

        Raises ValidationError if new capacity is less than current active occupancy.
        """
        room = self._find_room(room_number)
        validate_positive_int(capacity, "Capacity")
        if gender_restriction not in GENDER_RESTRICTIONS:
            raise ValidationError(
                f"Gender restriction must be one of {GENDER_RESTRICTIONS}."
            )
        occupancy = self._active_occupancy(room_number)
        if capacity < occupancy:
            raise ValidationError(
                f"Cannot reduce capacity to {capacity}: room currently has "
                f"{occupancy} active student(s)."
            )
        room.capacity = capacity
        room.gender_restriction = gender_restriction
        self._dm.save_rooms(self._rooms)
        return room

    def delete_room(self, room_number: int) -> None:
        """Delete a room. Raises ValidationError if any student is assigned to it."""
        self._find_room(room_number)  # raises RoomNotFoundError if missing
        assigned = [s for s in self._students if s.room_number == room_number]
        if assigned:
            raise ValidationError(
                f"Cannot delete room {room_number}: "
                f"{len(assigned)} student(s) are still assigned to it."
            )
        self._rooms = [r for r in self._rooms if r.room_number != room_number]
        self._dm.save_rooms(self._rooms)

    def get_room_summary(self) -> List[Dict[str, Any]]:
        """Return a list of dicts with room stats (for display in the UI)."""
        summaries = []
        for room in self._rooms:
            occupancy = self._active_occupancy(room.room_number)
            summaries.append(
                {
                    "room_number": room.room_number,
                    "capacity": room.capacity,
                    "gender_restriction": room.gender_restriction,
                    "occupancy": occupancy,
                    "available": room.capacity - occupancy,
                }
            )
        return summaries

    # ------------------------------------------------------------------
    # Student operations
    # ------------------------------------------------------------------

    def add_student(
        self,
        student_id: str,
        name: str,
        phone: str,
        gender: str,
        room_number: int,
        admission_date: datetime.date,
        email: Optional[str] = None,
        is_staying: bool = True,
    ) -> Student:
        """Add a new student. Enforces all business rules."""
        # Validation
        validate_non_empty(student_id, "Student ID")
        validate_non_empty(name, "Name")
        validate_phone(phone)
        validate_email(email)
        validate_date(admission_date)
        if gender not in GENDERS:
            raise ValidationError(f"Gender must be one of {GENDERS}.")

        # Business rules
        if any(s.student_id == student_id for s in self._students):
            raise DuplicateStudentError(f"Student ID '{student_id}' already exists.")

        room = self._find_room(room_number)  # raises RoomNotFoundError if missing

        if is_staying and self._active_occupancy(room_number) >= room.capacity:
            raise RoomFullError(
                f"Room {room_number} is full "
                f"(capacity {room.capacity})."
            )

        student = Student(
            student_id=student_id,
            name=name,
            phone=phone,
            email=email or None,
            gender=gender,
            room_number=room_number,
            admission_date=admission_date,
            is_staying=is_staying,
        )
        self._students.append(student)
        self._dm.save_students(self._students)
        return student

    def get_all_students(self) -> List[Student]:
        """Return a copy of all students."""
        return list(self._students)

    def get_student_by_id(self, student_id: str) -> Student:
        """Return the student with the given ID. Raises StudentNotFoundError if missing."""
        return self._find_student(student_id)

    def update_student(
        self,
        student_id: str,
        name: str,
        phone: str,
        gender: str,
        email: Optional[str] = None,
    ) -> Student:
        """Update personal details of an existing student (not room assignment)."""
        student = self._find_student(student_id)
        validate_non_empty(name, "Name")
        validate_phone(phone)
        validate_email(email)
        if gender not in GENDERS:
            raise ValidationError(f"Gender must be one of {GENDERS}.")

        student.name = name
        student.phone = phone
        student.email = email or None
        student.gender = gender
        self._dm.save_students(self._students)
        return student

    def delete_student(self, student_id: str) -> None:
        """Permanently remove a student record."""
        self._find_student(student_id)  # raises StudentNotFoundError if missing
        self._students = [s for s in self._students if s.student_id != student_id]
        self._dm.save_students(self._students)

    def check_out_student(self, student_id: str) -> Student:
        """Mark a student as checked out (is_staying=False)."""
        student = self._find_student(student_id)
        if not student.is_staying:
            raise ValidationError(f"Student '{student_id}' is already checked out.")
        student.is_staying = False
        self._dm.save_students(self._students)
        return student

    def check_in_student(self, student_id: str) -> Student:
        """Mark a student as checked in (is_staying=True). Re-checks room capacity."""
        student = self._find_student(student_id)
        if student.is_staying:
            raise ValidationError(f"Student '{student_id}' is already checked in.")
        room = self._find_room(student.room_number)
        if self._active_occupancy(student.room_number) >= room.capacity:
            raise RoomFullError(
                f"Cannot check in: room {student.room_number} is full "
                f"(capacity {room.capacity})."
            )
        student.is_staying = True
        self._dm.save_students(self._students)
        return student

    def change_room(self, student_id: str, new_room_number: int) -> Student:
        """Move a student to a different room. Validates new room exists and has capacity."""
        student = self._find_student(student_id)
        if student.room_number == new_room_number:
            raise ValidationError(
                f"Student is already in room {new_room_number}."
            )
        new_room = self._find_room(new_room_number)  # raises RoomNotFoundError if missing
        if student.is_staying and self._active_occupancy(new_room_number) >= new_room.capacity:
            raise RoomFullError(
                f"Room {new_room_number} is full "
                f"(capacity {new_room.capacity})."
            )
        student.room_number = new_room_number
        self._dm.save_students(self._students)
        return student

    def filter_students(
        self,
        room_number: Optional[int] = None,
        gender: Optional[str] = None,
        is_staying: Optional[bool] = None,
    ) -> List[Student]:
        """Return students matching the given filter criteria.

        Pass None for any criterion to skip that filter.
        """
        result = list(self._students)
        if room_number is not None:
            result = [s for s in result if s.room_number == room_number]
        if gender is not None:
            result = [s for s in result if s.gender == gender]
        if is_staying is not None:
            result = [s for s in result if s.is_staying == is_staying]
        return result
