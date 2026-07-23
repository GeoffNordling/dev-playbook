"""Shared git-checkout primitives for the workspace pre-commit hooks.

The two questions every hook answers the same way: which repo is the
invoking checkout a working copy of (identical answer from the main
checkout and any worktree of it), and which files does that checkout
contain (gitignore-aware, scoped to the invoking worktree).

Both answers name their repository with an explicit ``git -C <root>``, and
``no_git_env`` is what makes that argument authoritative: hooks run with an
ambient ``GIT_DIR`` that would otherwise outrank it. Every git subprocess in
this package passes ``env=no_git_env()``.
"""

import os
import subprocess
from pathlib import Path

# Git redirection variables an explicit root must outrank, minus the entries
# that carry no repository location: GIT_EXEC_PATH points at git's own helper
# binaries, and the GIT_CONFIG_* family passes ad-hoc config to the child.
_GIT_ENV_KEEP_PREFIXES = ("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_")
_GIT_ENV_KEEP = frozenset({"GIT_EXEC_PATH", "GIT_CONFIG_COUNT", "GIT_ALLOW_PROTOCOL"})


class NotAGitRepository(Exception):
    """The given directory is not inside a git repository."""


def no_git_env() -> dict[str, str]:
    """``os.environ`` minus git redirection variables (``GIT_DIR`` et al.).

    Git hooks export an absolute ``GIT_DIR`` (plus ``GIT_WORK_TREE`` /
    ``GIT_INDEX_FILE`` in some flows), and an absolute ``GIT_DIR`` outranks
    ``git -C <root>`` — inside a hook, a git call naming an explicit root
    silently operates on the hook's repository instead. Stripping ``GIT_*``
    while allowlisting known-safe entries makes explicit root arguments
    authoritative. Same pattern as pre-commit's ``no_git_env``.
    """
    return {
        k: v
        for k, v in os.environ.items()
        if not k.startswith("GIT_")
        or k.startswith(_GIT_ENV_KEEP_PREFIXES)
        or k in _GIT_ENV_KEEP
    }


def canonical_repo_name(repo_root: Path) -> str:
    """Repo name from git, identical for main checkout and any worktree of it.

    Uses `git rev-parse --git-common-dir`, which points at the shared .git
    directory regardless of which worktree you're standing in. The parent of
    that directory is the repo's canonical on-disk name.
    """
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        env=no_git_env(),
    )
    if result.returncode != 0:
        raise NotAGitRepository(str(repo_root))
    common = Path(result.stdout.strip())
    if not common.is_absolute():
        common = (repo_root / common).resolve()
    return common.parent.name


def git_files(root: Path, *, tracked_only: bool = False) -> list[str]:
    """Relative paths of files in ``root``'s checkout, honoring ``.gitignore``.

    ``--cached`` lists tracked files, ``--others`` untracked ones,
    ``--exclude-standard`` drops anything ``.gitignore`` matches. With
    ``tracked_only`` only the index is listed — what "must be committed"
    requirements check; at commit time the index includes staged files. An
    entry whose working-tree file was deleted is skipped by ``is_file``.
    """
    cmd = ["git", "-C", str(root), "ls-files", "--cached"]
    if not tracked_only:
        cmd += ["--others", "--exclude-standard"]
    cmd.append("-z")
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, env=no_git_env()
    )
    return sorted(
        rel for rel in result.stdout.split("\0") if rel and (root / rel).is_file()
    )
