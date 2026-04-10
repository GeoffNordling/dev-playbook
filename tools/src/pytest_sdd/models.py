"""Shared data types and regex patterns for pytest-sdd."""

import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# OFT off-block markers
# ---------------------------------------------------------------------------

# Matches <!-- oft:off --> ... <!-- oft:on --> blocks (including content)
OFT_OFF_BLOCK_RE = re.compile(
    r"<!--\s*oft:off\s*-->.*?<!--\s*oft:on\s*-->",
    re.DOTALL,
)


def strip_oft_off_blocks(text: str) -> str:
    """Remove content between <!-- oft:off --> and <!-- oft:on --> markers.

    Replaces each off-block with the equivalent number of blank lines so that
    line numbers in error messages remain accurate.
    """
    def _blank_lines(match: "re.Match[str]") -> str:
        return "\n" * match.group().count("\n")

    return OFT_OFF_BLOCK_RE.sub(_blank_lines, text)


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# OFT spec item ID in backticks: `type~name~revision`
# name: starts with a letter, then letters/digits/hyphens/underscores/dots
#       (no consecutive dots)
_NAME_CHARS = r"(?:[a-zA-Z0-9_-]|\.(?!\.))*"
SPEC_ID_RE = re.compile(rf"`([a-z]+)~([a-zA-Z]{_NAME_CHARS})~(\d+)`")

# Bare OFT ID (no backticks) — used for validating Covers: references
SPEC_ID_BARE_RE = re.compile(rf"([a-z]+)~([a-zA-Z]{_NAME_CHARS})~(\d+)")

# "Near-miss" IDs: backtick content with tildes that may be malformed spec IDs
NEAR_MISS_ID_RE = re.compile(r"`[a-z][a-z0-9]*~[^`\s]+`")

# Obligation keywords wrapped in backticks
OBLIGATION_BACKTICK_RE = re.compile(r"`(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)`")

# Bare obligation keywords (for stripping and then detecting)
OBLIGATION_BARE_RE = re.compile(r"\b(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)\b")

# Backtick spans (for stripping before bare-keyword scan)
BACKTICK_SPAN_RE = re.compile(r"`[^`]+`")

# Status field
STATUS_RE = re.compile(r"^Status:\s*(\S+)\s*$", re.MULTILINE)

# Needs field (inline, comma-separated): "Needs: dsn, utest"
NEEDS_RE = re.compile(r"^Needs:\s*(.+)$", re.MULTILINE)

# Covers block: "Covers:\n  - ref\n  - ref"
COVERS_RE = re.compile(r"^Covers:\s*\n((?:[ \t]*[-*+][ \t]+\S+[ \t]*\n?)+)", re.MULTILINE)

# Heading patterns
H3_RE = re.compile(r"^###\s+(.+)$", re.MULTILINE)

# Horizontal rule (section separator between spec items)
HRULE_RE = re.compile(r"^---\s*$", re.MULTILINE)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_STATUSES = frozenset({"draft", "proposed", "approved"})

KNOWN_ARTIFACT_TYPES = frozenset({
    "feat", "req", "arch", "dsn", "impl",
    "utest", "itest", "stest", "sman", "oman",
})

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class SpecItem:
    """A single OFT specification item parsed from a markdown file."""

    id: str              # "req~ing.allowlist-check~1"
    item_type: str       # "req"
    name: str            # "ing.allowlist-check"
    revision: int        # 1
    title: str           # "Allowlist Check" (from ### heading before ID)
    status: str          # "approved" (or "" if missing/malformed)
    body: str            # full segment text (for obligation scanning)
    needs: list[str] = field(default_factory=list)    # ["dsn", "utest"] or []
    covers: list[str] = field(default_factory=list)   # ["req~area.name~1", ...] or []
    source_file: str = ""   # absolute file path
    line_number: int = 0    # line number of the ID line in the file
