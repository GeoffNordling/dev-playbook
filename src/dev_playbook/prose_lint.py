"""Audit authored content against the workspace prose standard.

prose-lint is the detector behind the Prose Standard. It walks a repo's files once
(via dev_playbook.md.find_files, so gitignore-aware and worktree-scoped) and
applies these deterministic rules:

  - **judgment-spelling** — the house spelling is American ``judgment``; the
    British ``judgement`` / ``judgements`` is flagged. The check runs over
    authored Markdown prose *outside* fenced blocks and inline code spans, so
    an identifier or a doc that must name the forbidden form in backticks does
    not self-trip.
  - **banned-word** — the person operating the workspace is the ``user``; the
    actor noun ``human`` (bare, plural, or hyphenated compound, any case)
    appears in no authored file (prose/conventions.md — The banned word). The
    ban is absolute, so the check runs over every tracked file of every type,
    whole-file — frontmatter, fenced blocks, and inline code spans included;
    there is no backtick escape hatch.
  - **repo-vocabulary** — a repo bans further words of its own, each in a
    named part of its tree, by declaring them in a tracked root-level
    ``.prose-lint-vocabulary`` (prose/conventions.md — The repo vocabulary).
    Each entry is one word, the word that replaces it, and the directories the
    ban covers; an entry with no directories covers the whole repo. A word so
    banned is matched the way ``human`` is, bare or plural, any case,
    whole-file, in every tracked file under a covered directory.

The two word rules read one vocabulary in two layers: the workspace's, fixed
in this module because the Standard fixes it, and the repo's, read from its
declaration. A later layer may only add words — a repo cannot re-declare the
workspace's word, and the run fails loud if it tries — so the vocabulary a
file answers to is the union of every layer whose scope contains it.
  - **agent-facing-voice** — a harness-loaded agent instruction file is
    addressed *to* the executing agent, so it never speaks in the first person
    (prose/conventions.md — Imperative and second person). Unlike its two
    siblings this rule reads only the agent-facing subset of the tree
    (``md.is_agent_instruction``), the members of Doc Conventions' condition
    Harness-loaded agent instructions. Frontmatter is in scope — a runbook's
    ``description`` is prose the agent reads to choose it.

Scope is **all authored content, harness files included** (``CLAUDE.md``,
rules, skills; for the banned-word rule, code and config too). What is out is
``md.classify``'s ``"excluded"`` category: transient scratch (``PLAN.md`` /
``PROGRESS.md``, the root ``tmp/`` tree).
Verbatim upstream mirrors are excluded per file via the registry's
``is_verbatim_doc`` (``type: Mirror`` documents). Symlinks are skipped: a
link's content belongs to its target, which is scanned at its own path when
it lives in the repo and is not ours when it does not. Beyond those structural
exclusions, each repo declares its own: a tracked root-level
``.prose-lint-exempt`` lists the paths — files or whole directories — that
every rule skips (dev-playbook's own lists this module and its test file,
which must name the banned word to ban it). Both declaration files are
structurally exempt, listed or not, since each must name what it bans.

Output:
    stdout — one finding per line, ``file:line: <name>.rule message``.
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

from dev_playbook import md, voice
from dev_playbook.external import is_verbatim_doc
from dev_playbook.findings import print_rules, render


class CannotRun(Exception):
    """A file the detector cannot process — surfaced as exit 2, not a traceback.

    Matches the sibling frontmatter-parsing detectors (decisions-lint,
    standards-lint): a malformed ``.md`` is a run failure to report, never an
    uncaught YAML error that blocks every commit.
    """


# The rule ids this detector emits, each namespaced by the directory whose
# Standard it answers — all three under Prose, whose Doc Conventions holds every rule row.
# Kept module-level constants so every emission site references them, never a
# raw literal, and RULES (what --list-rules prints) cannot drift from what the
# detector emits.
SPELLING = "prose.spelling"
THE_BANNED_WORD = "prose.the-banned-word"
THE_REPO_VOCABULARY = "prose.the-repo-vocabulary"
NO_FIRST_PERSON = "prose.no-first-person"

RULES = (SPELLING, THE_BANNED_WORD, THE_REPO_VOCABULARY, NO_FIRST_PERSON)

# The British form: the word "judgement", optionally pluralized, as a whole word
# so "judgemental" and the American "judgment" are both left alone. Matched
# case-insensitively so a sentence-initial "Judgement" is caught too.
JUDGEMENT_PATTERN = re.compile(r"\bjudgements?\b", re.IGNORECASE)

JUDGMENT_MESSAGE = "British `judgement`/`judgements`; the house spelling is `judgment`"


@dataclass(frozen=True)
class Word:
    """One banned word: the word, the word that replaces it, and where the ban holds.

    ``where`` is a tuple of repo-relative directories; empty means the whole
    repo. Which rule a finding on the word carries is the layer the word came
    from: a member of :data:`WORKSPACE_VOCABULARY` answers to
    ``prose.the-banned-word``, a repo's own word to ``prose.the-repo-vocabulary``.
    """

    word: str
    say: str
    where: tuple[str, ...]

    @property
    def pattern(self) -> re.Pattern[str]:
        """The word bare or plural, any case, as a whole word.

        The trailing word boundary sits at a hyphen too, so a compound like
        "human-readable" is caught, while a longer word that merely contains
        the sequence ("humane", "superhuman") is not the word and passes.
        """
        return re.compile(rf"\b{re.escape(self.word)}s?\b", re.IGNORECASE)

    def covers(self, rel: str) -> bool:
        """Whether the ban holds at a repo-relative path."""
        return not self.where or any(rel.startswith(d + "/") for d in self.where)

    def message(self, rel: str) -> str:
        """The finding's message: the word, its replacement, and where the ban holds."""
        if self in WORKSPACE_VOCABULARY:
            return (
                f"the person is the `{self.say}`; the word `{self.word}` appears in "
                "no tracked file (prose/conventions.md — The banned word)"
            )
        scope = (
            "in every tracked file"
            if not self.where
            else "under `"
            + next(d for d in self.where if rel.startswith(d + "/"))
            + "/`"
        )
        return (
            f"the word `{self.word}` is `{self.say}` {scope} "
            f"({VOCABULARY_FILE}; prose/conventions.md — The repo vocabulary)"
        )


# The workspace's layer of the vocabulary: the words the Standard bans in every
# repo, fixed here because a repo's declaration may add to it and never take
# from it. One word today, the actor noun.
WORKSPACE_VOCABULARY: tuple[Word, ...] = (Word("human", "user", ()),)

# The repo's layer: a tracked YAML file at the repo root mapping each banned
# word to ``say``, the word that replaces it, and ``where``, the repo-relative
# directories the ban covers, omitted to cover the whole repo. Read by
# :func:`vocabulary`; a malformed declaration is a run failure, never a silent
# no-op. The file itself is never scanned, because it names what it bans.
VOCABULARY_FILE = ".prose-lint-vocabulary"

# A double-quoted span on one line is somebody else's voice — the phrasing a
# user types to trigger a skill, the reaction a prototype is built to provoke —
# so the document is quoting, not speaking. Quotes do not span lines here: a
# lone quotation mark closes at the newline rather than swallowing the rest of
# the file.
QUOTED_SPEECH_PATTERN = re.compile(r'"[^"\n]*"')

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
                Finding(rel, line_num + line_offset, SPELLING, JUDGMENT_MESSAGE)
            )
    return findings


def scan_banned(
    rel: str, text: str, words: tuple[Word, ...] = WORKSPACE_VOCABULARY
) -> list[Finding]:
    """Flag every occurrence in ``text`` of a word whose ban covers ``rel``.

    Deliberately maskless: frontmatter, fenced blocks, inline code spans, and
    non-Markdown file content all count. The ban is absolute, so unlike the
    spelling rule there is no backtick escape hatch. ``words`` is the whole
    vocabulary, every layer; the words whose scope does not reach ``rel`` are
    skipped here, so a caller passes the vocabulary once, not a slice per file.
    """
    findings: list[Finding] = []
    held = [w for w in words if w.covers(rel)]
    if not held:
        return findings
    for line_num, line in enumerate(text.splitlines(), start=1):
        for word in held:
            for _ in word.pattern.finditer(line):
                message = word.message(rel)
                if word in WORKSPACE_VOCABULARY:
                    findings.append(Finding(rel, line_num, THE_BANNED_WORD, message))
                else:
                    findings.append(
                        Finding(rel, line_num, THE_REPO_VOCABULARY, message)
                    )
    return findings


def scan_voice(rel: str, text: str) -> list[Finding]:
    """Flag every first-person token in a harness-loaded agent instruction file.

    Fenced blocks are dropped by ``md.lines_outside_fences``; inline code spans
    and double-quoted utterances are stripped per line before matching, so a
    backticked example and a quoted phrase the document is reporting rather than
    speaking both pass. At most one finding per line per fault, since a line
    saying "I" three times has one thing wrong with it.
    """
    findings: list[Finding] = []
    for line_num, line in md.lines_outside_fences(text):
        prose = QUOTED_SPEECH_PATTERN.sub("", md.INLINE_CODE_PATTERN.sub("", line))
        for pattern, fault in voice.VOICE_PATTERNS:
            if pattern.search(prose):
                findings.append(Finding(rel, line_num, NO_FIRST_PERSON, fault))
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
    it. The two declaration files are always exempt, listed or not.
    """
    if rel in (EXEMPT_FILE, VOCABULARY_FILE):
        return True
    return any(rel == entry or rel.startswith(entry + "/") for entry in exempt)


def vocabulary(root: Path) -> tuple[Word, ...]:
    """The vocabulary a repo at ``root`` answers to: the workspace's words, then its own.

    The repo's layer is ``root``'s ``.prose-lint-vocabulary``, a YAML mapping
    of word to ``{say, where}``. Every fault in the declaration is a
    :class:`CannotRun`: a file that is not a mapping, an entry that is not a
    mapping or lacks ``say``, a ``where`` that is not a list of strings or
    names a path that is not a directory under ``root``, and a word the
    workspace already bans, which a repo may neither re-declare nor loosen.
    """
    declaration = root / VOCABULARY_FILE
    if not declaration.is_file():
        return WORKSPACE_VOCABULARY
    try:
        loaded = yaml.safe_load(declaration.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise CannotRun(f"{VOCABULARY_FILE}: malformed YAML: {err}") from err
    if loaded is None:
        return WORKSPACE_VOCABULARY
    if not isinstance(loaded, dict):
        raise CannotRun(
            f"{VOCABULARY_FILE}: the file is not a mapping of word to entry"
        )
    fixed = {w.word for w in WORKSPACE_VOCABULARY}
    words: list[Word] = []
    for word, entry in loaded.items():
        if not isinstance(word, str) or not word:
            raise CannotRun(f"{VOCABULARY_FILE}: {word!r} is not a word")
        if word.lower() in fixed:
            raise CannotRun(
                f"{VOCABULARY_FILE}: `{word}` is the workspace's word and is not re-declared"
            )
        if not isinstance(entry, dict) or not isinstance(entry.get("say"), str):
            raise CannotRun(f"{VOCABULARY_FILE}: `{word}` needs a mapping with `say`")
        unknown = set(entry) - {"say", "where"}
        if unknown:
            raise CannotRun(
                f"{VOCABULARY_FILE}: `{word}` has unknown key(s) {sorted(unknown)}"
            )
        where = entry.get("where", [])
        if not isinstance(where, list) or not all(
            isinstance(d, str) and d for d in where
        ):
            raise CannotRun(
                f"{VOCABULARY_FILE}: `{word}`'s `where` is not a list of paths"
            )
        dirs = tuple(d.rstrip("/") for d in where)
        for d in dirs:
            if not (root / d).is_dir():
                raise CannotRun(
                    f"{VOCABULARY_FILE}: `{word}`'s `{d}` is not a directory"
                )
        words.append(Word(word, entry["say"], dirs))
    return WORKSPACE_VOCABULARY + tuple(words)


def audit(root: Path) -> list[Finding]:
    """Scan every authored file under ``root`` for every rule.

    Scope is wider than ``md.classify``'s concept split — harness files are in,
    and the banned-word rule reads every tracked file, not just Markdown — but
    ``classify``'s ``"excluded"`` category is out: the ``.git`` tree and the
    transient scratch that is not authored content (``PLAN.md`` /
    ``PROGRESS.md`` and the root ``tmp/`` tree). Reusing that one boundary
    stops the gate firing on scratch. Verbatim Mirror docs are excluded per
    file, the repo's ``.prose-lint-exempt`` declarations per path; symlinks and
    binary files (NUL byte) are skipped — a link's content belongs to its
    target, scanned at its own path when it lives in the repo.
    """
    exempt = exempt_paths(root)
    words = vocabulary(root)
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
            if md.is_agent_instruction(rel):
                # Whole-file, not the body: a runbook's `description` is prose
                # the agent reads to choose it, so frontmatter answers to the
                # same voice.
                findings.extend(scan_voice(rel, text))
        findings.extend(scan_banned(rel, text, words))
    return findings


def main(argv: list[str] | None = None) -> int:
    """Scan a repo's files and print one finding per line; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="prose-lint",
        description=(
            "Lint authored prose: judgment spelling, the banned actor noun, "
            "the repo's own banned words, the agent-facing voice."
        ),
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
