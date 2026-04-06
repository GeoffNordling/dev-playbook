"""Tests for sdd_trace.parser — data extraction functions."""

from pathlib import Path

from sdd_trace.models import find_md_files
from sdd_trace.parser import (
    parse_design_refs,
    parse_functional_reqs,
    parse_test_markers,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


# ---------------------------------------------------------------------------
# parse_functional_reqs
# ---------------------------------------------------------------------------


class TestParseFunctionalReqs:
    def test_single_shall(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert "REQ-AUT-001" in result
        assert result["REQ-AUT-001"].obligation == "SHALL"

    def test_shall_not(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-ERR-001**: The system `SHALL NOT` silently drop errors.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-ERR-001"].obligation == "SHALL NOT"

    def test_should(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-UIX-001**: The system `SHOULD` highlight errors in red.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-UIX-001"].obligation == "SHOULD"

    def test_should_not(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-UIX-002**: The system `SHOULD NOT` use popups.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-UIX-002"].obligation == "SHOULD NOT"

    def test_may(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-OPT-001**: The system `MAY` display a tooltip.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-OPT-001"].obligation == "MAY"

    def test_multiple_definitions(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n\n"
            "- **REQ-AUT-002**: The system `MAY` remember the user.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-AUT-001"].obligation == "SHALL"
        assert result["REQ-AUT-002"].obligation == "MAY"

    def test_multiline_text_block(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n"
            "  This includes OAuth and password-based auth.\n\n"
            "- **REQ-AUT-002**: The system `SHALL` handle logout.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert len(result) == 2
        assert result["REQ-AUT-001"].obligation == "SHALL"

    def test_block_terminated_by_heading(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "## Auth\n\n"
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n\n"
            "## Errors\n\n"
            "- **REQ-ERR-001**: The system `SHALL` raise on bad input.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert len(result) == 2

    def test_block_terminated_by_hrule(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n\n"
            "---\n\n"
            "- **REQ-ERR-001**: The system `SHALL` raise on bad input.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert len(result) == 2

    def test_bare_reference_ignored(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n\n"
            "This relates to REQ-ERR-004.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert "REQ-AUT-001" in result
        assert "REQ-ERR-004" not in result

    def test_repeated_same_keyword(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` extract content.\n"
            "  Unrecognized content `SHALL` be dropped.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-AUT-001"].obligation == "SHALL"

    def test_split_files(self, tmp_path: Path) -> None:
        reqs = tmp_path / "specs" / "functional_requirements"
        _write(reqs / "index.md", "| File | Scope |\n|---|---|\n| auth.md | Auth |\n")
        _write(
            reqs / "auth.md",
            "- **REQ-AUT-001**: The system `SHALL` handle login.\n",
        )
        _write(
            reqs / "export.md",
            "- **REQ-EXP-001**: The system `MAY` export CSV.\n",
        )
        files = find_md_files(tmp_path / "specs", "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-AUT-001"].obligation == "SHALL"
        assert result["REQ-EXP-001"].obligation == "MAY"

    def test_accepts_four_letter_area(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-ABCD-001**: The system `SHALL` do something.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert "REQ-ABCD-001" in result

    def test_accepts_six_letter_area(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-ABCDEF-001**: The system `SHALL` do something.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert "REQ-ABCDEF-001" in result

    def test_all_obligations_populated(self, tmp_path: Path) -> None:
        """parse_functional_reqs populates all_obligations with every keyword found."""
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` extract content.\n"
            "  Unrecognized content `SHALL` be dropped.\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-AUT-001"].all_obligations == frozenset({"SHALL"})

    def test_all_obligations_mixed(self, tmp_path: Path) -> None:
        """Mixed keywords are captured in all_obligations; obligation is empty."""
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- **REQ-AUT-001**: The system `SHALL` extract content.\n"
            "  The system `MAY` log dropped content.\n\n"
            "## Next Section\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_functional_reqs(files)
        assert result["REQ-AUT-001"].all_obligations == frozenset({"SHALL", "MAY"})
        assert result["REQ-AUT-001"].obligation == ""


# ---------------------------------------------------------------------------
# parse_design_refs
# ---------------------------------------------------------------------------


class TestParseDesignRefs:
    def test_single_file(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- REQ-AUT-001: Login\n- REQ-AUT-002: Logout\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert set(result.keys()) == {"REQ-AUT-001", "REQ-AUT-002"}

    def test_split_requirements(self, tmp_path: Path) -> None:
        reqs = tmp_path / "specs" / "functional_requirements"
        _write(reqs / "index.md", "| File | Scope |\n|---|---|\n| auth.md | Auth |\n")
        _write(reqs / "auth.md", "- REQ-AUT-001: Login\n")
        _write(reqs / "export.md", "- REQ-EXP-001: CSV export\n")
        files = find_md_files(tmp_path / "specs", "functional_requirements")
        result = parse_design_refs(files)
        assert set(result.keys()) == {"REQ-AUT-001", "REQ-EXP-001"}

    def test_no_requirements_file(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        specs.mkdir()
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert result == {}

    def test_no_ids_in_file(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(specs / "functional_requirements.md", "# Requirements\n\nNo IDs here.\n")
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert result == {}

    def test_duplicate_ids_across_sections(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "## Auth\n- REQ-AUT-001: Login\n\n## Also Auth\n- REQ-AUT-001: Again\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert "REQ-AUT-001" in result

    def test_single_file_preferred_over_split(self, tmp_path: Path) -> None:
        """When both functional_requirements.md and functional_requirements/ exist, split takes precedence."""
        specs = tmp_path / "specs"
        _write(specs / "functional_requirements.md", "- REQ-FLT-001: Flat\n")
        reqs = specs / "functional_requirements"
        _write(reqs / "index.md", "| File | Scope |\n")
        _write(reqs / "nested.md", "- REQ-NST-001: Nested\n")
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        # Split dir takes precedence when index.md exists
        assert "REQ-NST-001" in result
        assert "REQ-FLT-001" not in result

    def test_accepts_four_letter_area(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- REQ-ABCD-001: Good ID\n- REQ-ERR-001: Good ID\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert "REQ-ERR-001" in result
        assert "REQ-ABCD-001" in result

    def test_accepts_six_letter_area(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- REQ-ABCDEF-001: Good ID\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert "REQ-ABCDEF-001" in result

    def test_rejects_seven_letter_area(self, tmp_path: Path) -> None:
        specs = tmp_path / "specs"
        _write(
            specs / "functional_requirements.md",
            "- REQ-ABCDEFG-001: Bad ID\n- REQ-ERR-001: Good ID\n",
        )
        files = find_md_files(specs, "functional_requirements")
        result = parse_design_refs(files)
        assert "REQ-ERR-001" in result
        assert "REQ-ABCDEFG-001" not in result


# ---------------------------------------------------------------------------
# parse_test_markers
# ---------------------------------------------------------------------------


class TestParseTestMarkers:
    def test_single_marker(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n',
        )
        result = parse_test_markers(tmp_path)
        assert "REQ-AUT-001" in result

    def test_single_quotes(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "test_auth.py",
            "@pytest.mark.req('REQ-AUT-001')\ndef test_login(): pass\n",
        )
        result = parse_test_markers(tmp_path)
        assert "REQ-AUT-001" in result

    def test_multi_marker_list(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "test_integration.py",
            '@pytest.mark.req(["REQ-AUT-001", "REQ-EXP-001"])\ndef test_flow(): pass\n',
        )
        result = parse_test_markers(tmp_path)
        assert "REQ-AUT-001" in result
        assert "REQ-EXP-001" in result

    def test_multi_marker_multiline(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "test_integration.py",
            '@pytest.mark.req([\n    "REQ-AUT-001",\n    "REQ-EXP-001",\n])\n'
            "def test_flow(): pass\n",
        )
        result = parse_test_markers(tmp_path)
        assert "REQ-AUT-001" in result
        assert "REQ-EXP-001" in result

    def test_no_markers(self, tmp_path: Path) -> None:
        _write(tmp_path / "test_plain.py", "def test_something(): pass\n")
        result = parse_test_markers(tmp_path)
        assert result == {}

    def test_nested_test_files(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "sub" / "test_deep.py",
            '@pytest.mark.req("REQ-DEP-001")\ndef test_deep(): pass\n',
        )
        result = parse_test_markers(tmp_path)
        assert "REQ-DEP-001" in result

    def test_multiple_markers_same_file(self, tmp_path: Path) -> None:
        _write(
            tmp_path / "test_auth.py",
            '@pytest.mark.req("REQ-AUT-001")\ndef test_login(): pass\n\n'
            '@pytest.mark.req("REQ-AUT-002")\ndef test_logout(): pass\n',
        )
        result = parse_test_markers(tmp_path)
        assert set(result.keys()) == {"REQ-AUT-001", "REQ-AUT-002"}
