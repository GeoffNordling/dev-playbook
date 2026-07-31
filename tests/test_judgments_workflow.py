"""Guards the judgments workflow's mirror of the fixed judge output schema.

The workflow script pins every judge agent to a structured-output schema written
as a JavaScript literal. That schema is hashed into each judgment's content key
by ``judgments.core``, so if the two ever disagreed the cache would record passes
for a schema the judges never actually answered under -- a silent corruption no
runtime check would catch, because the Python side would go on hashing its own
constant regardless.

The mirror is deliberate: the alternative is transcribing the schema through an
LLM at dispatch time, which puts a model in the path of a key-critical value.
Duplicating it and testing the duplicate is the cheaper trade, and this is the
test that makes it safe.
"""

import json
from pathlib import Path

from dev_playbook.judgments.core import SCHEMA

WORKFLOW = (
    Path(__file__).resolve().parents[1]
    / "dotfiles"
    / "dot-claude"
    / "workflows"
    / "judgments.js"
)

DECLARATION = "const VERDICT_SCHEMA = "


def _object_literal(source: str, declaration: str) -> str:
    """The balanced ``{...}`` block that ``declaration`` assigns, as raw text.

    Scans braces rather than matching a regex so nesting is handled exactly. The
    workflow keeps this particular literal in JSON-compatible form -- quoted keys,
    no trailing commas -- so the caller can parse the returned text directly.
    """
    start = source.index(declaration) + len(declaration)
    assert source[start] == "{", "VERDICT_SCHEMA must be assigned an object literal"
    depth = 0
    for offset, character in enumerate(source[start:], start=start):
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth == 0:
                return source[start : offset + 1]
    raise AssertionError("unbalanced braces in the VERDICT_SCHEMA literal")


def test_workflow_verdict_schema_mirrors_the_python_constant() -> None:
    literal = _object_literal(WORKFLOW.read_text(encoding="utf-8"), DECLARATION)

    assert json.loads(literal) == SCHEMA


def test_workflow_dispatches_judges_without_a_path_lookup() -> None:
    # The judge prompts come from the CLI, but the workflow's own two bootstrap
    # commands are spelled here. The planner is allowed `uv run` -- it is the one
    # call that cannot yet know the absolute invocation -- while the recorder must
    # use the absolute one the CLI handed back, never a bare or `uv`-prefixed name.
    source = WORKFLOW.read_text(encoding="utf-8")

    assert "uv run judgments-run plan" in source
    assert "${plan.cli} record" in source
    assert "uv run judgments-run record" not in source
