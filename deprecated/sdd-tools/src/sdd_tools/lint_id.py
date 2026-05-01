"""ID-format and Status lint rules.

Rules:
    lint.bad-id       backtick tokens shaped like an ID but malformed
    lint.bad-status   missing or invalid Status field on a spec item
"""

from __future__ import annotations

import re

from sdd_tools.models import SPEC_ID_BARE_RE, Finding, SpecFile

VALID_STATUSES = frozenset({"draft", "proposed", "approved"})

_NEAR_MISS_ID_RE = re.compile(r"`[a-z][a-z0-9]*~[^`\s]+`")


def check(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_check_id_format(spec_file, raw_text))
    findings.extend(_check_status(spec_file))
    return findings


def _check_id_format(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    """Flag backtick tokens that look like spec IDs but are malformed."""
    valid = {f"`{item.id}`" for item in spec_file.all_items()}
    findings: list[Finding] = []
    for match in _NEAR_MISS_ID_RE.finditer(raw_text):
        token = match.group()
        if token in valid:
            continue
        bare = token[1:-1]
        if SPEC_ID_BARE_RE.fullmatch(bare):
            continue
        findings.append(
            Finding(
                rule="lint.bad-id",
                file=spec_file.path,
                line=_line_at(raw_text, match.start()),
                message=f"malformed spec ID {token}",
                fix="expected `type~name~revision`",
            )
        )
    return findings


def _check_status(spec_file: SpecFile) -> list[Finding]:
    findings: list[Finding] = []
    expected = ", ".join(sorted(VALID_STATUSES))
    for item in spec_file.all_items():
        if not item.status:
            findings.append(
                Finding(
                    rule="lint.bad-status",
                    file=spec_file.path,
                    line=item.source_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message="missing Status field",
                    fix=f"add 'Status: <value>' (one of: {expected})",
                )
            )
        elif item.status not in VALID_STATUSES:
            status_line = _locate_status_line(item.raw_body, item.source_line)
            findings.append(
                Finding(
                    rule="lint.bad-status",
                    file=spec_file.path,
                    line=status_line,
                    spec_id=item.id,
                    message=f"invalid Status '{item.status}'",
                    fix=f"expected one of: {expected}",
                )
            )
    return findings


def _line_at(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _locate_status_line(raw_body: str, base_line: int) -> int:
    for offset, line in enumerate(raw_body.splitlines()):
        if line.startswith("Status:"):
            return base_line + offset
    return base_line
