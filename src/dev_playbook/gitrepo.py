"""Shared git-checkout primitives for the workspace pre-commit hooks.

The two questions every hook answers the same way: which repo is the
invoking checkout a working copy of (identical answer from the main
checkout and any worktree of it), and which files does that checkout
contain (gitignore-aware, scoped to the invoking worktree).
"""

import subprocess
from pathlib import Path


class NotAGitRepository(Exception):
    """The given directory is not inside a git repository."""


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
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return sorted(
        rel for rel in result.stdout.split("\0") if rel and (root / rel).is_file()
    )
