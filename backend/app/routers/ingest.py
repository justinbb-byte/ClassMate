from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException

from ..config import get_settings
from ..schemas import IngestResult
from .common import get_store

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


def require_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().ingest_api_key
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


def _result() -> dict:
    return {"created": 0, "updated": 0, "skipped": 0, "errors": [], "warnings": []}


def _parse_aware(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone offset")
    return parsed


def _weights_warning(item: dict, warnings: list[str]) -> None:
    weights = [m.get("weight", 0) for m in item.get("milestones", [])]
    if weights and sum(weights) != 100:
        warnings.append(f"milestone weights for {item.get('external_id', '<unknown>')} sum to {sum(weights)}, not 100")


def _incoming_milestones(item: dict, store, existing: list[dict] | None = None) -> list[dict]:
    milestones = []
    existing_by_seq = {m.get("seq"): m for m in (existing or [])}
    for seq, milestone in enumerate(item.get("milestones", []), 1):
        milestones.append({
            "id": milestone.get("id") or existing_by_seq.get(milestone.get("seq", seq), {}).get("id") or store.next_id("m"),
            "seq": milestone.get("seq", seq),
            "name": milestone["name"],
            "weight": milestone["weight"],
            "target_words": milestone.get("targetWords", 0),
            "words": milestone.get("words", 0),
            "done": milestone.get("done", False),
            "done_at": _parse_aware(milestone["doneAt"]) if milestone.get("doneAt") else None,
        })
    return milestones


def _merge_milestones(existing: list[dict], incoming: list[dict]) -> list[dict]:
    """Merge n8n structure without allowing it to erase student progress."""
    previous = {m["id"]: m for m in existing}
    merged = []
    for item in incoming:
        old = previous.get(item["id"])
        if old and old.get("done") and not item.get("done"):
            item["done"] = True
            item["done_at"] = old.get("done_at")
        merged.append(item)
    return merged


@router.post("/assignments", response_model=IngestResult)
def ingest_assignments(payload: dict, _: None = Depends(require_key), store=Depends(get_store)):
    result = _result()
    for index, item in enumerate(payload.get("items", [])):
        external_id = item.get("externalId") or item.get("external_id")
        try:
            if not external_id:
                raise ValueError("externalId is required")
            _weights_warning(item, result["warnings"])
            existing = next((a for a in store.data["assignments"] if a.get("external_id") == external_id), None)
            if existing is None:
                record = {
                    "id": item.get("id") or store.next_id("a"),
                    "external_id": external_id,
                    "course_id": item["courseId"],
                    "title": item["title"],
                    "assigned_at": _parse_aware(item["assignedAt"]),
                    "due_at": _parse_aware(item["dueAt"]),
                    "grade_weight_pct": item.get("gradeWeightPct", 0),
                    "total_words": item.get("totalWords", 0),
                    "status": item.get("status", "not_started"),
                    "milestones": [],
                }
                record["milestones"] = _incoming_milestones(item, store)
                store.data["assignments"].append(record)
                result["created"] += 1
            else:
                before = repr(existing)
                existing.update({"course_id": item["courseId"], "title": item["title"], "assigned_at": _parse_aware(item["assignedAt"]), "due_at": _parse_aware(item["dueAt"]), "grade_weight_pct": item.get("gradeWeightPct", 0), "total_words": item.get("totalWords", 0), "status": item.get("status", existing["status"])})
                if "milestones" in item:
                    existing["milestones"] = _merge_milestones(existing.get("milestones", []), _incoming_milestones(item, store, existing.get("milestones", [])))
                if repr(existing) == before:
                    result["skipped"] += 1
                else:
                    result["updated"] += 1
        except (KeyError, TypeError, ValueError) as exc:
            result["errors"].append({"index": index, "externalId": external_id, "reason": str(exc)})
    return result


@router.post("/events", response_model=IngestResult)
def ingest_events(payload: dict, _: None = Depends(require_key), store=Depends(get_store)):
    result = _result()
    for index, item in enumerate(payload.get("items", [])):
        external_id = item.get("externalId") or item.get("external_id")
        try:
            if not external_id:
                raise ValueError("externalId is required")
            existing = next((e for e in store.data["events"] if e.get("external_id") == external_id), None)
            record = {"id": item.get("id") or store.next_id("e"), "external_id": external_id, "course_id": item["courseId"], "title": item["title"], "type": item["type"], "start_at": _parse_aware(item["startAt"]), "end_at": _parse_aware(item["endAt"]), "location": item.get("location", "")}
            if existing is None:
                store.data["events"].append(record); result["created"] += 1
            elif all(existing.get(key) == value for key, value in record.items() if key not in {"id", "external_id"}):
                result["skipped"] += 1
            else:
                existing.update({key: value for key, value in record.items() if key not in {"id", "external_id"}}); result["updated"] += 1
        except (KeyError, TypeError, ValueError) as exc:
            result["errors"].append({"index": index, "externalId": external_id, "reason": str(exc)})
    return result


@router.post("/updates", response_model=IngestResult)
def ingest_updates(payload: dict, _: None = Depends(require_key), store=Depends(get_store)):
    result = _result()
    for index, item in enumerate(payload.get("items", [])):
        external_id = item.get("externalId") or item.get("external_id")
        try:
            if not external_id:
                raise ValueError("externalId is required")
            existing = next((u for u in store.data["updates"] if u.get("external_id") == external_id), None)
            record = {"id": item.get("id") or store.next_id("u"), "external_id": external_id, "course_id": item["courseId"], "kind": item["kind"], "at": _parse_aware(item["at"]), "text": item["text"]}
            if existing is None:
                store.data["updates"].append(record); result["created"] += 1
            elif all(existing.get(key) == value for key, value in record.items() if key not in {"id", "external_id"}):
                result["skipped"] += 1
            else:
                existing.update({key: value for key, value in record.items() if key not in {"id", "external_id"}}); result["updated"] += 1
        except (KeyError, TypeError, ValueError) as exc:
            result["errors"].append({"index": index, "externalId": external_id, "reason": str(exc)})
    return result
