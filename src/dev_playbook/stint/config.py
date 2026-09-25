"""The config copy: dev-playbook at published ``main``, which every agent reads.

Whatever repository a stint changes, its agents read the standards, skills,
and hooks as published, never from the stint's own branch. The config copy
is a clone of the named dev-playbook checkout's ``main``, made at launch,
mounted read-only into every call, and deleted at the end.

TEMPORARY, delete after the merge: ``main`` does not yet hold three changes
the stint needs, so the clone gets the patches in ``patches/`` applied and
committed. Once ``main`` holds them, ``git apply`` refuses the patches as
already applied, and the stint cannot launch until ``PATCHES`` and the step
that applies them are deleted. The delegation workstream's head file lists
this in its worklist.
"""

from importlib import resources
from pathlib import Path

from dev_playbook.stint.workcopy import git_in, run_git

PATCHES = sorted(
    Path(str(p))
    for p in resources.files("dev_playbook.stint").joinpath("patches").iterdir()
    if p.name.endswith(".patch")
)
"""TEMPORARY: the changes ``main`` lacks. Delete after the merge."""


def make_config(playbook: Path, config: Path, patches: list[Path]) -> None:
    """Clone ``playbook``'s ``main`` to ``config`` and commit ``patches`` on it."""
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
    if not patches:
        return
    git_in(config, "apply", "--index", *(str(p) for p in patches))
    git_in(
        config,
        "-c",
        "user.name=stint",
        "-c",
        "user.email=stint@example.invalid",
        "commit",
        "-q",
        "-m",
        "stint: the changes main does not hold yet",
    )
