"""Tests for sdd_tools.lint_dimensions."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.lint import lint_file


def _by_rule(findings, rule: str):
    return [f for f in findings if f.rule == rule]


_ALL_FOUR_HEADERS = "## Data\n\n## API Shape\n\n## Algorithms\n\n## Composition\n"


class TestNoDsnExempt:
    def test_file_with_only_reqs_is_exempt(self):
        text = (
            "### Req One\n"
            "`req~r.one~1`\n"
            "Status: approved\n"
            "\n"
            "The system `SHALL` do.\n"
            "\n"
            "Needs: dsn\n"
        )
        findings = lint_file(Path("req.md"), text)
        assert _by_rule(findings, "lint.missing-dimension-header") == []
        assert _by_rule(findings, "lint.dsn-outside-dimension") == []


class TestMissingDimensionHeader:
    def test_all_four_headers_no_finding(self):
        text = (
            "## Data\n\n"
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n"
        )
        findings = lint_file(Path("d.md"), text)
        assert _by_rule(findings, "lint.missing-dimension-header") == []

    def test_missing_one_header_flagged(self):
        text = (
            "## Data\n\n"
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            "## API Shape\n\n## Algorithms\n"
        )  # no Composition
        findings = lint_file(Path("d.md"), text)
        missing = _by_rule(findings, "lint.missing-dimension-header")
        assert len(missing) == 1
        assert "Composition" in missing[0].message

    def test_missing_all_headers_flagged(self):
        text = (
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
        )
        findings = lint_file(Path("d.md"), text)
        missing = _by_rule(findings, "lint.missing-dimension-header")
        assert len(missing) == 4


class TestDimensionOrder:
    def test_out_of_order_flagged(self):
        text = (
            "## API Shape\n\n"
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            "## Data\n\n## Algorithms\n\n## Composition\n"
        )  # API Shape before Data
        findings = lint_file(Path("d.md"), text)
        order = _by_rule(findings, "lint.dimension-order")
        assert len(order) == 1


class TestDsnOutsideDimension:
    def test_dsn_in_preamble_flagged(self):
        text = (
            "### Orphan\n"
            "`dsn~orphan~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            + _ALL_FOUR_HEADERS
        )
        findings = lint_file(Path("d.md"), text)
        orphans = _by_rule(findings, "lint.dsn-outside-dimension")
        assert len(orphans) == 1
        assert orphans[0].spec_id == "dsn~orphan~1"

    def test_dsn_in_custom_h2_flagged(self):
        text = (
            "## Other\n\n"
            "### Orphan\n"
            "`dsn~orphan~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            + _ALL_FOUR_HEADERS
        )
        findings = lint_file(Path("d.md"), text)
        orphans = _by_rule(findings, "lint.dsn-outside-dimension")
        assert len(orphans) == 1

    def test_dsn_under_dimension_no_finding(self):
        text = (
            "## Data\n\n"
            "### Foo\n"
            "`dsn~foo~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "\n"
            "## API Shape\n\n## Algorithms\n\n## Composition\n"
        )
        findings = lint_file(Path("d.md"), text)
        assert _by_rule(findings, "lint.dsn-outside-dimension") == []
