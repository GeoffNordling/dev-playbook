"""Audit authored content against the workspace prose standard.

prose-lint is the detector behind the Prose card. It walks a repo's files once
(via dev_playbook.md.find_files, so gitignore-aware and worktree-scoped) and
applies two deterministic rules:

  - **judgment-spelling** — the house spelling is American ``judgment``; the
    British ``judgement`` / ``judgements`` is flagged. The check runs over
    authored Markdown prose *outside* fenced blocks and inline code spans, so
    an identifier or a doc that must name the forbidden form in backticks does
    not self-trip.
  - **banned-word** — the person operating the workspace is the ``user``; the
    actor noun ``human`` (bare, plural, or hyphenated compound, any case)
    appears in no authored file (prose/conventions.md — Terminology). The ban
    is absolute, so the check runs over every tracked file of every type,
    whole-file — frontmatter, fenced blocks, and inline code spans included;
    there is no backtick escape hatch.

Scope is **all authored content, harness files included** (``CLAUDE.md``,
rules, skills; for the banned-word rule, code and config too). What is out is
``md.classify``'s ``"excluded"`` category: externally-managed vendored trees
(which ``classify`` decides through the shared dev_playbook.external registry)
and transient scratch (``PLAN.md`` / ``PROGRESS.md``, the root ``tmp/`` tree).
Verbatim upstream mirrors are excluded per file via the registry's
``is_verbatim_doc`` (``type: Reference`` documents). Symlinks are skipped: a
link's content belongs to its target, which is scanned at its own path when
authored here and is not ours when vendored. Beyond those structural
exclusions, each repo declares its own: a tracked root-level
``.prose-lint-exempt`` lists the paths — files or whole directories — that
both rules skip (dev-playbook's own lists this module and its test file,
which must name the banned word to ban it).

Output:
    stdout — one finding per line, ``file:line: prose.rule message``.
    stderr — one readable summary line.
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

import yaml

from dev_playbook import md
from dev_playbook.external import is_verbatim_doc
from dev_playbook.findings import print_rules, render


class CannotRun(Exception):
    """A file the detector cannot process — surfaced as exit 2, not a traceback.

    Matches the sibling frontmatter-parsing detectors (decisions-lint,
    standards-lint): a malformed ``.md`` is a run failure to report, never an
    uncaught YAML error that blocks every commit.
    """


# The rule ids this detector emits, namespaced by the Prose card whose
# questions they answer. Kept module-level constants so every emission site
# references them, never a raw literal, and RULES (what --list-rules prints)
# cannot drift from what the detector emits.
JUDGMENT_SPELLING = "prose.judgment-spelling"
BANNED_WORD = "prose.banned-word"

RULES = (JUDGMENT_SPELLING, BANNED_WORD)

# The British form: the word "judgement", optionally pluralized, as a whole word
# so "judgemental" and the American "judgment" are both left alone. Matched
# case-insensitively so a sentence-initial "Judgement" is caught too.
JUDGEMENT_PATTERN = re.compile(r"\bjudgements?\b", re.IGNORECASE)

JUDGMENT_MESSAGE = "British `judgement`/`judgements`; the house spelling is `judgment`"

# The banned actor noun: bare or plural, any case. The trailing \b sits at a
# hyphen too, so compounds like "human-readable" are caught, while longer words
# that merely contain the sequence ("humane", "superhuman") are not the actor
# noun and pass.
BANNED_PATTERN = re.compile(r"\bhumans?\b", re.IGNORECASE)

BANNED_MESSAGE = (
    "the person is the `user`; the word `human` appears in no authored file "
    "(prose/conventions.md — Terminology)"
)

# The per-repo exemption declaration: a tracked file at the repo root, one
# repo-relative path per line, a directory entry (trailing slash optional)
# covering its whole subtree. Blank lines and `#` lines are comments. Listed
# paths are skipped by both rules — the repo's reviewable declaration of what
# its prose rules do not govern (prose/conventions.md — Terminology). The file
# itself is never scanned, because an entry may legitimately name a path that
# carries the banned word.
EXEMPT_FILE = ".prose-lint-exempt"


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


def scan_text(rel: str, text: str, line_offset: int = 0) -> list[Finding]:
    """Flag every British judgement / judgements in prose outside code.

    Fenced blocks are dropped by ``md.lines_outside_fences``; inline code spans
    are stripped per line before matching, so a backticked mention of the
    forbidden form does not trip. One finding per occurrence. ``line_offset`` is
    added to every reported line so a caller scanning a document body keeps line
    numbers absolute to the file, matching what an editor shows.
    """
    findings: list[Finding] = []
    for line_num, line in md.lines_outside_fences(text):
        prose = md.INLINE_CODE_PATTERN.sub("", line)
        for _ in JUDGEMENT_PATTERN.finditer(prose):
            findings.append(
                Finding(
                    rel, line_num + line_offset, JUDGMENT_SPELLING, JUDGMENT_MESSAGE
                )
            )
    return findings


def scan_banned(rel: str, text: str) -> list[Finding]:
    """Flag every banned-word occurrence anywhere in ``text``.

    Deliberately maskless: frontmatter, fenced blocks, inline code spans, and
    non-Markdown file content all count. The ban is absolute, so unlike the
    spelling rule there is no backtick escape hatch.
    """
    findings: list[Finding] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        for _ in BANNED_PATTERN.finditer(line):
            findings.append(Finding(rel, line_num, BANNED_WORD, BANNED_MESSAGE))
    return findings


def exempt_paths(root: Path) -> tuple[str, ...]:
    """The paths ``root``'s ``.prose-lint-exempt`` declares, or empty.

    Entries come back with any trailing slash stripped, so a directory written
    either way matches the same subtree in :func:`is_exempt`.
    """
    declaration = root / EXEMPT_FILE
    if not declaration.is_file():
        return ()
    entries = []
    for line in declaration.read_text(encoding="utf-8").splitlines():
        entry = line.strip()
        if not entry or entry.startswith("#"):
            continue
        entries.append(entry.rstrip("/"))
    return tuple(entries)


def is_exempt(rel: str, exempt: tuple[str, ...]) -> bool:
    """Whether a repo-relative path is covered by a declared exemption.

    An entry covers itself and, when it names a directory, everything beneath
    it. The declaration file is always exempt, listed or not.
    """
    if rel == EXEMPT_FILE:
        return True
    return any(rel == entry or rel.startswith(entry + "/") for entry in exempt)


def audit(root: Path) -> list[Finding]:
    """Scan every authored file under ``root`` for both prose rules.

    Scope is wider than ``md.classify``'s concept split — harness files are in,
    and the banned-word rule reads every tracked file, not just Markdown — but
    ``classify``'s ``"excluded"`` category is out: externally-managed vendored
    trees, the ``.git`` tree, and the transient scratch that is not authored
    content (``PLAN.md`` / ``PROGRESS.md`` and the root ``tmp/`` tree). Reusing
    that one boundary keeps vendored-tree exclusion on the shared registry
    (``classify`` consults it) and stops the gate firing on scratch. Verbatim
    Reference docs are excluded per file, the repo's ``.prose-lint-exempt``
    declarations per path; symlinks and binary files (NUL byte) are skipped.
    """
    exempt = exempt_paths(root)
    findings: list[Finding] = []
    for path in md.find_files(root):
        rel = str(path.relative_to(root))
        if md.classify(rel) == "excluded" or is_exempt(rel, exempt):
            continue
        if path.is_symlink():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "\0" in text:
            continue
        if rel.endswith(".md"):
            # Only the body carries the spelling rule — frontmatter is
            # structured YAML, not prose, and a YAML scalar has no backtick
            # escape hatch, so a title carrying the forbidden spelling must not
            # be flagged. The body offset keeps reported line numbers absolute.
            try:
                frontmatter, body = md.parse_frontmatter(text)
            except yaml.YAMLError as err:
                raise CannotRun(f"{rel}: malformed frontmatter: {err}") from err
            if is_verbatim_doc(frontmatter):
                continue
            offset = text.count("\n", 0, len(text) - len(body))
            findings.extend(scan_text(rel, body, offset))
        findings.extend(scan_banned(rel, text))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Scan a repo's files and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="prose-lint",
        description="Lint authored prose: judgment spelling, the banned actor noun.",
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
    except CannotRun as err:
        print(f"prose-lint: cannot run: {err}", file=sys.stderr)
        return 2

    for f in sorted(findings, key=lambda f: (f.file, f.line, f.rule)):
        print(f.render())

    if findings:
        print(f"prose-lint: {len(findings)} finding(s)", file=sys.stderr)
        return 1
    print("prose-lint: clean", file=sys.stderr)
    return 0
