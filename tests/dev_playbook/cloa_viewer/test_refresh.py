import json
from pathlib import Path
from typing import Any

import pytest
from cloa_viewer_fixtures import build_checkout

from dev_playbook.cloa_viewer import refresh, registry, state
from dev_playbook.cloa_viewer.entry import Kind, View
from dev_playbook.cloa_viewer.kinds import index_tree


@pytest.fixture
def checkout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    return build_checkout(tmp_path)


def breaking_generate(checkout: Path) -> list[View]:
    """Stand in for a kind whose generator raises part way through."""
    raise RuntimeError("the generator broke")


def bad_payload_generate(checkout: Path) -> list[View]:
    """Stand in for a kind whose view breaks its own payload schema."""
    return [
        View(
            relpath="index-tree.json",
            envelope=state.envelope(
                "index-tree",
                1,
                "Index tree",
                None,
                {"root": {}, "unindexed": []},
                commit="46321be7c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
                generator="tests.dev_playbook.cloa_viewer.test_refresh",
            ),
        )
    ]


def view_at(directory: Path, relpath: str) -> dict[str, Any]:
    """The view file at ``relpath``; raises unless it matches the envelope schema."""
    view: dict[str, Any] = json.loads((directory / relpath).read_text())
    state.validate(view, state.load_schema("envelope"))
    return view


def test_refresh_writes_the_per_checkout_kinds_one_file(checkout: Path) -> None:
    refresh.refresh(checkout)
    view = view_at(state.checkout_dir(checkout), "index-tree.json")
    assert (view["kind"], view["subject"]) == ("index-tree", None)


def test_refresh_writes_one_file_per_subject(checkout: Path) -> None:
    refresh.refresh(checkout)
    view = view_at(state.checkout_dir(checkout), "markdown-file/alpha.md.json")
    assert (view["kind"], view["subject"]) == ("markdown-file", "alpha.md")


def test_the_record_names_every_generator_and_what_it_wrote(checkout: Path) -> None:
    record = refresh.refresh(checkout)
    assert record["generators"] == [
        {"kind": "index-tree", "status": "ok", "count": 1, "error": None},
        {"kind": "markdown-file", "status": "ok", "count": 7, "error": None},
    ]


def test_the_record_stamps_the_head_commit(checkout: Path) -> None:
    record = refresh.refresh(checkout)
    assert record["commit"] == state.head_commit(checkout)


def test_the_record_lands_on_disk_and_matches_its_schema(checkout: Path) -> None:
    record = refresh.refresh(checkout)
    written = json.loads((state.checkout_dir(checkout) / "refresh.json").read_text())
    state.validate(written, state.load_schema("refresh"))
    assert written == record


def test_refresh_writes_the_checkouts_facts(checkout: Path) -> None:
    refresh.refresh(checkout)
    facts = json.loads((state.checkout_dir(checkout) / "checkout.json").read_text())
    assert facts["path"] == str(checkout.resolve())


def test_refresh_leaves_no_staging_directory(checkout: Path) -> None:
    refresh.refresh(checkout)
    assert not (state.checkout_dir(checkout) / ".staging").exists()


def test_a_raising_generator_is_named_in_the_record(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    broken = Kind(
        name="broken", version=1, per_subject=False, generate=breaking_generate
    )
    monkeypatch.setattr(registry, "KINDS", (index_tree.KIND, broken))
    record = refresh.refresh(checkout)
    assert record["generators"][0] == {
        "kind": "index-tree",
        "status": "ok",
        "count": 1,
        "error": None,
    }
    assert record["generators"][1]["status"] == "failed"
    assert record["generators"][1]["count"] == 0
    assert "the generator broke" in record["generators"][1]["error"]


def test_a_failed_generator_leaves_no_staging_directory(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    broken = Kind(
        name="broken", version=1, per_subject=False, generate=breaking_generate
    )
    monkeypatch.setattr(registry, "KINDS", (broken,))
    refresh.refresh(checkout)
    assert not (state.checkout_dir(checkout) / ".staging").exists()


def test_a_failed_generator_leaves_its_last_good_files_alone(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    refresh.refresh(checkout)
    written = state.checkout_dir(checkout) / "markdown-file" / "alpha.md.json"
    before = written.read_text()
    broken = Kind(
        name="markdown-file", version=1, per_subject=True, generate=breaking_generate
    )
    monkeypatch.setattr(registry, "KINDS", (broken,))
    record = refresh.refresh(checkout)
    assert record["generators"][0]["status"] == "failed"
    assert written.read_text() == before


def test_a_view_failing_its_payload_schema_is_never_written(
    checkout: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    invalid = Kind(
        name="index-tree", version=1, per_subject=False, generate=bad_payload_generate
    )
    monkeypatch.setattr(registry, "KINDS", (invalid,))
    record = refresh.refresh(checkout)
    assert record["generators"][0]["status"] == "failed"
    assert "$.root" in record["generators"][0]["error"]
    assert not (state.checkout_dir(checkout) / "index-tree.json").exists()
