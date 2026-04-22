"""Syntactic lint rules.

Rules:
    lint.fenced-code   triple-backtick blocks (break OFT parsing)
    lint.bad-covers    malformed Covers: reference
    lint.bad-needs     unknown artifact type in Needs:
"""

from __future__ import annotations

import re

from sdd_tools.models import KNOWN_ARTIFACT_TYPES, SPEC_ID_BARE_RE, Finding, SpecFile

_FENCED_CODE_BLOCK_RE = re.compile(r"^```", re.MULTILINE)
_COVERS_BLOCK_RE = re.compile(
    r"^Covers:[ \t]*\n((?:[ \t]*[-*+][ \t]+\S+[ \t]*\n?)+)", re.MULTILINE
)
_LINE_AT_CACHE: dict[int, int] = {}


def check(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_check_fenced_code(spec_file, raw_text))
    findings.extend(_check_covers(spec_file))
    findings.extend(_check_needs(spec_file))
    return findings


def _check_fenced_code(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_num, line in enumerate(raw_text.splitlines(), start=1):
        if _FENCED_CODE_BLOCK_RE.match(line):
            findings.append(
                Finding(
                    rule="lint.fenced-code",
                    file=spec_file.path,
                    line=line_num,
                    message="fenced code block (```) breaks OFT parsing",
                    fix="use indented code blocks (4-space indent) instead",
                )
            )
    return findings


def _check_covers(spec_file: SpecFile) -> list[Finding]:
    """Flag malformed Covers: references using the parsed item bodies."""
    findings: list[Finding] = []
    for item in spec_file.all_items():
        for ref in item.covers:
            if not SPEC_ID_BARE_RE.fullmatch(ref):
                line = _locate_covers_ref_line(item.raw_body, ref, item.source_line)
                findings.append(
                    Finding(
                        rule="lint.bad-covers",
                        file=spec_file.path,
                        line=line,
                        spec_id=item.id,
                        message=f"malformed Covers reference '{ref}'",
                        fix="expected type~name~revision",
                    )
                )
    return findings


def _check_needs(spec_file: SpecFile) -> list[Finding]:
    findings: list[Finding] = []
    for item in spec_file.all_items():
        for value in item.needs:
            if value not in KNOWN_ARTIFACT_TYPES:
                line = _locate_needs_line(item.raw_body, item.source_line)
                findings.append(
                    Finding(
                        rule="lint.bad-needs",
                        file=spec_file.path,
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


def _locate_covers_ref_line(raw_body: str, ref: str, base_line: int) -> int:
    """Return the file line number of the bullet line holding ``ref``."""
    for offset, line in enumerate(raw_body.splitlines()):
        stripped = line.strip().lstrip("-*+").strip()
        if stripped == ref:
            return base_line + offset
    return base_line


def _locate_needs_line(raw_body: str, base_line: int) -> int:
    """Return the file line number of the ``Needs:`` line."""
    for offset, line in enumerate(raw_body.splitlines()):
        if line.startswith("Needs:"):
            return base_line + offset
    return base_line
