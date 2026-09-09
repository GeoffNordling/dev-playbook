import json
from pathlib import Path
from typing import Any

import pytest

from dev_playbook.cloa_viewer import state


def an_envelope() -> dict[str, Any]:
    """One well-formed envelope, as a generator would build it."""
    return state.envelope(
        "index-tree",
        1,
        "Index tree",
        None,
        {},
        commit="46321be7c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
        generator="dev_playbook.cloa_viewer.kinds.index_tree",
    )


def test_state_root_follows_xdg_state_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert state.state_root() == tmp_path / "cloa-viewer"


def test_state_root_falls_back_to_local_state(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: Path("/home/someone"))
    assert state.state_root() == Path("/home/someone/.local/state/cloa-viewer")


def test_checkout_dir_starts_with_the_checkout_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    directory = state.checkout_dir(tmp_path / "main" / "dev-playbook")
    assert directory.parent == tmp_path / "cloa-viewer"
    assert directory.name.startswith("dev-playbook-")


def test_checkout_dir_separates_two_paths_sharing_a_basename(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    main = state.checkout_dir(tmp_path / "main" / "dev-playbook")
    worktree = state.checkout_dir(tmp_path / "worktrees" / "dev-playbook")
    assert main != worktree


def test_envelope_carries_the_seven_fields() -> None:
    built = an_envelope()
    del built["stamp"]["generated_at"]
    assert built == {
        "envelope": 1,
        "kind": "index-tree",
        "kind_version": 1,
        "title": "Index tree",
        "subject": None,
        "stamp": {
            "commit": "46321be7c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
            "generator": "dev_playbook.cloa_viewer.kinds.index_tree",
        },
        "payload": {},
    }


def test_envelope_generated_at_ends_in_z() -> None:
    assert an_envelope()["stamp"]["generated_at"].endswith("Z")


def test_load_schema_reads_the_envelope_schema() -> None:
    schema = state.load_schema("envelope")
    assert schema["required"] == [
        "envelope",
        "kind",
        "kind_version",
        "title",
        "subject",
        "stamp",
        "payload",
    ]


def test_a_built_envelope_validates() -> None:
    state.validate(an_envelope(), state.load_schema("envelope"))


def test_an_extra_top_level_key_names_the_root() -> None:
    instance = an_envelope()
    instance["checkout"] = "/home/someone/dev-playbook"
    with pytest.raises(state.ContractError) as raised:
        state.validate(instance, state.load_schema("envelope"))
    assert str(raised.value).startswith("$: ")


def test_a_missing_field_raises() -> None:
    instance = an_envelope()
    del instance["payload"]
    with pytest.raises(state.ContractError):
        state.validate(instance, state.load_schema("envelope"))


def test_a_bad_kind_name_names_the_field() -> None:
    instance = an_envelope()
    instance["kind"] = "Index Tree"
    with pytest.raises(state.ContractError) as raised:
        state.validate(instance, state.load_schema("envelope"))
    assert str(raised.value).startswith("$.kind: ")


def test_write_json_creates_parents_and_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "checkout" / "markdown-file" / "alpha.md.json"
    state.write_json(path, {"kind": "markdown-file"})
    assert json.loads(path.read_text()) == {"kind": "markdown-file"}


def test_write_json_leaves_no_staging_file(tmp_path: Path) -> None:
    path = tmp_path / "index-tree.json"
    state.write_json(path, {"kind": "index-tree"})
    assert sorted(p.name for p in tmp_path.iterdir()) == ["index-tree.json"]
