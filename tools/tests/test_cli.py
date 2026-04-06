"""Tests for sdd_trace.cli — integration through the CLI entry point."""

from pathlib import Path

import pytest

from sdd_trace.cli import main


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def _setup_project(root: Path) -> None:
    """Create a minimal project with specs and tests."""
    _write(
        root / "specs" / "functional_requirements.md",
        "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
        "- **REQ-AUT-002**: The system `SHALL` handle logout.\n",
    )
    _write(
        root / "tests" / "test_auth.py",
        '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n\n'
        '@pytest.mark.req("REQ-AUT-002")\ndef test_logout(): pass\n',
    )


class TestCliExitCodes:
    def test_exit_0_when_fully_covered(self, tmp_path: Path, monkeypatch) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_exit_1_when_untested_mandatory(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "- **REQ-AUT-002**: The system `SHALL` handle logout.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_0_when_only_non_mandatory_untested(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "- **REQ-AUT-002**: The system `SHOULD` remember the user.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_exit_1_when_orphaned(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n\n'
            '@pytest.mark.req("REQ-GHO-999")\ndef test_ghost(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_2_when_no_specs(self, tmp_path: Path, monkeypatch) -> None:
        (tmp_path / "tests").mkdir()
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_no_spec_structure(self, tmp_path: Path, monkeypatch) -> None:
        """specs/ exists but has no functional_requirements.md or functional_requirements/."""
        (tmp_path / "specs").mkdir()
        (tmp_path / "tests").mkdir()
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_zero_definitions(self, tmp_path: Path, monkeypatch) -> None:
        """Spec file exists but contains no definition sites."""
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "# Requirements\n\nNo definition sites here.\n",
        )
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_no_tests(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_missing_obligation(self, tmp_path: Path, monkeypatch) -> None:
        """Definition site with no backtick-wrapped obligation keyword."""
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system shall handle login.\n",
        )
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_mixed_obligations(self, tmp_path: Path, monkeypatch) -> None:
        """Definition site with mixed obligation levels."""
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` extract content.\n"
            "  The system `MAY` log dropped content.\n\n"
            "## Next\n",
        )
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()


class TestCliFlags:
    def test_specs_override(self, tmp_path: Path, monkeypatch) -> None:
        custom = tmp_path / "custom_specs"
        _write(
            custom / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--specs", str(custom)])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_tests_override(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        custom = tmp_path / "custom_tests"
        _write(
            custom / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--tests", str(custom)])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_compact_default(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        assert "PASS" in output
        assert "Areas:" in output
        # Matrix header should NOT appear without --detail
        assert "In Spec" not in output

    def test_detail_shows_matrix(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--detail", "AUT"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        assert "In Spec" in output
        assert "Obligation" in output
        assert "REQ-AUT-001" in output
        assert "AUT (2 requirements" in output

    def test_detail_no_args_is_compact(
        self, tmp_path: Path, monkeypatch, capsys
    ) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--detail"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        assert "PASS" in output
        assert "In Spec" not in output

    def test_detail_multiple_areas(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "- **REQ-ERR-001**: The system `SHALL` raise on error.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n'
            '@pytest.mark.req("REQ-ERR-001")\ndef test_err(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--detail", "AUT", "ERR"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        assert "AUT (1 requirements" in output
        assert "ERR (1 requirements" in output

    def test_detail_nonexistent_area(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--detail", "ZZZ"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        # Compact section still present
        assert "PASS" in output
        # No matrix rows for nonexistent area
        assert "ZZZ" not in output

    def test_detail_case_insensitive(self, tmp_path: Path, monkeypatch, capsys) -> None:
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace", "--detail", "aut"])
        with pytest.raises(SystemExit, match="0"):
            main()
        output = capsys.readouterr().out
        assert "AUT (2 requirements" in output


class TestMalformedIds:
    def test_exit_2_when_seven_letter_area(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-ABCDEFG-001**: Bad area.\n",
        )
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_no_prefix(self, tmp_path: Path, monkeypatch) -> None:
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- ERR-001: Bad\n",
        )
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()

    def test_exit_2_when_malformed_in_design(self, tmp_path: Path, monkeypatch) -> None:
        _setup_project(tmp_path)
        _write(
            tmp_path / "specs" / "design.md",
            "REQ-AUT-001\nREQ-AUT-002\nREQ-TOOLONG-001\n",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="2"):
            main()


class TestDesignCoverage:
    def test_exit_0_when_design_absent(self, tmp_path: Path, monkeypatch) -> None:
        """No design files → design check silently skipped, exit 0 if tests pass."""
        _setup_project(tmp_path)
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_exit_0_when_design_covers_all(self, tmp_path: Path, monkeypatch) -> None:
        _setup_project(tmp_path)
        _write(
            tmp_path / "specs" / "design.md",
            "## Auth\nREQ-AUT-001 and REQ-AUT-002 are covered.\n",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()

    def test_exit_1_when_design_has_gaps(self, tmp_path: Path, monkeypatch) -> None:
        """Design exists but misses a requirement → exit 1."""
        _setup_project(tmp_path)
        _write(
            tmp_path / "specs" / "design.md",
            "## Auth\nOnly REQ-AUT-001 is in the design.\n",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_1_when_design_has_orphan(self, tmp_path: Path, monkeypatch) -> None:
        """Design references a requirement that doesn't exist in specs → exit 1."""
        _setup_project(tmp_path)
        _write(
            tmp_path / "specs" / "design.md",
            "REQ-AUT-001\nREQ-AUT-002\nREQ-GHO-001\n",
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_1_when_tests_pass_but_design_fails(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Tests fully cover requirements, but design has gaps → still exit 1."""
        _setup_project(tmp_path)
        _write(tmp_path / "specs" / "design.md", "Only REQ-AUT-001 here.\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_1_when_in_design_but_untested(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Design covers all mandatory but one has no test → exit 1."""
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "- **REQ-AUT-002**: The system `SHALL` handle logout.\n",
        )
        _write(
            tmp_path / "specs" / "design.md",
            "REQ-AUT-001 and REQ-AUT-002 are covered.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="1"):
            main()

    def test_exit_0_when_non_mandatory_missing_from_design(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """Non-mandatory not in design is fine — only mandatory matters."""
        _write(
            tmp_path / "specs" / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "- **REQ-AUT-002**: The system `SHOULD` remember the user.\n",
        )
        _write(
            tmp_path / "specs" / "design.md",
            "REQ-AUT-001 is designed.\n",
        )
        _write(
            tmp_path / "tests" / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(SystemExit, match="0"):
            main()


class TestSilentFailures:
    def test_raises_when_design_dir_missing_index(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """specs/design/ exists without index.md → must raise, not silently skip."""
        _setup_project(tmp_path)
        design_dir = tmp_path / "specs" / "design"
        design_dir.mkdir()
        _write(design_dir / "auth.md", "REQ-AUT-001\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(FileNotFoundError, match="index.md"):
            main()

    def test_raises_when_func_reqs_dir_missing_index(
        self, tmp_path: Path, monkeypatch
    ) -> None:
        """specs/functional_requirements/ exists without index.md → must raise."""
        reqs_dir = tmp_path / "specs" / "functional_requirements"
        reqs_dir.mkdir(parents=True)
        _write(reqs_dir / "auth.md", "- **REQ-AUT-001**: The system `SHALL` do X.\n")
        (tmp_path / "tests").mkdir()
        _write(tmp_path / "tests" / "test_x.py", "def test_x(): pass\n")
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr("sys.argv", ["sdd-trace"])
        with pytest.raises(FileNotFoundError, match="index.md"):
            main()
