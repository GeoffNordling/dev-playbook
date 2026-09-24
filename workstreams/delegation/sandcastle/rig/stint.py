"""The headless driver: run one unattended stint from launch to yield.

The loop, the stop rules, and the checkpoints live here. Every agent call
runs sealed through `call.mjs`. Each call is fresh except the principal's,
which is one conversation resumed at every checkpoint.

Between calls the driver reads the copy as plain files, never with host git,
and refuses a symlink on any path it reads, so a planted link cannot pull a
host file into a prompt.

Usage:
    stint.py REPO --base REF --workstream DIR --check CMD --budget N
             [--name NAME] [--home HOME] [--playbook PATH] [--model M]

REPO is any git repository; the stint's branch NAME starts at REF, which
already holds the workstream DIR (its WORKSTREAM.md, PLAN.md, and
PROGRESS.md). The stint's folder is HOME/<repo>/NAME. At launch the driver
makes two copies in it: the work copy, REPO opened by front-clone, and the
config copy, dev-playbook's `main` with the pipeline's two patches. At the
yield it closes the work copy, which brings the branch into REPO and deletes
the copy, and deletes the config copy. A work copy holding uncommitted work
is kept, and the close says so. The stint's record stays in its folder.

Refuses to launch a plan with more open tasks than the budget. Writes
stint.json, the stint's record, and exits 0 on done, 1 on any other yield.
The image `localhost/sandcastle-pipeline:rig` must already be built.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

RIG = Path(__file__).resolve().parent
OPEN_MARK = "<!-- [ ] checkpoint -->"
DONE_MARK = "<!-- [x] checkpoint -->"


class Yield(Exception):
    """The stint stops here; the message is the reason."""


def plain(copy: Path, rel: str) -> str:
    """Read a file in the copy as text, refusing a symlink anywhere on its path."""
    path = copy
    for part in Path(rel).parts:
        path = path / part
        if path.is_symlink():
            raise Yield(f"symlink in the copy: {rel}")
    return path.read_text()


def head_sha(copy: Path) -> str:
    """The copy's HEAD commit, read from .git as plain text."""
    head = plain(copy, ".git/HEAD").strip()
    if not head.startswith("ref: "):
        return head
    ref = head[5:]
    if (copy / ".git" / ref).exists():
        return plain(copy, f".git/{ref}").strip()
    for line in plain(copy, ".git/packed-refs").splitlines():
        if line.endswith(" " + ref):
            return line.split()[0]
    raise Yield(f"HEAD names {ref}, which the copy does not hold")


def plan_state(text: str) -> dict:
    """Count the plan's markers and the unchecked tasks in the open segment."""
    lines = text.splitlines()
    done = [i for i, line in enumerate(lines) if line.strip() == DONE_MARK]
    open_ = [i for i, line in enumerate(lines) if line.strip() == OPEN_MARK]
    tasks = [i for i, line in enumerate(lines) if re.match(r"- \[ \] ", line)]
    start = max([i for i in done if not open_ or i < open_[0]], default=-1)
    end = open_[0] if open_ else len(lines)
    return {
        "done": len(done),
        "open": len(open_),
        "segment": sum(1 for i in tasks if start < i < end),
        "left": len(tasks),
    }


def ending(answer: str) -> dict:
    """The JSON object on the answer's last line, past any backticks or code fence."""
    lines = [line.strip().strip("`").strip() for line in answer.splitlines()]
    lines = [line for line in lines if line and line != "json"]
    if not lines:
        raise Yield("the call gave no answer")
    try:
        return json.loads(lines[-1])
    except json.JSONDecodeError:
        raise Yield(f"the answer's last line is not JSON: {lines[-1][:80]}") from None


def context_tokens(record: dict) -> int:
    """The conversation's size at the call's last turn: its input, cached and new, and its output."""
    if not record.get("usage"):
        raise Yield(f"{record['name']} reported no token usage")
    u = record["usage"]
    return (
        u["inputTokens"]
        + u["cacheCreationInputTokens"]
        + u["cacheReadInputTokens"]
        + u["outputTokens"]
    )


def sandcastle_step(args, name: str, prompt: str, resume: str | None) -> dict:
    """Run one call sealed through call.mjs and return its record."""
    opts = {
        "config": str(args.config),
        "copy": str(args.copy),
        "stint": str(args.stint),
        "name": name,
        "model": args.model,
        "prompt": prompt,
    }
    if resume:
        opts["resume"] = resume
    opts_file = args.stint / "calls" / f"{name}.opts.json"
    opts_file.write_text(json.dumps(opts))
    done = subprocess.run(
        ["node", str(RIG / "call.mjs"), str(opts_file)], capture_output=True, text=True
    )
    record_file = args.stint / "calls" / f"{name}.json"
    if done.returncode or not record_file.exists():
        sys.stderr.write(done.stdout[-2000:] + done.stderr[-2000:])
        raise Yield(f"call {name} failed: exit {done.returncode}")
    return json.loads(record_file.read_text())


def fill(template: str, values: dict) -> str:
    """Fill a prompt template's {{KEY}} placeholders, refusing any left unfilled."""
    text = (RIG / "prompts" / f"{template}.md.in").read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", str(value))
    if "{{" in text:
        raise SystemExit(
            f"unfilled placeholder in {template}: {text[text.index('{{') :][:30]}"
        )
    return text


class Stint:
    """One stint's state: its calls, iterations spent, the principal's session, and HEAD."""

    def __init__(self, args, step=sandcastle_step):
        """Read the copy's HEAD and set the values every prompt shares."""
        self.args = args
        self.step = step
        ws = args.workstream
        self.base = {
            "REPO": f"/home/agent/assignment/{args.copy.name}",
            "HEAD": f"{ws}/WORKSTREAM.md",
            "PLAN": f"{ws}/PLAN.md",
            "PROGRESS": f"{ws}/PROGRESS.md",
            "CHECK": args.check,
            "BUDGET": args.budget,
        }
        self.calls = []
        self.notes = []
        self.context = []
        self.spent = 0
        self.principal = None
        self.head = head_sha(args.copy)

    def plan(self) -> dict:
        """The plan's marker and task counts, read as plain text."""
        return plan_state(plain(self.args.copy, self.base["PLAN"]))

    def call(
        self, name: str, template: str, resume: str | None = None, **values
    ) -> tuple[dict, dict | None]:
        """Run one call and apply the checks every call shares.

        Every prompt but the reviewer's ends in a line of JSON, returned parsed.
        """
        record = self.step(
            self.args, name, fill(template, {**self.base, **values}), resume
        )
        self.calls.append(record)
        print(
            f"{name}: {record['seconds']}s session={record['session']}"
            f" commits={len(record['commits'])} uncommitted={len(record['uncommitted'])}",
            flush=True,
        )
        if record["isError"]:
            raise Yield(f"{name} ended in error")
        if record["uncommitted"]:
            raise Yield(f"{name} left work uncommitted: {record['uncommitted'][:5]}")
        if record["commits"]:
            self.head = record["commits"][-1]
        if head_sha(self.args.copy) != self.head:
            raise Yield(f"{name}: the copy's HEAD is not the call's last commit")
        return record, None if template == "reviewer" else ending(record["answer"])

    def run(self) -> str:
        """Run the stint to its yield; return "done" or raise Yield."""
        if self.plan()["left"] > self.args.budget:
            raise Yield(
                f"not launched: {self.plan()['left']} tasks, budget {self.args.budget}"
            )
        record, end = self.call("principal-0", "principal-open")
        self.principal = record["session"]
        self.context.append({"call": "principal-0", "tokens": context_tokens(record)})
        if record["commits"]:
            raise Yield("the principal changed the plan at launch")
        if end.get("verdict") != "launch":
            raise Yield(f"stuck at launch: {end.get('reason')}")
        n = 0
        while True:
            n += 1
            seg_base, summaries = self.head, []
            while self.plan()["segment"] and self.spent < self.args.budget:
                before = self.plan()
                self.spent += 1
                name = f"iter-{self.spent}"
                record, end = self.call(name, "iteration")
                summary = f"- {name}: {end.get('summary')}"
                if end.get("blocker"):
                    raise Yield(f"{name} blocked: {end['blocker']}")
                if not record["commits"]:
                    raise Yield(f"{name} committed nothing")
                after = self.plan()
                if (after["done"], after["open"]) != (before["done"], before["open"]):
                    raise Yield(f"{name} moved a checkpoint marker")
                ticked = before["segment"] - after["segment"]
                if ticked != 1:
                    note = f"{name} checked off {ticked} tasks, not 1"
                    self.notes.append(note)
                    print(f"note: {note}", flush=True)
                    summary += f" (the driver notes: {note})"
                summaries.append(summary)
            if self.head == seg_base:
                raise Yield(f"segment {n} has no commits to review")
            record, _ = self.call(
                f"review-{n}", "reviewer", RANGE=f"{seg_base}..{self.head}"
            )
            if record["commits"]:
                raise Yield(f"review-{n} committed")
            review = record["answer"].strip()
            (self.args.stint / f"review-{n}.md").write_text(review + "\n")
            state = self.plan()
            record, end = self.call(
                f"principal-{n}",
                "principal-checkpoint",
                resume=self.principal,
                N=state["done"] + 1,
                OF=state["done"] + state["open"],
                SPENT=self.spent,
                SUMMARIES="\n".join(summaries),
                REVIEW=review,
            )
            self.principal = record["session"]
            self.context.append(
                {"call": f"principal-{n}", "tokens": context_tokens(record)}
            )
            verdict = end.get("verdict")
            after = self.plan()
            if verdict in ("continue", "done") and after["done"] != state["done"] + 1:
                raise Yield(f"principal-{n} did not check off the checkpoint")
            if verdict == "done":
                if after["left"] or after["open"]:
                    raise Yield(
                        f"principal-{n} said done with {after['left']} tasks left"
                    )
                return "done"
            if verdict != "continue":
                raise Yield(f"{verdict}: {end.get('reason')}")
            if self.spent >= self.args.budget:
                raise Yield(
                    f"budget: {self.spent} of {self.args.budget} iterations spent"
                )
            if not after["segment"]:
                raise Yield(
                    f"principal-{n} said continue with no task in the next segment"
                )


def make_config(playbook: Path, config: Path) -> None:
    """Clone dev-playbook's main into the config copy and commit the pipeline's two patches."""
    subprocess.run(
        [
            "git",
            "clone",
            "-q",
            "--no-hardlinks",
            "--branch",
            "main",
            str(playbook),
            str(config),
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(config),
            "apply",
            *sorted(str(p) for p in (RIG / "patches").glob("*.patch")),
        ],
        check=True,
    )
    subprocess.run(
        [
            "git",
            "-C",
            str(config),
            "-c",
            "user.name=stint",
            "-c",
            "user.email=stint@example.invalid",
            "commit",
            "-q",
            "-am",
            "stint: the pipeline's two dev-playbook changes",
        ],
        check=True,
    )


def main(argv=None, step=sandcastle_step) -> int:
    """Open both copies, run the stint, write stint.json, and close both copies."""
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("repo", type=Path)
    p.add_argument("--base", required=True)
    p.add_argument("--workstream", required=True)
    p.add_argument("--check", required=True)
    p.add_argument("--budget", type=int, required=True)
    p.add_argument("--name", default=time.strftime("stint-%Y%m%d-%H%M%S"))
    p.add_argument("--home", type=Path, default=Path.home() / "stints")
    p.add_argument(
        "--playbook", type=Path, default=Path.home() / "workspace" / "dev-playbook"
    )
    p.add_argument("--model", default="claude-sonnet-5")
    args = p.parse_args(argv)
    args.repo = args.repo.resolve()
    args.stint = (args.home / args.repo.name / args.name).resolve()
    args.copy = args.stint / args.repo.name
    args.config = args.stint / "config"
    if args.stint.exists():
        raise SystemExit(f"{args.stint} already exists; a stint's folder is made fresh")
    (args.stint / "calls").mkdir(parents=True)
    front_clone = str(RIG.parents[3] / "scripts" / "front-clone")
    started = time.time()
    try:
        make_config(args.playbook, args.config)
        subprocess.run(
            [
                front_clone,
                "open",
                str(args.repo),
                str(args.copy),
                args.name,
                "--base",
                args.base,
            ],
            check=True,
        )
        print(f"stint {args.name}: {args.stint}", flush=True)
        stint = Stint(args, step)
        try:
            reason = stint.run()
        except Yield as y:
            reason = str(y)
    finally:
        # Take down whatever the launch made, even when the launch failed part way.
        closed = (
            not args.copy.exists()
            or subprocess.run([front_clone, "close", str(args.copy)]).returncode == 0
        )
        shutil.rmtree(args.config, ignore_errors=True)
    record = {
        "reason": reason,
        "spent": stint.spent,
        "budget": args.budget,
        "principal": stint.principal,
        "head": stint.head,
        "minutes": round((time.time() - started) / 60, 1),
        "closed": closed,
        "notes": stint.notes,
        "principalContext": stint.context,
        "calls": [
            {k: c[k] for k in ("name", "session", "resumed", "seconds", "commits")}
            for c in stint.calls
        ],
    }
    (args.stint / "stint.json").write_text(json.dumps(record, indent=2))
    final = f"{stint.context[-1]['tokens']:,}" if stint.context else "none"
    print(
        f"yield: {reason} ({stint.spent}/{args.budget} iterations, {len(stint.calls)} calls,"
        f" {len(stint.notes)} notes, principal context {final} tokens, {record['minutes']} min)"
    )
    if not closed:
        print(f"the work copy is kept: {args.copy}")
    return 0 if reason == "done" and closed else 1


if __name__ == "__main__":
    raise SystemExit(main())
