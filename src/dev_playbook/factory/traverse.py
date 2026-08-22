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
from collections.abc import Iterable, Iterator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import FrameType
from typing import Any
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

# The node that settles what a review suggested. It is not in the graph below:
# it is launched from inside the review loop, at a verdict point, because which
# verdict was reached is the whole of what decides whether it runs at all.
ADJUDICATOR = "adjudicator"

# The graph, declared rather than walked: the phase a traverse enters at, and the
# nodes it runs from there. Entering at `pr-review` skips the build, which is
# what a re-review of work already committed does.
GRAPH = {BUILD: (BUILD, OPEN_PR), PR_REVIEW: (OPEN_PR,)}

# The three reviewer definitions, the review name each opens its cycle header
# with, and which track elects which. The header name is what a track's own
# cycle and last-reviewed sha are looked up by, so the two spellings are held
# together here rather than derived from each other.
BUG_REVIEW = "bug-pr-review"
CODE_REVIEW = "code-pr-review"
DOC_REVIEW = "doc-pr-review"
REVIEW_NAMES = {
    BUG_REVIEW: "bug review",
    CODE_REVIEW: "code review",
    DOC_REVIEW: "doc review",
}

# Every definition this graph can launch, so a missing one is found at traverse
# start rather than halfway through a run that has already spent money.
DEFINITIONS = (BUILD, OPEN_PR, *REVIEW_NAMES, ADJUDICATOR)

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
# diverge as the graph grows. The two committing nodes are the one envelope
# above; a review adds the two counts of what it posted, which are on its report
# because the reviewer definitions put them there — the loop reads what it acts
# on from the threads themselves.
BUILD_SCHEMA = REPORT_SCHEMA
OPEN_PR_SCHEMA = REPORT_SCHEMA
REVIEW_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "outcome": {"type": "string", "enum": [DONE, "escalated"]},
        "gist": {"type": "string"},
        "blocking_count": {"type": "integer"},
        "suggestion_count": {"type": "integer"},
    },
    "required": ["outcome", "gist", "blocking_count", "suggestion_count"],
    "additionalProperties": False,
}

# The keys of the adjudicator's report beyond the shared envelope, and the one
# disposition outcome the loop acts on. `dispositions` is the single value this
# graph takes on an agent's word: everything else it needs after a node is
# durable in git or on GitHub and is read from there, but a fix-now ruling is
# written nowhere — the thread it names is deliberately left open and unmarked
# for the next cycle's reviewer — so the report is the only place it exists.
DISPOSITIONS = "dispositions"
DISPOSITION_OUTCOME = "outcome"
THREAD = "thread"
FIX = "fix"
FIX_NOW = "fix-now"
CALLOUTS = "callouts"

# What the adjudicator is launched under. The per-entry conditionals — `fix`
# with a fix-now, `reason` with a defer or a decline, `stub` with a defer — are
# the definition's to hold rather than the schema's, so the shape below requires
# only what every entry carries. The loop reads fix-now strictly all the same:
# a ruling with no fix in it stops the traverse rather than reaching a builder
# as a bare thread id.
ADJUDICATOR_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "outcome": {"type": "string", "enum": [DONE, "escalated"]},
        "gist": {"type": "string"},
        DISPOSITIONS: {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    THREAD: {"type": "string"},
                    DISPOSITION_OUTCOME: {
                        "type": "string",
                        "enum": [FIX_NOW, "defer", "decline"],
                    },
                    FIX: {"type": "string"},
                    "reason": {"type": "string"},
                    "stub": {"type": "integer"},
                },
                "required": [THREAD, DISPOSITION_OUTCOME],
                "additionalProperties": False,
            },
        },
        CALLOUTS: {"type": "array", "items": {"type": "string"}},
    },
    "required": ["outcome", "gist", DISPOSITIONS, CALLOUTS],
    "additionalProperties": False,
}

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
PR = "pr"
CYCLE = "cycle"
SHA = "sha"
BASELINE = "baseline"
VERDICT = "verdict"
BLOCKING_OPEN = "blocking_open"
BLOCKING_RESOLVED = "blocking_resolved"
SUGGESTION_OPEN = "suggestion_open"
SUGGESTION_RESOLVED = "suggestion_resolved"

# The one payload key this module reads that it does not yet write. A
# user-ordered lap records the cycle the cap's clock restarts behind, and the
# merge boundary is what will write it; until then no start carries one and the
# baseline is zero.
BASELINE_CYCLE = "baseline_cycle"

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

# The shape of a review's cycle header — `<review> · <sha> · cycle <n> ·
# <session id>` — which the review contract fixes and this module only reads.
# The separator is the interpunct with a space on each side, so a review name or
# a session id carrying an ordinary dash splits into no extra field.
HEADER_SEPARATOR = " · "
HEADER_FIELDS = 4
CYCLE_WORD = "cycle "

# The two review tracks, and how a changed file is sorted into them. Content
# kind picks the track, and the kinds are told apart by suffix alone so the
# election is mechanical: `.md` is documentation, `.html` is rendered output
# nobody reviews as source, and everything else — `.py`, `.sh`, extensionless
# scripts and hooks, `Makefile*`, config — is code.
CODE_TRACK = "code"
DOC_TRACK = "doc"
DOC_SUFFIX = ".md"
IGNORED_SUFFIX = ".html"

# Which reviews a track runs. The code track runs two — a bug hunt and a
# fidelity-and-convention audit — because they read the same diff for different
# things and neither covers the other.
REVIEWS = {CODE_TRACK: (BUG_REVIEW, CODE_REVIEW), DOC_TRACK: (DOC_REVIEW,)}

# What `pulls/{n}/files` calls a file this pull request creates, and how many
# changed documentation lines make an edit substantive rather than the echo a
# code change forces.
ADDED = "added"
SUBSTANTIVE_DOC_LINES = 10
CHANGED_FILE_FIELDS = 4

# The one read of the pull request's threads, stated in pr-feedback.md and
# copied here field for field — `isOutdated` and `subjectType` included, which
# nothing below reads. The query is the documented one taken whole rather than
# trimmed to today's callers; in particular `isOutdated` does not drive
# `_thread`'s `line`/`originalLine` fallback, which keys on `line is None`
# alone. `reviewThreads` caps at 100 a page and returns
# them oldest first, so it is paged: the threads a long-running pull request
# would drop are its newest, and a verdict that never sees an open Blocking
# thread is a convergence declared falsely.
THREADS_QUERY = """query {{ repository(owner:"{owner}", name:"{name}") {{
  pullRequest(number:{number}) {{ reviewThreads(first:100, after:{after}) {{
    pageInfo {{ hasNextPage endCursor }}
    nodes {{
      id isResolved isOutdated path line originalLine subjectType
      comments(first:10) {{ nodes {{ databaseId body }} }}
    }}
  }} }} }} }}"""

# The two severities a review writes, folded for comparison, and the decoration
# a first word may be wrapped in. A severity is matched against these rather
# than against a literal, because the tally that misses a Blocking thread is a
# convergence declared over a finding nobody addressed.
BLOCKING = "blocking"
SUGGESTION = "suggestion"
SEVERITY_DECORATION = "*_`~:.,;—-()[]\"'"

# The three ways a cycle ends, and how many autonomous cycles past the baseline
# a pull request gets before its unresolved Blocking threads end the traverse.
REWORK = "rework"
CONVERGED = "converged"
CAP_ESCALATED = "cap-escalated"
CYCLE_CAP = 4

# What a rework lap launches the build node under. The issue number opens it, on
# a line of its own, because that is the whole of an ordinary build's prompt and
# the node reads it the same way here.
REWORK_PROMPT = """{issue}

Rework lap. These Blocking threads on the pull request are unresolved, and they
are your work list:

{threads}

Read each thread's content with `gh api` — none of it is repeated here. Reply
`Fixed in <sha>` on each thread you fix, and never resolve a thread; the next
cycle's reviewer resolves what it verifies. The order is yours."""

# What a lap carrying fix-now items appends to the prompt above. These are the
# one thing a prompt states rather than addresses: the ruling that a suggestion
# rides this lap was made moments ago and written nowhere the node could read it,
# so the line after each id is the whole of what the item asks for. The threads
# themselves are still read live, exactly like the Blocking ones.
FIX_NOW_PROMPT = """

These Suggestion threads were ruled fix now, and each line is the whole of what
its thread is being asked for:

{items}

Reply `Fixed in <sha>` on each one you fix, and leave every one of them open,
the same as the threads above."""


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
        self,
        reason: str,
        node: str | None = None,
        session_id: str | None = None,
        payload: Mapping[str, object] | None = None,
    ) -> None:
        """Hold what the escalation row names: why, which job if any, and its own.

        `payload` is the keys one escalation carries that the others do not — the
        cap records the cycle it stopped at and the baseline it counted from — and
        it is merged into the row beside the three above.
        """
        self.reason = reason
        self.node = node
        self.session_id = session_id
        self.payload = dict(payload or {})
        super().__init__(reason)


@dataclass(frozen=True)
class _Failure:
    """One way a fanned-out review did not come back clean and reporting done.

    A fan-out does not raise where the trouble is, the way the sequential path
    does, because several jobs can fail at once: an exception would surface
    whichever one was read from first and lose what the rest said. So each job's
    failure is carried back as a value and every one of them is relayed together
    once the whole fan-out has finished.
    """

    reason: str
    node: str
    session_id: str | None = None


@dataclass(frozen=True)
class _PullRequest:
    """The one pull request an issue has, by the two names the loop addresses it by.

    The number is what every `gh api` path and GraphQL argument needs; the URL is
    what a person reading a ledger row needs. Read together off one call, so the
    two can never come from different answers.
    """

    number: int
    url: str


def _judge(node: str, outcome: launcher.JobOutcome) -> _Failure | None:
    """Whether a finished job came back clean and reporting done, and why not.

    One rule for both paths. The sequential launch raises what this returns and
    the fan-out carries it back as a value, and a second copy of the judgment
    would let a review be accepted on terms a build is refused on.
    """
    if outcome.process_outcome != launcher.CLEAN:
        return _Failure(
            f"{node} ended {outcome.process_outcome}", node, outcome.session_id
        )
    if outcome.task_outcome != DONE:
        return _Failure(
            f"{node} reported {outcome.task_outcome!r}", node, outcome.session_id
        )
    return None


def _relay(failures: Sequence[_Failure]) -> _Escalated:
    """Every failure of one fan-out, as the escalation that ends the traverse.

    Verbatim, and never summarized: what a node said about why it stopped is
    what reaches the operator. The two grain columns are filled only where one
    job answers for the escalation — with several failing they would have to name
    one of them and read as though the others had not happened.
    """
    if len(failures) == 1:
        return _Escalated(
            failures[0].reason, node=failures[0].node, session_id=failures[0].session_id
        )
    return _Escalated("; ".join(failure.reason for failure in failures))


def _abort_reason(node: str, aborted: launcher.LaunchAborted) -> str:
    """Why a node never spawned, worded once for both paths that report it.

    The fan-out carries an abort back as a value and the sequential path raises
    it, but an operator reads the same sentence either way — and a message built
    twice is a message the two copies drift apart on.
    """
    return f"{node} could not be launched: {'; '.join(aborted.findings)}"


def _pool(workers: int) -> ThreadPoolExecutor:
    """A pool whose threads block the ledger's deferred signals before their first job.

    The invariant `launcher._pump` is held to, and for the same reason: a Python
    handler runs on the main thread at its next bytecode boundary whatever any
    other thread's mask says, so one unblocked thread anywhere is a route back
    into the middle of a ledger write — and the traverse's own trap writes to
    that ledger. `initializer` runs inside each worker thread as it starts, which
    is exactly where the mask has to be set.
    """
    return ThreadPoolExecutor(
        max_workers=workers,
        initializer=signal.pthread_sigmask,
        initargs=(signal.SIG_BLOCK, TRAPPED),
    )


def _thread(node: Mapping[str, Any]) -> ReviewThread:
    """One GraphQL thread node as the plain record the verdict is computed from.

    The line falls back to `originalLine`. A fix that edits the anchored line
    itself flips its thread outdated and takes the live line away — which is
    exactly the thread a cycle is there to verify — so keying on the live line
    alone would lose the location of every thread that was actually addressed.

    A thread carrying no comment is refused rather than stood in for. Every
    severity is the first word of a thread's first comment, so such a thread has
    none to read: passed over with an empty body it counts as neither Blocking
    nor Suggestion and leaves the tally in silence, which is a convergence
    declared over a finding nobody read.
    """
    comments = node["comments"]["nodes"]
    if not comments:
        raise _Escalated(
            f"the review thread {node['id']} carries no comment to read a "
            f"severity from, and a thread the verdict cannot grade is a finding "
            f"it would drop without saying so"
        )
    return ReviewThread(
        thread_id=str(node["id"]),
        resolved=bool(node["isResolved"]),
        path=str(node["path"]),
        line=node["line"] if node["line"] is not None else node["originalLine"],
        body=str(comments[0]["body"]),
    )


def _fix_now(report: Mapping[str, object] | None, verdict: str) -> tuple[FixNow, ...]:
    """The suggestions the adjudicator ruled the coming lap should carry.

    Read strictly, and never salvaged. A fix-now entry is a whole instruction —
    which thread, and what it is being asked for — and half of one cannot be
    turned into a work item: the builder would be handed a thread id it was told
    to fix and no statement of the fix, and the thread's own text is the
    unruled suggestion the ruling was there to replace. So a malformed entry
    ends the traverse in the node's own name rather than reaching a prompt with
    the ruling quietly missing from it.

    The verdict the run was launched under is read as strictly. A fix-now is
    work for the lap that follows, and a convergence has no lap that follows —
    the definition downgrades the item to a deferral there. A ruling that
    arrives anyway can be neither carried nor dropped: the thread it names is
    left open by design, and the fix text is written on no thread, so a traverse
    that read past it would end `pr-ready` saying a suggestion is settled that
    nobody settled.
    """
    dispositions = (report or {}).get(DISPOSITIONS)
    if not isinstance(dispositions, list):
        raise _Escalated(
            f"{ADJUDICATOR} reported {DONE} with {DISPOSITIONS} as "
            f"{dispositions!r}, where the schema it was launched under requires "
            f"the list of what it settled",
            node=ADJUDICATOR,
        )
    ruled = []
    for entry in dispositions:
        if not isinstance(entry, Mapping):
            raise _Escalated(
                f"{ADJUDICATOR} reported a disposition that is not an object: "
                f"{entry!r}",
                node=ADJUDICATOR,
            )
        if entry.get(DISPOSITION_OUTCOME) != FIX_NOW:
            continue
        if verdict != REWORK:
            raise _Escalated(
                f"{ADJUDICATOR} ruled a suggestion {FIX_NOW} on a {verdict} "
                f"run, where no lap remains to carry it: {dict(entry)!r}",
                node=ADJUDICATOR,
            )
        thread, fix = entry.get(THREAD), entry.get(FIX)
        if not isinstance(thread, str) or not isinstance(fix, str) or not fix.strip():
            raise _Escalated(
                f"{ADJUDICATOR} ruled a suggestion {FIX_NOW} and left the rework "
                f"lap no fix to carry: {dict(entry)!r}",
                node=ADJUDICATOR,
            )
        ruled.append(FixNow(thread=thread, fix=fix))
    return tuple(ruled)


@dataclass(frozen=True)
class TraverseOutcome:
    """How a traverse ended, in the two statuses a caller can be handed.

    `killed` is never here: a traverse taken down by a signal dies inside its
    trap, so there is nobody left to return to.
    """

    status: str
    pr_url: str | None = None
    session_id: str | None = None


# --- the review loop's arithmetic ---
#
# Plain data in, plain data out, and no I/O anywhere below: everything the loop
# decides is decided here, so the decisions are read and tested without a
# process, a store or a network in the way.


@dataclass(frozen=True)
class CycleHeader:
    """One review's cycle header, the first line of the review body it posted.

    The loop keeps no state of its own between invocations. These lines are the
    state, living on the pull request beside the findings they belong to, which
    is what lets a relaunched traverse pick a loop back up from GitHub alone.
    """

    review: str
    sha: str
    cycle: int
    session_id: str


def parse_cycle_headers(first_lines: Iterable[str]) -> dict[str, CycleHeader]:
    """The newest header each review name has posted, by that name.

    The lines come in oldest first, as the reviews endpoint returns them. A line
    that is not a header is not an error — a comment carrying neither a cycle
    header nor an attribution line is the user's, and the user may write
    anything — so it is passed over rather than refused.

    Per name, never across names: election is recomputed every cycle, so a track
    can sit out one and come back. Handed the newest header on the pull request,
    which belongs to a sibling that did run, a returning track would start its
    delta at a commit it never read and skip everything between in silence.
    """
    newest: dict[str, CycleHeader] = {}
    for line in first_lines:
        header = _header(line)
        if header is None:
            continue
        standing = newest.get(header.review)
        if standing is None or header.cycle >= standing.cycle:
            newest[header.review] = header
    return newest


@dataclass(frozen=True)
class ChangedFile:
    """One file the pull request changes, as the election weighs it.

    Four fields off `pulls/{n}/files` and nothing else. `status` is what tells a
    new document from an edited one, which neither line count can: a file
    written this lap and a file rewritten this lap add the same lines.
    """

    path: str
    status: str
    additions: int
    deletions: int


def elect_tracks(changed: Iterable[ChangedFile]) -> tuple[str, ...]:
    """The review tracks this diff earns, from the changed files alone.

    Recomputed every cycle and never carried, so a lap that touches only code
    drops the doc track and a later lap that touches documentation brings it
    back. It takes no cycle number: every elected track runs every cycle, and no
    review stands down. A stand-down would deadlock the loop, because only the
    next cycle's reviewer may resolve a thread — a stood-down track's fixed
    threads would stay open for good, `blocking_open` would never reach zero,
    and a converged pull request would cap out.

    Documentation is earned rather than defaulted while there is code beside it
    to carry the diff: a new document, or a substantive edit, and not the
    renames and reworded links a code change forces. With no code track there is
    nothing else to read the diff at all, so any documentation change earns it.
    """
    weighed = [file for file in changed if not file.path.endswith(IGNORED_SUFFIX)]
    docs = [file for file in weighed if file.path.endswith(DOC_SUFFIX)]
    code = [file for file in weighed if not file.path.endswith(DOC_SUFFIX)]
    tracks = []
    if code:
        tracks.append(CODE_TRACK)
    if docs and (
        not code
        or any(file.status == ADDED for file in docs)
        or sum(file.additions + file.deletions for file in docs)
        >= SUBSTANTIVE_DOC_LINES
    ):
        tracks.append(DOC_TRACK)
    return tuple(tracks)


@dataclass(frozen=True)
class FixNow:
    """One Suggestion the adjudicator ruled the coming rework lap should carry.

    The thread it names stays open — the next cycle's reviewer is the one who
    verifies and resolves it — so this pair is the whole record of the ruling
    until that reviewer reads the fix. It is why the rework prompt carries the
    `fix` text at all.
    """

    thread: str
    fix: str


def rework_prompt(
    issue: int,
    open_blocking: Iterable[ReviewThread],
    fix_now: Iterable[FixNow] = (),
) -> str:
    """The prompt a rework lap launches the build node under.

    Ids and locations, and not one word of what the findings said. The thread is
    the record, and it moves — a reply lands on it, a later cycle resolves it —
    so a prompt carrying a copy of its text would be handing the builder a
    snapshot of a conversation that has gone on without it. It reads the live
    thread from GitHub instead.

    The fix-now items are the one exception, and they are one because the rule
    above does not reach them: a fix-now ruling was made at this verdict point
    and left on no thread, so there is no live copy to read. Their threads are
    still read live like every other.

    No ordering either. The prompt is a work list, and which finding to take
    first is a judgment about the code, which is the node's.

    A thread with no line left is located by its file alone. A fix that edits
    the anchored line itself flips the thread outdated and takes its live line
    away — which is exactly the thread a rework lap is most likely to be looking
    at — so the path stands rather than the location reading `path:None`.
    """
    listed = []
    for thread in open_blocking:
        where = thread.path if thread.line is None else f"{thread.path}:{thread.line}"
        listed.append(f"- {thread.thread_id} — {where}")
    prompt = REWORK_PROMPT.format(issue=issue, threads="\n".join(listed))
    ruled = [f"- {item.thread} — {item.fix}" for item in fix_now]
    if not ruled:
        return prompt
    return prompt + FIX_NOW_PROMPT.format(items="\n".join(ruled))


def baseline_cycle(starts: Iterable[ledger.LedgerRow]) -> int:
    """The newest cycle a user-ordered lap set the cap's clock back to.

    Zero where no start records one, which is every issue until the merge
    boundary starts writing the key. The highest rather than the last, so the
    clock never resets: a plain `auto` relaunch after a user-ordered lap carries
    no baseline of its own, and reading the newest row alone would put the cap
    back to counting from zero and hand a stuck pull request four more cycles.

    A baseline that is not a whole number stops the traverse rather than being
    coerced or passed over. The cap is the one thing standing between a pull
    request that cannot converge and an unbounded spend, and a clock nobody can
    reason about is worse than no clock at all.
    """
    recorded: list[int] = []
    for row in starts:
        if BASELINE_CYCLE not in row.payload:
            continue
        baseline = row.payload[BASELINE_CYCLE]
        if not isinstance(baseline, int) or isinstance(baseline, bool):
            raise TraverseError(
                f"the {ledger.TRAVERSE_START} row at id {row.id} carries "
                f"{BASELINE_CYCLE} as {baseline!r}, where the review loop's cap "
                f"counts in whole cycles — this store has gone wrong"
            )
        recorded.append(baseline)
    return max(recorded, default=0)


@dataclass(frozen=True)
class ReviewThread:
    """One resolvable finding thread on the pull request.

    Five fields off the GraphQL `reviewThreads` read: what the thread is, where
    it sits, whether anyone has resolved it, and the first comment's text, whose
    first word is the severity the review wrote.
    """

    thread_id: str
    resolved: bool
    path: str
    line: int | None
    body: str


@dataclass(frozen=True)
class CycleVerdict:
    """What one cycle's thread state came to — the whole of the verdict record.

    The tallies and the verdict are the row; `open_blocking` is the same
    computation's other half, and it is what the rework prompt is built from. A
    caller that filtered the threads a second time for the prompt could disagree
    with the row it just wrote about what is still open.
    """

    verdict: str
    blocking_open: int
    blocking_resolved: int
    suggestion_open: int
    suggestion_resolved: int
    open_blocking: tuple[ReviewThread, ...]


def compute_verdict(
    threads: Iterable[ReviewThread], cycle: int, baseline: int
) -> CycleVerdict:
    """The cycle's verdict and its tallies, from thread state and the clock alone.

    Convergence is on Blocking alone, and an open Suggestion never holds it up.
    The tally is taken before the adjudicator runs, so `suggestion_open` counts
    what was open at this moment rather than what survives the verdict point —
    and it is that count the launch rule reads, because a docket of zero is a
    job with nothing in it.

    The cap is counted past the baseline rather than from zero, so a
    user-ordered lap restarts the clock behind it, and it is compared with `>=`
    rather than `==`: a traverse relaunched after a crash burns a cycle number,
    so the count can step over the exact cycle the cap names, and an equality
    would let the loop run past a cap it was meant to stop at.
    """
    graded = [(thread, _severity(thread.body)) for thread in threads]
    open_blocking = tuple(
        thread
        for thread, severity in graded
        if severity == BLOCKING and not thread.resolved
    )
    return CycleVerdict(
        verdict=_verdict(bool(open_blocking), cycle, baseline),
        blocking_open=len(open_blocking),
        blocking_resolved=_tally(graded, BLOCKING, resolved=True),
        suggestion_open=_tally(graded, SUGGESTION, resolved=False),
        suggestion_resolved=_tally(graded, SUGGESTION, resolved=True),
        open_blocking=open_blocking,
    )


def _verdict(blocking_open: bool, cycle: int, baseline: int) -> str:
    """Which of the three ways a cycle ends this one took."""
    if not blocking_open:
        return CONVERGED
    if cycle - baseline >= CYCLE_CAP:
        return CAP_ESCALATED
    return REWORK


def _tally(
    graded: Iterable[tuple[ReviewThread, str]], severity: str, *, resolved: bool
) -> int:
    """How many graded threads of one severity are in one resolution state."""
    return sum(
        1
        for thread, thread_severity in graded
        if thread_severity == severity and thread.resolved == resolved
    )


def _severity(body: str) -> str:
    """The severity a thread's first comment opens on, comparable and bare.

    The first word, as the review contract writes it, with the decoration a
    reviewer may put around it taken off and the case folded. Read strictly, a
    `**Blocking**` would be tallied as neither severity — and a Blocking thread
    that goes uncounted is a convergence declared over a finding nobody
    addressed, which is the one direction this must not be wrong in.
    """
    words = body.split()
    if not words:
        return ""
    return words[0].strip(SEVERITY_DECORATION).casefold()


def next_cycle(headers: Mapping[str, CycleHeader]) -> int:
    """The loop's own cycle number — one past the highest header any track holds.

    Across the tracks, where the sha is per track: the cap counts laps of the
    loop, and a count taken from one track would stand still through every cycle
    that track sat out. A pull request with no header yet is about to run its
    first.
    """
    return max((header.cycle for header in headers.values()), default=0) + 1


def newest_sha(headers: Mapping[str, CycleHeader]) -> str | None:
    """The sha of the newest header on the pull request, across every track.

    This is the cycle's own sha on the verdict record — what the cycle that just
    ran actually read. The tracks of one cycle all review the same branch tip,
    so which of them the newest header belongs to does not change the answer.
    """
    newest = max(headers.values(), key=lambda header: header.cycle, default=None)
    return None if newest is None else newest.sha


def _header(line: str) -> CycleHeader | None:
    """One line as a cycle header, or None where it is not one.

    The shape is fixed by the review contract — four ` · `-separated fields, the
    third of them `cycle <n>` — and every field is judged before any of them is
    used. A line matched loosely would hand the loop a cycle number lifted out
    of ordinary prose, and the cap counts what it is given.
    """
    fields = [field.strip() for field in line.strip().split(HEADER_SEPARATOR)]
    if len(fields) != HEADER_FIELDS:
        return None
    review, sha, counted, session_id = fields
    if not counted.startswith(CYCLE_WORD):
        return None
    count = counted.removeprefix(CYCLE_WORD).strip()
    if not count.isdecimal():
        return None
    return CycleHeader(review=review, sha=sha, cycle=int(count), session_id=session_id)


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
        """The nodes themselves, in the order this issue's phase calls for.

        The tuple in `GRAPH` is walked rather than read for one name and then
        second-guessed. Testing for one node and running the rest anyway would
        make the other names in those tuples decorative, and the next phase
        added to the graph would run nodes its own entry never declared.
        """
        nodes = self._nodes()
        worktree = self._worktree()
        self._preflight(worktree)
        steps = {BUILD: self._build, OPEN_PR: self._open_pr}
        for node in nodes:
            steps[node](worktree)
        return self._review_loop(worktree)

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
        """Run the build node, verify what it left behind, and move the label.

        The label move belongs to the graph's own build, not to the loop's. A
        rework lap runs the same node over the same worktree with the board
        already at `pr-review`, and moving a label there would be moving it to
        where it already is.
        """
        self._run_build(worktree, str(self.issue))
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

    def _run_build(self, worktree: Path, prompt: str) -> None:
        """Launch the build node under one prompt and verify what it left behind.

        The whole of what the graph's build and a rework lap have in common. The
        prompt is the only difference between them, and the verification is not
        optional on either: a rework lap that edits and never pushes leaves the
        next cycle reviewing the lap before it and reporting the same findings
        against work that has already moved.
        """
        self._launch(BUILD, worktree, BUILD_SCHEMA, prompt)
        self._verify_build(worktree)

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

    def _open_pr(self, worktree: Path) -> None:
        """Run the open-pr node. What it left behind is read by the loop below."""
        self._launch(OPEN_PR, worktree, OPEN_PR_SCHEMA, str(self.issue))

    # --- the review loop ---

    def _review_loop(self, worktree: Path) -> TraverseOutcome:
        """Review, judge, rework, and go round again until the loop leaves.

        One uniform body, entered the same way every time. A traverse arriving
        here for the first time and one relaunched after a crash run this
        identical code: there is no resume branch, no state carried in the
        process, and no label moved inside the loop. Everything the loop needs is
        read from the pull request each lap, which is what lets a relaunch pick
        up wherever the last one stopped. It costs a burned cycle number when a
        traverse dies after its reviews posted, and that is accepted — the clock
        the cap counts on is never turned back.

        The headers are read twice a lap, and they are two different reads. The
        one at the top says which cycle is about to run and what sha each track
        last saw; the one after the fan-out is this cycle's own, and its sha is
        what the verdict record names. The second is the next lap's first, so a
        lap makes one read of its own.
        """
        pull = self._pull_request()
        baseline = baseline_cycle(
            ledger.traverse_starts(
                repo=self.repo, issue=self.issue, db_path=self.db_path
            )
        )
        headers = self._cycle_headers(pull)
        while True:
            cycle = next_cycle(headers)
            self._fan_out(self._elected(pull, cycle), headers, worktree)
            headers, threads = self._headers_and_threads(pull)
            verdict = compute_verdict(threads, cycle, baseline)
            self._record_verdict(pull, cycle, newest_sha(headers), verdict)
            if verdict.verdict == CONVERGED:
                self._adjudicate(worktree, CONVERGED)
                return self._pr_ready(pull)
            if verdict.verdict == CAP_ESCALATED:
                raise _Escalated(
                    f"{verdict.blocking_open} Blocking threads on {pull.url} are "
                    f"still open at cycle {cycle}, {CYCLE_CAP} autonomous cycles "
                    f"past baseline {baseline}, so this pull request is not "
                    f"converging on its own",
                    payload={CYCLE: cycle, BASELINE: baseline},
                )
            ruled = (
                self._adjudicate(worktree, REWORK) if verdict.suggestion_open else ()
            )
            self._run_build(
                worktree, rework_prompt(self.issue, verdict.open_blocking, ruled)
            )

    def _elected(self, pull: _PullRequest, cycle: int) -> tuple[str, ...]:
        """The reviews this cycle runs, from the pull request's changed files.

        Recomputed every cycle rather than fixed at the first, because the diff
        moves under it: a rework lap that adds a document earns the doc track it
        did not earn before.

        A diff that elects nothing stops the traverse. Every other verdict rests
        on threads some review posted, so a cycle with no review at all would
        find no Blocking thread, converge, and hand back a pull request nobody
        read as though it had passed.
        """
        tracks = elect_tracks(self._changed_files(pull))
        if not tracks:
            raise _Escalated(
                f"cycle {cycle} of {pull.url} elects no review track — every file "
                f"it changes is one no review reads, so nothing would judge it"
            )
        elected = tuple(node for track in tracks for node in REVIEWS[track])
        _say(f"{self.repo}#{self.issue}: cycle {cycle} runs {', '.join(elected)}")
        return elected

    def _fan_out(
        self, nodes: Sequence[str], headers: Mapping[str, CycleHeader], worktree: Path
    ) -> None:
        """Run the cycle's reviews at once, and relay every one that did not land.

        The books come first and the escalation second. The `with` block joins
        every worker before a single result is read, so whatever any one of them
        did, the siblings run to the end and their `job-report` rows land — and
        only then is a failure relayed. Nothing is retried and nothing is
        absorbed: a review that did not come back clean and reporting done ends
        the traverse.

        Failures come back as values rather than exceptions so that all of them
        are relayed. Raising would surface whichever job the results were read
        from first and lose what the others said, and what a node reported about
        why it stopped is the whole of what reaches the operator.

        One thing is different here from the sequential path. A traverse killed
        mid-fan-out files these jobs from its trap, and each worker's own
        `launch_job` still returns and files a second report for the same
        session: the `SystemExit` the trap raises reaches the main thread alone.
        Both rows are true and neither hides the other — a launch with two
        reports still reads as finished — so the duplicate is left rather than
        papered over.
        """
        with _pool(len(nodes)) as pool:
            running = [
                pool.submit(self._review, node, headers, worktree) for node in nodes
            ]
        failures = [failure for job in running if (failure := job.result()) is not None]
        if failures:
            raise _relay(failures)

    def _review(
        self, node: str, headers: Mapping[str, CycleHeader], worktree: Path
    ) -> _Failure | None:
        """Launch one review, and hand back how it failed rather than raising.

        The prompt carries the sha from this review's own newest header, and
        never a sibling's. Election is recomputed every cycle, so a track really
        can sit out one and come back — handed the newest sha on the pull
        request it would start its delta at a commit it never read, and skip
        every change between in silence. A review with no header yet is on its
        first cycle and reads the whole diff, so it is given the issue number
        alone.

        `LaunchAborted` is the one exception caught, exactly as the sequential
        path catches it and for the same reason: nothing spawned and nothing was
        spent. Anything else is the harness breaking a promise mid-flight, and a
        reviewer answers for that the way a builder does — it leaves as itself,
        rises through the traverse, and ends the run red rather than being folded
        into an ordinary escalation nobody would look at twice.
        """
        header = headers.get(REVIEW_NAMES[node])
        prompt = str(self.issue) if header is None else f"{self.issue} {header.sha}"
        _say(f"{self.repo}#{self.issue}: launching {node}")
        try:
            outcome = self._launch_job(node, worktree, REVIEW_SCHEMA, prompt)
        except launcher.LaunchAborted as aborted:
            return _Failure(_abort_reason(node, aborted), node)
        return _judge(node, outcome)

    def _adjudicate(self, worktree: Path, verdict: str) -> tuple[FixNow, ...]:
        """Settle the open Suggestion threads at one verdict point.

        The launch rule is the verdict word and nothing else, which is what
        makes it deterministic: a convergence always runs it, because that run
        is what leaves the pull request's two disposition sections complete for
        the merge read; a rework runs it only with Suggestion threads open,
        because an empty docket is a job with nothing to do; and a cap
        escalation never reaches here at all.

        The prompt is the issue number and that word. Everything else the node
        acts on — which threads are open, what each says, what the pull request
        already records — it reads from GitHub itself, so two runs finding the
        same pull request are given the same input.
        """
        outcome = self._launch(
            ADJUDICATOR, worktree, ADJUDICATOR_SCHEMA, f"{self.issue} {verdict}"
        )
        return _fix_now(outcome.structured_output, verdict)

    def _pull_request(self) -> _PullRequest:
        """The open pull request on this issue's branch, refused when there is none.

        Read off GitHub rather than lifted from what a node said. A node that
        believes it opened a pull request and did not would otherwise send the
        loop reviewing a number that stands for nothing.
        """
        listed = self._gh_or_absent(
            "pr",
            "list",
            "--repo",
            self.repo,
            "--head",
            self._branch(),
            "--json",
            "number,url",
            "--jq",
            r'.[] | "\(.number) \(.url)"',
        )
        if listed is None:
            raise _Escalated(
                f"{OPEN_PR} reported {DONE} but no pull request is open on "
                f"{self._branch()}",
                node=OPEN_PR,
            )
        number, url = listed.splitlines()[0].split(" ", 1)
        return _PullRequest(number=int(number), url=url)

    def _headers_and_threads(
        self, pull: _PullRequest
    ) -> tuple[dict[str, CycleHeader], list[ReviewThread]]:
        """The two reads a verdict rests on, run at once.

        They are independent — different endpoints, and neither answer shapes
        the other's request — so run one after the other a cycle would pay both
        round trips end to end, every cycle, up to `CYCLE_CAP` of them a
        traverse.
        """
        with _pool(2) as pool:
            posted = pool.submit(self._cycle_headers, pull)
            threads = pool.submit(self._threads, pull)
        return posted.result(), threads.result()

    def _cycle_headers(self, pull: _PullRequest) -> dict[str, CycleHeader]:
        """Every review's newest cycle header, read off the pull request itself.

        `--paginate` is not optional. The endpoint returns 30 reviews a page,
        oldest first, so an unpaginated read drops the newest headers — exactly
        the ones the cycle count and the shas depend on. A traverse busy enough
        to approach the cap is the one whose count would silently reset.
        """
        return parse_cycle_headers(
            self._gh(
                "api",
                "--paginate",
                f"repos/{self.repo}/pulls/{pull.number}/reviews",
                "--jq",
                r'.[].body | split("\n")[0]',
            ).splitlines()
        )

    def _changed_files(self, pull: _PullRequest) -> list[ChangedFile]:
        """What the pull request changes, in the four fields the election weighs.

        One line per file, and every line is parsed strictly. A line this cannot
        read is a filter that has stopped returning what it used to, and a file
        dropped from the answer is a track that quietly stops being elected.
        """
        changed = []
        for line in self._gh(
            "api",
            "--paginate",
            f"repos/{self.repo}/pulls/{pull.number}/files",
            "--jq",
            r".[] | [.filename, .status, (.additions|tostring), "
            r"(.deletions|tostring)] | @tsv",
        ).splitlines():
            changed.append(self._changed_file(line, pull))
        return changed

    def _changed_file(self, line: str, pull: _PullRequest) -> ChangedFile:
        """One tab-separated file line, refused rather than guessed at."""
        fields = line.split("\t")
        if len(fields) != CHANGED_FILE_FIELDS or not all(
            count.isdecimal() for count in fields[2:]
        ):
            raise _Escalated(
                f"the file list of {pull.url} carries a line this cannot read as "
                f"a path, a status and two line counts: {line!r}"
            )
        path, status, additions, deletions = fields
        return ChangedFile(
            path=path,
            status=status,
            additions=int(additions),
            deletions=int(deletions),
        )

    def _threads(self, pull: _PullRequest) -> list[ReviewThread]:
        """Every review thread on the pull request, with its resolution state.

        Paged to the end. `reviewThreads` caps at 100 and returns them oldest
        first, so the threads a long-running pull request would drop are its
        newest — and a verdict that never sees an open Blocking thread is a
        convergence declared falsely.
        """
        owner, name = self.repo.split("/")
        threads: list[ReviewThread] = []
        after = "null"
        while True:
            page = self._threads_page(owner, name, pull.number, after)
            threads.extend(_thread(node) for node in page["nodes"])
            if not page["pageInfo"]["hasNextPage"]:
                return threads
            after = json.dumps(page["pageInfo"]["endCursor"])

    def _threads_page(
        self, owner: str, name: str, number: int, after: str
    ) -> dict[str, Any]:
        """One GraphQL page of review threads, decoded.

        `gh api graphql` has no `-R` flag: the owner and the repository are
        spelled into the query's own arguments, which is why they are formatted
        in rather than passed as a repository option.
        """
        query = THREADS_QUERY.format(owner=owner, name=name, number=number, after=after)
        answered = json.loads(self._gh("api", "graphql", "-f", f"query={query}"))
        return answered["data"]["repository"]["pullRequest"]["reviewThreads"]  # type: ignore[no-any-return]

    def _record_verdict(
        self, pull: _PullRequest, cycle: int, sha: str | None, verdict: CycleVerdict
    ) -> None:
        """Write the cycle's verdict row — the one record of what a cycle decided."""
        ledger.verdict(
            self.repo,
            self.issue,
            {
                PR: pull.url,
                CYCLE: cycle,
                SHA: sha,
                BLOCKING_OPEN: verdict.blocking_open,
                BLOCKING_RESOLVED: verdict.blocking_resolved,
                SUGGESTION_OPEN: verdict.suggestion_open,
                SUGGESTION_RESOLVED: verdict.suggestion_resolved,
                VERDICT: verdict.verdict,
            },
            db_path=self.db_path,
        )
        _say(f"{self.repo}#{self.issue}: cycle {cycle} — {verdict.verdict}")

    def _pr_ready(self, pull: _PullRequest) -> TraverseOutcome:
        """Close the window over a pull request that has converged on Blocking."""
        ledger.traverse_end(
            self.repo,
            self.issue,
            {ledger.STATUS: ledger.PR_READY, PR_URL: pull.url},
            db_path=self.db_path,
        )
        _say(f"{self.repo}#{self.issue}: pr-ready at {pull.url}")
        return TraverseOutcome(ledger.PR_READY, pr_url=pull.url)

    # --- launching a node ---

    def _launch(
        self, node: str, worktree: Path, schema: Mapping[str, object], prompt: str
    ) -> launcher.JobOutcome:
        """Launch one node and refuse anything but a clean process reporting done.

        The outcome is handed back for the one caller that needs the report on
        it. Most ignore it, because what the graph does next is read from git
        and GitHub rather than from what a node said.

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
            outcome = self._launch_job(node, worktree, schema, prompt)
        except launcher.LaunchAborted as aborted:
            raise _Escalated(_abort_reason(node, aborted), node=node) from aborted
        failure = _judge(node, outcome)
        if failure is not None:
            raise _Escalated(
                failure.reason, node=failure.node, session_id=failure.session_id
            )
        return outcome

    def _launch_job(
        self, node: str, worktree: Path, schema: Mapping[str, object], prompt: str
    ) -> launcher.JobOutcome:
        """One `launch_job` call with this traverse's seams filled in."""
        return launcher.launch_job(
            self.repo,
            self.issue,
            node,
            worktree,
            prompt,
            schema,
            {MODE: self.mode, NODE: node},
            db_path=self.db_path,
            agents_dir=self.agents_dir,
            claude_cmd=self.claude_cmd,
            timeout_s=self.timeout_s,
            grace_s=self.grace_s,
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

        With no worktree there, origin is asked about the issue's own branch
        before anything is cut. A branch on origin with no tree here means the
        work is on GitHub and only the local side is gone — a re-cloned
        checkout, or a `git branch -D` run before the merge landed — and
        `git worktree add -b` would answer that by resetting the branch to
        `main`, silently, because it refuses only a local branch that exists.
        Every commit the last lap pushed would be off the branch with no node
        running to put it back, and a `pr-review` entry skips the build and the
        verification with it, so nothing downstream would notice either.
        """
        worktree = self.checkout / WORKTREES / self._branch()
        if worktree.exists():
            self._gate_reuse(worktree)
            _say(f"{self.repo}#{self.issue}: reusing {worktree}")
            return worktree
        stranded = self._origin_sha(self._branch())
        if stranded is not None:
            raise _Escalated(
                f"{self._branch()} is on origin at {stranded} with no worktree at "
                f"{worktree}, so the issue's work is stranded — cutting the branch "
                f"again here would reset it to main"
            )
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
        it reads what is still standing, closes the window with a `killed` end,
        then kills each child and files its terminal row. Then it raises
        `SystemExit`, which is what stops `launch_job` writing a second report for
        the job just filed — the exception leaves through the supervision instead
        of returning into it.

        Both signals are put back to the default first, so a second one while
        this is running kills outright rather than re-entering a handler already
        part-way through the books. They are put back by walking `TRAPPED`, so a
        signal added to the pair cannot be left trapped with no way out.

        The three steps run in that order for a reason. Filing has ways to fail
        that nothing here can rule out — a session id the probe will not compile,
        a store that refuses the write — and a handler that filed first would
        lose the `killed` end to any of them, with both signals already back at
        the default and no second chance at the books. So the end goes ahead of
        the filing. It cannot go ahead of the *read*, though: `traverse-end` is
        what closes the window, and `live_jobs` only answers while the window is
        open, so an end written before the read would empty the cascade of
        everything it exists to file. Read, close, then file.

        A filing that fails after the end is chained onto the exit rather than
        raised on its own, so the operator sees it and the supervision above
        never gets the chance to write a second, contradicting end.

        `PR_SET_PDEATHSIG` on the children covers what no trap can: a launcher
        SIGKILLed or OOM-killed runs none of this, the children still die, and the
        next invocation's sweep files their rows.
        """

        def die(number: int, frame: FrameType | None) -> None:
            for trapped in TRAPPED:
                signal.signal(trapped, signal.SIG_DFL)
            _say(f"{self.repo}#{self.issue}: signal {number}, taking children down")
            standing = self._standing()
            ledger.traverse_end(
                self.repo,
                self.issue,
                {ledger.STATUS: ledger.KILLED},
                db_path=self.db_path,
            )
            try:
                self._file(standing, KILL_CASCADE)
            except TraverseError as unfinished:
                raise SystemExit(EXIT_KILLED) from unfinished
            raise SystemExit(EXIT_KILLED)

        restore = [(number, signal.signal(number, die)) for number in TRAPPED]
        try:
            yield
        finally:
            for number, handler in restore:
                signal.signal(number, handler)

    def _sweep(self, why: str) -> None:
        """Read this issue's unfinished jobs and finish their books.

        The two halves are named apart because the kill cascade needs them apart:
        it has to read before it closes its own window and file after. Nothing
        else does, so every other caller takes them together here.
        """
        self._file(self._standing(), why)

    def _standing(self) -> list[ledger.LedgerRow]:
        """Every job of this issue whose launch has no terminal row yet.

        Scoped to this `(repo, issue)` and nothing wider. Other pairs' jobs belong
        to other traverses, which are running right now under their own locks, and
        a sweep that reached them would kill live work and file it as dead.

        The rows are read into a list rather than left as a cursor, because the
        one caller that separates the read from the filing writes the window's
        terminal row between the two — and `live_jobs` answers only while the
        window is open.
        """
        return list(
            ledger.live_jobs(repo=self.repo, issue=self.issue, db_path=self.db_path)
        )

    def _file(self, standing: Iterable[ledger.LedgerRow], why: str) -> None:
        """Take each standing job down and write it the terminal row it never got.

        A job is found in the process table by its session id, which rides the
        child's command line as `--session-id`, so the match is exact rather than
        a guess at what a claude process looks like. One that is still running is
        SIGTERMed; one that is already gone needs no signal. Either way its row is
        written, because completing the books is the whole duty here — a launch
        with no report reads as live for good.

        The row it writes is shaped the way `launcher._payload` shapes one, down
        to leaving `kill` out when nothing was signalled. `factory-status` reads
        both writers, and a key one of them always writes and the other writes
        only sometimes is a query that answers `"kill" in payload` with kills
        that never happened.
        """
        for row in standing:
            session_id = _column(row, "session_id")
            node = _column(row, "node")
            killed = _terminate(session_id)
            _say(f"{self.repo}#{self.issue}: sweeping {node} {session_id} ({why})")
            ledger.job_report(
                self.repo,
                self.issue,
                node,
                session_id,
                {
                    launcher.PROCESS_OUTCOME: launcher.DIED,
                    launcher.TASK_OUTCOME: None,
                    launcher.STRUCTURED_OUTPUT: None,
                    launcher.EXIT_CODE: None,
                    **({launcher.KILL: launcher.SIGTERM} if killed else {}),
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

        The escalation's own keys are merged last, so a payload that named one of
        the three above would be the one written — a merge that dropped them
        silently would leave a row whose extra keys are a lie about which
        escalation it is.
        """
        _say(f"{self.repo}#{self.issue}: escalated — {escalated.reason}")
        ledger.traverse_escalation(
            self.repo,
            self.issue,
            {
                REASON: escalated.reason,
                NODE: escalated.node,
                SESSION_ID: escalated.session_id,
                **escalated.payload,
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
        are not told apart, and deliberately so — both end the traverse
        escalated, which is the safe direction to be wrong in. Neither read moves
        a label itself, but the pull request read runs after `_build` has already
        moved one, so an escalation here does not leave the board where the
        traverse found it.
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


def _column(row: ledger.LedgerRow, name: str) -> str:
    """One grain column of a launch row the sweep cannot do without.

    `LedgerRow` types both of them `str | None`, and coercing a missing one
    with `str()` would hand `_terminate` the literal `"None"` to hunt the
    process table for — a probe that looked for the wrong thing and then filed
    a live job as dead, which is the outcome `_terminate` refuses to reach by
    every other route. No writer in `ledger` produces such a row, so meeting
    one means the store has gone wrong, and that is said rather than papered
    over.
    """
    value = getattr(row, name)
    if value is None:
        raise TraverseError(
            f"the {row.kind} row at id {row.id} has no {name}, so the job it "
            f"records cannot be found in the process table or filed against a "
            f"node — this store has gone wrong"
        )
    return str(value)


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
