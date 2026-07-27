"""Behavioral tests for machine detection."""

from pathlib import Path

import pytest

from dev_playbook.dotfiles.machine import detect_machine


def point_detection_at(
    monkeypatch: pytest.MonkeyPatch, kernel: str, os_release: str, tmp_path: Path
) -> None:
    """Redirect machine detection at throwaway files holding the given contents."""
    kernel_file = tmp_path / "version"
    kernel_file.write_text(kernel)
    release_file = tmp_path / "os-release"
    release_file.write_text(os_release)
    monkeypatch.setattr("dev_playbook.dotfiles.machine.PROC_VERSION", kernel_file)
    monkeypatch.setattr("dev_playbook.dotfiles.machine.OS_RELEASE", release_file)


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
