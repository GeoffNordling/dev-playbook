"""Shared git-checkout primitives for the workspace pre-commit hooks.

The two questions every hook answers the same way: which repo is the
invoking checkout a working copy of (identical answer from the main
checkout and any worktree of it), and which files does that checkout
contain (gitignore-aware, scoped to the invoking worktree).

Both answers name their repository with an explicit ``git -C <root>``, and
``no_git_env`` is what makes that argument authoritative: a hook fired from a
linked worktree runs with an ambient ``GIT_DIR`` that would otherwise outrank
it. Every git subprocess in this package passes ``env=no_git_env()``, with one
exception that cannot: the call inside ``no_git_env`` that asks git which
variables to scrub. That one names no repository, so nothing in the ambient
environment can change its answer.
"""

import functools
import os
import subprocess
from pathlib import Path


class NotAGitRepository(Exception):
    """The given directory is not inside a git repository."""


@functools.cache
def _repository_local_env_vars() -> frozenset[str]:
    """The variables git itself reports as naming a repository.

    ``git rev-parse --local-env-vars`` is git's own answer, and ``githooks(5)``
    documents ``unset $(git rev-parse --local-env-vars)`` as the supported
    remedy for hook-exported redirection. Asking git keeps the list
    version-correct where a hand-copied one goes stale as git adds variables.
    The listing needs no repository, so it is safe to run under an ambient
    ``GIT_DIR``; the answer cannot change within a process, hence the cache.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--local-env-vars"],
        capture_output=True,
        text=True,
        check=True,
    )
    return frozenset(result.stdout.split())


def no_git_env() -> dict[str, str]:
    """``os.environ`` minus the variables that redirect git to a repository.

    Git exports an absolute ``GIT_DIR`` into the hooks it runs whenever
    discovery from the hook's working directory would land on the wrong
    repository — always from a linked worktree, and in submodule flows — and an
    absolute ``GIT_DIR`` outranks ``git -C <root>``, so inside such a hook a git
    call naming an explicit root silently operates on the hook's repository
    instead. Removing exactly git's own ``--local-env-vars`` set makes explicit
    root arguments authoritative again.

    Same intent as pre-commit's ``no_git_env``, deriving the set rather than
    hand-listing it. Two consequences of following git: transport and auth
    variables (``GIT_SSH_COMMAND``, ``GIT_ASKPASS``, ``GIT_SSL_*``) survive
    because they name no repository, and the ``GIT_CONFIG_*`` channel does not,
    because ad-hoc config relocates a repository as readily as ``GIT_DIR``
    (``core.worktree``, ``core.bare``, ``include.path``). ``GIT_CONFIG_KEY_n``
    / ``GIT_CONFIG_VALUE_n`` need no separate handling — git reads them only
    when ``GIT_CONFIG_COUNT`` is present, and that is stripped.
    """
    local = _repository_local_env_vars()
    return {k: v for k, v in os.environ.items() if k not in local}


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
