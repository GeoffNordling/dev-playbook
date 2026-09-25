"""The config copy: dev-playbook at published ``main``, which every agent reads.

Whatever repository a stint changes, its agents read the standards, skills,
and hooks as published, never from the stint's own branch. The config copy
is a clone of the named dev-playbook checkout's ``main``, made at launch,
mounted read-only into every call, and deleted at the end.
"""

from pathlib import Path

from dev_playbook.stint.workcopy import run_git


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
