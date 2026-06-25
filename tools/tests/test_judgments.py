"""Behavioral tests for the judgments library: model, fixed config, and prepare."""

import json

from judgments import PROMPT, SCHEMA, Judgment


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
