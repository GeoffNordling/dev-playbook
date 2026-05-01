"""Tests for sdd_tools.formatter."""

from pathlib import Path

from sdd_tools.formatter import format_chains
from sdd_tools.models import SpecItem


def _item(spec_id, doctype, **kwargs):
    name = spec_id.split("~")[1]
    defaults = dict(
        id=spec_id,
        doctype=doctype,
        name=name,
        revision=1,
        title=name,
        status="approved",
        description="The system shall do something.",
        rationale="",
        covers=[],
        needs=[],
        source_file=Path(f"/repo/specs/{name}.md"),
        source_line=10,
    )
    defaults.update(kwargs)
    return SpecItem(**defaults)


class TestFormatChains:
    def test_chain_label_in_header(self):
        chain = [_item("feat~auth~1", "feat"), _item("req~login~1", "req")]
        text = format_chains([chain], Path("/repo"))
        assert "Chain 1: feat~auth~1 > req~login~1" in text

    def test_per_item_metadata(self):
        chain = [_item("req~x~1", "req")]
        text = format_chains([chain], Path("/repo"))
        assert "[req] req~x~1" in text
        assert "Title: x" in text
        assert "File: specs/x.md:10" in text

    def test_status_rendered(self):
        chain = [_item("req~x~1", "req", status="approved")]
        text = format_chains([chain], Path("/repo"))
        assert "Status: approved" in text

    def test_covers_block_rendered(self):
        chain = [_item("req~x~1", "req", covers=["feat~y~1"])]
        text = format_chains([chain], Path("/repo"))
        assert "Covers:" in text
        assert "- feat~y~1" in text

    def test_needs_inline_rendered(self):
        chain = [_item("req~x~1", "req", needs=["dsn", "utest"])]
        text = format_chains([chain], Path("/repo"))
        assert "Needs: dsn, utest" in text

    def test_source_outside_root_kept_absolute(self):
        chain = [_item("req~x~1", "req", source_file=Path("/elsewhere/r.md"))]
        text = format_chains([chain], Path("/repo"))
        assert "/elsewhere/r.md" in text
