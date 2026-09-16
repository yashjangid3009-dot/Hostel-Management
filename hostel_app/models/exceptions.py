"""Custom exceptions for the Hostel Management System."""


class ValidationError(Exception):
    """Raised when a field fails its validation rule."""
    pass


class DuplicateStudentError(Exception):
    """Raised when a student_id already exists."""
    pass


class StudentNotFoundError(Exception):
    """Raised when a student lookup, update, or delete targets a non-existent ID."""
    pass


class RoomNotFoundError(Exception):
    """Raised when a referenced room_number does not exist."""
    pass


class RoomFullError(Exception):
    """Raised when a room has reached its capacity."""
    pass


class DuplicateRoomError(Exception):
    """Raised when a room_number already exists."""
    pass
