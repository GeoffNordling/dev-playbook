"""Move one consumer repo's dev-playbook pin, or check whether it can move.

The mechanical half of one repo's release. A bump can newly redden a repo — a
check that never ran there before now runs, a canonical artifact it copies has
changed — and deciding what each finding means is a judgment call. So this tool
answers one question and makes one edit, and stops there:

  ``--check``   Can this repo's pin move to the release head without going red?
  ``--write``   Move it.

``--check`` is a probe run in a throwaway detached worktree of the consumer's
``origin/main``: the pin rewritten, the gate run once, the worktree removed.
The caller's own checkout is never read or written, so it may sit on any
branch, dirty or clean, with sessions working in it. A green probe can then be
committed straight to ``main``, while a red one belongs on a branch where the
findings can be worked, and neither choice is made here. The steps:

  - **preflight** — the repo is a consumer carrying a dev-playbook pin, and its
    ``origin/main`` was just fetched.
  - **verify** — rewrite the pin and run the gate. pre-commit clones the new
    rev during this run, so this is the moment the new standard takes effect
    in that repo and, with a host's ``uv lock``, the only step that touches the
    network.

There is no baseline run at the current pin. The question is "green at the
new pin", and every finding there is worked whichever release brought it: a
repo red before the bump has more findings to work, not a reason to refuse.
``update-pins`` has judged the same way from the start, and a hand probe that
refused what the timer would have handed to the agent left a repo nobody
could bump (mission-control, 2026-09-24, four ``ref-lint`` links its current
pin already broke). Exit 2 is now an environment fault alone.

``--write`` makes the durable edit — the pinned block's ``rev:`` line and its
hook ids, and in a host the dev-playbook source's rev in ``pyproject.toml``
and ``uv.lock`` (``config.move_pin``), nothing else — and runs no gate. It asks only for a clean working
tree, so it serves the worktree a caller cuts after a red probe as readily as
``main`` after a green one.

The target is always the hook repo's release head (``release.release_head``),
and the manifest is read there too. Nothing is committed and nothing is pushed.

Output:
    stdout — the verdict line, then the gate output when the repo goes red.
    stderr — progress, and the refusal when the run cannot proceed.
    exit   — 0 green, written, or already current; 1 needs work; 2 cannot run.
"""

import argparse
import sys
from pathlib import Path

from dev_playbook.errors import ToolError
from dev_playbook.pins.config import move_pin, pinned_rev
from dev_playbook.pins.gate import run_gate
from dev_playbook.pins.release import (
    hook_repo_url,
    is_hook_repo,
    published_hook_ids,
    release_head,
)
from dev_playbook.pins.worktree import fetch_origin, git_out, probe_worktree

CLEAN = "green"
NEEDS_WORK = "needs work"
CURRENT = "already current"


def consumer_root(start: Path) -> Path:
    """The git root holding ``start``, refusing the hook repo itself.

    dev-playbook runs the published hook from its own working tree through its
    ``repo: local`` block, so it carries no pin and there is nothing here to
    move. Identity is the test, exactly as it is in workspace-lint.
    """
    root = Path(git_out(start, "rev-parse", "--show-toplevel"))
    if is_hook_repo(root):
        raise ToolError("dev-playbook dogfoods from its working tree and pins nothing")
    return root


def pinned(repo: Path, url: str) -> str:
    """The dev-playbook rev ``repo`` currently pins."""
    config = repo / ".pre-commit-config.yaml"
    if not config.is_file():
        raise ToolError(f"no .pre-commit-config.yaml in {repo}")
    rev = pinned_rev(config.read_text(encoding="utf-8"), url)
    if rev is None:
        raise ToolError(f"no {url} pin in {repo}; wiring one is adoption, not a bump")
    return rev


def require_clean(repo: Path) -> None:
    """Refuse a repo whose working tree already holds someone's changes."""
    if git_out(repo, "status", "--porcelain"):
        raise ToolError(f"uncommitted changes in {repo}")


def check(repo: Path, url: str, sha: str, ids: tuple[str, ...]) -> int:
    """Probe the bump in a throwaway worktree of ``origin/main``; the exit code is the verdict."""
    old = pinned(repo, url)
    if old == sha:
        print(f"{repo.name}: {CURRENT} ({sha[:12]})")
        return 0

    with probe_worktree(repo) as tree:
        move_pin(tree, url, sha, ids)
        print(
            f"bump-pin: {repo.name}: {old[:12]} -> {sha[:12]}, verifying",
            file=sys.stderr,
        )
        passed, output = run_gate(tree)

    if passed:
        print(f"{repo.name}: {CLEAN} at {sha[:12]}")
        return 0
    print(f"{repo.name}: {NEEDS_WORK} at {sha[:12]}\n\n{output}")
    return 1


def write(repo: Path, url: str, sha: str, ids: tuple[str, ...]) -> int:
    """Move the pin for real, hook ids with it, running no gate."""
    require_clean(repo)
    old = pinned(repo, url)
    if old == sha:
        print(f"{repo.name}: {CURRENT} ({sha[:12]})")
        return 0
    changed, _ = move_pin(repo, url, sha, ids)
    print(f"{repo.name}: pinned {old[:12]} -> {sha[:12]} ({', '.join(changed)})")
    return 0


def main(argv: list[str] | None = None) -> int:
    """The ``bump-pin`` command-line entry point.

    Returns the process exit code: 0 green, written, or already current; 1 the
    repo needs work at the new pin; 2 the run could not reach a verdict.
    """
    parser = argparse.ArgumentParser(
        prog="bump-pin",
        description=(
            "Check whether one consumer repo's dev-playbook pin can move to the "
            "release head, or move it. Commits nothing."
        ),
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check",
        action="store_true",
        help="probe the bump in a throwaway worktree of origin/main and report the verdict",
    )
    mode.add_argument(
        "--write",
        action="store_true",
        help="rewrite the rev line and hook ids, running no gate",
    )
    parser.add_argument(
        "repo",
        nargs="?",
        type=Path,
        default=Path.cwd(),
        help="the consumer repo (default: the repo the working directory sits in)",
    )
    args = parser.parse_args(argv)

    try:
        repo = consumer_root(args.repo)
        url = hook_repo_url()
        sha = release_head()
        ids = published_hook_ids(sha)
        print(f"bump-pin: target {sha} ({', '.join(ids)})", file=sys.stderr)
        if args.check:
            fetch_origin(repo)
            return check(repo, url, sha, ids)
        return write(repo, url, sha, ids)
    except ToolError as err:
        print(f"bump-pin: {err}", file=sys.stderr)
        return 2
