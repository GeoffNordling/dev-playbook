"""Pure transforms: timeline label events + an observation time → phase history."""

import itertools
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from workflow_state_data.phases import CANONICAL_LABELS, is_backward


class PersistentDoublePhaseError(Exception):
    """An issue settled on more than one phase label at the same instant."""


@dataclass(frozen=True)
class LabelEvent:
    """One labeled/unlabeled timeline event: action, label name, timestamp."""

    action: Literal["labeled", "unlabeled"]
    label: str
    at: datetime


@dataclass(frozen=True)
class IssueData:
    """Everything fetched about one issue, ready for pure transformation."""

    repo: str
    number: int
    title: str
    state: Literal["open", "closed"]
    created_at: datetime
    closed_at: datetime | None
    labels: tuple[str, ...]
    events: tuple[LabelEvent, ...]
    comment_count: int


@dataclass(frozen=True)
class PhaseVisit:
    """One stay in a phase; an in-flight visit has no exit timestamp."""

    phase: str
    entered_at: datetime
    exited_at: datetime | None
    duration_seconds: float


def _double_phase_error(
    since: datetime, active: set[str]
) -> PersistentDoublePhaseError:
    """Error for a double-phase state that outlived the swap tolerance."""
    return PersistentDoublePhaseError(
        f"multiple phase labels active since {since.isoformat()}: {sorted(active)}"
    )


def reconstruct_phase_history(
    events: list[LabelEvent], until: datetime
) -> list[PhaseVisit]:
    """Replay phase-label events into a list of visits; open visits run to until."""

    def visit(
        phase: str, entered_at: datetime, exited_at: datetime | None
    ) -> PhaseVisit:
        """Build a PhaseVisit, measuring an open visit's duration to until."""
        end = exited_at if exited_at is not None else until
        return PhaseVisit(
            phase=phase,
            entered_at=entered_at,
            exited_at=exited_at,
            duration_seconds=(end - entered_at).total_seconds(),
        )

    visits: list[PhaseVisit] = []
    open_visit: tuple[str, datetime] | None = None
    active: set[str] = set()

    def apply(event: LabelEvent) -> None:
        """Apply one labeled/unlabeled event to the active phase set."""
        phase = event.label.removeprefix("phase:")
        if event.action == "labeled":
            active.add(phase)
        else:
            active.discard(phase)

    # Events past until (labels edited on a closed issue — e.g. a human
    # tidying the stale phase label the approve path leaves behind) are
    # deliberately ignored: the history only covers the issue's lifetime.
    # They are kept aside because the terminal double-phase check below
    # consults them.
    phase_events = [e for e in events if e.label.startswith("phase:")]
    lifetime_events = (e for e in phase_events if e.at <= until)
    post_until_events = [e for e in phase_events if e.at > until]
    # Phase-label swaps usually land as add/remove pairs at the same timestamp,
    # but gh dispatches the two mutations concurrently, so with GitHub's
    # second-granularity timestamps a swap can straddle a boundary. Apply each
    # same-timestamp group atomically (API order preserved, no re-sort) and
    # tolerate a double-phase state for one group; fail loud only when it
    # persists past the next group — that is a real double label, not a swap.
    double_since: datetime | None = None
    for at, group in itertools.groupby(lifetime_events, key=lambda e: e.at):
        for event in group:
            apply(event)
        if len(active) > 1:
            if double_since is not None:
                raise _double_phase_error(double_since, active)
            double_since = at
            continue
        double_since = None
        settled = next(iter(active)) if active else None
        if open_visit is not None and settled == open_visit[0]:
            continue
        if open_visit is not None:
            visits.append(visit(open_visit[0], open_visit[1], at))
        open_visit = (settled, at) if settled is not None else None

    if double_since is not None:
        # A swap bundled with a close dispatches its two mutations
        # concurrently, so the resolving unlabel can land just past until.
        # Consult the otherwise-ignored post-until events before declaring
        # the double persistent; a resolved swap settles at until.
        for event in post_until_events:
            apply(event)
            if len(active) <= 1:
                break
        if len(active) > 1:
            raise _double_phase_error(double_since, active)
        settled = next(iter(active)) if active else None
        if open_visit is None or settled != open_visit[0]:
            if open_visit is not None:
                visits.append(visit(open_visit[0], open_visit[1], until))
            open_visit = (settled, until) if settled is not None else None
    if open_visit is not None:
        visits.append(visit(open_visit[0], open_visit[1], None))
    return visits


def build_record(issue: IssueData, now: datetime) -> dict | None:
    """Assemble one issue's JSON-ready metrics record, or None if out of scope."""
    # Scope rule: the tool only sees issues fully inside the canonical
    # workflow — any non-canonical label (current or historical) or an empty
    # phase history means silently omitted, not an error.
    seen_labels = set(issue.labels) | {event.label for event in issue.events}
    if not seen_labels <= CANONICAL_LABELS:
        return None

    until = issue.closed_at if issue.closed_at is not None else now
    history = reconstruct_phase_history(list(issue.events), until)
    if not history:
        return None
    last = history[-1]
    current_phase = last.phase if last.exited_at is None else None
    transitions = [
        {
            "from": prev.phase,
            "to": nxt.phase,
            "at": nxt.entered_at.isoformat(),
            "backward": is_backward(prev.phase, nxt.phase),
        }
        for prev, nxt in itertools.pairwise(history)
    ]
    metadata = dict(
        label.split(":", 1) for label in issue.labels if not label.startswith("phase:")
    )
    # An issue may legitimately carry no category:/mode:/tests: label, so the
    # metadata lookups below deliberately fall back to None.
    return {
        "repo": issue.repo,
        "number": issue.number,
        "title": issue.title,
        "state": issue.state,
        "category": metadata.get("category"),
        "mode": metadata.get("mode"),
        "tests": metadata.get("tests"),
        "created_at": issue.created_at.isoformat(),
        "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
        "current_phase": current_phase,
        "lifetime_seconds": (until - issue.created_at).total_seconds(),
        "transitions": transitions,
        "rework_count": sum(1 for t in transitions if t["backward"]),
        "phase_visits": dict(Counter(v.phase for v in history)),
        "comments": {"issue": issue.comment_count, "total": issue.comment_count},
        "phase_history": [
            {
                "phase": v.phase,
                "entered_at": v.entered_at.isoformat(),
                "exited_at": v.exited_at.isoformat() if v.exited_at else None,
                "duration_seconds": v.duration_seconds,
            }
            for v in history
        ],
    }


def live_view(records: list[dict]) -> dict:
    """Group open issues by current phase: {phase: [{repo, number, title}]}."""
    view: dict[str, list[dict]] = {}
    for record in records:
        if record["state"] != "open":
            continue
        # An open issue whose last phase label was removed without a
        # replacement is in limbo; surface it deliberately under "no-phase".
        phase = (
            record["current_phase"]
            if record["current_phase"] is not None
            else "no-phase"
        )
        view.setdefault(phase, []).append(
            {
                "repo": record["repo"],
                "number": record["number"],
                "title": record["title"],
            }
        )
    return view
