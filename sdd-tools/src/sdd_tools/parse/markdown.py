"""Pure-Python parser for OFT spec markdown files.

Produces SpecFile objects with Sections (one per ``## Header``) and SpecItems.
Shared by lint, sdd-index, sdd-atlas, and sdd-review. The OFT JAR remains the
canonical parser for coverage checks and chain building in ``sdd_tools.oft``.

Parsing is permissive: structural and well-formedness rules live in the lint
modules, not here. The parser does not reject malformed spec files; it extracts
what it can and leaves validation to downstream tooling.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from sdd_tools.models import (
    DIMENSION_NAMES,
    SPEC_ID_BARE_RE,
    Section,
    SpecFile,
    SpecItem,
)

# Match a top-level ``## Header`` line (not ``###`` or deeper).
_H2_RE = re.compile(r"^##(?!#)\s+(.+?)\s*$")
# Match any ATX heading (``#`` through ``######``).
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
# Horizontal rule: exactly ``---`` (optional trailing whitespace).
_HRULE_RE = re.compile(r"^---\s*$")
# A line consisting solely of a backticked spec ID.
_BACKTICKED_ID_LINE_RE = re.compile(rf"^\s*`{SPEC_ID_BARE_RE.pattern}`\s*$")
# OFT keyword line: ``Keyword: value-or-empty``. Captures keyword + remainder.
_KEYWORD_LINE_RE = re.compile(r"^([A-Z][A-Za-z]+):\s*(.*)$")
# ``<!-- oft:off --> ... <!-- oft:on -->`` block (dotall).
_OFT_OFF_BLOCK_RE = re.compile(
    r"<!--\s*oft:off\s*-->.*?<!--\s*oft:on\s*-->",
    re.DOTALL,
)

# OFT keyword fields this parser recognizes at the start of a line.
_KNOWN_KEYWORDS = frozenset(
    {
        "Status",
        "Covers",
        "Needs",
        "Rationale",
        "Comment",
        "Tags",
        "Depends",
        "Description",
        "Interface",
        "AgentReview",
    }
)


def parse_file(path: Path) -> SpecFile:
    """Read and parse one spec markdown file."""
    raw = path.read_text(encoding="utf-8")
    return parse_text(raw, path)


def parse_project(spec_dirs: list[Path]) -> list[SpecFile]:
    """Parse every .md file found under the given spec directories.

    Missing directories are skipped silently; project configuration may list
    directories that don't exist yet (e.g. a design layer not yet started).
    """
    files: list[SpecFile] = []
    for spec_dir in spec_dirs:
        if not spec_dir.is_dir():
            continue
        for md_file in sorted(spec_dir.rglob("*.md")):
            files.append(parse_file(md_file))
    return files


def group_by_dimension(files: list[SpecFile]) -> dict[str, list[SpecItem]]:
    """Group items across all files by dimension header.

    Returns a dict keyed by the four canonical dimension names in canonical
    order. Items from non-dimension sections (preamble, or custom H2 headers)
    are excluded.
    """
    groups: dict[str, list[SpecItem]] = {d: [] for d in DIMENSION_NAMES}
    for sf in files:
        for section in sf.sections:
            if section.is_dimension and section.header is not None:
                groups[section.header].extend(section.items)
    return groups


def parse_text(text: str, source_file: Path) -> SpecFile:
    """Parse spec markdown text into a SpecFile."""
    text = strip_oft_off_blocks(text)
    lines = text.splitlines()

    section_specs = _split_sections(lines)

    sections: list[Section] = []
    for spec in section_specs:
        items = _parse_items(
            spec.body_lines,
            spec.body_start_line,
            source_file,
        )
        sections.append(
            Section(
                header=spec.header,
                header_line=spec.header_line,
                items=items,
            )
        )
    return SpecFile(path=source_file, sections=sections)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


@dataclass
class _SectionSpec:
    header: str | None
    header_line: int | None
    body_lines: list[str]
    body_start_line: int  # 1-based line of body_lines[0] in the full file


def strip_oft_off_blocks(text: str) -> str:
    """Blank out ``<!-- oft:off --> ... <!-- oft:on -->`` regions.

    Line numbers stay aligned because each match is replaced with the same
    count of newlines it contained. Lint rules that scan the raw text apply
    this first so suppressed regions don't trigger findings.
    """

    def _blank(match: re.Match[str]) -> str:
        return "\n" * match.group().count("\n")

    return _OFT_OFF_BLOCK_RE.sub(_blank, text)


def _split_sections(lines: list[str]) -> list[_SectionSpec]:
    """Split file lines into sections on H2 headers.

    Content before the first H2 becomes a preamble section with ``header=None``.
    """
    sections: list[_SectionSpec] = []
    cur_header: str | None = None
    cur_header_line: int | None = None
    cur_body: list[str] = []
    cur_body_start = 1

    for i, line in enumerate(lines, start=1):
        m = _H2_RE.match(line)
        if m:
            sections.append(
                _SectionSpec(
                    header=cur_header,
                    header_line=cur_header_line,
                    body_lines=cur_body,
                    body_start_line=cur_body_start,
                )
            )
            cur_header = m.group(1).strip()
            cur_header_line = i
            cur_body = []
            cur_body_start = i + 1
        else:
            cur_body.append(line)

    sections.append(
        _SectionSpec(
            header=cur_header,
            header_line=cur_header_line,
            body_lines=cur_body,
            body_start_line=cur_body_start,
        )
    )
    return sections


def _parse_items(
    section_lines: list[str],
    body_start_line: int,
    source_file: Path,
) -> list[SpecItem]:
    """Parse spec items within a section's body lines."""
    id_anchors: list[tuple[int, re.Match[str]]] = []
    for i, line in enumerate(section_lines):
        m = _BACKTICKED_ID_LINE_RE.match(line)
        if m:
            id_anchors.append((i, m))

    items: list[SpecItem] = []
    for k, (id_idx, id_match) in enumerate(id_anchors):
        doctype = id_match.group(1)
        name = id_match.group(2)
        revision = int(id_match.group(3))
        spec_id = f"{doctype}~{name}~{revision}"

        title = _find_title(section_lines, id_idx, id_anchors, k)
        body_end = _find_body_end(section_lines, id_idx, id_anchors, k)

        body_lines = section_lines[id_idx:body_end]
        fields = _parse_fields(body_lines)

        items.append(
            SpecItem(
                id=spec_id,
                doctype=doctype,
                name=name,
                revision=revision,
                title=title,
                status=fields["status"],
                description=fields["description"],
                rationale=fields["rationale"],
                covers=fields["covers"],
                needs=fields["needs"],
                source_file=source_file,
                source_line=body_start_line + id_idx,
                interfaces=fields["interfaces"],
                agent_reviews=fields["agent_reviews"],
                raw_body="\n".join(body_lines),
            )
        )
    return items


def _find_title(
    section_lines: list[str],
    id_idx: int,
    id_anchors: list[tuple[int, re.Match[str]]],
    k: int,
) -> str:
    """Return the nearest preceding ATX heading title, or '' if none."""
    floor = id_anchors[k - 1][0] + 1 if k > 0 else 0
    for j in range(id_idx - 1, floor - 1, -1):
        m = _HEADING_RE.match(section_lines[j])
        if m:
            return m.group(2).strip()
    return ""


def _find_body_end(
    section_lines: list[str],
    id_idx: int,
    id_anchors: list[tuple[int, re.Match[str]]],
    k: int,
) -> int:
    """Return the exclusive index where this item's body ends."""
    hard_end = (
        id_anchors[k + 1][0] if k + 1 < len(id_anchors) else len(section_lines)
    )

    body_end = hard_end
    # Walk back from the next item's ID: any heading sitting just above it
    # belongs to the next item, not this one.
    j = hard_end - 1
    while j > id_idx:
        line = section_lines[j]
        if not line.strip():
            j -= 1
            continue
        if _HEADING_RE.match(line):
            body_end = j
            j -= 1
            continue
        break

    # Any hrule between this item and body_end terminates the body earlier.
    for j in range(id_idx + 1, body_end):
        if _HRULE_RE.match(section_lines[j]):
            body_end = j
            break
    return body_end


def _parse_fields(body_lines: list[str]) -> dict:
    """Extract OFT keyword fields from item body lines.

    ``body_lines[0]`` is the ID line and is skipped. Lines before any keyword
    contribute to ``description``; a recognized ``Keyword:`` line opens a field
    and subsequent non-keyword lines continue that field until the next
    keyword.
    """
    status = ""
    rationale = ""
    covers: list[str] = []
    needs: list[str] = []
    interfaces: list[str] = []
    agent_reviews: list[str] = []
    description_parts: list[str] = []
    explicit_description: list[str] = []

    cur_key: str | None = None
    cur_buf: list[str] = []

    def flush() -> None:
        nonlocal status, rationale
        if cur_key is None:
            return
        value = "\n".join(cur_buf).strip()
        if cur_key == "Status":
            status = value.lower()
        elif cur_key == "Needs":
            for n in value.split(","):
                n = n.strip()
                if n:
                    needs.append(n)
        elif cur_key == "Covers":
            for line in value.splitlines():
                s = line.strip().lstrip("-*+").strip()
                if s:
                    covers.append(s)
        elif cur_key == "Rationale":
            rationale = value
        elif cur_key == "Interface":
            if value:
                interfaces.append(value)
        elif cur_key == "AgentReview":
            if value:
                agent_reviews.append(value)
        elif cur_key == "Description" and value:
            explicit_description.append(value)
        # Comment, Tags, Depends — parsed but not surfaced in SpecItem today

    for line in body_lines[1:]:
        m = _KEYWORD_LINE_RE.match(line)
        if m and m.group(1) in _KNOWN_KEYWORDS:
            flush()
            cur_key = m.group(1)
            rest = m.group(2)
            cur_buf = [rest] if rest else []
        elif not line.strip():
            # Blank line terminates the current keyword's value.
            flush()
            cur_key = None
            cur_buf = []
        else:
            if cur_key is None:
                description_parts.append(line)
            else:
                cur_buf.append(line)
    flush()

    if explicit_description:
        description = "\n".join(explicit_description).strip()
    else:
        description = "\n".join(description_parts).strip()

    return {
        "status": status,
        "description": description,
        "rationale": rationale,
        "covers": covers,
        "needs": needs,
        "interfaces": interfaces,
        "agent_reviews": agent_reviews,
    }
