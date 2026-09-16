"""Room data model."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


GENDER_RESTRICTIONS = ("Any", "Male", "Female")


@dataclass
class Room:
    """Pure data container for a hostel room."""

    room_number: int
    capacity: int
    gender_restriction: str = "Any"

    def to_dict(self) -> dict:
        """Serialise to a JSON-compatible dictionary."""
        return {
            "room_number": self.room_number,
            "capacity": self.capacity,
            "gender_restriction": self.gender_restriction,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Room":
        """Deserialise from a dictionary (e.g. loaded from JSON)."""
        return cls(
            room_number=int(data["room_number"]),
            capacity=int(data["capacity"]),
            gender_restriction=data.get("gender_restriction", "Any"),
        )
