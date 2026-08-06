"""Audit a repo's Python tests against the workspace testing conventions.

testing-lint is the detector behind the Python-testing card. It walks a repo's
Python files once (via dev_playbook.pyast.find_python_files, so gitignore-aware
and worktree-scoped) and applies three rules to the test files it finds:

  - **no-private-access** — a ``test_*.py`` file must not import or reach into a
    private name (``_foo``) of a non-test module; dunders are public. The
    finding message keeps the import-vs-attribute-reach distinction. Moved here
    from python-lint, whose ``privacy.*`` family answered the testing standard's
    question, not Python's.
  - **mirror-layout** — a ``test_<stem>.py`` whose stem names an existing ``src``
    module must sit at that module's literal mirror beneath ``tests/``
    (``src/x/y.py`` -> ``tests/x/test_y.py``). Test files matching no module
    (e2e suites, flattened names), ``conftest.py``, and non-``test_*`` helpers
    are outside the rule's domain. Placement only, not coverage or naming.
  - **no-logic** — no ``if``/``else`` or ``try``/``except`` statement in the body
    of a ``test_*`` function; loops, ternary expressions, and comprehension
    filters stay legal; nested helpers and module level are exempt.

See standards/testing/conventions.md for the conventions these rules enforce.

Output:
    stdout — one finding per line, ``file:line: testing.rule message``.
    stderr — one human-readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    testing-lint [directory]
    testing-lint --list-rules
"""

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import pyast
from dev_playbook.external import is_externally_managed
from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the testing card whose
# question it answers. Each id is a module-level constant so every emission site
# references the constant, never a raw literal, and RULES (what --list-rules
# prints) cannot drift from what the detector actually emits.
NO_PRIVATE_ACCESS = "testing.no-private-access"
MIRROR_LAYOUT = "testing.mirror-layout"
NO_LOGIC = "testing.no-logic"

RULES = (NO_PRIVATE_ACCESS, MIRROR_LAYOUT, NO_LOGIC)

# git ls-files already drops gitignored caches; this name filter also covers the
# rare tracked copy. A test file is scanned when none of its parent directory
# names is in this set and it is not in an externally-managed tree (that skip is
# the shared dev_playbook.external registry, adopted here to close the drift with
# python-lint and md.classify).
_CACHES = frozenset(
    {
        ".git",
        ".venv",
        ".hatch",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "node_modules",
    }
)


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a repo-relative location, a rule id, and a message."""

    file: str
    line: int | None
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message, self.line)


# --- no-private-access rule ---


def check_no_private_access(rel: str, tree: ast.Module) -> list[Finding]:
    """Private-name access from a test file into a non-test module."""
    visitor = _PrivacyVisitor(rel)
    visitor.visit(tree)
    return visitor.findings


def _is_private(name: str) -> bool:
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


def _is_test_module(module: str) -> bool:
    for segment in module.split("."):
        if segment == "tests" or segment.startswith("test_") or segment == "conftest":
            return True
    return False


def _root_name(node: ast.Attribute) -> str | None:
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        current = current.value
    return current.id if isinstance(current, ast.Name) else None


def _attribute_chain(node: ast.Attribute) -> str:
    parts: list[str] = [node.attr]
    current: ast.expr = node.value
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


class _PrivacyVisitor(ast.NodeVisitor):
    """Collect private-access findings within one test file's AST.

    Both the import reach and the attribute reach emit the one
    ``testing.no-private-access`` rule; only the message distinguishes them.
    """

    def __init__(self, rel: str) -> None:
        self.rel = rel
        self.findings: list[Finding] = []
        self._imports: dict[str, str] = {}

    def visit_Import(self, node: ast.Import) -> None:
        """Records aliases and flags private module segments in each import."""
        for alias in node.names:
            module = alias.name
            local = alias.asname or alias.name.split(".")[0]
            if not _is_test_module(module):
                self._flag_private_segments(node, module)
            self._imports[local] = module
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Flags private names (and segments) imported from a non-test module."""
        module = node.module or ""
        if module and not _is_test_module(module):
            self._flag_private_segments(node, module)
            for alias in node.names:
                if _is_private(alias.name):
                    self._add(
                        node,
                        f"imports private name '{alias.name}' from "
                        f"non-test module '{module}'",
                    )
        for alias in node.names:
            local = alias.asname or alias.name
            self._imports[local] = module
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Shadows the function name so later attribute reaches skip it."""
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Shadows the coroutine name so later attribute reaches skip it."""
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Shadows the class name so later attribute reaches skip it."""
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Shadows assigned names so later attribute reaches skip them."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._imports.setdefault(target.id, "")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Flags reaching into a private attribute of a non-test import."""
        if _is_private(node.attr):
            root = _root_name(node)
            if root is not None:
                source_module = self._imports.get(root)
                if source_module and not _is_test_module(source_module):
                    self._add(
                        node,
                        f"reaches into private name '{node.attr}' on "
                        f"non-test import '{root}' ({_attribute_chain(node)})",
                    )
        self.generic_visit(node)

    def _flag_private_segments(self, node: ast.AST, module: str) -> None:
        for segment in module.split("."):
            if _is_private(segment):
                self._add(
                    node,
                    f"imports through private module segment '{segment}' in '{module}'",
                )
                return

    def _add(self, node: ast.AST, message: str) -> None:
        self.findings.append(
            Finding(self.rel, getattr(node, "lineno", 0), NO_PRIVATE_ACCESS, message)
        )


# --- mirror-layout rule ---


def _mirror_of(src_rel: str) -> str:
    """The test path that mirrors a src module: ``src/x/y.py`` -> ``tests/x/test_y.py``."""
    below_src = Path(src_rel).relative_to("src")
    return str(Path("tests") / below_src.parent / f"test_{below_src.name}")


def src_module_mirrors(files: list[Path], root: Path) -> dict[str, set[str]]:
    """Map each src module stem to the test path(s) that mirror it.

    A src module is a non-``__init__`` ``.py`` file under ``src/``. The stem is
    the filename without ``.py``; the same stem can name modules in different
    subpackages, so the value is a set of literal mirror paths.
    """
    mirrors: dict[str, set[str]] = {}
    for path in files:
        rel = str(path.relative_to(root))
        parts = Path(rel).parts
        if parts[0] != "src" or path.name == "__init__.py" or path.suffix != ".py":
            continue
        mirrors.setdefault(path.stem, set()).add(_mirror_of(rel))
    return mirrors


def check_mirror_layout(rel: str, mirrors: dict[str, set[str]]) -> list[Finding]:
    """Flag a stem-matching test file that does not sit at its module's mirror.

    The mirror relationship holds between the repo's top-level ``src/`` and
    ``tests/`` trees, so only files under ``tests/`` are in the rule's domain. A
    ``test_*.py`` living elsewhere -- e.g. a nested template scaffold's own test
    tree -- is not matched against the top-level ``src/`` modules.
    """
    if Path(rel).parts[0] != "tests":
        return []
    stem = Path(rel).name[len("test_") : -len(".py")]
    targets = mirrors.get(stem)
    if not targets or rel in targets:
        return []
    expected = " or ".join(sorted(targets))
    return [
        Finding(
            rel,
            None,
            MIRROR_LAYOUT,
            f"test file for a src module must sit at its mirror ({expected})",
        )
    ]


# --- no-logic rule ---

_NESTED_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def check_no_logic(rel: str, tree: ast.Module) -> list[Finding]:
    """Flag ``if``/``try`` statements in the body of a ``test_*`` function.

    Only the two constructs the testing contract bans are matched; ``if``/``try``
    inside a nested helper (its own function or class scope) are that helper's
    concern, not the test's, and are exempt.
    """
    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(
            node, ast.FunctionDef | ast.AsyncFunctionDef
        ) and node.name.startswith("test_"):
            findings.extend(_logic_in_test_body(rel, node))
    return findings


def _logic_in_test_body(
    rel: str, fn: ast.FunctionDef | ast.AsyncFunctionDef
) -> list[Finding]:
    findings: list[Finding] = []
    for node in _body_nodes(fn):
        if isinstance(node, ast.If):
            findings.append(
                Finding(rel, node.lineno, NO_LOGIC, "`if`/`else` in a test body")
            )
        elif isinstance(node, ast.Try):
            findings.append(
                Finding(rel, node.lineno, NO_LOGIC, "`try`/`except` in a test body")
            )
    return findings


def _body_nodes(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> list[ast.AST]:
    """Every node under ``fn``'s body, not descending into a nested def or class."""
    nodes: list[ast.AST] = []
    stack: list[ast.AST] = [n for n in fn.body if not isinstance(n, _NESTED_SCOPES)]
    while stack:
        node = stack.pop()
        nodes.append(node)
        for child in ast.iter_child_nodes(node):
            if not isinstance(child, _NESTED_SCOPES):
                stack.append(child)
    return nodes


# --- the walk ---


def scan_file(path: Path, root: Path, mirrors: dict[str, set[str]]) -> list[Finding]:
    """Every finding a single test file yields across the detector's rules."""
    rel = str(path.relative_to(root))
    dir_parts = set(Path(rel).parts[:-1])
    if not (path.name.startswith("test_") and path.suffix == ".py"):
        return []
    if _CACHES & dir_parts or is_externally_managed(rel):
        return []
    findings: list[Finding] = []
    findings.extend(check_mirror_layout(rel, mirrors))
    tree = pyast.parse(path)
    if tree is not None:
        findings.extend(check_no_private_access(rel, tree))
        findings.extend(check_no_logic(rel, tree))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Scan a repo's test files and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="testing-lint",
        description="Lint Python tests: no-private-access, mirror-layout, no-logic.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)
    root = Path(args.directory).resolve()

    try:
        files = pyast.find_python_files(root)
    except subprocess.CalledProcessError as err:
        print(f"testing-lint: cannot list files in {root}: {err}", file=sys.stderr)
        return 2
    mirrors = src_module_mirrors(files, root)
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root, mirrors))

    for f in sorted(findings, key=lambda f: (f.file, f.line or 0, f.rule)):
        print(f.render())

    if findings:
        print(
            f"testing-lint: {len(findings)} finding(s) across {len(files)} files",
            file=sys.stderr,
        )
        return 1
    print(f"testing-lint: clean across {len(files)} files", file=sys.stderr)
    return 0
