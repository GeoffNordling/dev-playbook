"""Behavioral tests for machine detection and the settings merge."""

import json
from pathlib import Path

import pytest

from dev_playbook.machine import (
    detect_machine,
    merge,
    render,
    settings_for,
)


def write_json(path: Path, payload: dict) -> Path:
    """Write payload as JSON to path and return the path."""
    path.write_text(json.dumps(payload))
    return path


def point_detection_at(
    monkeypatch: pytest.MonkeyPatch, kernel: str, os_release: str, tmp_path: Path
) -> None:
    """Redirect machine detection at throwaway files holding the given contents."""
    kernel_file = tmp_path / "version"
    kernel_file.write_text(kernel)
    release_file = tmp_path / "os-release"
    release_file.write_text(os_release)
    monkeypatch.setattr("dev_playbook.machine.PROC_VERSION", kernel_file)
    monkeypatch.setattr("dev_playbook.machine.OS_RELEASE", release_file)


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
    write_json(tmp_path / "base.json", {"model": "opus", "effortLevel": "medium"})
    write_json(tmp_path / "wsl.json", {"effortLevel": "xhigh"})

    result = settings_for(tmp_path, "wsl")

    assert result == {"model": "opus", "effortLevel": "xhigh"}


def test_settings_for_ignores_fragments_for_other_machines(tmp_path: Path) -> None:
    write_json(tmp_path / "base.json", {"model": "opus"})
    write_json(tmp_path / "wsl.json", {})
    write_json(tmp_path / "fedora.json", {"sandbox": {"enabled": True}})

    result = settings_for(tmp_path, "wsl")

    assert "sandbox" not in result


def test_settings_for_raises_when_the_fragment_is_missing(tmp_path: Path) -> None:
    write_json(tmp_path / "base.json", {"model": "opus"})

    with pytest.raises(FileNotFoundError):
        settings_for(tmp_path, "wsl")


# --- render ----------------------------------------------------------------


def test_render_round_trips_through_json() -> None:
    settings = {"model": "opus", "permissions": {"allow": ["Bash(git *)"]}}

    assert json.loads(render(settings)) == settings


def test_render_ends_with_a_single_newline() -> None:
    assert render({"model": "opus"}).endswith("}\n")


# --- detect_machine --------------------------------------------------------


def test_detect_machine_reads_wsl_from_the_kernel_version(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    point_detection_at(
        monkeypatch,
        kernel="Linux version 6.6.87.2-microsoft-standard-WSL2",
        os_release='ID=ubuntu\nNAME="Ubuntu"\n',
        tmp_path=tmp_path,
    )

    assert detect_machine() == "wsl"


def test_detect_machine_reads_fedora_from_os_release(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    point_detection_at(
        monkeypatch,
        kernel="Linux version 6.14.0-63.fc42.x86_64",
        os_release='ID=fedora\nNAME="Fedora Linux"\n',
        tmp_path=tmp_path,
    )

    assert detect_machine() == "fedora"


def test_detect_machine_rejects_a_distro_with_no_fragment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    point_detection_at(
        monkeypatch,
        kernel="Linux version 6.14.0-generic",
        os_release='ID=arch\nNAME="Arch Linux"\n',
        tmp_path=tmp_path,
    )

    with pytest.raises(ValueError, match="arch"):
        detect_machine()
