"""The repo model: one checkout read once into memory, in parsed form.

Every check reads a :class:`Repo` and nothing else: no disk, no git. The
model is built once per run from one ``git ls-files`` (:meth:`Repo.from_git`)
or, in a test, from a mapping of paths to bytes (:meth:`Repo.from_files`).
Both go through the same constructor, so a test's repo is the real thing.
The model also carries what no tracked file of a consumer holds: the
repository's name and the canonical files a repo copies, read from the copy
shipped inside this package, so a check needs neither git nor dev-playbook's
tree.

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
from dataclasses import dataclass, field
from functools import cache
from importlib import resources
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from dev_playbook import gitrepo, md, sources

# A rule trailer: the whole line is a code span holding `<family>.<slug>`,
# then ` · ` and the kind.
TRAILER_PATTERN = re.compile(
    r"^`([a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*)` · (deterministic|stochastic)$"
)
# An inline link whose text may wrap across one line break.
LINK_PATTERN = re.compile(r"\[([^\]\n]*(?:\n[^\]\n]*)?)\]\(([^)\s]+)\)")
# A list item's marker and the spaces after it, which set its content column.
LIST_ITEM = re.compile(r"^( *)([-*+]|\d+[.)])( +|$)")
PYTHON_SHEBANG_PREFIXES = (
    "#!/usr/bin/env python",
    "#!/usr/bin/python",
    "#!/usr/bin/env -S uv run --script",
)
REGULAR_FILE = "100644"
EXECUTABLE_FILE = "100755"
# The package directory that ships a copy of sources.CANONICAL_DIR.
SHIPPED_CANONICAL = "canonical"


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
class BarePath:
    """One ``~/workspace/`` path in prose, outside a link's target and outside code.

    ``in_link`` is True where the path sits in a link's text.
    """

    target: str
    line: int
    in_link: bool


@dataclass(frozen=True)
class MarkdownFile:
    """One parsed markdown file.

    ``content`` is every body line outside a code fence, as ``(line, text)``
    with 1-based line numbers and no trailing newline; frontmatter lines are
    not in it. ``indented_code`` holds the line numbers of the indented code
    blocks among them, and ``bare_paths`` every ``~/workspace/`` path outside
    both kinds of code.
    """

    path: str
    text: str
    frontmatter: dict[str, Any] | None
    headings: tuple[Heading, ...]
    trailers: tuple[Trailer, ...]
    links: tuple[Link, ...]
    content: tuple[tuple[int, str], ...]
    indented_code: frozenset[int] = frozenset()
    bare_paths: tuple[BarePath, ...] = ()

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
    """One checkout in memory: every tracked file, the parsed ones by kind.

    ``name`` is the repository's name. ``canonical`` maps each name in
    ``sources.CANONICAL_FILES`` to the bytes of the copy shipped in this
    package.
    """

    root: Path
    name: str
    files: tuple[str, ...]
    contents: Mapping[str, bytes]
    executable: frozenset[str]
    markdown: Mapping[str, MarkdownFile]
    python: Mapping[str, PythonFile]
    canonical: Mapping[str, bytes]
    # The heading slugs of files read from disk, held for this model's run only.
    disk_slugs: dict[str, frozenset[str]] = field(
        default_factory=dict, compare=False, repr=False
    )

    @classmethod
    def from_files(
        cls,
        root: Path,
        contents: Mapping[str, bytes],
        executable: Iterable[str] = (),
        name: str | None = None,
        canonical: Mapping[str, bytes] | None = None,
    ) -> Repo:
        """Build the model from ``{repo-relative path: bytes}``.

        ``name`` defaults to the root's directory name and ``canonical`` to
        the shipped copy; a test passes either to pin its own.
        """
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
            name=root.name if name is None else name,
            files=tuple(sorted(contents)),
            contents=dict(contents),
            executable=frozenset(executable),
            markdown=markdown,
            python=python,
            canonical=shipped_canonical() if canonical is None else dict(canonical),
        )

    @classmethod
    def from_git(cls, root: Path) -> Repo:
        """Build the model from the tracked files of the checkout at ``root``.

        One ``git ls-files`` lists the index with each entry's mode, so the
        listing is worktree-scoped and gitignore is moot. Symlinks and
        submodules are not files and are left out; an entry deleted from the
        working tree is skipped. The name is the directory holding the shared
        ``.git``, the same from the main checkout and every worktree.
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
        return cls.from_files(
            root, contents, executable, name=gitrepo.canonical_repo_name(root)
        )

    def text(self, path: str) -> str:
        """The UTF-8 text of one tracked file."""
        return decode(path, self.contents[path])

    @property
    def is_dev_playbook(self) -> bool:
        """True for the repo that tracks the canonical directory, dev-playbook."""
        prefix = sources.CANONICAL_DIR + "/"
        return any(path.startswith(prefix) for path in self.files)

    def slugs_on_disk(self, path: str) -> frozenset[str]:
        """The heading slugs of a ``.md`` file outside the model, read once per model.

        The one read from disk, for a check tagged ``WORKSPACE`` that opens
        another repo's file; the answer lives as long as this model, so a
        long-lived process that builds a new model never reads a stale one.
        """
        if path not in self.disk_slugs:
            self.disk_slugs[path] = md.heading_slugs(Path(path))
        return self.disk_slugs[path]


@cache
def shipped_canonical() -> Mapping[str, bytes]:
    """Each canonical file name to the bytes of the copy shipped in this package."""
    shipped = resources.files("dev_playbook") / SHIPPED_CANONICAL
    return {name: (shipped / name).read_bytes() for name in sources.CANONICAL_FILES}


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
    code = _indented_code(content)
    return MarkdownFile(
        path=path,
        text=text,
        frontmatter=frontmatter,
        headings=headings,
        trailers=trailers,
        links=_links(content),
        content=content,
        indented_code=code,
        bare_paths=_bare_paths(tuple((n, t) for n, t in content if n not in code)),
    )


_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$")


def _heading_above(headings: tuple[Heading, ...], line: int) -> Heading | None:
    above = [h for h in headings if h.line < line]
    return above[-1] if above else None


@dataclass(frozen=True)
class _Joined:
    """Content lines with inline code stripped, joined, and each offset's line."""

    text: str
    starts: list[int]
    numbers: list[int]

    def line(self, offset: int) -> int:
        """The line number the character at ``offset`` sits on."""
        return self.numbers[bisect.bisect_right(self.starts, offset) - 1]


def _join(content: tuple[tuple[int, str], ...]) -> _Joined:
    """Strip inline code spans line by line, then join the lines.

    A bracketed example inside backticks is then prose, not a link, and a
    link whose text wraps a line break is one match of the joined text.
    """
    stripped = [md.INLINE_CODE_PATTERN.sub("", text) for _, text in content]
    starts = [0]
    for text in stripped[:-1]:
        starts.append(starts[-1] + len(text) + 1)
    return _Joined("\n".join(stripped), starts, [n for n, _ in content])


def _links(content: tuple[tuple[int, str], ...]) -> tuple[Link, ...]:
    """Every inline link in the content lines, wrapped text included.

    A link is reported on the line its ``[`` opens.
    """
    joined = _join(content)
    return tuple(
        Link(m.group(1), m.group(2), joined.line(m.start()))
        for m in LINK_PATTERN.finditer(joined.text)
    )


def _bare_paths(content: tuple[tuple[int, str], ...]) -> tuple[BarePath, ...]:
    """Every ``~/workspace/`` path in the content lines outside a link's target.

    A link's brackets and target become spaces, so every offset keeps its
    line and a path in the link's text is still read. A trailing ``.``,
    ``,``, ``;``, or ``:`` ends the sentence, not the path.
    """
    joined = _join(content)
    masked = list(joined.text)
    text_spans: list[tuple[int, int]] = []
    for m in LINK_PATTERN.finditer(joined.text):
        text_spans.append(m.span(1))
        for i in range(m.start(), m.end()):
            if not m.start(1) <= i < m.end(1) and masked[i] != "\n":
                masked[i] = " "
    found: list[BarePath] = []
    for m in md.WORKSPACE_REF_PATTERN.finditer("".join(masked)):
        target = m.group(0).rstrip(md.BARE_PATH_TRAILER)
        in_link = any(start <= m.start() < end for start, end in text_spans)
        found.append(BarePath(target, joined.line(m.start()), in_link))
    return tuple(found)


def _indented_code(content: tuple[tuple[int, str], ...]) -> frozenset[int]:
    """The line numbers of the indented code blocks among the content lines.

    A line opens or continues one when it follows a blank line or another
    such line, is indented four columns past its container's content
    column, and is not a list item. The container is the document, column
    0, or the list item last opened at or left of the line, whose content
    column is past its marker and the spaces after it, so a list item's
    continuation paragraph is not code.
    """
    found: set[int] = set()
    base = 0
    after_blank = False
    in_block = False
    for number, text in content:
        if not text.strip():
            after_blank = True
            continue
        indent = len(text) - len(text.lstrip(" "))
        item = LIST_ITEM.match(text)
        if (after_blank or in_block) and indent >= base + 4 and item is None:
            found.add(number)
            in_block = True
        elif item is not None:
            in_block = False
            spaces = len(item.group(3))
            base = indent + len(item.group(2)) + (spaces if 1 <= spaces <= 4 else 1)
        else:
            in_block = False
            if after_blank and indent < base:
                base = indent
        after_blank = False
    return frozenset(found)
