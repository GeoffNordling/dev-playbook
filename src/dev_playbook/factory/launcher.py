"""The job launcher — one factory node launch, preflight through spawn to a ledgered job."""

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path

from dev_playbook import gitrepo

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


class LauncherError(Exception):
    """The base every failure this module raises derives from."""


class LaunchAborted(LauncherError):
    """Nothing spawned and nothing spent, carrying every finding that stopped it."""

    def __init__(self, findings: list[str]) -> None:
        """Hold the findings whole, and say all of them in the message."""
        self.findings = tuple(findings)
        super().__init__(f"launch aborted: {'; '.join(self.findings)}")


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
