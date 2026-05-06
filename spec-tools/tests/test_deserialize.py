"""Tests for spec_tools.deserialize."""

import pathlib

import pytest

from spec_tools.deserialize import SpecParseError, parse
from spec_tools.model import ItemId, SpecItem

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


def load(name: str) -> pathlib.Path:
    """Return the absolute path to a fixture file under `tests/fixtures/`."""
    return FIXTURES_DIR / name


@pytest.mark.covers("dsn~deserialize.parse-error~0")
def test_spec_parse_error_exposes_constructor_fields():
    error = SpecParseError(
        path=pathlib.Path("specs/example.md"),
        line=7,
        rule_violated="id-syntax",
        message="ID triple has wrong number of parts",
    )

    assert error.path == pathlib.Path("specs/example.md")
    assert error.line == 7
    assert error.rule_violated == "id-syntax"
    assert error.message == "ID triple has wrong number of parts"


@pytest.mark.covers("dsn~deserialize.parse-error~0")
def test_spec_parse_error_is_raisable():
    with pytest.raises(SpecParseError) as exc_info:
        raise SpecParseError(
            path=pathlib.Path("specs/example.md"),
            line=7,
            rule_violated="id-syntax",
            message="ID triple has wrong number of parts",
        )

    assert exc_info.value.rule_violated == "id-syntax"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_empty_file_returns_empty_list():
    assert parse(load("good/empty.md")) == []


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_unknown_keyword_for_undefined_keyword():
    fixture_path = load("bad/unknown_keyword.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "unknown-keyword"
    assert error.path == fixture_path
    assert error.line == 13


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_duplicate_keyword_when_block_keyword_repeats():
    fixture_path = load("bad/duplicate_keyword.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "duplicate-keyword"
    assert error.path == fixture_path
    assert error.line == 13


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_malformed_body_for_empty_tags_inline():
    fixture_path = load("bad/malformed_tags.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.path == fixture_path
    assert error.line == 13


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_missing_keyword_when_description_absent():
    fixture_path = load("bad/missing_description.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "missing-keyword"
    assert error.path == fixture_path
    assert error.line == 7


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_error_with_line_and_path():
    fixture_path = load("bad/id_syntax_too_few_parts.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.path == fixture_path
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_for_whitespace_in_name():
    fixture_path = load("bad/id_whitespace_in_name.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_for_negative_revision():
    fixture_path = load("bad/id_negative_revision.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_when_id_line_missing_backticks():
    fixture_path = load("bad/id_not_backtick_wrapped.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name",
    [
        "bad/id_artifact_type_unknown.md",
        "bad/id_artifact_type_empty.md",
        "bad/id_name_lead_digit.md",
        "bad/id_name_lead_dot.md",
        "bad/id_name_lead_hyphen.md",
        "bad/id_name_lead_underscore.md",
        "bad/id_name_consecutive_dots.md",
        "bad/id_name_empty.md",
        "bad/id_name_invalid_char.md",
        "bad/id_revision_non_integer.md",
    ],
)
def test_parse_raises_id_syntax_for_section_3_violations(fixture_name: str):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.path == fixture_path
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name, expected_line",
    [
        ("bad/empty_description.md", 10),
        ("bad/empty_rationale.md", 13),
        ("bad/empty_comment.md", 13),
        ("bad/empty_covers.md", 13),
        ("bad/empty_depends.md", 13),
        ("bad/empty_needs.md", 13),
        ("bad/empty_interface.md", 13),
        ("bad/empty_agent_review.md", 13),
    ],
)
def test_parse_raises_malformed_body_for_empty_keyword_content(
    fixture_name: str, expected_line: int
):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.path == fixture_path
    assert error.line == expected_line


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name",
    [
        "bad/heading_h1.md",
        "bad/heading_h2.md",
        "bad/heading_h4.md",
        "bad/heading_no_space.md",
        "bad/heading_empty_text.md",
    ],
)
def test_parse_raises_malformed_heading_for_non_conformant_atx_headings(
    fixture_name: str,
):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-heading"
    assert error.path == fixture_path
    assert error.line == 1


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name",
    [
        "bad/tags_no_space_after_colon.md",
        "bad/tags_double_space_after_colon.md",
        "bad/tags_no_space_after_comma.md",
        "bad/tags_space_before_comma.md",
        "bad/tags_empty_entry.md",
    ],
)
def test_parse_raises_malformed_body_for_non_canonical_tags(fixture_name: str):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.path == fixture_path
    assert error.line == 7


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_malformed_body_for_blank_line_in_description():
    fixture_path = load("bad/blank_line_in_description.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.path == fixture_path
    assert error.line == 7


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_malformed_body_for_stray_prose_within_item():
    fixture_path = load("bad/stray_prose_in_item.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.line == 15


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_repeated_keywords_collect_each_entry_in_order():
    [item] = parse(load("good/repeated.md"))

    assert item.interface == ["mod.f() -> None", "mod.g() -> int"]
    assert item.agent_review == ["check 1", "check 2"]


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_inline_tags_split_on_commas():
    [item] = parse(load("good/tags.md"))

    assert item.tags == ["alpha", "beta", "gamma"]


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_needs_keyword_yields_string_list():
    [item] = parse(load("good/needs.md"))

    assert item.needs == ["utest", "itest"]


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_id_bullet_keywords_yield_lists_of_item_ids():
    [item] = parse(load("good/id_bullets.md"))

    assert item.covers == [ItemId("feat", "alpha", 0), ItemId("feat", "beta", 1)]
    assert item.depends == [ItemId("dsn", "gamma", 2)]


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_block_keywords_capture_multiline_bodies():
    [item] = parse(load("good/blocks.md"))

    assert item.description == (
        "First line of description.\nSecond line of description."
    )
    assert item.rationale == "Why we built this.\nAcross two lines."
    assert item.comment == "Side note."


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_preserves_source_order_across_multiple_items():
    items = parse(load("good/two_items.md"))

    assert [item.id for item in items] == [
        ItemId("dsn", "first", 0),
        ItemId("dsn", "second", 0),
    ]
    assert [item.description for item in items] == ["One.", "Two."]


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_when_heading_at_eof():
    fixture_path = load("bad/missing_id_line_eof.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 1


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_id_syntax_when_id_line_replaced_by_keyword():
    fixture_path = load("bad/missing_id_line_followed_by_keyword.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 2


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_keyword_order_when_keywords_out_of_canonical_order():
    fixture_path = load("bad/keyword_order.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "keyword-order"
    assert error.line == 9


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name",
    ["bad/fenced_code_block_backtick.md", "bad/fenced_code_block_tilde.md"],
)
def test_parse_raises_fenced_code_block_for_fence_markers(fixture_name: str):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "fenced-code-block"
    assert error.line == 7


@pytest.mark.covers("dsn~deserialize.parse~0")
@pytest.mark.parametrize(
    "fixture_name",
    [
        "bad/interface_continuation.md",
        "bad/agent_review_continuation.md",
    ],
)
def test_parse_raises_malformed_body_for_repeated_keyword_continuation(
    fixture_name: str,
):
    fixture_path = load(fixture_name)

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"
    assert error.line == 8


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_malformed_body_for_lowercase_keyword():
    fixture_path = load("bad/keyword_lowercase.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "malformed-body"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_unknown_keyword_for_uppercase_keyword():
    fixture_path = load("bad/keyword_uppercase.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "unknown-keyword"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_obligation_not_backticked_for_bare_uppercase_verb():
    fixture_path = load("bad/obligation_not_backticked.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "obligation-not-backticked"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_raises_obligation_mixed_levels_for_shall_and_should():
    fixture_path = load("bad/obligation_mixed_levels.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "obligation-mixed-levels"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_accepts_shall_and_shall_not_as_same_level():
    [item] = parse(load("good/obligation_same_level.md"))

    assert item.id.name == "same-level"


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_aborts_on_first_violation_only():
    fixture_path = load("bad/multiple_violations.md")

    with pytest.raises(SpecParseError) as exc_info:
        parse(fixture_path)

    error = exc_info.value
    assert error.rule_violated == "id-syntax"
    assert error.line == 2


@pytest.mark.covers("dsn~deserialize.parse~0")
def test_parse_minimal_item_yields_one_spec_item_with_default_optionals():
    items = parse(load("good/minimal.md"))

    assert items == [
        SpecItem(
            heading="Topic Classifier",
            id=ItemId("dsn", "classifier.topic", 1),
            description="The classifier classifies topics.",
            rationale=None,
            comment=None,
            covers=[],
            depends=[],
            needs=[],
            tags=[],
            interface=[],
            agent_review=[],
        )
    ]
