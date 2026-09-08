from pathlib import Path
from typing import Any

import pytest
from cloa_viewer_fixtures import build_checkout
from conftest import commit_all, init_repo

from dev_playbook.cloa_viewer import state
from dev_playbook.cloa_viewer.kinds import markdown_file


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    return build_checkout(tmp_path)


@pytest.fixture
def link_shapes(tmp_path: Path) -> dict[str, Any]:
    """Payloads for a repo whose one document links every way a link can go."""
    repo = tmp_path / "links"
    init_repo(repo)
    (repo / "notes.md").write_text(
        "# Notes\n"
        "\n"
        "[site](https://example.com) [mail](mailto:a@b.c) [above](#notes) "
        "[partner](partner.md) [gone](other.md)\n"
    )
    (repo / "partner.md").write_text("# Partner\n")
    commit_all(repo)
    return payloads_of(repo)


def payloads_of(checkout: Path) -> dict[str, Any]:
    """Every view's payload, keyed by the identity that view describes."""
    return {
        view.envelope["subject"]: view.envelope["payload"]
        for view in markdown_file.generate(checkout)
    }


def envelope_of(checkout: Path, identity: str) -> dict[str, Any]:
    """The whole view file describing ``identity``."""
    for view in markdown_file.generate(checkout):
        if view.envelope["subject"] == identity:
            envelope: dict[str, Any] = view.envelope
            return envelope
    raise AssertionError(f"no view for {identity}")


def test_the_kind_writes_one_view_per_markdown_file(checkout: Path) -> None:
    assert [view.relpath for view in markdown_file.generate(checkout)] == [
        "markdown-file/alpha.md.json",
        "markdown-file/docs/beta.md.json",
        "markdown-file/docs/index.md.json",
        "markdown-file/index.md.json",
        "markdown-file/orphan.md.json",
    ]


def test_every_envelope_validates(checkout: Path) -> None:
    schema = state.load_schema("envelope")
    for view in markdown_file.generate(checkout):
        state.validate(view.envelope, schema)


def test_every_payload_validates(checkout: Path) -> None:
    schema = state.load_schema("markdown-file")
    for payload in payloads_of(checkout).values():
        state.validate(payload, schema)


def test_the_envelope_names_the_file_it_describes(checkout: Path) -> None:
    envelope = envelope_of(checkout, "alpha.md")
    assert envelope["kind"] == "markdown-file"
    assert envelope["kind_version"] == 1
    assert envelope["title"] == "Alpha"
    assert envelope["subject"] == "alpha.md"


def test_a_file_with_no_frontmatter_is_titled_by_its_identity(checkout: Path) -> None:
    assert envelope_of(checkout, "orphan.md")["title"] == "orphan.md"


def test_a_heading_carries_its_level_text_and_slug(checkout: Path) -> None:
    assert payloads_of(checkout)["alpha.md"]["headings"] == [
        {"level": 1, "text": "Alpha", "slug": "alpha"},
        {"level": 2, "text": "Second heading", "slug": "second-heading"},
    ]


def test_a_link_out_is_ok_when_the_checkout_holds_its_target(checkout: Path) -> None:
    assert payloads_of(checkout)["alpha.md"]["links_out"] == [
        {"target": "/docs/beta.md", "status": "ok", "identity": "docs/beta.md"},
        {"target": "/missing.md", "status": "broken", "identity": "missing.md"},
        {
            "target": "~/workspace/fixture/docs/beta.md#beta",
            "status": "ok",
            "identity": "docs/beta.md",
        },
        {
            "target": "~/workspace/elsewhere/notes.md",
            "status": "citation",
            "identity": None,
        },
    ]


def test_links_in_lists_every_other_file_that_links_here(checkout: Path) -> None:
    assert payloads_of(checkout)["docs/beta.md"]["links_in"] == [
        "alpha.md",
        "docs/index.md",
    ]


def test_a_file_nothing_links_to_has_no_links_in(checkout: Path) -> None:
    assert payloads_of(checkout)["orphan.md"]["links_in"] == []


def test_a_file_with_no_frontmatter_has_null_facts(checkout: Path) -> None:
    orphan = payloads_of(checkout)["orphan.md"]
    assert (orphan["type"], orphan["title"], orphan["description"]) == (
        None,
        None,
        None,
    )
    assert orphan["words"] == 4


def test_the_source_is_the_file_as_written(checkout: Path) -> None:
    payloads = payloads_of(checkout)
    assert payloads["orphan.md"]["source"] == "# Orphan\n\nSeven eight.\n"
    assert payloads["alpha.md"]["source"].startswith("---\ntype: Guide\n")


def test_a_link_off_the_checkout_or_back_to_the_file_is_not_broken(
    link_shapes: dict[str, Any],
) -> None:
    assert link_shapes["notes.md"]["links_out"] == [
        {"target": "https://example.com", "status": "external", "identity": None},
        {"target": "mailto:a@b.c", "status": "external", "identity": None},
        {"target": "#notes", "status": "ok", "identity": "notes.md"},
        {"target": "partner.md", "status": "ok", "identity": "partner.md"},
        {"target": "other.md", "status": "broken", "identity": "other.md"},
    ]


def test_a_files_own_anchor_is_not_a_link_in(link_shapes: dict[str, Any]) -> None:
    assert link_shapes["notes.md"]["links_in"] == []
    assert link_shapes["partner.md"]["links_in"] == ["notes.md"]
