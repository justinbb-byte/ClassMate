import React, { useState, useRef, useEffect, useMemo } from "react";
import {
  Sun, ListChecks, CalendarDays, MessageSquare, Send,
  Clock, MapPin, Check, ChevronRight, Flame, Sparkles,
} from "lucide-react";

/* ────────────────────────────────────────────────────────────────
   MOCK DATA  —  this is also the API contract.
   Backend: return exactly this shape from GET /api/state
   All timestamps are ISO 8601 strings.
   Dates are generated relative to "now" so the demo never goes stale;
   the real backend returns fixed ISO strings.
   ──────────────────────────────────────────────────────────────── */

const day = 86400000;
const iso = (offsetDays, hour = 23, min = 59) => {
  const d = new Date(Date.now() + offsetDays * day);
  d.setHours(hour, min, 0, 0);
  return d.toISOString();
};

const mockData = {
  student: { name: "Wan", timezone: "Asia/Kuala_Lumpur" },

  courses: [
    { id: "c1", code: "BDA2043", name: "Big Data Analytics" },
    { id: "c2", code: "DDS2113", name: "Data Visualisation" },
    { id: "c3", code: "CSC1024", name: "Database Management" },
  ],

  // status: "not_started" | "in_progress" | "submitted"
  assignments: [
    {
      id: "a1",
      courseId: "c1",
      title: "Hadoop cluster case study",
      assignedAt: iso(-12),
      dueAt: iso(3, 17, 0),
      gradeWeightPct: 30,
      totalWords: 2000,
      status: "in_progress",
      milestones: [
        { id: "m1", name: "Read the brief and pick a case", weight: 10, targetWords: 0, words: 0, done: true, doneAt: iso(-11) },
        { id: "m2", name: "Background research", weight: 25, targetWords: 500, words: 520, done: true, doneAt: iso(-7) },
        { id: "m3", name: "Write the introduction", weight: 15, targetWords: 300, words: 140, done: false, doneAt: null },
        { id: "m4", name: "Analysis and findings", weight: 30, targetWords: 900, words: 0, done: false, doneAt: null },
        { id: "m5", name: "Conclusion", weight: 12, targetWords: 300, words: 0, done: false, doneAt: null },
        { id: "m6", name: "Review and submit", weight: 8, targetWords: 0, words: 0, done: false, doneAt: null },
      ],
    },
    {
      id: "a2",
      courseId: "c2",
      title: "Qlik Sense sales dashboard",
      assignedAt: iso(-6),
      dueAt: iso(9, 23, 59),
      gradeWeightPct: 25,
      totalWords: 800,
      status: "in_progress",
      milestones: [
        { id: "m7", name: "Clean the dataset", weight: 20, targetWords: 0, words: 0, done: true, doneAt: iso(-4) },
        { id: "m8", name: "Build the data model", weight: 25, targetWords: 0, words: 0, done: true, doneAt: iso(-2) },
        { id: "m9", name: "Design the sheets", weight: 30, targetWords: 0, words: 0, done: false, doneAt: null },
        { id: "m10", name: "Write the rationale", weight: 17, targetWords: 800, words: 210, done: false, doneAt: null },
        { id: "m11", name: "Review and submit", weight: 8, targetWords: 0, words: 0, done: false, doneAt: null },
      ],
    },
    {
      id: "a3",
      courseId: "c3",
      title: "Library system SQL exercises",
      assignedAt: iso(-2),
      dueAt: iso(1, 12, 0),
      gradeWeightPct: 10,
      totalWords: 0,
      status: "in_progress",
      milestones: [
        { id: "m12", name: "Questions 1 to 5", weight: 40, targetWords: 0, words: 0, done: true, doneAt: iso(-1) },
        { id: "m13", name: "Questions 6 to 10", weight: 40, targetWords: 0, words: 0, done: false, doneAt: null },
        { id: "m14", name: "Check and submit", weight: 20, targetWords: 0, words: 0, done: false, doneAt: null },
      ],
    },
    {
      id: "a4",
      courseId: "c1",
      title: "Reading response: MapReduce",
      assignedAt: iso(-20),
      dueAt: iso(-3, 17, 0),
      gradeWeightPct: 5,
      totalWords: 500,
      status: "submitted",
      milestones: [
        { id: "m15", name: "Read and annotate", weight: 40, targetWords: 0, words: 0, done: true, doneAt: iso(-6) },
        { id: "m16", name: "Write response", weight: 50, targetWords: 500, words: 540, done: true, doneAt: iso(-4) },
        { id: "m17", name: "Submit", weight: 10, targetWords: 0, words: 0, done: true, doneAt: iso(-3) },
      ],
    },
  ],

  // type: "lecture" | "tutorial" | "lab" | "deadline" | "consultation"
  events: [
    { id: "e1", courseId: "c1", title: "BDA lecture", type: "lecture", startAt: iso(0, 9, 0), endAt: iso(0, 11, 0), location: "UW2-4" },
    { id: "e2", courseId: "c3", title: "Database lab", type: "lab", startAt: iso(0, 14, 0), endAt: iso(0, 16, 0), location: "Lab 3A" },
    { id: "e3", courseId: "c2", title: "Qlik tutorial", type: "tutorial", startAt: iso(1, 10, 0), endAt: iso(1, 12, 0), location: "UW1-7" },
    { id: "e4", courseId: "c1", title: "Consultation with Dr Lim", type: "consultation", startAt: iso(2, 15, 0), endAt: iso(2, 15, 30), location: "Office 5-12" },
    { id: "e5", courseId: "c2", title: "Qlik lecture", type: "lecture", startAt: iso(3, 9, 0), endAt: iso(3, 11, 0), location: "UW2-1" },
  ],

  // feed for "Catch me up"
  updates: [
    { id: "u1", at: iso(-1, 16, 20), courseId: "c1", kind: "announcement", text: "Dr Lim moved the case study deadline to Wednesday 5pm." },
    { id: "u2", at: iso(-1, 9, 5), courseId: "c2", kind: "material", text: "Week 9 slides on set analysis were uploaded." },
    { id: "u3", at: iso(-2, 21, 40), courseId: "c3", kind: "grade", text: "Quiz 2 marked: 17 out of 20." },
    { id: "u4", at: iso(-3, 11, 0), courseId: "c1", kind: "announcement", text: "Group sign-up sheet for the final project is open until Friday." },
    { id: "u5", at: iso(-5, 14, 30), courseId: "c2", kind: "material", text: "Sample dataset v2 replaced v1. Use the new file." },
  ],
};

/* ── palette ─────────────────────────────────────────────────── */
const C = {
  paper: "#F2F4F1",
  card: "#FFFFFF",
  ink: "#1C2620",
  muted: "#6D7A73",
  line: "#E0E5E0",
  calm: "#2E6F5E",
  calmSoft: "#E6F0EC",
  soon: "#B5711A",
  soonSoft: "#FAF0E0",
  now: "#A93A31",
  nowSoft: "#FAE9E7",
};

/* ── progress maths ──────────────────────────────────────────── */
function analyse(a) {
  const now = Date.now();
  const start = new Date(a.assignedAt).getTime();
  const due = new Date(a.dueAt).getTime();

  const actual = a.milestones.reduce((sum, m) => {
    if (m.done) return sum + m.weight;
    if (m.targetWords > 0) return sum + m.weight * Math.min(m.words / m.targetWords, 1);
    return sum;
  }, 0);

  const span = Math.max(due - start, 1);
  const elapsed = Math.min(Math.max((now - start) / span, 0), 1);
  const expected = a.status === "submitted" ? 100 : elapsed * 100;
  const gap = actual - expected;

  const hoursLeft = (due - now) / 3600000;
  const daysLeft = hoursLeft / 24;

  let band = "green";
  if (a.status !== "submitted") {
    if (gap < -25) band = "red";
    else if (gap < -10) band = "amber";
  }
  if (a.status !== "submitted" && hoursLeft < 0) band = "red";

  const next = a.milestones.find((m) => !m.done) || null;
  const wordsLeft = a.milestones.reduce(
    (s, m) => s + (m.done ? 0 : Math.max(m.targetWords - m.words, 0)), 0
  );

  // rough scheduling estimate: 220 words an hour of real writing
  const estMinutes = next
    ? Math.max(20, Math.round((Math.max(next.targetWords - next.words, 0) / 220) * 60) || 40)
    : 0;

  const score =
    a.status === "submitted" ? -999 : -gap * 1.6 + Math.max(0, 14 - daysLeft) * 4 + a.gradeWeightPct * 0.3;

  return { actual, expected, gap, daysLeft, hoursLeft, band, next, wordsLeft, estMinutes, score };
}

const tone = (band) =>
  band === "red" ? { fg: C.now, bg: C.nowSoft }
  : band === "amber" ? { fg: C.soon, bg: C.soonSoft }
  : { fg: C.calm, bg: C.calmSoft };

const fmtDue = (isoStr) => {
  const d = new Date(isoStr);
  const hrs = (d.getTime() - Date.now()) / 3600000;
  const time = d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
  if (hrs < 0) return `overdue since ${d.toLocaleDateString([], { weekday: "short" })}`;
  if (hrs < 24) return `due today, ${time}`;
  if (hrs < 48) return `due tomorrow, ${time}`;
  return `due ${d.toLocaleDateString([], { weekday: "long" })}, ${time}`;
};

const fmtTime = (isoStr) =>
  new Date(isoStr).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });

/* ── small pieces ────────────────────────────────────────────── */

function Ring({ pct, size = 46, band = "green" }) {
  const r = (size - 6) / 2;
  const circ = 2 * Math.PI * r;
  const t = tone(band);
  return (
    <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }} aria-hidden="true">
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={C.line} strokeWidth="4" />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none" stroke={t.fg} strokeWidth="4"
        strokeLinecap="round" strokeDasharray={circ}
        strokeDashoffset={circ * (1 - Math.min(pct, 100) / 100)}
      />
    </svg>
  );
}

function GapBar({ actual, expected, band }) {
  const t = tone(band);
  return (
    <div className="w-full">
      <div className="relative h-2 rounded-full" style={{ background: C.line }}>
        <div
          className="absolute left-0 top-0 h-2 rounded-full"
          style={{ width: `${Math.min(actual, 100)}%`, background: t.fg }}
        />
        <div
          className="absolute top-[-3px] w-[2px] h-[14px] rounded"
          style={{ left: `${Math.min(expected, 100)}%`, background: C.ink, opacity: 0.55 }}
          title="where you should be by now"
        />
      </div>
    </div>
  );
}

function TaskCard({ a, course, onOpen }) {
  const s = analyse(a);
  const t = tone(s.band);
  const done = a.status === "submitted";
  return (
    <button
      onClick={() => onOpen(a.id)}
      className="w-full text-left flex gap-3 p-4 rounded-xl transition-colors"
      style={{ background: C.card, border: `1px solid ${C.line}` }}
    >
      <div className="w-1 rounded-full shrink-0" style={{ background: done ? C.line : t.fg }} />
      <div className="flex-1 min-w-0">
        <div className="flex items-baseline gap-2">
          <span className="text-xs font-medium" style={{ color: C.muted }}>{course.code}</span>
          <span className="text-xs" style={{ color: C.muted }}>{a.gradeWeightPct}% of grade</span>
        </div>
        <div className="mt-0.5 text-[15px] font-medium truncate" style={{ color: C.ink }}>
          {a.title}
        </div>
        <div className="mt-2">
          <GapBar actual={s.actual} expected={s.expected} band={s.band} />
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs" style={{ color: C.muted }}>
          <span>{Math.round(s.actual)}% done</span>
          {!done && (
            <span style={{ color: t.fg }}>
              {s.gap >= -10 ? "on track" : `${Math.round(-s.gap)}% behind`}
            </span>
          )}
          <span>{done ? "submitted" : fmtDue(a.dueAt)}</span>
        </div>
      </div>
      <ChevronRight size={16} className="shrink-0 mt-1" style={{ color: C.line }} />
    </button>
  );
}

/* ── views ───────────────────────────────────────────────────── */

function TodayView({ data, onOpen, onAsk }) {
  const byId = Object.fromEntries(data.courses.map((c) => [c.id, c]));
  const live = data.assignments.filter((a) => a.status !== "submitted");
  const ranked = live.map((a) => ({ a, s: analyse(a) })).sort((x, y) => y.s.score - x.s.score);
  const hero = ranked[0];
  const todayEvents = data.events.filter(
    (e) => new Date(e.startAt).toDateString() === new Date().toDateString()
  );

  const heroTone = hero ? tone(hero.s.band) : tone("green");
  const today = new Date().toLocaleDateString([], { weekday: "long", day: "numeric", month: "long" });

  return (
    <div className="space-y-7">
      <div>
        <h1 className="text-[26px] leading-tight" style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}>
          Good to see you, {data.student.name}
        </h1>
        <p className="text-sm mt-1" style={{ color: C.muted }}>{today}</p>
      </div>

      {hero && (
        <section
          className="rounded-2xl p-5 sm:p-6 classmate-hero"
          style={{ background: C.card, border: `1px solid ${C.line}` }}
        >
          <div className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <span
                className="inline-block text-[11px] px-2 py-0.5 rounded-full font-medium"
                style={{ background: heroTone.bg, color: heroTone.fg }}
              >
                {hero.s.band === "red" ? "Needs attention" : hero.s.band === "amber" ? "Slipping a little" : "Next up"}
              </span>
              <h2
                className="mt-3 text-[21px] sm:text-[24px] leading-snug"
                style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}
              >
                {hero.s.next ? hero.s.next.name : "Review and submit"}
              </h2>
              <p className="mt-1.5 text-sm" style={{ color: C.muted }}>
                {byId[hero.a.courseId].code} · {hero.a.title}
              </p>
            </div>
            <div className="shrink-0 relative">
              <Ring pct={hero.s.actual} size={58} band={hero.s.band} />
              <span
                className="absolute inset-0 flex items-center justify-center text-[13px] font-semibold"
                style={{ color: C.ink }}
              >
                {Math.round(hero.s.actual)}
              </span>
            </div>
          </div>

          <div className="mt-5 flex flex-wrap gap-x-5 gap-y-2 text-sm" style={{ color: C.muted }}>
            <span className="flex items-center gap-1.5"><Clock size={14} /> about {hero.s.estMinutes} min</span>
            <span className="flex items-center gap-1.5"><Flame size={14} style={{ color: heroTone.fg }} /> {fmtDue(hero.a.dueAt)}</span>
            {hero.s.wordsLeft > 0 && <span>{hero.s.wordsLeft} words to go</span>}
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            <button
              onClick={() => onOpen(hero.a.id)}
              className="px-4 py-2 rounded-lg text-sm font-medium text-white"
              style={{ background: C.calm }}
            >
              Start this
            </button>
            <button
              onClick={() => onAsk("Break this into smaller steps")}
              className="px-4 py-2 rounded-lg text-sm font-medium"
              style={{ background: C.paper, color: C.ink, border: `1px solid ${C.line}` }}
            >
              Break it down
            </button>
          </div>
        </section>
      )}

      {todayEvents.length > 0 && (
        <section>
          <h3 className="text-sm font-medium mb-3" style={{ color: C.ink }}>On your timetable today</h3>
          <div className="space-y-2">
            {todayEvents.map((e) => (
              <div
                key={e.id}
                className="flex items-center gap-3 px-4 py-3 rounded-xl"
                style={{ background: C.card, border: `1px solid ${C.line}` }}
              >
                <span className="text-sm tabular-nums w-[72px] shrink-0" style={{ color: C.ink }}>
                  {fmtTime(e.startAt)}
                </span>
                <div className="min-w-0 flex-1">
                  <div className="text-sm truncate" style={{ color: C.ink }}>{e.title}</div>
                  <div className="text-xs flex items-center gap-1" style={{ color: C.muted }}>
                    <MapPin size={11} /> {e.location}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section>
        <h3 className="text-sm font-medium mb-3" style={{ color: C.ink }}>Everything open</h3>
        <div className="space-y-2">
          {ranked.map(({ a }) => (
            <TaskCard key={a.id} a={a} course={byId[a.courseId]} onOpen={onOpen} />
          ))}
        </div>
      </section>
    </div>
  );
}

function TasksView({ data, openId, onOpen }) {
  const byId = Object.fromEntries(data.courses.map((c) => [c.id, c]));
  const open = data.assignments.find((a) => a.id === openId);

  if (open) {
    const s = analyse(open);
    const t = tone(s.band);
    return (
      <div className="space-y-6">
        <button className="text-sm" style={{ color: C.calm }} onClick={() => onOpen(null)}>
          ← All tasks
        </button>
        <div>
          <p className="text-xs font-medium" style={{ color: C.muted }}>
            {byId[open.courseId].code} · {byId[open.courseId].name}
          </p>
          <h1 className="mt-1 text-[24px] leading-snug" style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}>
            {open.title}
          </h1>
          <p className="mt-1.5 text-sm" style={{ color: C.muted }}>
            {fmtDue(open.dueAt)} · worth {open.gradeWeightPct}% of the module
          </p>
        </div>

        <div className="rounded-xl p-5" style={{ background: C.card, border: `1px solid ${C.line}` }}>
          <div className="flex items-end justify-between mb-3">
            <div>
              <div className="text-[30px] leading-none" style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}>
                {Math.round(s.actual)}%
              </div>
              <div className="text-xs mt-1" style={{ color: C.muted }}>done</div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium" style={{ color: t.fg }}>
                {s.gap >= -10 ? "On track" : `${Math.round(-s.gap)}% behind pace`}
              </div>
              <div className="text-xs mt-1" style={{ color: C.muted }}>
                pace mark sits at {Math.round(s.expected)}%
              </div>
            </div>
          </div>
          <GapBar actual={s.actual} expected={s.expected} band={s.band} />
        </div>

        <div>
          <h3 className="text-sm font-medium mb-3" style={{ color: C.ink }}>Milestones</h3>
          <ol className="space-y-2">
            {open.milestones.map((m) => {
              const part = m.targetWords > 0 ? Math.min(m.words / m.targetWords, 1) : 0;
              return (
                <li
                  key={m.id}
                  className="flex items-center gap-3 px-4 py-3 rounded-xl"
                  style={{ background: C.card, border: `1px solid ${C.line}` }}
                >
                  <span
                    className="w-5 h-5 rounded-full shrink-0 flex items-center justify-center"
                    style={{
                      background: m.done ? C.calm : "transparent",
                      border: m.done ? "none" : `1.5px solid ${C.line}`,
                    }}
                  >
                    {m.done && <Check size={12} color="#fff" />}
                  </span>
                  <span
                    className="flex-1 text-sm"
                    style={{ color: m.done ? C.muted : C.ink, textDecoration: m.done ? "line-through" : "none" }}
                  >
                    {m.name}
                  </span>
                  {!m.done && m.targetWords > 0 && (
                    <span className="text-xs tabular-nums" style={{ color: part > 0 ? C.soon : C.muted }}>
                      {m.words}/{m.targetWords}w
                    </span>
                  )}
                  <span className="text-xs tabular-nums w-8 text-right" style={{ color: C.muted }}>
                    {m.weight}%
                  </span>
                </li>
              );
            })}
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-[26px]" style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}>Tasks</h1>
      {data.courses.map((c) => {
        const list = data.assignments.filter((a) => a.courseId === c.id);
        if (!list.length) return null;
        return (
          <section key={c.id}>
            <h3 className="text-sm font-medium mb-3" style={{ color: C.ink }}>
              {c.code} <span style={{ color: C.muted, fontWeight: 400 }}>· {c.name}</span>
            </h3>
            <div className="space-y-2">
              {list.map((a) => <TaskCard key={a.id} a={a} course={c} onOpen={onOpen} />)}
            </div>
          </section>
        );
      })}
    </div>
  );
}

function CalendarView({ data }) {
  const byId = Object.fromEntries(data.courses.map((c) => [c.id, c]));
  const days = Array.from({ length: 7 }, (_, i) => new Date(Date.now() + i * day));

  const items = [
    ...data.events.map((e) => ({ at: e.startAt, kind: "event", e })),
    ...data.assignments
      .filter((a) => a.status !== "submitted")
      .map((a) => ({ at: a.dueAt, kind: "due", a })),
  ].sort((x, y) => new Date(x.at) - new Date(y.at));

  return (
    <div className="space-y-6">
      <h1 className="text-[26px]" style={{ color: C.ink, fontFamily: "var(--display)", fontWeight: 600 }}>Week ahead</h1>

      <div className="flex gap-2 overflow-x-auto pb-1">
        {days.map((d, i) => {
          const count = items.filter((it) => new Date(it.at).toDateString() === d.toDateString()).length;
          const hasDue = items.some(
            (it) => it.kind === "due" && new Date(it.at).toDateString() === d.toDateString()
          );
          return (
            <div
              key={i}
              className="shrink-0 w-[62px] rounded-xl py-3 text-center"
              style={{
                background: i === 0 ? C.ink : C.card,
                border: `1px solid ${i === 0 ? C.ink : C.line}`,
              }}
            >
              <div className="text-[11px]" style={{ color: i === 0 ? "#B9C4BE" : C.muted }}>
                {d.toLocaleDateString([], { weekday: "short" })}
              </div>
              <div className="text-lg leading-tight" style={{ color: i === 0 ? "#fff" : C.ink, fontWeight: 600 }}>
                {d.getDate()}
              </div>
              <div className="h-1.5 mt-1.5 flex justify-center gap-1">
                {count > 0 && (
                  <span
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ background: hasDue ? C.now : i === 0 ? "#8FA69C" : C.calm }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="space-y-2">
        {items.map((it, i) => {
          const d = new Date(it.at);
          const label = d.toLocaleDateString([], { weekday: "short", day: "numeric", month: "short" });
          return (
            <div
              key={i}
              className="flex gap-3 px-4 py-3 rounded-xl items-center"
              style={{ background: C.card, border: `1px solid ${C.line}` }}
            >
              <div className="w-1 self-stretch rounded-full" style={{ background: it.kind === "due" ? C.now : C.line }} />
              <div className="w-[104px] shrink-0">
                <div className="text-xs" style={{ color: C.muted }}>{label}</div>
                <div className="text-sm tabular-nums" style={{ color: C.ink }}>{fmtTime(it.at)}</div>
              </div>
              <div className="min-w-0 flex-1">
                <div className="text-sm truncate" style={{ color: C.ink }}>
                  {it.kind === "due" ? `${it.a.title} due` : it.e.title}
                </div>
                <div className="text-xs truncate" style={{ color: C.muted }}>
                  {it.kind === "due"
                    ? `${byId[it.a.courseId].code} · ${it.a.gradeWeightPct}% of grade`
                    : `${byId[it.e.courseId].code} · ${it.e.location}`}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ── chat ────────────────────────────────────────────────────────
   Responses are computed locally from mockData so the demo works
   with no backend. Swap `reply()` for POST /api/chat when it exists.
   ─────────────────────────────────────────────────────────────── */

function reply(input, data) {
  const q = input.toLowerCase();
  const byId = Object.fromEntries(data.courses.map((c) => [c.id, c]));
  const live = data.assignments.filter((a) => a.status !== "submitted");
  const ranked = live.map((a) => ({ a, s: analyse(a) })).sort((x, y) => y.s.score - x.s.score);

  if (/(today|now|what should i do|start|plan)/.test(q)) {
    const picks = ranked.slice(0, 3);
    const total = picks.reduce((n, p) => n + p.s.estMinutes, 0);
    return {
      text: `Three things, about ${Math.round(total / 60 * 10) / 10} hours in total. Start at the top and stop when you run out of energy.`,
      cards: picks.map((p, i) => ({
        title: p.s.next ? p.s.next.name : "Review and submit",
        meta: `${byId[p.a.courseId].code} · ${p.s.estMinutes} min · ${fmtDue(p.a.dueAt)}`,
        band: p.s.band,
        index: i + 1,
      })),
    };
  }

  if (/(catch me up|missed|what.?s new|update|happened)/.test(q)) {
    const recent = data.updates.slice(0, 4);
    return {
      text: "Here is what changed while you were away.",
      cards: recent.map((u) => ({
        title: u.text,
        meta: `${byId[u.courseId].code} · ${new Date(u.at).toLocaleDateString([], { weekday: "short" })} ${fmtTime(u.at)}`,
        band: u.kind === "announcement" ? "amber" : "green",
      })),
    };
  }

  if (/(behind|risk|worried|stress|panic)/.test(q)) {
    const late = ranked.filter((p) => p.s.gap < -10);
    if (!late.length) return { text: "Nothing is behind pace right now. You have more room than it feels like." };
    return {
      text: `${late.length} ${late.length === 1 ? "task is" : "tasks are"} behind pace. Behind pace is not the same as in trouble, and the fix is usually one sitting.`,
      cards: late.map((p) => ({
        title: p.a.title,
        meta: `${Math.round(-p.s.gap)}% behind · ${fmtDue(p.a.dueAt)}`,
        band: p.s.band,
      })),
    };
  }

  if (/(due|deadline|when)/.test(q)) {
    const soon = [...live].sort((a, b) => new Date(a.dueAt) - new Date(b.dueAt)).slice(0, 4);
    return {
      text: "Your next deadlines.",
      cards: soon.map((a) => ({
        title: a.title,
        meta: `${byId[a.courseId].code} · ${fmtDue(a.dueAt)}`,
        band: analyse(a).band,
      })),
    };
  }

  if (/(break|smaller|step)/.test(q)) {
    const top = ranked[0];
    if (!top) return { text: "Nothing open to break down." };
    const rest = top.a.milestones.filter((m) => !m.done).slice(0, 4);
    return {
      text: `${top.a.title}, broken into what is left.`,
      cards: rest.map((m, i) => ({
        title: m.name,
        meta: m.targetWords ? `${Math.max(m.targetWords - m.words, 0)} words left · worth ${m.weight}%` : `worth ${m.weight}%`,
        band: "green",
        index: i + 1,
      })),
    };
  }

  const course = data.courses.find((c) => q.includes(c.code.toLowerCase()) || q.includes(c.name.toLowerCase()));
  if (course) {
    const list = data.assignments.filter((a) => a.courseId === course.id && a.status !== "submitted");
    if (!list.length) return { text: `Nothing open for ${course.code} right now.` };
    return {
      text: `${course.code} has ${list.length} open ${list.length === 1 ? "task" : "tasks"}.`,
      cards: list.map((a) => {
        const s = analyse(a);
        return { title: a.title, meta: `${Math.round(s.actual)}% done · ${fmtDue(a.dueAt)}`, band: s.band };
      }),
    };
  }

  return {
    text: "I can plan your day, catch you up on what you missed, list deadlines, or break a task into steps. Try one of the buttons below.",
  };
}

function ChatPanel({ data, messages, setMessages, pending, setPending }) {
  const [input, setInput] = useState("");
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  const send = (text) => {
    const t = text.trim();
    if (!t || pending) return;
    setMessages((m) => [...m, { role: "user", text: t }]);
    setInput("");
    setPending(true);
    // TODO backend: replace with POST /api/chat { message, studentId }
    setTimeout(() => {
      setMessages((m) => [...m, { role: "bot", ...reply(t, data) }]);
      setPending(false);
    }, 650);
  };

  const chips = ["What should I do today?", "Catch me up", "What's due this week?"];

  return (
    <div className="flex flex-col h-full" style={{ background: C.card }}>
      <header
        className="px-5 py-4 flex items-center gap-2 shrink-0"
        style={{ borderBottom: `1px solid ${C.line}` }}
      >
        <Sparkles size={16} style={{ color: C.calm }} />
        <span className="text-sm font-medium" style={{ color: C.ink }}>Ask ClassMate</span>
      </header>

      <div className="flex-1 overflow-y-auto px-5 py-5 space-y-4">
        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="flex justify-end">
              <div
                className="max-w-[85%] px-3.5 py-2.5 rounded-2xl rounded-br-sm text-sm"
                style={{ background: C.ink, color: "#fff" }}
              >
                {m.text}
              </div>
            </div>
          ) : (
            <div key={i} className="space-y-2">
              <div
                className="max-w-[92%] px-3.5 py-2.5 rounded-2xl rounded-bl-sm text-sm"
                style={{ background: C.paper, color: C.ink }}
              >
                {m.text}
              </div>
              {m.cards?.map((c, j) => {
                const t = tone(c.band || "green");
                return (
                  <div
                    key={j}
                    className="flex gap-3 px-3.5 py-3 rounded-xl"
                    style={{ background: C.card, border: `1px solid ${C.line}` }}
                  >
                    <div className="w-1 rounded-full shrink-0" style={{ background: t.fg }} />
                    <div className="min-w-0">
                      <div className="text-sm leading-snug" style={{ color: C.ink }}>
                        {c.index ? `${c.index}. ` : ""}{c.title}
                      </div>
                      <div className="text-xs mt-0.5" style={{ color: C.muted }}>{c.meta}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          )
        )}
        {pending && (
          <div className="flex gap-1.5 px-3.5 py-3 w-fit rounded-2xl" style={{ background: C.paper }}>
            {[0, 1, 2].map((i) => (
              <span
                key={i}
                className="w-1.5 h-1.5 rounded-full classmate-dot"
                style={{ background: C.muted, animationDelay: `${i * 0.15}s` }}
              />
            ))}
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="px-5 pb-5 pt-3 shrink-0 space-y-3" style={{ borderTop: `1px solid ${C.line}` }}>
        <div className="flex gap-2 overflow-x-auto">
          {chips.map((c) => (
            <button
              key={c}
              onClick={() => send(c)}
              className="shrink-0 px-3 py-1.5 rounded-full text-xs whitespace-nowrap"
              style={{ background: C.paper, color: C.ink, border: `1px solid ${C.line}` }}
            >
              {c}
            </button>
          ))}
        </div>
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send(input)}
            placeholder="Ask about your week"
            aria-label="Message ClassMate"
            className="flex-1 px-3.5 py-2.5 rounded-lg text-sm outline-none"
            style={{ background: C.paper, color: C.ink, border: `1px solid ${C.line}` }}
          />
          <button
            onClick={() => send(input)}
            aria-label="Send message"
            className="px-3.5 rounded-lg"
            style={{ background: C.calm }}
          >
            <Send size={16} color="#fff" />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ── shell ───────────────────────────────────────────────────── */

export default function ClassMate() {
  const data = mockData;
  const [view, setView] = useState("today");
  const [openId, setOpenId] = useState(null);
  const [pending, setPending] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "bot",
      text: `Morning ${data.student.name}. You have three tasks open and one deadline inside 24 hours. Want the plan for today?`,
    },
  ]);

  const ask = (text) => {
    setMessages((m) => [...m, { role: "user", text }]);
    setPending(true);
    setView("chat");
    setTimeout(() => {
      setMessages((m) => [...m, { role: "bot", ...reply(text, data) }]);
      setPending(false);
    }, 650);
  };

  const openTask = (id) => {
    setOpenId(id);
    setView("tasks");
  };

  const nav = [
    { id: "today", label: "Today", icon: Sun },
    { id: "tasks", label: "Tasks", icon: ListChecks },
    { id: "calendar", label: "Week", icon: CalendarDays },
    { id: "chat", label: "Ask", icon: MessageSquare },
  ];

  const main =
    view === "today" ? <TodayView data={data} onOpen={openTask} onAsk={ask} />
    : view === "tasks" ? <TasksView data={data} openId={openId} onOpen={setOpenId} />
    : view === "calendar" ? <CalendarView data={data} />
    : null;

  return (
    <div className="flex flex-col lg:flex-row h-screen w-full overflow-hidden" style={{ background: C.paper, fontFamily: "var(--body)" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600&family=Inter:wght@400;500;600&display=swap');
        :root {
          --display: 'Bricolage Grotesque', 'Inter', system-ui, sans-serif;
          --body: 'Inter', system-ui, -apple-system, sans-serif;
        }
        .classmate-dot { animation: cmBounce 1s infinite ease-in-out; }
        @keyframes cmBounce { 0%,60%,100%{ transform: translateY(0); opacity:.4 } 30%{ transform: translateY(-4px); opacity:1 } }
        .classmate-hero { animation: cmRise .45s cubic-bezier(.2,.7,.3,1) both; }
        @keyframes cmRise { from { opacity:0; transform: translateY(8px) } to { opacity:1; transform:none } }
        @media (prefers-reduced-motion: reduce) {
          .classmate-hero, .classmate-dot { animation: none !important; }
        }
        ::-webkit-scrollbar { width: 8px; height: 8px }
        ::-webkit-scrollbar-thumb { background: ${C.line}; border-radius: 8px }
        button:focus-visible, input:focus-visible { outline: 2px solid ${C.calm}; outline-offset: 2px }
      `}</style>

      {/* desktop rail */}
      <nav
        className="hidden lg:flex flex-col w-[92px] shrink-0 py-6 items-center gap-1"
        style={{ background: C.card, borderRight: `1px solid ${C.line}` }}
      >
        <div
          className="w-9 h-9 rounded-xl mb-6 flex items-center justify-center text-sm"
          style={{ background: C.calm, color: "#fff", fontFamily: "var(--display)", fontWeight: 600 }}
        >
          CM
        </div>
        {nav.filter((n) => n.id !== "chat").map((n) => {
          const active = view === n.id;
          return (
            <button
              key={n.id}
              onClick={() => { setView(n.id); if (n.id !== "tasks") setOpenId(null); }}
              className="w-full py-3 flex flex-col items-center gap-1"
              style={{ color: active ? C.calm : C.muted }}
            >
              <n.icon size={19} />
              <span className="text-[11px]" style={{ fontWeight: active ? 600 : 400 }}>{n.label}</span>
            </button>
          );
        })}
      </nav>

      {/* main column */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-[640px] mx-auto px-5 sm:px-8 py-7 pb-28 lg:pb-12">
          {view === "chat" ? (
            <div className="lg:hidden -mx-5 sm:-mx-8 -my-7 h-[calc(100vh-72px)]">
              <ChatPanel data={data} messages={messages} setMessages={setMessages} pending={pending} setPending={setPending} />
            </div>
          ) : (
            main
          )}
          {view === "chat" && <div className="hidden lg:block">{<TodayView data={data} onOpen={openTask} onAsk={ask} />}</div>}
        </div>
      </main>

      {/* desktop chat panel */}
      <aside className="hidden lg:block w-[380px] shrink-0" style={{ borderLeft: `1px solid ${C.line}` }}>
        <ChatPanel data={data} messages={messages} setMessages={setMessages} pending={pending} setPending={setPending} />
      </aside>

      {/* mobile bottom nav */}
      <nav
        className="lg:hidden fixed bottom-0 left-0 right-0 flex"
        style={{ background: C.card, borderTop: `1px solid ${C.line}` }}
      >
        {nav.map((n) => {
          const active = view === n.id;
          return (
            <button
              key={n.id}
              onClick={() => { setView(n.id); if (n.id !== "tasks") setOpenId(null); }}
              className="flex-1 py-3 flex flex-col items-center gap-1"
              style={{ color: active ? C.calm : C.muted }}
            >
              <n.icon size={19} />
              <span className="text-[10px]" style={{ fontWeight: active ? 600 : 400 }}>{n.label}</span>
            </button>
          );
        })}
      </nav>
    </div>
  );
}
