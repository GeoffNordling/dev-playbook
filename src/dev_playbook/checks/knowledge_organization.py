"""The knowledge-organization family: the rules of ``standards/knowledge-organization/``.

Thirty-five rules, each decided by a function over the model. Three hold the
root ``CONTEXT.md`` to its type, its ``## Language`` section, and the shape of
an entry. Eight hold a reference in a markdown file to the cross-reference
grammar: it resolves, its anchor names a distinct, unnumbered heading, and its
form fits where the target lives and whether the file has a fixed repo root.
Eleven hold a concept document to its frontmatter, one a directory of concept
documents to its ``index.md``, five an ``index.md`` to its listing, one a
``README.md`` to its H1, three a consumer's ``okf_types`` mapping to its shape,
and three ``working-docs/`` to its sets.

Two checks, the ones that read a ``~/workspace/<other repo>/`` target, read
that repo's main checkout on this machine and are tagged ``WORKSPACE``.
"""

import bisect
import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass
from functools import cache
from pathlib import Path, PurePosixPath
from typing import Any

from dev_playbook import md, sources
from dev_playbook.check_registry import WORKSPACE, Finding, check
from dev_playbook.model import LINK_PATTERN, Heading, MarkdownFile, Repo

CONTEXT = "CONTEXT.md"
ROOT_INDEX = "index.md"
INDEX = "index.md"
README = "README.md"
ROOT_NOTE = "ROOT.md"
WORKING_DOCS = "working-docs"
VOCABULARY = "Vocabulary"
README_TYPE = "README"
LANGUAGE = "Language"
AVOID = "_Avoid_:"
ORDERING = "Ordering:"
LOCAL_TYPES = "okf_types"
OKF_VERSION = "okf_version"
PLANNED_AND_COMPLETED = ("Planned", "Completed")
RESOURCE_REQUIRED = "Recipe-Description"
LIVES_UNDER = {
    "Standard": "standards/",
    "Loop": "loops/",
    "Guide": "guides/",
}
CANONICAL_PREFIX = sources.CANONICAL_DIR + "/"
WORKSPACE_PREFIX = "~/workspace/"
CLAUDE_PREFIX = "~/.claude/"
# A URI: a scheme, then a colon.
URI = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
# A bare `~/workspace/...` path outside a link and outside code.
WORKSPACE_PATH = re.compile(r"~/workspace/[^\s)`]+")
# A heading that starts with a section number, such as `3. Bundle` or `2.2.3 X`.
NUMBERED_HEADING = re.compile(r"^\d+(\.\d+)*\.?\s")
# A type name: Title Case, hyphen-joined for a multi-word name.
TYPE_NAME = re.compile(r"[A-Z][A-Za-z0-9]*(?:-[A-Z][A-Za-z0-9]*)*")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIXED_NAMES = frozenset(
    {INDEX, ROOT_NOTE, README, "PROMPT.md", "SKILL.md", "CLAUDE.md"}
)
BULLET = re.compile(r"^\s*[-*+]\s")
TOP_BULLET = re.compile(r"^[-*+]\s")
LIST_MARKER = re.compile(r"^(?:[-*+]|\d+[.)])(?:\s|$)")
# An index bullet: a link at the start of a bullet, then the rest of the line.
INDEX_ENTRY = re.compile(r"^\s*[-*+]\s+\[([^\]]*)\]\(([^)\s]+)\)(.*)$")
BOLD_TERM = re.compile(r"^\*\*[^*]+\*\*$")
BOLD_START = re.compile(r"^[-*+]\s+\*\*")


@dataclass(frozen=True)
class Reference:
    """One reference in a markdown file: a link target or a bare workspace path."""

    source: str
    line: int
    target: str
    text: str
    bare: bool

    @property
    def path(self) -> str:
        """The target without its ``#anchor``."""
        return self.target.partition("#")[0]

    @property
    def anchor(self) -> str:
        """The target's ``#anchor``, without the ``#``; empty where there is none."""
        return self.target.partition("#")[2]


@dataclass(frozen=True)
class Resolved:
    """Where a reference points: this repo's path, another repo's, or nowhere read.

    ``kind`` is ``repo`` (``path`` is repo-relative, ``""`` the root), ``other``
    (``path`` is the full path on this machine), ``outside`` (a relative target
    above the repo root), or ``skip`` (a URI, a ``~/.claude/`` path, or any form
    the grammar does not resolve).
    """

    kind: str
    path: str


# --- shared: references --------------------------------------------------


def _sources(repo: Repo) -> Iterator[MarkdownFile]:
    """Every markdown file a reference is read from: all but a numbered Decision Record."""
    for path, doc in repo.markdown.items():
        if not md.is_decision_record(path):
            yield doc


def _indented_code(doc: MarkdownFile) -> frozenset[int]:
    """The line numbers of the indented code blocks in a file.

    A line opens or continues one when it follows a blank line or another
    such line, is indented four columns past the last prose line before the
    blank, and is not a list item.
    """
    found: set[int] = set()
    base = 0
    after_blank = False
    in_block = False
    for number, text in doc.content:
        if not text.strip():
            after_blank = True
            continue
        indent = len(text) - len(text.lstrip(" "))
        stripped = text.lstrip(" ")
        opens = (after_blank or in_block) and indent >= base + 4
        if opens and not LIST_MARKER.match(stripped):
            found.add(number)
            in_block = True
        else:
            in_block = False
            base = indent
        after_blank = False
    return frozenset(found)


def _references(doc: MarkdownFile) -> list[Reference]:
    """Every reference in one file, outside fenced and indented code.

    A reference is an inline link's target, or a ``~/workspace/`` path
    outside a link. Inline code spans are not read. The lines are joined so a
    link whose text wraps a line break is one link.
    """
    code = _indented_code(doc)
    refs = [
        Reference(doc.path, link.line, link.target, link.text, False)
        for link in doc.links
        if link.line not in code
    ]
    kept = [(n, t) for n, t in doc.content if n not in code]
    stripped = [md.INLINE_CODE_PATTERN.sub("", t) for _, t in kept]
    starts = [0]
    for text in stripped[:-1]:
        starts.append(starts[-1] + len(text) + 1)
    joined = "\n".join(stripped)
    # A link becomes spaces of its own length, so every offset still maps to its line.
    masked = LINK_PATTERN.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), joined)
    for m in WORKSPACE_PATH.finditer(masked):
        line = kept[bisect.bisect_right(starts, m.start()) - 1][0]
        refs.append(Reference(doc.path, line, m.group(0), "", True))
    return refs


def _resolve(repo: Repo, ref: Reference) -> Resolved:
    """Where one reference points, read from the linking file's repo."""
    path = ref.path
    if not path:
        return Resolved("repo", ref.source) if ref.anchor else Resolved("skip", "")
    if URI.match(path) or path.startswith(CLAUDE_PREFIX):
        return Resolved("skip", "")
    if path.startswith(WORKSPACE_PREFIX):
        name, _, rest = path.removeprefix(WORKSPACE_PREFIX).partition("/")
        if name == repo.name:
            return Resolved("repo", _normal(rest))
        return Resolved("other", str(Path.home() / "workspace" / name / rest))
    if path.startswith("~"):
        return Resolved("skip", "")
    if path.startswith("/"):
        return Resolved("repo", _normal(path.lstrip("/")))
    joined = posixpath.normpath(posixpath.join(posixpath.dirname(ref.source), path))
    if joined == ".." or joined.startswith("../"):
        return Resolved("outside", joined)
    return Resolved("repo", _normal(joined))


def _normal(path: str) -> str:
    normal = posixpath.normpath(path) if path else ""
    return "" if normal == "." else normal


def _exists(repo: Repo, path: str) -> bool:
    """True for the root, a tracked file, or a directory holding a tracked file."""
    if not path or path in repo.contents:
        return True
    prefix = path + "/"
    return any(f.startswith(prefix) for f in repo.files)


@cache
def _slugs_on_disk(path: str) -> frozenset[str]:
    return md.heading_slugs(Path(path))


def _heading(repo: Repo, resolved: Resolved, anchor: str) -> Heading | None:
    """The heading of an in-repo ``.md`` target whose slug is ``anchor``."""
    doc = repo.markdown.get(resolved.path)
    if doc is None:
        return None
    return next((h for h in doc.headings if h.slug == anchor), None)


def _is_repo_md(repo: Repo, resolved: Resolved) -> bool:
    return resolved.kind == "repo" and resolved.path in repo.markdown


def _bundle(path: str) -> str | None:
    """The ``.../skills/<name>`` directory a file sits in, or None."""
    parts = PurePosixPath(path).parts
    for i, part in enumerate(parts[:-2]):
        if part == "skills":
            return "/".join(parts[: i + 2])
    return None


def _inside(path: str, directory: str) -> bool:
    return path == directory or path.startswith(directory + "/")


# --- context-content.md --------------------------------------------------


@check("knowledge-organization.frontmatter-declares-type-vocabulary")
def frontmatter_declares_type_vocabulary(repo: Repo) -> Iterator[Finding]:
    """A repo's ``CONTEXT.md`` declares ``type: Vocabulary`` in its frontmatter."""
    doc = repo.markdown.get(CONTEXT)
    if doc is None:
        return
    front = doc.frontmatter or {}
    if front.get("type") != VOCABULARY:
        yield Finding(CONTEXT, None, f"frontmatter does not declare type: {VOCABULARY}")


@check("knowledge-organization.language-section-present")
def language_section_present(repo: Repo) -> Iterator[Finding]:
    """A repo's ``CONTEXT.md`` has a ``## Language`` section."""
    doc = repo.markdown.get(CONTEXT)
    if doc is None:
        return
    if not any(h.level == 2 and h.text == LANGUAGE for h in doc.headings):
        yield Finding(CONTEXT, None, f"no '## {LANGUAGE}' section")


@check("knowledge-organization.term-definition-avoid-line")
def term_definition_avoid_line(repo: Repo) -> Iterator[Finding]:
    """An entry under ``## Language`` is a bold term, its definition, and at most one last ``_Avoid_:`` line."""
    doc = repo.markdown.get(CONTEXT)
    if doc is None:
        return
    section = next(
        (h for h in doc.headings if h.level == 2 and h.text == LANGUAGE), None
    )
    if section is None:
        return
    for paragraph in _paragraphs(doc.section(section.slug)):
        yield from _entry_findings(paragraph)


def _paragraphs(
    lines: tuple[tuple[int, str], ...],
) -> list[list[tuple[int, str]]]:
    """Split lines into paragraphs at blank lines and headings."""
    paragraphs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for number, text in lines:
        if not text.strip() or text.lstrip().startswith("#"):
            if current:
                paragraphs.append(current)
            current = []
            continue
        current.append((number, text))
    if current:
        paragraphs.append(current)
    return paragraphs


def _entry_findings(paragraph: list[tuple[int, str]]) -> Iterator[Finding]:
    first_line, first = paragraph[0]
    avoids = [(n, t) for n, t in paragraph if t.startswith(AVOID)]
    if not first.startswith("**"):
        for number, _ in avoids:
            yield Finding(CONTEXT, number, f"an '{AVOID}' line outside an entry")
        return
    if not BOLD_TERM.match(first.strip()):
        yield Finding(
            CONTEXT, first_line, "an entry's first line is not only the term in bold"
        )
    definitions = [(n, t) for n, t in paragraph[1:] if not t.startswith(AVOID)]
    if not definitions:
        yield Finding(CONTEXT, first_line, "an entry has no definition line")
    for number, _ in avoids[1:]:
        yield Finding(CONTEXT, number, f"an entry has more than one '{AVOID}' line")
    if len(avoids) == 1 and avoids[0][0] != paragraph[-1][0]:
        yield Finding(
            CONTEXT, avoids[0][0], f"the '{AVOID}' line is not the entry's last"
        )


# --- cross-references.md -------------------------------------------------


@check("knowledge-organization.reference-resolves", needs=[WORKSPACE])
def reference_resolves(repo: Repo) -> Iterator[Finding]:
    """The target of a reference exists, another repo's read from its main checkout."""
    for doc in _sources(repo):
        for ref in _references(doc):
            resolved = _resolve(repo, ref)
            if resolved.kind == "repo" and not _exists(repo, resolved.path):
                yield Finding(
                    ref.source, ref.line, f"reference does not resolve: {ref.target}"
                )
            if resolved.kind == "other" and not Path(resolved.path).exists():
                yield Finding(
                    ref.source, ref.line, f"reference does not resolve: {ref.target}"
                )


@check("knowledge-organization.fragment-anchor-matches-the-slug", needs=[WORKSPACE])
def fragment_anchor_matches_the_slug(repo: Repo) -> Iterator[Finding]:
    """In a reference to a ``.md`` file that ends ``#anchor``, the anchor is a heading's slug."""
    for doc in _sources(repo):
        for ref in _references(doc):
            if not ref.anchor:
                continue
            resolved = _resolve(repo, ref)
            if _is_repo_md(repo, resolved):
                slugs = {h.slug for h in repo.markdown[resolved.path].headings}
            elif (
                resolved.kind == "other"
                and resolved.path.endswith(".md")
                and Path(resolved.path).is_file()
            ):
                slugs = set(_slugs_on_disk(resolved.path))
            else:
                continue
            if ref.anchor not in slugs:
                yield Finding(
                    ref.source,
                    ref.line,
                    f"anchor names no heading slug of the target: {ref.target}",
                )


@check("knowledge-organization.headings-slugify-distinctly")
def headings_slugify_distinctly(repo: Repo) -> Iterator[Finding]:
    """No two headings in a ``.md`` file, a numbered Decision Record aside, share a slug."""
    for doc in _sources(repo):
        seen: set[str] = set()
        for heading in doc.headings:
            if heading.slug in seen:
                yield Finding(
                    doc.path,
                    heading.line,
                    f"heading slug '{heading.slug}' repeats an earlier heading's",
                )
            seen.add(heading.slug)


@check("knowledge-organization.stable-named-anchor")
def stable_named_anchor(repo: Repo) -> Iterator[Finding]:
    """A reference's ``#anchor`` does not name a heading that starts with a section number."""
    for doc in _sources(repo):
        for ref in _references(doc):
            if not ref.anchor:
                continue
            resolved = _resolve(repo, ref)
            if not _is_repo_md(repo, resolved):
                continue
            heading = _heading(repo, resolved, ref.anchor)
            if heading is not None and NUMBERED_HEADING.match(heading.text):
                yield Finding(
                    ref.source,
                    ref.line,
                    f"anchor names a numbered heading: {ref.target}",
                )


@check("knowledge-organization.workspace-path-for-another-repo")
def workspace_path_for_another_repo(repo: Repo) -> Iterator[Finding]:
    """Another repo's file is a ``~/workspace/<repo>/`` link: no bare path, no relative climb."""
    for doc in _sources(repo):
        for ref in _references(doc):
            resolved = _resolve(repo, ref)
            if ref.bare and resolved.kind == "other":
                yield Finding(
                    ref.source,
                    ref.line,
                    f"another repo's path outside a link: {ref.target}",
                )
            if not ref.bare and resolved.kind == "outside":
                yield Finding(
                    ref.source,
                    ref.line,
                    f"relative target leaves the repo root: {ref.target}",
                )


@check("knowledge-organization.root-absolute-path-in-the-same-repo")
def root_absolute_path_in_the_same_repo(repo: Repo) -> Iterator[Finding]:
    """In a file with a fixed repo root, a same-repo reference is a ``/`` link."""
    for doc in _sources(repo):
        if not md.has_fixed_repo_root(doc.path):
            continue
        for ref in _references(doc):
            if _is_this_workspace(repo, ref):
                yield Finding(
                    ref.source,
                    ref.line,
                    f"same-repo target must be a '/' link, not a workspace path: {ref.target}",
                )
            elif _is_relative(ref) and _resolve(repo, ref).kind == "repo":
                yield Finding(
                    ref.source,
                    ref.line,
                    f"same-repo target must be a '/' link, not relative: {ref.target}",
                )


def _is_this_workspace(repo: Repo, ref: Reference) -> bool:
    return ref.path.startswith(f"{WORKSPACE_PREFIX}{repo.name}/") or (
        ref.path == f"{WORKSPACE_PREFIX}{repo.name}"
    )


def _is_relative(ref: Reference) -> bool:
    path = ref.path
    return (
        not ref.bare
        and bool(path)
        and not path.startswith(("/", "~"))
        and not URI.match(path)
    )


@check("knowledge-organization.workspace-path-for-a-stable-location")
def workspace_path_for_a_stable_location(repo: Repo) -> Iterator[Finding]:
    """In a file with no fixed repo root, a same-repo target outside its bundle is a workspace link."""
    for doc in _sources(repo):
        if md.has_fixed_repo_root(doc.path):
            continue
        bundle = _bundle(doc.path)
        for ref in _references(doc):
            if ref.bare:
                continue
            resolved = _resolve(repo, ref)
            if resolved.kind != "repo":
                continue
            outside = bundle is None or not _inside(resolved.path, bundle)
            if not outside:
                continue
            if ref.path.startswith("/"):
                yield Finding(
                    ref.source,
                    ref.line,
                    f"'/' target in a file with no fixed repo root: {ref.target}",
                )
            elif _is_relative(ref):
                yield Finding(
                    ref.source,
                    ref.line,
                    f"relative target leaves the file's skill bundle: {ref.target}",
                )


@check("knowledge-organization.relative-path-inside-the-bundle")
def relative_path_inside_the_bundle(repo: Repo) -> Iterator[Finding]:
    """In a skill bundle, a link to a file of the same bundle has a relative target."""
    for doc in _sources(repo):
        bundle = _bundle(doc.path)
        if bundle is None:
            continue
        for ref in _references(doc):
            if ref.bare or _is_relative(ref):
                continue
            inside = _bundle_target(repo, ref, bundle)
            if inside:
                yield Finding(
                    ref.source,
                    ref.line,
                    f"target inside the file's own bundle must be relative: {ref.target}",
                )


def _bundle_target(repo: Repo, ref: Reference, bundle: str) -> bool:
    """True where a ``/``, ``~/workspace/``, or ``~/.claude/`` target lands in ``bundle``."""
    path = ref.path
    if path.startswith(CLAUDE_PREFIX):
        skill = "skills/" + PurePosixPath(bundle).name
        return _inside(_normal(path.removeprefix(CLAUDE_PREFIX)), skill)
    if not path.startswith(("/", WORKSPACE_PREFIX)):
        return False
    resolved = _resolve(repo, ref)
    return resolved.kind == "repo" and _inside(resolved.path, bundle)


# --- document-types.md ---------------------------------------------------


def _concept_documents(repo: Repo) -> Iterator[MarkdownFile]:
    for path, doc in repo.markdown.items():
        if md.classify(path) == "concept":
            yield doc


def _is_dev_playbook(repo: Repo) -> bool:
    return any(path.startswith(CANONICAL_PREFIX) for path in repo.files)


def _local_types(repo: Repo) -> dict[Any, Any] | None:
    """The root index's ``okf_types`` mapping, where a consumer declares one."""
    if _is_dev_playbook(repo):
        return None
    index = repo.markdown.get(ROOT_INDEX)
    if index is None or index.frontmatter is None:
        return None
    declared = index.frontmatter.get(LOCAL_TYPES)
    return declared if isinstance(declared, dict) else None


def _registry(repo: Repo) -> frozenset[str]:
    local = _local_types(repo) or {}
    names = {k for k in local if isinstance(k, str) and TYPE_NAME.fullmatch(k)}
    return sources.REGISTERED_TYPES | names


@check("knowledge-organization.frontmatter-a-yaml-mapping")
def frontmatter_a_yaml_mapping(repo: Repo) -> Iterator[Finding]:
    """A concept document opens with a ``---`` frontmatter block whose YAML is a mapping."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            yield Finding(doc.path, None, "no frontmatter mapping")


@check("knowledge-organization.type-names-a-registered-type")
def type_names_a_registered_type(repo: Repo) -> Iterator[Finding]:
    """A concept document's ``type`` names a registered type or a local ``okf_types`` entry."""
    registry = _registry(repo)
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            continue
        doctype = doc.frontmatter.get("type")
        if doctype is None:
            yield Finding(doc.path, None, "missing 'type'")
        elif doctype not in registry:
            yield Finding(doc.path, None, f"type '{doctype}' is not registered")


@check("knowledge-organization.non-empty-title")
def non_empty_title(repo: Repo) -> Iterator[Finding]:
    """A concept document's frontmatter has a non-empty ``title``."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is not None and not doc.frontmatter.get("title"):
            yield Finding(doc.path, None, "missing 'title'")


@check("knowledge-organization.non-empty-description-no-closing-period")
def non_empty_description_no_closing_period(repo: Repo) -> Iterator[Finding]:
    """A concept document's ``description`` is non-empty and does not end with a period."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            continue
        description = doc.frontmatter.get("description")
        if not description:
            yield Finding(doc.path, None, "missing 'description'")
        elif isinstance(description, str) and description.rstrip().endswith("."):
            yield Finding(doc.path, None, "description ends with a period")


@check("knowledge-organization.resource-a-repo-root-path-or-a-uri")
def resource_a_repo_root_path_or_a_uri(repo: Repo) -> Iterator[Finding]:
    """A concept document's ``resource``, where present, starts ``/`` or is a URI."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is None or "resource" not in doc.frontmatter:
            continue
        resource = doc.frontmatter["resource"]
        if not isinstance(resource, str) or not (
            resource.startswith("/") or URI.match(resource)
        ):
            yield Finding(
                doc.path, None, f"resource {resource!r} is not a '/' path or a URI"
            )


@check("knowledge-organization.no-tags-or-timestamp")
def no_tags_or_timestamp(repo: Repo) -> Iterator[Finding]:
    """A concept document's frontmatter has no ``tags`` and no ``timestamp`` key."""
    for doc in _concept_documents(repo):
        for key in ("tags", "timestamp"):
            if doc.frontmatter is not None and key in doc.frontmatter:
                yield Finding(doc.path, None, f"frontmatter has a '{key}' key")


@check("knowledge-organization.recipe-description-carries-a-resource")
def recipe_description_carries_a_resource(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Recipe-Description`` has a non-empty ``resource``."""
    for doc in _concept_documents(repo):
        front = doc.frontmatter
        if (
            front
            and front.get("type") == RESOURCE_REQUIRED
            and not front.get("resource")
        ):
            yield Finding(
                doc.path, None, f"'{RESOURCE_REQUIRED}' requires a 'resource'"
            )


def _lives_under(repo: Repo, doctype: str) -> Iterator[Finding]:
    home = LIVES_UNDER[doctype]
    for doc in _concept_documents(repo):
        front = doc.frontmatter
        if front and front.get("type") == doctype and not doc.path.startswith(home):
            yield Finding(doc.path, None, f"'{doctype}' lives under {home}")


@check("knowledge-organization.standard-lives-under-standards")
def standard_lives_under_standards(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Standard`` lives under ``standards/``."""
    yield from _lives_under(repo, "Standard")


@check("knowledge-organization.loop-lives-under-loops")
def loop_lives_under_loops(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Loop`` lives under ``loops/``."""
    yield from _lives_under(repo, "Loop")


@check("knowledge-organization.guide-lives-under-guides")
def guide_lives_under_guides(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Guide`` lives under ``guides/``."""
    yield from _lives_under(repo, "Guide")


@check("knowledge-organization.readmemd-is-typed-readme")
def readmemd_is_typed_readme(repo: Repo) -> Iterator[Finding]:
    """A concept document is named ``README.md`` exactly where it has ``type: README``."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is None or "type" not in doc.frontmatter:
            continue
        named = PurePosixPath(doc.path).name == README
        typed = doc.frontmatter["type"] == README_TYPE
        if named and not typed:
            yield Finding(
                doc.path, None, f"a {README} does not have type: {README_TYPE}"
            )
        if typed and not named:
            yield Finding(
                doc.path, None, f"type: {README_TYPE} on a file not named {README}"
            )


# --- documentation-sets.md -----------------------------------------------


@check("knowledge-organization.an-index-in-every-directory")
def an_index_in_every_directory(repo: Repo) -> Iterator[Finding]:
    """Every directory that has a concept document has an ``index.md``."""
    directories = {posixpath.dirname(doc.path) for doc in _concept_documents(repo)}
    for directory in sorted(directories):
        index = posixpath.join(directory, INDEX)
        if index not in repo.contents:
            yield Finding(
                index, None, "directory has concept documents but no index.md"
            )


# --- indexes.md ----------------------------------------------------------


def _indexes(repo: Repo) -> Iterator[MarkdownFile]:
    for path, doc in repo.markdown.items():
        if md.classify(path) == "index":
            yield doc


@check("knowledge-organization.no-okf-type")
def no_okf_type(repo: Repo) -> Iterator[Finding]:
    """The frontmatter of an ``index.md`` has no ``type`` key."""
    for doc in _indexes(repo):
        if doc.frontmatter is not None and "type" in doc.frontmatter:
            yield Finding(doc.path, None, "an index.md has a 'type' key")


@check("knowledge-organization.introduction-between-h1-and-listing")
def introduction_between_h1_and_listing(repo: Repo) -> Iterator[Finding]:
    """An ``index.md`` has a line of prose between its H1 and its first listed entry."""
    for doc in _indexes(repo):
        prose = False
        for _, text in doc.content:
            stripped = text.strip()
            if BULLET.match(text):
                break
            if stripped.startswith("# "):
                prose = False
            elif stripped and not stripped.startswith(("#", ORDERING)):
                prose = True
        if not prose:
            yield Finding(
                doc.path, None, "no introduction between the H1 and the first entry"
            )


@dataclass(frozen=True)
class Entry:
    """One bullet of an index's listing; ``target`` is empty where no ``/`` link opens it."""

    line: int
    text: str
    target: str
    rest: str


def _entries(doc: MarkdownFile) -> list[Entry]:
    entries: list[Entry] = []
    for number, text in doc.content:
        if not BULLET.match(text):
            continue
        m = INDEX_ENTRY.match(text)
        if m and m.group(2).startswith("/"):
            target = m.group(2).partition("#")[0].lstrip("/")
            entries.append(Entry(number, m.group(1), target, m.group(3)))
        else:
            entries.append(Entry(number, "", "", text))
    return entries


def _child_indexes(repo: Repo, directory: str) -> set[str]:
    """The ``index.md`` of each directory directly under ``directory``."""
    prefix = directory + "/" if directory else ""
    return {
        path
        for path in repo.contents
        if path.startswith(prefix)
        and path.count("/") == prefix.count("/") + 1
        and PurePosixPath(path).name == INDEX
    }


@check("knowledge-organization.one-entry-per-concept-document-and-child-directory")
def one_entry_per_concept_document_and_child_directory(
    repo: Repo,
) -> Iterator[Finding]:
    """An ``index.md`` lists each concept document and child index once, with the description."""
    concepts = {doc.path: doc for doc in _concept_documents(repo)}
    for doc in _indexes(repo):
        directory = posixpath.dirname(doc.path)
        expected = {
            path for path in concepts if posixpath.dirname(path) == directory
        } | _child_indexes(repo, directory)
        seen: set[str] = set()
        for entry in _entries(doc):
            if not entry.target:
                yield Finding(doc.path, entry.line, "a bullet with no '/' link")
                continue
            if entry.target not in expected:
                yield Finding(
                    doc.path,
                    entry.line,
                    f"lists {entry.target}, not a concept document or child index here",
                )
                continue
            if entry.target in seen:
                yield Finding(
                    doc.path, entry.line, f"lists {entry.target} more than once"
                )
            seen.add(entry.target)
            concept = concepts.get(entry.target)
            if concept is None or concept.frontmatter is None:
                continue
            description = concept.frontmatter.get("description")
            if isinstance(description, str) and entry.rest != f" — {description}":
                yield Finding(
                    doc.path,
                    entry.line,
                    f"entry for {entry.target} does not end with its description",
                )
        for missing in sorted(expected - seen):
            yield Finding(doc.path, None, f"omits {missing}")


@check("knowledge-organization.alphabetical-unless-declared-otherwise")
def alphabetical_unless_declared_otherwise(repo: Repo) -> Iterator[Finding]:
    """An index lists ``README.md`` first, then concept documents, then child indexes, each sorted."""
    for doc in _indexes(repo):
        entries = [e for e in _entries(doc) if e.target]
        if not entries:
            continue
        readmes = [i for i, e in enumerate(entries) if _group(e) == 0]
        if readmes and readmes[0] != 0:
            yield Finding(
                doc.path, entries[readmes[0]].line, "the README.md entry is not first"
            )
        if _declares_order(doc, entries[0].line):
            continue
        groups = [_group(e) for e in entries]
        if groups != sorted(groups):
            yield Finding(
                doc.path,
                None,
                "concept-document entries do not all come before child directories",
            )
        for group, name in ((1, "concept-document"), (2, "child-directory")):
            titles = [e.text.lower() for e in entries if _group(e) == group]
            if titles != sorted(titles):
                yield Finding(
                    doc.path, None, f"{name} entries are not in alphabetical order"
                )


def _group(entry: Entry) -> int:
    name = PurePosixPath(entry.target).name
    if name == README:
        return 0
    return 2 if name == INDEX else 1


def _declares_order(doc: MarkdownFile, first_entry: int) -> bool:
    return any(
        text.strip().startswith(ORDERING)
        for number, text in doc.content
        if number < first_entry
    )


@check("knowledge-organization.okf-version-declared")
def okf_version_declared(repo: Repo) -> Iterator[Finding]:
    """The ``index.md`` at the repository root declares ``okf_version``."""
    doc = repo.markdown.get(ROOT_INDEX)
    if doc is None:
        return
    if doc.frontmatter is None or OKF_VERSION not in doc.frontmatter:
        yield Finding(ROOT_INDEX, None, f"root index.md does not declare {OKF_VERSION}")


# --- readme-content.md ---------------------------------------------------


@check("knowledge-organization.readme-holds-an-h1")
def readme_holds_an_h1(repo: Repo) -> Iterator[Finding]:
    """Every ``README.md`` has an H1."""
    for path, doc in repo.markdown.items():
        if PurePosixPath(path).name == README and not any(
            h.level == 1 for h in doc.headings
        ):
            yield Finding(path, None, "no H1")


# --- type-registry.md ----------------------------------------------------


@check("knowledge-organization.type-name-to-description")
def type_name_to_description(repo: Repo) -> Iterator[Finding]:
    """Each ``okf_types`` key is a type name and its value one non-empty line."""
    if _is_dev_playbook(repo):
        return
    index = repo.markdown.get(ROOT_INDEX)
    if index is None or index.frontmatter is None:
        return
    if LOCAL_TYPES not in index.frontmatter:
        return
    declared = index.frontmatter[LOCAL_TYPES]
    if not isinstance(declared, dict):
        yield Finding(ROOT_INDEX, None, f"'{LOCAL_TYPES}' is not a mapping")
        return
    for key, value in declared.items():
        if not isinstance(key, str) or not TYPE_NAME.fullmatch(key):
            yield Finding(
                ROOT_INDEX, None, f"'{LOCAL_TYPES}' key {key!r} is not a type name"
            )
        elif not isinstance(value, str) or not value.strip() or "\n" in value.strip():
            yield Finding(
                ROOT_INDEX, None, f"local type '{key}' has no one-line description"
            )


def _local_names(repo: Repo) -> list[str]:
    declared = _local_types(repo) or {}
    return [k for k in declared if isinstance(k, str) and TYPE_NAME.fullmatch(k)]


@check("knowledge-organization.keys-in-alphabetical-order")
def keys_in_alphabetical_order(repo: Repo) -> Iterator[Finding]:
    """The keys of the ``okf_types`` mapping are in case-insensitive alphabetical order."""
    lowered = [name.lower() for name in _local_names(repo)]
    if lowered != sorted(lowered):
        yield Finding(
            ROOT_INDEX, None, f"'{LOCAL_TYPES}' keys are not in alphabetical order"
        )


@check("knowledge-organization.add-never-shadow")
def add_never_shadow(repo: Repo) -> Iterator[Finding]:
    """No ``okf_types`` key equals, ignoring case, a registered type or an earlier key."""
    upstream = {name.lower() for name in sources.REGISTERED_TYPES}
    seen = set(upstream)
    for name in _local_names(repo):
        lowered = name.lower()
        if lowered in seen:
            what = "a registered type" if lowered in upstream else "an earlier key"
            yield Finding(ROOT_INDEX, None, f"local type '{name}' shadows {what}")
        seen.add(lowered)


# --- working-documentation-sets.md ---------------------------------------


def _sets(repo: Repo) -> list[str]:
    """Each directory directly under ``working-docs/``."""
    prefix = WORKING_DOCS + "/"
    return sorted(
        {
            prefix + path.removeprefix(prefix).split("/", 1)[0]
            for path in repo.files
            if path.startswith(prefix) and path.removeprefix(prefix).count("/") >= 1
        }
    )


@check("knowledge-organization.working-docs-holds-only-sets")
def working_docs_holds_only_sets(repo: Repo) -> Iterator[Finding]:
    """``working-docs/`` directly has ``index.md``, directories, and no other file."""
    prefix = WORKING_DOCS + "/"
    for path in repo.files:
        name = path.removeprefix(prefix)
        if path.startswith(prefix) and "/" not in name and name != INDEX:
            yield Finding(
                path, None, "a file directly under working-docs/ other than index.md"
            )


@check("knowledge-organization.one-directory-under-working-docs")
def one_directory_under_working_docs(repo: Repo) -> Iterator[Finding]:
    """Each set has an ``index.md`` and a ``ROOT.md``, and its files kebab-case names."""
    for directory in _sets(repo):
        for name in (INDEX, ROOT_NOTE):
            path = f"{directory}/{name}"
            if path not in repo.contents:
                yield Finding(path, None, f"the set has no {name}")
        for path in repo.files:
            if not path.startswith(directory + "/"):
                continue
            name = PurePosixPath(path).name
            if name in FIXED_NAMES or name.endswith(".py"):
                continue
            if not KEBAB.match(name.partition(".")[0]):
                yield Finding(path, None, "the file name is not lowercase kebab-case")


def _roots(repo: Repo, directory: str) -> list[str]:
    return sorted(
        path
        for path in repo.markdown
        if path.startswith(directory + "/") and PurePosixPath(path).name == ROOT_NOTE
    )


@check("knowledge-organization.one-list-of-items-state-by-section")
def one_list_of_items_state_by_section(repo: Repo) -> Iterator[Finding]:
    """A leaf ``ROOT.md`` has one ``## Planned`` and one ``## Completed``; no other file has either."""
    for directory in _sets(repo):
        roots = _roots(repo, directory)
        leaves = {
            root
            for root in roots
            if not any(
                other != root and other.startswith(posixpath.dirname(root) + "/")
                for other in roots
            )
        }
        for path, doc in repo.markdown.items():
            if not path.startswith(directory + "/"):
                continue
            yield from _worklist_findings(doc, path in leaves)


def _worklist_findings(doc: MarkdownFile, leaf: bool) -> Iterator[Finding]:
    for name in PLANNED_AND_COMPLETED:
        headings = [h for h in doc.headings if h.level == 2 and h.text == name]
        if leaf and len(headings) != 1:
            yield Finding(
                doc.path, None, f"has {len(headings)} '## {name}' sections, not one"
            )
        if not leaf:
            for heading in headings:
                yield Finding(
                    doc.path, heading.line, f"a '## {name}' outside a leaf ROOT.md"
                )
        for heading in headings[:1] if leaf else ():
            for number, text in doc.section(heading.slug):
                if TOP_BULLET.match(text) and not BOLD_START.match(text):
                    yield Finding(
                        doc.path,
                        number,
                        "a worklist item does not start with a bold name",
                    )
