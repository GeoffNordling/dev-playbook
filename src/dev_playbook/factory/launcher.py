"""The job launcher — one factory node launch, preflight through spawn to a ledgered job."""

import json
import os
import shutil
import subprocess
import uuid
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

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


def main_checkout(worktree: Path) -> Path:
    """The main checkout a worktree is linked to, derived from the worktree alone.

    `git rev-parse --git-common-dir` names the main checkout's `.git`, whose
    parent is the checkout. Asking git is what lets a caller hand over a
    worktree and nothing else: the sweep needs the main checkout's
    `settings.local.json`, which fires into a worktree-cwd'd child, and the
    shadow check needs both trees.

    The answer comes back absolute from a linked worktree and relative from a
    main checkout, so it is joined onto the worktree either way — joining an
    absolute path discards the left side, which is exactly right here.
    """
    common = subprocess.run(
        ["git", "-C", str(worktree), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=True,
        env=gitrepo.no_git_env(),
    ).stdout.strip()
    return (worktree / common).resolve().parent


def _settings_roster(worktree: Path, env: Mapping[str, str]) -> list[Path]:
    """Every settings file a launch from `worktree` under `env` would merge.

    The user scope resolves from the swept environment's own `HOME` rather than
    the launcher's, because what is under inspection is the environment the
    child will receive — a child pointed at another home reads that home's
    settings.

    Managed settings are listed in both forms. Whether `-p` honors the drop-in
    directory is unverified, and sweeping a file that never fires is harmless
    where missing one that does is the exact hole the sweep exists for.
    """
    checkout = main_checkout(worktree)
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
    """
    findings = [
        f"environment: {var} is set" for var in BILLING_ENV_VARS if env.get(var)
    ]
    for path in _settings_roster(worktree, env):
        if path.is_file():
            findings += _swept(path)
    if findings:
        raise LaunchAborted(findings)


def _swept(path: Path) -> list[str]:
    """Findings from one settings file that exists.

    Two duties in one pass, because both need the file read. It must parse:
    `-p` silently ignores a settings file it cannot read, so a launch under one
    runs with settings nobody has seen, and this is the only place that
    surfaces. And it must carry no billing key, at the top level or in the
    `env` block it exports into the child.

    A file that parses into something other than an object — a list, a bare
    number — fails the parse duty rather than the sweep: there is no place in
    it for the keys to be, so it cannot be reported clean.
    """
    try:
        settings = json.loads(path.read_text())
    except (OSError, ValueError) as error:
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
            if settings.get(key)
        ),
        *(f"{path}: env.{var} is set" for var in BILLING_ENV_VARS if exported.get(var)),
    ]


# --- pre-spawn validation ---


def _prespawn_findings(
    node: str,
    worktree: Path,
    env: Mapping[str, str],
    agents_dir: Path,
    claude_cmd: Sequence[str],
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
        *_shadow_findings(worktree),
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


def _shadow_findings(worktree: Path) -> list[str]:
    """Findings for any repo-local copy of a factory node's definition.

    The whole six-name roster, in both trees, whatever node is being launched:
    a project-scope `.claude/agents/<name>.md` silently beats the user-scope
    definition, so a stray copy left in a checkout quietly replaces a factory
    node with whatever that file says.
    """
    findings = []
    for tree in (worktree, main_checkout(worktree)):
        for node in NODES:
            path = tree / CLAUDE_DIR / "agents" / f"{node}.md"
            if path.is_file():
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
    preflight(worktree, env)
    findings = _prespawn_findings(node, worktree, env, agents_dir, claude_cmd)
    if findings:
        raise LaunchAborted(findings)
    session_id = str(uuid.uuid4())
    ledger.job_launch(repo, issue, node, session_id, launch_payload, db_path=db_path)
    raise NotImplementedError
