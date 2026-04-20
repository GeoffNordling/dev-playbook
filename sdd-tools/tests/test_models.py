"""Tests for sdd_tools.models — SpecItem and Finding."""

from pathlib import Path

from sdd_tools.models import Finding, SpecItem, render_findings


def test_specitem_default_interfaces_empty():
    item = SpecItem(
        id="req~area.x~1",
        doctype="req",
        name="area.x",
        revision=1,
        title="X",
        status="approved",
        description="body",
        rationale="",
        covers=[],
        needs=[],
        source_file=Path("specs/x.md"),
        source_line=10,
    )
    assert item.interfaces == []


class TestFindingRender:
    def test_basic(self):
        f = Finding(
            rule="lint.fenced-code",
            file=Path("specs/foo.md"),
            line=12,
            message="fenced code block (```) breaks OFT parsing",
        )
        assert f.render() == "specs/foo.md:12  lint.fenced-code  fenced code block (```) breaks OFT parsing"

    def test_with_line_kind(self):
        f = Finding(
            rule="interface.mismatch",
            file=Path("specs/d.md"),
            line=42,
            line_kind="dsn header",
            message="signature differs",
        )
        assert "specs/d.md:42 (dsn header)" in f.render()

    def test_with_detail_and_fix(self):
        f = Finding(
            rule="interface.mismatch",
            file=Path("specs/d.md"),
            line=42,
            line_kind="dsn header",
            message="signature differs for parser.parse_session",
            detail="committed: parser.parse_session(path: str) -> None\nactual:    parser.parse_session(path: pathlib.Path) -> None",
            fix="update Interface: or update the code to match",
        )
        rendered = f.render()
        assert "  committed:" in rendered
        assert "  actual:" in rendered
        assert "  fix:       update Interface:" in rendered


def test_render_findings_joins_blocks():
    findings = [
        Finding(
            rule="lint.bare-obligation",
            file=Path("a.md"),
            line=1,
            message="bare 'SHALL'",
        ),
        Finding(
            rule="lint.fenced-code",
            file=Path("b.md"),
            line=5,
            message="fenced",
        ),
    ]
    rendered = render_findings(findings)
    assert "a.md:1" in rendered
    assert "b.md:5" in rendered
