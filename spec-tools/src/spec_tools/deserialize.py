"""Read SDD spec files from disk into the in-memory model."""

import pathlib
import re
from collections.abc import Mapping
from dataclasses import dataclass

from spec_tools.model import ItemId, SpecItem

_HEADING_PREFIX = "### "
_KEYWORD_LINE = re.compile(r"^(?P<keyword>[A-Z][A-Za-z]+):\s*(?P<inline>.*)$")
_BULLET_PREFIX = "- "

_BLOCK_KEYWORDS = {"Description", "Rationale", "Comment"}
_ID_BULLET_KEYWORDS = {"Covers", "Depends"}
_STRING_BULLET_KEYWORDS = {"Needs"}
_INLINE_KEYWORDS = {"Tags"}
_REPEATED_KEYWORDS = {"Interface", "AgentReview"}
_KNOWN_KEYWORDS = (
    _BLOCK_KEYWORDS
    | _ID_BULLET_KEYWORDS
    | _STRING_BULLET_KEYWORDS
    | _INLINE_KEYWORDS
    | _REPEATED_KEYWORDS
)


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


# ---------------------------------------------------------------------------
# Error builders
# ---------------------------------------------------------------------------


def _id_syntax_error(
    line_index: int, path: pathlib.Path, message: str
) -> SpecParseError:
    """Build an `id-syntax` error for the malformed ID at `line_index`."""
    return SpecParseError(path, line_index + 1, "id-syntax", message)


def _unknown_keyword_error(
    keyword: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build an `unknown-keyword` error for `keyword` at `line_index`."""
    message = f"keyword {keyword!r} is not defined by the spec standard"
    return SpecParseError(path, line_index + 1, "unknown-keyword", message)


def _duplicate_keyword_error(
    keyword: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a `duplicate-keyword` error for `keyword` repeated at `line_index`."""
    message = f"`{keyword}:` appears more than once within one item"
    return SpecParseError(path, line_index + 1, "duplicate-keyword", message)


def _missing_keyword_error(
    keyword: str, heading: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a `missing-keyword` error for `keyword` absent from item `heading`."""
    message = f"item {heading!r} is missing required `{keyword}:` keyword"
    return SpecParseError(path, line_index + 1, "missing-keyword", message)


def _empty_body_error(
    keyword: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a `malformed-body` error for `keyword` declared with no content."""
    message = (
        f"`{keyword}:` is declared with no content; "
        "omit the keyword entirely when it has no entries"
    )
    return SpecParseError(path, line_index + 1, "malformed-body", message)


def _stray_line_error(line: str, line_index: int, path: pathlib.Path) -> SpecParseError:
    """Build a `malformed-body` error for a non-blank, non-keyword line in an item."""
    message = f"unexpected non-keyword line within item: {line!r}"
    return SpecParseError(path, line_index + 1, "malformed-body", message)


def _malformed_heading_error(
    line: str, line_index: int, path: pathlib.Path
) -> SpecParseError:
    """Build a `malformed-heading` error for a non-conformant ATX heading."""
    message = (
        f"heading {line!r} does not match the required `### <text>` form "
        "(three hashes, single space, non-empty text)"
    )
    return SpecParseError(path, line_index + 1, "malformed-heading", message)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parse(path: pathlib.Path) -> list[SpecItem]:
    """Parse the spec file at `path` into a list of SpecItems in source order.

    Aborts on the first standard violation by raising `SpecParseError`.
    """
    lines = path.read_text().splitlines()
    items: list[SpecItem] = []
    cursor = 0
    while cursor < len(lines):
        line = lines[cursor]
        if line.startswith(_HEADING_PREFIX) and line[len(_HEADING_PREFIX) :].strip():
            item, cursor = _parse_item(lines, cursor, path)
            items.append(item)
        elif line.startswith("#"):
            raise _malformed_heading_error(line, cursor, path)
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
    item_id = _parse_id(lines[start + 1], start + 1, path)
    blocks: dict[str, str] = {}
    id_bullets: dict[str, list[ItemId]] = {}
    string_bullets: dict[str, list[str]] = {}
    inline: dict[str, list[str]] = {}
    repeated: dict[str, list[str]] = {}
    cursor = start + 2
    while cursor < len(lines) and not lines[cursor].startswith(_HEADING_PREFIX):
        line = lines[cursor]
        if not line.strip():
            cursor += 1
            continue
        match = _KEYWORD_LINE.match(line)
        if match is None:
            raise _stray_line_error(line, cursor, path)
        keyword = match.group("keyword")
        inline_value = match.group("inline")
        keyword_line = cursor
        if keyword not in _KNOWN_KEYWORDS:
            raise _unknown_keyword_error(keyword, cursor, path)
        if keyword in _BLOCK_KEYWORDS:
            _check_duplicate(keyword, blocks, cursor, path)
            body, cursor = _capture_block(lines, cursor + 1)
            if not body:
                raise _empty_body_error(keyword, keyword_line, path)
            blocks[keyword] = body
        elif keyword in _ID_BULLET_KEYWORDS:
            _check_duplicate(keyword, id_bullets, cursor, path)
            ids, cursor = _capture_id_bullets(lines, cursor + 1, path)
            if not ids:
                raise _empty_body_error(keyword, keyword_line, path)
            id_bullets[keyword] = ids
        elif keyword in _STRING_BULLET_KEYWORDS:
            _check_duplicate(keyword, string_bullets, cursor, path)
            entries, cursor = _capture_string_bullets(lines, cursor + 1)
            if not entries:
                raise _empty_body_error(keyword, keyword_line, path)
            string_bullets[keyword] = entries
        elif keyword in _INLINE_KEYWORDS:
            _check_duplicate(keyword, inline, cursor, path)
            entries = _parse_inline_tags(line, keyword, keyword_line, path)
            inline[keyword] = entries
            cursor += 1
        else:  # _REPEATED_KEYWORDS
            if not inline_value.strip():
                raise _empty_body_error(keyword, keyword_line, path)
            repeated.setdefault(keyword, []).append(inline_value)
            cursor += 1
    if "Description" not in blocks:
        raise _missing_keyword_error("Description", heading, start, path)
    item = SpecItem(
        heading=heading,
        id=item_id,
        description=blocks["Description"],
        rationale=blocks.get("Rationale"),
        comment=blocks.get("Comment"),
        covers=id_bullets.get("Covers", []),
        depends=id_bullets.get("Depends", []),
        needs=string_bullets.get("Needs", []),
        tags=inline.get("Tags", []),
        interface=repeated.get("Interface", []),
        agent_review=repeated.get("AgentReview", []),
    )
    return item, cursor


# ---------------------------------------------------------------------------
# Body capture
# ---------------------------------------------------------------------------


def _capture_block(lines: list[str], start: int) -> tuple[str, int]:
    """Capture a block body up to the first blank line, keyword, heading, or EOF.

    A blank line inside the body is not allowed; blank lines terminate the
    body. If the next non-blank line after the terminator is still body
    content (rather than a keyword or heading), `_parse_item`'s stray-line
    check raises `malformed-body`.
    """
    body: list[str] = []
    cursor = start
    while cursor < len(lines):
        line = lines[cursor]
        if not line.strip():
            break
        if line.startswith(_HEADING_PREFIX) or _KEYWORD_LINE.match(line):
            break
        body.append(line)
        cursor += 1
    return "\n".join(body), cursor


def _capture_id_bullets(
    lines: list[str], start: int, path: pathlib.Path
) -> tuple[list[ItemId], int]:
    """Capture `- type~name~rev` bullets until the first non-bullet line."""
    ids: list[ItemId] = []
    cursor = start
    while cursor < len(lines) and lines[cursor].startswith(_BULLET_PREFIX):
        triple = lines[cursor][len(_BULLET_PREFIX) :]
        ids.append(_parse_id_triple(triple, cursor, path))
        cursor += 1
    return ids, cursor


def _capture_string_bullets(lines: list[str], start: int) -> tuple[list[str], int]:
    """Capture `- entry` bullets until the first non-bullet line."""
    entries: list[str] = []
    cursor = start
    while cursor < len(lines) and lines[cursor].startswith(_BULLET_PREFIX):
        entries.append(lines[cursor][len(_BULLET_PREFIX) :])
        cursor += 1
    return entries, cursor


# ---------------------------------------------------------------------------
# ID parsing
# ---------------------------------------------------------------------------


def _parse_id(line: str, line_index: int, path: pathlib.Path) -> ItemId:
    """Parse a backtick-wrapped `` `type~name~rev` `` ID line into an ItemId."""
    stripped = line.strip()
    if not (stripped.startswith("`") and stripped.endswith("`")):
        raise _id_syntax_error(
            line_index, path, f"expected backtick-wrapped ID triple, got {line!r}"
        )
    return _parse_id_triple(stripped[1:-1], line_index, path)


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
# Small helpers
# ---------------------------------------------------------------------------


def _check_duplicate(
    keyword: str,
    seen: Mapping[str, object],
    line_index: int,
    path: pathlib.Path,
) -> None:
    """Raise `duplicate-keyword` if `keyword` already has an entry in `seen`."""
    if keyword in seen:
        raise _duplicate_keyword_error(keyword, line_index, path)


def _parse_inline_tags(
    line: str, keyword: str, line_index: int, path: pathlib.Path
) -> list[str]:
    """Parse a `Tags: ...` line under the canonical `, `-separated form."""
    prefix = f"{keyword}: "
    if not line.startswith(prefix):
        raise SpecParseError(
            path,
            line_index + 1,
            "malformed-body",
            f"`{keyword}:` must be followed by a single space, got {line!r}",
        )
    body = line[len(prefix) :]
    if not body:
        raise _empty_body_error(keyword, line_index, path)
    entries = body.split(", ")
    for entry in entries:
        if not entry or entry != entry.strip() or "," in entry:
            raise SpecParseError(
                path,
                line_index + 1,
                "malformed-body",
                f"`{keyword}:` entries must be non-empty and free of "
                f"whitespace or extra commas, got {entry!r}",
            )
    return entries
