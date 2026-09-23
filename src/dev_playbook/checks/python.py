"""The python family: the rules of ``standards/python/``.

Two rules are decided by functions over the model. The docstring rule and
the formatting rule are decided by ruff, and are registered by hook name.
"""

import ast
from collections.abc import Iterator
from pathlib import PurePosixPath

from dev_playbook.check_registry import Finding, check, tool_check
from dev_playbook.model import Repo

INIT_MESSAGE = "`__init__.py` must be empty (no docstring, no code)"
FUTURE_MESSAGE = "`from __future__ import annotations` is banned (Python >= 3.11)"

tool_check(
    "python.every-definition-carries-a-docstring", hook="ruff-check", module=__name__
)
tool_check("python.formatted-by-ruff-format", hook="ruff-format", module=__name__)


@check("python.empty-init")
def empty_init(repo: Repo) -> Iterator[Finding]:
    """A file named ``__init__.py`` holds no character other than whitespace."""
    for path, source in repo.python.items():
        if PurePosixPath(path).name == "__init__.py" and source.text.strip():
            yield Finding(path, 1, INIT_MESSAGE)


@check("python.no-future-annotations")
def no_future_annotations(repo: Repo) -> Iterator[Finding]:
    """``from __future__ import annotations`` does not appear in the file."""
    for path, source in repo.python.items():
        if source.tree is None:
            continue
        for node in ast.walk(source.tree):
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "__future__"
                and any(alias.name == "annotations" for alias in node.names)
            ):
                yield Finding(path, node.lineno, FUTURE_MESSAGE)
