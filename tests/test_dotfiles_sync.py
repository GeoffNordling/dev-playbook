"""Behavioral tests for the dotfiles install: package targeting, links, loader."""

import subprocess
from pathlib import Path

import pytest

from dev_playbook.dotfiles.sync import (
    LOADER_MARKER,
    PACKAGES,
    SyncError,
    claim_targets,
    ensure_bashrc_loader,
    mirror_skills,
    stale_links,
    stow_packages,
    stray_links,
    sync,
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


def a_repo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A repo complete enough for a whole sync run, on a host reporting `wsl`."""
    repo = tmp_path / "repo"
    dotfiles = a_dotfiles_tree(repo)
    (dotfiles / ".bashrc.d").mkdir()
    (dotfiles / "settings").mkdir()
    (dotfiles / "settings" / "base.json").write_text('{"model": "opus"}')
    (dotfiles / "settings" / "wsl.json").write_text("{}")
    monkeypatch.setattr("dev_playbook.dotfiles.sync.detect_machine", lambda: "wsl")
    monkeypatch.setattr("dev_playbook.dotfiles.sync.missing_tools", lambda: [])
    return repo


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


# --- claiming the targets --------------------------------------------------
#
# Stow refuses to stow a package over itself, so a target that is a symlink to
# the package must become a real directory before stow sees it.


def test_a_target_that_does_not_exist_is_created(tmp_path: Path) -> None:
    home = tmp_path / "home"

    claim_targets(home, tmp_path / "dotfiles")

    assert (home / ".bashrc.d").is_dir()


def test_a_target_linked_to_its_own_package_becomes_a_real_directory(
    tmp_path: Path,
) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    (home / ".agents").symlink_to(dotfiles / ".agents")

    replaced = claim_targets(home, dotfiles)

    assert replaced == [home / ".agents"]
    assert (home / ".agents").is_dir() and not (home / ".agents").is_symlink()


def test_a_target_linked_outside_the_repo_is_refused(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (home / ".agents").symlink_to(elsewhere)

    with pytest.raises(SyncError, match="does not manage"):
        claim_targets(home, dotfiles)


def test_a_target_occupied_by_a_file_is_refused(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    (home / ".agents").write_text("not a directory")

    with pytest.raises(SyncError, match="needs a directory"):
        claim_targets(home, tmp_path / "dotfiles")


# --- stray links in $HOME --------------------------------------------------


def test_a_link_loose_in_home_pointing_into_the_repo_is_a_stray(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    (dotfiles / ".bashrc.d").mkdir()
    (dotfiles / ".bashrc.d" / "aliases.sh").write_text("alias x=y")
    stray = home / "aliases.sh"
    stray.symlink_to(dotfiles / ".bashrc.d" / "aliases.sh")

    assert stray_links(home, dotfiles) == [stray]


def test_a_link_to_a_retired_package_is_a_stray(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    stray = home / "bin"
    stray.symlink_to(dotfiles / "bin")

    assert stray_links(home, dotfiles) == [stray]


def test_a_link_in_home_pointing_elsewhere_is_left_alone(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    elsewhere = tmp_path / "notes.txt"
    elsewhere.write_text("mine")
    (home / "notes.txt").symlink_to(elsewhere)

    assert stray_links(home, dotfiles) == []


def test_a_package_target_is_never_a_stray(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = tmp_path / "home"
    home.mkdir()
    (home / ".agents").symlink_to(dotfiles / ".agents")

    assert stray_links(home, dotfiles) == []


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


def test_stale_links_leaves_a_live_link_for_stow_to_keep_current(
    tmp_path: Path,
) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    real = dotfiles / "dot-claude" / "CLAUDE.md"
    real.write_text("rules")
    (home / ".claude" / "CLAUDE.md").symlink_to(real)

    assert stale_links(home, dotfiles) == []


def test_stale_links_leaves_someone_elses_broken_link_alone(tmp_path: Path) -> None:
    dotfiles = a_dotfiles_tree(tmp_path)
    home = a_home(tmp_path)
    (home / ".claude" / "notes").symlink_to(tmp_path / "never-existed")

    assert stale_links(home, dotfiles) == []


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


# --- the whole run ---------------------------------------------------------


def test_a_stow_that_aborts_still_leaves_the_settings_file_installed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = a_repo(tmp_path, monkeypatch)
    home = tmp_path / "home"

    def fail(argv: list[str], **kwargs: object) -> None:
        raise subprocess.CalledProcessError(1, argv)

    monkeypatch.setattr(subprocess, "run", fail)

    with pytest.raises(subprocess.CalledProcessError):
        sync(repo, home)

    assert (home / ".claude" / "settings.json").is_file()


def test_a_run_that_changes_nothing_reports_nothing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = a_repo(tmp_path, monkeypatch)
    home = tmp_path / "home"
    monkeypatch.setattr(subprocess, "run", lambda argv, **kwargs: None)
    sync(repo, home)

    assert sync(repo, home) == []
