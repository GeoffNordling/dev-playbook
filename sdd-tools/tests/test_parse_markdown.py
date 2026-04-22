"""Tests for sdd_tools.parse.markdown."""

from __future__ import annotations

from pathlib import Path

from sdd_tools.parse.markdown import parse_text


def _parse(text: str) -> object:
    return parse_text(text, Path("s.md"))


class TestSectionSplitting:
    def test_no_headers_single_preamble(self):
        text = "Intro text.\n"
        sf = _parse(text)
        assert len(sf.sections) == 1
        assert sf.sections[0].header is None
        assert sf.sections[0].header_line is None

    def test_four_dimension_headers(self):
        text = (
            "Intro.\n\n"
            "## Data\n\n"
            "## API Shape\n\n"
            "## Algorithms\n\n"
            "## Composition\n"
        )
        sf = _parse(text)
        headers = [s.header for s in sf.sections]
        assert headers == [None, "Data", "API Shape", "Algorithms", "Composition"]
        assert sf.sections[1].is_dimension
        assert sf.sections[1].header_line == 3

    def test_h3_not_a_section(self):
        text = "## Data\n\n### Not a section\nBody.\n"
        sf = _parse(text)
        assert [s.header for s in sf.sections] == [None, "Data"]


class TestItemBasic:
    def test_single_item_with_title(self):
        text = (
            "### Login Validation\n"
            "`req~auth.login~1`\n"
            "Status: approved\n"
            "\n"
            "When the user submits credentials, the system `SHALL` verify.\n"
        )
        sf = _parse(text)
        items = sf.all_items()
        assert len(items) == 1
        item = items[0]
        assert item.id == "req~auth.login~1"
        assert item.doctype == "req"
        assert item.name == "auth.login"
        assert item.revision == 1
        assert item.title == "Login Validation"
        assert item.status == "approved"
        assert item.source_line == 2
        assert "submits credentials" in item.description

    def test_item_without_heading(self):
        text = "`req~foo~1`\nStatus: draft\n\nBody.\n"
        sf = _parse(text)
        item = sf.all_items()[0]
        assert item.title == ""
        assert item.status == "draft"
        assert "Body" in item.description


class TestKeywordFields:
    def test_covers_bullet_block(self):
        text = (
            "`req~foo~1`\n"
            "Status: draft\n"
            "Covers:\n"
            "- feat~a~1\n"
            "- feat~b~2\n"
            "\n"
            "Needs: dsn, utest\n"
        )
        item = _parse(text).all_items()[0]
        assert item.covers == ["feat~a~1", "feat~b~2"]
        assert item.needs == ["dsn", "utest"]

    def test_rationale(self):
        text = (
            "`req~foo~1`\n"
            "Status: draft\n"
            "\n"
            "Body prose.\n"
            "\n"
            "Rationale:\n"
            "Because it matters.\n"
        )
        item = _parse(text).all_items()[0]
        assert item.rationale == "Because it matters."
        assert "Body prose" in item.description

    def test_interface_repeatable(self):
        text = (
            "`dsn~p~1`\n"
            "Status: approved\n"
            "Interface: mod.func(x: int) -> str\n"
            "Interface: mod.Klass.m(self, y: int) -> None\n"
        )
        item = _parse(text).all_items()[0]
        assert item.interfaces == [
            "mod.func(x: int) -> str",
            "mod.Klass.m(self, y: int) -> None",
        ]

    def test_agent_review_single_line(self):
        text = (
            "`dsn~p~1`\n"
            "Status: approved\n"
            "AgentReview: The prompt at src/prompts/agent.md should discourage filler.\n"
        )
        item = _parse(text).all_items()[0]
        assert len(item.agent_reviews) == 1
        assert "should discourage filler" in item.agent_reviews[0]

    def test_agent_review_multiline_continuation(self):
        text = (
            "`dsn~p~1`\n"
            "Status: approved\n"
            "AgentReview: The prompt at src/prompts/agent.md should contain\n"
            "             a directive discouraging filler or polite conversation.\n"
        )
        item = _parse(text).all_items()[0]
        assert len(item.agent_reviews) == 1
        assert "a directive discouraging" in item.agent_reviews[0]

    def test_agent_review_repeatable(self):
        text = (
            "`dsn~p~1`\n"
            "Status: approved\n"
            "AgentReview: First check.\n"
            "AgentReview: Second check.\n"
        )
        item = _parse(text).all_items()[0]
        assert item.agent_reviews == ["First check.", "Second check."]

    def test_needs_multiple_items_from_dsn_and_interface(self):
        """Needs:, Interface:, AgentReview: can coexist on a dsn."""
        text = (
            "`dsn~p~1`\n"
            "Status: approved\n"
            "Needs: utest\n"
            "Interface: mod.f() -> None\n"
            "AgentReview: something.\n"
        )
        item = _parse(text).all_items()[0]
        assert item.needs == ["utest"]
        assert item.interfaces == ["mod.f() -> None"]
        assert item.agent_reviews == ["something."]


class TestItemBoundaries:
    def test_hrule_separated(self):
        text = (
            "### Item 1\n"
            "`req~a~1`\n"
            "Status: draft\n"
            "\n"
            "Body 1.\n"
            "\n"
            "---\n"
            "\n"
            "### Item 2\n"
            "`req~b~1`\n"
            "Status: draft\n"
            "\n"
            "Body 2.\n"
        )
        items = _parse(text).all_items()
        assert [it.id for it in items] == ["req~a~1", "req~b~1"]
        assert "Body 1" in items[0].description
        assert "Body 2" in items[1].description
        assert "Body 2" not in items[0].description

    def test_heading_separated_no_hrule(self):
        text = (
            "### Item 1\n"
            "`req~a~1`\n"
            "Status: draft\n"
            "\n"
            "Body 1.\n"
            "\n"
            "### Item 2\n"
            "`req~b~1`\n"
            "Status: draft\n"
            "\n"
            "Body 2.\n"
        )
        items = _parse(text).all_items()
        assert [it.id for it in items] == ["req~a~1", "req~b~1"]
        assert "Body 1" in items[0].description
        assert "Body 2" not in items[0].description

    def test_h2_boundary_ends_item(self):
        text = (
            "## Data\n"
            "### Item 1\n"
            "`dsn~a~1`\n"
            "Status: approved\n"
            "\n"
            "Body in Data.\n"
            "\n"
            "## API Shape\n"
            "### Item 2\n"
            "`dsn~b~1`\n"
            "Status: approved\n"
            "\n"
            "Body in API Shape.\n"
        )
        sf = _parse(text)
        data_section = next(s for s in sf.sections if s.header == "Data")
        api_section = next(s for s in sf.sections if s.header == "API Shape")
        assert len(data_section.items) == 1
        assert len(api_section.items) == 1
        assert data_section.items[0].id == "dsn~a~1"
        assert api_section.items[0].id == "dsn~b~1"
        assert "API Shape" not in data_section.items[0].description


class TestOftOffBlocks:
    def test_oft_off_suppresses_items(self):
        text = (
            "<!-- oft:off -->\n"
            "`req~ghost~1`\n"
            "Status: approved\n"
            "<!-- oft:on -->\n"
            "`req~real~1`\n"
            "Status: approved\n"
        )
        items = _parse(text).all_items()
        assert [it.id for it in items] == ["req~real~1"]

    def test_line_numbers_stay_aligned(self):
        text = (
            "<!-- oft:off -->\n"
            "ignored\n"
            "<!-- oft:on -->\n"
            "`req~real~1`\n"
            "Status: approved\n"
        )
        item = _parse(text).all_items()[0]
        assert item.source_line == 4


class TestSourceLine:
    def test_source_line_is_id_line(self):
        text = "# Header\n\n### Title\n`req~x~1`\nStatus: draft\n"
        item = _parse(text).all_items()[0]
        assert item.source_line == 4

    def test_source_line_in_later_section(self):
        text = (
            "## Data\n"
            "\n"
            "### First\n"
            "`dsn~a~1`\n"
            "Status: approved\n"
            "\n"
            "## API Shape\n"
            "\n"
            "### Second\n"
            "`dsn~b~1`\n"
            "Status: approved\n"
        )
        items = _parse(text).all_items()
        assert items[0].source_line == 4
        assert items[1].source_line == 10


class TestEmptyDimensions:
    def test_empty_dimension_section_preserved(self):
        text = (
            "## Data\n"
            "\n"
            "### Only Item\n"
            "`dsn~x~1`\n"
            "Status: approved\n"
            "Body.\n"
            "\n"
            "## API Shape\n"
            "\n"
            "## Algorithms\n"
            "\n"
            "## Composition\n"
        )
        sf = _parse(text)
        api = next(s for s in sf.sections if s.header == "API Shape")
        algo = next(s for s in sf.sections if s.header == "Algorithms")
        comp = next(s for s in sf.sections if s.header == "Composition")
        assert api.items == []
        assert algo.items == []
        assert comp.items == []
