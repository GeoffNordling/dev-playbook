"""Tests for sdd_tools.interface — Interface signature validator."""

from __future__ import annotations

import sys
from pathlib import Path

import _iface_fixture as fix
import pytest

from sdd_tools.interface import (
    _qualified_name,
    _resolve_symbol,
    render_annotation,
    render_signature,
    validate_interfaces,
)
from sdd_tools.models import SpecItem


@pytest.fixture(autouse=True, scope="module")
def _ensure_fixture_importable():
    # Ensure the tests/ dir is on sys.path so '_iface_fixture' resolves.
    here = str(Path(__file__).parent)
    if here not in sys.path:
        sys.path.insert(0, here)
    yield


def _dsn(*interfaces: str) -> SpecItem:
    return SpecItem(
        id="dsn~m.x~1",
        doctype="dsn",
        name="m.x",
        revision=1,
        title="X",
        status="approved",
        description="\n".join(f"Interface: {i}" for i in interfaces),
        rationale="",
        covers=[],
        needs=[],
        source_file=Path("specs/d.md"),
        source_line=42,
        interfaces=list(interfaces),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class TestQualifiedName:
    def test_simple(self):
        assert _qualified_name("foo.bar(x: int) -> None") == "foo.bar"

    def test_method(self):
        assert _qualified_name("a.b.C.method(self) -> None") == "a.b.C.method"

    def test_no_paren(self):
        assert _qualified_name("not a signature") == ""


class TestResolveSymbol:
    def test_module_function(self):
        obj = _resolve_symbol("_iface_fixture.parse_session")
        assert obj is fix.parse_session

    def test_class_method(self):
        obj = _resolve_symbol("_iface_fixture.Session.run")
        assert obj is fix.Session.run

    def test_missing_symbol_returns_none(self):
        assert _resolve_symbol("_iface_fixture.no_such_thing") is None

    def test_missing_module_returns_none(self):
        assert _resolve_symbol("no.such.module.fn") is None


# ---------------------------------------------------------------------------
# Annotation rendering
# ---------------------------------------------------------------------------


class TestRenderAnnotation:
    def test_int(self):
        assert render_annotation(int) == "int"

    def test_str(self):
        assert render_annotation(str) == "str"

    def test_none_type(self):
        assert render_annotation(type(None)) == "None"

    def test_pathlib_path(self):
        import pathlib

        assert render_annotation(pathlib.Path) == "pathlib.Path"

    def test_list_of_int(self):
        assert render_annotation(list[int]) == "list[int]"

    def test_dict_of_str_int(self):
        assert render_annotation(dict[str, int]) == "dict[str, int]"

    def test_pep604_union(self):
        assert render_annotation(int | None) == "int | None"

    def test_typing_optional(self):
        # render_annotation should normalise legacy Optional[X] to the modern
        # union spelling. Constructing Optional as a value (rather than as an
        # annotation) avoids the UP045 lint on the legacy form.
        import typing

        # typing.Union[int, None] is the desugared shape Optional[int] resolves
        # to; constructing it via subscript avoids ruff's UP rule on the legacy
        # spelling (which exists in older codebases we still need to handle).
        legacy_union = typing.Union[int, None]  # noqa: UP007
        assert render_annotation(legacy_union) == "int | None"


# ---------------------------------------------------------------------------
# Signature rendering
# ---------------------------------------------------------------------------


class TestRenderSignature:
    def test_simple_function(self):
        rendered = render_signature("_iface_fixture.parse_session", fix.parse_session)
        assert rendered == "_iface_fixture.parse_session(path: pathlib.Path) -> str"

    def test_default_marked_with_ellipsis(self):
        rendered = render_signature("_iface_fixture.with_default", fix.with_default)
        assert rendered == "_iface_fixture.with_default(value: int = ...) -> int"

    def test_optional_uses_modern_union(self):
        rendered = render_signature(
            "_iface_fixture.with_optional", fix.with_optional
        )
        assert rendered == "_iface_fixture.with_optional(value: int | None = ...) -> int"

    def test_list_annotation(self):
        rendered = render_signature("_iface_fixture.with_list", fix.with_list)
        assert rendered == "_iface_fixture.with_list(items: list[int]) -> int"

    def test_kwonly_marker(self):
        rendered = render_signature("_iface_fixture.with_kwonly", fix.with_kwonly)
        assert rendered == "_iface_fixture.with_kwonly(*, flag: bool) -> bool"

    def test_var_args(self):
        rendered = render_signature(
            "_iface_fixture.with_var_args", fix.with_var_args
        )
        assert rendered == "_iface_fixture.with_var_args(*args: int, **kwargs: str) -> None"

    def test_method_includes_self(self):
        rendered = render_signature("_iface_fixture.Session.run", fix.Session.run)
        assert rendered == "_iface_fixture.Session.run(self) -> None"


# ---------------------------------------------------------------------------
# Validate end-to-end
# ---------------------------------------------------------------------------


class TestValidateInterfaces:
    def test_match_no_findings(self):
        item = _dsn("_iface_fixture.parse_session(path: pathlib.Path) -> str")
        assert validate_interfaces([item]) == []

    def test_mismatch_emits_finding(self):
        item = _dsn("_iface_fixture.parse_session(path: str) -> str")
        findings = validate_interfaces([item])
        assert len(findings) == 1
        assert findings[0].rule == "interface.mismatch"
        assert findings[0].line_kind == "dsn header"
        assert findings[0].spec_id == "dsn~m.x~1"
        assert "committed:" in findings[0].detail
        assert "actual:" in findings[0].detail

    def test_missing_symbol_emits_finding(self):
        item = _dsn("_iface_fixture.no_such_function(x: int) -> None")
        findings = validate_interfaces([item])
        assert len(findings) == 1
        assert findings[0].rule == "interface.missing-symbol"

    def test_malformed_committed_string_emits_finding(self):
        item = _dsn("not a real signature")
        findings = validate_interfaces([item])
        assert len(findings) == 1
        assert findings[0].rule == "interface.malformed"

    def test_non_dsn_skipped(self):
        item = SpecItem(
            id="req~m.x~1",
            doctype="req",
            name="m.x",
            revision=1,
            title="X",
            status="approved",
            description="",
            rationale="",
            covers=[],
            needs=[],
            source_file=Path("specs/r.md"),
            source_line=1,
            interfaces=["_iface_fixture.no_such_thing(x: int) -> None"],
        )
        assert validate_interfaces([item]) == []
