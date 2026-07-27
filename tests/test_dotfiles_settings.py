"""Behavioral tests for the per-machine settings merge and install."""

import json
from pathlib import Path

import pytest

from dev_playbook.dotfiles.settings import (
    install,
    is_current,
    merge,
    render,
    settings_for,
)


def write_json(path: Path, payload: dict) -> Path:
    """Write payload as JSON to path and return the path."""
    path.write_text(json.dumps(payload))
    return path


def a_source_dir(tmp_path: Path, base: dict, **fragments: dict) -> Path:
    """A settings directory holding the given base and named fragments."""
    source = tmp_path / "settings"
    source.mkdir()
    write_json(source / "base.json", base)
    for machine, fragment in fragments.items():
        write_json(source / f"{machine}.json", fragment)
    return source


# --- merge -----------------------------------------------------------------


def test_merge_adds_keys_the_base_does_not_have() -> None:
    result = merge({"model": "opus"}, {"theme": "light"})

    assert result == {"model": "opus", "theme": "light"}


def test_merge_replaces_a_scalar_the_base_already_set() -> None:
    result = merge({"effortLevel": "medium"}, {"effortLevel": "xhigh"})

    assert result["effortLevel"] == "xhigh"


def test_merge_combines_nested_objects_key_by_key() -> None:
    base = {"hooks": {"SessionStart": ["a"]}}
    fragment = {"hooks": {"Stop": ["b"]}}

    result = merge(base, fragment)

    assert result["hooks"] == {"SessionStart": ["a"], "Stop": ["b"]}


def test_merge_concatenates_arrays_from_both_layers() -> None:
    base = {"allow": ["Bash(git *)"]}
    fragment = {"allow": ["Bash(make *)"]}

    result = merge(base, fragment)

    assert result["allow"] == ["Bash(git *)", "Bash(make *)"]


def test_merge_drops_an_array_entry_present_in_both_layers() -> None:
    base = {"allow": ["Bash(git *)", "Bash(make *)"]}
    fragment = {"allow": ["Bash(make *)"]}

    result = merge(base, fragment)

    assert result["allow"] == ["Bash(git *)", "Bash(make *)"]


def test_merge_dedupes_array_entries_that_are_objects() -> None:
    hook = {"matcher": "", "hooks": [{"type": "command", "command": "beep"}]}
    base = {"Stop": [hook]}
    fragment = {"Stop": [dict(hook)]}

    result = merge(base, fragment)

    assert result["Stop"] == [hook]


def test_merge_lets_the_fragment_win_when_the_types_disagree() -> None:
    result = merge({"sandbox": {"enabled": True}}, {"sandbox": False})

    assert result["sandbox"] is False


def test_merge_leaves_the_base_untouched() -> None:
    base = {"hooks": {"SessionStart": ["a"]}}

    merge(base, {"hooks": {"Stop": ["b"]}})

    assert base == {"hooks": {"SessionStart": ["a"]}}


# --- settings_for ----------------------------------------------------------


def test_settings_for_layers_the_named_fragment_over_the_base(tmp_path: Path) -> None:
    source = a_source_dir(
        tmp_path,
        {"model": "opus", "effortLevel": "medium"},
        wsl={"effortLevel": "xhigh"},
    )

    result = settings_for(source, "wsl")

    assert result == {"model": "opus", "effortLevel": "xhigh"}


def test_settings_for_ignores_fragments_for_other_machines(tmp_path: Path) -> None:
    source = a_source_dir(
        tmp_path, {"model": "opus"}, wsl={}, fedora={"sandbox": {"enabled": True}}
    )

    result = settings_for(source, "wsl")

    assert "sandbox" not in result


def test_settings_for_raises_when_the_fragment_is_missing(tmp_path: Path) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"})

    with pytest.raises(FileNotFoundError):
        settings_for(source, "wsl")


# --- render ----------------------------------------------------------------


def test_render_round_trips_through_json() -> None:
    settings = {"model": "opus", "permissions": {"allow": ["Bash(git *)"]}}

    assert json.loads(render(settings)) == settings


def test_render_ends_with_a_single_newline() -> None:
    assert render({"model": "opus"}).endswith("}\n")


# --- install / is_current --------------------------------------------------


def test_install_writes_the_merged_settings(tmp_path: Path) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"}, wsl={"effortLevel": "xhigh"})
    target = tmp_path / "home" / ".claude" / "settings.json"

    assert install(source, "wsl", target) is True
    assert json.loads(target.read_text()) == {"model": "opus", "effortLevel": "xhigh"}


def test_install_reports_no_change_when_already_current(tmp_path: Path) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"}, wsl={})
    target = tmp_path / "settings.json"
    install(source, "wsl", target)

    assert install(source, "wsl", target) is False


def test_install_replaces_a_symlink_rather_than_writing_through_it(
    tmp_path: Path,
) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"}, wsl={})
    checked_in = write_json(tmp_path / "checked-in.json", {"model": "ancient"})
    target = tmp_path / "settings.json"
    target.symlink_to(checked_in)

    install(source, "wsl", target)

    assert not target.is_symlink()
    assert json.loads(checked_in.read_text()) == {"model": "ancient"}


def test_is_current_reports_a_missing_file_as_out_of_date(tmp_path: Path) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"}, wsl={})

    assert is_current(source, "wsl", tmp_path / "absent.json") is False


def test_is_current_reports_a_hand_edited_file_as_out_of_date(tmp_path: Path) -> None:
    source = a_source_dir(tmp_path, {"model": "opus"}, wsl={})
    target = tmp_path / "settings.json"
    install(source, "wsl", target)
    target.write_text(json.dumps({"model": "meddled-with"}))

    assert is_current(source, "wsl", target) is False
