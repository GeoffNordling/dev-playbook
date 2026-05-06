"""Tests for spec_tools.serialize."""

import pathlib

import pytest

from spec_tools.model import ItemId, SpecItem
from spec_tools.serialize import render, write


def make_item(**overrides: object) -> SpecItem:
    """Build a SpecItem with placeholder defaults; override any field via kwargs."""
    defaults: dict[str, object] = dict(
        heading="Example",
        id=ItemId("dsn", "example", 0),
        description="An example item.",
        rationale=None,
        comment=None,
        covers=[],
        depends=[],
        needs=[],
        tags=[],
        interface=[],
        agent_review=[],
    )
    defaults.update(overrides)
    return SpecItem(**defaults)  # type: ignore[arg-type]


@pytest.mark.covers("dsn~serialize.render~0")
def test_render_minimal_item_emits_only_required_fields():
    item = make_item(
        heading="Topic Classifier",
        id=ItemId("dsn", "classifier.topic", 1),
        description="The classifier classifies topics.",
    )

    output = render([item])

    assert output == (
        "### Topic Classifier\n"
        "`dsn~classifier.topic~1`\n"
        "\n"
        "Description:\n"
        "The classifier classifies topics.\n"
    )


@pytest.mark.covers("dsn~serialize.render~0")
def test_render_fully_loaded_item_emits_all_keywords_in_canonical_order():
    item = make_item(
        heading="Heading",
        id=ItemId("dsn", "x", 0),
        description="desc.",
        rationale="rat.",
        comment="com.",
        covers=[ItemId("feat", "a", 0)],
        depends=[ItemId("dsn", "b", 1)],
        tags=["t1", "t2"],
        needs=["utest", "itest"],
        interface=["mod.f() -> None", "mod.g() -> int"],
        agent_review=["check 1", "check 2"],
    )

    output = render([item])

    assert output == (
        "### Heading\n"
        "`dsn~x~0`\n"
        "\n"
        "Description:\n"
        "desc.\n"
        "\n"
        "Rationale:\n"
        "rat.\n"
        "\n"
        "Comment:\n"
        "com.\n"
        "\n"
        "Covers:\n"
        "- feat~a~0\n"
        "\n"
        "Depends:\n"
        "- dsn~b~1\n"
        "\n"
        "Needs:\n"
        "- utest\n"
        "- itest\n"
        "\n"
        "Tags: t1, t2\n"
        "\n"
        "Interface: mod.f() -> None\n"
        "Interface: mod.g() -> int\n"
        "\n"
        "AgentReview: check 1\n"
        "AgentReview: check 2\n"
    )


@pytest.mark.covers("dsn~serialize.render~0")
def test_render_separates_multiple_items_with_blank_line():
    first = make_item(
        heading="First",
        id=ItemId("dsn", "first", 0),
        description="One.",
    )
    second = make_item(
        heading="Second",
        id=ItemId("dsn", "second", 0),
        description="Two.",
    )

    output = render([first, second])

    assert output == (
        "### First\n"
        "`dsn~first~0`\n"
        "\n"
        "Description:\n"
        "One.\n"
        "\n"
        "### Second\n"
        "`dsn~second~0`\n"
        "\n"
        "Description:\n"
        "Two.\n"
    )


@pytest.mark.covers("dsn~serialize.render~0")
def test_render_empty_list_returns_empty_string():
    assert render([]) == ""


@pytest.mark.covers("dsn~serialize.render~0")
def test_render_single_tag_emits_single_inline_entry():
    item = make_item(
        heading="One Tag",
        id=ItemId("dsn", "one-tag", 0),
        description="Body.",
        tags=["alpha"],
    )

    output = render([item])

    assert output == (
        "### One Tag\n`dsn~one-tag~0`\n\nDescription:\nBody.\n\nTags: alpha\n"
    )


@pytest.mark.covers("dsn~serialize.write~0")
def test_write_replaces_existing_file_contents(tmp_path: pathlib.Path):
    target = tmp_path / "spec.md"
    target.write_text("stale content from a previous version\n")
    items = [
        make_item(
            heading="Fresh",
            id=ItemId("dsn", "fresh", 0),
            description="Replaced.",
        )
    ]

    write(items, target)

    assert target.read_text() == render(items)


@pytest.mark.covers("dsn~serialize.write~0")
def test_write_persists_rendered_output(tmp_path: pathlib.Path):
    items = [
        make_item(
            heading="A",
            id=ItemId("dsn", "a", 0),
            description="Persisted.",
        )
    ]
    target = tmp_path / "spec.md"

    write(items, target)

    assert target.read_text() == render(items)
