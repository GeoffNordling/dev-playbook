"""The billing family: the rules of ``standards/billing/``.

These are the only checks that read the machine as well as the repository,
because a metered credential is configuration of the machine a run starts
on. They read four surfaces: the live environment, the shell startup files
under ``HOME``, the machine's Claude settings under ``~/.claude/``, and the
repository's own under ``.claude/``, read from disk because
``settings.local.json`` is not tracked.

A surface that cannot be read raises :class:`CannotRead` rather than
yielding nothing: a credential the check could not read is the case the
check exists for, so it never reports clean. A finding on a machine surface
names it ``environment`` or by a ``~``-prefixed path.
"""

import json
import os
import re
from collections.abc import Iterator, Mapping
from pathlib import Path

from dev_playbook.check_registry import Finding, check
from dev_playbook.model import Repo

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
CREDENTIAL_SETTINGS_KEYS = ("apiKeyHelper", "awsAuthRefresh", "awsCredentialExport")

# The shell startup files, relative to the home directory. ``.bashrc.d`` is a
# directory the dotfiles loader sources in full, so each file in it is read.
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

# The same two names sit under ``~/.claude/`` and under a repo's ``.claude/``.
SETTINGS_FILES = ("settings.json", "settings.local.json")

# An assignment of a billing variable: the name at a word boundary, then
# ``=``. It matches ``export NAME=x``, ``NAME=x cmd``, and a bare ``NAME=x``,
# and not ``unset NAME`` or ``$NAME``.
_ASSIGNMENT = re.compile(
    r"(?:^|[^\w$])({names})\s*=".format(names="|".join(BILLING_ENV_VARS))
)


class CannotRead(Exception):
    """A surface the check must read cannot be read, so the run cannot pass."""


def metered_env_vars(env: Mapping[str, str]) -> list[str]:
    """The billing variables set in ``env``, in the order they are listed.

    An empty value counts as unset, which is how the shell treats it; any
    other value counts as set, ``0`` included.
    """
    return [name for name in BILLING_ENV_VARS if env.get(name)]


def assignments_in(text: str) -> list[tuple[int, str]]:
    """Each billing-variable assignment in shell text, as (line number, name).

    A line whose first non-blank character is ``#`` is a comment and is
    skipped.
    """
    found: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        found.extend((number, match.group(1)) for match in _ASSIGNMENT.finditer(line))
    return found


def home_directory() -> Path:
    """The directory ``HOME`` names; :class:`CannotRead` where it names none.

    Taken from ``HOME`` rather than inferred: a check that silently reads the
    wrong directory reports a clean machine it never looked at.
    """
    home = os.environ.get("HOME")
    if not home:
        raise CannotRead("HOME is not set, so the machine's surfaces cannot be found")
    path = Path(home)
    if not path.is_dir():
        raise CannotRead(f"HOME names {home}, which is not a directory")
    return path


def read_settings(path: Path) -> dict:
    """A settings file as a mapping, empty where there is no such file.

    A file that exists and does not parse to a JSON object raises
    :class:`CannotRead`.
    """
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise CannotRead(f"cannot read {path}: {err}") from err
    if not isinstance(loaded, dict):
        raise CannotRead(f"{path} does not hold a JSON object")
    return loaded


def settings_env_vars(settings: Mapping) -> list[str]:
    """The billing variables set in a settings mapping's ``env`` block.

    A block that is not a mapping raises :class:`CannotRead`.
    """
    block = settings.get("env", {})
    if not isinstance(block, dict):
        raise CannotRead("a settings file's env key is not a mapping")
    return metered_env_vars({k: str(v) for k, v in block.items()})


def shell_config_files(home: Path) -> list[Path]:
    """The shell startup files present under ``home``, in a stable order."""
    present = [home / name for name in SHELL_CONFIG_FILES]
    loader = home / SHELL_CONFIG_DIR
    if loader.is_dir():
        present.extend(sorted(path for path in loader.iterdir() if path.is_file()))
    return [path for path in present if path.is_file()]


@check("billing.no-metered-variable-in-the-environment")
def no_metered_variable_in_the_environment(repo: Repo) -> Iterator[Finding]:
    """The environment the commit runs in sets no billing variable."""
    for name in metered_env_vars(os.environ):
        yield Finding(
            "environment", None, f"{name} is set, which routes a run to metered billing"
        )


@check("billing.no-metered-variable-in-a-shell-startup-file")
def no_metered_variable_in_a_shell_startup_file(repo: Repo) -> Iterator[Finding]:
    """No shell startup file assigns a billing variable."""
    home = home_directory()
    for path in shell_config_files(home):
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as err:
            raise CannotRead(f"cannot read {path}: {err}") from err
        for number, name in assignments_in(text):
            yield Finding(
                f"~/{path.relative_to(home)}",
                number,
                f"{name} is assigned here, so every later shell carries it",
            )


@check("billing.no-credential-in-a-claude-settings-file")
def no_credential_in_a_claude_settings_file(repo: Repo) -> Iterator[Finding]:
    """No Claude settings file, the machine's or the repo's, carries a credential."""
    home = home_directory()
    for directory, location in (
        (home / ".claude", "~/.claude"),
        (repo.root / ".claude", ".claude"),
    ):
        for name in SETTINGS_FILES:
            settings = read_settings(directory / name)
            shown = f"{location}/{name}"
            for key in CREDENTIAL_SETTINGS_KEYS:
                if key in settings:
                    yield Finding(shown, None, f"{key} mints or redirects a credential")
            for var in settings_env_vars(settings):
                yield Finding(
                    shown, None, f"the env block sets {var}, which meters every run"
                )
