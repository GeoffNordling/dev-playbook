"""The job launcher — one factory node launch, preflight through spawn to a ledgered job."""

import json
import os
import queue
import shutil
import subprocess
import threading
import time
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import IO

import yaml

from dev_playbook import gitrepo
from dev_playbook.factory import ledger

# Environment variables that route inference somewhere other than subscription
# OAuth. Every one outranks the `/login` credential in Anthropic's documented
# precedence, and `-p` uses a configured key whenever one is present, so any of
# them reaching the child moves the run to per-token billing with no warning.
BILLING_ENV_VARS = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "ANTHROPIC_BASE_URL",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
    "CLAUDE_CODE_USE_FOUNDRY",
    "ANTHROPIC_PROFILE",
    "ANTHROPIC_FEDERATION_RULE_ID",
    "ANTHROPIC_ORGANIZATION_ID",
)

# Settings keys that mint or redirect credentials.
BILLING_SETTINGS_KEYS = ("apiKeyHelper", "awsAuthRefresh", "awsCredentialExport")

# Managed settings, which no environment variable can redirect: tests point
# these two names elsewhere, which is why they are module constants.
MANAGED_SETTINGS = Path("/etc/claude-code/managed-settings.json")
MANAGED_SETTINGS_DIR = Path("/etc/claude-code/managed-settings.d")

# The per-scope directory every settings file and agent definition sits under.
CLAUDE_DIR = ".claude"

# Where the factory's own definitions are stowed, and the fence line that opens
# and closes the YAML frontmatter in one.
AGENTS_DIR = Path("~/.claude/agents").expanduser()
FRONTMATTER_FENCE = "---"

# The six factory node names. The shadow check reads the whole roster whatever
# node is being launched, because a repo-local copy of any of them silently
# beats the user-scope definition the next launch expects.
NODES = (
    "build",
    "open-pr",
    "bug-pr-review",
    "code-pr-review",
    "doc-pr-review",
    "adjudicator",
)

# The effort vocabulary a definition may pin, and the one environment variable
# that outranks a definition's pin. An effort outside the vocabulary is
# swallowed silently, so an unrecognised one is refused rather than passed on.
EFFORT_LEVELS = ("low", "medium", "high", "xhigh", "max")
EFFORT_LEVEL_VAR = "CLAUDE_CODE_EFFORT_LEVEL"

# The wall clock every job runs under, and how long a child gets to honor
# SIGTERM before SIGKILL. One hard rule, every node.
DEADLINE_SECONDS = 3600.0
GRACE_SECONDS = 30.0
MILLISECONDS = 1000.0

# The five process outcomes, named once. Every one is the launcher's own word
# for how the process ended, and the graph branches on nothing else.
CLEAN = "clean"
SCHEMA_REFUSED = "schema-refused"
DIED = "died"
TIMED_OUT = "timed-out"
MISCONFIGURED = "misconfigured"

# How far the launcher had to go to stop a child, recorded on the row.
SIGTERM = "sigterm"
SIGKILL = "sigkill"

# The two `init` fields that genuinely vary per run, and the value that means
# the run is on subscription rather than metered. Every other field the harness
# declares is recorded and never re-asserted.
INIT_CWD = "cwd"
INIT_API_KEY_SOURCE = "apiKeySource"
SUBSCRIPTION = "none"

# The report the harness validated, and the one key inside it the task layer
# reads. Every node schema carries a required top-level `outcome`, so this one
# key answers for node shapes no query has to know about.
STRUCTURED_OUTPUT = "structured_output"
OUTCOME = "outcome"

# Accounting lifted off the result envelope onto the `job-report` row, plus the
# duration field the row records in seconds.
RESULT_EXTRACTS = ("subtype", "is_error", "num_turns", "usage", "permission_denials")
DURATION_MS = "duration_ms"


class LauncherError(Exception):
    """The base every failure this module raises derives from."""


class LaunchAborted(LauncherError):
    """Nothing spawned and nothing spent, carrying every finding that stopped it."""

    def __init__(self, findings: list[str]) -> None:
        """Hold the findings whole, and say all of them in the message."""
        self.findings = tuple(findings)
        super().__init__(f"launch aborted: {'; '.join(self.findings)}")


class HarnessContractViolation(LauncherError):
    """The harness broke a measured promise mid-flight, so no outcome can be read."""


@dataclass(frozen=True)
class JobOutcome:
    """What a finished job was, in the two layers the factory reasons in.

    `process_outcome` is the launcher's own classification and is always
    present; `task_outcome` is the node's own word for how the work went, read
    from the report's top-level `outcome` and null whenever no report exists.
    Accounting — duration, usage, turns, exit code — is on the ledger row
    alone, because nothing in the graph branches on it.
    """

    process_outcome: str
    task_outcome: str | None
    structured_output: dict[str, object] | None
    session_id: str


def _main_checkout(worktree: Path) -> Path:
    """The main checkout a worktree is linked to, derived from the worktree alone.

    `git rev-parse --git-common-dir` names the main checkout's `.git`, whose
    parent is the checkout. Asking git is what lets a caller hand over a
    worktree and nothing else: the sweep needs the main checkout's
    `settings.local.json`, which fires into a worktree-cwd'd child, and the
    shadow check needs both trees.

    Resolved once per public entry point and passed down from there. Two calls
    within one launch can disagree if the worktree is repointed between them,
    and the sweep would then read one checkout's `settings.local.json` while
    the shadow check scans another's.

    The answer comes back absolute from a linked worktree and relative from a
    main checkout, so it is joined onto the worktree either way — joining an
    absolute path discards the left side, which is exactly right here.

    A path that is no git checkout at all leaves as git's own
    `CalledProcessError` rather than as a `LauncherError`: the worktree is the
    caller's to create and hand over, so a missing one is that caller's bug,
    and dressing it as a launch failure would send an operator to check a
    launch that was never the problem.
    """
    common = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
        env=gitrepo.no_git_env(),
    ).stdout.strip()
    return (worktree / common).resolve().parent


def _settings_roster(
    worktree: Path, env: Mapping[str, str], checkout: Path
) -> list[Path]:
    """Every settings file a launch from `worktree` under `env` would merge.

    The user scope resolves from the swept environment's own `HOME` rather than
    the launcher's, because what is under inspection is the environment the
    child will receive — a child pointed at another home reads that home's
    settings.

    Managed settings are listed in both forms. Whether `-p` honors the drop-in
    directory is unverified, and sweeping a file that never fires is harmless
    where missing one that does is the exact hole the sweep exists for.
    """
    return [
        worktree / CLAUDE_DIR / "settings.json",
        worktree / CLAUDE_DIR / "settings.local.json",
        checkout / CLAUDE_DIR / "settings.local.json",
        Path(env["HOME"]) / CLAUDE_DIR / "settings.json",
        MANAGED_SETTINGS,
        *sorted(MANAGED_SETTINGS_DIR.glob("*.json")),
    ]


def preflight(worktree: Path, env: Mapping[str, str]) -> None:
    """Refuse a launch whose environment or settings would meter it.

    Raises `LaunchAborted` carrying every finding at once, so an operator fixes
    the whole configuration in one pass rather than one finding per run.

    Presence is what condemns a billing name, here and in `_swept`, never
    truthiness: `ANTHROPIC_API_KEY=""` is set, and a check guarding money must
    not be the laxer of the two next to `CLAUDE_CODE_EFFORT_LEVEL`. An empty
    value that routes no billing is refused with the rest — a name nobody meant
    to export is a configuration an operator should see either way.
    """
    findings = _sweep_findings(worktree, env, _main_checkout(worktree))
    if findings:
        raise LaunchAborted(findings)


def _sweep_findings(
    worktree: Path, env: Mapping[str, str], checkout: Path
) -> list[str]:
    """The sweep itself, given a checkout its caller has already resolved.

    `preflight` and `launch_job` both run this and nothing else, so the launch
    is swept by the very code the traverse calls standalone — the two can never
    drift into disagreeing about what meters a run.
    """
    findings = [f"environment: {var} is set" for var in BILLING_ENV_VARS if var in env]
    for path in _settings_roster(worktree, env, checkout):
        if path.exists():
            findings += _swept(path)
    return findings


def _swept(path: Path) -> list[str]:
    """Findings from one settings file that is there.

    Two duties in one pass, because both need the file read. It must parse:
    `-p` silently ignores a settings file it cannot read, so a launch under one
    runs with settings nobody has seen, and this is the only place that
    surfaces. And it must carry no billing key, at the top level or in the
    `env` block it exports into the child.

    A file that parses into something other than an object — a list, a bare
    number — fails the parse duty rather than the sweep: there is no place in
    it for the keys to be, so it cannot be reported clean.

    The read is unconditional, and a file that is there but will not open is a
    finding of its own rather than a skip. Absent and unreadable are two
    different things, and the one check standing between the factory and
    metered billing must not report them the same way. This is what surfaces a
    roster file masked to `/dev/null` by a sandbox: `/dev/null` opens and reads
    as empty, empty is not valid JSON, and the mask lands as a parse finding.
    """
    try:
        settings = json.loads(path.read_text())
    except OSError as error:
        return [f"{path}: is there but will not open ({error})"]
    except ValueError as error:
        return [f"{path}: will not parse as JSON ({error})"]
    if not isinstance(settings, dict):
        return [f"{path}: parses as {type(settings).__name__}, not a settings object"]
    exported = settings.get("env", {})
    if not isinstance(exported, dict):
        return [f"{path}: env is a {type(exported).__name__}, not a block of variables"]
    return [
        *(
            f"{path}: {key} is configured"
            for key in BILLING_SETTINGS_KEYS
            if key in settings
        ),
        *(f"{path}: env.{var} is set" for var in BILLING_ENV_VARS if var in exported),
    ]


# --- pre-spawn validation ---


def _prespawn_findings(
    node: str,
    worktree: Path,
    env: Mapping[str, str],
    agents_dir: Path,
    claude_cmd: Sequence[str],
    checkout: Path,
) -> list[str]:
    """Everything about this launch that would make it spend money for nothing.

    Gathered rather than raised one at a time, for the same reason the sweep
    gathers: an operator with a stale worktree fixes the whole of it in one
    pass. Every one of these is checked before the session id is minted, so a
    launch that fails here leaves no `job-launch` row behind.

    Presence, not truthiness, is what condemns `CLAUDE_CODE_EFFORT_LEVEL`: the
    brief's rule is that it be absent, and it is never stripped — a launch
    under one is refused so the effort a definition pins is the effort that
    runs.
    """
    findings = []
    if shutil.which(claude_cmd[0]) is None:
        findings.append(f"{claude_cmd[0]} does not resolve on PATH")
    if EFFORT_LEVEL_VAR in env:
        findings.append(
            f"environment: {EFFORT_LEVEL_VAR} is set to {env[EFFORT_LEVEL_VAR]!r} and "
            f"outranks the effort the definition pins"
        )
    return [
        *findings,
        *_definition_findings(node, agents_dir),
        *_shadow_findings(worktree, checkout),
    ]


def _definition_findings(node: str, agents_dir: Path) -> list[str]:
    """Findings against the definition of the node this launch spawns.

    Scoped to the launched node alone. The six land incrementally across the
    epic, so a launch must not fail on a definition no job needs yet; checking
    the whole roster exists is the traverse's business, at traverse start.

    Both field checks guard a silent failure rather than a loud one. A
    definition whose `name` is not its filename stem drops out of the roster
    with no error, and an `effort` outside the vocabulary is swallowed — so a
    launch under either runs as something other than what was asked for, and
    nothing downstream would say so.
    """
    path = agents_dir / f"{node}.md"
    if not path.is_file():
        return [f"{path}: the launched node has no definition"]
    try:
        frontmatter = _frontmatter(path)
    except (ValueError, yaml.YAMLError) as error:
        return [f"{path}: frontmatter will not parse ({error})"]
    findings = []
    if frontmatter.get("name") != node:
        findings.append(
            f"{path}: name is {frontmatter.get('name')!r}, not {node!r}, so the "
            f"definition drops out of the roster silently"
        )
    effort = frontmatter.get("effort")
    if effort not in EFFORT_LEVELS:
        findings.append(
            f"{path}: effort is {effort!r}, not one of {EFFORT_LEVELS}, and an "
            f"unrecognised effort is swallowed silently"
        )
    return findings


def _frontmatter(path: Path) -> dict[str, object]:
    """One agent definition's YAML frontmatter, as a mapping.

    Raises `ValueError` for a file that carries no fenced block at all or whose
    block is not a mapping, alongside the `yaml.YAMLError` malformed YAML
    raises. The one caller reports all three the same way.
    """
    opening = f"{FRONTMATTER_FENCE}\n"
    text = path.read_text()
    if not text.startswith(opening):
        raise ValueError("the file opens with no frontmatter fence")
    _, _, rest = text.partition(opening)
    block, fence, _ = rest.partition(f"\n{FRONTMATTER_FENCE}")
    if not fence:
        raise ValueError("the frontmatter fence is never closed")
    frontmatter = yaml.safe_load(block)
    if not isinstance(frontmatter, dict):
        raise ValueError(
            f"the frontmatter is a {type(frontmatter).__name__}, not a mapping"
        )
    return frontmatter


def _shadow_findings(worktree: Path, checkout: Path) -> list[str]:
    """Findings for any repo-local copy of a factory node's definition.

    The whole six-name roster, in both trees, whatever node is being launched:
    a project-scope `.claude/agents/<name>.md` silently beats the user-scope
    definition, so a stray copy left in a checkout quietly replaces a factory
    node with whatever that file says.

    Anything at the path condemns it, not a regular file at the path. What is
    being asked is whether something sits where the child will look, and a
    check that answers "no" for a path it merely cannot read as a regular file
    hides the very copy it exists to find — a `.claude/agents` masked by a
    sandbox, most of all.
    """
    findings = []
    for tree in (worktree, checkout):
        for node in NODES:
            path = tree / CLAUDE_DIR / "agents" / f"{node}.md"
            if path.exists():
                findings.append(
                    f"{path}: a repo-local definition of {node!r} silently beats the "
                    f"user-scope one"
                )
    return findings


# --- the launch ---


def launch_job(
    repo: str,
    issue: int,
    node: str,
    worktree: Path,
    prompt: str,
    schema: Mapping[str, object],
    launch_payload: Mapping[str, object],
    *,
    db_path: Path = ledger.DB_PATH,
    agents_dir: Path = AGENTS_DIR,
    claude_cmd: Sequence[str] = ("claude",),
    timeout_s: float = DEADLINE_SECONDS,
    grace_s: float = GRACE_SECONDS,
) -> JobOutcome:
    """Carry one factory node launch from preflight to a classified, ledgered job.

    In order: sweep, validate, mint a session id, write the `job-launch` row,
    spawn, supervise the stream live, classify, write the `job-report` row.
    Every abort precedes the mint, so no `job-launch` row ever stands for a job
    that never spawned.

    `launch_payload` is written to the `job-launch` row uninterpreted — what a
    caller records about why it launched is its own business. The keyword
    parameters are the test seam; production callers pass none of them.

    Job-grain rows only: a `LaunchAborted` is the caller's to record at traverse
    grain, and this never writes `traverse-escalation`.
    """
    env = dict(os.environ)
    # One checkout for the whole launch. The sweep reads its
    # `settings.local.json` and the shadow check scans its `.claude/agents`, and
    # resolving it twice lets those two read different trees if the worktree is
    # repointed in between.
    checkout = _main_checkout(worktree)
    findings = _sweep_findings(worktree, env, checkout)
    if findings:
        raise LaunchAborted(findings)
    findings = _prespawn_findings(node, worktree, env, agents_dir, claude_cmd, checkout)
    if findings:
        raise LaunchAborted(findings)
    session_id = str(uuid.uuid4())
    ledger.job_launch(repo, issue, node, session_id, launch_payload, db_path=db_path)
    run = _supervise(
        _argv(node, prompt, schema, session_id, claude_cmd),
        worktree,
        env,
        timeout_s,
        grace_s,
    )
    outcome, payload = _classify(run, session_id)
    ledger.job_report(repo, issue, node, session_id, payload, db_path=db_path)
    return outcome


def _argv(
    node: str,
    prompt: str,
    schema: Mapping[str, object],
    session_id: str,
    claude_cmd: Sequence[str],
) -> list[str]:
    """The fixed flag roster a launch spawns under — nothing added, nothing defaulted.

    Never `--bare`, which skips the OAuth read outright and demands an API key,
    and never `--model`, `--effort`, `--tools` or `--max-turns`: model, effort
    and tool roster all bind from the definition's frontmatter, and a flag here
    would outrank what the definition pins without saying so.

    The session id goes down as a value because it is the ledger's join key and
    the caller minted it; nothing reads it back out of the environment.
    """
    return [
        *claude_cmd,
        "--agent",
        node,
        "-p",
        prompt,
        "--output-format",
        "stream-json",
        "--verbose",
        "--session-id",
        session_id,
        "--json-schema",
        json.dumps(dict(schema)),
        "--permission-mode",
        "bypassPermissions",
    ]


# --- live supervision ---


@dataclass
class _Run:
    """Everything one supervised child declared, and how it came to an end."""

    init: dict[str, object] | None = None
    result: dict[str, object] | None = None
    exit_code: int | None = None
    kill: str | None = None
    alarm: dict[str, object] | None = None
    timed_out: bool = False
    # Whether any stream line was unreadable. A line that will not parse cannot
    # be identified, so an `init` among them is unidentifiable too — and this
    # is what lets `_classify` refuse a run whose placement and billing may
    # never have been declared at all.
    dropped: bool = False


def _supervise(
    argv: list[str],
    worktree: Path,
    env: Mapping[str, str],
    timeout_s: float,
    grace_s: float,
) -> _Run:
    """Spawn the child and read its stream as it runs, killing it when it must be.

    stdin comes from `/dev/null` so a child that waits on input dies at the
    deadline rather than blocking for good, and the environment goes down
    exactly as the sweep saw it — nothing is stripped, because the sweep is
    what proved it clean.

    The stream is read by a thread onto a queue rather than straight off the
    pipe, so the deadline still fires while the child says nothing at all: a
    blocking `readline` on a silent child has no timeout to give.

    The decoder is pinned to UTF-8 rather than left to the machine's locale,
    which is what `text=True` alone would use. Agent prose carries em-dashes
    and other non-ASCII constantly, and stream-json is UTF-8 whatever the
    locale says, so a machine running under an ASCII locale would otherwise
    turn ordinary output into a decode failure.
    """
    with open(os.devnull) as no_input:
        process = subprocess.Popen(
            argv,
            cwd=worktree,
            env=dict(env),
            stdin=no_input,
            stdout=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
    stream = process.stdout
    if stream is None:
        raise LauncherError("the child was spawned without the stdout pipe to read")
    lines: queue.Queue[str | Exception | None] = queue.Queue()
    pump = threading.Thread(target=_pump, args=(stream, lines), daemon=True)
    pump.start()
    try:
        return _watch(process, lines, worktree, timeout_s, grace_s)
    finally:
        # Cleanup, not absorption: an exception on the way out must not leave a
        # child running on the subscription with nobody watching it. Nothing is
        # caught here, so every failure still leaves as itself.
        if process.poll() is None:
            process.kill()
            process.wait()
        pump.join(grace_s)
        stream.close()


def _pump(stream: IO[str], lines: queue.Queue[str | Exception | None]) -> None:
    """Move the child's stdout onto the queue, closing it with what ended the read.

    The close sits in a `finally` because a pump that dies without one leaves
    `_watch` blocked on a queue nothing will fill again: it waits out the whole
    deadline, SIGTERMs a child that finished long before, and files a clean run
    as `timed-out`. What ended the read goes on the queue as itself — the
    exception object, not a flag — so `_watch` re-raises it and a decode
    failure or a closed pipe leaves as the failure it was.
    """
    ended: Exception | None = None
    try:
        for line in stream:
            lines.put(line)
    except Exception as error:
        ended = error
    finally:
        lines.put(ended)


def _watch(
    process: subprocess.Popen[str],
    lines: queue.Queue[str | Exception | None],
    worktree: Path,
    timeout_s: float,
    grace_s: float,
) -> _Run:
    """Read the stream to its end, taking the child down on an alarm or the deadline.

    One deadline, moved rather than duplicated: it starts as the job's wall
    clock and becomes the grace a killed child gets to honor its signal. That
    is what makes the escalation ladder a loop — expiry means the next step
    down, and there is no step past SIGKILL.

    The stream is drained after a kill rather than abandoned, because a
    SIGTERM'd child still emits its result envelope, and the accounting on it
    belongs on the row.
    """
    run = _Run()
    deadline = time.monotonic() + timeout_s
    while True:
        # One clock read a pass, clamped. Reading it twice lets the deadline
        # fall between the guard and the `get`, and `Queue.get` refuses a
        # negative timeout with a bare `ValueError` — which is no `LauncherError`,
        # so it would escape a launch whose `job-launch` row is already written
        # and leave that job reading as live for good.
        remaining = max(0.0, deadline - time.monotonic())
        if remaining <= 0:
            if run.kill == SIGKILL:
                break
            run.timed_out = run.timed_out or run.alarm is None
            _escalate(process, run)
            deadline = time.monotonic() + grace_s
            continue
        try:
            line = lines.get(timeout=remaining)
        except queue.Empty:
            continue
        if line is None:
            break
        if isinstance(line, Exception):
            raise line
        _read(line, run, worktree)
        if run.alarm is not None and run.kill is None:
            _escalate(process, run)
            deadline = time.monotonic() + grace_s
    run.exit_code = _final_exit(process, grace_s)
    return run


def _escalate(process: subprocess.Popen[str], run: _Run) -> None:
    """Take the child down one step: SIGTERM first, SIGKILL once the grace is spent.

    SIGTERM is measured safe — the child exits, the result envelope is still
    emitted, and nothing is orphaned — so it is always the first step and
    SIGKILL only ever the answer to a child that ignored it.
    """
    if run.kill is None:
        process.terminate()
        run.kill = SIGTERM
    else:
        process.kill()
        run.kill = SIGKILL


def _final_exit(process: subprocess.Popen[str], grace_s: float) -> int:
    """The child's exit code, once there is nothing left to read."""
    try:
        return process.wait(timeout=grace_s)
    except subprocess.TimeoutExpired as expired:
        raise HarnessContractViolation(
            f"the child outlived every signal sent to it and will not exit: {expired}"
        ) from expired


def _read(line: str, run: _Run, worktree: Path) -> None:
    """Take one stream line into the run, raising the alarm an `init` fails.

    The first `init` is the one that counts, and a later one never displaces
    it. The stream is drained after a kill by design, so a second `init` in
    that tail would otherwise return a standing alarm to `None` — and the
    metered, SIGTERM'd child the alarm exists to catch would be filed as an
    ordinary death with no alarm on its row.
    """
    if not line.strip():
        return
    message = _parsed(line)
    if message is None:
        run.dropped = True
        return
    if (
        message.get("type") == "system"
        and message.get("subtype") == "init"
        and run.init is None
    ):
        run.init = message
        run.alarm = _alarm(message, worktree)
    elif message.get("type") == "result":
        run.result = message


def _parsed(line: str) -> dict[str, object] | None:
    """One stream line as a message, or `None` for a line that is not one.

    Everything other than `init` and `result` is read and dropped. A line that
    is not JSON at all, or that is JSON but not an object, is unreadable rather
    than uninteresting, and the caller records that one went by: what it said
    is unrecoverable, so a run that never read an `init` can no longer be
    assumed to have simply not been sent one.
    """
    try:
        message = json.loads(line)
    except ValueError:
        return None
    return message if isinstance(message, dict) else None


def _alarm(init: dict[str, object], worktree: Path) -> dict[str, object] | None:
    """The first of the two per-run facts this `init` got wrong, if either did.

    Exactly two alarms, because these are the two that genuinely vary run to
    run: where the process was placed, and what is paying for it. `cwd` is
    compared through `resolve` so a worktree reached by a symlink is not read
    as a misplacement, and the alarm records the path the harness actually
    declared, which is what an operator needs to see.

    An `init` missing either field is a contract violation, not an alarm: the
    two checks the whole supervision rests on cannot be made at all.
    """
    for declared in (INIT_CWD, INIT_API_KEY_SOURCE):
        if declared not in init:
            raise HarnessContractViolation(
                f"the init message declares no {declared!r}, so this run's placement "
                f"and billing cannot be checked: {init}"
            )
    placed = Path(str(init[INIT_CWD])).resolve()
    expected = worktree.resolve()
    if placed != expected:
        return {
            "field": INIT_CWD,
            "observed": init[INIT_CWD],
            "expected": str(expected),
        }
    if init[INIT_API_KEY_SOURCE] != SUBSCRIPTION:
        return {
            "field": INIT_API_KEY_SOURCE,
            "observed": init[INIT_API_KEY_SOURCE],
            "expected": SUBSCRIPTION,
        }
    return None


# --- classification ---


def _classify(run: _Run, session_id: str) -> tuple[JobOutcome, dict[str, object]]:
    """What the finished run was, and the payload its `job-report` row carries.

    First match wins, and the two states that leave a run's placement and
    billing undeclared are refused before the table rather than classified into
    it. Both come down to the same thing: the two alarms the whole supervision
    rests on were never evaluated, so a run billed to a metered key would
    otherwise be filed as an ordinary timeout or an ordinary crash.

    The brief's third refusal — a stream ending with neither an envelope nor an
    exit — is enforced in `_final_exit`, which raises when a child outlives
    every signal sent to it. A run that reaches here therefore always has an
    exit code, and a second guard for it here would be a defensive one standing
    in for the real one.
    """
    if run.result is not None and run.init is None:
        raise HarnessContractViolation(
            f"the harness emitted a result envelope having never emitted an init, so "
            f"this run's placement and billing were never declared: {run.result}"
        )
    if run.init is None and run.dropped:
        raise HarnessContractViolation(
            "the child emitted a stream line that will not parse and never emitted a "
            "readable init, so this run's placement and billing were never declared"
        )
    report = None
    if run.alarm is not None:
        process_outcome, task_outcome = MISCONFIGURED, None
    elif run.timed_out:
        process_outcome, task_outcome = TIMED_OUT, None
    elif run.exit_code != 0:
        process_outcome, task_outcome = DIED, None
    elif run.result is None:
        raise HarnessContractViolation(
            "the child exited cleanly having emitted no result envelope, so it "
            "reported nothing at all"
        )
    else:
        report = _report(run.result)
        process_outcome = SCHEMA_REFUSED if report is None else CLEAN
        task_outcome = None if report is None else _task_outcome(report)
    return (
        JobOutcome(process_outcome, task_outcome, report, session_id),
        _payload(run, process_outcome, task_outcome, report),
    )


def _report(result: Mapping[str, object]) -> dict[str, object] | None:
    """The validated report on a result envelope, or `None` where the node gave none.

    A report that is present and is not an object is neither: the schema every
    node is launched under describes an object, so the harness validating
    something else against it is a promise broken.
    """
    report = result.get(STRUCTURED_OUTPUT)
    if report is None:
        return None
    if not isinstance(report, dict):
        raise HarnessContractViolation(
            f"the validated report is a {type(report).__name__}, not the object every "
            f"node schema describes: {report!r}"
        )
    return report


def _task_outcome(report: Mapping[str, object]) -> str:
    """The node's own word for how the work went, read from the report's `outcome`.

    Exactly one key, by the epic's report-envelope convention: every node schema
    carries a required top-level `outcome`, so a report the harness validated
    and that still lacks one was validated against a schema this launch never
    handed it.
    """
    if OUTCOME not in report:
        raise HarnessContractViolation(
            f"the validated report carries no {OUTCOME!r}, which every node schema "
            f"requires of it: {dict(report)}"
        )
    return str(report[OUTCOME])


def _payload(
    run: _Run,
    process_outcome: str,
    task_outcome: str | None,
    report: dict[str, object] | None,
) -> dict[str, object]:
    """The `job-report` row's payload, composed from everything the run left behind."""
    payload: dict[str, object] = {
        "process_outcome": process_outcome,
        "task_outcome": task_outcome,
        STRUCTURED_OUTPUT: report,
        # On every row, not just the ones carrying a result envelope: the exit
        # code comes from `process.wait`, never off the envelope, and a `died`
        # run has no envelope at all — so this is the one thing that separates
        # exit 1 from a segfault from an OOM kill for whoever reads the row.
        "exit_code": run.exit_code,
    }
    if run.result is not None:
        # Accounting, recorded as the harness reported it and never re-asserted.
        # A field the harness omits is left off the row rather than failing a
        # job that already ran: nothing in the graph branches on a token count,
        # and only `subtype`, `is_error`, `permission_denials` and
        # `duration_ms` are measured promises to begin with.
        for extract in RESULT_EXTRACTS:
            if extract in run.result:
                payload[extract] = run.result[extract]
        duration_ms = run.result.get(DURATION_MS)
        if isinstance(duration_ms, int | float):
            payload["duration_s"] = duration_ms / MILLISECONDS
    if run.kill is not None:
        payload["kill"] = run.kill
    if run.alarm is not None:
        payload["alarm"] = run.alarm
    return payload
