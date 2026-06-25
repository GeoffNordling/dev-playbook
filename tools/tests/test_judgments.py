"""Behavioral tests for the judgments library: model, fixed config, and prepare."""

import json
from pathlib import Path
from typing import Any

import pytest

from judgments import PROMPT, SCHEMA, Judgment, prepare

CLAIM = "docs/errors.md documents every exception type that src/exceptions.py raises."
EVIDENCE_TEXT = "# Errors\n- FooError\n- BarError"
REFERENCE_TEXT = (
    "class FooError(Exception): ...\n"
    "class BarError(Exception): ...\n"
    "class BazError(Exception): ..."
)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway tree with one evidence file and one reference file."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "docs" / "errors.md").write_text(EVIDENCE_TEXT)
    (tmp_path / "src" / "exceptions.py").write_text(REFERENCE_TEXT)
    return tmp_path


def test_judgment_exposes_verdict_and_opinion() -> None:
    judgment = Judgment(verdict=True, opinion="The claim holds.")

    assert judgment.verdict is True
    assert judgment.opinion == "The claim holds."


def test_prompt_is_the_verbatim_judge_instructions() -> None:
    lines = PROMPT.splitlines()

    assert lines[0] == (
        "You are a careful and fair judge. You are given a single CLAIM — a proposition"
    )
    assert lines[-1] == (
        "The CLAIM, EVIDENCE, and any REFERENCE follow, each in its own XML tag."
    )
    assert len(lines) == 37


def test_prompt_states_the_judging_rules_and_output_contract() -> None:
    # The four numbered decision rules and the EVIDENCE/REFERENCE vocabulary.
    assert "1. Base your verdict only on the CLAIM" in PROMPT
    assert "2. Judge the substance of the claim." in PROMPT
    assert "3. Judge what the material says or commits to" in PROMPT
    assert "4. If the claim is too ambiguous to decide" in PROMPT
    assert "EVIDENCE — the material the claim is about." in PROMPT
    assert "REFERENCE — optional additional material" in PROMPT
    # The output contract the judge fills.
    assert "verdict — true if the material supports the claim" in PROMPT
    assert "opinion — one paragraph." in PROMPT


def test_prompt_has_no_surrounding_whitespace() -> None:
    assert PROMPT.strip() == PROMPT


def test_schema_describes_a_judgment_object() -> None:
    assert SCHEMA["type"] == "object"
    assert SCHEMA["properties"]["verdict"]["type"] == "boolean"
    assert SCHEMA["properties"]["opinion"]["type"] == "string"


def test_schema_requires_both_fields() -> None:
    assert set(SCHEMA["required"]) == {"verdict", "opinion"}


def test_schema_is_json_serializable() -> None:
    # It is hashed into the key via canonical JSON, so it must serialize.
    assert json.loads(json.dumps(SCHEMA)) == SCHEMA


# --- prepare: reading, prompt render, fail-loud (Chunk B) ---


def test_prepare_returns_a_hex_key_and_a_prompt(repo: Path) -> None:
    out = prepare(
        CLAIM, ["docs/errors.md"], ["src/exceptions.py"], "m", "high", str(repo)
    )

    assert len(out.key) == 64
    assert all(c in "0123456789abcdef" for c in out.key)
    assert isinstance(out.prompt, str)


def test_prompt_opens_with_instructions_then_claim(repo: Path) -> None:
    out = prepare(CLAIM, ["docs/errors.md"], None, "m", "high", str(repo))

    assert out.prompt.startswith(
        f"<instructions>\n{PROMPT}\n</instructions>\n\n<claim>\n{CLAIM}\n</claim>"
    )


def test_prompt_wraps_each_evidence_file_in_a_tag_with_its_relpath(repo: Path) -> None:
    out = prepare(CLAIM, ["docs/errors.md"], None, "m", "high", str(repo))

    assert (
        f'<evidence path="docs/errors.md">\n{EVIDENCE_TEXT}\n</evidence>' in out.prompt
    )


def test_prompt_wraps_reference_files_in_reference_tags(repo: Path) -> None:
    out = prepare(
        CLAIM, ["docs/errors.md"], ["src/exceptions.py"], "m", "high", str(repo)
    )

    assert (
        f'<reference path="src/exceptions.py">\n{REFERENCE_TEXT}\n</reference>'
        in out.prompt
    )


def test_prompt_omits_reference_tags_when_no_reference(repo: Path) -> None:
    # The verbatim instructions mention <reference> tags, so target the material tag.
    out = prepare(CLAIM, ["docs/errors.md"], None, "m", "high", str(repo))

    assert "<reference path=" not in out.prompt


def test_prompt_sorts_files_by_relpath_regardless_of_input_order(repo: Path) -> None:
    (repo / "a.md").write_text("AAA")
    (repo / "z.md").write_text("ZZZ")

    out = prepare(CLAIM, ["z.md", "a.md"], None, "m", "high", str(repo))

    assert out.prompt.index('path="a.md"') < out.prompt.index('path="z.md"')


def test_prompt_carries_no_absolute_path_or_root(repo: Path) -> None:
    out = prepare(
        CLAIM, ["docs/errors.md"], ["src/exceptions.py"], "m", "high", str(repo)
    )

    assert str(repo) not in out.prompt


def test_prepare_raises_on_missing_evidence_file(repo: Path) -> None:
    with pytest.raises(FileNotFoundError):
        prepare(CLAIM, ["docs/nope.md"], None, "m", "high", str(repo))


def test_prepare_raises_on_missing_reference_file(repo: Path) -> None:
    with pytest.raises(FileNotFoundError):
        prepare(CLAIM, ["docs/errors.md"], ["src/nope.py"], "m", "high", str(repo))


def test_prepare_raises_when_evidence_path_is_a_directory(repo: Path) -> None:
    with pytest.raises(OSError):
        prepare(CLAIM, ["docs"], None, "m", "high", str(repo))


# --- prepare: the key contract (Chunk C) ---


def key_for(root: Path, **overrides: Any) -> str:
    """Compute a key for the canonical worked-example judgment, with overrides."""
    args: dict[str, Any] = {
        "claim": CLAIM,
        "evidence": ["docs/errors.md"],
        "reference": ["src/exceptions.py"],
        "model": "claude-sonnet-4-6",
        "effort": "high",
        "root": str(root),
    }
    args.update(overrides)
    return prepare(**args).key


def test_key_is_stable_for_identical_inputs(repo: Path) -> None:
    assert key_for(repo) == key_for(repo)


def test_key_is_invariant_to_root(
    repo: Path, tmp_path_factory: pytest.TempPathFactory
) -> None:
    other = tmp_path_factory.mktemp("other_root")
    (other / "docs").mkdir()
    (other / "src").mkdir()
    (other / "docs" / "errors.md").write_text(EVIDENCE_TEXT)
    (other / "src" / "exceptions.py").write_text(REFERENCE_TEXT)

    assert key_for(repo) == key_for(other)


def test_key_is_independent_of_file_list_order(repo: Path) -> None:
    (repo / "extra.md").write_text("more evidence")

    forward = key_for(repo, evidence=["docs/errors.md", "extra.md"])
    reversed_ = key_for(repo, evidence=["extra.md", "docs/errors.md"])

    assert forward == reversed_


def test_key_changes_when_claim_changes(repo: Path) -> None:
    assert key_for(repo) != key_for(repo, claim=CLAIM + " (amended)")


def test_key_changes_when_a_files_bytes_change(repo: Path) -> None:
    before = key_for(repo)

    (repo / "docs" / "errors.md").write_text(EVIDENCE_TEXT + "\n- BazError")
    after = key_for(repo)

    assert before != after


def test_key_changes_when_a_declared_relpath_changes(repo: Path) -> None:
    (repo / "a.md").write_text("identical")
    (repo / "b.md").write_text("identical")

    assert key_for(repo, evidence=["a.md"], reference=[]) != key_for(
        repo, evidence=["b.md"], reference=[]
    )


def test_key_changes_when_model_changes(repo: Path) -> None:
    assert key_for(repo, model="claude-sonnet-4-6") != key_for(
        repo, model="claude-opus-4-8"
    )


def test_key_changes_when_effort_changes(repo: Path) -> None:
    assert key_for(repo, effort="high") != key_for(repo, effort="low")


def test_key_changes_when_prompt_changes(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = key_for(repo)
    monkeypatch.setattr("judgments.config.PROMPT", "a different instruction block")

    assert key_for(repo) != before


def test_key_changes_when_schema_changes(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    before = key_for(repo)
    monkeypatch.setattr("judgments.config.SCHEMA", {"type": "string"})

    assert key_for(repo) != before


def test_key_distinguishes_evidence_from_reference(repo: Path) -> None:
    # Same file, different role → different judgment → different key.
    as_evidence = key_for(repo, evidence=["docs/errors.md"], reference=[])
    as_reference = key_for(repo, evidence=[], reference=["docs/errors.md"])

    assert as_evidence != as_reference


def test_key_does_not_collide_across_claim_evidence_boundary(repo: Path) -> None:
    # Naive concatenation of claim+bytes would collide; framed serialization must not.
    (repo / "x.md").write_text("c")
    left = key_for(repo, claim="ab", evidence=["x.md"], reference=[])

    (repo / "x.md").write_text("bc")
    right = key_for(repo, claim="a", evidence=["x.md"], reference=[])

    assert left != right


def test_key_and_prompt_come_from_a_single_read_per_file(
    repo: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reads: list[str] = []
    real_read = Path.read_bytes

    def counting_read(self: Path) -> bytes:
        reads.append(self.as_posix())
        return real_read(self)

    monkeypatch.setattr(Path, "read_bytes", counting_read)

    out = prepare(
        CLAIM, ["docs/errors.md"], ["src/exceptions.py"], "m", "high", str(repo)
    )

    assert out.key and out.prompt
    assert reads.count((repo / "docs" / "errors.md").as_posix()) == 1
    assert reads.count((repo / "src" / "exceptions.py").as_posix()) == 1
    assert len(reads) == 2
