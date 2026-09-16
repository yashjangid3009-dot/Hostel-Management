"""DataManager — handles all JSON file I/O for students and rooms.

This module has no business logic; it only serialises and deserialises data.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import List

from hostel_app.models.student import Student
from hostel_app.models.room import Room


class DataManager:
    """Reads and writes student and room data to JSON files."""

    def __init__(self, data_dir: str | Path = "hostel_app/data") -> None:
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._students_file = self._data_dir / "students.json"
        self._rooms_file = self._data_dir / "rooms.json"

    # ------------------------------------------------------------------
    # Students
    # ------------------------------------------------------------------

    def load_students(self) -> List[Student]:
        """Return a list of Student objects loaded from disk.

        Returns an empty list if the file does not exist.
        """
        if not self._students_file.exists():
            return []
        with open(self._students_file, "r", encoding="utf-8") as fh:
            raw: list = json.load(fh)
        return [Student.from_dict(d) for d in raw]

    def save_students(self, students: List[Student]) -> None:
        """Serialise *students* and write to disk."""
        with open(self._students_file, "w", encoding="utf-8") as fh:
            json.dump([s.to_dict() for s in students], fh, indent=2)

    # ------------------------------------------------------------------
    # Rooms
    # ------------------------------------------------------------------

    def load_rooms(self) -> List[Room]:
        """Return a list of Room objects loaded from disk.

        Returns an empty list if the file does not exist.
        """
        if not self._rooms_file.exists():
            return []
        with open(self._rooms_file, "r", encoding="utf-8") as fh:
            raw: list = json.load(fh)
        return [Room.from_dict(d) for d in raw]

    def save_rooms(self, rooms: List[Room]) -> None:
        """Serialise *rooms* and write to disk."""
        with open(self._rooms_file, "w", encoding="utf-8") as fh:
            json.dump([r.to_dict() for r in rooms], fh, indent=2)
