"""Audit a repo's Decision Records against the records contract.

decisions-audit is the detector behind the Decision Records card. It walks a
repo's markdown files once (via dev_playbook.md.find_md_files, so gitignore-aware
and worktree-scoped), keeps the ones under ``docs/decisions/``, and applies two
rules:

  - **sequential-numbering** — the ``NNNN-slug.md`` record files number
    contiguously from ``0001``, each zero-padded to four digits, with no
    duplicates. ``index.md``, ``README.md``, and any other filename carry no
    number and are ignored.
  - **status-vocabulary** — a record's optional ``status`` frontmatter key, when
    present, holds one of ``proposed | accepted | deprecated | superseded by
    NNNN`` (NNNN a 4-digit, zero-padded record number).

An absent ``docs/decisions/`` passes both rules — the directory is lazily
created. Frontmatter shape and index freshness are okf-audit's, not this
detector's.

See standards/decisions/records.md for the contract these rules enforce.

Output:
    stdout — one finding per line, ``file:line: decisions.rule message``.
    stderr — one human-readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    decisions-audit [directory]
    decisions-audit --list-rules
"""

import argparse
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import md
from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the decisions card whose
# question it answers. Each id is a module-level constant so every emission site
# references the constant, never a raw literal, and RULES (what --list-rules
# prints) cannot drift from what the detector actually emits.
SEQUENTIAL_NUMBERING = "decisions.sequential-numbering"
STATUS_VOCABULARY = "decisions.status-vocabulary"

RULES = (SEQUENTIAL_NUMBERING, STATUS_VOCABULARY)

# The records directory, relative to the repo root; also the location a
# directory-level gap finding reports against.
DECISIONS_DIR = "docs/decisions"

# A record file: a numeric prefix, a hyphen, a slug, then ``.md``. The prefix is
# captured so its padding and contiguity can be checked; index.md/README.md and
# any other unnumbered filename do not match and are ignored.
_RECORD_NAME = re.compile(r"^(\d+)-.+\.md$")

# The status vocabulary: three fixed words plus the parameterized supersession
# form, whose NNNN is a 4-digit, zero-padded record number.
_FIXED_STATUSES = frozenset({"proposed", "accepted", "deprecated"})
_SUPERSEDED = re.compile(r"^superseded by \d{4}$")

_VOCABULARY = "proposed | accepted | deprecated | superseded by NNNN"


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a repo-relative location, a rule id, and a message."""

    file: str
    line: int | None
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message, self.line)


def decision_files(root: Path) -> list[Path]:
    """The markdown files under ``docs/decisions/`` in ``root``'s checkout."""
    return [
        path
        for path in md.find_md_files(root)
        if path.relative_to(root).parts[:2] == ("docs", "decisions")
    ]


# --- sequential-numbering rule ---


def check_sequential_numbering(files: list[Path], root: Path) -> list[Finding]:
    """Flag non-zero-padded, duplicate, and missing record numbers.

    Zero-padding and duplication attach to the offending record file; a gap in
    the sequence attaches to the records directory, since no single file owns it.
    """
    numbered: list[tuple[int, str, str]] = []
    for path in files:
        match = _RECORD_NAME.match(path.name)
        if match is None:
            continue
        rel = str(path.relative_to(root))
        numbered.append((int(match.group(1)), match.group(1), rel))

    findings: list[Finding] = []
    counts = Counter(number for number, _, _ in numbered)
    for number, prefix, rel in numbered:
        if len(prefix) != 4:
            findings.append(
                Finding(
                    rel,
                    None,
                    SEQUENTIAL_NUMBERING,
                    f"record number '{prefix}' is not zero-padded to four digits",
                )
            )
        if counts[number] > 1:
            findings.append(
                Finding(
                    rel,
                    None,
                    SEQUENTIAL_NUMBERING,
                    f"record number {number:04d} is duplicated",
                )
            )

    present = set(counts)
    for missing in sorted(set(range(1, max(present) + 1)) - present) if present else []:
        findings.append(
            Finding(
                DECISIONS_DIR,
                None,
                SEQUENTIAL_NUMBERING,
                f"record number {missing:04d} is missing from the sequence",
            )
        )
    return findings


# --- status-vocabulary rule ---


def check_status_vocabulary(files: list[Path], root: Path) -> list[Finding]:
    """Flag a record whose ``status`` frontmatter key is off the vocabulary."""
    findings: list[Finding] = []
    for path in files:
        front, _ = md.parse_frontmatter(
            path.read_text(encoding="utf-8", errors="replace")
        )
        if not front or "status" not in front:
            continue
        status = front["status"]
        if not _is_valid_status(status):
            findings.append(
                Finding(
                    str(path.relative_to(root)),
                    None,
                    STATUS_VOCABULARY,
                    f"status {status!r} is not one of {_VOCABULARY}",
                )
            )
    return findings


def _is_valid_status(status: object) -> bool:
    """True when ``status`` is a fixed word or a padded supersession phrase."""
    return isinstance(status, str) and (
        status in _FIXED_STATUSES or _SUPERSEDED.fullmatch(status) is not None
    )


# --- the walk ---


def main(argv: list[str] | None = None) -> int:
    """Scan a repo's Decision Records and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="decisions-audit",
        description="Lint Decision Records: sequential-numbering, status-vocabulary.",
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--list-rules",
        action="store_true",
        help="print the rule ids this detector can emit, one per line, and exit",
    )
    args = parser.parse_args(argv)
    if args.list_rules:
        return print_rules(RULES)
    root = Path(args.directory).resolve()

    try:
        files = decision_files(root)
    except subprocess.CalledProcessError as err:
        print(f"decisions-audit: cannot list files in {root}: {err}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    findings.extend(check_sequential_numbering(files, root))
    findings.extend(check_status_vocabulary(files, root))

    for f in sorted(findings, key=lambda f: (f.file, f.line or 0, f.rule)):
        print(f.render())

    if findings:
        print(
            f"decisions-audit: {len(findings)} finding(s) in {DECISIONS_DIR}",
            file=sys.stderr,
        )
        return 1
    print(
        f"decisions-audit: clean ({len(files)} file(s) under {DECISIONS_DIR})",
        file=sys.stderr,
    )
    return 0
