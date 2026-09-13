from fastapi import APIRouter, Depends

from ..schemas import EventCreate, EventOut, EventPatch
from .common import find_event, get_store

router = APIRouter(prefix="/api", tags=["events"])


def _event_out(event: dict) -> dict:
    return {key: event[key] for key in ("id", "course_id", "title", "type", "start_at", "end_at", "location")}


@router.post("/events", response_model=EventOut, status_code=201)
def create_event(payload: EventCreate, store=Depends(get_store)):
    record = payload.model_dump(exclude_none=True)
    record["id"] = payload.id or store.next_id("e")
    store.data["events"].append(record)
    return _event_out(record)


@router.patch("/events/{event_id}", response_model=EventOut)
def patch_event(event_id: str, payload: EventPatch, store=Depends(get_store)):
    record = find_event(store, event_id)
    record.update(payload.model_dump(exclude_unset=True))
    return _event_out(record)
