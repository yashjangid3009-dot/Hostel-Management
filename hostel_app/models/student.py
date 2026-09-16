"""Student data model."""
from __future__ import annotations
import datetime
from dataclasses import dataclass
from typing import Optional


GENDERS = ("Male", "Female", "Other")


@dataclass
class Student:
    """Pure data container for a hostel student."""

    student_id: str
    name: str
    phone: str
    gender: str
    room_number: int
    admission_date: datetime.date
    is_staying: bool = True
    email: Optional[str] = None

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dictionary."""
        return {
            "student_id": self.student_id,
            "name": self.name,
            "phone": self.phone,
            "email": self.email or "",
            "gender": self.gender,
            "room_number": self.room_number,
            "admission_date": self.admission_date.isoformat(),
            "is_staying": self.is_staying,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        """Deserialise from a dictionary (e.g. loaded from JSON)."""
        return cls(
            student_id=str(data["student_id"]),
            name=str(data["name"]),
            phone=str(data["phone"]),
            email=data.get("email") or None,
            gender=str(data["gender"]),
            room_number=int(data["room_number"]),
            admission_date=datetime.date.fromisoformat(data["admission_date"]),
            is_staying=bool(data["is_staying"]),
        )
