"""Pure progress and prioritisation functions shared by API and chat."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _value(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("All timestamps must include a timezone offset")
    return value


def compute_progress(assignment: Any, now: datetime | None = None) -> dict[str, float | str]:
    """Compute the frozen frontend progress formula without database access."""

    current = _aware(now or datetime.now(timezone.utc))
    assigned_at = _aware(_value(assignment, "assigned_at", _value(assignment, "assignedAt")))
    due_at = _aware(_value(assignment, "due_at", _value(assignment, "dueAt")))
    status = _value(assignment, "status", "not_started")
    milestones = _value(assignment, "milestones", []) or []

    actual = 0.0
    words_left = 0
    for milestone in milestones:
        done = bool(_value(milestone, "done", False))
        weight = float(_value(milestone, "weight", 0) or 0)
        target_words = int(_value(milestone, "target_words", _value(milestone, "targetWords", 0)) or 0)
        words = int(_value(milestone, "words", 0) or 0)
        if done:
            actual += weight
        elif target_words > 0:
            actual += weight * min(max(words / target_words, 0), 1)
        words_left += max(target_words - words, 0) if not done else 0

    span_ms = max((due_at - assigned_at).total_seconds() * 1000, 1)
    elapsed = min(max((current - assigned_at).total_seconds() * 1000 / span_ms, 0), 1)
    expected = 100.0 if status == "submitted" else elapsed * 100
    gap = actual - expected
    days_left = (due_at - current).total_seconds() / 86400

    if status == "submitted":
        band = "green"
    elif (gap < -25) or (due_at < current):
        band = "red"
    elif gap < -10:
        band = "amber"
    else:
        band = "green"

    grade_weight = float(_value(assignment, "grade_weight_pct", _value(assignment, "gradeWeightPct", 0)) or 0)
    priority_score = -gap * 1.6 + max(0, 14 - days_left) * 4 + grade_weight * 0.3
    return {
        "actualPct": round(actual, 4),
        "expectedPct": round(expected, 4),
        "gap": round(gap, 4),
        "band": band,
        "priorityScore": round(priority_score, 4),
        "daysLeft": round(days_left, 4),
        "wordsLeft": words_left,
    }
