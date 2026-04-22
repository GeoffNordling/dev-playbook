"""Obligation-keyword lint rules.

Rules:
    lint.bare-obligation     SHALL/SHOULD/MAY outside backticks
    lint.mixed-obligations   multiple obligation levels in one item
"""

from __future__ import annotations

import re

from sdd_tools.models import Finding, SpecFile

_OBLIGATION_BARE_RE = re.compile(r"\b(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)\b")
_OBLIGATION_BACKTICK_RE = re.compile(r"`(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)`")
_BACKTICK_SPAN_RE = re.compile(r"`[^`]+`")

_OBLIGATION_LEVEL = {
    "SHALL": "mandatory",
    "SHALL NOT": "mandatory",
    "SHOULD": "preferred",
    "SHOULD NOT": "preferred",
    "MAY": "optional",
}


def check(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(_check_bare_obligations(spec_file, raw_text))
    findings.extend(_check_mixed_obligations(spec_file))
    return findings


def _check_bare_obligations(spec_file: SpecFile, raw_text: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_num, line in enumerate(raw_text.splitlines(), start=1):
        stripped = _BACKTICK_SPAN_RE.sub("", line)
        for match in _OBLIGATION_BARE_RE.finditer(stripped):
            findings.append(
                Finding(
                    rule="lint.bare-obligation",
                    file=spec_file.path,
                    line=line_num,
                    message=(
                        f"bare obligation keyword '{match.group()}' must be "
                        "wrapped in backticks"
                    ),
                )
            )
    return findings


def _check_mixed_obligations(spec_file: SpecFile) -> list[Finding]:
    findings: list[Finding] = []
    for item in spec_file.all_items():
        keywords = {
            m.group(1) for m in _OBLIGATION_BACKTICK_RE.finditer(item.raw_body)
        }
        levels = {_OBLIGATION_LEVEL[kw] for kw in keywords}
        if len(levels) > 1:
            found = ", ".join(sorted(keywords))
            findings.append(
                Finding(
                    rule="lint.mixed-obligations",
                    file=spec_file.path,
                    line=item.source_line,
                    line_kind="item header",
                    spec_id=item.id,
                    message=f"mixed obligation levels ({found})",
                    fix="use a single obligation level per item",
                )
            )
    return findings
