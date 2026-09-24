"""The testing family: the rules of ``standards/testing/``.

Two rules are decided by functions over the model: a file that defines
tests is named ``test_*.py``, and a test file for a ``src/`` module sits at
one of that module's mirrors under ``tests/``.
"""

import ast
from collections.abc import Iterator
from pathlib import PurePosixPath

from dev_playbook.check_registry import Finding, check
from dev_playbook.model import Repo

PREFIX_MESSAGE = "`{name}` is a test, so the file must be named `test_*.py`"
MIRROR_MESSAGE = "test file for a src module must sit at one of its mirrors ({})"

# The scope directories a suite may put between ``tests/`` and the mirrored
# module path.
MIRROR_SCOPES = ("unit", "integration")


def _is_test_definition(node: ast.stmt) -> str | None:
    """The name of a module-level test function or test class, else None."""
    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
        return node.name if node.name.startswith("test_") else None
    if isinstance(node, ast.ClassDef):
        return node.name if node.name.startswith("Test") else None
    return None


@check("testing.test-files-carry-the-test-prefix")
def carries_test_prefix(repo: Repo) -> Iterator[Finding]:
    """A ``.py`` file that defines a test at module level is named ``test_*.py``."""
    for path, source in repo.python.items():
        name = PurePosixPath(path).name
        if not name.endswith(".py") or name.startswith("test_"):
            continue
        if source.tree is None:
            continue
        for node in source.tree.body:
            test_name = _is_test_definition(node)
            if test_name is not None:
                yield Finding(path, node.lineno, PREFIX_MESSAGE.format(name=test_name))


def _mirrors(repo: Repo) -> dict[str, set[str]]:
    """Map each ``src/`` module name to the test paths that mirror it."""
    mirrors: dict[str, set[str]] = {}
    for path in repo.files:
        module = PurePosixPath(path)
        if (
            module.parts[0] != "src"
            or module.suffix != ".py"
            or module.name == "__init__.py"
        ):
            continue
        below_src = module.relative_to("src")
        tail = below_src.parent / f"test_{below_src.name}"
        targets = mirrors.setdefault(module.stem, set())
        targets.add(str(PurePosixPath("tests") / tail))
        targets.update(
            str(PurePosixPath("tests") / scope / tail) for scope in MIRROR_SCOPES
        )
    return mirrors


@check("testing.test-tree-mirrors-the-source-tree")
def mirrors_source_tree(repo: Repo) -> Iterator[Finding]:
    """A ``tests/**/test_<name>.py`` for a ``src`` module sits at one of its mirrors."""
    mirrors = _mirrors(repo)
    for path in repo.files:
        test = PurePosixPath(path)
        if (
            test.parts[0] != "tests"
            or not test.name.startswith("test_")
            or test.suffix != ".py"
        ):
            continue
        targets = mirrors.get(test.stem.removeprefix("test_"))
        if targets and path not in targets:
            yield Finding(
                path, None, MIRROR_MESSAGE.format(" or ".join(sorted(targets)))
            )
