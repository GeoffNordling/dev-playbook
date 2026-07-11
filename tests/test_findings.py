"""Unit tests for the shared GNU-format finding rendering."""

import pytest

from dev_playbook import findings


def test_render_with_line_includes_the_location_line() -> None:
    line = findings.render("src/mod.py", "python.empty-init", "must be empty", line=12)

    assert line == "src/mod.py:12: python.empty-init must be empty"


def test_render_without_line_drops_the_line_segment() -> None:
    line = findings.render("README.md", "docs.doc-shape", "missing an H1 title")

    assert line == "README.md: docs.doc-shape missing an H1 title"


def test_print_rules_prints_sorted_unique_ids_and_returns_zero(
    capsys: pytest.CaptureFixture[str],
) -> None:
    code = findings.print_rules(["b.two", "a.one", "b.two"])

    assert code == 0
    assert capsys.readouterr().out == "a.one\nb.two\n"
