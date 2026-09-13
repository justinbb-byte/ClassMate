from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, Request

from ..mock.fixture import MockStore
from ..progress import compute_progress


def get_store(request: Request) -> MockStore:
    store = getattr(request.app.state, "mock_store", None)
    if store is None:
        raise HTTPException(status_code=503, detail="Mock store is unavailable")
    return store


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def assignment_out(record: dict, now: datetime | None = None) -> dict:
    progress = compute_progress(record, now)
    return {
        "id": record["id"],
        "course_id": record["course_id"],
        "title": record["title"],
        "assigned_at": record["assigned_at"],
        "due_at": record["due_at"],
        "grade_weight_pct": record["grade_weight_pct"],
        "total_words": record["total_words"],
        "status": record["status"],
        "milestones": [
            {
                "id": m["id"],
                "name": m["name"],
                "weight": m["weight"],
                "target_words": m["target_words"],
                "words": m["words"],
                "done": m["done"],
                "done_at": m["done_at"],
            }
            for m in sorted(record.get("milestones", []), key=lambda item: item.get("seq", 0))
        ],
        "progress": {
            "actual_pct": progress["actualPct"],
            "expected_pct": progress["expectedPct"],
            "gap": progress["gap"],
            "band": progress["band"],
            "priority_score": progress["priorityScore"],
            "days_left": progress["daysLeft"],
            "words_left": progress["wordsLeft"],
        },
    }


def state_out(store: MockStore) -> dict[str, Any]:
    now = now_utc()
    return {
        "student": store.data["student"],
        "courses": store.data["courses"],
        "assignments": [
            assignment_out(a, now)
            for a in sorted(store.data["assignments"], key=lambda item: item["due_at"])
        ],
        "events": [
            {key: event[key] for key in ("id", "course_id", "title", "type", "start_at", "end_at", "location")}
            for event in sorted(store.data["events"], key=lambda item: item["start_at"])
        ],
        "updates": [
            {key: update[key] for key in ("id", "course_id", "kind", "at", "text")}
            for update in sorted(store.data["updates"], key=lambda item: item["at"], reverse=True)
        ],
    }


def find_assignment(store: MockStore, assignment_id: str) -> dict:
    for assignment in store.data["assignments"]:
        if assignment["id"] == assignment_id:
            return assignment
    raise HTTPException(status_code=404, detail="Assignment not found")


def find_event(store: MockStore, event_id: str) -> dict:
    for event in store.data["events"]:
        if event["id"] == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")


def find_milestone(store: MockStore, milestone_id: str) -> tuple[dict, dict]:
    for assignment in store.data["assignments"]:
        for milestone in assignment.get("milestones", []):
            if milestone["id"] == milestone_id:
                return assignment, milestone
    raise HTTPException(status_code=404, detail="Milestone not found")
