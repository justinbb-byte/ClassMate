from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def to_camel(value: str) -> str:
    head, *tail = value.split("_")
    return head + "".join(part[:1].upper() + part[1:] for part in tail)


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        serialize_by_alias=True,
        extra="ignore",
    )


def require_aware(value: datetime | None) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError("timestamps must be ISO 8601 values with a timezone offset")
    return value


class StudentOut(CamelModel):
    id: str
    name: str
    timezone: str


class CourseOut(CamelModel):
    id: str
    code: str
    name: str


class ProgressOut(CamelModel):
    actual_pct: float
    expected_pct: float
    gap: float
    band: Literal["green", "amber", "red"]
    priority_score: float
    days_left: float
    words_left: int


class MilestoneOut(CamelModel):
    id: str
    name: str
    weight: int
    target_words: int
    words: int
    done: bool
    done_at: datetime | None

    _aware_done_at = field_validator("done_at")(require_aware)


class AssignmentOut(CamelModel):
    id: str
    course_id: str
    title: str
    assigned_at: datetime
    due_at: datetime
    grade_weight_pct: int
    total_words: int
    status: Literal["not_started", "in_progress", "submitted"]
    milestones: list[MilestoneOut]
    progress: ProgressOut

    _aware_dates = field_validator("assigned_at", "due_at")(require_aware)


class EventOut(CamelModel):
    id: str
    course_id: str
    title: str
    type: Literal["lecture", "tutorial", "lab", "deadline", "consultation"]
    start_at: datetime
    end_at: datetime
    location: str

    _aware_dates = field_validator("start_at", "end_at")(require_aware)


class UpdateOut(CamelModel):
    id: str
    course_id: str
    kind: Literal["announcement", "material", "grade"]
    at: datetime
    text: str

    _aware_at = field_validator("at")(require_aware)


class StateOut(CamelModel):
    student: StudentOut
    courses: list[CourseOut]
    assignments: list[AssignmentOut]
    events: list[EventOut]
    updates: list[UpdateOut]


class MilestoneInput(CamelModel):
    id: str | None = None
    name: str
    weight: int
    target_words: int = 0
    words: int = 0
    done: bool = False
    done_at: datetime | None = None
    seq: int | None = None

    _aware_done_at = field_validator("done_at")(require_aware)


class AssignmentCreate(CamelModel):
    id: str | None = None
    course_id: str
    title: str
    assigned_at: datetime
    due_at: datetime
    grade_weight_pct: int = 0
    total_words: int = 0
    status: Literal["not_started", "in_progress", "submitted"] = "not_started"
    milestones: list[MilestoneInput] = Field(default_factory=list)
    external_id: str | None = None

    _aware_dates = field_validator("assigned_at", "due_at")(require_aware)


class AssignmentPatch(CamelModel):
    title: str | None = None
    course_id: str | None = None
    assigned_at: datetime | None = None
    due_at: datetime | None = None
    grade_weight_pct: int | None = None
    total_words: int | None = None
    status: Literal["not_started", "in_progress", "submitted"] | None = None

    _aware_dates = field_validator("assigned_at", "due_at")(require_aware)


class MilestonePatch(CamelModel):
    name: str | None = None
    words: int | None = None
    done: bool | None = None


class EventCreate(CamelModel):
    id: str | None = None
    course_id: str
    title: str
    type: Literal["lecture", "tutorial", "lab", "deadline", "consultation"]
    start_at: datetime
    end_at: datetime
    location: str = ""
    external_id: str | None = None

    _aware_dates = field_validator("start_at", "end_at")(require_aware)


class EventPatch(CamelModel):
    title: str | None = None
    course_id: str | None = None
    type: Literal["lecture", "tutorial", "lab", "deadline", "consultation"] | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    location: str | None = None

    _aware_dates = field_validator("start_at", "end_at")(require_aware)


class ChatRequest(CamelModel):
    message: str
    student_id: str


class ChatCard(CamelModel):
    title: str
    meta: str
    band: Literal["green", "amber", "red"] = "green"
    index: int | None = None


class ChatResponse(CamelModel):
    text: str
    cards: list[ChatCard] = Field(default_factory=list)


class IngestAssignment(MilestoneInput):
    pass


class IngestAssignmentItem(AssignmentCreate):
    external_id: str


class IngestEventItem(EventCreate):
    external_id: str


class IngestUpdateItem(CamelModel):
    id: str | None = None
    course_id: str
    kind: Literal["announcement", "material", "grade"]
    at: datetime
    text: str
    external_id: str

    _aware_at = field_validator("at")(require_aware)


class IngestBatch(CamelModel):
    items: list[dict]


class IngestResult(CamelModel):
    created: int
    updated: int
    skipped: int
    errors: list[dict]
    warnings: list[str] = Field(default_factory=list)
