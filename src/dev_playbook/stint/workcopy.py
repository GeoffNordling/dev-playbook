"""The stint's work copy: a throwaway clone whose commits outlive it.

Every agent call of a stint runs in a container, and a container mounts only
copies made for the stint, never a real file: podman's SELinux option
relabels whatever it mounts, permanently, even read-only. So the stint works
on a fresh clone of its repository, and the clone is deleted at the end.
Something on the host has to bring the stint's commits into the repository
before that, and this module is that something.

The round trip has two halves and one recorded fact between them:

  - ``open_copy`` clones with ``--no-hardlinks`` and starts the stint's
    branch at its base commit. A local clone shares object files with its
    source by default, and a relabel would reach the repository through that
    sharing, so the absence of sharing is verified by inode, not assumed.
  - The copy records what it is in ``.git/stint-workcopy.json``: its source,
    its branch, and its base. The file sits inside ``.git`` so it is never an
    uncommitted change, and the closing half takes no arguments that could
    disagree with the opening half.
  - ``close_copy`` brings the commits back, verifies the branch tip in the
    repository is the commit the copy held, and only then deletes the copy.

The commits travel by the repository fetching from the copy, never the copy
pushing: git refuses a push to a branch that is checked out.

The closing half never runs git *in* the copy. The agents could write the
copy's ``.git``, so its config, hooks, and attributes are theirs to set, and
git runs several of them on its own: ``core.fsmonitor`` on an index refresh,
a hook, a filter driver named in the attributes. Any of those would run on
the host, outside the container. So the copy is only read as data: its origin
from its config file as text, its commits by the repository fetching them
(the serving side of a fetch is git's one path built to be safe against an
untrusted repository), and its files by the repository comparing them against
the fetched tip under its own config. ``test_stint_workcopy_traps.py`` plants
a trigger at every point and holds this.

Every failure raises ``CopyFault``, and a refused close leaves the copy on
disk to be read.
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from dev_playbook.gitrepo import no_git_env

# The copy's own record of what it is, read by the closing half. It lives
# inside ``.git`` because git reports nothing there as an uncommitted change,
# and an uncommitted change is what the closing half refuses over.
METADATA = "stint-workcopy.json"


class CopyFault(Exception):
    """The round trip cannot be completed, so it stops rather than guess."""


def run_git(args: list[str]) -> str:
    """Run git and return its stdout stripped; a nonzero exit raises.

    ``no_git_env`` is what makes an explicit ``-C <root>`` authoritative: this
    runs from pre-commit hooks and from worktrees, both of which export an
    absolute ``GIT_DIR`` that would otherwise outrank the argument and operate
    on a repository nobody named.
    """
    done = subprocess.run(
        ["git", *args], capture_output=True, text=True, env=no_git_env()
    )
    if done.returncode != 0:
        raise CopyFault(f"git {' '.join(args)} failed: {done.stderr.strip()}")
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
    """The full SHA a ref names in ``root``; an unresolvable ref raises."""
    return git_in(root, "rev-parse", "--verify", f"{ref}^{{commit}}")


def branch_exists(root: Path, branch: str) -> bool:
    """Whether ``root`` already holds a local branch of that name."""
    return git_ok(root, "show-ref", "--verify", "--quiet", f"refs/heads/{branch}")


def object_inodes(checkout: Path) -> set[tuple[int, int]]:
    """Every object file in a checkout, identified by device and inode.

    Two object files that answer alike are one file on disk under two names,
    which is what a default local clone produces.
    """
    objects = checkout / ".git" / "objects"
    found: set[tuple[int, int]] = set()
    for path in objects.rglob("*"):
        if path.is_file():
            info = path.stat()
            found.add((info.st_dev, info.st_ino))
    return found


def shared_object_files(copy: Path, source: Path) -> list[Path]:
    """Object files the copy and its source hold as one file on disk.

    An empty list is the only acceptable answer: a relabel applied to a
    shared file reaches the repository.
    """
    original = object_inodes(source)
    objects = copy / ".git" / "objects"
    shared: list[Path] = []
    for path in sorted(objects.rglob("*")):
        if path.is_file():
            info = path.stat()
            if (info.st_dev, info.st_ino) in original:
                shared.append(path)
    return shared


def has_git_dir(copy: Path) -> bool:
    """Whether ``copy`` holds a repository, judged from files alone.

    Asking git would read the copy's config, which the agents wrote.
    """
    return (copy / ".git" / "HEAD").is_file()


def copy_origin(copy: Path) -> str:
    """The copy's ``origin`` URL, read from its config file as text.

    ``git config --file`` reads the one file and follows no ``include.path``,
    so nothing the agents wrote into the config is executed or pulled in.
    """
    return run_git(
        [
            "config",
            "--file",
            str(copy / ".git" / "config"),
            "--get",
            "remote.origin.url",
        ]
    )


def quarantine_ref(branch: str) -> str:
    """Where the stint's branch lands in the repository before it is checked."""
    return f"refs/stint-workcopy/{branch}"


def uncommitted(copy: Path, source: Path, ref: str) -> list[str]:
    """The copy's files that differ from ``ref``, as git's short status lines.

    Nothing in git protects work that was never committed, and the copy is
    deleted at the end, so this is the one loss the round trip cannot undo.
    The comparison runs in the repository, under its own config, against a
    throwaway index built from ``ref``: the copy's working files are read as
    data and its ``.git`` is not consulted at all. A change staged in the
    copy and then deleted from its files is invisible to this, which is the
    price of never reading the copy's index.
    """
    git_dir = git_in(source, "rev-parse", "--absolute-git-dir")
    base = [
        "git",
        "--git-dir",
        git_dir,
        "--work-tree",
        str(copy),
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.hooksPath=/dev/null",
    ]
    # ``status`` would also compare against the repository's own HEAD, so the
    # two halves are asked for directly: tracked files that differ from
    # ``ref``, and files ``ref`` does not track and nothing ignores. The refresh
    # exits nonzero exactly when something differs, which the diff then names.
    steps = [
        (["read-tree", ref], True),
        (["update-index", "-q", "--refresh"], False),
        (["diff-files", "--name-status"], True),
        (["ls-files", "--others", "--exclude-standard"], True),
    ]
    found: list[str] = []
    with tempfile.TemporaryDirectory() as scratch:
        env = no_git_env() | {"GIT_INDEX_FILE": str(Path(scratch) / "index")}
        for args, must_succeed in steps:
            done = subprocess.run(
                [*base, *args], capture_output=True, text=True, env=env
            )
            if must_succeed and done.returncode != 0:
                raise CopyFault(
                    f"comparing {copy} with {ref} failed: {done.stderr.strip()}"
                )
            if args[0] == "diff-files":
                found += done.stdout.splitlines()
            elif args[0] == "ls-files":
                found += [f"??\t{path}" for path in done.stdout.splitlines()]
    return found


def metadata_path(copy: Path) -> Path:
    """Where a copy records what it is."""
    return copy / ".git" / METADATA


def read_metadata(copy: Path) -> dict:
    """What the copy records about itself; its absence raises.

    A directory with no record was not opened here, and closing it would move
    commits between repositories nobody chose.
    """
    path = metadata_path(copy)
    if not path.is_file():
        raise CopyFault(f"{copy} carries no {METADATA}, so it was not opened here")
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        raise CopyFault(f"cannot read {path}: {err}") from err
    if not isinstance(loaded, dict):
        raise CopyFault(f"{path} does not hold a JSON object")
    missing = [key for key in ("source", "branch", "base") if key not in loaded]
    if missing:
        raise CopyFault(f"{path} names no {', '.join(missing)}")
    return loaded


def open_copy(source: Path, destination: Path, branch: str, base: str) -> str:
    """Clone ``source`` to ``destination`` and start ``branch`` there at ``base``.

    The branch is made in the copy alone: the repository gains it only when
    the commits come back, so a stint that never finishes leaves nothing
    half-started there.

    Returns the base commit the stint starts from.
    """
    source = source.resolve()
    destination = destination.resolve()
    if not is_checkout(source):
        raise CopyFault(f"{source} is not a git checkout")
    if destination.exists():
        raise CopyFault(f"{destination} already exists; a work copy is made fresh")
    if branch_exists(source, branch):
        raise CopyFault(
            f"{source} already holds a branch named {branch}; "
            "a stint's branch is made for the stint, not reused"
        )
    base_sha = resolve_commit(source, base)

    run_git(["clone", "--no-hardlinks", str(source), str(destination)])

    alternates = destination / ".git" / "objects" / "info" / "alternates"
    if alternates.exists():
        raise CopyFault(
            f"{destination} borrows objects through {alternates}, "
            "so its files are not its own"
        )
    shared = shared_object_files(destination, source)
    if shared:
        raise CopyFault(
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


def close_copy(copy: Path) -> str:
    """Bring the stint's commits into the repository, verify, and delete the copy.

    Returns the commit the branch names in the repository. The branch first
    lands on a quarantine ref, every check runs there, and only then does it
    move onto the real branch, through git's own fast-forward and checked-out
    refusals. Every check refuses rather than repairs, and a refusal leaves
    the copy on disk.
    """
    copy = copy.resolve()
    if not has_git_dir(copy):
        raise CopyFault(f"{copy} is not a git checkout")
    recorded = read_metadata(copy)
    source = Path(recorded["source"])
    branch = str(recorded["branch"])
    base = str(recorded["base"])

    if not is_checkout(source):
        raise CopyFault(f"{source}, which {copy} was cloned from, is not a checkout")
    origin = copy_origin(copy)
    if Path(origin).resolve() != source.resolve():
        raise CopyFault(f"{copy} has origin {origin}, not the {source} it records")

    held = quarantine_ref(branch)
    git_in(source, "fetch", "--no-tags", str(copy), f"+refs/heads/{branch}:{held}")
    try:
        tip = resolve_commit(source, held)
        dirty = uncommitted(copy, source, held)
        if dirty:
            raise CopyFault(
                f"{copy} holds {len(dirty)} uncommitted change(s) that would be "
                f"lost with it: {'; '.join(dirty[:5])}"
            )
        if not git_ok(source, "merge-base", "--is-ancestor", base, held):
            raise CopyFault(
                f"{base[:12]} is not an ancestor of {branch}; "
                "the stint rewrote the commit it started from"
            )
        git_in(source, "fetch", "--no-tags", ".", f"{held}:refs/heads/{branch}")
    finally:
        git_in(source, "update-ref", "-d", held)

    landed = resolve_commit(source, branch)
    if landed != tip:
        raise CopyFault(
            f"{branch} is {landed} in {source} but {tip} in {copy}; "
            "the commits did not arrive"
        )
    shutil.rmtree(copy)
    return tip
