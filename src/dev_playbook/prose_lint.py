"""Audit authored Markdown prose against the workspace prose standard.

prose-lint is the detector behind the Prose card. It walks a repo's Markdown
files once (via dev_playbook.md.find_md_files, so gitignore-aware and
worktree-scoped) and applies one deterministic rule:

  - **judgment-spelling** — the house spelling is American ``judgment``; the
    British ``judgement`` / ``judgements`` is flagged. The check runs over prose
    *outside* fenced blocks and inline code spans, so an identifier or a doc
    that must name the forbidden form in backticks does not self-trip.

Scope is **all authored Markdown, harness files included** (``CLAUDE.md``,
rules, skills) — deliberately wider than ``md.classify``'s concept-only split,
since the spelling is house-wide. Two kinds of content are excluded, both via
the shared dev_playbook.external registry: externally-managed vendored trees
(``is_externally_managed``) and verbatim upstream mirrors (``is_verbatim_doc``,
i.e. ``type: Reference`` documents).

Output:
    stdout — one finding per line, ``file:line: prose.rule message``.
    stderr — one human-readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    prose-lint [directory]
    prose-lint --list-rules
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from dev_playbook import md
from dev_playbook.external import is_externally_managed, is_verbatim_doc
from dev_playbook.findings import print_rules, render

# The one rule id this detector emits, namespaced by the Prose card whose
# question it answers. Kept a module-level constant so every emission site
# references it, never a raw literal, and RULES (what --list-rules prints)
# cannot drift from what the detector emits.
JUDGMENT_SPELLING = "prose.judgment-spelling"

RULES = (JUDGMENT_SPELLING,)

# The British form: the word "judgement", optionally pluralized, as a whole word
# so "judgemental" and the American "judgment" are both left alone. Matched
# case-insensitively so a sentence-initial "Judgement" is caught too.
JUDGEMENT_PATTERN = re.compile(r"\bjudgements?\b", re.IGNORECASE)

JUDGMENT_MESSAGE = "British `judgement`/`judgements`; the house spelling is `judgment`"


@dataclass(frozen=True)
class Finding:
    """One nonconformance: a repo-relative location, a rule id, and a message."""

    file: str
    line: int
    rule: str
    message: str

    def render(self) -> str:
        """The finding as one GNU-format line."""
        return render(self.file, self.rule, self.message, self.line)


def scan_text(rel: str, text: str) -> list[Finding]:
    """Flag every British judgement / judgements in prose outside code.

    Fenced blocks are dropped by ``md.lines_outside_fences``; inline code spans
    are stripped per line before matching, so a backticked mention of the
    forbidden form does not trip. One finding per occurrence, line numbers
    matching what an editor shows.
    """
    findings: list[Finding] = []
    for line_num, line in md.lines_outside_fences(text):
        prose = md.INLINE_CODE_PATTERN.sub("", line)
        for _ in JUDGEMENT_PATTERN.finditer(prose):
            findings.append(Finding(rel, line_num, JUDGMENT_SPELLING, JUDGMENT_MESSAGE))
    return findings


def scan_file(path: Path, root: Path) -> list[Finding]:
    """Every finding one Markdown file yields; verbatim mirrors are skipped."""
    rel = str(path.relative_to(root))
    text = path.read_text(encoding="utf-8", errors="replace")
    frontmatter, _ = md.parse_frontmatter(text)
    if is_verbatim_doc(frontmatter):
        return []
    return scan_text(rel, text)


def audit(root: Path) -> list[Finding]:
    """Scan every authored Markdown file under ``root`` for the spelling rule.

    Externally-managed vendored trees are excluded by path; verbatim Reference
    docs are excluded per file in ``scan_file``.
    """
    findings: list[Finding] = []
    for path in md.find_md_files(root):
        rel = str(path.relative_to(root))
        if is_externally_managed(rel):
            continue
        findings.extend(scan_file(path, root))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Scan a repo's Markdown and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="prose-lint",
        description="Lint authored Markdown prose: judgment spelling.",
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
        findings = audit(root)
    except subprocess.CalledProcessError as err:
        print(f"prose-lint: cannot list files in {root}: {err}", file=sys.stderr)
        return 2

    for f in sorted(findings, key=lambda f: (f.file, f.line, f.rule)):
        print(f.render())

    if findings:
        print(f"prose-lint: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print("prose-lint: clean", file=sys.stderr)
    return 0
