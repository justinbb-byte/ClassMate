from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.progress import compute_progress
from app.routers.ingest import require_key




@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_state_is_camel_case_and_timestamps_are_aware(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    body = response.json()
    assert {"student", "courses", "assignments", "events", "updates"} <= body.keys()
    assignment = body["assignments"][0]
    assert "courseId" in assignment and "course_id" not in assignment
    assert "progress" in assignment
    assert datetime.fromisoformat(assignment["dueAt"]).utcoffset() is not None
    assert datetime.fromisoformat(assignment["milestones"][0]["doneAt"]).utcoffset() is not None


def test_state_is_sorted_and_milestones_nested(client):
    body = client.get("/api/state").json()
    due_dates = [datetime.fromisoformat(item["dueAt"]) for item in body["assignments"]]
    assert due_dates == sorted(due_dates)
    assert all("milestones" in item for item in body["assignments"])
    assert "milestones" not in body


def test_done_stamps_and_clears_done_at(client):
    response = client.patch("/api/milestones/m3", json={"done": True})
    assert response.status_code == 200
    milestone = next(item for item in response.json()["milestones"] if item["id"] == "m3")
    assert milestone["done"] is True
    assert milestone["doneAt"] is not None
    response = client.patch("/api/milestones/m3", json={"done": False})
    assert response.json()["milestones"][2]["doneAt"] is None


def test_progress_divide_by_zero_guard():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    result = compute_progress({"assigned_at": now, "due_at": now, "status": "not_started", "grade_weight_pct": 1, "milestones": []}, now)
    assert result["expectedPct"] == 0
    assert result["band"] == "green"


def test_ingest_requires_key_and_is_idempotent(client, monkeypatch):
    monkeypatch.setenv("INGEST_API_KEY", "test-key")
    payload = {"items": [{"externalId": "test-ext", "courseId": "c1", "title": "Test", "assignedAt": "2026-09-13T09:00:00+08:00", "dueAt": "2026-09-20T17:00:00+08:00", "status": "not_started", "milestones": []}]}
    assert client.post("/api/ingest/assignments", json=payload).status_code == 401

    app.dependency_overrides[require_key] = lambda: None
    try:
        first = client.post("/api/ingest/assignments", json=payload)
        second = client.post("/api/ingest/assignments", json=payload)
        assert first.json()["created"] == 1
        assert second.json()["skipped"] == 1
    finally:
        app.dependency_overrides.pop(require_key, None)
