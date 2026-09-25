"""The knowledge-organization family: the rules of ``standards/knowledge-organization/``.

Thirty-seven rules, each decided by a function over the model. Three hold the
root ``CONTEXT.md`` to its type, its ``## Language`` section, and the shape of
an entry. Eight hold a reference in a markdown file to the cross-reference
grammar: it resolves, its anchor names a distinct, unnumbered heading, and its
form fits where the target lives and whether the file has a fixed repo root.
Twelve hold a concept document to its frontmatter, one a directory of concept
documents to its ``index.md``, five an ``index.md`` to its listing, one a
``README.md`` to its H1, three a consumer's table of local OKF types to its shape,
and four ``workstreams/`` to the files of its workstreams.

Two checks, the ones that read a ``~/workspace/<other repo>/`` target, read
that repo's main checkout on this machine and are tagged ``WORKSPACE``.
"""

import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dev_playbook import md, sources
from dev_playbook.check_registry import WORKSPACE, Finding, check
from dev_playbook.model import Heading, MarkdownFile, Repo

CONTEXT = "CONTEXT.md"
ROOT_INDEX = "index.md"
INDEX = "index.md"
README = "README.md"
HEAD_FILE = "WORKSTREAM.md"
WORKSTREAMS = "workstreams"
VOCABULARY = "Vocabulary"
README_TYPE = "README"
LANGUAGE = "Language"
AVOID = "_Avoid_:"
ORDERING = "Ordering:"
OKF_VERSION = "okf_version"
PLANNED_AND_COMPLETED = ("Planned", "Completed")
RESOURCE_REQUIRED = "Recipe-Description"
LIVES_UNDER = {
    "Standard": "standards/",
    "Loop": "loops/",
    "Guide": "guides/",
    "Registry": "registries/",
}
# Where the harness files ``~/.claude/`` holds are tracked, in dev-playbook.
CLAUDE_SOURCE = "dotfiles/dot-claude"
# The slug of a heading that starts with a section number: `3. Bundle` slugs
# to `3-bundle`, `2.2.3 Revision` to `223-revision`.
NUMBERED_SLUG = re.compile(r"^\d+-")
# A line made only of three or more ``=`` or ``-``: a setext underline or a divider.
UNDERLINE = re.compile(r"^\s*(={3,}|-{3,})\s*$")
# A type name: Title Case, hyphen-joined for a multi-word name.
TYPE_NAME = re.compile(r"[A-Z][A-Za-z0-9]*(?:-[A-Z][A-Za-z0-9]*)*")
# A file name's extension: lowercase letters and digits after the last dot.
EXTENSION = re.compile(r"^[a-z0-9]*$")
FIXED_NAMES = frozenset(
    {
        INDEX,
        HEAD_FILE,
        README,
        "PLAN.md",
        "PROGRESS.md",
        "PROMPT.md",
        "SKILL.md",
        "CLAUDE.md",
    }
)
BULLET = re.compile(r"^\s*[-*+]\s")
TOP_BULLET = re.compile(r"^[-*+]\s")
# An index bullet: a link at the start of a bullet, then the rest of the line.
INDEX_ENTRY = re.compile(r"^\s*[-*+]\s+\[([^\]]*)\]\(([^)\s]+)\)(.*)$")
BOLD_TERM = re.compile(r"^\*\*[^*]+\*\*$")
BOLD_START = re.compile(r"^[-*+]\s+\*\*")


@dataclass(frozen=True)
class Reference:
    """One reference in a markdown file: a link target or a bare workspace path.

    ``in_link`` is True for a bare path that sits in a link's text.
    """

    source: str
    line: int
    target: str
    text: str
    bare: bool
    in_link: bool = False

    @property
    def path(self) -> str:
        """The target without its ``#anchor``."""
        return self.target.partition("#")[0]

    @property
    def anchor(self) -> str:
        """The target's ``#anchor``, without the ``#``; empty where there is none."""
        return self.target.partition("#")[2]


# --- shared: references --------------------------------------------------


def _sources(repo: Repo) -> Iterator[MarkdownFile]:
    """Every markdown file a reference is read from: all but a numbered Decision Record."""
    for path, doc in repo.markdown.items():
        if not md.is_decision_record(path):
            yield doc


def _references(doc: MarkdownFile) -> list[Reference]:
    """Every reference in one file, outside fenced and indented code.

    A reference is an inline link's target, or a ``~/workspace/`` path
    outside a link's target, as the model reads both.
    """
    refs = [
        Reference(doc.path, link.line, link.target, link.text, False)
        for link in doc.links
        if link.line not in doc.indented_code
    ]
    refs.extend(
        Reference(doc.path, bare.line, bare.target, "", True, bare.in_link)
        for bare in doc.bare_paths
    )
    return refs


def _resolve(repo: Repo, ref: Reference) -> md.Target:
    """Where one reference points, read from the linking file's repo.

    A ``~/.claude/`` target resolves into ``dotfiles/dot-claude/`` where the
    repo tracks that directory, and is skipped where it does not.
    """
    claude_root = CLAUDE_SOURCE if _has_dir(repo, CLAUDE_SOURCE) else None
    return md.resolve_target(ref.source, ref.target, repo.name, claude_root)


def _has_dir(repo: Repo, directory: str) -> bool:
    prefix = directory + "/"
    return any(f.startswith(prefix) for f in repo.files)


def _exists(repo: Repo, path: str) -> bool:
    """True for the root, a tracked file, or a directory holding a tracked file."""
    if not path or path in repo.contents:
        return True
    prefix = path + "/"
    return any(f.startswith(prefix) for f in repo.files)


def _is_repo_md(repo: Repo, resolved: md.Target) -> bool:
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
    for paragraph in _paragraphs(_under(doc, section)):
        yield from _entry_findings(paragraph)


def _under(doc: MarkdownFile, heading: Heading) -> tuple[tuple[int, str], ...]:
    """The content lines under ``heading``, to the next heading of its level or higher."""
    end = next(
        (
            h.line
            for h in doc.headings
            if h.line > heading.line and h.level <= heading.level
        ),
        None,
    )
    return tuple(
        (n, t) for n, t in doc.content if n > heading.line and (end is None or n < end)
    )


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
                slugs = set(repo.slugs_on_disk(resolved.path))
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


@check("knowledge-organization.atx-headings-only")
def atx_headings_only(repo: Repo) -> Iterator[Finding]:
    """No line of only ``=`` or ``-`` sits directly under a line of text.

    Reads the lines outside fences and the frontmatter block, so a line
    directly above is text only where it is the previous content line.
    A numbered Decision Record is frozen and exempt, as ``_sources`` reads.
    """
    for doc in _sources(repo):
        previous: tuple[int, str] | None = None
        for number, text in doc.content:
            if (
                UNDERLINE.match(text)
                and previous is not None
                and previous[0] == number - 1
                and previous[1].strip()
            ):
                yield Finding(
                    doc.path,
                    number,
                    "a line of '=' or '-' under text is a setext heading; "
                    "put a blank line above a divider",
                )
            previous = (number, text)


@check("knowledge-organization.stable-named-anchor")
def stable_named_anchor(repo: Repo) -> Iterator[Finding]:
    """A reference's ``#anchor`` does not have the form of a numbered heading's slug.

    The form needs no file, so every ``.md`` target is read, in this repo or
    another, and a same-file anchor too.
    """
    for doc in _sources(repo):
        for ref in _references(doc):
            if not ref.anchor or not (not ref.path or ref.path.endswith(".md")):
                continue
            if NUMBERED_SLUG.match(ref.anchor):
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
            if ref.bare and not ref.in_link and resolved.kind == "other":
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
    return ref.path.startswith(f"{md.WORKSPACE_PREFIX}{repo.name}/") or (
        ref.path == f"{md.WORKSPACE_PREFIX}{repo.name}"
    )


def _is_relative(ref: Reference) -> bool:
    path = ref.path
    return (
        not ref.bare
        and bool(path)
        and not path.startswith(("/", "~"))
        and not md.URI_PATTERN.match(path)
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
    """True where a ``/``, ``~/workspace/``, or ``~/.claude/`` target lands in ``bundle``.

    A ``~/.claude/skills/<name>/`` target lands in the file's own bundle only
    where that bundle is ``dotfiles/dot-claude/skills/<name>/``, the copy
    ``~/.claude/`` holds.
    """
    if not ref.path.startswith(("/", md.WORKSPACE_PREFIX, md.CLAUDE_PREFIX)):
        return False
    resolved = _resolve(repo, ref)
    return resolved.kind == "repo" and _inside(resolved.path, bundle)


# --- okf-frontmatter.md ---------------------------------------------------


def _in_workstream(path: str) -> bool:
    """Whether ``path`` is under ``workstreams/``, where some rules loosen."""
    return path.startswith(WORKSTREAMS + "/")


def _concept_documents(repo: Repo) -> Iterator[MarkdownFile]:
    for path, doc in repo.markdown.items():
        if md.classify(path) == "concept":
            yield doc


@dataclass(frozen=True)
class LocalRow:
    """One row of a consumer's table of local OKF types, with its line."""

    line: int
    cells: list[str]

    @property
    def name(self) -> str | None:
        """The OKF type the first cell names, or None when it names none."""
        cell = self.cells[0] if self.cells else ""
        name = cell[1:-1] if len(cell) > 1 and cell[0] == cell[-1] == "`" else ""
        return name if TYPE_NAME.fullmatch(name) else None


def _local_table(repo: Repo) -> tuple[tuple[int, str], ...] | None:
    """The consumer's ``## OKF types`` section, or None where it declares none.

    Raises ``KeyError`` when the file is present and the heading is not.
    """
    if repo.is_dev_playbook:
        return None
    table = sources.OKF_TYPE_REGISTRY
    doc = repo.markdown.get(table.path)
    return None if doc is None else doc.section(table.heading)


def _local_rows(repo: Repo) -> list[LocalRow]:
    """The body rows of the consumer's table of local OKF types."""
    try:
        section = _local_table(repo) or ()
    except KeyError:
        return []
    rows = [
        LocalRow(n, [c.strip() for c in text.strip().strip("|").split("|")])
        for n, text in section
        if text.lstrip().startswith("|")
    ]
    return rows[2:]


def _local_names(repo: Repo) -> list[tuple[int, str]]:
    return [(row.line, row.name) for row in _local_rows(repo) if row.name]


def _registry(repo: Repo) -> frozenset[str]:
    names = {name for _, name in _local_names(repo)}
    return sources.REGISTERED_OKF_TYPES | names


@check("knowledge-organization.frontmatter-a-yaml-mapping")
def frontmatter_a_yaml_mapping(repo: Repo) -> Iterator[Finding]:
    """A concept document opens with a ``---`` frontmatter block whose YAML is a mapping.

    The mapping half is the model's: frontmatter that is not a mapping stops the run.
    """
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            yield Finding(doc.path, None, "no frontmatter mapping")


@check("knowledge-organization.type-is-a-registered-okf-type")
def type_is_a_registered_okf_type(repo: Repo) -> Iterator[Finding]:
    """A concept document's ``type`` is a registered OKF type or a local one."""
    registry = _registry(repo)
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            continue
        doctype = doc.frontmatter.get("type")
        if doctype is None:
            yield Finding(doc.path, None, "missing 'type'")
        elif not isinstance(doctype, str):
            yield Finding(doc.path, None, f"type {doctype!r} is not one name")
        elif doctype not in registry:
            yield Finding(
                doc.path,
                None,
                f"type '{doctype}' is not a registered OKF type; declare a local"
                f" one as a row of {sources.OKF_TYPE_REGISTRY.path}",
            )


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
            resource.startswith("/") or md.URI_PATTERN.match(resource)
        ):
            yield Finding(
                doc.path, None, f"resource {resource!r} is not a '/' path or a URI"
            )


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
        if _in_workstream(doc.path):
            continue
        front = doc.frontmatter
        if front and front.get("type") == doctype and not doc.path.startswith(home):
            yield Finding(doc.path, None, f"'{doctype}' lives under {home}")


@check("knowledge-organization.standard-lives-under-standards")
def standard_lives_under_standards(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Standard`` lives under ``standards/`` or under ``workstreams/``."""
    yield from _lives_under(repo, "Standard")


@check("knowledge-organization.loop-lives-under-loops")
def loop_lives_under_loops(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Loop`` lives under ``loops/`` or under ``workstreams/``."""
    yield from _lives_under(repo, "Loop")


@check("knowledge-organization.guide-lives-under-guides")
def guide_lives_under_guides(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Guide`` lives under ``guides/`` or under ``workstreams/``."""
    yield from _lives_under(repo, "Guide")


@check("knowledge-organization.registry-lives-under-registries")
def registry_lives_under_registries(repo: Repo) -> Iterator[Finding]:
    """A concept document typed ``Registry`` lives under ``registries/`` or under ``workstreams/``."""
    yield from _lives_under(repo, "Registry")


@check("knowledge-organization.readmemd-is-typed-readme")
def readmemd_is_typed_readme(repo: Repo) -> Iterator[Finding]:
    """A concept document is named ``README.md`` exactly where it has ``type: README``."""
    for doc in _concept_documents(repo):
        if doc.frontmatter is None:
            continue
        named = PurePosixPath(doc.path).name == README
        typed = doc.frontmatter.get("type") == README_TYPE
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
    """An ``index.md`` has a line of prose between its H1 and its first listed entry.

    An ``index.md`` with no H1 above its first entry has no such line.
    """
    for doc in _indexes(repo):
        h1 = False
        prose = False
        for _, text in doc.content:
            stripped = text.strip()
            if BULLET.match(text):
                break
            if stripped.startswith("# "):
                h1 = True
                prose = False
            elif h1 and stripped and not stripped.startswith(("#", ORDERING)):
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
    """The bullets of the listing: every bullet outside fences."""
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
    """The index of each directory directly under ``directory``, as the model classifies it."""
    prefix = directory + "/" if directory else ""
    return {
        doc.path
        for doc in _indexes(repo)
        if doc.path.startswith(prefix) and doc.path.count("/") == prefix.count("/") + 1
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
        loose = _in_workstream(doc.path)
        for entry in _entries(doc):
            if loose and not entry.target.endswith(".md"):
                continue
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
            if isinstance(description, str) and not entry.rest.endswith(
                f" — {description}"
            ):
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
        if _declares_order(doc):
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


def _declares_order(doc: MarkdownFile) -> bool:
    """True where an ``Ordering:`` line sits above the file's first bullet of any kind."""
    for _, text in doc.content:
        if BULLET.match(text):
            return False
        if text.strip().startswith(ORDERING):
            return True
    return False


@check("knowledge-organization.okf-version-declared")
def okf_version_declared(repo: Repo) -> Iterator[Finding]:
    """The ``index.md`` at the repository root declares ``okf_version``.

    A repo with no root ``index.md`` declares nothing, so it is a finding too.
    """
    doc = repo.markdown.get(ROOT_INDEX)
    if doc is None:
        yield Finding(ROOT_INDEX, None, f"no root index.md to declare {OKF_VERSION}")
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


# --- local-okf-types.md ------------------------------------------------------


@check("knowledge-organization.okf-type-name-to-description")
def okf_type_name_to_description(repo: Repo) -> Iterator[Finding]:
    """Each local row names an OKF type in backticks and describes it in a non-empty cell."""
    path = sources.OKF_TYPE_REGISTRY.path
    try:
        _local_table(repo)
    except KeyError:
        yield Finding(path, None, f"no `## OKF types` table in {path}")
        return
    for row in _local_rows(repo):
        if row.name is None:
            yield Finding(path, row.line, f"{row.cells[0]!r} is not an OKF type name")
        elif len(row.cells) < 2 or not row.cells[1]:
            yield Finding(
                path, row.line, f"local OKF type '{row.name}' has no description"
            )


@check("knowledge-organization.rows-in-alphabetical-order")
def rows_in_alphabetical_order(repo: Repo) -> Iterator[Finding]:
    """The rows of the local OKF types table are in case-insensitive alphabetical order."""
    names = _local_names(repo)
    lowered = [name.lower() for _, name in names]
    if lowered != sorted(lowered):
        yield Finding(
            sources.OKF_TYPE_REGISTRY.path,
            names[0][0],
            "the local OKF types are not in alphabetical order",
        )


@check("knowledge-organization.add-never-shadow")
def add_never_shadow(repo: Repo) -> Iterator[Finding]:
    """No local row names, ignoring case, a registered OKF type or an earlier row's."""
    upstream = {name.lower() for name in sources.REGISTERED_OKF_TYPES}
    seen = set(upstream)
    for line, name in _local_names(repo):
        lowered = name.lower()
        if lowered in seen:
            what = "a registered OKF type" if lowered in upstream else "an earlier row"
            yield Finding(
                sources.OKF_TYPE_REGISTRY.path,
                line,
                f"local OKF type '{name}' shadows {what}",
            )
        seen.add(lowered)


# --- workstream-files.md ---------------------------------------


def _workstreams(repo: Repo) -> list[str]:
    """Each directory directly under ``workstreams/``."""
    prefix = WORKSTREAMS + "/"
    return sorted(
        {
            prefix + path.removeprefix(prefix).split("/", 1)[0]
            for path in repo.files
            if path.startswith(prefix) and path.removeprefix(prefix).count("/") >= 1
        }
    )


@check("knowledge-organization.workstreams-holds-only-workstreams")
def workstreams_holds_only_workstreams(repo: Repo) -> Iterator[Finding]:
    """``workstreams/`` directly has ``index.md``, directories, and no other file."""
    prefix = WORKSTREAMS + "/"
    for path in repo.files:
        name = path.removeprefix(prefix)
        if path.startswith(prefix) and "/" not in name and name != INDEX:
            yield Finding(
                path, None, "a file directly under workstreams/ other than index.md"
            )


@check("knowledge-organization.one-directory-under-workstreams")
def one_directory_under_workstreams(repo: Repo) -> Iterator[Finding]:
    """Each workstream has an ``index.md`` and a ``WORKSTREAM.md``, and kebab-case names."""
    for directory in _workstreams(repo):
        for name in (INDEX, HEAD_FILE):
            path = f"{directory}/{name}"
            if path not in repo.contents:
                yield Finding(path, None, f"the workstream has no {name}")
        for path in repo.files:
            if not path.startswith(directory + "/"):
                continue
            name = PurePosixPath(path).name
            if name in FIXED_NAMES or not name.endswith(".md"):
                continue
            stem, dot, extension = name.rpartition(".")
            if not dot:
                stem, extension = name, ""
            if not (md.KEBAB_CASE.match(stem) and EXTENSION.match(extension)):
                yield Finding(path, None, "the file name is not lowercase kebab-case")


@check("knowledge-organization.the-worklist-in-the-head-file-only")
def the_worklist_in_the_head_file_only(repo: Repo) -> Iterator[Finding]:
    """No file under ``workstreams/`` but a ``WORKSTREAM.md`` has a worklist section."""
    for path, doc in sorted(repo.markdown.items()):
        if not _in_workstream(path) or PurePosixPath(path).name == HEAD_FILE:
            continue
        for heading in doc.headings:
            if heading.level == 2 and heading.text in PLANNED_AND_COMPLETED:
                yield Finding(
                    path, heading.line, f"a '## {heading.text}' outside a WORKSTREAM.md"
                )


@check("knowledge-organization.every-file-reached-from-its-head-file")
def every_file_reached_from_its_head_file(repo: Repo) -> Iterator[Finding]:
    """Every ``.md`` file of a workstream but an index or a head file is reached from its head."""
    for directory in _workstreams(repo):
        members = {
            path
            for path in repo.markdown
            if path.startswith(directory + "/") and PurePosixPath(path).name != INDEX
        }
        graph = {path: _set_links(repo, path, members) for path in members}
        for path in sorted(members):
            if PurePosixPath(path).name == HEAD_FILE:
                continue
            head = _head_of(repo, directory, path)
            if head is not None and path not in _reached(graph, head):
                yield Finding(path, None, f"not reached by links from {head}")


def _set_links(repo: Repo, path: str, members: set[str]) -> set[str]:
    """The members of the set that one member's links point at."""
    doc = repo.markdown[path]
    targets: set[str] = set()
    for ref in _references(doc):
        if ref.bare:
            continue
        resolved = _resolve(repo, ref)
        if resolved.kind == "repo" and resolved.path in members:
            targets.add(resolved.path)
    return targets


def _head_of(repo: Repo, directory: str, path: str) -> str | None:
    """The ``WORKSTREAM.md`` in ``path``'s directory or the nearest above; None if none."""
    here = posixpath.dirname(path)
    while _inside(here, directory):
        candidate = f"{here}/{HEAD_FILE}"
        if candidate in repo.markdown:
            return candidate
        here = posixpath.dirname(here)
    return None


def _reached(graph: dict[str, set[str]], root: str) -> set[str]:
    """Every member a chain of links leads to from ``root``, ``root`` included."""
    seen = {root}
    frontier = [root]
    while frontier:
        for target in graph.get(frontier.pop(), set()):
            if target not in seen:
                seen.add(target)
                frontier.append(target)
    return seen
