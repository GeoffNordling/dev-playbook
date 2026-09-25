"""What a stint leaves in its folder: one record per call, and ``stint.json``.

The stint's folder, ``<home>/<repo>/<name>/``, outlives the stint:

    calls/<call>.json   a CallRecord, one per agent call, or a CheckRecord
    calls/<call>.request.json   what Sandcastle was asked to run
    calls/<call>.log    Sandcastle's log of the call
    calls/<call>-setup.log      Sandcastle's log of an agent call's hook install
    calls/<call>-probe.log      Sandcastle's log of the uncommitted-work probe
    check-<n>.txt       the target check's output at checkpoint n
    review-<n>.md       the reviewer's report for segment n
    sessions/           the agents' session files, the principal's included
    stint.json          the StintRecord
"""

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Usage:
    """Token use at the call's last turn, as Claude reports it."""

    input_tokens: int
    cache_creation_input_tokens: int
    cache_read_input_tokens: int
    output_tokens: int

    @property
    def context(self) -> int:
        """The conversation's size at that turn: its input, cached and new, and its output."""
        return (
            self.input_tokens
            + self.cache_creation_input_tokens
            + self.cache_read_input_tokens
            + self.output_tokens
        )


@dataclass(frozen=True)
class CallRecord:
    """One sealed agent call."""

    name: str
    """Such as ``iter-3``, ``review-1``, or ``principal-2``."""
    session: str
    """The Claude session ID; the principal's calls resume one session."""
    resumed: str | None
    """The session this call resumed, or None for a fresh one."""
    api_key_source: str
    """Where Claude found its credential; ``none`` means the subscription."""
    seconds: int
    is_error: bool
    usage: Usage | None
    commits: list[str]
    """The commits the call made, oldest first."""
    uncommitted: list[str]
    """Files the call left uncommitted, as git's short status lines."""
    answer: str
    """The agent's final message."""

    def write(self, calls: Path) -> None:
        """Write the record to ``calls/<name>.json``."""
        (calls / f"{self.name}.json").write_text(
            json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8"
        )


@dataclass(frozen=True)
class CheckRecord:
    """One run of the target check, in a sealed container, run by the stint."""

    name: str
    """Such as ``check-2``, the run at checkpoint 2."""
    seconds: int
    exit: int
    """The check's exit code; 0 is zero findings."""
    output: list[str]
    """What the check printed, stdout and stderr, one line each."""
    uncommitted: list[str]
    """Files the check left uncommitted, as git's short status lines."""

    def write(self, calls: Path) -> None:
        """Write the record to ``calls/<name>.json``."""
        (calls / f"{self.name}.json").write_text(
            json.dumps(asdict(self), indent=2) + "\n", encoding="utf-8"
        )


@dataclass(frozen=True)
class ContextSize:
    """The principal's conversation size after one of its calls."""

    call: str
    tokens: int


@dataclass
class StintRecord:
    """The whole stint, written to ``stint.json`` at the end."""

    reason: str
    """``done``, or why the stint stopped."""
    budget: int
    spent: int = 0
    """Iterations used."""
    head: str = ""
    """The stint branch's last commit."""
    minutes: float = 0.0
    closed: bool = False
    """Whether the work copy's commits landed and both copies were deleted."""
    principal: str | None = None
    """The principal's session ID."""
    notes: list[str] = field(default_factory=list)
    """Things the stint saw that were not reasons to stop."""
    principal_context: list[ContextSize] = field(default_factory=list)
    calls: list[CallRecord] = field(default_factory=list)
    checks: list[CheckRecord] = field(default_factory=list)

    def write(self, folder: Path) -> None:
        """Write the record to ``stint.json``.

        Each call keeps its name, session, and commits; each check, its name
        and exit code.
        """
        record = asdict(self)
        record["calls"] = [
            {k: c[k] for k in ("name", "session", "resumed", "seconds", "commits")}
            for c in record["calls"]
        ]
        record["checks"] = [
            {k: c[k] for k in ("name", "seconds", "exit")} for c in record["checks"]
        ]
        (folder / "stint.json").write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )
