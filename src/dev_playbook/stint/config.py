"""The read-only copies every agent reads: dev-playbook, and the sibling repos.

Whatever repository a stint changes, its agents read the standards, skills,
and hooks as published, never from the stint's own branch. The config copy
is a clone of the named dev-playbook checkout's ``main``, made at launch,
mounted read-only into every call, and deleted at the end.

A repository's documents also reference other repos by ``~/workspace/<name>/``
paths, and the gate's ``reference-resolves`` check reads each one from that
repo's main checkout. The container holds no checkout but its own, so at
launch each repo the base references gets a sibling copy: the files of its
``main``, exported with ``git archive``, which runs nothing of the repo's and
carries no ``.git``. Each is mounted read-only at ``~/workspace/<name>``, and
deleted at the end.
"""

import re
import subprocess
import tarfile
import tempfile
from pathlib import Path

from dev_playbook.gitrepo import no_git_env
from dev_playbook.stint.workcopy import CopyFault, is_checkout, run_git

PLAYBOOK = "dev-playbook"
"""The repo the config copy stands in for, so never a sibling copy."""
REFERENCE = re.compile(r"~/workspace/([A-Za-z0-9._-]+)/")


def make_config(playbook: Path, config: Path) -> None:
    """Clone ``playbook``'s ``main`` to ``config``."""
    run_git(
        [
            "clone",
            "-q",
            "--no-hardlinks",
            "--branch",
            "main",
            str(playbook),
            str(config),
        ]
    )


def referenced_repos(repo: Path, base: str, own: str) -> set[str]:
    """The repos ``base`` references by ``~/workspace/<name>/``, but its own and dev-playbook."""
    done = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "grep",
            "-h",
            "-I",
            "-o",
            "-E",
            REFERENCE.pattern,
            base,
        ],
        capture_output=True,
        text=True,
        env=no_git_env(),
    )
    if done.returncode not in (0, 1):
        raise CopyFault(f"git grep in {repo} failed: {done.stderr.strip()}")
    names = {m.group(1) for m in REFERENCE.finditer(done.stdout)}
    return names - {own, PLAYBOOK}


def make_siblings(names: set[str], workspace: Path, siblings: Path) -> list[Path]:
    """Export ``main`` of each named checkout in ``workspace`` to ``siblings/<name>``.

    A name with no checkout in the workspace gets no copy: its references
    fail in the container as they fail on the host.
    """
    made: list[Path] = []
    for name in sorted(names):
        checkout = workspace / name
        if not is_checkout(checkout):
            continue
        destination = siblings / name
        destination.mkdir(parents=True)
        with tempfile.TemporaryDirectory(prefix="stint-sibling-") as temp:
            archive = Path(temp) / "main.tar"
            run_git(["-C", str(checkout), "archive", "-o", str(archive), "main"])
            with tarfile.open(archive) as tree:
                tree.extractall(destination, filter="data")
        made.append(destination)
    return made
