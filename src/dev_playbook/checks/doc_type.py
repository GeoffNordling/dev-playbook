"""The doc-type family: the rules of ``standards/doc-type/``.

Twenty-one rules are decided by functions over the model. One holds each
``doc-types/<name>/`` directory to a row of the registry rulings table. Three
hold a file typed ``Guide`` to its steps and its lack of trailers. One holds
the acts of a file typed ``Loop`` to a runbook link. Thirteen hold a runbook, a
skill bundle or an agent definition under ``.claude/`` or
``dotfiles/dot-claude/``, to its front matter, its body, and its bundle files.
Three hold a file typed ``Standard`` to its population and its rule shape.
The five other rules over a Loop are decided by ``loop-lint``.
"""

import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from dev_playbook import md, sources
from dev_playbook.check_registry import Finding, check, tool_check
from dev_playbook.model import TRAILER_PATTERN, MarkdownFile, Repo

for _loop_rule in (
    "doc-type.one-paragraph-then-one-graph",
    "doc-type.acts-checks-and-yields-in-that-order",
    "doc-type.nodes-and-entries-agree",
    "doc-type.edges-lead-to-steps",
    "doc-type.every-entry-states-its-condition",
):
    tool_check(_loop_rule, hook="loop-lint", module=__name__)

DOC_TYPES = "doc-types"
STANDARDS = "standards"
GUIDE_TYPE = "Guide"
LOOP_TYPE = "Loop"
STANDARD_TYPE = "Standard"
WHY = "> **Why.**"
# The blocks a rule may hold after its first paragraph.
RULE_BLOCKS = frozenset({"paragraph", "list", "fence", "quote", "table"})

ORDERED_ITEM = re.compile(r"^(\d+)[.)](?:\s|$)")
NESTED_ORDERED_ITEM = re.compile(r"^\s+\d+[.)](?:\s|$)")
ANY_ORDERED_ITEM = re.compile(r"^\s*\d+[.)]\s+(.*)$")
LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])(?:\s|$)")
HEADING = re.compile(r"^ {0,3}(#{1,6})\s")
STEP_NAME = re.compile(r"^\*\*(?:(?!\*\*).)*\.\*\*")
# A sentence ends at . ! or ? before whitespace or the end of the text,
# optionally after closing quotes or brackets.
SENTENCE_END = re.compile(r"""[.!?]["')\]]*(?=\s|$)""")

# The runbook roots: the two harness roots, each with a skills and an agents
# directory.
SKILL = re.compile(r"^(\.claude|dotfiles/dot-claude)/skills/([^/]+)/SKILL\.md$")
AGENT = re.compile(r"^(\.claude|dotfiles/dot-claude)/agents/([^/]+)\.md$")
RUNBOOK = re.compile(
    r"^(?:\.claude|dotfiles/dot-claude)/(?:skills/[^/]+/SKILL\.md|agents/[^/]+\.md)$"
)
SKILL_REQUIRED = ("name", "description", "disable-model-invocation", "model", "effort")
SKILL_OPTIONAL = ("allowed-tools", "disallowed-tools", "arguments")
AGENT_REQUIRED = ("name", "description", "model", "effort")
AGENT_OPTIONAL = ("tools",)
MODELS = ("haiku", "sonnet", "opus", "fable", "inherit")
EFFORTS = ("low", "medium", "high", "xhigh")
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TOOL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
DESCRIPTION_MAX = 1024
TRIGGER_PREFIX = "Use when"
BODY_MAX_LINES = 500
PLACEHOLDERS = ("$ARGUMENTS", "$0")
BUNDLE_DIRECTORIES = ("references", "scripts")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*<?([^\s>]+)")
EXTERNAL = ("http://", "https://", "mailto:")
LOOP_ENTRY = re.compile(r"^[-*]\s+`[^`]+`\s+—\s")


@dataclass(frozen=True)
class Line:
    """One body line: its number, its text, and whether a fence holds it."""

    number: int
    text: str
    fenced: bool


@dataclass(frozen=True)
class Block:
    """A run of body lines between blank lines; a fenced block is one run."""

    kind: str
    lines: tuple[Line, ...]

    @property
    def first(self) -> Line:
        """The block's first line."""
        return self.lines[0]


@dataclass(frozen=True)
class Runbook:
    """One skill's ``SKILL.md`` or one agent's file, with its kind and home."""

    path: str
    kind: str
    home: str
    root: str
    front: dict[str, Any] | None

    @property
    def bundle(self) -> str:
        """The skill's bundle directory; an agent's is its file's directory."""
        return posixpath.dirname(self.path)


# --- doc-type.md --------------------------------------------------------------


@check("doc-type.registered")
def registered(repo: Repo) -> Iterator[Finding]:
    """Each ``doc-types/<name>/`` is linked from a Ruling cell of the registry rulings."""
    table = sources.REGISTRY_RULINGS
    ruled: set[str] = set()
    if table.path in repo.markdown:
        for cell in _column(repo.markdown[table.path].section(table.heading), "Ruling"):
            for _, target in md.markdown_links(cell):
                parts = _resolve(table.path, target, repo.name, "").split("/")
                if len(parts) > 2 and parts[0] == DOC_TYPES:
                    ruled.add(parts[1])
    directories = {
        parts[1]
        for path in repo.files
        if len(parts := path.split("/")) > 2 and parts[0] == DOC_TYPES
    }
    for name in sorted(directories - ruled):
        yield Finding(
            f"{DOC_TYPES}/{name}",
            None,
            f"no Ruling cell of `{table.path}#{table.heading}` links a file in it",
        )


# --- guide-conventions.md -----------------------------------------------------


@check("doc-type.a-sequence-is-one-list")
def a_sequence_is_one_list(repo: Repo) -> Iterator[Finding]:
    """Each ordered list of a Guide starts at 1, nests none, and fills its section.

    Between the heading above the list and the list there is at most one
    paragraph of one sentence, and after the list nothing until a heading of
    the same level or higher.
    """
    for path, doc in _typed(repo, GUIDE_TYPE):
        lines = _body(doc)
        for start, end in _top_level_lists(lines):
            yield from _one_list(path, lines, start, end)


@check("doc-type.a-step-opens-with-its-name")
def a_step_opens_with_its_name(repo: Repo) -> Iterator[Finding]:
    """Each item of an ordered list in a Guide opens with a bold run ending in a period."""
    for path, doc in _typed(repo, GUIDE_TYPE):
        for number, text in doc.content:
            item = ANY_ORDERED_ITEM.match(text)
            if item and not STEP_NAME.match(item.group(1)):
                yield Finding(
                    path, number, "a step opens with its bold name, as `**Name.**`"
                )


@check("doc-type.no-trailer")
def no_trailer(repo: Repo) -> Iterator[Finding]:
    """No line of a Guide is a rule trailer."""
    for path, doc in _typed(repo, GUIDE_TYPE):
        for line in _body(doc):
            if TRAILER_PATTERN.match(line.text):
                yield Finding(path, line.number, "a Guide holds no rule trailer")


# --- loop-conventions.md ------------------------------------------------------


@check("doc-type.an-act-links-a-runbook")
def an_act_links_a_runbook(repo: Repo) -> Iterator[Finding]:
    """An act's entry in a Loop has a link to a skill's ``SKILL.md`` or an agent.

    An entry with no link at all is the condition rule's finding.
    """
    for path, doc in _typed(repo, LOOP_TYPE):
        if not any(h.slug == "acts" for h in doc.headings):
            continue
        section = doc.section("acts")
        starts = [n for n, text in section if LOOP_ENTRY.match(text)]
        ends = starts[1:] + [section[-1][0] + 1 if section else 0]
        for start, end in zip(starts, ends, strict=True):
            targets = [
                _resolve(path, link.target, repo.name, "")
                for link in doc.links
                if start <= link.line < end
            ]
            if targets and not any(RUNBOOK.match(t) for t in targets):
                yield Finding(path, start, "an act links a runbook")


# --- runbook-conventions.md ---------------------------------------------------


@check("doc-type.front-matter-holds-its-kinds-vocabulary")
def front_matter_holds_its_kinds_vocabulary(repo: Repo) -> Iterator[Finding]:
    """A runbook's front matter has its kind's required keys and no key outside its vocabulary."""
    for runbook in _runbooks(repo):
        if runbook.front is None:
            yield Finding(runbook.path, 1, "no YAML front matter between `---` lines")
            continue
        required, optional = (
            (SKILL_REQUIRED, SKILL_OPTIONAL)
            if runbook.kind == "skill"
            else (AGENT_REQUIRED, AGENT_OPTIONAL)
        )
        for key in required:
            if key not in runbook.front:
                yield Finding(runbook.path, None, f"missing `{key}`")
        for key in sorted(runbook.front, key=str):
            if key not in required + optional:
                yield Finding(
                    runbook.path,
                    None,
                    f"`{key}` is not in a {runbook.kind}'s vocabulary",
                )


@check("doc-type.name-matches-its-home")
def name_matches_its_home(repo: Repo) -> Iterator[Finding]:
    """A runbook's ``name`` equals its bundle directory or its file stem."""
    for runbook in _runbooks(repo):
        name = _field(runbook, "name")
        if name is not None and name != runbook.home:
            yield Finding(
                runbook.path, None, f"name {name!r} is not its home {runbook.home!r}"
            )


@check("doc-type.kebab-case-name")
def kebab_case_name(repo: Repo) -> Iterator[Finding]:
    """A runbook's ``name`` is kebab-case."""
    for runbook in _runbooks(repo):
        name = _field(runbook, "name")
        if name is not None and not (isinstance(name, str) and KEBAB.match(name)):
            yield Finding(runbook.path, None, f"name {name!r} is not kebab-case")


@check("doc-type.description-two-sentences-or-one")
def description_two_sentences_or_one(repo: Repo) -> Iterator[Finding]:
    """A runbook's ``description`` is a string of at most 1024 characters of the right shape.

    A skill with ``disable-model-invocation: true`` has one sentence; any
    other runbook has two, the second opening ``Use when``.
    """
    for runbook in _runbooks(repo):
        description = _field(runbook, "description")
        if description is None:
            continue
        if not isinstance(description, str):
            yield Finding(runbook.path, None, "description is not a string")
            continue
        if len(description) > DESCRIPTION_MAX:
            yield Finding(
                runbook.path,
                None,
                f"description is {len(description)} characters, over {DESCRIPTION_MAX}",
            )
        user_invoked = _field(runbook, "disable-model-invocation") is True
        sentences = _sentences(description)
        expected = 1 if user_invoked else 2
        if len(sentences) != expected:
            yield Finding(
                runbook.path,
                None,
                f"description is {len(sentences)} sentence(s), not {expected}",
            )
        elif not user_invoked and not sentences[1].startswith(TRIGGER_PREFIX):
            yield Finding(
                runbook.path,
                None,
                f"the description's second sentence opens `{TRIGGER_PREFIX}`",
            )


@check("doc-type.model-and-effort-from-closed-sets")
def model_and_effort_from_closed_sets(repo: Repo) -> Iterator[Finding]:
    """A runbook's ``model`` and ``effort`` are each one of their closed set."""
    for runbook in _runbooks(repo):
        for key, allowed in (("model", MODELS), ("effort", EFFORTS)):
            value = _field(runbook, key)
            if value is not None and value not in allowed:
                yield Finding(
                    runbook.path, None, f"{key} {value!r} is not one of {allowed}"
                )


@check("doc-type.body-opens-with-an-h1")
def body_opens_with_an_h1(repo: Repo) -> Iterator[Finding]:
    """The first non-blank line of a runbook's body is an H1."""
    for runbook in _runbooks(repo):
        first = next(
            (line for line in _body(repo.markdown[runbook.path]) if line.text.strip()),
            None,
        )
        if first is None:
            yield Finding(runbook.path, None, "the body is empty")
        elif not first.text.startswith("# "):
            yield Finding(runbook.path, first.number, "the body opens with an H1")


@check("doc-type.every-bundle-file-reached-from-skillmd")
def every_bundle_file_reached_from_skillmd(repo: Repo) -> Iterator[Finding]:
    """Every file in a skill's ``references/`` or ``scripts/`` is a link target of its ``SKILL.md``."""
    for runbook in _skills(repo):
        doc = repo.markdown[runbook.path]
        linked = {
            _resolve(runbook.path, target, repo.name, runbook.root)
            for target in _link_targets(doc)
        }
        for path in repo.files:
            parts = path.removeprefix(runbook.bundle + "/").split("/")
            if (
                path.startswith(runbook.bundle + "/")
                and len(parts) > 1
                and parts[0] in BUNDLE_DIRECTORIES
                and path not in linked
            ):
                yield Finding(path, None, f"no link in {runbook.path} targets it")


@check("doc-type.boolean-disable-model-invocation")
def boolean_disable_model_invocation(repo: Repo) -> Iterator[Finding]:
    """A skill's ``disable-model-invocation`` is boolean."""
    for runbook in _skills(repo):
        value = _field(runbook, "disable-model-invocation")
        if value is not None and not isinstance(value, bool):
            yield Finding(
                runbook.path, None, f"disable-model-invocation {value!r} is not boolean"
            )


@check("doc-type.arguments-bare-kebab-case-names")
def arguments_bare_kebab_case_names(repo: Repo) -> Iterator[Finding]:
    """A skill's ``arguments`` is a non-empty list of kebab-case names."""
    for runbook in _skills(repo):
        value = _field(runbook, "arguments")
        if value is None:
            continue
        if not isinstance(value, list) or not value:
            yield Finding(runbook.path, None, "arguments is not a non-empty list")
            continue
        for item in value:
            if not (isinstance(item, str) and KEBAB.match(item)):
                yield Finding(
                    runbook.path, None, f"argument {item!r} is not a kebab-case name"
                )


@check("doc-type.no-argument-placeholder")
def no_argument_placeholder(repo: Repo) -> Iterator[Finding]:
    """A skill's body, fences included, holds neither ``$ARGUMENTS`` nor ``$0``."""
    for runbook in _skills(repo):
        for line in _body(repo.markdown[runbook.path]):
            for placeholder in PLACEHOLDERS:
                if placeholder in line.text:
                    yield Finding(
                        runbook.path, line.number, f"the body holds `{placeholder}`"
                    )


@check("doc-type.references-one-level-deep")
def references_one_level_deep(repo: Repo) -> Iterator[Finding]:
    """No ``.md`` file in a skill's ``references/`` links another ``.md`` file there.

    Inline and reference-style links are read, root-absolute and ``~/`` ones
    included, and ``references/`` is read at any depth.
    """
    for runbook in _skills(repo):
        references = f"{runbook.bundle}/references/"
        for path, doc in sorted(repo.markdown.items()):
            if not path.startswith(references):
                continue
            for target in _link_targets(doc):
                resolved = _resolve(path, target, repo.name, runbook.root)
                if (
                    resolved != path
                    and resolved.startswith(references)
                    and resolved.endswith(".md")
                ):
                    yield Finding(
                        path, None, f"links {target}, another file in references/"
                    )


@check("doc-type.skillmd-at-most-500-lines")
def skillmd_at_most_500_lines(repo: Repo) -> Iterator[Finding]:
    """A skill's ``SKILL.md`` body, after the front matter, is at most 500 lines."""
    for runbook in _skills(repo):
        count = len(_body(repo.markdown[runbook.path]))
        if count > BODY_MAX_LINES:
            yield Finding(
                runbook.path, None, f"the body is {count} lines, over {BODY_MAX_LINES}"
            )


@check("doc-type.tools-comma-separated-tool-names")
def tools_comma_separated_tool_names(repo: Repo) -> Iterator[Finding]:
    """An agent's ``tools`` is a non-empty comma-separated string of tool names."""
    for runbook in _runbooks(repo):
        if runbook.kind != "agent":
            continue
        value = _field(runbook, "tools")
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            yield Finding(runbook.path, None, "tools is not a string of tool names")
            continue
        for part in value.split(","):
            if not TOOL_NAME.match(part.strip()):
                yield Finding(
                    runbook.path, None, f"tools: {part.strip()!r} is not a tool name"
                )


# --- standard-conventions.md --------------------------------------------------


@check("doc-type.the-frontmatter-names-the-population")
def the_frontmatter_names_the_population(repo: Repo) -> Iterator[Finding]:
    """A Standard's frontmatter ``population`` is a string that is not empty."""
    for path, doc in _typed(repo, STANDARD_TYPE):
        population = (doc.frontmatter or {}).get("population")
        if not isinstance(population, str) or not population.strip():
            yield Finding(path, None, "no `population` string in the frontmatter")


@check("doc-type.a-rule-heading-predicate-trailer")
def a_rule_heading_predicate_trailer(repo: Repo) -> Iterator[Finding]:
    """Each rule of a Standard is an H2 or H3, a paragraph, blocks, a trailer, a Why.

    The trailer's name is the file's first directory under ``standards/`` and
    its slug the heading's. After the paragraph come any number of
    paragraphs, lists, fenced blocks, blockquotes, or tables; after the trailer
    nothing, or one blockquote opening ``> **Why.**``. An H3 sits only under
    an H2 with no trailer.
    """
    for path, doc in _typed(repo, STANDARD_TYPE):
        parts = path.split("/")
        name = parts[1] if len(parts) > 2 and parts[0] == STANDARDS else None
        lines = _body(doc)
        index = {line.number: i for i, line in enumerate(lines)}
        rules = {t.heading.line for t in doc.trailers if t.heading is not None}
        for trailer in doc.trailers:
            heading = trailer.heading
            if heading is None or heading.level not in (2, 3):
                yield Finding(path, trailer.line, "a trailer ends an H2 or H3 section")
                continue
            if trailer.family != name:
                yield Finding(
                    path, trailer.line, f"the trailer's name is {name!r}, the directory"
                )
            if trailer.slug != heading.slug:
                yield Finding(
                    path, trailer.line, f"the trailer's slug is {heading.slug!r}"
                )
            between = _blocks(lines[index[heading.line] + 1 : index[trailer.line]])
            if not between or between[0].kind != "paragraph":
                yield Finding(path, heading.line, "a rule opens with one paragraph")
            elif any(b.kind not in RULE_BLOCKS for b in between[1:]):
                yield Finding(
                    path,
                    heading.line,
                    "after its paragraph a rule holds only paragraphs, lists, "
                    "fenced blocks, blockquotes, and tables",
                )
            after = _blocks(_until_heading(lines, index[trailer.line] + 1))
            if len(after) > 1 or (after and not _is_why(after[0])):
                yield Finding(
                    path,
                    trailer.line,
                    "after the trailer comes nothing or one `> **Why.**` blockquote",
                )
        parent = None
        for heading in doc.headings:
            if heading.level <= 2:
                parent = heading if heading.level == 2 else None
            elif heading.level == 3 and (parent is None or parent.line in rules):
                yield Finding(
                    path, heading.line, "an H3 sits only under an H2 with no trailer"
                )


@check("doc-type.the-files-why-ends-the-opening-prose")
def the_files_why_ends_the_opening_prose(repo: Repo) -> Iterator[Finding]:
    """Between a Standard's H1 and first H2, one ``> **Why.**`` blockquote at most, and last."""
    for path, doc in _typed(repo, STANDARD_TYPE):
        h1 = next((h for h in doc.headings if h.level == 1), None)
        if h1 is None:
            continue
        lines = _body(doc)
        start = next(i for i, line in enumerate(lines) if line.number == h1.line)
        blocks = _blocks(_until_heading(lines, start + 1, 2))
        whys = [i for i, block in enumerate(blocks) if _is_why(block)]
        if len(whys) > 1:
            yield Finding(
                path, blocks[whys[1]].first.number, "the opening prose has one Why"
            )
        elif whys and whys[0] != len(blocks) - 1:
            yield Finding(
                path,
                blocks[whys[0]].first.number,
                "the file's Why is the last block before the first H2",
            )


# --- helpers ------------------------------------------------------------------


def _typed(repo: Repo, doctype: str) -> Iterator[tuple[str, MarkdownFile]]:
    """Every markdown file whose frontmatter ``type`` is ``doctype``."""
    for path, doc in sorted(repo.markdown.items()):
        if doc.frontmatter is not None and doc.frontmatter.get("type") == doctype:
            yield path, doc


def _body(doc: MarkdownFile) -> list[Line]:
    """Every line after the frontmatter, each marked fenced or not."""
    all_lines = doc.text.split("\n")
    if doc.text.endswith("\n"):
        all_lines.pop()
    first = 1
    if doc.frontmatter is not None:
        first = doc.text[: doc.text.index("\n---\n", 4) + 1].count("\n") + 2
    outside = {n for n, _ in doc.content}
    return [
        Line(n, text, n not in outside)
        for n, text in enumerate(all_lines, start=1)
        if n >= first
    ]


def _blocks(lines: list[Line]) -> list[Block]:
    """The blocks of ``lines``, split at blank lines outside fences."""
    blocks: list[Block] = []
    run: list[Line] = []
    for line in [*lines, Line(0, "", False)]:
        if line.text.strip() or line.fenced:
            run.append(line)
        elif run:
            blocks.append(Block(_kind(run[0]), tuple(run)))
            run = []
    return blocks


def _kind(line: Line) -> str:
    """What a block is, from its first line."""
    text = line.text.lstrip()
    if line.fenced:
        return "fence"
    if text.startswith(">"):
        return "quote"
    if text.startswith("|"):
        return "table"
    if HEADING.match(line.text):
        return "heading"
    if LIST_ITEM.match(line.text):
        return "list"
    return "paragraph"


def _is_why(block: Block) -> bool:
    """Whether a block is a blockquote opening ``> **Why.**``."""
    return block.kind == "quote" and block.first.text.startswith(WHY)


def _until_heading(lines: list[Line], start: int, level: int = 6) -> list[Line]:
    """The lines from ``start`` up to the next heading of ``level`` or higher."""
    taken: list[Line] = []
    for line in lines[start:]:
        heading = HEADING.match(line.text)
        if heading and not line.fenced and len(heading.group(1)) <= level:
            break
        taken.append(line)
    return taken


def _top_level_lists(lines: list[Line]) -> Iterator[tuple[int, int]]:
    """The ``(start, end)`` indexes of each ordered list at column zero."""
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.fenced or not ORDERED_ITEM.match(line.text):
            i += 1
            continue
        end = i + 1
        last = i
        while end < len(lines):
            text = lines[end].text
            if text.strip() == "":
                end += 1
                continue
            if text[0] in " \t" or (not lines[end].fenced and ORDERED_ITEM.match(text)):
                last = end
                end += 1
                continue
            break
        yield i, last + 1
        i = last + 1


def _one_list(path: str, lines: list[Line], start: int, end: int) -> Iterator[Finding]:
    """The findings of the sequence rule for the list at ``lines[start:end]``."""
    number = lines[start].number
    first = ORDERED_ITEM.match(lines[start].text)
    if first is not None and first.group(1) != "1":
        yield Finding(path, number, "an ordered list starts at `1.`")
    for line in lines[start:end]:
        if not line.fenced and NESTED_ORDERED_ITEM.match(line.text):
            yield Finding(
                path, line.number, "an ordered list has no ordered list in it"
            )
    above = next(
        (
            i
            for i in range(start - 1, -1, -1)
            if not lines[i].fenced and HEADING.match(lines[i].text)
        ),
        None,
    )
    if above is None:
        yield Finding(path, number, "an ordered list sits under a heading")
        return
    before = _blocks(lines[above + 1 : start])
    if len(before) > 1 or (
        before
        and (before[0].kind != "paragraph" or len(_sentences(_joined(before[0]))) > 1)
    ):
        yield Finding(
            path,
            number,
            "at most one paragraph of one sentence sits between the heading and "
            "the list",
        )
    heading = HEADING.match(lines[above].text)
    level = len(heading.group(1)) if heading else 1
    after = [line for line in _until_heading(lines, end, level) if line.text.strip()]
    if after:
        yield Finding(
            path,
            after[0].number,
            "nothing follows the list until a heading at its heading's level or higher",
        )


def _joined(block: Block) -> str:
    """A block's text on one line."""
    return " ".join(line.text.strip() for line in block.lines)


def _sentences(text: str) -> list[str]:
    """The terminated sentences of ``text``; a fragment with no end is none."""
    parts = []
    start = 0
    for match in SENTENCE_END.finditer(text):
        parts.append(text[start : match.end()].strip())
        start = match.end()
    return parts


def _column(section: tuple[tuple[int, str], ...], name: str) -> list[str]:
    """The cells of the column headed ``name`` in the first table of ``section``."""
    rows = [
        [cell.strip() for cell in text.strip().strip("|").split("|")]
        for _, text in section
        if text.lstrip().startswith("|")
    ]
    if not rows or name not in rows[0]:
        return []
    column = rows[0].index(name)
    return [row[column] for row in rows[2:] if len(row) > column]


def _resolve(source: str, target: str, repo_name: str, harness_root: str) -> str:
    """A link target as a repo path, anchor dropped; empty when it leaves the repo.

    A target is root-absolute, relative to ``source``, under
    ``~/workspace/<repo_name>/``, or, where ``harness_root`` is given, under
    ``~/.claude/``, which is that root.
    """
    target = target.split("#", 1)[0].strip()
    workspace = f"~/workspace/{repo_name}/"
    if not target or target.startswith(EXTERNAL):
        return ""
    if target.startswith(workspace):
        joined = target[len(workspace) :]
    elif harness_root and target.startswith("~/.claude/"):
        joined = harness_root + "/" + target[len("~/.claude/") :]
    elif target.startswith("~"):
        return ""
    elif target.startswith("/"):
        joined = target.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(source), target)
    resolved = posixpath.normpath(joined)
    return "" if resolved.startswith("..") else resolved


def _link_targets(doc: MarkdownFile) -> list[str]:
    """The targets of every inline and reference-style link outside fences."""
    targets = [link.target for link in doc.links]
    targets.extend(
        m.group(1) for _, text in doc.content if (m := REFERENCE_DEFINITION.match(text))
    )
    return targets


def _runbooks(repo: Repo) -> Iterator[Runbook]:
    """Every skill's ``SKILL.md`` and every agent's file under a runbook root."""
    for path in sorted(repo.markdown):
        skill = SKILL.match(path)
        agent = AGENT.match(path)
        match, kind = (skill, "skill") if skill else (agent, "agent")
        if match is None:
            continue
        yield Runbook(
            path,
            kind,
            match.group(2),
            match.group(1),
            repo.markdown[path].frontmatter,
        )


def _skills(repo: Repo) -> Iterator[Runbook]:
    """Every skill's ``SKILL.md``."""
    return (runbook for runbook in _runbooks(repo) if runbook.kind == "skill")


def _field(runbook: Runbook, key: str) -> Any:
    """One front matter value, or None where there is none."""
    return None if runbook.front is None else runbook.front.get(key)
