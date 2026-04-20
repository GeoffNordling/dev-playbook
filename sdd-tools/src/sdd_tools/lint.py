"""Structural lint of OFT spec markdown.

Operates on raw markdown only — no SpecItem dependency, no JAR. Emits Finding
objects per rule per offending location.

Rules:
    lint.fenced-code        triple-backtick blocks (break OFT parsing)
    lint.bare-obligation    SHALL/SHOULD/MAY outside backticks
    lint.bad-id             backtick token shaped like an ID but malformed
    lint.mixed-obligations  multiple obligation levels in one item
    lint.bad-status         missing or invalid Status field
    lint.bad-covers         malformed Covers: reference
    lint.bad-needs          unknown artifact type in Needs:
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from sdd_tools.models import KNOWN_ARTIFACT_TYPES, SPEC_ID_BARE_RE, Finding

VALID_STATUSES = frozenset({"draft", "proposed", "approved"})

_OFT_OFF_BLOCK_RE = re.compile(
    r"<!--\s*oft:off\s*-->.*?<!--\s*oft:on\s*-->",
    re.DOTALL,
)
_FENCED_CODE_BLOCK_RE = re.compile(r"^```", re.MULTILINE)
_OBLIGATION_BARE_RE = re.compile(r"\b(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)\b")
_OBLIGATION_BACKTICK_RE = re.compile(r"`(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)`")
_BACKTICK_SPAN_RE = re.compile(r"`[^`]+`")
_NEAR_MISS_ID_RE = re.compile(r"`[a-z][a-z0-9]*~[^`\s]+`")
_SPEC_ID_RE = re.compile(rf"`{SPEC_ID_BARE_RE.pattern}`")
_HRULE_RE = re.compile(r"^---\s*$", re.MULTILINE)
_STATUS_RE = re.compile(r"^Status:\s*(.+?)\s*$", re.MULTILINE)
_NEEDS_RE = re.compile(r"^Needs:\s*(.+)$", re.MULTILINE)
_COVERS_BLOCK_RE = re.compile(
    r"^Covers:[ \t]*\n((?:[ \t]*[-*+][ \t]+\S+[ \t]*\n?)+)", re.MULTILINE
)

_OBLIGATION_LEVEL = {
    "SHALL": "mandatory",
    "SHALL NOT": "mandatory",
    "SHOULD": "preferred",
    "SHOULD NOT": "preferred",
    "MAY": "optional",
}


@dataclass
class _Item:
    """Internal-to-lint representation of one parsed item."""

    id: str
    id_line: int
    body: str
    status: str = ""
    status_line: int = 0
    needs: list[tuple[str, int]] = field(default_factory=list)  # (value, line)
    covers: list[tuple[str, int]] = field(default_factory=list)  # (ref, line)


def lint_file(path: Path, raw_text: str) -> list[Finding]:
    """Run all lint checks against one spec file. Returns Finding list."""
    text = _strip_oft_off_blocks(raw_text)
    items = _parse_items(text)

    findings: list[Finding] = []
    findings.extend(_check_fenced_code(path, text))
    findings.extend(_check_bare_obligations(path, text))
    findings.extend(_check_id_format(path, text, items))
    findings.extend(_check_mixed_obligations(path, items))
    findings.extend(_check_status(path, items))
    findings.extend(_check_covers(path, items))
    findings.extend(_check_needs(path, items))
    return findings


def _strip_oft_off_blocks(text: str) -> str:
    """Replace <!-- oft:off --> blocks with blank lines so line numbers align."""

    def _blank(match: re.Match[str]) -> str:
        return "\n" * match.group().count("\n")

    return _OFT_OFF_BLOCK_RE.sub(_blank, text)


def _line_at(text: str, offset: int) -> int:
    """Return the 1-based line number at the given character offset."""
    return text.count("\n", 0, offset) + 1


def _parse_items(text: str) -> list[_Item]:
    """Lightweight per-item parse for lint. Tracks field line numbers."""
    items: list[_Item] = []
    segments = _HRULE_RE.split(text)
    line_offset = 0
    for segment in segments:
        id_match = _SPEC_ID_RE.search(segment)
        if id_match:
            items.append(_parse_one(segment, id_match, line_offset))
        line_offset += segment.count("\n") + 1
    return items


def _parse_one(segment: str, id_match: re.Match[str], line_offset: int) -> _Item:
    spec_id = f"{id_match.group(1)}~{id_match.group(2)}~{id_match.group(3)}"
    id_line_in_seg = segment[: id_match.start()].count("\n") + 1
    id_line = line_offset + id_line_in_seg

    item = _Item(id=spec_id, id_line=id_line, body=segment)

    status_match = _STATUS_RE.search(segment)
    if status_match:
        item.status = status_match.group(1).strip().lower()
        item.status_line = line_offset + _line_at(segment, status_match.start())

    needs_match = _NEEDS_RE.search(segment)
    if needs_match:
        needs_line = line_offset + _line_at(segment, needs_match.start())
        item.needs = [
            (n.strip(), needs_line)
            for n in needs_match.group(1).split(",")
            if n.strip()
        ]

    covers_match = _COVERS_BLOCK_RE.search(segment)
    if covers_match:
        covers_block_start = covers_match.start(1)
        for raw_line in covers_match.group(1).splitlines():
            ref = raw_line.strip().lstrip("-*+").strip()
            if not ref:
                continue
            ref_offset = segment.index(raw_line, covers_block_start)
            ref_line = line_offset + _line_at(segment, ref_offset)
            item.covers.append((ref, ref_line))

    return item


def _check_fenced_code(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        if _FENCED_CODE_BLOCK_RE.match(line):
            findings.append(
                Finding(
                    rule="lint.fenced-code",
                    file=path,
                    line=line_num,
                    message="fenced code block (```) breaks OFT parsing",
                    fix="use indented code blocks (4-space indent) instead",
                )
            )
    return findings


def _check_bare_obligations(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        stripped = _BACKTICK_SPAN_RE.sub("", line)
        for match in _OBLIGATION_BARE_RE.finditer(stripped):
            findings.append(
                Finding(
                    rule="lint.bare-obligation",
                    file=path,
                    line=line_num,
                    message=(
                        f"bare obligation keyword '{match.group()}' must be "
                        "wrapped in backticks"
                    ),
                )
            )
    return findings


def _check_id_format(
    path: Path, text: str, items: list[_Item]
) -> list[Finding]:
    """Flag backtick tokens that look like spec IDs but are malformed."""
    valid = {f"`{item.id}`" for item in items}
    findings: list[Finding] = []
    for match in _NEAR_MISS_ID_RE.finditer(text):
        token = match.group()
        if token in valid:
            continue
        bare = token[1:-1]
        if SPEC_ID_BARE_RE.fullmatch(bare):
            continue
        findings.append(
            Finding(
                rule="lint.bad-id",
                file=path,
                line=_line_at(text, match.start()),
                message=f"malformed spec ID {token}",
                fix="expected `type~name~revision`",
            )
        )
    return findings


def _check_mixed_obligations(
    path: Path, items: list[_Item]
) -> list[Finding]:
    findings: list[Finding] = []
    for item in items:
        keywords = {
            m.group(1) for m in _OBLIGATION_BACKTICK_RE.finditer(item.body)
        }
        levels = {_OBLIGATION_LEVEL[kw] for kw in keywords}
        if len(levels) > 1:
            found = ", ".join(sorted(keywords))
            findings.append(
                Finding(
                    rule="lint.mixed-obligations",
                    file=path,
                    line=item.id_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message=f"mixed obligation levels ({found})",
                    fix="use a single obligation level per item",
                )
            )
    return findings


def _check_status(path: Path, items: list[_Item]) -> list[Finding]:
    findings: list[Finding] = []
    expected = ", ".join(sorted(VALID_STATUSES))
    for item in items:
        if not item.status:
            findings.append(
                Finding(
                    rule="lint.bad-status",
                    file=path,
                    line=item.id_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message="missing Status field",
                    fix=f"add 'Status: <value>' (one of: {expected})",
                )
            )
        elif item.status not in VALID_STATUSES:
            findings.append(
                Finding(
                    rule="lint.bad-status",
                    file=path,
                    line=item.status_line,
                    spec_id=item.id,
                    message=f"invalid Status '{item.status}'",
                    fix=f"expected one of: {expected}",
                )
            )
    return findings


def _check_covers(path: Path, items: list[_Item]) -> list[Finding]:
    findings: list[Finding] = []
    for item in items:
        for ref, ref_line in item.covers:
            if not SPEC_ID_BARE_RE.fullmatch(ref):
                findings.append(
                    Finding(
                        rule="lint.bad-covers",
                        file=path,
                        line=ref_line,
                        spec_id=item.id,
                        message=f"malformed Covers reference '{ref}'",
                        fix="expected type~name~revision",
                    )
                )
    return findings


def _check_needs(path: Path, items: list[_Item]) -> list[Finding]:
    findings: list[Finding] = []
    for item in items:
        for value, line in item.needs:
            if value not in KNOWN_ARTIFACT_TYPES:
                findings.append(
                    Finding(
                        rule="lint.bad-needs",
                        file=path,
                        line=line,
                        spec_id=item.id,
                        message=f"unknown artifact type '{value}' in Needs:",
                        fix=(
                            "expected one of: "
                            + ", ".join(sorted(KNOWN_ARTIFACT_TYPES))
                        ),
                    )
                )
    return findings
