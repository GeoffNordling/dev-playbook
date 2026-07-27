"""Merge and install ~/.claude/settings.json from a base and one machine fragment.

Why that file is generated rather than symlinked: /dotfiles/README.md.
"""

import json
from pathlib import Path
from typing import Any


def merge(base: dict[str, Any], fragment: dict[str, Any]) -> dict[str, Any]:
    """A shared base with one machine fragment layered on top.

    Mirrors Claude Code's own cross-scope merge — objects merge key by key,
    arrays concatenate, anything else the fragment sets replaces its base
    counterpart — so the generated file behaves as a native override layer
    would if Claude Code had one.
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
    """The two lists joined in order, dropping entries equal to an earlier one."""
    joined: list[Any] = []
    seen: set[str] = set()
    for entry in [*first, *second]:
        # Settings arrays hold unhashable entries — a `hooks` array is a list
        # of matcher objects — so equality goes through a canonical rendering.
        key = json.dumps(entry, sort_keys=True)
        if key not in seen:
            seen.add(key)
            joined.append(entry)
    return joined


def settings_for(settings_dir: Path, machine: str) -> dict[str, Any]:
    """The settings one machine should run.

    A missing fragment raises: every machine in MACHINES owns a file, empty
    object and all, so absence is a packaging error rather than a machine that
    happens to need no overrides.
    """
    base = json.loads((settings_dir / "base.json").read_text())
    fragment = json.loads((settings_dir / f"{machine}.json").read_text())
    return merge(base, fragment)


def render(settings: dict[str, Any]) -> str:
    """The on-disk rendering of merged settings.

    Pinned here because the drift check compares a fresh rendering against the
    installed file byte for byte; the two must agree on formatting.
    """
    return json.dumps(settings, indent=2) + "\n"


def _installed(target: Path) -> str | None:
    """The installed file's text, or None where there is nothing installed."""
    return target.read_text() if target.exists() else None


def is_current(settings_dir: Path, machine: str, target: Path) -> bool:
    """Whether the installed file already matches what this machine should run.

    A missing file counts as out of date, not as an error: on a fresh machine
    the honest answer is "run the sync", which is what out-of-date already says.
    """
    return _installed(target) == render(settings_for(settings_dir, machine))


def install(settings_dir: Path, machine: str, target: Path) -> bool:
    """Write the merged settings to target. True if that changed anything."""
    wanted = render(settings_for(settings_dir, machine))
    if _installed(target) == wanted:
        return False

    target.parent.mkdir(parents=True, exist_ok=True)
    # Replace the path rather than write through it: where it is a symlink into
    # the repo, writing through it would edit the source.
    target.unlink(missing_ok=True)
    target.write_text(wanted)
    return True
