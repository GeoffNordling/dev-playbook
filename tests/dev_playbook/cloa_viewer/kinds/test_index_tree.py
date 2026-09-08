from pathlib import Path
from typing import Any

import pytest
from cloa_viewer_fixtures import build_checkout
from conftest import commit_all, init_repo

from dev_playbook.cloa_viewer import state
from dev_playbook.cloa_viewer.kinds import index_tree


@pytest.fixture
def checkout(tmp_path: Path) -> Path:
    return build_checkout(tmp_path)


def payload_of(checkout: Path) -> dict[str, Any]:
    """The one view file's payload, the tree itself."""
    payload: dict[str, Any] = index_tree.generate(checkout)[0].envelope["payload"]
    return payload


def test_the_kind_writes_one_view_at_index_tree_json(checkout: Path) -> None:
    assert [view.relpath for view in index_tree.generate(checkout)] == [
        "index-tree.json"
    ]


def test_the_envelope_validates(checkout: Path) -> None:
    state.validate(
        index_tree.generate(checkout)[0].envelope, state.load_schema("envelope")
    )


def test_the_envelope_names_the_kind_and_no_subject(checkout: Path) -> None:
    envelope = index_tree.generate(checkout)[0].envelope
    assert envelope["kind"] == "index-tree"
    assert envelope["kind_version"] == 1
    assert envelope["title"] == "Index tree"
    assert envelope["subject"] is None


def test_the_payload_validates(checkout: Path) -> None:
    state.validate(payload_of(checkout), state.load_schema("index-tree"))


def test_the_root_holds_its_own_index_then_its_listing(checkout: Path) -> None:
    root = payload_of(checkout)["root"]
    assert [child["identity"] for child in root["children"]] == [
        "index.md",
        "alpha.md",
        "docs/",
    ]


def test_the_root_takes_its_title_and_first_sentence_from_its_index(
    checkout: Path,
) -> None:
    root = payload_of(checkout)["root"]
    assert root["identity"] == ""
    assert root["title"] == "Fixture — index"
    assert root["description"] == "The fixture bundle"


def test_a_file_row_carries_its_frontmatter(checkout: Path) -> None:
    alpha = payload_of(checkout)["root"]["children"][1]
    assert alpha == {
        "identity": "alpha.md",
        "type": "Guide",
        "title": "Alpha",
        "description": "The alpha document",
        "exists": True,
    }


def test_a_file_with_no_frontmatter_has_null_facts(checkout: Path) -> None:
    index = payload_of(checkout)["root"]["children"][0]
    assert index == {
        "identity": "index.md",
        "type": None,
        "title": None,
        "description": None,
        "exists": True,
    }


def test_a_directory_lists_its_own_index_then_its_listing(checkout: Path) -> None:
    docs = payload_of(checkout)["root"]["children"][2]
    assert docs["title"] == "docs — index"
    assert [child["identity"] for child in docs["children"]] == [
        "docs/index.md",
        "docs/beta.md",
        "docs/decisions/",
    ]


def test_a_file_no_index_reaches_is_unindexed(checkout: Path) -> None:
    unindexed = payload_of(checkout)["unindexed"]
    assert [node["identity"] for node in unindexed] == ["orphan.md"]


def test_a_listed_file_the_checkout_lacks_is_flagged_missing(tmp_path: Path) -> None:
    repo = tmp_path / "gap"
    init_repo(repo)
    (repo / "index.md").write_text(
        "# Gap — index\n\nThe gap.\n\n- [Gone](/gone.md) — Not on disk\n"
    )
    commit_all(repo)
    assert payload_of(repo)["root"]["children"][1] == {
        "identity": "gone.md",
        "type": None,
        "title": None,
        "description": None,
        "exists": False,
    }


def test_a_checkout_with_no_root_index_holds_every_file_as_unindexed(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "flat"
    init_repo(repo)
    (repo / "one.md").write_text("# One\n")
    (repo / "two.md").write_text("# Two\n")
    commit_all(repo)
    payload = payload_of(repo)
    assert [node["identity"] for node in payload["unindexed"]] == ["one.md", "two.md"]
    assert payload["root"] == {
        "identity": "",
        "title": "flat",
        "description": None,
        "children": [],
    }


def test_an_index_hierarchy_that_is_not_a_tree_raises(tmp_path: Path) -> None:
    repo = tmp_path / "cycle"
    init_repo(repo)
    (repo / "a").mkdir()
    (repo / "b").mkdir()
    (repo / "index.md").write_text("# Root\n\nThe root.\n\n- [a](/a/index.md) — a\n")
    (repo / "a" / "index.md").write_text("# A\n\nThe a.\n\n- [b](/b/index.md) — b\n")
    (repo / "b" / "index.md").write_text("# B\n\nThe b.\n\n- [a](/a/index.md) — a\n")
    commit_all(repo)
    with pytest.raises(ValueError, match="a/index.md is reached twice"):
        index_tree.generate(repo)
