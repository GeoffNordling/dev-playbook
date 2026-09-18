"""Audit the machine and the repo for a credential that meters Claude billing.

billing-lint is the detector behind the Billing card. Every other detector in
the roster reads the repository; this one reads the machine as well, because
the thing it guards against does not live in a repository. Run
non-interactively, Claude prefers a configured API key over the subscription
login and says nothing about the choice, so a misconfigured run succeeds and
the cost arrives later. There is no loud failure to catch, which is what earns
this detector its place at a gate.

Four surfaces can carry such a credential, and the detector reads all four:

  - **no-metered-env** — the live environment holds none of the billing
    variables. An empty value counts as unset, the way the shell treats it;
    any other value counts as set, ``0`` included.
  - **no-metered-shell-config** — no shell startup file assigns one. A login
    shell exports it into every later process, so an assignment here is the
    same defect as the variable being set, one reboot away.
  - **no-credential-settings** — no Claude settings file carries a key that
    mints or redirects a credential (``apiKeyHelper``, ``awsAuthRefresh``,
    ``awsCredentialExport``), and no settings file's ``env`` block sets a
    billing variable. Claude Code applies that block to every run it starts.
  - The settings leg reads the machine's files under ``~/.claude/`` and the
    repo's own under ``.claude/``, so a repo that ships a metered credential
    is caught on a machine that is otherwise clean.

``CLAUDE_CODE_OAUTH_TOKEN`` is absent from the variable list on purpose: it is
a subscription credential and so is safe.

The detector asserts rather than reports: its findings block the commit gate.
A settings file it cannot parse is a tool error, not a pass — a credential
the detector could not read is exactly the case it exists to prevent.

Output:
    stdout — one finding per line, ``location:line: billing.rule message``.
             The location is a repo-relative path for a repo surface, a
             ``~``-prefixed path for a machine file, and the word
             ``environment`` for the live environment. Machine surfaces have
             no repo-relative path, which is why the location slot widens
             here the way it does for workspace-lint.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    billing-lint [directory]
    billing-lint --list-rules
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the billing card whose
# question it answers. Each id is a module-level constant so every emission
# site references the constant, never a raw literal, and RULES (what
# --list-rules prints) cannot drift from what the detector actually emits.
NO_METERED_ENV = "billing.no-metered-env"
NO_METERED_SHELL_CONFIG = "billing.no-metered-shell-config"
NO_CREDENTIAL_SETTINGS = "billing.no-credential-settings"

RULES = (NO_METERED_ENV, NO_METERED_SHELL_CONFIG, NO_CREDENTIAL_SETTINGS)

# Set any one of these and a run goes somewhere other than the subscription: a
# metered key, a different endpoint, or a cloud provider's billing.
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

# Settings keys that mint a credential or point at a different one.
CREDENTIAL_SETTINGS_KEYS = (
    "apiKeyHelper",
    "awsAuthRefresh",
    "awsCredentialExport",
)

# The shell startup files a login or interactive shell reads, relative to the
# home directory. ``.bashrc.d`` is a directory the dotfiles loader sources in
# full, so every file in it is read rather than the directory itself.
SHELL_CONFIG_FILES = (
    ".bashrc",
    ".bash_profile",
    ".bash_login",
    ".profile",
    ".zshrc",
    ".zshenv",
    ".zprofile",
)
SHELL_CONFIG_DIR = ".bashrc.d"

# The Claude settings files, relative to the directory that holds them. The
# same two names appear under ``~/.claude/`` and under a repo's ``.claude/``.
SETTINGS_FILES = ("settings.json", "settings.local.json")

# An assignment of NAME in shell: the name at a word boundary, then ``=``. It
# matches ``export NAME=x``, ``NAME=x cmd``, and a bare ``NAME=x``, and does
# not match ``unset NAME`` or ``$NAME``.
_ASSIGNMENT = re.compile(
    r"(?:^|[^\w$])({names})\s*=".format(names="|".join(BILLING_ENV_VARS))
)


class CannotRun(Exception):
    """The detector cannot complete its scan, so it reports a tool error."""


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a location, a rule id, and a message."""

    file: str
    line: int | None
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message, self.line)


def metered_env_vars(env: dict[str, str]) -> list[str]:
    """The billing variables set in ``env``, in the order they are listed.

    An empty value counts as unset, which is how the shell treats it. Any
    other value counts as set, ``0`` included: refusing a disabled-looking
    flag is the safe direction to be wrong in.
    """
    return [name for name in BILLING_ENV_VARS if env.get(name)]


def credential_settings_keys(settings: dict) -> list[str]:
    """The credential-minting keys present in a settings mapping."""
    return [key for key in CREDENTIAL_SETTINGS_KEYS if key in settings]


def settings_env_vars(settings: dict) -> list[str]:
    """The billing variables set in a settings mapping's ``env`` block.

    Claude Code applies that block to every run it starts, so a variable here
    reaches the model the same way one exported from a shell does. A block
    that is not a mapping is malformed rather than clean, so it raises.
    """
    block = settings.get("env", {})
    if not isinstance(block, dict):
        raise CannotRun("a settings file's env key is not a mapping")
    return metered_env_vars({k: str(v) for k, v in block.items()})


def assignments_in(text: str) -> list[tuple[int, str]]:
    """Each billing-variable assignment in shell text, as (line number, name).

    A line whose first non-blank character is ``#`` is a comment and is
    skipped, so prose naming a variable does not read as configuring one.
    """
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        found.extend((number, match.group(1)) for match in _ASSIGNMENT.finditer(line))
    return found


def read_settings(path: Path) -> dict:
    """A settings file as a mapping, or empty where there is no such file.

    A file that exists and does not parse raises: an unreadable settings file
    is the case this detector exists to catch, so it is never a pass.
    """
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise CannotRun(f"cannot read {path}: {err}") from err
    if not isinstance(loaded, dict):
        raise CannotRun(f"{path} does not hold a JSON object")
    return loaded


def check_env(env: dict[str, str]) -> list[Finding]:
    """The live environment carries no billing variable."""
    return [
        Finding(
            "environment",
            None,
            NO_METERED_ENV,
            f"{name} is set, which routes a run to metered billing",
        )
        for name in metered_env_vars(env)
    ]


def shell_config_files(home: Path) -> list[Path]:
    """The shell startup files present under ``home``, in a stable order."""
    present = [home / name for name in SHELL_CONFIG_FILES]
    loader = home / SHELL_CONFIG_DIR
    if loader.is_dir():
        present.extend(sorted(path for path in loader.iterdir() if path.is_file()))
    return [path for path in present if path.is_file()]


def check_shell_config(home: Path) -> list[Finding]:
    """No shell startup file assigns a billing variable."""
    findings: list[Finding] = []
    for path in shell_config_files(home):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            raise CannotRun(f"cannot read {path}: {err}") from err
        findings.extend(
            Finding(
                _display(path, home, "~/"),
                number,
                NO_METERED_SHELL_CONFIG,
                f"{name} is assigned here, so every later shell carries it",
            )
            for number, name in assignments_in(text)
        )
    return findings


def check_settings(home: Path, root: Path) -> list[Finding]:
    """No settings file mints a credential or sets a billing variable.

    Both the machine's settings under ``~/.claude/`` and the repo's own under
    ``.claude/`` are read, so neither a machine nor a repo can carry one past
    this detector alone.
    """
    findings: list[Finding] = []
    directories = ((home / ".claude", home, "~/"), (root / ".claude", root, ""))
    for directory, base, prefix in directories:
        for name in SETTINGS_FILES:
            path = directory / name
            settings = read_settings(path)
            location = _display(path, base, prefix)
            findings.extend(
                Finding(
                    location,
                    None,
                    NO_CREDENTIAL_SETTINGS,
                    f"{key} mints or redirects a credential",
                )
                for key in credential_settings_keys(settings)
            )
            findings.extend(
                Finding(
                    location,
                    None,
                    NO_CREDENTIAL_SETTINGS,
                    f"the env block sets {var}, which meters every run",
                )
                for var in settings_env_vars(settings)
            )
    return findings


def _display(path: Path, base: Path, prefix: str) -> str:
    """A path as the finding shows it, relative to ``base`` behind ``prefix``.

    The prefix is the caller's, not inferred from the path: a machine surface
    shows as ``~/.bashrc`` whichever directory HOME names, so a test's home
    and the real one render alike.
    """
    return f"{prefix}{path.relative_to(base)}"


def home_directory(env: dict[str, str]) -> Path:
    """The home directory whose configuration this run audits.

    Taken from ``HOME`` rather than inferred, and its absence is a tool error:
    a scan that silently audits the wrong directory reports a clean machine it
    never looked at.
    """
    home = env.get("HOME")
    if not home:
        raise CannotRun("HOME is not set, so the machine's surfaces cannot be found")
    path = Path(home)
    if not path.is_dir():
        raise CannotRun(f"HOME names {home}, which is not a directory")
    return path


def main(argv: list[str] | None = None) -> int:
    """Audit the machine and the repo; return the detector's exit code."""
    parser = argparse.ArgumentParser(
        prog="billing-lint",
        description="Audit for a credential that meters Claude billing.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)
    root = Path(args.directory).resolve()

    env = dict(os.environ)
    try:
        home = home_directory(env)
        findings = check_env(env)
        findings.extend(check_shell_config(home))
        findings.extend(check_settings(home, root))
    except CannotRun as err:
        print(f"billing-lint: cannot run: {err}", file=sys.stderr)
        return 2

    for finding in sorted(findings, key=lambda f: (f.file, f.line or 0, f.rule)):
        print(finding.render())

    if findings:
        print(
            f"billing-lint: {len(findings)} finding(s); this machine or repo can "
            "bill the metered API",
            file=sys.stderr,
        )
        return 1
    print("billing-lint: clean (no metered credential on 4 surfaces)", file=sys.stderr)
    return 0
