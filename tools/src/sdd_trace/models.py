"""Shared types, constants, regex patterns, and helpers for sdd-trace."""

import bisect
import re
from dataclasses import dataclass, field
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MANDATORY_OBLIGATIONS = frozenset({"SHALL", "SHALL NOT"})

# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------


@dataclass
class FunctionalReq:
    """A requirement parsed from a definition site in a functional spec."""

    sources: list[str] = field(default_factory=list)
    obligation: str = ""  # "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "MAY"
    all_obligations: frozenset[str] = field(default_factory=frozenset)

    @property
    def mandatory(self) -> bool:
        return self.obligation in MANDATORY_OBLIGATIONS


# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

REQ_ID_PATTERN = re.compile(r"\bREQ-[A-Z]{3,6}-\d{3}\b")
MARKER_PATTERN = re.compile(r'@pytest\.mark\.req\(\s*["\'](.+?)["\']\s*\)')
MULTI_MARKER_PATTERN = re.compile(r"@pytest\.mark\.req\(\s*\[(.+?)\]\s*\)", re.DOTALL)
STRING_IN_LIST = re.compile(r'["\'](.+?)["\']')

# Definition site: **REQ-XXX-NNN**: (bold ID + colon)
DEFINITION_SITE_PATTERN = re.compile(r"\*\*(REQ-[A-Z]{3,6}-\d{3})\*\*:")

# Obligation keyword inside backticks (multi-word forms first)
OBLIGATION_PATTERN = re.compile(r"`(SHALL NOT|SHOULD NOT|SHALL|SHOULD|MAY)`")

# Text-block terminators
_HEADING_PATTERN = re.compile(r"^#{1,6}\s", re.MULTILINE)
_HRULE_PATTERN = re.compile(r"^---\s*$", re.MULTILINE)

# Near-miss patterns for validation
_MALFORMED_LONG_AREA = re.compile(r"\bREQ-[A-Z]{7,}-\d{3}\b")
_MALFORMED_SHORT_AREA = re.compile(r"\bREQ-[A-Z]{1,2}-\d{3}\b")
_MALFORMED_NO_PREFIX = re.compile(r"(?<![-A-Z])[A-Z]{3,6}-\d{3}\b")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def extract_area_code(req_id: str) -> str:
    """Extract area code from REQ-<AREA>-NNN. E.g., 'REQ-TRANS-001' → 'TRANS'."""
    return req_id.split("-")[1]


def find_md_files(specs_dir: Path, name: str) -> list[Path]:
    """Locate markdown files for a spec artifact (e.g., 'functional_requirements', 'design').

    Checks (in priority order):
    1. specs/<name>/ directory (split structure, requires index.md)
    2. specs/<name>.md (single file)

    Returns list of markdown files found, or empty list if no structure found.
    """
    split_dir = specs_dir / name
    single_file = specs_dir / f"{name}.md"

    if split_dir.is_dir():
        if (split_dir / "index.md").is_file():
            return list(split_dir.glob("*.md"))
        raise FileNotFoundError(f"{split_dir} exists but has no index.md")
    elif single_file.is_file():
        return [single_file]

    return []


# ---------------------------------------------------------------------------
# Text-block extraction
# ---------------------------------------------------------------------------


def text_block_boundaries(text: str) -> list[int]:
    """Return sorted start positions of all text-block terminators in *text*.

    Terminators are: definition sites, markdown headings, horizontal rules, and EOF.
    """
    positions: list[int] = []
    for m in DEFINITION_SITE_PATTERN.finditer(text):
        positions.append(m.start())
    for m in _HEADING_PATTERN.finditer(text):
        positions.append(m.start())
    for m in _HRULE_PATTERN.finditer(text):
        positions.append(m.start())
    positions.append(len(text))  # sentinel: end of file
    return sorted(positions)


def extract_text_block(text: str, start: int, boundaries: list[int]) -> str:
    """Return the text block starting at *start*, ending at the next boundary."""
    idx = bisect.bisect_right(boundaries, start)
    end = boundaries[idx] if idx < len(boundaries) else len(text)
    return text[start:end]
