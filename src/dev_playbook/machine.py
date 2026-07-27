"""Machine identity and the per-machine Claude Code settings merge.

Claude Code offers no user-level local override file: `~/.claude/settings.json`
is the only user-scope settings file it reads. A workspace spanning machines
that differ in ways settings must reflect -- a Fedora sound hook, a bwrap
sandbox block -- therefore cannot ship one checked-in file and layer the
remainder on top. It has to generate the file instead.

This module supplies both halves of that: which machine we are on, and how a
shared base and one machine fragment combine. The merge deliberately mirrors
Claude Code's own cross-scope semantics (objects deep-merge, arrays
concatenate and de-duplicate, scalars are replaced), so the generated file
behaves the way a native override layer would if one existed.
"""

import json
from pathlib import Path
from typing import Any

FEDORA = "fedora"
WSL = "wsl"
MACHINES = (FEDORA, WSL)

# WSL's kernel always identifies itself here, for every distro and every user
# session. $WSL_DISTRO_NAME is friendlier but is only exported into interactive
# shells, so it is absent exactly where detection matters most -- a hook or a
# cron job. /proc/version is the reliable signal.
PROC_VERSION = Path("/proc/version")
OS_RELEASE = Path("/etc/os-release")


def detect_machine() -> str:
    """The machine key for the host this runs on, as used to name a fragment."""
    if "microsoft" in PROC_VERSION.read_text().lower():
        return WSL

    for line in OS_RELEASE.read_text().splitlines():
        if line.startswith("ID="):
            distro = line.removeprefix("ID=").strip().strip('"')
            if distro == FEDORA:
                return FEDORA
            raise ValueError(
                f"unknown machine: /etc/os-release ID={distro!r} is not WSL and "
                f"not Fedora. Add a fragment for it and extend MACHINES."
            )

    raise ValueError(f"unknown machine: no ID= line in {OS_RELEASE}")


def merge(base: dict[str, Any], fragment: dict[str, Any]) -> dict[str, Any]:
    """A shared base with one machine fragment layered on top.

    Mirrors Claude Code's cross-scope merge: nested objects merge key by key,
    arrays concatenate, and anything else in the fragment replaces its base
    counterpart. A type mismatch between the two (an object in one, a scalar
    in the other) resolves the same way a higher scope would resolve it --
    the fragment wins.
    """
    merged = dict(base)
    for key, value in fragment.items():
        existing = merged.get(key)
        if isinstance(existing, dict) and isinstance(value, dict):
            merged[key] = merge(existing, value)
        elif isinstance(existing, list) and isinstance(value, list):
            merged[key] = _concat_dedupe(existing, value)
        else:
            merged[key] = value
    return merged


def _concat_dedupe(first: list[Any], second: list[Any]) -> list[Any]:
    """The two lists joined in order, dropping entries equal to an earlier one.

    Settings arrays hold unhashable entries -- a `hooks` array is a list of
    matcher objects -- so equality is tested on a canonical JSON rendering
    rather than by putting the entries in a set.
    """
    joined: list[Any] = []
    seen: set[str] = set()
    for entry in [*first, *second]:
        key = json.dumps(entry, sort_keys=True)
        if key not in seen:
            seen.add(key)
            joined.append(entry)
    return joined


def settings_for(settings_dir: Path, machine: str) -> dict[str, Any]:
    """The settings one machine should run, merged from a source directory.

    A missing base or fragment raises: every machine in MACHINES owns a
    fragment file, empty object and all, so absence is a packaging error
    rather than a machine that happens to need no overrides.
    """
    base: dict[str, Any] = json.loads((settings_dir / "base.json").read_text())
    fragment: dict[str, Any] = json.loads(
        (settings_dir / f"{machine}.json").read_text()
    )
    return merge(base, fragment)


def render(settings: dict[str, Any]) -> str:
    """The on-disk rendering of merged settings.

    Pinned here rather than at the call site because the drift check compares
    a freshly rendered string against the installed file byte for byte; the
    two must agree on formatting or every check reports drift.
    """
    return json.dumps(settings, indent=2) + "\n"
