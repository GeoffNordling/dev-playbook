"""One consumer's state and landings, read and written on its ``origin/main``.

Reading: the pin its published ``main`` carries, and the remote branches with
commits ``main`` does not have. Landing: the green commit pushed to ``main``,
and the red worktree on ``bump-pin-<sha12>`` holding the committed bump for an
agent to work.
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import gitrepo
from dev_playbook.errors import ToolError
from dev_playbook.pins.config import pinned_rev, rewritten
from dev_playbook.pins.worktree import git_out

WORKTREES = Path(".claude") / "worktrees"


@dataclass(frozen=True)
class Branch:
    """One remote branch carrying commits ``origin/main`` does not have."""

    name: str
    date: str
    ahead: int

    def render(self) -> str:
        """``name (date, n ahead)``."""
        return f"{self.name} ({self.date}, {self.ahead} ahead)"


def pinned_on_main(repo: Path, url: str) -> str:
    """The dev-playbook rev ``origin/main`` pins, refusing a tree with no pin."""
    result = subprocess.run(
        ["git", "-C", str(repo), "show", "origin/main:.pre-commit-config.yaml"],
        capture_output=True,
        text=True,
        env=gitrepo.no_git_env(),
    )
    if result.returncode != 0:
        raise ToolError("no .pre-commit-config.yaml on origin/main")
    rev = pinned_rev(result.stdout, url)
    if rev is None:
        raise ToolError(f"no {url} pin on origin/main; wiring one is adoption")
    return rev


def unmerged_branches(repo: Path) -> list[Branch]:
    """Every ``origin/*`` branch with commits not on ``origin/main``, newest first.

    ``origin/HEAD`` is a pointer and ``origin/main`` is the base, so neither is
    a branch here. A branch fully merged reads as zero ahead and is left out:
    it is history, and the question is what is still in flight.
    """
    listing = git_out(
        repo,
        "for-each-ref",
        "--format=%(refname:short)%09%(committerdate:short)",
        "refs/remotes/origin/",
    )
    branches = []
    for line in listing.splitlines():
        name, _, date = line.partition("\t")
        if name in ("origin/HEAD", "origin/main"):
            continue
        ahead = int(git_out(repo, "rev-list", "--count", f"origin/main..{name}"))
        if ahead:
            branches.append(Branch(name.removeprefix("origin/"), date, ahead))
    return sorted(branches, key=lambda branch: branch.date, reverse=True)


def branch_notes(branches: list[Branch]) -> str:
    """The unmerged-branch report as one ledger cell."""
    if not branches:
        return "no unmerged branches"
    return "unmerged: " + "; ".join(branch.render() for branch in branches)


def branch_name(sha: str) -> str:
    """``bump-pin-<sha12>``: the branch and worktree name for one release."""
    return f"bump-pin-{sha[:12]}"


def land_green(tree: Path, old: str, sha: str) -> str:
    """Commit the moved pin in the probe worktree and push it to ``main``; the new sha.

    Hooks run: the consumer's commit hook is the gate at the new pin, its
    pre-push hook is ``make check``, and a rejection from either is the caller's
    ``failed`` row. The worktree is throwaway, so the commit's home is
    ``origin/main`` or nowhere.
    """
    git_out(tree, "add", ".pre-commit-config.yaml")
    git_out(
        tree,
        "commit",
        "-q",
        "-m",
        f"Pin dev-playbook at {sha[:12]}\n\n"
        f"update-pins moved the standards pin {old[:12]} -> {sha[:12]}; "
        "the gate is green at the new pin.",
    )
    landed = git_out(tree, "rev-parse", "HEAD")
    git_out(tree, "push", "-q", "origin", "HEAD:main")
    return landed


def red_worktree(
    repo: Path, url: str, sha: str, ids: tuple[str, ...]
) -> tuple[Path, str]:
    """A persistent worktree on ``bump-pin-<sha12>`` holding the moved pin; path and old rev.

    Cut from ``origin/main``, which is the tree the probe judged, so the
    findings reproduce there exactly. The pin is committed with ``--no-verify``
    because the gate is known red; the agent's last commit runs it. A worktree
    already there is refused rather than reused: it belongs to an earlier run
    that did not finish, and its state is the user's to read.
    """
    branch = branch_name(sha)
    path = repo / WORKTREES / branch
    if path.exists():
        raise ToolError(f"worktree {path} already exists, kept from an earlier run")
    path.parent.mkdir(parents=True, exist_ok=True)
    git_out(repo, "worktree", "add", "-q", "-b", branch, str(path), "origin/main")
    config = path / ".pre-commit-config.yaml"
    updated, old = rewritten(config.read_text(encoding="utf-8"), url, sha, ids)
    config.write_text(updated, encoding="utf-8")
    git_out(path, "add", ".pre-commit-config.yaml")
    git_out(
        path,
        "commit",
        "-q",
        "--no-verify",
        "-m",
        f"Pin dev-playbook at {sha[:12]}\n\n"
        f"update-pins moved the standards pin {old[:12]} -> {sha[:12]}; "
        "the gate is red at the new pin and the findings follow.",
    )
    return path, old
