"""Interface validator: parse Interface: claims and check them against code.

For each ``Interface:`` line in a dsn item, resolve the named symbol, render
its actual signature in the same modern form the spec uses, and compare the
two as strings. Per ADR-004, mismatch or missing symbol is a hard fail.

Anchors all findings to the dsn item's header line (``line_kind="dsn header"``)
because the parser does not re-locate the precise ``Interface:`` line within
the description body.
"""

from __future__ import annotations

import importlib
import inspect
import types
import typing
from typing import Any

from sdd_tools.models import Finding, SpecItem


def validate_interfaces(items: list[SpecItem]) -> list[Finding]:
    """Validate every Interface: declaration across all dsn items."""
    findings: list[Finding] = []
    for item in items:
        if item.doctype != "dsn":
            continue
        for committed in item.interfaces:
            findings.extend(_check_one(item, committed))
    return findings


def _check_one(item: SpecItem, committed: str) -> list[Finding]:
    qualified = _qualified_name(committed)
    if not qualified:
        return [
            Finding(
                rule="interface.malformed",
                file=item.source_file,
                line=item.source_line,
                line_kind="dsn header",
                spec_id=item.id,
                message=f"could not parse Interface: line: {committed!r}",
                fix="expected: module.symbol(arg: type, ...) -> type",
            )
        ]

    obj = _resolve_symbol(qualified)
    if obj is None:
        return [
            Finding(
                rule="interface.missing-symbol",
                file=item.source_file,
                line=item.source_line,
                line_kind="dsn header",
                spec_id=item.id,
                message=f"symbol not found: {qualified}",
                fix=(
                    "create the symbol at the committed path or update "
                    "Interface: to match the code"
                ),
            )
        ]

    try:
        actual = render_signature(qualified, obj)
    except (TypeError, ValueError) as exc:
        return [
            Finding(
                rule="interface.introspection-failed",
                file=item.source_file,
                line=item.source_line,
                line_kind="dsn header",
                spec_id=item.id,
                message=f"could not introspect {qualified}: {exc}",
            )
        ]

    if actual != committed:
        return [
            Finding(
                rule="interface.mismatch",
                file=item.source_file,
                line=item.source_line,
                line_kind="dsn header",
                spec_id=item.id,
                message=f"signature differs for {qualified}",
                detail=f"committed: {committed}\nactual:    {actual}",
                fix="update Interface: or update the code to match",
            )
        ]
    return []


def _qualified_name(committed: str) -> str:
    """Extract the dotted symbol path from a committed Interface: line."""
    paren = committed.find("(")
    if paren <= 0:
        return ""
    return committed[:paren].strip()


def _resolve_symbol(qualified: str) -> Any | None:
    """Resolve a dotted name by importing the longest module prefix.

    For ``a.b.C.method``, tries to import ``a.b.C.method`` first, then
    ``a.b.C``, then ``a.b``, then ``a``. As soon as one import succeeds, the
    remaining parts are walked as attributes.
    """
    parts = qualified.split(".")
    for split_at in range(len(parts), 0, -1):
        module_name = ".".join(parts[:split_at])
        try:
            mod = importlib.import_module(module_name)
        except (ModuleNotFoundError, ImportError):
            continue
        obj: Any = mod
        for attr in parts[split_at:]:
            obj = getattr(obj, attr, None)
            if obj is None:
                break
        if obj is not None:
            return obj
    return None


def render_signature(qualified: str, obj: Any) -> str:
    """Render the symbol's actual signature in the modern form spec uses."""
    sig = inspect.signature(obj)
    try:
        hints = typing.get_type_hints(obj)
    except Exception:
        hints = {}

    parts: list[str] = []
    prev_kind: inspect._ParameterKind | None = None
    saw_var_positional = False

    for name, param in sig.parameters.items():
        if (
            prev_kind == inspect.Parameter.POSITIONAL_ONLY
            and param.kind != inspect.Parameter.POSITIONAL_ONLY
        ):
            parts.append("/")
        if (
            param.kind == inspect.Parameter.KEYWORD_ONLY
            and not saw_var_positional
        ):
            parts.append("*")
        parts.append(_render_param(name, param, hints.get(name, param.annotation)))
        if param.kind == inspect.Parameter.VAR_POSITIONAL:
            saw_var_positional = True
        prev_kind = param.kind

    if prev_kind == inspect.Parameter.POSITIONAL_ONLY:
        parts.append("/")

    args_str = ", ".join(parts)

    return_ann = hints.get("return", sig.return_annotation)
    if return_ann is inspect.Signature.empty:
        ret_str = ""
    else:
        ret_str = f" -> {render_annotation(return_ann)}"

    return f"{qualified}({args_str}){ret_str}"


def _render_param(
    name: str, param: inspect.Parameter, annotation: Any
) -> str:
    if param.kind == inspect.Parameter.VAR_POSITIONAL:
        prefix = "*"
    elif param.kind == inspect.Parameter.VAR_KEYWORD:
        prefix = "**"
    else:
        prefix = ""

    rendered = f"{prefix}{name}"
    if annotation is not inspect.Parameter.empty:
        rendered += f": {render_annotation(annotation)}"
    if param.default is not inspect.Parameter.empty:
        # Presence of default matters; precise value does not affect signature
        # equality unless the spec writes one. Render as "= ..." sentinel.
        rendered += " = ..."
    return rendered


def render_annotation(ann: Any) -> str:
    """Render an annotation in the modern PEP 585/604 idiom."""
    if ann is None or ann is type(None):
        return "None"
    if ann is inspect.Parameter.empty:
        return ""

    # PEP 604 union: X | Y
    if isinstance(ann, types.UnionType):
        return " | ".join(render_annotation(a) for a in ann.__args__)

    origin = typing.get_origin(ann)
    args = typing.get_args(ann)

    if origin is typing.Union:
        return " | ".join(render_annotation(a) for a in args)

    if origin is not None and args:
        origin_name = _origin_name(origin)
        rendered_args = ", ".join(render_annotation(a) for a in args)
        return f"{origin_name}[{rendered_args}]"

    if isinstance(ann, type):
        if ann.__module__ == "builtins":
            return ann.__name__
        return f"{ann.__module__}.{ann.__qualname__}"

    return str(ann)


def _origin_name(origin: Any) -> str:
    """Modernize a typing origin (typing.List → list, etc.)."""
    if isinstance(origin, type):
        if origin.__module__ == "builtins":
            return origin.__name__
        return f"{origin.__module__}.{origin.__qualname__}"
    # typing aliases retain a __name__ like "List", "Dict", etc.
    name = getattr(origin, "__name__", None) or getattr(origin, "_name", None)
    if not isinstance(name, str):
        return str(origin)
    aliases = {
        "List": "list",
        "Dict": "dict",
        "Set": "set",
        "FrozenSet": "frozenset",
        "Tuple": "tuple",
        "Type": "type",
    }
    return aliases.get(name, name.lower())
