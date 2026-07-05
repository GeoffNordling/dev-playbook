"""The judgment model and the SCHEMA structured-output contract.

PROMPT's exact text is pinned by the constant in ``dev_playbook.judgments.core`` (and the
issue brief, its source of truth); a golden copy here would only duplicate it.
Its rendered role is covered behaviorally in ``test_judgments_prepare.py``.
"""

import json

from dev_playbook.judgments.core import SCHEMA, Judgment


def test_judgment_holds_a_verdict_and_an_opinion() -> None:
    judgment = Judgment(verdict=True, opinion="the evidence supports the claim")

    assert judgment.verdict is True
    assert judgment.opinion == "the evidence supports the claim"


def test_schema_declares_verdict_boolean_and_opinion_string() -> None:
    assert SCHEMA["type"] == "object"
    assert SCHEMA["properties"]["verdict"]["type"] == "boolean"
    assert SCHEMA["properties"]["opinion"]["type"] == "string"


def test_schema_requires_both_fields() -> None:
    assert set(SCHEMA["required"]) == {"verdict", "opinion"}


def test_schema_is_json_serializable() -> None:
    # SCHEMA enters the content key, so it must serialize deterministically.
    assert json.loads(json.dumps(SCHEMA)) == SCHEMA
