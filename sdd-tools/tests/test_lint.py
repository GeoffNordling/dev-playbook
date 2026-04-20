"""Tests for sdd_tools.lint — Finding-emitting markdown lint."""

from pathlib import Path

from sdd_tools.lint import lint_file


def _by_rule(findings, rule):
    return [f for f in findings if f.rule == rule]


# ---------------------------------------------------------------------------
# Fenced code blocks
# ---------------------------------------------------------------------------


class TestFencedCode:
    def test_clean(self):
        text = "# Title\n\nProse.\n"
        assert _by_rule(lint_file(Path("s.md"), text), "lint.fenced-code") == []

    def test_fenced_block(self):
        text = "# Title\n\n```python\nprint('x')\n```\n"
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.fenced-code")
        assert len(findings) == 2
        assert findings[0].line == 3
        assert findings[1].line == 5

    def test_indented_block_allowed(self):
        text = "Prose\n\n    indented code\n"
        assert _by_rule(lint_file(Path("s.md"), text), "lint.fenced-code") == []

    def test_off_block_suppresses(self):
        text = (
            "<!-- oft:off -->\n"
            "```python\n"
            "x\n"
            "```\n"
            "<!-- oft:on -->\n"
        )
        assert _by_rule(lint_file(Path("s.md"), text), "lint.fenced-code") == []


# ---------------------------------------------------------------------------
# Bare obligation keywords
# ---------------------------------------------------------------------------


class TestBareObligations:
    def test_clean(self):
        text = "The system `SHALL` validate.\n"
        assert _by_rule(lint_file(Path("s.md"), text), "lint.bare-obligation") == []

    def test_bare_shall_flagged(self):
        text = "The system SHALL validate.\n"
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.bare-obligation")
        assert len(findings) == 1
        assert findings[0].line == 1
        assert "SHALL" in findings[0].message

    def test_bare_shall_not_flagged(self):
        findings = _by_rule(
            lint_file(Path("s.md"), "Do not SHALL NOT skip.\n"),
            "lint.bare-obligation",
        )
        assert len(findings) == 1
        assert "SHALL NOT" in findings[0].message

    def test_off_block_suppresses(self):
        text = "<!-- oft:off -->\nIt SHALL be ignored.\n<!-- oft:on -->\n"
        assert _by_rule(lint_file(Path("s.md"), text), "lint.bare-obligation") == []


# ---------------------------------------------------------------------------
# Bad ID format
# ---------------------------------------------------------------------------


class TestIdFormat:
    def test_clean(self):
        text = "`req~area.x~1`\n"
        assert _by_rule(lint_file(Path("s.md"), text), "lint.bad-id") == []

    def test_extra_segment_flagged(self):
        text = "`req~area~item~1`\n"
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.bad-id")
        assert len(findings) == 1


# ---------------------------------------------------------------------------
# Item-level checks (mixed obligations, status, covers, needs)
# ---------------------------------------------------------------------------


_GOOD_ITEM_TEMPLATE = """\
---

### Item
`{id}`
Status: {status}

The system `SHALL` do something.

{extra}

---
"""


def _spec(id_="req~area.x~1", status="approved", extra="Needs: utest"):
    return _GOOD_ITEM_TEMPLATE.format(id=id_, status=status, extra=extra)


class TestStatus:
    def test_valid_status_no_finding(self):
        findings = _by_rule(lint_file(Path("s.md"), _spec()), "lint.bad-status")
        assert findings == []

    def test_invalid_status_flagged(self):
        findings = _by_rule(
            lint_file(Path("s.md"), _spec(status="active")),
            "lint.bad-status",
        )
        assert len(findings) == 1
        assert "invalid Status 'active'" in findings[0].message

    def test_missing_status_flagged(self):
        text = """\
---

### Item
`req~area.x~1`

The system `SHALL` do something.

Needs: utest

---
"""
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.bad-status")
        assert len(findings) == 1
        assert "missing Status" in findings[0].message
        assert findings[0].line_kind == "item header"


class TestMixedObligations:
    def test_single_level_no_finding(self):
        text = _spec(extra="More `SHALL` and `SHALL NOT` text.\n\nNeeds: utest")
        assert (
            _by_rule(lint_file(Path("s.md"), text), "lint.mixed-obligations")
            == []
        )

    def test_mixed_levels_flagged(self):
        text = _spec(extra="Also `MAY` skip.\n\nNeeds: utest")
        findings = _by_rule(
            lint_file(Path("s.md"), text), "lint.mixed-obligations"
        )
        assert len(findings) == 1
        assert findings[0].spec_id == "req~area.x~1"


class TestCovers:
    def test_valid_covers_no_finding(self):
        text = """\
---

### D
`dsn~area.d~1`
Status: approved

`SHALL` do.

Covers:
  - req~area.x~1

Needs: utest

---
"""
        assert _by_rule(lint_file(Path("s.md"), text), "lint.bad-covers") == []

    def test_malformed_covers_flagged(self):
        text = """\
---

### D
`dsn~area.d~1`
Status: approved

`SHALL` do.

Covers:
  - bad-ref

Needs: utest

---
"""
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.bad-covers")
        assert len(findings) == 1
        assert "bad-ref" in findings[0].message


class TestNeeds:
    def test_known_type_no_finding(self):
        assert _by_rule(lint_file(Path("s.md"), _spec()), "lint.bad-needs") == []

    def test_unknown_type_flagged(self):
        text = _spec(extra="Needs: unittest")
        findings = _by_rule(lint_file(Path("s.md"), text), "lint.bad-needs")
        assert len(findings) == 1
        assert "unittest" in findings[0].message
