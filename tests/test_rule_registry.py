"""Drift guards tying each detector's ``--list-rules`` to what it actually emits.

Each detector hand-maintains a rule-id tuple that ``--list-rules`` prints, and
the standards-audit slice will consume ``--list-rules`` as ground truth for the
card->rule matrix. Two ways the tuple could lie, each guarded here:

- **Literal drift.** An emission site could pass a raw string literal instead of
  a rule-id constant, so the tuple silently diverges from the emitted id. The
  first guard walks each detector's AST and asserts every finding-carrier
  construction passes its rule argument as a name reference (a module-level
  constant), never a string literal. ``None`` -- a workspace-audit informational
  ``Line`` with no rule id -- is fine.

- **Membership drift.** A rule-id constant could be emitted but forgotten from
  the tuple (``--list-rules`` under-reports), or listed but never emitted
  (over-reports). The second guard asserts, per detector, that the set of
  rule-id constants the module actually emits equals the set the tuple lists.

ref-audit is absent from both: its ``RULES = tuple(RULE_FOR.values())`` derives
from the emission map, so the tuple cannot drift from what it emits by
construction.
"""

import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
SRC = REPO_ROOT / "src"

# The shape of a card-namespaced rule id: ``card.rule``, lowercase words joined
# by hyphens on each side of a single dot. This distinguishes a rule-id constant
# from any other module-level string constant (messages, paths, markers).
RULE_ID = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*\.[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# (source file, finding-carrier class name, 0-based position of the rule arg).
CARRIERS = [
    (SCRIPTS / "okf-audit", "Finding", 1),
    (SCRIPTS / "python-audit", "Finding", 2),
    (SCRIPTS / "repo-audit", "Finding", 1),
    (SCRIPTS / "skill-audit", "Finding", 1),
    (SRC / "dev_playbook" / "workspace_audit.py", "Line", 1),
    (SRC / "dev_playbook" / "judgments" / "loader.py", "LintFinding", 1),
    (SRC / "dev_playbook" / "testing_audit.py", "Finding", 2),
    (SRC / "dev_playbook" / "decisions_audit.py", "Finding", 2),
]

# (source file, name of the rule-id tuple that --list-rules prints).
REGISTRIES = [
    (SCRIPTS / "okf-audit", "RULES"),
    (SCRIPTS / "python-audit", "RULES"),
    (SCRIPTS / "repo-audit", "RULES"),
    (SCRIPTS / "skill-audit", "RULES"),
    (SRC / "dev_playbook" / "workspace_audit.py", "RULES"),
    (SRC / "dev_playbook" / "judgments" / "loader.py", "JUDGMENTS_RULES"),
    (SRC / "dev_playbook" / "testing_audit.py", "RULES"),
    (SRC / "dev_playbook" / "decisions_audit.py", "RULES"),
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


def _string_constants(tree: ast.Module) -> dict[str, str]:
    """Map each module-level ``NAME = "value"`` string constant to its value."""
    consts: dict[str, str] = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    consts[target.id] = node.value.value
    return consts


def _tuple_member_names(tree: ast.Module, tuple_name: str) -> set[str]:
    """The names listed in the module-level ``tuple_name = (...)`` assignment."""
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == tuple_name for t in node.targets
        ):
            elts = getattr(node.value, "elts", [])
            return {e.id for e in elts if isinstance(e, ast.Name)}
    raise AssertionError(f"no module-level {tuple_name} tuple found")


def _call_argument_names(tree: ast.Module) -> set[str]:
    """Every name passed as a positional or keyword argument to any call.

    A rule-id constant reaches ``--list-rules``'s ground truth only by being
    emitted, i.e. passed to a finding carrier -- directly, or through a helper
    that forwards it (python-audit's private-access findings go through ``_add``,
    whose constant argument is captured here). This over-approximates emission by
    any call argument, which is exactly the rule-id constants at emission sites,
    since a rule-id constant is referenced nowhere else but the rule tuple.
    """
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for arg in (*node.args, *(kw.value for kw in node.keywords)):
                if isinstance(arg, ast.Name):
                    names.add(arg.id)
    return names


def _listed_and_emitted(tree: ast.Module, tuple_name: str) -> tuple[set[str], set[str]]:
    """The rule-id constants the tuple lists and those the module emits."""
    consts = _string_constants(tree)
    rule_constants = {n for n, v in consts.items() if RULE_ID.fullmatch(v)}
    listed = _tuple_member_names(tree, tuple_name)
    emitted = rule_constants & _call_argument_names(tree)
    return listed, emitted


@pytest.mark.parametrize(
    ("source", "tuple_name"),
    REGISTRIES,
    ids=[source.name for source, _ in REGISTRIES],
)
def test_rule_tuple_lists_exactly_the_emitted_rule_constants(
    source: Path, tuple_name: str
) -> None:
    tree = ast.parse(source.read_text(encoding="utf-8"))

    listed, emitted = _listed_and_emitted(tree, tuple_name)

    assert emitted == listed, (
        f"{source.name}: {tuple_name} (what --list-rules prints) disagrees with "
        f"the rule ids actually emitted -- listed but never emitted: "
        f"{sorted(listed - emitted)}; emitted but not listed: "
        f"{sorted(emitted - listed)}"
    )
