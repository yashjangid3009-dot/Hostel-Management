# Hostel Management System — Implementation Plan

## Top-Level Overview

Build a beginner-level Python OOP project — a Hostel Management System — using:
- **Python** with object-oriented design
- **Streamlit** multi-page web UI (`pages/` folder)
- **JSON** for local data persistence (`students.json`, `rooms.json`)
- **pytest** for unit testing of all classes

The system allows a hostel administrator to manage rooms and students: create rooms
with fixed capacity, assign students to rooms, check students in/out, edit or delete
records, and filter views. Business logic is fully separated from the UI layer.

No authentication, databases, APIs, datasets, or payment systems are used.

---

## Architecture Overview

```
hostel_app/
├── app.py                     # Streamlit entry point (home/landing page)
├── pages/
│   ├── 1_Manage_Rooms.py      # Add / edit / delete rooms; view occupancy
│   ├── 2_Add_Student.py       # Add new student and assign to a room
│   ├── 3_View_Students.py     # View, filter, check-in/out students
│   ├── 4_Edit_Student.py      # Edit student details or change room
│   └── 5_Delete_Student.py    # Delete a student record
├── models/
│   ├── __init__.py
│   ├── student.py             # Student dataclass + exceptions
│   └── room.py                # Room dataclass
├── services/
│   ├── __init__.py
│   ├── hostel_manager.py      # All business logic
│   └── data_manager.py        # JSON read/write operations
├── utils/
│   ├── __init__.py
│   └── validators.py          # Pure validation functions
├── data/
│   ├── students.json          # Persisted student records
│   └── rooms.json             # Persisted room records
└── tests/
    ├── __init__.py
    ├── test_student.py
    ├── test_room.py
    ├── test_hostel_manager.py
    └── test_data_manager.py
```

---

## Class Responsibilities

### `Student` (models/student.py)
- Holds all data fields for one student
- Fields: `student_id`, `name`, `phone`, `email` (optional), `gender`, `room_number`,
  `admission_date`, `is_staying`
- Provides `to_dict()` and `from_dict()` for JSON serialisation
- Has no business logic — it is a pure data container

### `Room` (models/room.py)
- Holds all data fields for one room
- Fields: `room_number`, `capacity`, `gender_restriction` (optional: Male/Female/Any)
- Provides `to_dict()` and `from_dict()` for JSON serialisation
- Has no business logic — it is a pure data container

### `HostelManager` (services/hostel_manager.py)
- The single source of business logic
- Holds in-memory lists of `Student` and `Room` objects loaded from `DataManager`
- Enforces all business rules (unique IDs, room capacity, valid room assignment)
- Provides all CRUD methods: add, get, update, delete for both students and rooms
- Provides: `check_out_student`, `check_in_student`, `change_room`, `filter_students`,
  `get_room_summary`
- Calls `DataManager.save_*` after every mutating operation to persist changes
- Raises named exceptions on rule violations; never returns error strings

### `DataManager` (services/data_manager.py)
- Owns all file I/O: reads and writes `students.json` and `rooms.json`
- Provides: `load_students`, `save_students`, `load_rooms`, `save_rooms`
- Converts raw dicts from JSON into `Student`/`Room` objects and vice versa
- Handles missing files gracefully (returns empty list on first run)
- Has no business logic — it only serialises and deserialises

### Custom Exceptions (models/student.py or models/exceptions.py)
- `DuplicateStudentError` — student_id already exists
- `StudentNotFoundError` — lookup/update/delete on non-existent ID
- `RoomNotFoundError` — referenced room_number does not exist
- `RoomFullError` — room has reached its capacity
- `DuplicateRoomError` — room_number already exists
- `ValidationError` — any field fails its validation rule

### `validators.py` (utils/validators.py)
- Pure functions, no state
- `validate_phone(phone)` — 10-digit numeric string
- `validate_email(email)` — basic format check, allows empty/None
- `validate_date(date_str)` — not in the future
- `validate_non_empty(value, field_name)` — raises ValidationError if blank
- `validate_positive_int(value, field_name)` — must be >= 1

---

## Data Model

### Student JSON record
```json
{
  "student_id": "S001",
  "name": "Riya Sharma",
  "phone": "9876543210",
  "email": "riya@example.com",
  "gender": "Female",
  "room_number": 102,
  "admission_date": "2024-06-01",
  "is_staying": true
}
```

### Room JSON record
```json
{
  "room_number": 102,
  "capacity": 3,
  "gender_restriction": "Female"
}
```

---

## Business Rules

1. Student ID must be unique across all students.
2. Room number must exist before a student can be assigned to it.
3. A room's current occupancy (count of students with `is_staying=True` in that room)
   must be less than its capacity before a new student can be checked in.
4. A checked-out student (`is_staying=False`) does not count toward room occupancy.
5. A student's room can be changed only if the target room exists and has available capacity.
6. Room capacity can only be reduced if the new capacity is >= current active occupancy.
7. Deleting a room is only allowed if no students are currently assigned to it.
8. Admission date must not be in the future.
9. Phone must be a 10-digit numeric string.
10. Email, if provided, must match a basic format.

---

## Data Flow

1. **App starts** → Streamlit loads `app.py` → `HostelManager` is instantiated in
   `st.session_state`, calling `DataManager.load_*` to populate in-memory lists.
2. **User action on a page** → page calls a `HostelManager` method.
3. **HostelManager validates** inputs (using `validators.py`) and enforces business rules.
4. **On success** → in-memory list is updated, then `DataManager.save_*` is called.
5. **On failure** → a named exception is raised → the Streamlit page catches it and
   displays `st.error(...)`.
6. **Page re-renders** → Streamlit re-reads from the updated in-memory state.

---

## Streamlit UI Components

### `app.py` — Home / Landing Page
- Brief title and description
- Summary stats: total rooms, total students, currently staying, available beds

### `pages/1_Manage_Rooms.py`
- Form to add a new room: room number, capacity, gender restriction
- Table of all rooms with columns: number, capacity, occupancy, available beds
- Inline edit and delete buttons per row (delete blocked if students assigned)

### `pages/2_Add_Student.py`
- Form fields: student ID, name, phone, email, gender, room (selectbox from existing rooms),
  admission date
- On submit: calls `HostelManager.add_student`, shows success or error message

### `pages/3_View_Students.py`
- Filters sidebar: by room, by gender, by status (Staying / Checked Out / All)
- `st.dataframe` table of filtered results
- Check-In and Check-Out buttons per student row

### `pages/4_Edit_Student.py`
- Selectbox to choose a student by ID/name
- Pre-filled form with current values
- Save changes: calls `HostelManager.update_student`
- Change room: separate selectbox + button, calls `HostelManager.change_room`

### `pages/5_Delete_Student.py`
- Selectbox to choose a student
- Confirmation checkbox ("I confirm I want to delete this record")
- Delete button: calls `HostelManager.delete_student`

---

## Validation Strategy

- All validation lives in `utils/validators.py` as pure functions.
- `HostelManager` calls validators before any mutation.
- Streamlit pages display user-friendly messages from caught exceptions — they never
  contain validation logic themselves.
- Validators raise `ValidationError` with a descriptive message.

---

## Exception Handling

- All custom exceptions are defined in one place (`models/exceptions.py`).
- `HostelManager` raises exceptions; it never returns `None` or error strings.
- Streamlit pages wrap `HostelManager` calls in `try/except` blocks and map each
  exception to `st.error(...)`.
- `DataManager` raises `IOError` or `json.JSONDecodeError` only for genuine file
  system problems, not for business rule violations.

---

## Unit Testing Strategy

- Tests live in `tests/`, one file per class.
- Each test file uses `pytest` with no external dependencies (no files, no Streamlit).
- `DataManager` tests use `tmp_path` (pytest fixture) to write/read real temp JSON files.
- `HostelManager` tests inject a mock or stub `DataManager` that does not touch the disk.
- Every business rule has at least one positive test and one negative test.

### Test coverage targets per class
| Class | Key tests |
|---|---|
| `Student` | to_dict / from_dict round-trip, field defaults |
| `Room` | to_dict / from_dict round-trip, field defaults |
| `HostelManager` | add/get/update/delete student, add/delete room, check-in, check-out, change room, filter, capacity enforcement, duplicate ID, room-not-found |
| `DataManager` | load from missing file, save and reload, data integrity round-trip |
| `validators` | valid/invalid phone, email, date, non-empty, positive int |

---

## Implementation Sequence

Each sub-task below is designed to be implemented independently in order.

---

### Sub-Task 1 — Project Scaffold and Custom Exceptions
**Intent:** Create the full folder structure and the exception classes that every other
module depends on.

**Expected Outcomes:**
- All folders and `__init__.py` files exist
- `models/exceptions.py` defines all six custom exceptions
- Empty placeholder files exist for every module

**Todo List:**
1. Create folder tree: `models/`, `services/`, `utils/`, `data/`, `tests/`, `pages/`
2. Add `__init__.py` to `models/`, `services/`, `utils/`, `tests/`
3. Create `models/exceptions.py` with all six exception classes
4. Create empty placeholder files for every module listed in the architecture

**Status:** [ ] pending

---

### Sub-Task 2 — Data Models: Student and Room
**Intent:** Implement the `Student` and `Room` dataclasses with serialisation support.

**Expected Outcomes:**
- `Student` and `Room` objects can be created with all required fields
- `to_dict()` and `from_dict()` work correctly for both classes
- All fields have correct types and default values

**Todo List:**
1. Implement `models/room.py`: fields, `to_dict`, `from_dict`
2. Implement `models/student.py`: fields, `to_dict`, `from_dict`
3. Write `tests/test_student.py`: round-trip serialisation tests
4. Write `tests/test_room.py`: round-trip serialisation tests

**Relevant Context:**
- See Data Model section above for exact field names and types
- `admission_date` is stored as an ISO date string in JSON, converted to `datetime.date` in Python

**Status:** [ ] pending

---

### Sub-Task 3 — Validators
**Intent:** Implement all pure validation functions.

**Expected Outcomes:**
- Each validator raises `ValidationError` with a clear message on invalid input
- Each validator passes silently on valid input

**Todo List:**
1. Implement `utils/validators.py` with all five validators
2. Write `tests/test_validators.py` covering valid and invalid cases for each function

**Relevant Context:**
- Phone: exactly 10 digits, numeric only
- Email: optional — validate format only if a non-empty string is provided
- Date: must be today or in the past (use `datetime.date.today()`)
- `ValidationError` is imported from `models/exceptions.py`

**Status:** [ ] pending

---

### Sub-Task 4 — DataManager
**Intent:** Implement file I/O for persisting and loading student and room records.

**Expected Outcomes:**
- `load_students` and `load_rooms` return empty lists when files do not exist
- `save_students` and `save_rooms` write correctly formatted JSON
- A save followed by a load returns identical objects

**Todo List:**
1. Implement `services/data_manager.py` with four methods
2. Ensure the `data/` directory is created if it does not exist
3. Write `tests/test_data_manager.py` using `tmp_path` for isolation

**Relevant Context:**
- Use Python's built-in `json` module
- Use `Student.from_dict` and `Room.from_dict` when loading
- Use `Student.to_dict` and `Room.to_dict` when saving

**Status:** [ ] pending

---

### Sub-Task 5 — HostelManager: Room Operations
**Intent:** Implement all room-level business logic (add, update, delete, view).

**Expected Outcomes:**
- Admin can add a room; duplicate room numbers raise `DuplicateRoomError`
- Admin can update room capacity; reduction blocked if it would drop below active occupancy
- Admin can delete a room; blocked if students are assigned to it
- `get_room_summary` returns correct occupancy counts

**Todo List:**
1. Implement `HostelManager.__init__` to accept and store a `DataManager` instance
2. Implement `add_room`, `update_room`, `delete_room`, `get_all_rooms`, `get_room_summary`
3. Write `tests/test_hostel_manager.py` room-operation tests

**Relevant Context:**
- `HostelManager` calls `DataManager.save_rooms` after every mutation
- Active occupancy = count of students with `is_staying=True` in that room

**Status:** [ ] pending

---

### Sub-Task 6 — HostelManager: Student Operations
**Intent:** Implement all student-level business logic (add, get, update, delete,
check-in, check-out, change room, filter).

**Expected Outcomes:**
- Adding a student validates fields, checks room exists and has capacity
- Updating a student re-validates changed fields
- Changing room validates new room exists and has capacity
- Check-out sets `is_staying=False`; check-in sets `is_staying=True` (room capacity re-checked)
- Filter returns correct subsets by room, gender, and status
- All failure scenarios raise the correct named exception

**Todo List:**
1. Implement `add_student`, `get_student_by_id`, `get_all_students`
2. Implement `update_student`, `delete_student`
3. Implement `check_out_student`, `check_in_student`
4. Implement `change_room`
5. Implement `filter_students`
6. Extend `tests/test_hostel_manager.py` with student-operation tests

**Relevant Context:**
- Call `validators.py` functions before any mutation
- Call `DataManager.save_students` after every mutation
- Business rules 1–10 from the Business Rules section all apply here

**Status:** [ ] pending

---

### Sub-Task 7 — Streamlit App Shell and Home Page
**Intent:** Set up the Streamlit multi-page app and the home/landing page with summary stats.

**Expected Outcomes:**
- `streamlit run app.py` launches without errors
- Home page shows title, description, and live summary stats
- `HostelManager` is initialised once in `st.session_state` and shared across pages

**Todo List:**
1. Implement `app.py`: initialise `DataManager` and `HostelManager` in `st.session_state`
2. Display summary stats: total rooms, total students, currently staying, available beds
3. Verify navigation sidebar shows all pages

**Relevant Context:**
- Use `st.session_state` key `"manager"` for the `HostelManager` instance
- All pages access `st.session_state["manager"]` — never create a new instance per page

**Status:** [ ] pending

---

### Sub-Task 8 — Streamlit Pages: Room Management
**Intent:** Implement `pages/1_Manage_Rooms.py`.

**Expected Outcomes:**
- Admin can add a room via a form
- All rooms display in a table with occupancy and available beds
- Admin can edit capacity or delete a room (with guard against deletion if occupied)
- Exceptions surface as `st.error` messages

**Todo List:**
1. Build the Add Room form
2. Build the rooms table with edit and delete controls
3. Wire all controls to `HostelManager` methods
4. Handle and display all relevant exceptions

**Status:** [ ] pending

---

### Sub-Task 9 — Streamlit Pages: Add Student
**Intent:** Implement `pages/2_Add_Student.py`.

**Expected Outcomes:**
- Admin can fill in all student fields and submit
- Room selectbox only shows existing rooms
- Success and error feedback displayed correctly

**Todo List:**
1. Build the Add Student form with all fields
2. Populate room selectbox from `HostelManager.get_all_rooms`
3. Wire form submission to `HostelManager.add_student`
4. Handle and display all relevant exceptions

**Status:** [ ] pending

---

### Sub-Task 10 — Streamlit Pages: View and Filter Students
**Intent:** Implement `pages/3_View_Students.py`.

**Expected Outcomes:**
- All students shown in a dataframe
- Sidebar filters for room, gender, and status work correctly
- Check-In and Check-Out buttons work per row

**Todo List:**
1. Build sidebar filter controls
2. Call `HostelManager.filter_students` and display results
3. Add per-row Check-In and Check-Out buttons wired to `HostelManager`
4. Handle and display all relevant exceptions

**Status:** [ ] pending

---

### Sub-Task 11 — Streamlit Pages: Edit Student and Delete Student
**Intent:** Implement `pages/4_Edit_Student.py` and `pages/5_Delete_Student.py`.

**Expected Outcomes:**
- Edit page pre-fills current values; saves changes correctly; supports room change
- Delete page requires confirmation checkbox before allowing deletion

**Todo List:**
1. Build Edit Student page: student selector, pre-filled form, save + change-room controls
2. Build Delete Student page: selector, confirmation checkbox, delete button
3. Wire all controls to `HostelManager` methods
4. Handle and display all relevant exceptions

**Status:** [ ] pending

---

### Sub-Task 12 — Final Integration and Smoke Test
**Intent:** Verify the full application works end-to-end and all tests pass.

**Expected Outcomes:**
- `pytest tests/` passes with no failures
- Full user journey works: add room → add student → view → edit → check out → delete
- `students.json` and `rooms.json` persist correctly between page navigations

**Todo List:**
1. Run `pytest tests/` and fix any failures
2. Manually walk through the full user journey in the browser
3. Verify JSON files are written and read correctly across a simulated restart

**Status:** [ ] pending
