"""The booby trap: nothing a front plants in its clone runs on the host.

A front has write access to its clone's ``.git``, so it can set any config key,
drop any hook, and name any filter driver. Git executes several of those on its
own when a command runs in that repository, and ``front-clone close`` runs on
the host, outside the container. These tests plant a trigger at every point
git offers, run the closing half, and assert no trigger fired.

The control proves the traps are live: an ordinary ``git status`` in the same
clone sets one off. Without it, a trap that never worked would pass as safe.
"""

import os
import subprocess
from pathlib import Path

import pytest

from dev_playbook import front_clone
from dev_playbook.gitrepo import no_git_env

# Every hook name git documents. A front could plant any of them, and which
# ones a given git command fires is git's business, not this module's.
HOOKS = [
    "applypatch-msg",
    "pre-applypatch",
    "post-applypatch",
    "pre-commit",
    "pre-merge-commit",
    "prepare-commit-msg",
    "commit-msg",
    "post-commit",
    "pre-rebase",
    "post-checkout",
    "post-merge",
    "pre-push",
    "pre-receive",
    "update",
    "proc-receive",
    "post-receive",
    "post-update",
    "reference-transaction",
    "push-to-checkout",
    "pre-auto-gc",
    "post-rewrite",
    "sendemail-validate",
    "fsmonitor-watchman",
    "p4-changelist",
    "p4-prepare-changelist",
    "p4-post-changelist",
    "p4-pre-submit",
    "post-index-change",
]


def git(root: Path, *args: str) -> str:
    """Run git against a scratch checkout, with no trap of its own firing."""
    done = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    return done.stdout.strip()


def make_repo(path: Path) -> Path:
    """A scratch repository with one commit on ``main``."""
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Front Clone Test")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "commit.gpgsign", "false")
    (path / "first.md").write_text("one\n", encoding="utf-8")
    git(path, "add", "first.md")
    git(path, "commit", "-m", "the first commit")
    return path


def trap(markers: Path, name: str) -> str:
    """A shell command that leaves a marker named for the trap that fired."""
    return f"touch {markers / name}"


def write_script(path: Path, body: str) -> None:
    """An executable shell script."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!/bin/sh\n{body}\nexit 0\n", encoding="utf-8")
    path.chmod(0o755)


def plant(clone: Path, markers: Path) -> None:
    """Set every trigger a front could set in its clone.

    Called after the front's honest commit, so planting never fires anything
    the test itself runs.
    """
    gitdir = clone / ".git"
    for hook in HOOKS:
        write_script(gitdir / "hooks" / hook, trap(markers, f"hook-{hook}"))
    elsewhere = clone.parent / "planted-hooks"
    for hook in HOOKS:
        write_script(elsewhere / hook, trap(markers, f"hookspath-{hook}"))

    keys = {
        "core.hooksPath": str(elsewhere),
        "core.fsmonitor": f"{trap(markers, 'fsmonitor')}; false",
        "core.pager": trap(markers, "pager"),
        "pager.status": trap(markers, "pager-status"),
        "core.editor": trap(markers, "editor"),
        "sequence.editor": trap(markers, "sequence-editor"),
        "core.sshCommand": trap(markers, "ssh"),
        "core.askPass": trap(markers, "askpass"),
        "core.alternateRefsCommand": trap(markers, "alternate-refs"),
        "credential.helper": f"!{trap(markers, 'credential')}",
        "gpg.program": trap(markers, "gpg"),
        "diff.external": trap(markers, "diff-external"),
        "diff.trap.textconv": trap(markers, "textconv"),
        "filter.trap.clean": f"{trap(markers, 'filter-clean')}; cat",
        "filter.trap.smudge": f"{trap(markers, 'filter-smudge')}; cat",
        "filter.trap.process": trap(markers, "filter-process"),
        "filter.trap.required": "true",
        "uploadpack.packObjectsHook": trap(markers, "pack-objects-hook"),
        "remote.origin.uploadpack": trap(markers, "remote-uploadpack"),
        "include.path": str(clone.parent / "planted.gitconfig"),
    }
    for key, value in keys.items():
        git(clone, "config", key, value)
    (clone.parent / "planted.gitconfig").write_text(
        f"[core]\n\tfsmonitor = {trap(markers, 'included-fsmonitor')}; false\n",
        encoding="utf-8",
    )
    (gitdir / "info").mkdir(exist_ok=True)
    (gitdir / "info" / "attributes").write_text(
        "* filter=trap diff=trap\n", encoding="utf-8"
    )
    # A racy timestamp makes git re-read a file's content, which is when a
    # clean filter is consulted.
    for path in clone.iterdir():
        if path.is_file():
            os.utime(path, None)


@pytest.fixture
def planted(tmp_path: Path) -> tuple[Path, Path, Path, str]:
    """A clone holding one honest commit and every trap; its markers directory."""
    repo = make_repo(tmp_path / "real")
    clone = tmp_path / "work"
    markers = tmp_path / "markers"
    markers.mkdir()
    front_clone.open_clone(repo, clone, "front-a")
    (clone / "front.md").write_text("work\n", encoding="utf-8")
    git(clone, "add", "front.md")
    git(clone, "commit", "-m", "the front's honest commit")
    made = git(clone, "rev-parse", "HEAD")
    plant(clone, markers)
    return repo, clone, markers, made


def fired(markers: Path) -> list[str]:
    """The traps that left a marker."""
    return sorted(path.name for path in markers.iterdir())


def test_the_traps_are_live(planted: tuple[Path, Path, Path, str]) -> None:
    """The control: ordinary git in the clone sets a trap off."""
    _, clone, markers, _ = planted
    subprocess.run(
        ["git", "-C", str(clone), "status", "--porcelain"],
        capture_output=True,
        env=no_git_env(),
    )
    assert fired(markers) != []


def test_close_fires_no_trap(planted: tuple[Path, Path, Path, str]) -> None:
    repo, clone, markers, made = planted
    assert front_clone.close_clone(clone) == made
    assert fired(markers) == []
    assert git(repo, "rev-parse", "front-a") == made


def test_close_from_the_command_line_fires_no_trap(
    planted: tuple[Path, Path, Path, str],
) -> None:
    _, clone, markers, _ = planted
    assert front_clone.main(["close", str(clone)]) == 0
    assert fired(markers) == []
    assert not clone.exists()


def test_a_refused_close_fires_no_trap(planted: tuple[Path, Path, Path, str]) -> None:
    """The refusal path reads the clone too, and must be as careful."""
    _, clone, markers, _ = planted
    (clone / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    with pytest.raises(front_clone.LapFault, match="uncommitted"):
        front_clone.close_clone(clone)
    assert fired(markers) == []
