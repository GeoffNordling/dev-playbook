"""Shared workspace and git helpers for dev-playbook tools."""

import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    "RDMCoreUIWorkspace",
    "RDMWorkspace",
    "personal-trainer",
    "tail-claude",
}


def find_workplace() -> Path:
    """Auto-detect the workplace/workspace directory on Mac or Linux."""
    candidates = [
        Path("/Volumes/workplace"),
        Path.home() / "workplace",
        Path.home() / "workspace",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    print(
        "Could not auto-detect workplace directory. Pass it as an argument.",
        file=sys.stderr,
    )
    sys.exit(1)


def list_repos(
    workspace: Path,
    *,
    skip: set[str] | None = None,
    require_git: bool = True,
) -> list[Path]:
    """Return sorted repo paths in a workspace directory.

    Parameters
    ----------
    workspace:
        Root directory containing repos.
    skip:
        Extra directory names to skip (merged with the global SKIP_DIRS).
    require_git:
        If True, only include directories that contain a .git folder.
    """
    skip_all = SKIP_DIRS | (skip or set())
    repos = []
    for entry in sorted(workspace.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name.startswith("."):
            continue
        if entry.name in skip_all:
            continue
        if require_git and not (entry / ".git").exists():
            continue
        repos.append(entry)
    return repos


def git(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    """Run a git command and return the completed process."""
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=30,
    )
