"""The build-region traverse — one `phase:build` issue carried to an open PR.

Deterministic end to end: every branch in the graph is code here, and the only
judgment in a traverse happens inside the agents it launches. Nothing is caught,
retried or degraded — a job that did not come back clean, a verification that did
not hold, and a preflight finding all end the traverse escalated, with the books
complete, and a retry is the caller invoking this again.

This module is the single writer of an issue's phase label and the single writer
of the traverse-grain ledger rows, which is what lets one lock per issue make the
whole thing serial.
"""

import fcntl
import json
import os
import signal
import subprocess
import sys
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import FrameType
from urllib.parse import quote

from dev_playbook import gitrepo
from dev_playbook.factory import launcher, ledger

# Where the per-issue locks live. A lock file is created and never removed: the
# lock rides the open file descriptor, so a leftover file holds nothing and a
# stale lock cannot exist.
LOCK_DIR = Path("~/.local/share/claude-measure/locks").expanduser()

# Where every repo this factory runs is checked out. The workspace is flat — one
# directory per repo, named by the slug's second half — which is what makes
# `owner/name` the only address a caller needs.
WORKSPACE_DIR = Path("~/workspace").expanduser()

# The two modes a traverse runs under. `user-rework` is validated and recorded
# here and means nothing else yet — the lap it names belongs to the merge
# boundary.
AUTO = "auto"
USER_REWORK = "user-rework"
MODES = (AUTO, USER_REWORK)

# The labels this graph reads. The phase label is the program counter, and a
# spike is refused outright: it opens no PR, so there is nothing here to run it
# through.
PHASE_PREFIX = "phase:"
SPIKE_LABEL = "mode:spike"

# The two nodes, and the two phases a traverse may enter at.
BUILD = "build"
OPEN_PR = "open-pr"
PR_REVIEW = "pr-review"

# The graph, declared rather than walked: the phase a traverse enters at, and the
# nodes it runs from there. Entering at `pr-review` skips the build, which is
# what a re-review of work already committed does.
GRAPH = {BUILD: (BUILD, OPEN_PR), PR_REVIEW: (OPEN_PR,)}

# Every definition this graph can launch, so a missing one is found at traverse
# start rather than halfway through a run that has already spent money.
DEFINITIONS = (BUILD, OPEN_PR)

# The node's own word for work that finished. Anything else it reports — its own
# `escalated` included — ends the traverse.
DONE = "done"

# The report envelope every node is launched under: a top-level `outcome` the
# graph branches on and a `gist` for whoever reads the row, and nothing else.
# Everything the script needs after a node is durable in git and on GitHub, and
# is read from there rather than taken on the agent's word.
REPORT_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "outcome": {"type": "string", "enum": [DONE, "escalated"]},
        "gist": {"type": "string"},
    },
    "required": ["outcome", "gist"],
    "additionalProperties": False,
}

# One per node, because a node's schema is the node's own and the two are free to
# diverge as the graph grows. Today they are the one envelope above.
BUILD_SCHEMA = REPORT_SCHEMA
OPEN_PR_SCHEMA = REPORT_SCHEMA

# Where an issue's worktree sits inside its checkout, and the branch it carries.
WORKTREES = Path(".claude") / "worktrees"

# The two line prefixes `git worktree list --porcelain` writes, and the namespace
# a branch line names its ref in. The porcelain form rather than the one meant
# for reading, because it is the form git undertakes not to change.
WORKTREE_RECORD = "worktree "
BRANCH_RECORD = "branch "
HEADS = "refs/heads/"

# The payload keys this module writes. Named once, because `factory-status` will
# read them and a typo on either side is a query that answers with nothing.
MODE = "mode"
REASON = "reason"
NODE = "node"
SESSION_ID = "session_id"
FROM = "from"
TO = "to"
PR_URL = "pr_url"

# Why a job's terminal row was written by the sweep rather than by the launcher
# that started it, recorded so the two are told apart on the row. The key is this
# module's own; the rest of that row's keys are the launcher's, and are taken
# from it by name rather than typed out again here.
SWEPT = "swept"
ORPHAN_RECOVERY = "orphan-recovery"
KILL_CASCADE = "kill-cascade"

# The exit status a killed traverse leaves. Nonzero, because the traverse did not
# finish — the JSON line on stdout belongs to the two statuses that did.
EXIT_KILLED = 1

# The signals a traverse takes its children down on. The ledger's own deferred
# pair, not a second tuple beside it: the trap writes the books, so a signal
# trapped here that the store did not hold off for the length of a write would
# be one whose handler could deadlock against the write it interrupted. SIGKILL
# is absent because it cannot be trapped — that is what `PR_SET_PDEATHSIG` in
# the launcher is for.
TRAPPED = ledger.DEFERRED_SIGNALS

# The one `pgrep` exit that is an answer rather than a fault: it looked, and
# nothing is running under that session id.
PGREP_NO_MATCH = 1


class TraverseError(Exception):
    """The traverse cannot start, or cannot go on — raised, never degraded past."""


class _Escalated(Exception):
    """The graph's own stop signal, raised where the trouble is and caught once.

    Control flow, not a failure: it carries the three things the escalation row
    records from wherever the traverse gave up — deep inside a node launch, or at
    the label read before anything has spawned — up to the one place that writes
    the books and returns. Threading that back by hand would put a check after
    every step of a sequence whose whole point is that it reads as a sequence.
    """

    def __init__(
        self, reason: str, node: str | None = None, session_id: str | None = None
    ) -> None:
        """Hold what the escalation row names: why, and which job if any."""
        self.reason = reason
        self.node = node
        self.session_id = session_id
        super().__init__(reason)


@dataclass(frozen=True)
class TraverseOutcome:
    """How a traverse ended, in the two statuses a caller can be handed.

    `killed` is never here: a traverse taken down by a signal dies inside its
    trap, so there is nobody left to return to.
    """

    status: str
    pr_url: str | None = None
    session_id: str | None = None


def _say(message: str) -> None:
    """Put one progress line on stderr, so stdout stays one parseable JSON line."""
    print(message, file=sys.stderr, flush=True)


def _gate_mode(mode: str) -> None:
    """Refuse a mode the graph does not run, before the store is ever touched.

    One of the two things judged ahead of the lock, because a traverse that
    cannot run must leave no trace: a `traverse-start` written and then abandoned
    would close the window of whatever traverse of this issue is genuinely live.
    """
    if mode not in MODES:
        raise TraverseError(f"a traverse runs in one of {MODES}, never {mode!r}")


def checkout_of(repo: str, workspace_dir: Path) -> Path:
    """The local checkout a repo slug names, refused when it is not there.

    The workspace is flat — one directory per repo, named by the slug's second
    half — so the owner half addresses GitHub and nothing on disk. A slug with no
    checkout is the caller naming a repo this machine has never cloned, and it is
    judged here, ahead of the lock, so nothing is written for a traverse that
    cannot run.
    """
    if repo.count("/") != 1 or not all(repo.split("/")):
        raise TraverseError(
            f"a traverse addresses its issue by an owner/name slug, never {repo!r}"
        )
    checkout = workspace_dir / repo.split("/")[1]
    if not (checkout / ".git").exists():
        raise TraverseError(
            f"{repo} is not checked out at {checkout}, so there is nothing to traverse"
        )
    return checkout


def lock_path(repo: str, issue: int, lock_dir: Path) -> Path:
    """The lock file standing for one `(repo, issue)` pair.

    The slug's separator is percent-encoded rather than swapped for a dash,
    because a dash is a character slugs already contain: `a/b-c` and `a-b/c`
    would otherwise land on one lock and each would read as the other running.
    """
    return lock_dir / f"{quote(repo, safe='')}-{issue}.lock"


@contextmanager
def _locked(repo: str, issue: int, lock_dir: Path) -> Iterator[None]:
    """Hold this issue's lock for the block, or refuse to start at all.

    Non-blocking by design. A held lock means another traverse of this issue is
    live, and the answer is to stop immediately rather than queue behind it:
    waiting would leave two traverses of one issue running back to back over a
    branch and a label the first is still moving.

    Nothing is written before this succeeds. A second `traverse-start` is itself
    a window closer, so a traverse that announced itself and then found the lock
    held would have closed the live traverse's window on its way past — and every
    job that traverse is still running would read as finished.

    The lock rides the descriptor, so it is released by the close in `finally`
    however the block ends, and the file left behind holds nothing. That is why
    nothing removes it: an unlink would race the next traverse's open, and a
    leftover file is harmless where that race is not.
    """
    lock_dir.mkdir(parents=True, exist_ok=True)
    path = lock_path(repo, issue, lock_dir)
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError as error:
        os.close(descriptor)
        raise TraverseError(
            f"another traverse of {repo}#{issue} holds {path} and is still "
            f"running, so this one will not start"
        ) from error
    try:
        yield
    finally:
        os.close(descriptor)


@dataclass(frozen=True)
class _Traverse:
    """One invocation: the issue it carries, and every seam it reaches through.

    Held together rather than threaded through a dozen parameters, because every
    step below needs the addresses and most need two or three of the seams.
    """

    repo: str
    issue: int
    mode: str
    checkout: Path
    db_path: Path
    agents_dir: Path
    claude_cmd: Sequence[str]
    gh_cmd: Sequence[str]
    timeout_s: float
    grace_s: float

    # --- the sequence ---

    def run(self) -> TraverseOutcome:
        """The whole traverse, from the orphan sweep to a terminal ledger row.

        Every way out of the graph closes the window — the one the graph knows
        about and the one it does not.
        """
        self._sweep(ORPHAN_RECOVERY)
        ledger.traverse_start(
            self.repo, self.issue, {MODE: self.mode}, db_path=self.db_path
        )
        with self._trapped():
            try:
                return self._graph()
            except _Escalated as escalated:
                return self._record_escalation(escalated)
            except Exception as failure:
                # Not a way this graph knows a traverse can end: the harness
                # breaking one of its promises, a git call that failed, the
                # store itself. The books are completed all the same, because a
                # window left open reads as a live traverse for good and every
                # job of the issue reads as still running with it — and then the
                # failure goes on rising, because nothing here understood it
                # well enough to turn it into an outcome anyone could act on.
                self._record_escalation(
                    _Escalated(f"{type(failure).__name__}: {failure}")
                )
                raise

    def _graph(self) -> TraverseOutcome:
        """The nodes themselves, in the order this issue's phase calls for."""
        nodes = self._nodes()
        worktree = self._worktree()
        self._preflight(worktree)
        if BUILD in nodes:
            self._build(worktree)
        return self._open_pr(worktree)

    def _nodes(self) -> tuple[str, ...]:
        """The nodes this issue's labels call for — the phase label is the counter.

        Nothing else about readiness is re-derived. Whether the issue was fit to
        cross into the factory was settled at its release, and asking again here
        would let a traverse overrule a decision that is the user's.
        """
        labels = self._labels()
        if SPIKE_LABEL in labels:
            raise _Escalated(
                f"{self.repo}#{self.issue} carries {SPIKE_LABEL}, and a spike opens "
                f"no pull request for this graph to reach"
            )
        phases = [
            label.removeprefix(PHASE_PREFIX)
            for label in labels
            if label.startswith(PHASE_PREFIX)
        ]
        if len(phases) != 1 or phases[0] not in GRAPH:
            runnable = ", ".join(f"{PHASE_PREFIX}{phase}" for phase in GRAPH)
            carried = ", ".join(f"{PHASE_PREFIX}{phase}" for phase in phases) or "none"
            raise _Escalated(
                f"{self.repo}#{self.issue} carries {carried} where this graph runs "
                f"exactly one of {runnable}"
            )
        _say(f"{self.repo}#{self.issue}: entering at {PHASE_PREFIX}{phases[0]}")
        return GRAPH[phases[0]]

    def _build(self, worktree: Path) -> None:
        """Run the build node, verify what it left behind, and move the label."""
        self._launch(BUILD, worktree, BUILD_SCHEMA)
        self._verify_build(worktree)
        self._gh(
            "issue",
            "edit",
            str(self.issue),
            "--repo",
            self.repo,
            "--add-label",
            f"{PHASE_PREFIX}{PR_REVIEW}",
            "--remove-label",
            f"{PHASE_PREFIX}{BUILD}",
        )
        ledger.phase_transition(
            self.repo, self.issue, {FROM: BUILD, TO: PR_REVIEW}, db_path=self.db_path
        )
        _say(f"{self.repo}#{self.issue}: {BUILD} -> {PR_REVIEW}")

    def _verify_build(self, worktree: Path) -> None:
        """Refuse to advance the board on anything but the facts the node left.

        A node reporting `done` is a claim. That every edit it made is a commit,
        that the commit is on `issue-<N>`, and that `issue-<N>` is on origin at
        that same sha, are the facts, and only the facts move the label.

        The tree is read before origin is, because the two ways work goes
        missing without moving a sha are both local. A node that edits and never
        commits leaves `issue-<N>` exactly where the lap before it did, and a
        node that commits onto a detached HEAD leaves it there too — so a
        comparison against origin alone agrees with itself and passes over work
        the pull request will never show. Neither is hypothetical on a rework
        lap, where the branch is already on origin when the node starts.
        """
        local = self._git(worktree, "rev-parse", self._branch())
        head = self._git(worktree, "rev-parse", "HEAD")
        if head != local:
            raise _Escalated(
                f"{BUILD} reported {DONE} but {worktree} is at {head} on a "
                f"detached HEAD where {self._branch()} is at {local}, so the "
                f"branch a review reads holds none of what it committed",
                node=BUILD,
            )
        pending = self._git(worktree, "status", "--porcelain")
        if pending:
            raise _Escalated(
                f"{BUILD} reported {DONE} but left {worktree} uncommitted:\n{pending}",
                node=BUILD,
            )
        pushed = self._origin_sha(self._branch())
        if pushed is None:
            raise _Escalated(
                f"{BUILD} reported {DONE} but {self._branch()} is not on origin, so "
                f"the work it committed is nowhere a review can read it",
                node=BUILD,
            )
        if local != pushed:
            raise _Escalated(
                f"{BUILD} reported {DONE} but {self._branch()} is {local} in the "
                f"worktree and {pushed} on origin, so the branch was never fully "
                f"pushed",
                node=BUILD,
            )

    def _open_pr(self, worktree: Path) -> TraverseOutcome:
        """Run the open-pr node, then read the PR off GitHub rather than the report.

        The URL is never lifted from what the agent said. A node that believes it
        opened a PR and did not would otherwise hand back a link to nothing, and
        the traverse would end `pr-ready` over an issue with no pull request.
        """
        self._launch(OPEN_PR, worktree, OPEN_PR_SCHEMA)
        url = self._pr_url()
        if url is None:
            raise _Escalated(
                f"{OPEN_PR} reported {DONE} but no pull request is open on "
                f"{self._branch()}",
                node=OPEN_PR,
            )
        ledger.traverse_end(
            self.repo,
            self.issue,
            {ledger.STATUS: ledger.PR_READY, PR_URL: url},
            db_path=self.db_path,
        )
        _say(f"{self.repo}#{self.issue}: pr-ready at {url}")
        return TraverseOutcome(ledger.PR_READY, pr_url=url)

    # --- launching a node ---

    def _launch(self, node: str, worktree: Path, schema: Mapping[str, object]) -> None:
        """Launch one node and refuse anything but a clean process reporting done.

        Zero retries live here. Every way a job can fail — the process
        classifications and the node's own `escalated` alike — ends the traverse,
        and a retry is the caller invoking `traverse_issue` again from the top.

        `LaunchAborted` is the one launcher failure caught, because it is not a
        failure of the run: it means nothing spawned and nothing was spent, and
        it carries the findings an operator has to fix. Every other
        `LauncherError` is the harness breaking a promise mid-flight and leaves
        as itself.
        """
        _say(f"{self.repo}#{self.issue}: launching {node}")
        try:
            outcome = launcher.launch_job(
                self.repo,
                self.issue,
                node,
                worktree,
                str(self.issue),
                schema,
                {MODE: self.mode, NODE: node},
                db_path=self.db_path,
                agents_dir=self.agents_dir,
                claude_cmd=self.claude_cmd,
                timeout_s=self.timeout_s,
                grace_s=self.grace_s,
            )
        except launcher.LaunchAborted as aborted:
            raise _Escalated(
                f"{node} could not be launched: {'; '.join(aborted.findings)}",
                node=node,
            ) from aborted
        if outcome.process_outcome != launcher.CLEAN:
            raise _Escalated(
                f"{node} ended {outcome.process_outcome}",
                node=node,
                session_id=outcome.session_id,
            )
        if outcome.task_outcome != DONE:
            raise _Escalated(
                f"{node} reported {outcome.task_outcome!r}",
                node=node,
                session_id=outcome.session_id,
            )

    def _preflight(self, worktree: Path) -> None:
        """Refuse a launch that would be metered, or a node with no definition.

        The definition roster is checked whole and here rather than per launch,
        because a graph that spends an hour on a build and then finds `open-pr`
        missing has burned the build for nothing.
        """
        try:
            launcher.preflight(worktree, os.environ)
        except launcher.LaunchAborted as aborted:
            raise _Escalated(
                f"this launch would not run on the subscription: "
                f"{'; '.join(aborted.findings)}"
            ) from aborted
        missing = [
            str(self.agents_dir / f"{node}.md")
            for node in DEFINITIONS
            if not (self.agents_dir / f"{node}.md").is_file()
        ]
        if missing:
            raise _Escalated(
                f"this graph launches {DEFINITIONS} and these have no definition: "
                f"{', '.join(missing)}"
            )

    # --- the worktree ---

    def _branch(self) -> str:
        """The one branch this issue's work lives on."""
        return f"issue-{self.issue}"

    def _worktree(self) -> Path:
        """The issue's worktree, created on a fresh base or taken exactly as found.

        A worktree that is already there is reused untouched — no freshness
        check, no rebase. Whether work in flight should be rebased onto a moved
        `main` is a judgment about the issue, not about this traverse, and it
        belongs to the manager above.
        """
        worktree = self.checkout / WORKTREES / self._branch()
        if worktree.exists():
            self._gate_reuse(worktree)
            _say(f"{self.repo}#{self.issue}: reusing {worktree}")
            return worktree
        self._git(self.checkout, "fetch", "origin", "main")
        local = self._git(self.checkout, "rev-parse", "origin/main")
        remote = self._origin_sha("main")
        if local != remote:
            raise _Escalated(
                f"origin/main is {local} here and {remote} on GitHub even after a "
                f"fetch, so a branch cut now would be off a base nobody else has"
            )
        worktree.parent.mkdir(parents=True, exist_ok=True)
        self._git(
            self.checkout,
            "worktree",
            "add",
            str(worktree),
            "-b",
            self._branch(),
            "origin/main",
        )
        _say(f"{self.repo}#{self.issue}: created {worktree} off {local}")
        return worktree

    def _gate_reuse(self, worktree: Path) -> None:
        """Refuse a directory at the worktree path that git does not answer for.

        A directory being there proves nothing. A `git worktree remove` refused
        over untracked files leaves the tree standing, and a re-cloned checkout
        leaves one whose link points nowhere — both of which an existence check
        reuses happily, and both of which break the first git command a node
        runs, deep inside a launch that has already been paid for. The registry
        is asked instead, because it is what every git command in that tree will
        answer from.

        The branch is judged with it. A tree on some other branch would take the
        node's commits, and the push and the verification would then read a
        branch nothing was written to.
        """
        registered = self._registrations()
        here = worktree.resolve()
        if here not in registered:
            raise _Escalated(
                f"{worktree} is a directory {self.checkout} has no worktree "
                f"registered at, so nothing launched into it would be working in "
                f"a git tree at all"
            )
        branch = registered[here]
        if branch != self._branch():
            raise _Escalated(
                f"{worktree} is checked out on {branch or 'a detached HEAD'} where "
                f"this issue's work belongs on {self._branch()}"
            )

    def _registrations(self) -> dict[Path, str | None]:
        """Every worktree this checkout holds, by path, and the branch each is on.

        The porcelain form is parsed rather than the one meant for reading,
        because it is the form git promises not to change: one `worktree <path>`
        line opening each record, and a `branch <ref>` line only where that
        record has one — a detached tree simply has none, which is what leaves
        the branch None.
        """
        registrations: dict[Path, str | None] = {}
        here: Path | None = None
        for line in self._git(
            self.checkout, "worktree", "list", "--porcelain"
        ).splitlines():
            if line.startswith(WORKTREE_RECORD):
                here = Path(line.removeprefix(WORKTREE_RECORD)).resolve()
                registrations[here] = None
            elif line.startswith(BRANCH_RECORD) and here is not None:
                registrations[here] = line.removeprefix(BRANCH_RECORD).removeprefix(
                    HEADS
                )
        return registrations

    # --- the orphan sweep and the kill cascade ---

    @contextmanager
    def _trapped(self) -> Iterator[None]:
        """Take every live child down with this process, on a signal it can catch.

        The trap completes the books itself rather than letting the unwind do it:
        it kills what it launched, files each child's terminal row, and closes the
        window with a `killed` end. Then it raises `SystemExit`, which is what
        stops `launch_job` writing a second report for the job just filed — the
        exception leaves through the supervision instead of returning into it.

        Both signals are put back to the default first, so a second one while
        this is running kills outright rather than re-entering a handler already
        part-way through the books. They are put back by walking `TRAPPED`, so a
        signal added to the pair cannot be left trapped with no way out.

        `PR_SET_PDEATHSIG` on the children covers what no trap can: a launcher
        SIGKILLed or OOM-killed runs none of this, the children still die, and the
        next invocation's sweep files their rows.
        """

        def die(number: int, frame: FrameType | None) -> None:
            for trapped in TRAPPED:
                signal.signal(trapped, signal.SIG_DFL)
            _say(f"{self.repo}#{self.issue}: signal {number}, taking children down")
            self._sweep(KILL_CASCADE)
            ledger.traverse_end(
                self.repo,
                self.issue,
                {ledger.STATUS: ledger.KILLED},
                db_path=self.db_path,
            )
            raise SystemExit(EXIT_KILLED)

        restore = [(number, signal.signal(number, die)) for number in TRAPPED]
        try:
            yield
        finally:
            for number, handler in restore:
                signal.signal(number, handler)

    def _sweep(self, why: str) -> None:
        """Finish the books for every job of this issue that has no terminal row.

        Scoped to this `(repo, issue)` and nothing wider. Other pairs' jobs belong
        to other traverses, which are running right now under their own locks, and
        a sweep that reached them would kill live work and file it as dead.

        A job is found in the process table by its session id, which rides the
        child's command line as `--session-id`, so the match is exact rather than
        a guess at what a claude process looks like. One that is still running is
        SIGTERMed; one that is already gone needs no signal. Either way its row is
        written, because completing the books is the whole duty here — a launch
        with no report reads as live for good.
        """
        for row in ledger.live_jobs(
            repo=self.repo, issue=self.issue, db_path=self.db_path
        ):
            session_id = str(row.session_id)
            killed = _terminate(session_id)
            _say(f"{self.repo}#{self.issue}: sweeping {row.node} {session_id} ({why})")
            ledger.job_report(
                self.repo,
                self.issue,
                str(row.node),
                session_id,
                {
                    launcher.PROCESS_OUTCOME: launcher.DIED,
                    launcher.TASK_OUTCOME: None,
                    launcher.STRUCTURED_OUTPUT: None,
                    launcher.EXIT_CODE: None,
                    launcher.KILL: launcher.SIGTERM if killed else None,
                    SWEPT: why,
                },
                db_path=self.db_path,
            )

    # --- writing the escalation ---

    def _record_escalation(self, escalated: _Escalated) -> TraverseOutcome:
        """Write the two rows an escalated exit leaves, and hand back the outcome.

        `traverse-end` follows the escalation row rather than replacing it: the
        escalation says why, and the end is what closes the window, so a traverse
        that wrote only the first would leave its issue open for good.
        """
        _say(f"{self.repo}#{self.issue}: escalated — {escalated.reason}")
        ledger.traverse_escalation(
            self.repo,
            self.issue,
            {
                REASON: escalated.reason,
                NODE: escalated.node,
                SESSION_ID: escalated.session_id,
            },
            db_path=self.db_path,
        )
        ledger.traverse_end(
            self.repo,
            self.issue,
            {ledger.STATUS: ledger.ESCALATED},
            db_path=self.db_path,
        )
        return TraverseOutcome(ledger.ESCALATED, session_id=escalated.session_id)

    # --- talking to git and GitHub ---

    def _git(self, where: Path, *arguments: str) -> str:
        """One git command in a checkout or a worktree, its stdout stripped.

        `no_git_env` is what makes `-C` authoritative. A traverse runs from
        wherever the manager launched it — often a worktree, where git exports an
        absolute `GIT_DIR` that outranks the directory named here.
        """
        done = subprocess.run(
            ["git", "-C", str(where), *arguments],
            capture_output=True,
            text=True,
            env=gitrepo.no_git_env(),
        )
        if done.returncode != 0:
            raise _Escalated(
                f"git {' '.join(arguments)} in {where} failed: {done.stderr.strip()}"
            )
        return done.stdout.strip()

    def _gh(self, *arguments: str) -> str:
        """One gh command that has to succeed, its stdout stripped."""
        done = subprocess.run(
            [*self.gh_cmd, *arguments], capture_output=True, text=True
        )
        if done.returncode != 0:
            raise _Escalated(f"gh {' '.join(arguments)} failed: {done.stderr.strip()}")
        return done.stdout.strip()

    def _gh_or_absent(self, *arguments: str) -> str | None:
        """One gh command whose failure is an answer rather than a fault.

        Exactly two reads use this, and both are asking whether something exists
        on GitHub: a branch, and a pull request. A 404 and an unreachable network
        are not told apart, and deliberately so — both end the traverse escalated
        with the label unmoved, which is the safe direction to be wrong in.
        """
        done = subprocess.run(
            [*self.gh_cmd, *arguments], capture_output=True, text=True
        )
        if done.returncode != 0:
            return None
        return done.stdout.strip() or None

    def _labels(self) -> list[str]:
        """Every label on the issue, by name."""
        listed = self._gh(
            "issue",
            "view",
            str(self.issue),
            "--repo",
            self.repo,
            "--json",
            "labels",
            "--jq",
            ".labels[].name",
        )
        return listed.splitlines()

    def _origin_sha(self, branch: str) -> str | None:
        """The commit GitHub holds for one branch, or None when it holds none."""
        return self._gh_or_absent(
            "api", f"repos/{self.repo}/branches/{branch}", "--jq", ".commit.sha"
        )

    def _pr_url(self) -> str | None:
        """The URL of the open pull request on this issue's branch, if there is one."""
        listed = self._gh_or_absent(
            "pr",
            "list",
            "--repo",
            self.repo,
            "--head",
            self._branch(),
            "--json",
            "url",
            "--jq",
            ".[].url",
        )
        return listed.splitlines()[0] if listed else None


def _terminate(session_id: str) -> bool:
    """SIGTERM whatever process is running under `session_id`; say whether any was.

    The session id is on the child's command line, so `pgrep -f` matches that job
    and nothing else. `pgrep` exits 1 when it matches nothing, which is not a
    failure here: a job whose process is already gone still needs its row.

    Every other nonzero exit is a probe that never got to look — a pattern it
    would not compile, a fault in the tool itself — and it raises. Read as "no
    such process" instead, it would file the job's terminal row while the
    session is still running, and the one thing that would have taken it down
    is the signal this decided not to send.
    """
    found = subprocess.run(["pgrep", "-f", session_id], capture_output=True, text=True)
    if found.returncode == PGREP_NO_MATCH:
        return False
    if found.returncode != 0:
        raise TraverseError(
            f"pgrep could not say whether {session_id} is still running "
            f"(exit {found.returncode}): {found.stderr.strip()}"
        )
    pids = [int(line) for line in found.stdout.split()]
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            # It exited between the probe and the signal, which is the outcome
            # being asked for anyway.
            continue
    return bool(pids)


def traverse_issue(
    repo: str,
    issue: int,
    mode: str,
    *,
    db_path: Path = ledger.DB_PATH,
    lock_dir: Path = LOCK_DIR,
    workspace_dir: Path = WORKSPACE_DIR,
    agents_dir: Path = launcher.AGENTS_DIR,
    claude_cmd: Sequence[str] = ("claude",),
    gh_cmd: Sequence[str] = ("gh",),
    timeout_s: float = launcher.DEADLINE_SECONDS,
    grace_s: float = launcher.GRACE_SECONDS,
) -> TraverseOutcome:
    """Carry one issue from its phase label to an open PR, or to an escalation.

    Two things are judged before anything is written or locked — the mode, and
    that the repo is checked out — because a traverse that cannot run must leave
    no trace. Everything discovered after the lock is held runs the full
    book-keeping instead, ending on a `traverse-end` whatever happens.

    The keyword parameters are the test seam; production callers pass none of
    them.
    """
    _gate_mode(mode)
    checkout = checkout_of(repo, workspace_dir)
    with _locked(repo, issue, lock_dir):
        return _Traverse(
            repo=repo,
            issue=issue,
            mode=mode,
            checkout=checkout,
            db_path=db_path,
            agents_dir=agents_dir,
            claude_cmd=claude_cmd,
            gh_cmd=gh_cmd,
            timeout_s=timeout_s,
            grace_s=grace_s,
        ).run()


def main(argv: Sequence[str] | None = None, **seams: object) -> int:
    """Run one traverse from the command line and print its terminal status.

    Exactly one JSON line on stdout, and only on a terminal status: everything
    that goes wrong before the ledger is touched leaves as a raised
    `TraverseError`, and a killed traverse exits from its trap without printing.
    Progress goes to stderr, so a caller can read stdout without filtering it.

    `seams` is the test seam, forwarded whole to `traverse_issue`; the shim
    passes none of it.
    """
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 3:
        raise TraverseError(
            f"usage: traverse-issue <owner/name> <issue> <{'|'.join(MODES)}>, "
            f"given {arguments}"
        )
    repo, issue, mode = arguments
    outcome = traverse_issue(repo, int(issue), mode, **seams)  # type: ignore[arg-type]
    line: dict[str, object] = {ledger.STATUS: outcome.status}
    if outcome.pr_url is not None:
        line[PR_URL] = outcome.pr_url
    if outcome.status == ledger.ESCALATED:
        line[SESSION_ID] = outcome.session_id
    print(json.dumps(line), flush=True)
    return 0
