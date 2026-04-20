"""Tests for sdd_tools.markers."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from sdd_tools.markers import (
    collect_covered_ids,
    create_coverage_dir,
    generate_coverage_markdown,
    write_coverage_file,
)


def _fake_item(node_id: str, *markers: tuple[str, str]) -> Mock:
    item = Mock(spec=pytest.Item)
    item.nodeid = node_id
    fake_markers = []
    for name, value in markers:
        m = Mock()
        m.name = name
        m.args = (value,)
        fake_markers.append(m)
    item.iter_markers = lambda: iter(fake_markers)
    return item


class TestCollectCoveredIds:
    def test_empty(self):
        assert collect_covered_ids([]) == {}

    def test_no_relevant_markers(self):
        item = _fake_item("test_x.py::test_a", ("parametrize", "x"))
        assert collect_covered_ids([item]) == {}

    def test_req_marker(self):
        item = _fake_item("test_x.py::test_a", ("req", "req~area.x~1"))
        assert collect_covered_ids([item]) == {"req~area.x~1": {"test_x.py::test_a"}}

    def test_dsn_marker(self):
        item = _fake_item("t.py::a", ("dsn", "dsn~area.d~1"))
        assert collect_covered_ids([item]) == {"dsn~area.d~1": {"t.py::a"}}

    def test_invalid_marker_value_skipped(self):
        item = _fake_item("t.py::a", ("req", "not-a-spec-id"))
        assert collect_covered_ids([item]) == {}

    def test_two_tests_one_id(self):
        items = [
            _fake_item("t.py::a", ("req", "req~x.y~1")),
            _fake_item("t.py::b", ("req", "req~x.y~1")),
        ]
        result = collect_covered_ids(items)
        assert result == {"req~x.y~1": {"t.py::a", "t.py::b"}}


class TestGenerateCoverageMarkdown:
    def test_empty_returns_empty(self):
        assert generate_coverage_markdown({}) == ""

    def test_single_id(self):
        text = generate_coverage_markdown({"req~area.x~1": {"t.py::a"}})
        assert "`utest~area.x~1`" in text
        assert "Covers:" in text
        assert "  - req~area.x~1" in text

    def test_sorted_output(self):
        text = generate_coverage_markdown(
            {
                "req~b.x~1": {"t.py::b"},
                "req~a.x~1": {"t.py::a"},
            }
        )
        assert text.index("a.x") < text.index("b.x")


class TestWriteCoverageFile:
    def test_writes(self, tmp_path):
        path = write_coverage_file({"req~x.y~1": {"t.py::a"}}, tmp_path)
        assert path.exists()
        assert "`utest~x.y~1`" in path.read_text()


class TestCreateCoverageDir:
    def test_no_markers_returns_none(self):
        assert create_coverage_dir([]) is None

    def test_with_markers_returns_tempdir(self):
        item = _fake_item("t.py::a", ("req", "req~x.y~1"))
        tmp = create_coverage_dir([item])
        try:
            assert tmp is not None
            files = list(Path(tmp.name).iterdir())
            assert len(files) == 1
            assert files[0].name == "utest-coverage.md"
        finally:
            if tmp is not None:
                tmp.cleanup()
