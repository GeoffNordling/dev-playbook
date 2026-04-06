"""Tests for sdd_trace.report."""

from sdd_trace.models import FunctionalReq
from sdd_trace.report import format_area_counts, print_compact, print_detail


def _req(
    obligation: str = "SHALL", source: str = "specs/requirements.md"
) -> FunctionalReq:
    return FunctionalReq(
        sources=[source],
        obligation=obligation,
        all_obligations=frozenset({obligation}) if obligation else frozenset(),
    )


class TestFormatAreaCounts:
    def test_basic(self) -> None:
        func_reqs = {
            "REQ-ERR-001": _req(),
            "REQ-ERR-002": _req(),
            "REQ-AQD-001": _req(),
        }
        result = format_area_counts(func_reqs)
        assert result == "Areas: AQD:1  ERR:2"

    def test_empty(self) -> None:
        result = format_area_counts({})
        assert result == "Areas: "


class TestPrintCompact:
    # --- No design doc (fallback: mandatory must be tested directly) ---

    def test_all_mandatory_tested_no_design(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        exit_code = print_compact(func_reqs, markers)
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.startswith("PASS")
        assert "1/1 tested" in output

    def test_untested_mandatory_no_design(self, capsys) -> None:
        """No design doc: untested mandatory → FAIL via fallback."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("SHALL"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        exit_code = print_compact(func_reqs, markers)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert output.startswith("FAIL")
        assert "1 in design but untested" in output
        assert "REQ-AUT-002" in output

    def test_non_mandatory_not_tracked_no_design(self, capsys) -> None:
        """Non-mandatory reqs are counted, not tracked."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("MAY"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        exit_code = print_compact(func_reqs, markers)
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.startswith("PASS")
        assert "1 non-mandatory (not tracked)" in output

    # --- With design doc (pipeline: mandatory→design→tests) ---

    def test_mandatory_missing_from_design(self, capsys) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("SHALL"),
        }
        markers = {
            "REQ-AUT-001": ["tests/test_auth.py"],
            "REQ-AUT-002": ["tests/test_auth.py"],
        }
        design = {"REQ-AUT-001": ["specs/design.md"]}
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "1 mandatory missing from design" in output
        assert "REQ-AUT-002" in output

    def test_in_design_but_untested(self, capsys) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("SHALL"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        design = {
            "REQ-AUT-001": ["specs/design.md"],
            "REQ-AUT-002": ["specs/design.md"],
        }
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "1 in design but untested" in output
        assert "REQ-AUT-002" in output

    def test_non_mandatory_missing_from_design_ok(self, capsys) -> None:
        """Non-mandatory not in design is NOT a failure."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("MAY"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        design = {"REQ-AUT-001": ["specs/design.md"]}
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.startswith("PASS")
        assert "missing from design" not in output

    def test_full_pipeline_pass(self, capsys) -> None:
        """All mandatory in design, all design tested → PASS."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("SHALL"),
            "REQ-AUT-003": _req("MAY"),
        }
        markers = {
            "REQ-AUT-001": ["tests/test_auth.py"],
            "REQ-AUT-002": ["tests/test_auth.py"],
        }
        design = {
            "REQ-AUT-001": ["specs/design.md"],
            "REQ-AUT-002": ["specs/design.md"],
        }
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.startswith("PASS")
        assert "1 non-mandatory (not tracked)" in output

    # --- Orphans ---

    def test_orphaned_marker(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {
            "REQ-AUT-001": ["tests/test_auth.py"],
            "REQ-GHO-999": ["tests/test_ghost.py"],
        }
        exit_code = print_compact(func_reqs, markers)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "1 orphaned markers" in output
        assert "REQ-GHO-999" in output

    def test_design_orphan(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        design = {
            "REQ-AUT-001": ["specs/design.md"],
            "REQ-GHO-001": ["specs/design.md"],
        }
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert "1 orphaned design refs" in output
        assert "REQ-GHO-001" in output

    # --- Edge cases ---

    def test_empty(self, capsys) -> None:
        exit_code = print_compact({}, {})
        assert exit_code == 0
        output = capsys.readouterr().out
        assert output.startswith("PASS")
        assert "0 mandatory" in output

    def test_without_design_no_design_in_output(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        exit_code = print_compact(func_reqs, markers, None)
        assert exit_code == 0
        output = capsys.readouterr().out
        assert "missing from design" not in output

    def test_area_counts_line(self, capsys) -> None:
        func_reqs = {
            "REQ-ERR-001": _req(),
            "REQ-ERR-002": _req(),
            "REQ-AQD-001": _req(),
        }
        print_compact(func_reqs, {})
        output = capsys.readouterr().out
        assert "Areas: AQD:1  ERR:2" in output

    def test_fail_lists_all_gap_types(self, capsys) -> None:
        """All gap types present at once."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("SHALL"),
            "REQ-AUT-003": _req("MAY"),
        }
        markers = {
            "REQ-AUT-001": ["tests/test_auth.py"],
            "REQ-GHO-999": ["tests/test_ghost.py"],
        }
        design = {"REQ-AUT-001": ["specs/design.md"]}
        exit_code = print_compact(func_reqs, markers, design)
        assert exit_code == 1
        output = capsys.readouterr().out
        assert output.startswith("FAIL")
        assert "1 mandatory missing from design" in output
        assert "1 orphaned markers" in output
        assert "1 non-mandatory (not tracked)" in output
        assert "Mandatory missing from design (1):" in output
        assert "REQ-AUT-002" in output
        assert "Orphaned test markers (1):" in output
        assert "REQ-GHO-999" in output


class TestPrintDetail:
    def test_single_area(self, capsys) -> None:
        func_reqs = {
            "REQ-AUT-001": _req(),
            "REQ-ERR-001": _req(),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        print_detail(func_reqs, markers, areas=["AUT"])
        output = capsys.readouterr().out
        assert "AUT (1 requirements" in output
        assert "REQ-AUT-001" in output
        assert "REQ-ERR-001" not in output

    def test_multiple_areas(self, capsys) -> None:
        func_reqs = {
            "REQ-AUT-001": _req(),
            "REQ-ERR-001": _req(),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        print_detail(func_reqs, markers, areas=["AUT", "ERR"])
        output = capsys.readouterr().out
        assert "AUT (1 requirements" in output
        assert "ERR (1 requirements" in output

    def test_nonexistent_area_skipped(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        print_detail(func_reqs, {}, areas=["ZZZ"])
        output = capsys.readouterr().out
        assert output == ""

    def test_matrix_columns_without_design(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        print_detail(func_reqs, markers, areas=["AUT"])
        output = capsys.readouterr().out
        assert "In Spec" in output
        assert "Obligation" in output
        assert "In Design" not in output
        assert "test_auth.py" in output

    def test_matrix_columns_with_design(self, capsys) -> None:
        func_reqs = {"REQ-AUT-001": _req()}
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        design = {"REQ-AUT-001": ["specs/design.md"]}
        print_detail(func_reqs, markers, design, areas=["AUT"])
        output = capsys.readouterr().out
        assert "In Design" in output

    def test_orphan_in_area(self, capsys) -> None:
        """Orphaned test markers appear in detail for their area."""
        func_reqs = {"REQ-ERR-001": _req()}
        markers = {
            "REQ-ERR-001": ["tests/test_err.py"],
            "REQ-ERR-099": ["tests/test_ghost.py"],
        }
        print_detail(func_reqs, markers, areas=["ERR"])
        output = capsys.readouterr().out
        assert "REQ-ERR-099" in output
        assert "N/A" in output  # Obligation column for orphan

    def test_obligation_shown_in_detail(self, capsys) -> None:
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("MAY"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        print_detail(func_reqs, markers, areas=["AUT"])
        output = capsys.readouterr().out
        assert "SHALL" in output
        assert "MAY" in output

    def test_non_mandatory_shows_dash(self, capsys) -> None:
        """Non-mandatory rows show '-' for design/tested columns."""
        func_reqs = {
            "REQ-AUT-001": _req("SHALL"),
            "REQ-AUT-002": _req("MAY"),
        }
        markers = {"REQ-AUT-001": ["tests/test_auth.py"]}
        design = {"REQ-AUT-001": ["specs/design.md"]}
        print_detail(func_reqs, markers, design, areas=["AUT"])
        output = capsys.readouterr().out
        lines = output.strip().split("\n")
        # Find the MAY row
        may_line = [line for line in lines if "REQ-AUT-002" in line][0]
        # Should have dashes for design/tested/test-files columns
        parts = may_line.split()
        assert "-" in parts
