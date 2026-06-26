"""The judgment model and the fixed judge configuration (PROMPT, SCHEMA)."""

import json
from pathlib import Path

from judgments import PROMPT, SCHEMA, Judgment

VERBATIM_PROMPT = (Path(__file__).parent / "fixtures" / "judge_prompt.txt").read_text()


def test_judgment_holds_a_verdict_and_an_opinion() -> None:
    judgment = Judgment(verdict=True, opinion="the evidence supports the claim")

    assert judgment.verdict is True
    assert judgment.opinion == "the evidence supports the claim"


def test_prompt_is_the_verbatim_judge_instructions() -> None:
    assert PROMPT == VERBATIM_PROMPT


def test_schema_declares_verdict_boolean_and_opinion_string() -> None:
    assert SCHEMA["type"] == "object"
    assert SCHEMA["properties"]["verdict"]["type"] == "boolean"
    assert SCHEMA["properties"]["opinion"]["type"] == "string"


def test_schema_requires_both_fields() -> None:
    assert set(SCHEMA["required"]) == {"verdict", "opinion"}


def test_schema_is_json_serializable() -> None:
    # SCHEMA enters the content key, so it must serialize deterministically.
    assert json.loads(json.dumps(SCHEMA)) == SCHEMA
