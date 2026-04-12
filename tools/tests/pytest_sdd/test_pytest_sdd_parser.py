"""Tests for pytest_sdd.parser — OFT markdown → SpecItem list."""

from pathlib import Path

from pytest_sdd.parser import parse_spec_file


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestParseSpecFile:
    def test_single_req_item(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Allowlist Check
`req~ing.allowlist-check~1`
Status: approved

When a message arrives, the system `SHALL` validate the sender.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 1
        item = items[0]
        assert item.id == "req~ing.allowlist-check~1"
        assert item.item_type == "req"
        assert item.name == "ing.allowlist-check"
        assert item.revision == 1
        assert item.title == "Allowlist Check"
        assert item.status == "approved"
        assert item.needs == ["utest"]
        assert item.covers == []
        assert item.source_file == str(f)

    def test_multiple_items_split_by_hrule(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item One
`req~area.item-one~1`
Status: approved

The system `SHALL` do one thing.

Needs: utest

---

### Item Two
`req~area.item-two~1`
Status: approved

The system `SHALL` do another thing.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 2
        assert items[0].id == "req~area.item-one~1"
        assert items[1].id == "req~area.item-two~1"

    def test_dsn_item_with_covers(self, tmp_path):
        f = tmp_path / "design.md"
        _write(
            f,
            """\
---

### Classifier Function
`dsn~class.classify~1`
Status: approved

`classify_activity()` `SHALL` accept a list of exchanges.

Covers:
  - req~class.assign-categories~1
  - req~class.prefer-specific~1

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 1
        item = items[0]
        assert item.item_type == "dsn"
        assert item.covers == [
            "req~class.assign-categories~1",
            "req~class.prefer-specific~1",
        ]
        assert item.needs == ["utest"]

    def test_needs_comma_separated(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: dsn, utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].needs == ["dsn", "utest"]

    def test_no_needs_is_leaf(self, tmp_path):
        """An item without Needs: is a terminating/leaf item — not an error."""
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Leaf Item
`utest~area.check~1`
Status: approved

This test covers the requirement.

Covers:
  - req~area.item~1

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].needs == []

    def test_status_extracted(self, tmp_path):
        for status in ("draft", "proposed", "approved"):
            f = tmp_path / f"spec_{status}.md"
            _write(
                f,
                f"""\
---

### Item
`req~area.item~1`
Status: {status}

The system `SHALL` do something.

Needs: utest

---
""",
            )
            items = parse_spec_file(f)
            assert items[0].status == status

    def test_missing_status_is_empty_string(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`req~area.item~1`

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].status == ""

    def test_title_from_h3(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### My Requirement Title
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].title == "My Requirement Title"

    def test_index_file_no_items(self, tmp_path):
        """Files with no spec IDs return an empty list."""
        f = tmp_path / "index.md"
        _write(
            f,
            """\
# Index

This file describes the spec structure.

| File | Scope |
|------|-------|
| ingress.md | Message ingress |
| access-control.md | Access control |
""",
        )
        items = parse_spec_file(f)
        assert items == []

    def test_intro_text_before_first_hrule_ignored(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
# Section Title

This introductory prose has no spec items.

---

### Real Item
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 1
        assert items[0].id == "req~area.item~1"

    def test_h2_segment_without_id_ignored(self, tmp_path):
        """H2 section headings without a spec ID are not counted as items."""
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

## Parsing Pipeline

This section groups parsing requirements.

---

### Parse Entry
`req~parse.entry~1`
Status: approved

The system `SHALL` parse each entry.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 1
        assert items[0].id == "req~parse.entry~1"

    def test_name_with_dots_hierarchy(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Deep Name
`req~parser.segment.timestamp~1`
Status: approved

The system `SHALL` parse timestamps.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].name == "parser.segment.timestamp"

    def test_name_with_hyphens_and_underscores(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`req~area.my-item_v2~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].name == "area.my-item_v2"

    def test_multi_digit_revision(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`req~area.item~12`
Status: approved

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].revision == 12

    def test_various_item_types(self, tmp_path):
        for itype in ("feat", "arch", "impl", "utest", "itest", "stest"):
            f = tmp_path / f"spec_{itype}.md"
            _write(
                f,
                f"""\
---

### Item
`{itype}~area.item~1`
Status: approved

Description.

---
""",
            )
            items = parse_spec_file(f)
            assert items[0].item_type == itype

    def test_line_number_tracked(self, tmp_path):
        f = tmp_path / "spec.md"
        content = """\
---

### Item
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
"""
        _write(f, content)
        items = parse_spec_file(f)
        # ID is on line 4 (0-indexed: 3), after the leading ---\n\n### Item\n
        assert items[0].line_number == 3

    def test_rationale_section_included_in_body(self, tmp_path):
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`req~area.item~1`
Status: approved

The system `SHALL` do something.

Rationale:
This is why.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert "Rationale:" in items[0].body
        assert "This is why." in items[0].body

    def test_oft_off_block_prevents_phantom_items(self, tmp_path):
        """Spec IDs inside <!-- oft:off --> blocks are not parsed."""
        f = tmp_path / "index.md"
        _write(
            f,
            """\
# Index

<!-- oft:off -->
IDs use the `req~name~revision` format.

---

### Example Item
`req~example.item~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
<!-- oft:on -->
""",
        )
        items = parse_spec_file(f)
        assert items == []

    def test_oft_off_block_real_items_outside_still_parsed(self, tmp_path):
        """Items outside off-blocks are still parsed normally."""
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
<!-- oft:off -->
`req~example.ignored~1`
<!-- oft:on -->

---

### Real Item
`req~area.real~1`
Status: approved

The system `SHALL` do something.

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert len(items) == 1
        assert items[0].id == "req~area.real~1"

    def test_covers_with_asterisk_bullets(self, tmp_path):
        """Covers: blocks may use * or + bullets as well as -."""
        f = tmp_path / "spec.md"
        _write(
            f,
            """\
---

### Item
`dsn~area.item~1`
Status: approved

Description.

Covers:
  * req~area.req-one~1
  + req~area.req-two~1

Needs: utest

---
""",
        )
        items = parse_spec_file(f)
        assert items[0].covers == ["req~area.req-one~1", "req~area.req-two~1"]
