"""Test-privacy validator: AST walk flagging private access to non-test code.

Per ADR-004: tests access only public names (identifiers not prefixed with
``_``, excluding Python dunder protocol methods). Private helpers in
non-test modules are exercised through the public interfaces that call them.

Walks each test file's AST and emits a Finding for:

- ``from pkg import _name`` where ``pkg`` is non-test and ``_name`` is not
  a dunder
- ``import pkg._private`` (non-test path with a private segment)
- ``from pkg._private import name`` (import path traverses a private segment)
- ``obj._private`` where ``obj`` is bound to a non-test import

Local underscore helpers defined in the test file are not flagged.
"""

from __future__ import annotations

import ast
from pathlib import Path

from sdd_tools.models import Finding


def validate_files(paths: list[Path]) -> list[Finding]:
    """Validate every test file in `paths`. Returns combined Finding list."""
    findings: list[Finding] = []
    for path in paths:
        findings.extend(_validate_one(path))
    return findings


def _validate_one(path: Path) -> list[Finding]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    visitor = _PrivacyVisitor(path)
    visitor.visit(tree)
    return visitor.findings


class _PrivacyVisitor(ast.NodeVisitor):
    """Collect private-access findings within one test file's AST."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.findings: list[Finding] = []
        # name → module path it was imported from (root only). Empty value
        # means the binding is local (defined in this file) and shouldn't
        # be cross-checked.
        self._imports: dict[str, str] = {}

    # --- import statements ----------------------------------------------

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module = alias.name  # "foo.bar.baz"
            local = alias.asname or alias.name.split(".")[0]
            if not _is_test_module(module):
                self._flag_private_segments(node, module)
            self._imports[local] = module
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        if module and not _is_test_module(module):
            self._flag_private_segments(node, module)
            for alias in node.names:
                if _is_private(alias.name):
                    self._add(
                        node,
                        rule="privacy.import-private",
                        message=(
                            f"imports private name '{alias.name}' from "
                            f"non-test module '{module}'"
                        ),
                    )
        for alias in node.names:
            local = alias.asname or alias.name
            self._imports[local] = module
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        # Locally defined names — record as local (no associated module)
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._imports.setdefault(node.name, "")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self._imports.setdefault(target.id, "")
        self.generic_visit(node)

    # --- attribute access -----------------------------------------------

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if _is_private(node.attr):
            root = _root_name(node)
            if root is not None:
                source_module = self._imports.get(root)
                if source_module and not _is_test_module(source_module):
                    chain = _attribute_chain(node)
                    self._add(
                        node,
                        rule="privacy.attribute-access",
                        message=(
                            f"reaches into private name '{node.attr}' on "
                            f"non-test import '{root}' ({chain})"
                        ),
                    )
        self.generic_visit(node)

    # --- helpers --------------------------------------------------------

    def _flag_private_segments(self, node: ast.AST, module: str) -> None:
        for segment in module.split("."):
            if _is_private(segment):
                self._add(
                    node,
                    rule="privacy.import-private",
                    message=(
                        f"imports through private module segment "
                        f"'{segment}' in '{module}'"
                    ),
                )
                return

    def _add(self, node: ast.AST, *, rule: str, message: str) -> None:
        self.findings.append(
            Finding(
                rule=rule,
                file=self.path,
                line=getattr(node, "lineno", 0),
                message=message,
                fix="exercise the private name through the public interface",
            )
        )


def _is_private(name: str) -> bool:
    """True for `_foo` (private), False for `__foo__` (dunder) and `foo`."""
    return name.startswith("_") and not (name.startswith("__") and name.endswith("__"))


def _is_test_module(module: str) -> bool:
    """True if any segment of the module path identifies it as a test module."""
    for segment in module.split("."):
        if segment == "tests" or segment.startswith("test_") or segment == "conftest":
            return True
    return False


def _root_name(node: ast.Attribute) -> str | None:
    """Return the root Name id of an attribute chain, or None."""
    current: ast.expr = node
    while isinstance(current, ast.Attribute):
        current = current.value
    if isinstance(current, ast.Name):
        return current.id
    return None


def _attribute_chain(node: ast.Attribute) -> str:
    """Render an attribute chain back to source form (best-effort)."""
    parts: list[str] = [node.attr]
    current: ast.expr = node.value
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))
