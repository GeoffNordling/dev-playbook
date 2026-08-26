"""Shared markdown primitives for the workspace pre-commit hooks.

This module is the single home for the markdown mechanics that more than one
hook needs: fenced-code skipping, GitHub heading slugs, YAML frontmatter,
link extraction, the OKF concept-doc/harness-owned path classification, and
the rootless-source test behind the cross-reference grammar. The slug rule,
the bundle boundary, and the rootless roster are defined once here rather than
drifting between scripts.

``yaml`` is imported lazily inside :func:`parse_frontmatter` so importers that
only need the pure-text helpers (``ref-lint`` runs under plain ``python3``) do
not require pyyaml on the interpreter; only frontmatter-parsing callers do, and
those run under ``uv run --script`` with pyyaml declared.
"""

import functools
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path, PurePosixPath

from dev_playbook import gitrepo
from dev_playbook.external import is_externally_managed

# A CommonMark code fence: a run of three or more backticks or tildes, group 1,
# followed by group 2's info string (empty on a closing fence). Capturing the
# whole run rather than a fixed three is what lets lines_outside_fences nest by
# length; see its docstring for the closing rule. The indent is capped at three
# spaces, as CommonMark caps it: past that the run is literal text inside an
# indented code block, so an indented transcript carrying a stray backtick line
# does not open a block that swallows the rest of the document.
FENCE_PATTERN = re.compile(r"^ {0,3}(`{3,}|~{3,})\s*(.*?)\s*$")
# A CommonMark inline code span: an opening run of N backticks closes on the
# next run of exactly N (the trailing (?!`) rejects a longer run). The
# backreference ties the closing length to the opening one, so a double-backtick
# span whose body itself contains a single backtick — e.g. ``a`b`` — is stripped
# as one unit rather than read as two empty single-backtick spans that would leak
# the body into the surrounding prose. The body is non-greedy and newline-free,
# matching how callers mask code span by span, line by line.
INLINE_CODE_PATTERN = re.compile(r"(`+)([^\n]+?)\1(?!`)")
HEADING_PATTERN = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
# A markdown inline link: [text](target). target stops at whitespace or ')';
# a trailing "#anchor" stays part of the captured target.
MD_LINK_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")
# Bare ~/workspace/<repo>/... citations, matched outside code spans/fences.
WORKSPACE_REF_PATTERN = re.compile(r"~/workspace/[^ )`\n]+")

# Inline-markdown stripping for heading slugs; see github_slug.
SLUG_BACKTICK = re.compile(r"`([^`]*)`")
SLUG_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
# Asterisk emphasis is stripped anywhere (it may be intraword); underscore
# emphasis only at word boundaries, so intraword `foo_bar_baz` stays literal —
# matching GitHub's rendered-text anchors.
SLUG_STAR = re.compile(r"(\*{1,2})(.+?)\1")
SLUG_UNDERSCORE = re.compile(r"(?<!\w)(_{1,2})(?=\S)(.+?)(?<=\S)\1(?!\w)")
SLUG_DROP = re.compile(r"[^\w\s\-]", re.UNICODE)
SLUG_WHITESPACE = re.compile(r"\s")

# Path segments marking sources with no fixed repo root: skills, rules, and
# agent definitions ship into ~/.claude, so a `/path` Link in one would resolve
# against whatever repo the reading agent happens to stand in. They use the
# Citation form even for same-repo targets, per the cross-reference standard.
# classify() spells these names out again; add a fourth segment in both places.
ROOTLESS_SEGMENTS = {"skills", "rules", "agents"}


class UnclosedFence(ValueError):
    """A fenced code block that nothing ever closes.

    Every consumer of this module scans a document in order to report on it, so
    a block left open swallows the rest of the file while the scan still comes
    back clean — silence exactly where a finding belongs. Raised rather than
    swallowed, on the same footing as :func:`parse_frontmatter`'s malformed
    YAML: a parse failure is surfaced.

    ``source`` names the file when one is known (:func:`content_lines` supplies
    it); scanning a bare string, only the opening line number is available.
    """

    def __init__(self, marker: str, line: int, source: str | None = None) -> None:
        """Name the fence run, the line it opened on, and the file if known."""
        self.marker = marker
        self.line = line
        self.source = source
        where = f"{source}:{line}" if source else f"line {line}"
        super().__init__(f"unclosed {marker} code fence opened at {where}")


def github_slug(heading_text: str) -> str:
    """Compute the GitHub-style anchor slug for a heading.

    Strip inline markdown (backticks, link syntax, emphasis), lowercase,
    drop non-word/non-whitespace/non-hyphen chars, then whitespace -> "-".
    """
    text = SLUG_BACKTICK.sub(r"\1", heading_text)
    text = SLUG_LINK.sub(r"\1", text)
    text = SLUG_STAR.sub(r"\2", text)
    text = SLUG_UNDERSCORE.sub(r"\2", text)
    text = text.lower()
    text = SLUG_DROP.sub("", text)
    text = SLUG_WHITESPACE.sub("-", text)
    return text


def lines_outside_fences(text: str) -> Iterator[tuple[int, str]]:
    """Yield (line_number, line) for every line of ``text`` outside a fence.

    The single place that knows how to skip ``` / ~~~ fenced code blocks.
    Line numbers are 1-based and count fence-delimiter lines too, so a
    reported line matches what an editor shows.

    Fences nest by length, as CommonMark has them: a block closes only on a run
    of the same character, at least as long as the one that opened it, and
    carrying no info string. That is what makes a four-backtick fence able to
    wrap three-backtick content — the form issue-authoring.md mandates for an
    artifact block whose content carries its own fences — instead of ending on
    the first inner fence.

    A block still open when the text runs out raises :class:`UnclosedFence`.
    Yielding the truncated view instead would leave every consumer scanning
    nothing for the rest of the document and still reporting clean, and one
    mistyped closer — a run that repeats the opener's info string — is all it
    takes.
    """
    marker: str | None = None
    opened_at = 0
    for line_num, line in enumerate(text.splitlines(keepends=True), start=1):
        fence = FENCE_PATTERN.match(line)
        if marker is None:
            if fence:
                marker = fence.group(1)
                opened_at = line_num
            else:
                yield line_num, line
        elif (
            fence
            and not fence.group(2)
            and fence.group(1)[0] == marker[0]
            and len(fence.group(1)) >= len(marker)
        ):
            marker = None
    if marker is not None:
        raise UnclosedFence(marker, opened_at)


def content_lines(filepath: Path) -> Iterator[tuple[int, str]]:
    """Yield (line_number, line) for every line of a file outside a fence.

    An :class:`UnclosedFence` from the scan is re-raised naming the file, so a
    checkout-wide run points at the document to fix rather than at a line
    number with no home.
    """
    text = filepath.read_text(encoding="utf-8", errors="replace")
    try:
        yield from lines_outside_fences(text)
    except UnclosedFence as unclosed:
        raise UnclosedFence(unclosed.marker, unclosed.line, str(filepath)) from None


@functools.cache
def heading_slugs(filepath: Path) -> frozenset[str]:
    """Return the set of GitHub slugs for every ATX heading in ``filepath``.

    Headings inside fenced code blocks are skipped. Cached by path so a
    target referenced from many sources is only parsed once per run.
    """
    return frozenset(
        github_slug(m.group(1))
        for _, line in content_lines(filepath)
        if (m := HEADING_PATTERN.match(line))
    )


def markdown_links(line: str) -> list[tuple[str, str]]:
    """Return (text, target) for every inline ``[text](target)`` link on a line.

    Inline code spans are stripped first, so a bracketed example inside
    backticks is treated as prose, not a link.
    """
    stripped = INLINE_CODE_PATTERN.sub("", line)
    return [(m.group(1), m.group(2)) for m in MD_LINK_PATTERN.finditer(stripped)]


def parse_frontmatter(text: str) -> tuple[dict | None, str]:
    """Split leading ``---`` YAML frontmatter from the body.

    Returns ``(mapping, body)`` when the text opens with a ``---`` block whose
    YAML is a mapping; ``(None, text)`` when there is no frontmatter. Raises
    the underlying ``yaml`` error on malformed frontmatter — parsing failures
    are surfaced, not swallowed.
    """
    if not text.startswith("---\n"):
        return None, text
    try:
        end = text.index("\n---\n", 4)
    except ValueError:
        return None, text
    import yaml  # lazy: only frontmatter callers need pyyaml on the interpreter

    front = yaml.safe_load(text[4:end])
    body = text[end + 5 :]
    if not isinstance(front, dict):
        return None, body
    return front, body


def has_fixed_repo_root(relpath: str) -> bool:
    """True when a source file is always read from one repo, so ``/`` resolves.

    The one home for the rootless test: ``ref-lint`` decides the ``wrong-form``
    finding with it and the file graph stamps the matching edge status, so a new
    rootless segment reaches both at once rather than drifting between them.

    A segment matches at any depth, which is what lets
    ``dotfiles/dot-claude/skills/...`` and a consumer's ``.claude/skills/...``
    answer alike.
    """
    return not (ROOTLESS_SEGMENTS & set(PurePosixPath(relpath).parts))


def classify(relpath: str) -> str:
    """Classify a repo-relative path within the OKF bundle taxonomy.

    Returns one of:

    - ``"excluded"`` — out of the bundle entirely: the transient ``PLAN.md``
      and ``PROGRESS.md`` (ralph-loop plan/progress pair), the root ``tmp/``
      scratch tree, the ``.git`` directory, and anything under an
      externally-managed vendored tree (the shared dev_playbook.external
      registry, currently ``dotfiles/.agents``).
    - ``"index"`` — a directory listing (``index.md``): typeless, validated as
      an index rather than as a concept document.
    - ``"concept"`` — a prose concept document that carries OKF frontmatter and
      is subject to the type-lint.
    - ``"harness"`` — an in-bundle file a tool consumes as configuration or
      runs as code, not prose: ``CLAUDE.md``, ``SKILL.md`` and skill
      ``references/``/``scripts/``, ``agents/``, ``rules/``, every top-level
      ``tests/`` tree (fixture data a test consumes, held to no doc
      standard), and every non-``.md`` file.

    The concept/harness split mirrors the file roles in the docs
    standard and the Claude Code file registry
    (standards/harness/files.md); keep them in step.
    """
    parts = PurePosixPath(relpath).parts
    name = parts[-1]
    dirparts = parts[:-1]

    if name in {"PLAN.md", "PROGRESS.md"}:
        return "excluded"
    if parts[0] == "tmp":
        return "excluded"
    if ".git" in parts or is_externally_managed(relpath):
        return "excluded"
    if parts[0] == "tests":
        return "harness"

    if not name.endswith(".md"):
        return "harness"
    if name == "index.md":
        return "index"
    if name in {"CLAUDE.md", "SKILL.md"}:
        return "harness"
    # ROOTLESS_SEGMENTS' names again, not read from the roster: `skills` differs
    # here, where only the references/ and scripts/ subtrees are harness.
    if {"rules", "agents"} & set(dirparts):
        return "harness"
    if "skills" in dirparts and ({"references", "scripts"} & set(dirparts)):
        return "harness"
    return "concept"


def find_files(root: Path) -> list[Path]:
    """Every file in ``root``'s git checkout, honoring ``.gitignore``.

    Uses ``git ls-files`` rather than a filesystem walk so discovery is both
    gitignore-aware and worktree-scoped: from inside a worktree, git's
    per-worktree index lists only that worktree's files, so the main checkout
    and sibling worktrees are invisible by construction. ``--cached`` lists
    tracked files, ``--others`` untracked ones, ``--exclude-standard`` drops
    anything ``.gitignore`` matches. A ``--cached`` entry whose file was
    deleted from the working tree is skipped by the ``is_file`` guard.
    """
    result = subprocess.run(
        [
            "git",
            "-C",
            str(root),
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=gitrepo.no_git_env(),
    )
    results = []
    for rel in result.stdout.split("\0"):
        if not rel:
            continue
        path = root / rel
        if path.is_file():
            results.append(path)
    return sorted(results)


def find_md_files(root: Path) -> list[Path]:
    """All ``.md`` files in ``root``'s git checkout, honoring ``.gitignore``."""
    return [path for path in find_files(root) if path.name.endswith(".md")]
