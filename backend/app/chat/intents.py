from __future__ import annotations

import re
from datetime import datetime

from ..progress import compute_progress
from ..routers.common import assignment_out


def _fmt_due(value: datetime, now: datetime) -> str:
    hours = (value - now).total_seconds() / 3600
    when = value.strftime("%a %-I:%M %p")
    if hours < 0:
        return f"overdue since {when}"
    if hours < 24:
        return f"due today, {when}"
    if hours < 48:
        return f"due tomorrow, {when}"
    return f"due {when}"


def _card(title: str, meta: str, band: str = "green", index: int | None = None) -> dict:
    return {"title": title, "meta": meta, "band": band, "index": index}


def reply(message: str, state: dict, now: datetime) -> dict:
    """Return the same small response shape expected by the frontend."""

    query = message.lower()
    courses = {course["id"]: course for course in state["courses"]}
    live = [a for a in state["assignments"] if a["status"] != "submitted"]
    ranked = sorted(live, key=lambda a: compute_progress(a, now)["priorityScore"], reverse=True)

    if re.search(r"today|now|what should i do|start|plan", query):
        picks = ranked[:3]
        total_minutes = 0
        cards = []
        for index, assignment in enumerate(picks, 1):
            progress = compute_progress(assignment, now)
            next_milestone = next((m for m in assignment["milestones"] if not m["done"]), None)
            minutes = max(20, round(max((next_milestone or {}).get("target_words", 0) - (next_milestone or {}).get("words", 0), 0) / 220 * 60) or 40)
            total_minutes += minutes
            cards.append(_card(
                next_milestone["name"] if next_milestone else "Review and submit",
                f"{courses[assignment['course_id']]['code']} · {minutes} min · {_fmt_due(assignment['due_at'], now)}",
                progress["band"], index,
            ))
        return {"text": f"Three things, about {round(total_minutes / 60, 1)} hours in total. Start at the top.", "cards": cards}

    if re.search(r"catch me up|missed|what.?s new|update|happened", query):
        return {
            "text": "Here is what changed while you were away.",
            "cards": [
                _card(update["text"], f"{courses[update['course_id']]['code']} · {update['at'].strftime('%a %-I:%M %p')}", "amber" if update["kind"] == "announcement" else "green")
                for update in state["updates"][:4]
            ],
        }

    if re.search(r"behind|risk|worried|stress|panic", query):
        late = [(a, compute_progress(a, now)) for a in ranked if compute_progress(a, now)["gap"] < -10]
        if not late:
            return {"text": "Nothing is behind pace right now. You have more room than it feels like.", "cards": []}
        return {
            "text": f"{len(late)} task{'s are' if len(late) != 1 else ' is'} behind pace. The fix is usually one focused sitting.",
            "cards": [_card(a["title"], f"{round(-p['gap'])}% behind · {_fmt_due(a['due_at'], now)}", p["band"]) for a, p in late],
        }

    if re.search(r"due|deadline|when", query):
        soon = sorted(live, key=lambda a: a["due_at"])[:4]
        return {
            "text": "Your next deadlines.",
            "cards": [_card(a["title"], f"{courses[a['course_id']]['code']} · {_fmt_due(a['due_at'], now)}", compute_progress(a, now)["band"]) for a in soon],
        }

    if re.search(r"break|smaller|step", query):
        if not ranked:
            return {"text": "Nothing open to break down.", "cards": []}
        top = ranked[0]
        remaining = [m for m in top["milestones"] if not m["done"]][:4]
        return {"text": f"{top['title']}, broken into what is left.", "cards": [_card(m["name"], f"{max(m['target_words'] - m['words'], 0)} words left · worth {m['weight']}%", "green", i) for i, m in enumerate(remaining, 1)]}

    for course in state["courses"]:
        if course["code"].lower() in query or course["name"].lower() in query:
            tasks = [a for a in live if a["course_id"] == course["id"]]
            return {"text": f"{course['code']} has {len(tasks)} open task{'s' if len(tasks) != 1 else ''}.", "cards": [_card(a["title"], f"{round(compute_progress(a, now)['actualPct'])}% done · {_fmt_due(a['due_at'], now)}", compute_progress(a, now)["band"]) for a in tasks]}

    return {"text": "I can plan your day, catch you up, list deadlines, or break a task into steps.", "cards": []}
