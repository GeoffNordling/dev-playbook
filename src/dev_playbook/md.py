"""Shared markdown primitives for the workspace pre-commit hooks.

This module is the single home for the markdown mechanics that more than one
hook needs: fenced-code skipping, GitHub heading slugs, YAML frontmatter,
link extraction, and the OKF concept-doc/harness-owned path classification.
``ref-check`` and ``okf-audit`` both consume it, so the slug rule and the bundle
boundary are defined once here rather than drifting between scripts.

``yaml`` is imported lazily inside :func:`parse_frontmatter` so importers that
only need the pure-text helpers (``ref-check`` runs under plain ``python3``) do
not require pyyaml on the interpreter; only frontmatter-parsing callers do, and
those run under ``uv run --script`` with pyyaml declared.
"""

import functools
import re
import subprocess
from collections.abc import Iterator
from pathlib import Path, PurePosixPath

FENCE_PATTERN = re.compile(r"^\s*(```|~~~)")
INLINE_CODE_PATTERN = re.compile(r"`[^`\n]*`")
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
    """
    in_fence = False
    for line_num, line in enumerate(text.splitlines(keepends=True), start=1):
        if FENCE_PATTERN.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield line_num, line


def content_lines(filepath: Path) -> Iterator[tuple[int, str]]:
    """Yield (line_number, line) for every line of a file outside a fence."""
    text = filepath.read_text(encoding="utf-8", errors="replace")
    yield from lines_outside_fences(text)


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


def classify(relpath: str) -> str:
    """Classify a repo-relative path within the OKF bundle taxonomy.

    Returns one of:

    - ``"excluded"`` — out of the bundle entirely: the transient ``PLAN.md``
      and ``PROGRESS.md`` (ralph-loop plan/progress pair), the root ``tmp/``
      scratch tree, and anything under externally-managed
      ``.agents``/``.dhub`` trees.
    - ``"index"`` — a directory listing (``index.md``): typeless, validated as
      an index rather than as a concept document.
    - ``"concept"`` — a prose concept document that carries OKF frontmatter and
      is subject to the type-lint.
    - ``"harness"`` — an in-bundle file a tool consumes as configuration or
      runs as code, not prose: ``CLAUDE.md``, ``SKILL.md`` and skill
      ``references/``/``scripts/``, ``rules/``, and every non-``.md`` file.

    The concept/harness split mirrors the bundle boundary in the docs
    standard and the Claude Code file registry
    (standards/claude-code/files.md); keep them in step.
    """
    parts = PurePosixPath(relpath).parts
    name = parts[-1]
    dirparts = parts[:-1]

    if name in {"PLAN.md", "PROGRESS.md"}:
        return "excluded"
    if parts[0] == "tmp":
        return "excluded"
    if any(seg in {".agents", ".dhub", ".git"} for seg in parts):
        return "excluded"

    if not name.endswith(".md"):
        return "harness"
    if name == "index.md":
        return "index"
    if name in {"CLAUDE.md", "SKILL.md"}:
        return "harness"
    if "rules" in dirparts:
        return "harness"
    if "skills" in dirparts and ({"references", "scripts"} & set(dirparts)):
        return "harness"
    return "concept"


def find_md_files(root: Path) -> list[Path]:
    """All ``.md`` files in ``root``'s git checkout, honoring ``.gitignore``.

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
    )
    results = []
    for rel in result.stdout.split("\0"):
        if not rel.endswith(".md"):
            continue
        path = root / rel
        if path.is_file():
            results.append(path)
    return sorted(results)
