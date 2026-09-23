"""The repo model: one checkout read once into memory, in parsed form.

Every check reads a :class:`Repo` and nothing else: no disk, no git. The
model is built once per run from one ``git ls-files`` (:meth:`Repo.from_git`)
or, in a test, from a mapping of paths to bytes (:meth:`Repo.from_files`).
Both go through the same constructor, so a test's repo is the real thing.

A markdown file is parsed into frontmatter, headings with slugs and line
numbers, rule trailers, links, and the lines outside code fences. A Python
file is parsed into an ``ast`` tree. Everything else is bytes. A file the
model cannot parse raises :class:`ModelError` naming it: a fence nothing
closes or frontmatter that is not YAML is surfaced, never skipped.
"""

import ast
import bisect
import re
import subprocess
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from dev_playbook import gitrepo, md

# A rule trailer: the whole line is a code span holding `<family>.<slug>`,
# then ` · ` and the kind.
TRAILER_PATTERN = re.compile(
    r"^`([a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*)` · (deterministic|stochastic)$"
)
# An inline link whose text may wrap across one line break.
LINK_PATTERN = re.compile(r"\[([^\]\n]*(?:\n[^\]\n]*)?)\]\(([^)\s]+)\)")
PYTHON_SHEBANG_PREFIXES = (
    "#!/usr/bin/env python",
    "#!/usr/bin/python",
    "#!/usr/bin/env -S uv run --script",
)
REGULAR_FILE = "100644"
EXECUTABLE_FILE = "100755"


class ModelError(Exception):
    """A tracked file the model cannot parse; ``path`` names it."""

    def __init__(self, path: str, reason: str) -> None:
        """Name the file and say what failed."""
        self.path = path
        self.reason = reason
        super().__init__(f"{path}: {reason}")


@dataclass(frozen=True)
class Heading:
    """One ATX heading outside a fence: its level, text, slug, and line."""

    level: int
    text: str
    slug: str
    line: int


@dataclass(frozen=True)
class Trailer:
    """One rule trailer, with the nearest heading above it."""

    id: str
    kind: str
    line: int
    heading: Heading | None

    @property
    def family(self) -> str:
        """The part of the id before the dot."""
        return self.id.partition(".")[0]

    @property
    def slug(self) -> str:
        """The part of the id after the dot."""
        return self.id.partition(".")[2]


@dataclass(frozen=True)
class Link:
    """One inline ``[text](target)`` link, on the line its ``[`` opens."""

    text: str
    target: str
    line: int


@dataclass(frozen=True)
class MarkdownFile:
    """One parsed markdown file.

    ``content`` is every body line outside a code fence, as ``(line, text)``
    with 1-based line numbers and no trailing newline; frontmatter lines are
    not in it.
    """

    path: str
    text: str
    frontmatter: dict[str, Any] | None
    headings: tuple[Heading, ...]
    trailers: tuple[Trailer, ...]
    links: tuple[Link, ...]
    content: tuple[tuple[int, str], ...]

    def section(self, slug: str) -> tuple[tuple[int, str], ...]:
        """The content lines under the heading with ``slug``.

        Runs to the next heading of the same or a higher level. Raises
        ``KeyError`` when no heading has the slug.
        """
        start = next((h for h in self.headings if h.slug == slug), None)
        if start is None:
            raise KeyError(slug)
        end = next(
            (
                h.line
                for h in self.headings
                if h.line > start.line and h.level <= start.level
            ),
            None,
        )
        return tuple(
            (n, t)
            for n, t in self.content
            if n > start.line and (end is None or n < end)
        )


@dataclass(frozen=True)
class PythonFile:
    """One Python file; ``tree`` is None when ``error`` holds the syntax error."""

    path: str
    text: str
    tree: ast.Module | None
    error: str | None


@dataclass(frozen=True)
class Repo:
    """One checkout in memory: every tracked file, the parsed ones by kind."""

    root: Path
    files: tuple[str, ...]
    contents: Mapping[str, bytes]
    executable: frozenset[str]
    markdown: Mapping[str, MarkdownFile]
    python: Mapping[str, PythonFile]

    @classmethod
    def from_files(
        cls,
        root: Path,
        contents: Mapping[str, bytes],
        executable: Iterable[str] = (),
    ) -> Repo:
        """Build the model from ``{repo-relative path: bytes}``."""
        markdown: dict[str, MarkdownFile] = {}
        python: dict[str, PythonFile] = {}
        for path in sorted(contents):
            data = contents[path]
            if path.endswith(".md"):
                markdown[path] = parse_markdown(path, decode(path, data))
            elif is_python(path, data):
                python[path] = parse_python(path, decode(path, data))
        return cls(
            root=root,
            files=tuple(sorted(contents)),
            contents=dict(contents),
            executable=frozenset(executable),
            markdown=markdown,
            python=python,
        )

    @classmethod
    def from_git(cls, root: Path) -> Repo:
        """Build the model from the tracked files of the checkout at ``root``.

        One ``git ls-files`` lists the index with each entry's mode, so the
        listing is worktree-scoped and gitignore is moot. Symlinks and
        submodules are not files and are left out; an entry deleted from the
        working tree is skipped.
        """
        result = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--stage", "-z"],
            capture_output=True,
            text=True,
            check=True,
            env=gitrepo.no_git_env(),
        )
        contents: dict[str, bytes] = {}
        executable: set[str] = set()
        for entry in result.stdout.split("\0"):
            if not entry:
                continue
            meta, path = entry.split("\t", 1)
            mode = meta.split(" ", 1)[0]
            if mode not in (REGULAR_FILE, EXECUTABLE_FILE):
                continue
            full = root / path
            if not full.is_file():
                continue
            contents[path] = full.read_bytes()
            if mode == EXECUTABLE_FILE:
                executable.add(path)
        return cls.from_files(root, contents, executable)

    def text(self, path: str) -> str:
        """The UTF-8 text of one tracked file."""
        return decode(path, self.contents[path])


def decode(path: str, data: bytes) -> str:
    """``data`` as UTF-8, or :class:`ModelError` naming the file."""
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as err:
        raise ModelError(path, f"not UTF-8: {err}") from None


def is_python(path: str, data: bytes) -> bool:
    """True for a ``.py`` file or an extensionless file with a Python shebang."""
    name = PurePosixPath(path)
    if name.suffix == ".py":
        return True
    if name.suffix:
        return False
    first = data.split(b"\n", 1)[0].decode("utf-8", errors="replace")
    return first.startswith(PYTHON_SHEBANG_PREFIXES)


def parse_python(path: str, text: str) -> PythonFile:
    """Parse one Python file; a syntax error is recorded, not raised.

    Syntax is ruff's to report. A file that does not parse still exists in
    the model, with ``tree`` None, so a check over Python files sees it.
    """
    try:
        return PythonFile(path, text, ast.parse(text, filename=path), None)
    except SyntaxError as err:
        return PythonFile(path, text, None, str(err))


def parse_markdown(path: str, text: str) -> MarkdownFile:
    """Parse one markdown file into its :class:`MarkdownFile`."""
    try:
        frontmatter, body = md.parse_frontmatter(text)
    except yaml.YAMLError as err:
        raise ModelError(path, f"frontmatter is not YAML: {err}") from None
    if frontmatter is None and body is not text:
        raise ModelError(path, "frontmatter is not a mapping")
    first_body_line = text[: len(text) - len(body)].count("\n") + 1
    try:
        content = tuple(
            (n, line.rstrip("\n"))
            for n, line in md.lines_outside_fences(text)
            if n >= first_body_line
        )
    except md.UnclosedFence as err:
        raise ModelError(path, str(err)) from None
    headings = tuple(
        Heading(len(m.group(1)), m.group(2), md.github_slug(m.group(2)), n)
        for n, line in content
        if (m := _HEADING.match(line))
    )
    trailers = tuple(
        Trailer(m.group(1), m.group(2), n, _heading_above(headings, n))
        for n, line in content
        if (m := TRAILER_PATTERN.match(line))
    )
    return MarkdownFile(
        path=path,
        text=text,
        frontmatter=frontmatter,
        headings=headings,
        trailers=trailers,
        links=_links(content),
        content=content,
    )


_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def _heading_above(headings: tuple[Heading, ...], line: int) -> Heading | None:
    above = [h for h in headings if h.line < line]
    return above[-1] if above else None


def _links(content: tuple[tuple[int, str], ...]) -> tuple[Link, ...]:
    """Every inline link in the content lines, wrapped text included.

    Inline code spans are stripped line by line first, so a bracketed
    example inside backticks is prose, not a link. The lines are then joined
    so a link whose text wraps across one line break is still found; it is
    reported on the line its ``[`` opens.
    """
    stripped = [md.INLINE_CODE_PATTERN.sub("", text) for _, text in content]
    starts = [0]
    for text in stripped[:-1]:
        starts.append(starts[-1] + len(text) + 1)
    joined = "\n".join(stripped)
    return tuple(
        Link(
            m.group(1),
            m.group(2),
            content[bisect.bisect_right(starts, m.start()) - 1][0],
        )
        for m in LINK_PATTERN.finditer(joined)
    )
