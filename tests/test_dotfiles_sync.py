"""Behavioral tests for the dotfiles install: package targeting, links, loader."""

import subprocess
from pathlib import Path

import pytest

from dev_playbook.dotfiles.sync import (
    LOADER_MARKER,
    PACKAGES,
    SyncError,
    ensure_bashrc_loader,
    mirror_skills,
    stale_links,
    stow_packages,
    target_for,
)


def a_dotfiles_tree(tmp_path: Path, *skills: str) -> Path:
    """A dotfiles tree with the mirror directories and the named .agents skills."""
    dotfiles = tmp_path / "dotfiles"
    (dotfiles / "dot-claude" / "skills").mkdir(parents=True)
    (dotfiles / ".agents" / "skills").mkdir(parents=True)
    for skill in skills:
        (dotfiles / ".agents" / "skills" / skill).mkdir()
    return dotfiles


def a_home(tmp_path: Path) -> Path:
    """An empty home directory with every managed target present."""
    home = tmp_path / "home"
    for name in PACKAGES.values():
        (home / name).mkdir(parents=True)
    return home


# --- package targeting -----------------------------------------------------
#
# Stow installs a package's *contents*, so a package targeted at $HOME scatters
# its files one level too high. That shipped once: aliases.sh landed in $HOME
# and ~/.bashrc.d was never created.


def test_every_package_installs_into_its_own_directory(tmp_path: Path) -> None:
    home = tmp_path / "home"

    targets = {package: target_for(home, package) for package in PACKAGES}

    assert targets == {
        ".agents": home / ".agents",
        ".bashrc.d": home / ".bashrc.d",
        "dot-claude": home / ".claude",
    }


def test_no_package_installs_directly_into_home(tmp_path: Path) -> None:
    home = tmp_path / "home"

    assert home not in {target_for(home, package) for package in PACKAGES}


def test_stow_is_invoked_once_per_package_with_that_package_as_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[list[str]] = []

    def record(argv: list[str], **kwargs: object) -> None:
        calls.append(argv)

    monkeypatch.setattr(subprocess, "run", record)
    dotfiles = tmp_path / "dotfiles"
    home = tmp_path / "home"

    stow_packages(home, dotfiles)

    assert calls == [
        ["stow", "-d", str(dotfiles), "-t", str(home / ".agents"), ".agents"],
        ["stow", "-d", str(dotfiles), "-t", str(home / ".bashrc.d"), ".bashrc.d"],
        ["stow", "-d", str(dotfiles), "-t", str(home / ".claude"), "dot-claude"],
    ]


def test_stow_creates_a_target_directory_that_does_not_exist(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(subprocess, "run", lambda argv, **kwargs: None)
    home = tmp_path / "home"

    stow_packages(home, tmp_path / "dotfiles")

    assert (home / ".bashrc.d").is_dir()


# --- skill mirroring -------------------------------------------------------


def test_mirror_skills_links_an_externally_managed_skill(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path, "zoom-out")

    mirrored = mirror_skills(dotfiles)

    link = dotfiles / "dot-claude" / "skills" / "zoom-out"
    assert mirrored == ["zoom-out"]
    assert link.resolve() == (dotfiles / ".agents" / "skills" / "zoom-out").resolve()


def test_mirror_skills_reports_nothing_on_a_second_run(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path, "zoom-out")
    mirror_skills(dotfiles)

    assert mirror_skills(dotfiles) == []


def test_mirror_skills_drops_a_link_whose_skill_was_removed(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path, "zoom-out")
    mirror_skills(dotfiles)
    (dotfiles / ".agents" / "skills" / "zoom-out").rmdir()

    mirror_skills(dotfiles)

    assert not (dotfiles / "dot-claude" / "skills" / "zoom-out").is_symlink()


def test_mirror_skills_refuses_to_shadow_an_authored_skill(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path, "commit")
    (dotfiles / "dot-claude" / "skills" / "commit").mkdir()

    with pytest.raises(SyncError, match="commit"):
        mirror_skills(dotfiles)


# --- stale links -----------------------------------------------------------


def test_stale_links_finds_a_link_whose_target_is_gone(tmp_path: Path) -> None:
    dotfiles = tmp_path / "dotfiles"
    home = a_home(tmp_path)
    broken = home / ".claude" / "renamed-away"
    broken.symlink_to(dotfiles / "dot-claude" / "gone")

    assert stale_links(home, dotfiles) == [broken]


def test_stale_links_finds_a_live_link_into_the_repo(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    real = dotfiles / "dot-claude" / "CLAUDE.md"
    real.write_text("rules")
    link = home / ".claude" / "CLAUDE.md"
    link.symlink_to(real)

    assert stale_links(home, dotfiles) == [link]


def test_stale_links_leaves_a_hand_made_link_alone(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    elsewhere = tmp_path / "somewhere-else"
    elsewhere.write_text("mine")
    (home / ".claude" / "notes").symlink_to(elsewhere)

    assert stale_links(home, dotfiles) == []


def test_stale_links_leaves_unmanaged_content_alone(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    (home / ".claude" / "projects").mkdir()
    (home / ".claude" / "projects" / "session.jsonl").write_text("{}")

    assert stale_links(home, dotfiles) == []


# --- bashrc loader ---------------------------------------------------------


def test_loader_is_appended_when_bashrc_does_not_source_the_directory(
    tmp_path: Path,
) -> None:
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text("export EDITOR=vim\n")

    assert ensure_bashrc_loader(bashrc) is True
    assert LOADER_MARKER in bashrc.read_text()


def test_loader_is_not_appended_twice(tmp_path: Path) -> None:
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text("export EDITOR=vim\n")
    ensure_bashrc_loader(bashrc)

    assert ensure_bashrc_loader(bashrc) is False
    assert bashrc.read_text().count(LOADER_MARKER) == 1


def test_a_hand_rolled_loader_is_left_alone(tmp_path: Path) -> None:
    bashrc = tmp_path / ".bashrc"
    bashrc.write_text('for f in ~/.bashrc.d/*; do . "$f"; done\n')

    assert ensure_bashrc_loader(bashrc) is False
    assert LOADER_MARKER not in bashrc.read_text()


def test_no_bashrc_means_nothing_to_wire_up(tmp_path: Path) -> None:
    assert ensure_bashrc_loader(tmp_path / "absent") is False
