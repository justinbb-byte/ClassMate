from copy import deepcopy
from datetime import datetime, timedelta
from itertools import count
from zoneinfo import ZoneInfo


MYT = ZoneInfo("Asia/Kuala_Lumpur")


def _iso(offset_days: int, hour: int = 23, minute: int = 59) -> datetime:
    value = datetime.now(MYT) + timedelta(days=offset_days)
    return value.replace(hour=hour, minute=minute, second=0, microsecond=0)


def build_fixture() -> dict:
    """Build a fresh relative-date fixture for every process."""

    return {
        "student": {"id": "student_001", "name": "Wan", "timezone": "Asia/Kuala_Lumpur"},
        "courses": [
            {"id": "c1", "code": "BDA2043", "name": "Big Data Analytics"},
            {"id": "c2", "code": "DDS2113", "name": "Data Visualisation"},
            {"id": "c3", "code": "CSC1024", "name": "Database Management"},
        ],
        "assignments": [
            {
                "id": "a1", "course_id": "c1", "title": "Hadoop cluster case study",
                "assigned_at": _iso(-12), "due_at": _iso(3, 17, 0), "grade_weight_pct": 30,
                "total_words": 2000, "status": "in_progress", "external_id": "fixture-a1",
                "milestones": [
                    {"id": "m1", "seq": 1, "name": "Read the brief and pick a case", "weight": 10, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-11)},
                    {"id": "m2", "seq": 2, "name": "Background research", "weight": 25, "target_words": 500, "words": 520, "done": True, "done_at": _iso(-7)},
                    {"id": "m3", "seq": 3, "name": "Write the introduction", "weight": 15, "target_words": 300, "words": 140, "done": False, "done_at": None},
                    {"id": "m4", "seq": 4, "name": "Analysis and findings", "weight": 30, "target_words": 900, "words": 0, "done": False, "done_at": None},
                    {"id": "m5", "seq": 5, "name": "Conclusion", "weight": 12, "target_words": 300, "words": 0, "done": False, "done_at": None},
                    {"id": "m6", "seq": 6, "name": "Review and submit", "weight": 8, "target_words": 0, "words": 0, "done": False, "done_at": None},
                ],
            },
            {
                "id": "a2", "course_id": "c2", "title": "Qlik Sense sales dashboard",
                "assigned_at": _iso(-6), "due_at": _iso(9, 23, 59), "grade_weight_pct": 25,
                "total_words": 800, "status": "in_progress", "external_id": "fixture-a2",
                "milestones": [
                    {"id": "m7", "seq": 1, "name": "Clean the dataset", "weight": 20, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-4)},
                    {"id": "m8", "seq": 2, "name": "Build the data model", "weight": 25, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-2)},
                    {"id": "m9", "seq": 3, "name": "Design the sheets", "weight": 30, "target_words": 0, "words": 0, "done": False, "done_at": None},
                    {"id": "m10", "seq": 4, "name": "Write the rationale", "weight": 17, "target_words": 800, "words": 210, "done": False, "done_at": None},
                    {"id": "m11", "seq": 5, "name": "Review and submit", "weight": 8, "target_words": 0, "words": 0, "done": False, "done_at": None},
                ],
            },
            {
                "id": "a3", "course_id": "c3", "title": "Library system SQL exercises",
                "assigned_at": _iso(-2), "due_at": _iso(1, 12, 0), "grade_weight_pct": 10,
                "total_words": 0, "status": "in_progress", "external_id": "fixture-a3",
                "milestones": [
                    {"id": "m12", "seq": 1, "name": "Questions 1 to 5", "weight": 40, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-1)},
                    {"id": "m13", "seq": 2, "name": "Questions 6 to 10", "weight": 40, "target_words": 0, "words": 0, "done": False, "done_at": None},
                    {"id": "m14", "seq": 3, "name": "Check and submit", "weight": 20, "target_words": 0, "words": 0, "done": False, "done_at": None},
                ],
            },
            {
                "id": "a4", "course_id": "c1", "title": "Reading response: MapReduce",
                "assigned_at": _iso(-20), "due_at": _iso(-3, 17, 0), "grade_weight_pct": 5,
                "total_words": 500, "status": "submitted", "external_id": "fixture-a4",
                "milestones": [
                    {"id": "m15", "seq": 1, "name": "Read and annotate", "weight": 40, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-6)},
                    {"id": "m16", "seq": 2, "name": "Write response", "weight": 50, "target_words": 500, "words": 540, "done": True, "done_at": _iso(-4)},
                    {"id": "m17", "seq": 3, "name": "Submit", "weight": 10, "target_words": 0, "words": 0, "done": True, "done_at": _iso(-3)},
                ],
            },
        ],
        "events": [
            {"id": "e1", "course_id": "c1", "title": "BDA lecture", "type": "lecture", "start_at": _iso(0, 9, 0), "end_at": _iso(0, 11, 0), "location": "UW2-4", "external_id": "fixture-e1"},
            {"id": "e2", "course_id": "c3", "title": "Database lab", "type": "lab", "start_at": _iso(0, 14, 0), "end_at": _iso(0, 16, 0), "location": "Lab 3A", "external_id": "fixture-e2"},
            {"id": "e3", "course_id": "c2", "title": "Qlik tutorial", "type": "tutorial", "start_at": _iso(1, 10, 0), "end_at": _iso(1, 12, 0), "location": "UW1-7", "external_id": "fixture-e3"},
            {"id": "e4", "course_id": "c1", "title": "Consultation with Dr Lim", "type": "consultation", "start_at": _iso(2, 15, 0), "end_at": _iso(2, 15, 30), "location": "Office 5-12", "external_id": "fixture-e4"},
            {"id": "e5", "course_id": "c2", "title": "Qlik lecture", "type": "lecture", "start_at": _iso(3, 9, 0), "end_at": _iso(3, 11, 0), "location": "UW2-1", "external_id": "fixture-e5"},
        ],
        "updates": [
            {"id": "u1", "course_id": "c1", "kind": "announcement", "at": _iso(-1, 16, 20), "text": "Dr Lim moved the case study deadline to Wednesday 5pm.", "external_id": "fixture-u1"},
            {"id": "u2", "course_id": "c2", "kind": "material", "at": _iso(-1, 9, 5), "text": "Week 9 slides on set analysis were uploaded.", "external_id": "fixture-u2"},
            {"id": "u3", "course_id": "c3", "kind": "grade", "at": _iso(-2, 21, 40), "text": "Quiz 2 marked: 17 out of 20.", "external_id": "fixture-u3"},
            {"id": "u4", "course_id": "c1", "kind": "announcement", "at": _iso(-3, 11, 0), "text": "Group sign-up sheet for the final project is open until Friday.", "external_id": "fixture-u4"},
            {"id": "u5", "course_id": "c2", "kind": "material", "at": _iso(-5, 14, 30), "text": "Sample dataset v2 replaced v1. Use the new file.", "external_id": "fixture-u5"},
        ],
    }


class MockStore:
    def __init__(self) -> None:
        self.data = build_fixture()
        self._ids = count(100)

    def next_id(self, prefix: str) -> str:
        return f"{prefix}{next(self._ids)}"

    def reset(self) -> None:
        self.data = build_fixture()

    def snapshot(self) -> dict:
        return deepcopy(self.data)
