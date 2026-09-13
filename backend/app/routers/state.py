from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from ..schemas import AssignmentOut, EventOut, StateOut
from .common import assignment_out, find_assignment, get_store, state_out

router = APIRouter(prefix="/api", tags=["read"])


@router.get("/state", response_model=StateOut)
def get_state(store=Depends(get_store)):
    return state_out(store)


@router.get("/assignments", response_model=list[AssignmentOut])
def list_assignments(
    status: str | None = None,
    course_id: str | None = Query(default=None, alias="courseId"),
    store=Depends(get_store),
):
    records = store.data["assignments"]
    if status:
        records = [record for record in records if record["status"] == status]
    if course_id:
        records = [record for record in records if record["course_id"] == course_id]
    return [assignment_out(record) for record in sorted(records, key=lambda item: item["due_at"])]


@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
def get_assignment(assignment_id: str, store=Depends(get_store)):
    return assignment_out(find_assignment(store, assignment_id))


@router.get("/events", response_model=list[EventOut])
def list_events(
    from_: datetime | None = Query(default=None, alias="from"),
    to: datetime | None = None,
    store=Depends(get_store),
):
    start = from_ or datetime.now(timezone.utc)
    end = to or (start + timedelta(days=7))
    if start.tzinfo is None or end.tzinfo is None:
        raise HTTPException(status_code=422, detail="from and to must include a timezone offset")
    records = [event for event in store.data["events"] if event["start_at"] >= start and event["start_at"] <= end]
    return [
        {key: event[key] for key in ("id", "course_id", "title", "type", "start_at", "end_at", "location")}
        for event in sorted(records, key=lambda item: item["start_at"])
    ]
