"""Shared data types for sdd_tools.

SpecItem -- canonical representation of one OFT spec item, produced by the JAR.
Finding  -- canonical output of every validator. Replaces ad-hoc list[str].
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# OFT spec ID without surrounding backticks: type~name~revision.
# name starts with a letter, then letters/digits/hyphens/underscores/dots
# (consecutive dots disallowed).
_NAME_CHARS = r"(?:[a-zA-Z0-9_-]|\.(?!\.))*"
SPEC_ID_BARE_RE = re.compile(rf"([a-z]+)~([a-zA-Z]{_NAME_CHARS})~(\d+)")

KNOWN_ARTIFACT_TYPES = frozenset(
    {
        "feat",
        "req",
        "arch",
        "dsn",
        "impl",
        "utest",
        "itest",
        "stest",
        "uman",
        "oman",
    }
)


@dataclass
class SpecItem:
    """One OFT specification item, parsed from the JAR's XML output."""

    id: str  # "dsn~parser.session~1"
    doctype: str  # "req", "dsn", "feat", "utest", "itest", ...
    name: str  # "parser.session"
    revision: int  # 1
    title: str  # from <shortdesc>; may be empty
    status: str  # "approved" / "draft" / "proposed" / ""
    description: str  # from <description>
    rationale: str  # from <rationale>
    covers: list[str]  # full upstream IDs ("req~area.name~1")
    needs: list[str]  # downstream artifact types ("utest", "dsn")
    source_file: Path
    source_line: int
    interfaces: list[str] = field(default_factory=list)
    # parsed from description; empty for non-dsn items


@dataclass(frozen=True)
class Finding:
    """One validator finding. Renders to a single block in failure output."""

    rule: str  # "interface.mismatch", "lint.fenced-code", ...
    file: Path  # relative to project root
    line: int  # best-available anchor line
    message: str  # one line
    line_kind: str | None = None  # "dsn header" when line is not the exact site
    spec_id: str | None = None
    detail: str | None = None  # multi-line block
    fix: str | None = None  # one-line guidance

    def render(self) -> str:
        """Render this finding as the text block shown in failure output."""
        anchor = f"{self.file}:{self.line}"
        if self.line_kind:
            anchor = f"{anchor} ({self.line_kind})"
        head = f"{anchor}  {self.rule}  {self.message}"
        body_lines: list[str] = []
        if self.detail:
            for line in self.detail.splitlines():
                body_lines.append(f"  {line}")
        if self.fix:
            body_lines.append(f"  fix:       {self.fix}")
        if not body_lines:
            return head
        return head + "\n" + "\n".join(body_lines)


def render_findings(findings: list[Finding]) -> str:
    """Render a list of findings into a multi-block text report."""
    return "\n".join(f.render() for f in findings)
