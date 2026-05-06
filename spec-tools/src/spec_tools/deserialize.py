"""Read SDD spec files from disk into the in-memory model."""

import pathlib
import re
from collections.abc import Callable
from dataclasses import dataclass, fields
from enum import Enum
from typing import Any

from spec_tools.model import ItemId, SpecItem

# ---------------------------------------------------------------------------
# Lexical primitives
# ---------------------------------------------------------------------------

_HEADING_PREFIX = "### "
_BULLET_PREFIX = "- "
_KEYWORD_LINE = re.compile(r"^(?P<keyword>[A-Z][A-Za-z]+):\s*(?P<inline>.*)$")
_FENCE_PREFIXES = ("```", "~~~")

_OBLIGATION_VERB = re.compile(r"\b(SHALL|SHOULD|MAY)\b")
_BACKTICK_SPAN = re.compile(r"`[^`\n]*`")
# An obligation verb in normative use is a backticked verb followed by
# whitespace and a lowercase predicate. Citations like `` `SHALL`, `SHOULD`,
# `MAY` `` are followed by punctuation, so they don't match.
_USED_OBLIGATION = re.compile(r"`(SHALL|SHOULD|MAY)(?:\s+NOT)?`\s+[a-z]")

_OPTIONAL_FIELD_DEFAULTS: dict[str, Any] = {
    "rationale": None,
    "comment": None,
    "covers": [],
    "depends": [],
    "needs": [],
    "tags": [],
    "interface": [],
    "agent_review": [],
}


# ---------------------------------------------------------------------------
# Keyword registry
# ---------------------------------------------------------------------------


class _BodyForm(Enum):
    """The five body shapes that §6 of the spec standard defines."""

    BLOCK = "block"
    ID_BULLETS = "id-bullets"
    STRING_BULLETS = "string-bullets"
    INLINE = "inline"
    REPEATED = "repeated"


@dataclass(frozen=True)
class _Keyword:
    """A keyword's parse contract: PascalCase label, SpecItem field, body form."""

    name: str
    field: str
    body_form: _BodyForm


_KEYWORDS: tuple[_Keyword, ...] = (
    _Keyword("Description", "description", _BodyForm.BLOCK),
    _Keyword("Rationale", "rationale", _BodyForm.BLOCK),
    _Keyword("Comment", "comment", _BodyForm.BLOCK),
    _Keyword("Covers", "covers", _BodyForm.ID_BULLETS),
    _Keyword("Depends", "depends", _BodyForm.ID_BULLETS),
    _Keyword("Needs", "needs", _BodyForm.STRING_BULLETS),
    _Keyword("Tags", "tags", _BodyForm.INLINE),
    _Keyword("Interface", "interface", _BodyForm.REPEATED),
    _Keyword("AgentReview", "agent_review", _BodyForm.REPEATED),
)


def _validate_keyword_registry() -> None:
    """Assert the registry's order and field names match SpecItem.

    The keyword sequence above must equal SpecItem's field order (skipping
    `heading` and `id`). Catching drift at module load preserves the §6
    canonical-order guarantee that the AgentReview claim on
    `dsn~model.spec-item~0` rests on.
    """
    expected = [f.name for f in fields(SpecItem) if f.name not in {"heading", "id"}]
    actual = [kw.field for kw in _KEYWORDS]
    if actual != expected:
        raise RuntimeError(
            f"keyword registry fields {actual} do not match "
            f"SpecItem field order {expected}"
        )


_validate_keyword_registry()

_KEYWORD_BY_NAME: dict[str, _Keyword] = {kw.name: kw for kw in _KEYWORDS}
_KEYWORD_POSITION: dict[str, int] = {kw.name: i for i, kw in enumerate(_KEYWORDS)}


# ---------------------------------------------------------------------------
# Public error type
# ---------------------------------------------------------------------------


@dataclass
class SpecParseError(Exception):
    """Structured error for spec-standard violations encountered during parse.

    `line` is 1-indexed against the source file. `rule_violated` is one of the
    stable string ids enumerated in `dsn~deserialize.parse-error~0`.
    """

    path: pathlib.Path
    line: int
    rule_violated: str
    message: str


def _error(
    rule: str, message: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a SpecParseError, converting a 0-indexed line into 1-indexed `line`."""
    return SpecParseError(path, line_index + 1, rule, message)


def _id_syntax_error(
    line_index: int, path: pathlib.Path, message: str
) -> SpecParseError:
    """Build an `id-syntax` error for the malformed ID at `line_index`."""
    return _error("id-syntax", message, line_index, path)


def _empty_body_error(
    keyword: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a `malformed-body` error for `keyword` declared with no content."""
    return _error(
        "malformed-body",
        f"`{keyword}:` is declared with no content; "
        "omit the keyword entirely when it has no entries",
        line_index,
        path,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parse(path: pathlib.Path) -> list[SpecItem]:
    """Parse the spec file at `path` into a list of SpecItems in source order.

    Aborts on the first standard violation by raising `SpecParseError`.
    """
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.startswith(_FENCE_PREFIXES):
            raise _error(
                "fenced-code-block",
                f"fenced code block marker {line!r} is forbidden by §8 of the "
                "workspace spec standard; use a 4-space indented code block",
                index,
                path,
            )
    items: list[SpecItem] = []
    cursor = 0
    while cursor < len(lines):
        line = lines[cursor]
        if line.startswith(_HEADING_PREFIX) and line[len(_HEADING_PREFIX) :].strip():
            item, cursor = _parse_item(lines, cursor, path)
            items.append(item)
        elif line.startswith("#"):
            raise _error(
                "malformed-heading",
                f"heading {line!r} does not match the required `### <text>` form "
                "(three hashes, single space, non-empty text)",
                cursor,
                path,
            )
        else:
            cursor += 1
    return items


# ---------------------------------------------------------------------------
# Item parser
# ---------------------------------------------------------------------------


def _parse_item(
    lines: list[str], start: int, path: pathlib.Path
) -> tuple[SpecItem, int]:
    """Parse one `### heading` item beginning at `lines[start]`.

    Returns the SpecItem and the cursor index of the first line not consumed
    by the item (typically the next `### heading` or end of file).
    """
    heading = lines[start][len(_HEADING_PREFIX) :]
    if start + 1 >= len(lines):
        raise _id_syntax_error(
            start, path, f"heading {heading!r} is missing its required ID line"
        )
    id_line = lines[start + 1].strip()
    if not (id_line.startswith("`") and id_line.endswith("`")):
        raise _id_syntax_error(
            start + 1,
            path,
            f"expected backtick-wrapped ID triple, got {lines[start + 1]!r}",
        )
    item_id = _parse_id_triple(id_line[1:-1], start + 1, path)
    field_values: dict[str, Any] = {}
    last_position = 0
    cursor = start + 2
    while cursor < len(lines) and not lines[cursor].startswith(_HEADING_PREFIX):
        line = lines[cursor]
        if not line.strip():
            cursor += 1
            continue
        match = _KEYWORD_LINE.match(line)
        if match is None:
            raise _error(
                "malformed-body",
                f"unexpected non-keyword line within item: {line!r}",
                cursor,
                path,
            )
        keyword = match.group("keyword")
        if keyword not in _KEYWORD_BY_NAME:
            raise _error(
                "unknown-keyword",
                f"keyword {keyword!r} is not defined by the spec standard",
                cursor,
                path,
            )
        position = _KEYWORD_POSITION[keyword]
        if position < last_position:
            raise _error(
                "keyword-order",
                f"`{keyword}:` appears out of canonical order; "
                "see §6 of the workspace spec standard",
                cursor,
                path,
            )
        last_position = position
        spec = _KEYWORD_BY_NAME[keyword]
        cursor = _BODY_FORM_HANDLERS[spec.body_form](
            spec, match, lines, cursor, path, field_values
        )
    if "description" not in field_values:
        raise _error(
            "missing-keyword",
            f"item {heading!r} is missing required `Description:` keyword",
            start,
            path,
        )
    return (
        SpecItem(
            heading=heading, id=item_id, **(_OPTIONAL_FIELD_DEFAULTS | field_values)
        ),
        cursor,
    )


# ---------------------------------------------------------------------------
# Per-body-form handlers
# ---------------------------------------------------------------------------


_Handler = Callable[
    [_Keyword, re.Match[str], list[str], int, pathlib.Path, dict[str, Any]], int
]


def _check_not_duplicate(
    spec: _Keyword,
    field_values: dict[str, Any],
    line_index: int,
    path: pathlib.Path,
) -> None:
    """Raise `duplicate-keyword` if `spec`'s field already has a captured value."""
    if spec.field in field_values:
        raise _error(
            "duplicate-keyword",
            f"`{spec.name}:` appears more than once within one item",
            line_index,
            path,
        )


def _handle_block(
    spec: _Keyword,
    match: re.Match[str],
    lines: list[str],
    cursor: int,
    path: pathlib.Path,
    field_values: dict[str, Any],
) -> int:
    """Capture a Description / Rationale / Comment block body."""
    keyword_line = cursor
    _check_not_duplicate(spec, field_values, keyword_line, path)
    body_lines: list[str] = []
    cursor += 1
    while cursor < len(lines):
        line = lines[cursor]
        if not line.strip():
            break
        if line.startswith(_HEADING_PREFIX) or _KEYWORD_LINE.match(line):
            break
        body_lines.append(line)
        cursor += 1
    body = "\n".join(body_lines)
    if not body:
        raise _empty_body_error(spec.name, keyword_line, path)
    if spec.name == "Description":
        _check_obligation_vocabulary(body, keyword_line, path)
    field_values[spec.field] = body
    return cursor


def _handle_id_bullets(
    spec: _Keyword,
    match: re.Match[str],
    lines: list[str],
    cursor: int,
    path: pathlib.Path,
    field_values: dict[str, Any],
) -> int:
    """Capture a Covers / Depends bullet list of typed ItemIds."""
    keyword_line = cursor
    _check_not_duplicate(spec, field_values, keyword_line, path)
    ids: list[ItemId] = []
    cursor += 1
    while cursor < len(lines) and lines[cursor].startswith(_BULLET_PREFIX):
        triple = lines[cursor][len(_BULLET_PREFIX) :]
        ids.append(_parse_id_triple(triple, cursor, path))
        cursor += 1
    if not ids:
        raise _empty_body_error(spec.name, keyword_line, path)
    field_values[spec.field] = ids
    return cursor


def _handle_string_bullets(
    spec: _Keyword,
    match: re.Match[str],
    lines: list[str],
    cursor: int,
    path: pathlib.Path,
    field_values: dict[str, Any],
) -> int:
    """Capture a Needs bullet list of strings."""
    keyword_line = cursor
    _check_not_duplicate(spec, field_values, keyword_line, path)
    entries: list[str] = []
    cursor += 1
    while cursor < len(lines) and lines[cursor].startswith(_BULLET_PREFIX):
        entries.append(lines[cursor][len(_BULLET_PREFIX) :])
        cursor += 1
    if not entries:
        raise _empty_body_error(spec.name, keyword_line, path)
    field_values[spec.field] = entries
    return cursor


def _handle_inline(
    spec: _Keyword,
    match: re.Match[str],
    lines: list[str],
    cursor: int,
    path: pathlib.Path,
    field_values: dict[str, Any],
) -> int:
    """Capture a Tags inline comma-separated list."""
    keyword_line = cursor
    _check_not_duplicate(spec, field_values, keyword_line, path)
    field_values[spec.field] = _parse_inline_tags(
        lines[cursor], spec.name, keyword_line, path
    )
    return cursor + 1


def _handle_repeated(
    spec: _Keyword,
    match: re.Match[str],
    lines: list[str],
    cursor: int,
    path: pathlib.Path,
    field_values: dict[str, Any],
) -> int:
    """Capture one occurrence of a repeatable keyword (Interface / AgentReview)."""
    inline_value = match.group("inline")
    if not inline_value.strip():
        raise _empty_body_error(spec.name, cursor, path)
    field_values.setdefault(spec.field, []).append(inline_value)
    return cursor + 1


_BODY_FORM_HANDLERS: dict[_BodyForm, _Handler] = {
    _BodyForm.BLOCK: _handle_block,
    _BodyForm.ID_BULLETS: _handle_id_bullets,
    _BodyForm.STRING_BULLETS: _handle_string_bullets,
    _BodyForm.INLINE: _handle_inline,
    _BodyForm.REPEATED: _handle_repeated,
}


# ---------------------------------------------------------------------------
# ID-triple parsing
# ---------------------------------------------------------------------------


def _parse_id_triple(triple: str, line_index: int, path: pathlib.Path) -> ItemId:
    """Parse the bare `type~name~rev` substring (no surrounding backticks)."""
    parts = triple.split("~")
    if len(parts) != 3:
        raise _id_syntax_error(
            line_index,
            path,
            f"ID triple must have three tilde-separated parts, got {triple!r}",
        )
    artifact_type, name, revision_text = parts
    try:
        revision = int(revision_text)
    except ValueError:
        raise _id_syntax_error(
            line_index, path, f"ID revision must be an integer, got {revision_text!r}"
        ) from None
    try:
        return ItemId(artifact_type, name, revision)
    except ValueError as exc:
        raise _id_syntax_error(line_index, path, str(exc)) from None


# ---------------------------------------------------------------------------
# Inline-tag parsing
# ---------------------------------------------------------------------------


def _parse_inline_tags(
    line: str, keyword: str, line_index: int, path: pathlib.Path
) -> list[str]:
    """Parse a `Tags: ...` line under the canonical `, `-separated form."""
    prefix = f"{keyword}: "
    if not line.startswith(prefix):
        raise _error(
            "malformed-body",
            f"`{keyword}:` must be followed by a single space, got {line!r}",
            line_index,
            path,
        )
    body = line[len(prefix) :]
    if not body:
        raise _empty_body_error(keyword, line_index, path)
    entries = body.split(", ")
    for entry in entries:
        if not entry or entry != entry.strip() or "," in entry:
            raise _error(
                "malformed-body",
                f"`{keyword}:` entries must be non-empty and free of "
                f"whitespace or extra commas, got {entry!r}",
                line_index,
                path,
            )
    return entries


# ---------------------------------------------------------------------------
# Obligation-vocabulary check (§7.1)
# ---------------------------------------------------------------------------


def _check_obligation_vocabulary(
    body: str, line_index: int, path: pathlib.Path
) -> None:
    """Enforce §7.1: obligation verbs are backticked, one level per item."""
    bare = _OBLIGATION_VERB.search(_BACKTICK_SPAN.sub("", body))
    if bare is not None:
        raise _error(
            "obligation-not-backticked",
            f"unbackticked obligation verb {bare.group(0)!r} in `Description:`; "
            "§7.1 requires obligation verbs to be wrapped in backticks",
            line_index,
            path,
        )
    levels = {match.group(1) for match in _USED_OBLIGATION.finditer(body)}
    if len(levels) > 1:
        raise _error(
            "obligation-mixed-levels",
            f"`Description:` mixes obligation levels {sorted(levels)}; "
            "§7.1 permits one level per item",
            line_index,
            path,
        )
