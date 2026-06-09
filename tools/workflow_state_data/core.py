"""Pure transforms: timeline label events + an observation time → phase history."""

import itertools
from dataclasses import dataclass
from datetime import datetime
from typing import Literal


class PersistentDoublePhaseError(Exception):
    """An issue settled on more than one phase label at the same instant."""


@dataclass(frozen=True)
class LabelEvent:
    action: Literal["labeled", "unlabeled"]
    label: str
    at: datetime


@dataclass(frozen=True)
class PhaseVisit:
    phase: str
    entered_at: datetime
    exited_at: datetime | None
    duration_seconds: float


def reconstruct_phase_history(
    events: list[LabelEvent], until: datetime
) -> list[PhaseVisit]:
    def visit(
        phase: str, entered_at: datetime, exited_at: datetime | None
    ) -> PhaseVisit:
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

    phase_events = (e for e in events if e.label.startswith("phase:"))
    # Phase-label swaps land as add/remove pairs at the same timestamp; apply
    # each same-timestamp group atomically (API order preserved, no re-sort)
    # so transient two-label/zero-label instants inside a group never surface.
    for at, group in itertools.groupby(phase_events, key=lambda e: e.at):
        for event in group:
            phase = event.label.removeprefix("phase:")
            if event.action == "labeled":
                active.add(phase)
            else:
                active.discard(phase)
        if len(active) > 1:
            raise PersistentDoublePhaseError(
                f"multiple phase labels active at {at.isoformat()}: {sorted(active)}"
            )
        settled = next(iter(active)) if active else None
        if open_visit is not None and settled == open_visit[0]:
            continue
        if open_visit is not None:
            visits.append(visit(open_visit[0], open_visit[1], at))
        open_visit = (settled, at) if settled is not None else None

    if open_visit is not None:
        visits.append(visit(open_visit[0], open_visit[1], None))
    return visits
