"""Behavioral tests for scripts/front-clone — the clone round trip.

Experiment one of the delegation workstream: a front's commits are made inside a
throwaway clone that gets deleted, so the host has to move them into the real
repository first. These tests build real git repositories under tmp_path and
run the real plumbing against them, because the questions being asked are git's
own — which direction the commits travel, whether the clone shares files with
its source, and what happens when the return cannot be made.

The positive half is that a commit made in the clone lands in the real
repository at the same SHA. The negative half is larger on purpose: every way
the return can be wrong stops the lap, and a stopped lap leaves the clone on
disk to be read.
"""

import json
import subprocess
from pathlib import Path

import pytest

from dev_playbook import front_clone
from dev_playbook.gitrepo import no_git_env

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "front-clone"


def git(root: Path, *args: str) -> str:
    """Run git against a scratch checkout and return its stdout, stripped."""
    done = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=True,
        env=no_git_env(),
    )
    return done.stdout.strip()


def commit(root: Path, name: str, text: str, message: str) -> str:
    """Write a file, commit it, and return the new commit's SHA."""
    (root / name).write_text(text, encoding="utf-8")
    git(root, "add", name)
    git(root, "commit", "-m", message)
    return git(root, "rev-parse", "HEAD")


def make_repo(path: Path) -> Path:
    """A scratch repository with one commit on ``main``."""
    path.mkdir(parents=True)
    git(path, "init", "-b", "main")
    git(path, "config", "user.name", "Front Clone Test")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "commit.gpgsign", "false")
    commit(path, "first.md", "one\n", "the first commit")
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """The real repository a front is assigned to change."""
    return make_repo(tmp_path / "real")


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """Where a front's throwaway clone is made. Nothing is there yet."""
    return tmp_path / "work"


# --- the positive half: commits come back ---


def test_open_starts_the_branch_at_the_lap_base(repo: Path, clone: Path) -> None:
    head = git(repo, "rev-parse", "HEAD")
    base = front_clone.open_clone(repo, clone, "front-a")
    assert base == head
    assert git(clone, "rev-parse", "HEAD") == head
    assert git(clone, "rev-parse", "--abbrev-ref", "HEAD") == "front-a"


def test_open_leaves_the_real_repository_without_the_branch(
    repo: Path, clone: Path
) -> None:
    """A lap that never finishes must not leave a half-started branch behind."""
    front_clone.open_clone(repo, clone, "front-a")
    assert not front_clone.branch_exists(repo, "front-a")


def test_open_takes_an_explicit_base(repo: Path, clone: Path) -> None:
    first = git(repo, "rev-parse", "HEAD")
    commit(repo, "second.md", "two\n", "the second commit")
    base = front_clone.open_clone(repo, clone, "front-a", base=first)
    assert base == first


def test_the_clone_shares_no_file_with_its_source(repo: Path, clone: Path) -> None:
    """The restamp reaches the real repository through a shared object file."""
    front_clone.open_clone(repo, clone, "front-a")
    assert front_clone.shared_object_files(clone, repo) == []


def test_a_default_clone_does_share_files(repo: Path, tmp_path: Path) -> None:
    """The control: without --no-hardlinks the sharing is real and detected."""
    plain = tmp_path / "plain"
    front_clone.run_git(["clone", str(repo), str(plain)])
    assert front_clone.shared_object_files(plain, repo) != []


def test_a_commit_made_in_the_clone_lands_in_the_repository(
    repo: Path, clone: Path
) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    made = commit(clone, "front.md", "work\n", "the front's commit")
    returned = front_clone.close_clone(clone)
    assert returned == made
    assert git(repo, "rev-parse", "front-a") == made


def test_the_content_arrives_with_the_commit(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    commit(clone, "front.md", "work\n", "the front's commit")
    front_clone.close_clone(clone)
    assert git(repo, "show", "front-a:front.md") == "work"


def test_every_commit_of_a_lap_arrives(repo: Path, clone: Path) -> None:
    base = front_clone.open_clone(repo, clone, "front-a")
    commit(clone, "a.md", "a\n", "one")
    commit(clone, "b.md", "b\n", "two")
    commit(clone, "c.md", "c\n", "three")
    front_clone.close_clone(clone)
    landed = git(repo, "rev-list", f"{base}..front-a").splitlines()
    assert len(landed) == 3


def test_a_lap_that_wrote_nothing_closes_cleanly(repo: Path, clone: Path) -> None:
    base = front_clone.open_clone(repo, clone, "front-a")
    assert front_clone.close_clone(clone) == base


def test_the_clones_own_record_is_not_an_uncommitted_change(
    repo: Path, clone: Path
) -> None:
    """It sits inside .git, which is why a fresh clone closes without refusing."""
    front_clone.open_clone(repo, clone, "front-a")
    assert front_clone.close_clone(clone)
    assert front_clone.metadata_path(clone).is_file()


def test_close_deletes_the_clone(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    commit(clone, "front.md", "work\n", "the front's commit")
    front_clone.close_clone(clone)
    front_clone.remove_clone(clone)
    assert not clone.exists()


# --- the negative half: every wrong return stops the lap ---


def test_uncommitted_work_stops_the_lap(repo: Path, clone: Path) -> None:
    """It would die with the clone, and nothing in git could bring it back."""
    front_clone.open_clone(repo, clone, "front-a")
    (clone / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    with pytest.raises(front_clone.LapFault, match="uncommitted"):
        front_clone.close_clone(clone)


def test_a_stopped_lap_leaves_the_clone_on_disk(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    (clone / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    front_clone.main(["close", str(clone)])
    assert (clone / "unsaved.md").is_file()


def test_a_staged_but_uncommitted_change_stops_the_lap(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    (clone / "staged.md").write_text("staged\n", encoding="utf-8")
    git(clone, "add", "staged.md")
    with pytest.raises(front_clone.LapFault, match="uncommitted"):
        front_clone.close_clone(clone)


def test_a_missing_branch_stops_the_lap(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    git(clone, "checkout", "main")
    git(clone, "branch", "-D", "front-a")
    with pytest.raises(front_clone.LapFault, match="couldn't find remote ref"):
        front_clone.close_clone(clone)


def test_a_rewritten_base_stops_the_lap(repo: Path, clone: Path) -> None:
    """The front must build on the lap's starting commit, not replace it."""
    first = git(repo, "rev-parse", "HEAD")
    commit(repo, "second.md", "two\n", "the second commit")
    front_clone.open_clone(repo, clone, "front-a")
    git(clone, "reset", "--hard", first)
    commit(clone, "front.md", "work\n", "built on the wrong base")
    with pytest.raises(front_clone.LapFault, match="not an ancestor"):
        front_clone.close_clone(clone)


def test_a_branch_checked_out_in_the_repository_stops_the_lap(
    repo: Path, clone: Path
) -> None:
    """Git refuses to fetch into a checked-out branch, and the lap surfaces it."""
    front_clone.open_clone(repo, clone, "front-a")
    commit(clone, "front.md", "work\n", "the front's commit")
    git(repo, "checkout", "-b", "front-a")
    with pytest.raises(front_clone.LapFault, match="checked out at"):
        front_clone.close_clone(clone)


def test_a_diverged_branch_stops_the_lap(repo: Path, clone: Path) -> None:
    """Something else moved the branch, so the return is not a fast-forward."""
    front_clone.open_clone(repo, clone, "front-a")
    commit(clone, "front.md", "work\n", "the front's commit")
    git(repo, "checkout", "-b", "elsewhere")
    commit(repo, "other.md", "other\n", "a commit the front never saw")
    git(repo, "branch", "front-a", "HEAD")
    git(repo, "checkout", "main")
    with pytest.raises(front_clone.LapFault, match="non-fast-forward"):
        front_clone.close_clone(clone)


def test_a_directory_opened_by_something_else_stops_the_lap(
    repo: Path, tmp_path: Path
) -> None:
    plain = tmp_path / "plain"
    front_clone.run_git(["clone", "--no-hardlinks", str(repo), str(plain)])
    with pytest.raises(front_clone.LapFault, match="was not opened here"):
        front_clone.close_clone(plain)


def test_a_record_naming_another_repository_stops_the_lap(
    repo: Path, clone: Path, tmp_path: Path
) -> None:
    """The record and the clone's own origin must name the same repository."""
    other = make_repo(tmp_path / "other")
    front_clone.open_clone(repo, clone, "front-a")
    front_clone.metadata_path(clone).write_text(
        json.dumps({"source": str(other), "branch": "front-a", "base": "HEAD"}),
        encoding="utf-8",
    )
    with pytest.raises(front_clone.LapFault, match="origin"):
        front_clone.close_clone(clone)


def test_an_unreadable_record_stops_the_lap(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    front_clone.metadata_path(clone).write_text("{not json", encoding="utf-8")
    with pytest.raises(front_clone.LapFault, match="cannot read"):
        front_clone.close_clone(clone)


def test_a_record_missing_a_field_stops_the_lap(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    front_clone.metadata_path(clone).write_text(
        json.dumps({"source": "/somewhere"}), encoding="utf-8"
    )
    with pytest.raises(front_clone.LapFault, match="names no"):
        front_clone.close_clone(clone)


def test_an_existing_destination_stops_the_lap(repo: Path, clone: Path) -> None:
    clone.mkdir()
    with pytest.raises(front_clone.LapFault, match="already exists"):
        front_clone.open_clone(repo, clone, "front-a")


def test_a_source_that_is_not_a_checkout_stops_the_lap(
    tmp_path: Path, clone: Path
) -> None:
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    with pytest.raises(front_clone.LapFault, match="not a git checkout"):
        front_clone.open_clone(plain, clone, "front-a")


def test_a_branch_the_repository_already_holds_stops_the_lap(
    repo: Path, clone: Path
) -> None:
    git(repo, "branch", "front-a")
    with pytest.raises(front_clone.LapFault, match="already holds a branch"):
        front_clone.open_clone(repo, clone, "front-a")


def test_a_base_that_does_not_resolve_stops_the_lap(repo: Path, clone: Path) -> None:
    with pytest.raises(front_clone.LapFault, match="rev-parse --verify"):
        front_clone.open_clone(repo, clone, "front-a", base="no-such-ref")


# --- the command end to end ---


def test_the_round_trip_runs_from_the_command_line(repo: Path, clone: Path) -> None:
    opened = subprocess.run(
        [
            "uv",
            "run",
            "--script",
            str(SCRIPT),
            "open",
            str(repo),
            str(clone),
            "front-a",
        ],
        capture_output=True,
        text=True,
    )
    assert opened.returncode == 0, opened.stdout + opened.stderr
    made = commit(clone, "front.md", "work\n", "the front's commit")
    closed = subprocess.run(
        ["uv", "run", "--script", str(SCRIPT), "close", str(clone)],
        capture_output=True,
        text=True,
    )
    assert closed.returncode == 0, closed.stdout + closed.stderr
    assert git(repo, "rev-parse", "front-a") == made
    assert not clone.exists()


def test_keep_verifies_the_return_without_deleting(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    made = commit(clone, "front.md", "work\n", "the front's commit")
    assert front_clone.main(["close", str(clone), "--keep"]) == 0
    assert clone.is_dir()
    assert git(repo, "rev-parse", "front-a") == made


def test_a_fault_exits_nonzero(repo: Path, clone: Path) -> None:
    front_clone.open_clone(repo, clone, "front-a")
    (clone / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    assert front_clone.main(["close", str(clone)]) == 1
