"""Audit a repo's Python tests against the workspace testing conventions.

testing-lint is the detector behind the Python-testing Standard. It walks a repo's
Python files once (via dev_playbook.pyast.find_python_files, so gitignore-aware
and worktree-scoped) and applies one rule to the test files it finds:

  - **mirror-layout** — a ``test_<stem>.py`` whose stem names an existing ``src``
    module must sit at a mirror of that module: beneath ``tests/`` directly
    (``src/x/y.py`` -> ``tests/x/test_y.py``) or beneath a recognized scope
    directory (``tests/unit/x/test_y.py``, ``tests/integration/x/test_y.py``).
    Test files matching no module (e2e suites, flattened names),
    ``conftest.py``, and non-``test_*`` helpers are outside the rule's domain.
    Placement only, not coverage or naming.

See standards/testing/conventions.md for the conventions these rules enforce.

Output:
    stdout — one finding per line, ``file:line: testing.rule message``.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    testing-lint [directory]
    testing-lint --list-rules
"""

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import pyast
from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the testing directory
# whose Standard it answers. Each id is a module-level constant so every emission site
# references the constant, never a raw literal, and RULES (what --list-rules
# prints) cannot drift from what the detector actually emits.
MIRROR_SOURCE_STRUCTURE = "testing.test-tree-mirrors-the-source-tree"

RULES = (MIRROR_SOURCE_STRUCTURE,)

# git ls-files already drops gitignored caches; this name filter also covers the
# rare tracked copy. A test file is scanned when none of its parent directory
# names is in this set.
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


# --- mirror-layout rule ---

# The scope directories a suite may interpose between ``tests/`` and the
# mirrored package path. ``unit`` and ``integration`` each mirror ``src/``
# beneath them. The set is fixed: any other directory in that position is a
# misplacement, not a scope.
MIRROR_SCOPES = ("unit", "integration")


def _mirrors_of(src_rel: str) -> set[str]:
    """The test paths that mirror a src module, flat and scoped.

    ``src/x/y.py`` -> ``tests/x/test_y.py``, plus ``tests/<scope>/x/test_y.py``
    for each recognized mirror scope.
    """
    below_src = Path(src_rel).relative_to("src")
    tail = below_src.parent / f"test_{below_src.name}"
    return {str(Path("tests") / tail)} | {
        str(Path("tests") / scope / tail) for scope in MIRROR_SCOPES
    }


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
        mirrors.setdefault(path.stem, set()).update(_mirrors_of(rel))
    return mirrors


def check_mirror_layout(rel: str, mirrors: dict[str, set[str]]) -> list[Finding]:
    """Flag a stem-matching test file that sits at none of its module's mirrors.

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
            MIRROR_SOURCE_STRUCTURE,
            f"test file for a src module must sit at one of its mirrors ({expected})",
        )
    ]


# --- the walk ---


def scan_file(path: Path, root: Path, mirrors: dict[str, set[str]]) -> list[Finding]:
    """Every finding a single test file yields across the detector's rules."""
    rel = str(path.relative_to(root))
    dir_parts = set(Path(rel).parts[:-1])
    if not (path.name.startswith("test_") and path.suffix == ".py"):
        return []
    if _CACHES & dir_parts:
        return []
    return check_mirror_layout(rel, mirrors)


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
