from datetime import timezone, datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from ..schemas import AssignmentCreate, AssignmentOut, AssignmentPatch, MilestonePatch
from .common import assignment_out, find_assignment, find_milestone, get_store, now_utc

router = APIRouter(prefix="/api", tags=["assignments"])


def _milestone_dict(item, index: int, store) -> dict:
    return {
        "id": item.id or store.next_id("m"),
        "seq": item.seq or index,
        "name": item.name,
        "weight": item.weight,
        "target_words": item.target_words,
        "words": item.words,
        "done": item.done,
        "done_at": item.done_at,
    }


@router.post("/assignments", response_model=AssignmentOut, status_code=201)
def create_assignment(payload: AssignmentCreate, store=Depends(get_store)):
    record = payload.model_dump(exclude_none=True)
    record["id"] = payload.id or store.next_id("a")
    record["external_id"] = payload.external_id
    record["milestones"] = [_milestone_dict(item, index, store) for index, item in enumerate(payload.milestones, 1)]
    store.data["assignments"].append(record)
    return assignment_out(record)


@router.patch("/assignments/{assignment_id}", response_model=AssignmentOut)
def patch_assignment(assignment_id: str, payload: AssignmentPatch, store=Depends(get_store)):
    record = find_assignment(store, assignment_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"assigned_at", "due_at"} and value.tzinfo is None:
            raise HTTPException(status_code=422, detail="timestamps must include a timezone offset")
        record[key] = value
    return assignment_out(record)


@router.patch("/milestones/{milestone_id}", response_model=AssignmentOut)
def patch_milestone(milestone_id: str, payload: MilestonePatch, store=Depends(get_store)):
    assignment, milestone = find_milestone(store, milestone_id)
    changes = payload.model_dump(exclude_unset=True)
    for key, value in changes.items():
        milestone[key] = value
    if "done" in changes:
        milestone["done_at"] = now_utc() if changes["done"] else None
    return assignment_out(assignment)
