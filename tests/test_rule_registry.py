"""Drift guard: every detector's finding carriers reference a rule-id constant.

Each detector hand-maintains a ``RULES`` tuple that ``--list-rules`` prints, and
the standards-audit slice will consume ``--list-rules`` as ground truth for the
card->rule matrix. If an emission site passed a raw string literal, ``RULES``
could silently drift from what the detector actually emits. This walks each
detector's AST and asserts every finding-carrier construction passes its rule
argument as a name reference (a module-level constant), never a string literal.
``None`` -- a workspace-audit informational ``Line`` with no rule id -- is fine.
"""

import ast
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
SRC = REPO_ROOT / "src"

# (source file, finding-carrier class name, 0-based position of the rule arg).
CARRIERS = [
    (SCRIPTS / "okf-audit", "Finding", 1),
    (SCRIPTS / "python-audit", "Finding", 2),
    (SCRIPTS / "repo-audit", "Finding", 1),
    (SCRIPTS / "skill-audit", "Finding", 1),
    (SCRIPTS / "workspace-audit", "Line", 1),
    (SRC / "dev_playbook" / "judgments" / "loader.py", "LintFinding", 1),
]


def _rule_args(source: Path, class_name: str, rule_pos: int) -> list[ast.expr]:
    """The rule-position argument of every ``class_name(...)`` construction."""
    tree = ast.parse(source.read_text(encoding="utf-8"))
    args: list[ast.expr] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == class_name
        ):
            assert len(node.args) > rule_pos, (
                f"{source.name}: {class_name}(...) at line {node.lineno} does not "
                "pass the rule argument positionally"
            )
            args.append(node.args[rule_pos])
    return args


@pytest.mark.parametrize(
    ("source", "class_name", "rule_pos"),
    CARRIERS,
    ids=[source.name for source, _, _ in CARRIERS],
)
def test_every_finding_carrier_references_a_rule_constant_not_a_literal(
    source: Path, class_name: str, rule_pos: int
) -> None:
    rule_args = _rule_args(source, class_name, rule_pos)

    assert rule_args, f"{source.name}: found no {class_name}(...) constructions"
    for arg in rule_args:
        # A name reference (a module-level rule-id constant) is required; None --
        # an informational Line with no rule id -- is allowed; a string literal is
        # the drift this guard forbids.
        is_name = isinstance(arg, ast.Name)
        is_none = isinstance(arg, ast.Constant) and arg.value is None
        assert is_name or is_none, (
            f"{source.name}: {class_name}(...) at line {arg.lineno} passes a raw "
            f"rule literal ({ast.dump(arg)}); reference a module-level constant"
        )
