"""Tests for pytest_sdd.markers — pytest marker to OFT coverage bridge."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pytest_sdd.markers import (
    collect_covered_ids,
    create_coverage_dir,
    generate_coverage_markdown,
    write_coverage_file,
)
from pytest_sdd.parser import parse_spec_file


def _make_item(nodeid: str, markers: list[tuple[str, list[str]]]) -> MagicMock:
    """Create a mock pytest.Item with the given markers."""
    item = MagicMock(spec=pytest.Item)
    item.nodeid = nodeid
    mock_markers = []
    for name, args in markers:
        m = MagicMock()
        m.name = name
        m.args = args
        mock_markers.append(m)
    item.iter_markers = MagicMock(return_value=mock_markers)
    return item


class TestCollectCoveredIds:
    def test_single_req_marker(self):
        item = _make_item("test_foo.py::test_check", [("req", ["req~auth.login~1"])])
        result = collect_covered_ids([item])
        assert "req~auth.login~1" in result
        assert "test_foo.py::test_check" in result["req~auth.login~1"]

    def test_dsn_marker(self):
        item = _make_item("test_foo.py::test_design", [("dsn", ["dsn~auth.login~1"])])
        result = collect_covered_ids([item])
        assert "dsn~auth.login~1" in result

    def test_multiple_markers_on_one_test(self):
        item = _make_item(
            "test_foo.py::test_multi",
            [("req", ["req~a.one~1"]), ("req", ["req~a.two~1"])],
        )
        result = collect_covered_ids([item])
        assert "req~a.one~1" in result
        assert "req~a.two~1" in result

    def test_multiple_tests_same_id(self):
        item1 = _make_item("test_a.py::test_1", [("req", ["req~auth.login~1"])])
        item2 = _make_item("test_b.py::test_2", [("req", ["req~auth.login~1"])])
        result = collect_covered_ids([item1, item2])
        assert len(result["req~auth.login~1"]) == 2

    def test_non_oft_markers_ignored(self):
        item = _make_item(
            "test_foo.py::test_check",
            [("parametrize", ["x", [1, 2]]), ("slow", [])],
        )
        result = collect_covered_ids([item])
        assert result == {}

    def test_invalid_id_format_ignored(self):
        item = _make_item(
            "test_foo.py::test_check",
            [("req", ["not-a-valid-id"])],
        )
        result = collect_covered_ids([item])
        assert result == {}

    def test_empty_items_list(self):
        assert collect_covered_ids([]) == {}


class TestGenerateCoverageMarkdown:
    def test_empty_dict_returns_empty_string(self):
        assert generate_coverage_markdown({}) == ""

    def test_single_req_generates_utest_item(self):
        md = generate_coverage_markdown({"req~auth.login~1": {"test::t1"}})
        assert "`utest~auth.login~1`" in md
        assert "Covers:" in md
        assert "- req~auth.login~1" in md
        assert "Status: approved" in md

    def test_dsn_marker_generates_utest_covering_dsn(self):
        md = generate_coverage_markdown({"dsn~auth.login~1": {"test::t1"}})
        assert "`utest~auth.login~1`" in md
        assert "- dsn~auth.login~1" in md

    def test_multiple_ids_sorted(self):
        md = generate_coverage_markdown(
            {
                "req~z.item~1": {"test::t1"},
                "req~a.item~1": {"test::t2"},
            }
        )
        # a.item should appear before z.item
        pos_a = md.index("req~a.item~1")
        pos_z = md.index("req~z.item~1")
        assert pos_a < pos_z

    def test_generated_markdown_parses_cleanly(self, tmp_path):
        """The generated markdown should be parseable by our own parser."""
        md = generate_coverage_markdown(
            {
                "req~auth.login~1": {"test::t1"},
                "req~auth.logout~2": {"test::t2"},
            }
        )
        f = tmp_path / "coverage.md"
        f.write_text(md, encoding="utf-8")
        items = parse_spec_file(f)
        assert len(items) == 2
        ids = {item.id for item in items}
        assert ids == {"utest~auth.login~1", "utest~auth.logout~2"}
        # Verify covers links
        for item in items:
            assert len(item.covers) == 1
            assert item.item_type == "utest"


class TestWriteCoverageFile:
    def test_writes_file_to_directory(self, tmp_path):
        covered = {"req~auth.login~1": {"test::t1"}}
        path = write_coverage_file(covered, tmp_path)
        assert path.exists()
        assert path.name == "utest-coverage.md"
        content = path.read_text(encoding="utf-8")
        assert "utest~auth.login~1" in content


class TestCreateCoverageDir:
    def test_returns_none_when_no_markers(self):
        item = _make_item("test_foo.py::test_plain", [])
        result = create_coverage_dir([item])
        assert result is None

    def test_returns_temp_dir_with_coverage_file(self):
        item = _make_item("test_foo.py::test_check", [("req", ["req~auth.login~1"])])
        tmp = create_coverage_dir([item])
        assert tmp is not None
        try:
            files = list(Path(tmp.name).iterdir())
            assert len(files) == 1
            assert files[0].name == "utest-coverage.md"
            content = files[0].read_text(encoding="utf-8")
            assert "utest~auth.login~1" in content
        finally:
            tmp.cleanup()
