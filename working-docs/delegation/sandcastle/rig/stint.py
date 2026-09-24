"""The headless driver: run one unattended stint from launch to yield.

The loop, the stop rules, and the checkpoints live here. One step runs one
agent call and is swappable: `sandcastle` runs it sealed through `call.mjs`,
`local` runs `claude -p` on the host in the copy. Each call is fresh except
the principal's, which is one conversation resumed at every checkpoint.

Between calls the driver reads the copy as plain files, never with host git,
and refuses a symlink on any path it reads, so a planted link cannot pull a
host file into a prompt.

Usage:
    stint.py --lab LAB --copy COPY --stint STINT --workstream DIR
             --check CMD --budget N [--model M] [--step sandcastle|local]
             [--close]

COPY is a work copy front-clone opened, already holding the workstream DIR
(its WORKSTREAM.md, PLAN.md, and PROGRESS.md). STINT is the stint's folder on
the host. Writes STINT/stint.json, the stint's record, and exits 0 on done,
1 on any other yield.
"""

import argparse
import json
import re
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


def sandcastle_step(args, name: str, prompt: str, resume: str | None) -> dict:
    """Run one call sealed through call.mjs and return its record."""
    opts = {
        "lab": str(args.lab),
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


def local_step(args, name: str, prompt: str, resume: str | None) -> dict:
    """Run one call as `claude -p` on the host in the copy and return its record."""
    command = [
        "claude",
        "-p",
        "--model",
        args.model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--dangerously-skip-permissions",
    ]
    if resume:
        command += ["--resume", resume]
    before = head_sha(args.copy)
    started = time.time()
    done = subprocess.run(
        command, input=prompt, cwd=args.copy, capture_output=True, text=True
    )
    (args.stint / "calls" / f"{name}.log").write_text(done.stdout + done.stderr)
    messages = [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    init = next(
        (
            m
            for m in messages
            if m.get("type") == "system" and m.get("subtype") == "init"
        ),
        {},
    )
    final = next((m for m in messages if m.get("type") == "result"), {})
    after = head_sha(args.copy)
    listed = subprocess.run(
        ["git", "-C", str(args.copy), "rev-list", "--reverse", f"{before}..{after}"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    dirty = subprocess.run(
        ["git", "-C", str(args.copy), "status", "--porcelain", "--untracked-files=all"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    record = {
        "name": name,
        "session": final.get("session_id"),
        "resumed": resume,
        "apiKeySource": init.get("apiKeySource"),
        "seconds": round(time.time() - started),
        "isError": final.get("is_error"),
        "commits": listed,
        "uncommitted": dirty,
        "answer": final.get("result", ""),
    }
    (args.stint / "calls" / f"{name}.json").write_text(json.dumps(record, indent=2))
    if done.returncode:
        raise Yield(f"call {name} failed: exit {done.returncode}")
    return record


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

    def __init__(self, args):
        """Read the copy's HEAD and set the values every prompt shares."""
        self.args = args
        self.step = {"sandcastle": sandcastle_step, "local": local_step}[args.step]
        repo = (
            f"/home/agent/assignment/{args.copy.name}"
            if args.step == "sandcastle"
            else str(args.copy)
        )
        ws = args.workstream
        self.base = {
            "REPO": repo,
            "HEAD": f"{ws}/WORKSTREAM.md",
            "PLAN": f"{ws}/PLAN.md",
            "PROGRESS": f"{ws}/PROGRESS.md",
            "CHECK": args.check,
            "BUDGET": args.budget,
        }
        self.calls = []
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
            f"{name}: {record['seconds']}s session={record['session']} billed={record['apiKeySource']}"
            f" commits={len(record['commits'])} uncommitted={len(record['uncommitted'])}",
            flush=True,
        )
        if record["apiKeySource"] != "none":
            raise Yield(f"{name} billed {record['apiKeySource']}")
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
        record, end = self.call("principal-0", "principal-open")
        self.principal = record["session"]
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
                summaries.append(f"- {name}: {end.get('summary')}")
                if end.get("blocker"):
                    raise Yield(f"{name} blocked: {end['blocker']}")
                if not record["commits"]:
                    raise Yield(f"{name} committed nothing")
                after = self.plan()
                if (after["done"], after["open"]) != (before["done"], before["open"]):
                    raise Yield(f"{name} moved a checkpoint marker")
                if after["segment"] != before["segment"] - 1:
                    raise Yield(
                        f"{name} checked off {before['segment'] - after['segment']} tasks, not 1"
                    )
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


def main() -> int:
    """Parse the arguments, run the stint, write stint.json, and close the copy."""
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--lab", type=Path, required=True)
    p.add_argument("--copy", type=Path, required=True)
    p.add_argument("--stint", type=Path, required=True)
    p.add_argument("--workstream", required=True)
    p.add_argument("--check", required=True)
    p.add_argument("--budget", type=int, required=True)
    p.add_argument("--model", default="claude-sonnet-5")
    p.add_argument("--step", choices=["sandcastle", "local"], default="sandcastle")
    p.add_argument(
        "--close", action="store_true", help="front-clone close the copy at the yield"
    )
    args = p.parse_args()
    args.lab, args.copy, args.stint = (
        args.lab.resolve(),
        args.copy.resolve(),
        args.stint.resolve(),
    )
    (args.stint / "calls").mkdir(parents=True, exist_ok=True)
    stint = Stint(args)
    started = time.time()
    try:
        reason = stint.run()
    except Yield as y:
        reason = str(y)
    record = {
        "reason": reason,
        "spent": stint.spent,
        "budget": args.budget,
        "principal": stint.principal,
        "head": stint.head,
        "minutes": round((time.time() - started) / 60, 1),
        "calls": [
            {k: c[k] for k in ("name", "session", "resumed", "seconds", "commits")}
            for c in stint.calls
        ],
    }
    (args.stint / "stint.json").write_text(json.dumps(record, indent=2))
    print(
        f"yield: {reason} ({stint.spent}/{args.budget} iterations, {len(stint.calls)} calls, {record['minutes']} min)"
    )
    if args.close:
        subprocess.run(
            [str(RIG.parents[3] / "scripts" / "front-clone"), "close", str(args.copy)],
            check=True,
        )
    return 0 if reason == "done" else 1


if __name__ == "__main__":
    raise SystemExit(main())
