"""Canonical phase set and ordering, hand-encoded from workflow.md's graph.

Ranks encode the forward edges of workflow.md §State machine:
intake < design < tdd/build < code-pr-review on the direct path, and
intake < sdd-specs < sdd-spec-review < sdd-tdd < sdd-code-pr-review on the
SDD path. A transition to a lower rank is backward — rework.
"""

PHASE_RANK: dict[str, int] = {
    "intake": 0,
    "design": 1,
    "tdd": 2,
    "build": 2,
    "code-pr-review": 3,
    "sdd-specs": 1,
    "sdd-spec-review": 2,
    "sdd-tdd": 3,
    "sdd-code-pr-review": 4,
}


METADATA_LABELS: frozenset[str] = frozenset(
    {
        "category:bug",
        "category:enhancement",
        "mode:sdd",
        "mode:direct",
        "tests:yes",
        "tests:no",
    }
)

CANONICAL_LABELS: frozenset[str] = METADATA_LABELS | {
    f"phase:{phase}" for phase in PHASE_RANK
}


def is_backward(from_phase: str, to_phase: str) -> bool:
    return PHASE_RANK[to_phase] < PHASE_RANK[from_phase]
