"""Tests for pytest_sdd.lint — structural lint checks."""

from pathlib import Path

from pytest_sdd.lint import (
    check_bare_obligations,
    check_covers_syntax,
    check_id_format,
    check_mixed_obligations,
    check_needs_values,
    check_status,
    run_all,
)
from pytest_sdd.models import SpecItem


def _item(
    spec_id: str = "req~area.item~1",
    status: str = "approved",
    body: str = "",
    needs: list[str] | None = None,
    covers: list[str] | None = None,
) -> SpecItem:
    parts = spec_id.split("~")
    return SpecItem(
        id=spec_id,
        item_type=parts[0],
        name=parts[1],
        revision=int(parts[2]),
        title="Item",
        status=status,
        body=body or f"The system `SHALL` do something.\n\nNeeds: {', '.join(needs or ['utest'])}",
        needs=needs if needs is not None else ["utest"],
        covers=covers or [],
        source_file="spec.md",
        line_number=1,
    )


# ---------------------------------------------------------------------------
# check_bare_obligations
# ---------------------------------------------------------------------------


class TestBareObligations:
    def test_clean_file_no_errors(self):
        text = "The system `SHALL` validate the sender.\nIt `SHALL NOT` skip.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert errors == []

    def test_bare_shall_flagged(self):
        text = "The system SHALL validate the sender.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert len(errors) == 1
        assert "SHALL" in errors[0]
        assert "spec.md:1:" in errors[0]

    def test_bare_shall_not_flagged(self):
        text = "The system SHALL NOT skip validation.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert len(errors) == 1
        assert "SHALL NOT" in errors[0]

    def test_bare_should_flagged(self):
        errors = check_bare_obligations(Path("spec.md"), "Use SHOULD be preferred.\n")
        assert any("SHOULD" in e for e in errors)

    def test_bare_may_flagged(self):
        errors = check_bare_obligations(Path("spec.md"), "The user MAY skip.\n")
        assert any("MAY" in e for e in errors)

    def test_wrapped_keyword_no_error(self):
        text = "The system `SHALL` do it and `MAY` also do that.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert errors == []

    def test_multiple_bare_keywords_on_same_line(self):
        text = "SHALL and SHOULD not mix.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert len(errors) == 2

    def test_bare_keyword_in_preamble_prose(self):
        """Preamble prose (not inside spec items) is also checked."""
        text = "# Spec\n\nAll requirements SHALL be testable.\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert len(errors) == 1

    def test_line_number_in_error(self):
        text = "line 1\nline 2 SHALL fail\nline 3\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert "spec.md:2:" in errors[0]

    def test_shall_in_heading_flagged(self):
        """Headers are not exempt from the backtick rule."""
        text = "## SHALL Requirements\n"
        errors = check_bare_obligations(Path("spec.md"), text)
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# check_mixed_obligations
# ---------------------------------------------------------------------------


class TestMixedObligations:
    def test_single_shall_no_error(self):
        item = _item(body="The system `SHALL` do it.\n")
        errors = check_mixed_obligations([item])
        assert errors == []

    def test_repeated_shall_no_error(self):
        item = _item(body="The system `SHALL` do A and `SHALL` do B.\n")
        errors = check_mixed_obligations([item])
        assert errors == []

    def test_shall_and_may_flagged(self):
        item = _item(body="The system `SHALL` do A and `MAY` do B.\n")
        errors = check_mixed_obligations([item])
        assert len(errors) == 1
        assert "mixed obligation" in errors[0]
        assert item.id in errors[0]

    def test_shall_and_should_flagged(self):
        item = _item(body="The system `SHALL` do A and `SHOULD` do B.\n")
        errors = check_mixed_obligations([item])
        assert len(errors) == 1

    def test_shall_and_shall_not_no_error(self):
        """SHALL and SHALL NOT are both mandatory level — no error."""
        item = _item(body="The system `SHALL` do A. It `SHALL NOT` do B.\n")
        errors = check_mixed_obligations([item])
        assert errors == []

    def test_should_and_should_not_no_error(self):
        """SHOULD and SHOULD NOT are both preferred level — no error."""
        item = _item(body="The system `SHOULD` do A. It `SHOULD NOT` do B.\n")
        errors = check_mixed_obligations([item])
        assert errors == []

    def test_shall_and_should_not_flagged(self):
        """Mandatory + preferred is a mixed level — error."""
        item = _item(body="The system `SHALL` do A and `SHOULD NOT` do B.\n")
        errors = check_mixed_obligations([item])
        assert len(errors) == 1

    def test_no_keywords_no_error(self):
        """Items with no obligation keywords (e.g., leaf items) are not flagged."""
        item = _item(body="This item covers the requirement.\n")
        errors = check_mixed_obligations([item])
        assert errors == []

    def test_multiple_items_independent(self):
        items = [
            _item("req~area.a~1", body="The system `SHALL` do A.\n"),
            _item("req~area.b~1", body="The system `SHALL` do A and `MAY` do B.\n"),
        ]
        errors = check_mixed_obligations(items)
        assert len(errors) == 1
        assert "req~area.b~1" in errors[0]


# ---------------------------------------------------------------------------
# check_status
# ---------------------------------------------------------------------------


class TestStatus:
    def test_approved_no_error(self):
        assert check_status([_item(status="approved")]) == []

    def test_draft_no_error(self):
        assert check_status([_item(status="draft")]) == []

    def test_proposed_no_error(self):
        assert check_status([_item(status="proposed")]) == []

    def test_invalid_status_flagged(self):
        errors = check_status([_item(status="active")])
        assert len(errors) == 1
        assert "invalid Status" in errors[0]
        assert "active" in errors[0]

    def test_missing_status_flagged(self):
        errors = check_status([_item(status="")])
        assert len(errors) == 1
        assert "missing Status" in errors[0]

    def test_multiple_items(self):
        items = [_item("req~a.x~1", status="approved"), _item("req~a.y~1", status="bad")]
        errors = check_status(items)
        assert len(errors) == 1
        assert "req~a.y~1" in errors[0]


# ---------------------------------------------------------------------------
# check_covers_syntax
# ---------------------------------------------------------------------------


class TestCoversSyntax:
    def test_valid_covers_no_error(self):
        item = _item(covers=["req~area.item~1", "req~other.thing~2"])
        assert check_covers_syntax([item]) == []

    def test_malformed_covers_flagged(self):
        item = _item(covers=["req-area-001"])
        errors = check_covers_syntax([item])
        assert len(errors) == 1
        assert "malformed Covers" in errors[0]
        assert "req-area-001" in errors[0]

    def test_covers_with_spaces_flagged(self):
        item = _item(covers=["req~area.item ~1"])
        errors = check_covers_syntax([item])
        assert len(errors) == 1

    def test_empty_covers_no_error(self):
        item = _item(covers=[])
        assert check_covers_syntax([item]) == []

    def test_dsn_type_covers_valid(self):
        item = _item(covers=["dsn~area.design~1"])
        assert check_covers_syntax([item]) == []


# ---------------------------------------------------------------------------
# check_needs_values
# ---------------------------------------------------------------------------


class TestNeedsValues:
    def test_known_types_no_error(self):
        for needs in [["utest"], ["dsn", "utest"], ["itest"], ["feat"]]:
            item = _item(needs=needs)
            assert check_needs_values([item]) == [], f"should pass for {needs}"

    def test_unknown_type_flagged(self):
        item = _item(needs=["unittest"])
        errors = check_needs_values([item])
        assert len(errors) == 1
        assert "unknown artifact type" in errors[0]
        assert "unittest" in errors[0]

    def test_empty_needs_no_error(self):
        """Items with no Needs: (leaf items) are not flagged."""
        item = _item(needs=[])
        assert check_needs_values([item]) == []

    def test_multiple_invalid_needs(self):
        item = _item(needs=["foo", "bar"])
        errors = check_needs_values([item])
        assert len(errors) == 2


# ---------------------------------------------------------------------------
# check_id_format
# ---------------------------------------------------------------------------


class TestIdFormat:
    def test_valid_ids_no_error(self, tmp_path):
        path = tmp_path / "spec.md"
        text = "`req~area.item~1` and `dsn~other.thing~2`"
        items = [
            _item("req~area.item~1"),
            _item("dsn~other.thing~2"),
        ]
        assert check_id_format(path, text, items) == []

    def test_malformed_id_flagged(self, tmp_path):
        path = tmp_path / "spec.md"
        # Looks like an ID but has extra segment
        text = "`req~area~item~1`"
        errors = check_id_format(path, text, [])
        assert len(errors) == 1
        assert "malformed spec ID" in errors[0]

    def test_already_parsed_id_not_double_flagged(self, tmp_path):
        path = tmp_path / "spec.md"
        text = "`req~area.item~1`"
        items = [_item("req~area.item~1")]
        errors = check_id_format(path, text, items)
        assert errors == []

    def test_near_miss_without_valid_name_flagged(self, tmp_path):
        path = tmp_path / "spec.md"
        # Has tildes but malformed name (starts with digit)
        text = "`req~1invalid~1`"
        errors = check_id_format(path, text, [])
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# run_all with <!-- oft:off --> blocks
# ---------------------------------------------------------------------------


class TestOftOffBlocks:
    def test_bare_obligation_in_off_block_ignored(self):
        text = (
            "<!-- oft:off -->\n"
            "Every item uses SHALL be tested.\n"
            "<!-- oft:on -->\n"
        )
        errors = run_all(Path("spec.md"), text, [])
        assert errors == []

    def test_near_miss_id_in_off_block_ignored(self):
        text = (
            "<!-- oft:off -->\n"
            "IDs use the `req~name~revision` format.\n"
            "<!-- oft:on -->\n"
        )
        errors = run_all(Path("spec.md"), text, [])
        assert errors == []

    def test_content_outside_off_block_still_checked(self):
        text = (
            "<!-- oft:off -->\n"
            "Example: SHALL be ignored.\n"
            "<!-- oft:on -->\n"
            "But this SHALL fail.\n"
        )
        errors = run_all(Path("spec.md"), text, [])
        assert len(errors) == 1
        assert "SHALL" in errors[0]

    def test_multiple_off_blocks(self):
        text = (
            "<!-- oft:off -->\nSHALL\n<!-- oft:on -->\n"
            "Clean line.\n"
            "<!-- oft:off -->\nSHOULD\n<!-- oft:on -->\n"
        )
        errors = run_all(Path("spec.md"), text, [])
        assert errors == []

    def test_line_numbers_preserved_after_stripping(self):
        text = (
            "line 1\n"
            "<!-- oft:off -->\n"
            "line 3\n"
            "<!-- oft:on -->\n"
            "line 5 SHALL fail\n"
        )
        errors = run_all(Path("spec.md"), text, [])
        assert len(errors) == 1
        assert "spec.md:5:" in errors[0]
