"""Git in a consumer: one command, a fetch, a throwaway worktree of ``origin/main``.

The pin tools judge the tree a release will land on, ``origin/main``, and a
detached worktree is how they read that tree without caring what the caller's
checkout has checked out, whether it is dirty, or which branch a session there
is working: none of that is touched, and nothing is left behind.
"""

import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from dev_playbook import gitrepo
from dev_playbook.errors import ToolError


def git_out(repo: Path, *args: str) -> str:
    """One git command's stdout in ``repo``, stripped.

    Raises ToolError rather than returning a sentinel: every caller is asking a
    question whose unanswerability means the run cannot continue.
    """
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        raise ToolError(
            f"git {' '.join(args)} failed in {repo}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def fetch_origin(repo: Path) -> None:
    """Bring ``origin/main`` up to date; the probe judges that ref and nothing else."""
    git_out(repo, "fetch", "-q", "origin", "main")


def fetch_all(repo: Path) -> None:
    """Every remote branch, pruned: the branch report and the probe both read ``origin/*``."""
    git_out(repo, "fetch", "-q", "--prune", "origin")


@contextmanager
def probe_worktree(repo: Path, base: str = "origin/main") -> Iterator[Path]:
    """A throwaway detached worktree of ``repo`` at ``base``, removed on exit."""
    with tempfile.TemporaryDirectory(prefix="bump-pin-") as tmp:
        path = Path(tmp) / repo.name
        git_out(repo, "worktree", "add", "-q", "--detach", str(path), base)
        try:
            yield path
        finally:
            git_out(repo, "worktree", "remove", "--force", str(path))
