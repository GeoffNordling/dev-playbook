"""The stint's calls in order, and the rules that stop it.

    principal-0   reads the plan; answers launch, or why not
    iter-1..k     one task each, checked off and committed
    review-n      reads segment n's commits cold, commits nothing
    principal-n   the same conversation, resumed: continue, done, or stop

The loop repeats iterations, a review, and the principal's checkpoint until
the principal says done or a rule stops it. Every rule is checked here, in
code, and costs no tokens. The loop takes the function that makes one call,
so a test can pass a fake one.

Between calls the loop reads the copy as plain files, never with host git.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from dev_playbook.stint import workcopy
from dev_playbook.stint.call import CallFault
from dev_playbook.stint.plan import PlanState, plan_state
from dev_playbook.stint.records import CallRecord, ContextSize, StintRecord

Call = Callable[[str, str, str | None], CallRecord]
"""Make one call: its name, its prompt, and the session to resume, if any."""


class Stop(Exception):
    """The stint stops here; the message is the reason."""


@dataclass(frozen=True)
class Assignment:
    """What the stint works on, as the prompts and the rules see it."""

    copy: Path
    """The work copy on the host."""
    repo: str
    """The work copy's path inside the container."""
    workstream: str
    """The workstream folder, relative to the repository."""
    check: str
    """The command that must pass after every change."""
    budget: int
    """The most iterations the stint may spend."""


def fill(template: str, values: dict[str, object]) -> str:
    """The named prompt template with every ``{{KEY}}`` replaced."""
    text = (
        resources.files("dev_playbook.stint")
        .joinpath("prompts", f"{template}.md.in")
        .read_text(encoding="utf-8")
    )
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    if "{{" in text:
        raise ValueError(
            f"unfilled placeholder in {template}: {text[text.index('{{') :][:30]}"
        )
    return text


def ending(answer: str) -> dict:
    """The JSON object on the answer's last line, past any backticks or code fence."""
    lines = [line.strip().strip("`").strip() for line in answer.splitlines()]
    lines = [line for line in lines if line and line != "json"]
    if not lines:
        raise Stop("the call gave no answer")
    try:
        found = json.loads(lines[-1])
    except json.JSONDecodeError:
        raise Stop(f"the answer's last line is not JSON: {lines[-1][:80]}") from None
    if not isinstance(found, dict):
        raise Stop(f"the answer's last line is not a JSON object: {lines[-1][:80]}")
    return found


class Loop:
    """One stint's run, writing what happens into its record as it goes."""

    def __init__(
        self, work: Assignment, call: Call, record: StintRecord, folder: Path
    ) -> None:
        """Read the copy's HEAD and set the values every prompt shares."""
        self.work = work
        self.make_call = call
        self.record = record
        self.folder = folder
        ws = work.workstream
        self.shared = {
            "REPO": work.repo,
            "HEAD": f"{ws}/WORKSTREAM.md",
            "PLAN": f"{ws}/PLAN.md",
            "PROGRESS": f"{ws}/PROGRESS.md",
            "CHECK": work.check,
            "BUDGET": work.budget,
        }
        self.head = self.read(lambda: workcopy.head_commit(work.copy))
        record.head = self.head

    def read[T](self, reader: Callable[[], T]) -> T:
        """Read the copy, turning a refusal into a stop."""
        try:
            return reader()
        except workcopy.CopyFault as err:
            raise Stop(str(err)) from err

    def plan(self) -> PlanState:
        """The plan's state, read as plain text."""
        path = f"{self.work.workstream}/PLAN.md"
        return plan_state(self.read(lambda: workcopy.read_plain(self.work.copy, path)))

    def call(
        self, name: str, template: str, resume: str | None = None, **values: object
    ) -> CallRecord:
        """Make one call and apply the rules every call shares."""
        try:
            rec = self.make_call(
                name, fill(template, {**self.shared, **values}), resume
            )
        except CallFault as err:
            raise Stop(f"{name}: {err}") from err
        self.record.calls.append(rec)
        print(
            f"{name}: {rec.seconds}s session={rec.session}"
            f" commits={len(rec.commits)} uncommitted={len(rec.uncommitted)}",
            flush=True,
        )
        if rec.is_error:
            raise Stop(f"{name} ended in error")
        if rec.uncommitted:
            raise Stop(f"{name} left work uncommitted: {rec.uncommitted[:5]}")
        if rec.commits:
            self.head = rec.commits[-1]
            self.record.head = self.head
        if self.read(lambda: workcopy.head_commit(self.work.copy)) != self.head:
            raise Stop(f"{name}: the copy's HEAD is not the call's last commit")
        return rec

    def principal(self, rec: CallRecord) -> dict:
        """Keep the principal's session and context size; return its verdict line."""
        if rec.usage is None:
            raise Stop(f"{rec.name} reported no token usage")
        self.record.principal = rec.session
        self.record.principal_context.append(ContextSize(rec.name, rec.usage.context))
        return ending(rec.answer)

    def note(self, text: str) -> None:
        """Record something the driver saw that is not a reason to stop."""
        self.record.notes.append(text)
        print(f"note: {text}", flush=True)

    def run(self) -> None:
        """Run the stint until the principal says done; any other end raises Stop."""
        budget = self.work.budget
        if self.plan().left > budget:
            raise Stop(f"not launched: {self.plan().left} tasks, budget {budget}")
        rec = self.call("principal-0", "principal-open")
        end = self.principal(rec)
        if rec.commits:
            raise Stop("the principal changed the plan at launch")
        if end.get("verdict") != "launch":
            raise Stop(f"stuck at launch: {end.get('reason')}")
        n = 0
        while True:
            n += 1
            start, summaries = self.head, []
            while self.plan().segment and self.record.spent < budget:
                before = self.plan()
                self.record.spent += 1
                name = f"iter-{self.record.spent}"
                rec = self.call(name, "iteration")
                end = ending(rec.answer)
                summary = f"- {name}: {end.get('summary')}"
                if end.get("blocker"):
                    raise Stop(f"{name} blocked: {end['blocker']}")
                if not rec.commits:
                    raise Stop(f"{name} committed nothing")
                after = self.plan()
                if (after.done, after.open) != (before.done, before.open):
                    raise Stop(f"{name} moved a checkpoint marker")
                ticked = before.segment - after.segment
                if ticked != 1:
                    note = f"{name} checked off {ticked} tasks, not 1"
                    self.note(note)
                    summary += f" (the driver notes: {note})"
                summaries.append(summary)
            if self.head == start:
                raise Stop(f"segment {n} has no commits to review")
            rec = self.call(f"review-{n}", "reviewer", RANGE=f"{start}..{self.head}")
            if rec.commits:
                raise Stop(f"review-{n} committed")
            review = rec.answer.strip()
            (self.folder / f"review-{n}.md").write_text(review + "\n", encoding="utf-8")
            state = self.plan()
            rec = self.call(
                f"principal-{n}",
                "principal-checkpoint",
                resume=self.record.principal,
                N=state.done + 1,
                OF=state.done + state.open,
                SPENT=self.record.spent,
                SUMMARIES="\n".join(summaries),
                REVIEW=review,
            )
            end = self.principal(rec)
            verdict = end.get("verdict")
            after = self.plan()
            if verdict in ("continue", "done") and after.done != state.done + 1:
                raise Stop(f"principal-{n} did not check off the checkpoint")
            if verdict == "done":
                if after.left or after.open:
                    raise Stop(f"principal-{n} said done with {after.left} tasks left")
                return
            if verdict != "continue":
                raise Stop(f"{verdict}: {end.get('reason')}")
            if self.record.spent >= budget:
                raise Stop(f"budget: {self.record.spent} of {budget} iterations spent")
            if not after.segment:
                raise Stop(
                    f"principal-{n} said continue with no task in the next segment"
                )
