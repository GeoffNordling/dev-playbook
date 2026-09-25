"""Behavioral tests for the stint's work copy — the copy round trip.

The round trip: an agent's commits are made inside a
throwaway copy that gets deleted, so the host has to move them into the real
repository first. These tests build real git repositories under tmp_path and
run the real plumbing against them, because the questions being asked are git's
own — which direction the commits travel, whether the copy shares files with
its source, and what happens when the return cannot be made.

The positive half is that a commit made in the copy lands in the real
repository at the same SHA. The negative half is larger on purpose: every way
the return can be wrong stops the stint, and a stopped stint leaves the copy on
disk to be read.
"""

import json
import subprocess
from pathlib import Path

import pytest

from dev_playbook.gitrepo import no_git_env
from dev_playbook.stint import workcopy


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
    git(path, "config", "user.name", "Work Copy Test")
    git(path, "config", "user.email", "test@example.invalid")
    git(path, "config", "commit.gpgsign", "false")
    commit(path, "first.md", "one\n", "the first commit")
    return path


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """The real repository an agent is assigned to change."""
    return make_repo(tmp_path / "real")


@pytest.fixture
def copy(tmp_path: Path) -> Path:
    """Where an agent's throwaway copy is made. Nothing is there yet."""
    return tmp_path / "work"


# --- the positive half: commits come back ---


def test_open_starts_the_branch_at_the_lap_base(repo: Path, copy: Path) -> None:
    head = git(repo, "rev-parse", "HEAD")
    base = workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert base == head
    assert git(copy, "rev-parse", "HEAD") == head
    assert git(copy, "rev-parse", "--abbrev-ref", "HEAD") == "stint-a"


def test_open_leaves_the_real_repository_without_the_branch(
    repo: Path, copy: Path
) -> None:
    """A stint that never finishes must not leave a half-started branch behind."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert not workcopy.branch_exists(repo, "stint-a")


def test_open_takes_an_explicit_base(repo: Path, copy: Path) -> None:
    first = git(repo, "rev-parse", "HEAD")
    commit(repo, "second.md", "two\n", "the second commit")
    base = workcopy.open_copy(repo, copy, "stint-a", first)
    assert base == first


def test_the_copy_shares_no_file_with_its_source(repo: Path, copy: Path) -> None:
    """The restamp reaches the real repository through a shared object file."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert workcopy.shared_object_files(copy, repo) == []


def test_a_default_clone_does_share_files(repo: Path, tmp_path: Path) -> None:
    """The control: without --no-hardlinks the sharing is real and detected."""
    plain = tmp_path / "plain"
    workcopy.run_git(["clone", str(repo), str(plain)])
    assert workcopy.shared_object_files(plain, repo) != []


def test_a_commit_made_in_the_copy_lands_in_the_repository(
    repo: Path, copy: Path
) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    made = commit(copy, "work.md", "work\n", "the agent's commit")
    returned = workcopy.close_copy(copy)
    assert returned == made
    assert git(repo, "rev-parse", "stint-a") == made


def test_the_content_arrives_with_the_commit(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    commit(copy, "work.md", "work\n", "the agent's commit")
    workcopy.close_copy(copy)
    assert git(repo, "show", "stint-a:work.md") == "work"


def test_every_commit_of_a_lap_arrives(repo: Path, copy: Path) -> None:
    base = workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    commit(copy, "a.md", "a\n", "one")
    commit(copy, "b.md", "b\n", "two")
    commit(copy, "c.md", "c\n", "three")
    workcopy.close_copy(copy)
    landed = git(repo, "rev-list", f"{base}..stint-a").splitlines()
    assert len(landed) == 3


def test_a_lap_that_wrote_nothing_closes_cleanly(repo: Path, copy: Path) -> None:
    base = workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert workcopy.close_copy(copy) == base


def test_the_copys_own_record_is_not_an_uncommitted_change(
    repo: Path, copy: Path
) -> None:
    """It sits inside .git, which is why a fresh copy closes without refusing."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert workcopy.metadata_path(copy).is_file()
    assert workcopy.close_copy(copy)


def test_close_deletes_the_copy(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    commit(copy, "work.md", "work\n", "the agent's commit")
    workcopy.close_copy(copy)
    assert not copy.exists()


# --- the negative half: every wrong return stops the stint ---


def test_uncommitted_work_stops_the_close(repo: Path, copy: Path) -> None:
    """It would die with the copy, and nothing in git could bring it back."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    (copy / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    with pytest.raises(workcopy.CopyFault, match="uncommitted"):
        workcopy.close_copy(copy)


def test_a_refused_close_leaves_the_copy_on_disk(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    (copy / "unsaved.md").write_text("never committed\n", encoding="utf-8")
    with pytest.raises(workcopy.CopyFault):
        workcopy.close_copy(copy)
    assert (copy / "unsaved.md").is_file()


def test_a_staged_but_uncommitted_change_stops_the_close(
    repo: Path, copy: Path
) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    (copy / "staged.md").write_text("staged\n", encoding="utf-8")
    git(copy, "add", "staged.md")
    with pytest.raises(workcopy.CopyFault, match="uncommitted"):
        workcopy.close_copy(copy)


def test_a_missing_branch_stops_the_close(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    git(copy, "checkout", "main")
    git(copy, "branch", "-D", "stint-a")
    with pytest.raises(workcopy.CopyFault, match="couldn't find remote ref"):
        workcopy.close_copy(copy)


def test_a_rewritten_base_stops_the_close(repo: Path, copy: Path) -> None:
    """The agent must build on the stint's starting commit, not replace it."""
    first = git(repo, "rev-parse", "HEAD")
    commit(repo, "second.md", "two\n", "the second commit")
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    git(copy, "reset", "--hard", first)
    commit(copy, "work.md", "work\n", "built on the wrong base")
    with pytest.raises(workcopy.CopyFault, match="not an ancestor"):
        workcopy.close_copy(copy)


def test_a_branch_checked_out_in_the_repository_stops_the_close(
    repo: Path, copy: Path
) -> None:
    """Git refuses to fetch into a checked-out branch, and the stint surfaces it."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    commit(copy, "work.md", "work\n", "the agent's commit")
    git(repo, "checkout", "-b", "stint-a")
    with pytest.raises(workcopy.CopyFault, match="checked out at"):
        workcopy.close_copy(copy)


def test_a_diverged_branch_stops_the_close(repo: Path, copy: Path) -> None:
    """Something else moved the branch, so the return is not a fast-forward."""
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    commit(copy, "work.md", "work\n", "the agent's commit")
    git(repo, "checkout", "-b", "elsewhere")
    commit(repo, "other.md", "other\n", "a commit the agent never saw")
    git(repo, "branch", "stint-a", "HEAD")
    git(repo, "checkout", "main")
    with pytest.raises(workcopy.CopyFault, match="non-fast-forward"):
        workcopy.close_copy(copy)


def test_a_directory_opened_by_something_else_stops_the_close(
    repo: Path, tmp_path: Path
) -> None:
    plain = tmp_path / "plain"
    workcopy.run_git(["clone", "--no-hardlinks", str(repo), str(plain)])
    with pytest.raises(workcopy.CopyFault, match="was not opened here"):
        workcopy.close_copy(plain)


def test_a_record_naming_another_repository_stops_the_close(
    repo: Path, copy: Path, tmp_path: Path
) -> None:
    """The record and the copy's own origin must name the same repository."""
    other = make_repo(tmp_path / "other")
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    workcopy.metadata_path(copy).write_text(
        json.dumps({"source": str(other), "branch": "stint-a", "base": "HEAD"}),
        encoding="utf-8",
    )
    with pytest.raises(workcopy.CopyFault, match="origin"):
        workcopy.close_copy(copy)


def test_the_copy_carries_the_repositorys_own_origin(repo: Path, copy: Path) -> None:
    """Code that reads the GitHub slug from origin reads the same slug in the copy."""
    url = "https://github.com/owner/real.git"
    git(repo, "remote", "add", "origin", url)
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    assert workcopy.copy_origin(copy) == url
    commit(copy, "second.md", "two\n", "the stint's work")
    workcopy.close_copy(copy)
    assert git(repo, "log", "-1", "--format=%s", "stint-a") == "the stint's work"


def test_an_unreadable_record_stops_the_close(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    workcopy.metadata_path(copy).write_text("{not json", encoding="utf-8")
    with pytest.raises(workcopy.CopyFault, match="cannot read"):
        workcopy.close_copy(copy)


def test_a_record_missing_a_field_stops_the_close(repo: Path, copy: Path) -> None:
    workcopy.open_copy(repo, copy, "stint-a", "HEAD")
    workcopy.metadata_path(copy).write_text(
        json.dumps({"source": "/somewhere"}), encoding="utf-8"
    )
    with pytest.raises(workcopy.CopyFault, match="names no"):
        workcopy.close_copy(copy)


def test_an_existing_destination_stops_the_close(repo: Path, copy: Path) -> None:
    copy.mkdir()
    with pytest.raises(workcopy.CopyFault, match="already exists"):
        workcopy.open_copy(repo, copy, "stint-a", "HEAD")


def test_a_source_that_is_not_a_checkout_stops_the_close(
    tmp_path: Path, copy: Path
) -> None:
    plain = tmp_path / "not-a-repo"
    plain.mkdir()
    with pytest.raises(workcopy.CopyFault, match="not a git checkout"):
        workcopy.open_copy(plain, copy, "stint-a", "HEAD")


def test_a_branch_the_repository_already_holds_stops_the_close(
    repo: Path, copy: Path
) -> None:
    git(repo, "branch", "stint-a")
    with pytest.raises(workcopy.CopyFault, match="already holds a branch"):
        workcopy.open_copy(repo, copy, "stint-a", "HEAD")


def test_a_base_that_does_not_resolve_stops_the_close(repo: Path, copy: Path) -> None:
    with pytest.raises(workcopy.CopyFault, match="rev-parse --verify"):
        workcopy.open_copy(repo, copy, "stint-a", "no-such-ref")
