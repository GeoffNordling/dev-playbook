"""Open and close a front's throwaway clone, so a lap's commits outlive it.

A front works inside a container, and every window the container opens must
address a copy rather than a real file — the SELinux restamp a bind mount
performs lands on the host disk permanently and cannot be prevented by opening
the window read-only. So the front is given a fresh clone of the repository it
is assigned to change, and that clone is deleted when the lap ends. Something
on the host has to move the front's commits into the real repository before
that deletion, and this module is that something.

The round trip has two halves and one recorded fact between them:

  - ``open_clone`` makes the clone with ``--no-hardlinks`` and creates the
    front's branch in it at the lap's base commit. A local clone shares object
    files with its source by default, and a restamp would reach the real
    repository through that sharing, so the absence of sharing is verified by
    inode rather than assumed from the flag.
  - The clone records what it is in ``.git/front-clone.json`` — its source, its
    branch, and the base it started from. The file sits inside ``.git`` so it
    never shows up as an uncommitted change, and it means the closing half
    takes no arguments that could disagree with the opening half.
  - ``close_clone`` moves the commits back, then verifies the branch tip in the
    real repository is the same commit the clone held.

The commits travel by the real repository fetching from the clone, never the
clone pushing into the real repository: git refuses a push to a branch that is
checked out, and the direction has to be settled once rather than discovered
per lap.

Every failure here stops the lap. A clone is removed only after its return has
been verified, so a refused close leaves the directory on disk to be read.

Output:
    stdout — one line naming what happened and the commit it happened at.
    stderr — the fault, where a lap stops.
    exit   — 0 done, 1 the lap stops.

Usage:
    front-clone open SOURCE DESTINATION BRANCH [--base REF]
    front-clone close CLONE [--keep]
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from dev_playbook.gitrepo import no_git_env

# The clone's own record of what it is, read by the closing half. It lives
# inside ``.git`` because git reports nothing there as an uncommitted change,
# and an uncommitted change is precisely what the closing half refuses over.
METADATA = "front-clone.json"


class LapFault(Exception):
    """The round trip cannot be completed, so the lap stops rather than guess."""


def run_git(args: list[str]) -> str:
    """Run git and return its stdout stripped; a nonzero exit stops the lap.

    ``no_git_env`` is what makes an explicit ``-C <root>`` authoritative: this
    runs from pre-commit hooks and from worktrees, both of which export an
    absolute ``GIT_DIR`` that would otherwise outrank the argument and operate
    on a repository nobody named.
    """
    done = subprocess.run(
        ["git", *args], capture_output=True, text=True, env=no_git_env()
    )
    if done.returncode != 0:
        raise LapFault(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout.strip()


def git_in(root: Path, *args: str) -> str:
    """Run git against the checkout at ``root``."""
    return run_git(["-C", str(root), *args])


def git_ok(root: Path, *args: str) -> bool:
    """Whether a git query against ``root`` succeeds, for the yes/no questions."""
    done = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        env=no_git_env(),
    )
    return done.returncode == 0


def is_checkout(path: Path) -> bool:
    """Whether ``path`` is a git checkout this module may act on."""
    return path.is_dir() and git_ok(path, "rev-parse", "--git-dir")


def resolve_commit(root: Path, ref: str) -> str:
    """The full SHA a ref names in ``root``; an unresolvable ref stops the lap."""
    return git_in(root, "rev-parse", "--verify", f"{ref}^{{commit}}")


def branch_exists(root: Path, branch: str) -> bool:
    """Whether ``root`` already holds a local branch of that name."""
    return git_ok(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")


def object_inodes(checkout: Path) -> set[tuple[int, int]]:
    """Every object file in a checkout, identified by device and inode.

    Two object files that answer alike are one file on disk under two names,
    which is what a default local clone produces and what this module exists
    to keep out of a lap.
    """
    objects = checkout / ".git" / "objects"
    found: set[tuple[int, int]] = set()
    for path in objects.rglob("*"):
        if path.is_file():
            info = path.stat()
            found.add((info.st_dev, info.st_ino))
    return found


def shared_object_files(clone: Path, source: Path) -> list[Path]:
    """Object files the clone and its source hold as one file on disk.

    An empty list is the only acceptable answer: a restamp applied to a shared
    file reaches the real repository, which is the fault the whole arrangement
    is built to avoid.
    """
    original = object_inodes(source)
    objects = clone / ".git" / "objects"
    shared: list[Path] = []
    for path in sorted(objects.rglob("*")):
        if path.is_file():
            info = path.stat()
            if (info.st_dev, info.st_ino) in original:
                shared.append(path)
    return shared


def uncommitted(clone: Path) -> list[str]:
    """The clone's uncommitted changes, as git's short status lines.

    Nothing in git protects work that was never committed, and the clone is
    deleted at the end of the lap, so this is the one thing whose loss the
    round trip cannot undo.
    """
    status = git_in(clone, "status", "--porcelain")
    return status.splitlines() if status else []


def metadata_path(clone: Path) -> Path:
    """Where a clone records what it is."""
    return clone / ".git" / METADATA


def read_metadata(clone: Path) -> dict:
    """What the clone records about itself; its absence stops the lap.

    A directory with no record was not opened here, and closing it would move
    commits between repositories nobody chose.
    """
    path = metadata_path(clone)
    if not path.is_file():
        raise LapFault(f"{clone} carries no {METADATA}, so it was not opened here")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise LapFault(f"cannot read {path}: {err}") from err
    if not isinstance(loaded, dict):
        raise LapFault(f"{path} does not hold a JSON object")
    missing = [key for key in ("source", "branch", "base") if key not in loaded]
    if missing:
        raise LapFault(f"{path} names no {', '.join(missing)}")
    return loaded


def open_clone(
    source: Path, destination: Path, branch: str, base: str | None = None
) -> str:
    """Clone ``source`` to ``destination`` and start ``branch`` there.

    The base defaults to the source's current ``HEAD``, which is the lap's
    shared starting commit. The branch is made in the clone alone: the real
    repository gains it only when the commits come back, so nothing there is
    left half-started by a lap that never finished.

    Returns the base commit the front starts from.
    """
    source = source.resolve()
    destination = destination.resolve()
    if not is_checkout(source):
        raise LapFault(f"{source} is not a git checkout")
    if destination.exists():
        raise LapFault(f"{destination} already exists; a lap's clone is made fresh")
    if branch_exists(source, branch):
        raise LapFault(
            f"{source} already holds a branch named {branch}; "
            "a front's branch is made for the lap, not reused"
        )
    base_sha = resolve_commit(source, base or "HEAD")

    run_git(["clone", "--no-hardlinks", str(source), str(destination)])

    alternates = destination / ".git" / "objects" / "info" / "alternates"
    if alternates.exists():
        raise LapFault(
            f"{destination} borrows objects through {alternates}, "
            "so its files are not its own"
        )
    shared = shared_object_files(destination, source)
    if shared:
        raise LapFault(
            f"{len(shared)} object file(s) in {destination} are the same file on "
            f"disk as {source}'s, first {shared[0]}"
        )

    git_in(destination, "checkout", "-b", branch, base_sha)
    metadata_path(destination).write_text(
        json.dumps(
            {"source": str(source), "branch": branch, "base": base_sha}, indent=2
        )
        + "\n",
        encoding="utf-8",
    )
    return base_sha


def close_clone(clone: Path) -> str:
    """Move the front's commits into the real repository and verify they landed.

    Returns the commit the branch now names in both places. Every check before
    the fetch refuses rather than repairs, and the check after it is the one
    that matters: the branch tip in the real repository is the commit the clone
    held, or the lap stops.
    """
    clone = clone.resolve()
    if not is_checkout(clone):
        raise LapFault(f"{clone} is not a git checkout")
    recorded = read_metadata(clone)
    source = Path(recorded["source"])
    branch = str(recorded["branch"])
    base = str(recorded["base"])

    if not is_checkout(source):
        raise LapFault(f"{source}, which {clone} was cloned from, is not a checkout")
    origin = git_in(clone, "remote", "get-url", "origin")
    if Path(origin).resolve() != source.resolve():
        raise LapFault(f"{clone} has origin {origin}, not the {source} it records")

    dirty = uncommitted(clone)
    if dirty:
        raise LapFault(
            f"{clone} holds {len(dirty)} uncommitted change(s) that would be lost "
            f"with it: {'; '.join(dirty[:5])}"
        )

    tip = resolve_commit(clone, branch)
    if not git_ok(clone, "merge-base", "--is-ancestor", base, branch):
        raise LapFault(
            f"{base[:12]} is not an ancestor of {branch}; "
            "the front rewrote the commit the lap started from"
        )

    git_in(source, "fetch", "--no-tags", str(clone), f"{branch}:{branch}")

    landed = resolve_commit(source, branch)
    if landed != tip:
        raise LapFault(
            f"{branch} is {landed} in {source} but {tip} in {clone}; "
            "the commits did not arrive"
        )
    return tip


def remove_clone(clone: Path) -> None:
    """Delete a clone whose return has been verified."""
    shutil.rmtree(clone)


def build_parser() -> argparse.ArgumentParser:
    """The two halves of the round trip, as subcommands."""
    parser = argparse.ArgumentParser(
        prog="front-clone",
        description="Open and close a front's throwaway clone for one lap.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    opener = commands.add_parser("open", help="clone a repository for one front")
    opener.add_argument("source", type=Path, help="the real repository")
    opener.add_argument("destination", type=Path, help="where the clone is made")
    opener.add_argument("branch", help="the branch the front works on")
    opener.add_argument(
        "--base",
        default=None,
        help="the commit the lap starts from (default: the source's HEAD)",
    )

    closer = commands.add_parser("close", help="return a front's commits and delete")
    closer.add_argument("clone", type=Path, help="the clone to close")
    closer.add_argument(
        "--keep",
        action="store_true",
        help="verify the return but leave the clone on disk",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run one half of the round trip; return the process exit code."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "open":
            base = open_clone(args.source, args.destination, args.branch, args.base)
            print(f"opened {args.destination} on {args.branch} at {base}")
        else:
            tip = close_clone(args.clone)
            if not args.keep:
                remove_clone(args.clone)
            print(f"closed {args.clone} at {tip}")
    except LapFault as err:
        print(f"front-clone: the lap stops: {err}", file=sys.stderr)
        return 1
    return 0
