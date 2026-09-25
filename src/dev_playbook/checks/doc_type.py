"""The doc-type family: the rules of ``standards/doc-type/``.

Thirty-three rules are decided by functions over the model. Four hold each
``doc-types/<name>/`` directory to its five files and to a row of the Doc-Type
Registry that names registered instances no other row names. Three
hold a file typed ``Guide`` to its steps and its lack of trailers. One holds
the acts of a file typed ``Loop`` to a runbook link. Four hold a file typed
``Workstream`` to its menu of headings, its worklist items, its stint entries,
and the links that reach it from its parent. Thirteen hold a runbook, a
skill bundle or an agent definition under ``.claude/`` or
``dotfiles/dot-claude/``, to its front matter, its body, and its bundle files.
Three hold a file typed ``Standard`` to its population and its rule shape.
Five more hold a file typed ``Loop`` to its encoding: one paragraph, one
Mermaid graph, and the Acts, Verifications and Yields sections that agree
with it.
"""

import posixpath
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from dev_playbook import md, sources
from dev_playbook.check_registry import Finding, check
from dev_playbook.model import TRAILER_PATTERN, MarkdownFile, Repo

DOC_TYPES = "doc-types"
DOC_TYPE_FILES = (
    "index.md",
    "definition.md",
    "contract-shape.md",
    "encoding.md",
    "residual-ledger.md",
)
STANDARDS = "standards"
WORKSTREAMS = "workstreams/"
HEAD_FILE = "WORKSTREAM.md"
GUIDE_TYPE = "Guide"
LOOP_TYPE = "Loop"
WORKSTREAM_TYPE = "Workstream"
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
TOOL_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
DESCRIPTION_MAX = 1024
TRIGGER_PREFIX = "Use when"
BODY_MAX_LINES = 500
PLACEHOLDERS = ("$ARGUMENTS", "$0")
BUNDLE_DIRECTORIES = ("references", "scripts")
REFERENCE_DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*<?([^\s>]+)")
LOOP_ENTRY = re.compile(r"^[-*]\s+`[^`]+`\s+—\s")
BULLET = re.compile(r"^[-*]\s")
STINT_OPENING = re.compile(r"^[-*]\s+\*\*(Planned|\d{4}-\d{2}-\d{2})\.\*\*")
VERDICT = re.compile(r"Verdict:\s*(\w*)")
VERDICTS = frozenset({"advance", "accept", "delete"})
TARGETS = re.compile(r"Targets:\s*(`[^`]+`(?:,\s*`[^`]+`)*)\.")

# The five rules that read a Loop's cut in order: each reads the cut the one
# before it made, so a Loop's first disagreement is its only finding of them.
ONE_GRAPH = "doc-type.one-paragraph-then-one-graph"
THREE_VERB_SECTIONS = "doc-type.acts-verifications-and-yields-in-that-order"
NODES_AND_ENTRIES_AGREE = "doc-type.nodes-and-entries-agree"
EDGES_LEAD_TO_STEPS = "doc-type.edges-lead-to-steps"
ENTRIES_STATE_CONDITIONS = "doc-type.every-entry-states-its-condition"
VERBS = ("Acts", "Verifications", "Yields")
VERB_OF = {"Acts": "act", "Verifications": "verification", "Yields": "yield"}
RECEIVER = "receiver"
# What each kind of node may lead to. A receiver is a node under no heading.
STEPS = frozenset({"act", "verification", "yield"})
MAY_LEAD_TO = {
    "act": STEPS,
    "verification": STEPS,
    "yield": STEPS | {RECEIVER},
    RECEIVER: STEPS,
}
CONDITION_OF = {
    "act": ("fires when", "fires every iteration"),
    "verification": ("fires when", "fires every iteration"),
    "yield": ("yields when",),
}
LOOP_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(\S*)\s*$")
LOOP_ENTRY_PARTS = re.compile(r"^[-*]\s+`([^`]+)`\s+—\s+(.*\S)\s*$")
INLINE_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# A Mermaid node: an id and an optional shape from the flowchart set —
# [text], (text), ([text]), [[text]], [(text)], ((text)), >text], {text},
# {{text}}. The label inside is opaque.
MERMAID_NODE = re.compile(
    r"^([A-Za-z_][\w-]*)"
    r"(\(\[.*?\]\)|\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\{\{.*?\}\}"
    r"|\[.*?\]|\(.*?\)|\{.*?\}|>.*?\])?$"
)
# An arrow between two node terms, with an optional |label|.
MERMAID_ARROW = re.compile(r"\s*(?:-->|-\.->|==>|---|-\.-|===)(?:\|[^|]*\|)?\s*")
# Statements that draw nothing the checks read.
MERMAID_DIRECTIVE = re.compile(
    r"^(%%|subgraph\b|end$|direction\b|classDef\b|class\b|style\b|linkStyle\b)"
)
WORKLIST = ("Planned", "Completed")
BOLD_START = re.compile(r"^[-*]\s+\*\*")


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


def _doc_type_directories(repo: Repo) -> set[str]:
    """The name of each ``doc-types/<name>/`` directory that holds a tracked file."""
    return {
        parts[1]
        for path in repo.files
        if len(parts := path.split("/")) > 2 and parts[0] == DOC_TYPES
    }


@check("doc-type.registered")
def registered(repo: Repo) -> Iterator[Finding]:
    """Each ``doc-types/<name>/`` is linked from a Doc-type cell of the Doc-Type Registry."""
    table = sources.DOC_TYPE_REGISTRY
    covered: set[str] = set()
    if table.path in repo.markdown:
        section = repo.markdown[table.path].section(table.heading)
        for cell in _column(section, "Doc-type"):
            for _, target in md.markdown_links(cell):
                parts = _resolve(table.path, target, repo.name, "").split("/")
                if len(parts) > 2 and parts[0] == DOC_TYPES:
                    covered.add(parts[1])
    for name in sorted(_doc_type_directories(repo) - covered):
        yield Finding(
            f"{DOC_TYPES}/{name}",
            None,
            f"no Doc-type cell of `{table.path}` links a file in it",
        )


NONE_CELL = "—"


def _table_cells(repo: Repo, table: sources.Section, column: str) -> list[str]:
    """The cells of ``column`` in ``table``, or none when the file is absent."""
    if table.path not in repo.markdown:
        return []
    return _column(repo.markdown[table.path].section(table.heading), column)


def _doc_type_rows(repo: Repo) -> list[tuple[str, set[str], set[str]]]:
    """Each Doc-Type Registry row: its directory name, OKF types, and harness members."""
    table = sources.DOC_TYPE_REGISTRY
    names = _table_cells(repo, table, "Doc-type")
    okf = _table_cells(repo, table, "OKF type")
    harness = _table_cells(repo, table, "Harness members")
    rows = []
    for name_cell, okf_cell, harness_cell in zip(names, okf, harness, strict=True):
        name = ""
        for _, target in md.markdown_links(name_cell):
            parts = _resolve(table.path, target, repo.name, "").split("/")
            if len(parts) > 2 and parts[0] == DOC_TYPES:
                name = parts[1]
        okf_types = {okf_cell} - {NONE_CELL, ""}
        members = {m.strip() for m in harness_cell.split(";")} - {NONE_CELL, ""}
        rows.append((name, okf_types, members))
    return rows


@check("doc-type.its-instances-are-registered")
def its_instances_are_registered(repo: Repo) -> Iterator[Finding]:
    """Each Doc-Type Registry row names a registered OKF type or registered harness members."""
    okf_types = set(_table_cells(repo, sources.OKF_TYPE_REGISTRY, "OKF type"))
    members = set(_table_cells(repo, sources.HARNESS_FILE_REGISTRY, "Member"))
    for name, row_okf, row_members in _doc_type_rows(repo):
        where = f"{DOC_TYPES}/{name}"
        if not row_okf and not row_members:
            yield Finding(where, None, "its registry row names no instances")
        for okf in sorted(row_okf - okf_types):
            yield Finding(where, None, f"{okf} is not a registered OKF type")
        for member in sorted(row_members - members):
            yield Finding(where, None, f"{member} is not a registered harness member")


@check("doc-type.its-instances-are-its-own")
def its_instances_are_its_own(repo: Repo) -> Iterator[Finding]:
    """No OKF type or harness member is named by two Doc-Type Registry rows."""
    owner: dict[str, str] = {}
    for name, row_okf, row_members in _doc_type_rows(repo):
        for instance in sorted(row_okf | row_members):
            if instance in owner:
                yield Finding(
                    f"{DOC_TYPES}/{name}",
                    None,
                    f"{instance} is also named by {DOC_TYPES}/{owner[instance]}",
                )
            else:
                owner[instance] = name


@check("doc-type.five-files")
def five_files(repo: Repo) -> Iterator[Finding]:
    """Each ``doc-types/<name>/`` holds the five files of a doc-type."""
    for name in sorted(_doc_type_directories(repo)):
        for file in DOC_TYPE_FILES:
            if f"{DOC_TYPES}/{name}/{file}" not in repo.files:
                yield Finding(f"{DOC_TYPES}/{name}", None, f"no {file}")


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


@check("doc-type.one-paragraph-then-one-graph")
def one_paragraph_then_one_graph(repo: Repo) -> Iterator[Finding]:
    """A Loop is one H1, one paragraph, then one readable ``mermaid`` flowchart."""
    yield from _loop_findings(repo, ONE_GRAPH)


@check("doc-type.acts-verifications-and-yields-in-that-order")
def acts_verifications_and_yields_in_that_order(repo: Repo) -> Iterator[Finding]:
    """After a Loop's graph, the three verb H2s in order, each a list of entries."""
    yield from _loop_findings(repo, THREE_VERB_SECTIONS)


@check("doc-type.nodes-and-entries-agree")
def nodes_and_entries_agree(repo: Repo) -> Iterator[Finding]:
    """Every entry of a Loop is a node; every node has an entry or is yielded to."""
    yield from _loop_findings(repo, NODES_AND_ENTRIES_AGREE)


@check("doc-type.edges-lead-to-steps")
def edges_lead_to_steps(repo: Repo) -> Iterator[Finding]:
    """Every edge of a Loop leads to a step, except a yield's, which may reach a receiver."""
    yield from _loop_findings(repo, EDGES_LEAD_TO_STEPS)


@check("doc-type.every-entry-states-its-condition")
def every_entry_states_its_condition(repo: Repo) -> Iterator[Finding]:
    """Every entry of a Loop states its condition and links what its verb needs."""
    yield from _loop_findings(repo, ENTRIES_STATE_CONDITIONS)


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
        if name is not None and not (
            isinstance(name, str) and md.KEBAB_CASE.match(name)
        ):
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
            if not (isinstance(item, str) and md.KEBAB_CASE.match(item)):
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

    The trailer's name is the file's first directory under ``standards/``, or
    a draft Standard's workstream directory, and its slug the heading's. After the paragraph come any number of
    paragraphs, lists, fenced blocks, blockquotes, or tables; after the trailer
    nothing, or one blockquote opening ``> **Why.**``. An H3 sits only under
    an H2 with no trailer.
    """
    for path, doc in _typed(repo, STANDARD_TYPE):
        parts = path.split("/")
        name = parts[1] if len(parts) > 2 and parts[0] == STANDARDS else None
        if path.startswith(WORKSTREAMS):
            name = _workstream_name(repo, path)
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


# --- workstream-conventions.md ------------------------------------------------


@check("doc-type.headings-from-the-registry")
def headings_from_the_registry(repo: Repo) -> Iterator[Finding]:
    """Each H2 of a Workstream is a heading of the menu, and none is used twice."""
    for path, doc in _typed(repo, WORKSTREAM_TYPE):
        seen: set[str] = set()
        for heading in doc.headings:
            if heading.level != 2:
                continue
            if heading.text not in sources.WORKSTREAM_HEADINGS:
                yield Finding(
                    path, heading.line, f"`{heading.text}` is not a menu heading"
                )
            elif heading.text in seen:
                yield Finding(path, heading.line, f"`{heading.text}` is used twice")
            seen.add(heading.text)


@check("doc-type.a-worklist-item-opens-with-its-bold-name")
def a_worklist_item_opens_with_its_bold_name(repo: Repo) -> Iterator[Finding]:
    """Each item directly under Planned or Completed starts with a bold name."""
    for path, doc in _typed(repo, WORKSTREAM_TYPE):
        for heading in doc.headings:
            if heading.level != 2 or heading.text not in WORKLIST:
                continue
            end = next((h.line for h in doc.headings if h.line > heading.line), None)
            for number, text in doc.content:
                if number <= heading.line or (end is not None and number >= end):
                    continue
                if BULLET.match(text) and not BOLD_START.match(text):
                    yield Finding(
                        path, number, "a worklist item does not start with a bold name"
                    )


@check("doc-type.a-stint-entry-in-form")
def a_stint_entry_in_form(repo: Repo) -> Iterator[Finding]:
    """Each Stints item opens planned or dated, links one Loop, and sits in order.

    The planned item is first; the dated ones follow, newest first. A
    ``Verdict:`` is one of the three the user rules. A ``Targets:`` lists
    rule ids of the draft Standards under the head file's directory.
    """
    for path, doc in _typed(repo, WORKSTREAM_TYPE):
        if not any(h.level == 2 and h.slug == "stints" for h in doc.headings):
            continue
        rule_ids = _draft_rule_ids(repo, posixpath.dirname(path))
        section = doc.section("stints")
        starts = [n for n, text in section if BULLET.match(text)]
        ends = starts[1:] + [section[-1][0] + 1 if section else 0]
        dates: list[str] = []
        for index, (start, end) in enumerate(zip(starts, ends, strict=True)):
            text = " ".join(t for n, t in section if start <= n < end)
            opening = STINT_OPENING.match(text)
            if opening is None:
                yield Finding(
                    path,
                    start,
                    "a stint opens with `**Planned.**` or `**YYYY-MM-DD.**`",
                )
                continue
            label = opening.group(1)
            if label == "Planned" and index != 0:
                yield Finding(path, start, "the planned stint is the first item")
            if label != "Planned":
                if dates and label > dates[-1]:
                    yield Finding(path, start, "the dated stints run newest first")
                dates.append(label)
            loops = [
                target
                for link in doc.links
                if start <= link.line < end
                and _type_of(repo, target := _resolve(path, link.target, repo.name, ""))
                == LOOP_TYPE
            ]
            if len(loops) != 1:
                yield Finding(
                    path, start, f"a stint links one file typed Loop, not {len(loops)}"
                )
            verdict = VERDICT.search(text)
            if verdict is not None and verdict.group(1) not in VERDICTS:
                yield Finding(
                    path, start, "a verdict is `advance`, `accept`, or `delete`"
                )
            if "Targets:" not in text:
                continue
            targets = TARGETS.search(text)
            if targets is None:
                yield Finding(
                    path, start, "targets are rule ids in backticks, then a period"
                )
                continue
            for rule_id in re.findall(r"`([^`]+)`", targets.group(1)):
                if rule_id not in rule_ids:
                    yield Finding(
                        path,
                        start,
                        f"`{rule_id}` is no rule of the workstream's draft Standards",
                    )


def _draft_rule_ids(repo: Repo, directory: str) -> set[str]:
    """The rule ids of every file typed ``Standard`` under ``directory``."""
    return {
        trailer.id
        for path, doc in _typed(repo, STANDARD_TYPE)
        if path.startswith(directory + "/")
        for trailer in doc.trailers
    }


@check("doc-type.stints-in-a-leaf-only")
def stints_in_a_leaf_only(repo: Repo) -> Iterator[Finding]:
    """A Workstream with a Stints heading has no child Workstream."""
    heads = [posixpath.dirname(path) for path, _ in _typed(repo, WORKSTREAM_TYPE)]
    for path, doc in _typed(repo, WORKSTREAM_TYPE):
        stints = next(
            (h for h in doc.headings if h.level == 2 and h.slug == "stints"), None
        )
        here = posixpath.dirname(path)
        if stints is not None and any(h.startswith(here + "/") for h in heads):
            yield Finding(path, stints.line, "a workstream with a child has no Stints")


@check("doc-type.every-child-reached-from-its-parent")
def every_child_reached_from_its_parent(repo: Repo) -> Iterator[Finding]:
    """Each child Workstream is reached by links from its parent's head file."""
    heads = {posixpath.dirname(path): path for path, _ in _typed(repo, WORKSTREAM_TYPE)}
    for path in sorted(heads.values()):
        parent = _parent_head(heads, path)
        if parent is None:
            continue
        top = posixpath.dirname(parent)
        prefix = f"{top}/" if top else ""
        members = {p for p in repo.markdown if p.startswith(prefix)}
        graph = {
            member: {
                target
                for link in repo.markdown[member].links
                if (target := _resolve(member, link.target, repo.name, "")) in members
            }
            for member in members
        }
        if path not in _reached(graph, parent):
            yield Finding(path, None, f"not reached by links from {parent}")


# --- helpers ------------------------------------------------------------------


class _Disagreement(Exception):
    """The first place a Loop's graph and prose disagree, under one rule."""

    def __init__(self, rule: str, message: str) -> None:
        """Record the rule the disagreement falls under, and the message."""
        super().__init__(message)
        self.rule = rule


def _loop_findings(repo: Repo, rule: str) -> Iterator[Finding]:
    """Each Loop whose first disagreement falls under ``rule``."""
    for path, doc in _typed(repo, LOOP_TYPE):
        try:
            _check_loop(repo, path, doc)
        except _Disagreement as err:
            if err.rule == rule:
                yield Finding(path, None, str(err))


def _check_loop(repo: Repo, path: str, doc: MarkdownFile) -> None:
    """Every rule over one Loop, in order; raises at the first disagreement."""
    _, body = md.parse_frontmatter(doc.text)
    mermaid, sections = _slice_loop(body)
    entries = _entries_of(sections)
    nodes, edges = _graph_of(mermaid)
    for node in entries:
        if node not in nodes:
            raise _Disagreement(
                NODES_AND_ENTRIES_AGREE,
                f"`{node}` has an entry but is not a node of the graph",
            )
    kind = {node: entries[node][0] if node in entries else RECEIVER for node in nodes}
    yielded_to = {t for s, t in edges if kind[s] == "yield"}
    for node in sorted(nodes):
        if kind[node] == RECEIVER and node not in yielded_to:
            raise _Disagreement(
                NODES_AND_ENTRIES_AGREE,
                f"`{node}` has no entry and no yield leads to it",
            )
    for s, t in edges:
        if kind[t] not in MAY_LEAD_TO[kind[s]]:
            raise _Disagreement(
                EDGES_LEAD_TO_STEPS,
                f"edge `{s}` → `{t}` is {kind[s]} → {kind[t]}; the shape does not allow it",
            )
    for node, (verb, rest) in entries.items():
        _check_entry(repo, path, node, verb, rest)


def _slice_loop(body: str) -> tuple[list[str], list[tuple[str, list[str]]]]:
    """Cut a Loop's body into (mermaid lines, H2 sections after the graph).

    Before the fence: the H1 and exactly one paragraph. The fence: one
    ``mermaid`` block. After it: H2s only, each with the lines beneath it.
    """
    before: list[str] = []
    mermaid: list[str] | None = None
    sections: list[tuple[str, list[str]]] = []
    fence: str | None = None
    in_mermaid = seen_h1 = False
    for line in body.split("\n"):
        if m := FENCE.match(line):
            marker, info = m.group(1)[0], m.group(2)
            if fence is None:
                fence = marker
                if info == "mermaid":
                    if mermaid is not None:
                        raise _Disagreement(
                            ONE_GRAPH, "two mermaid blocks; the encoding is one"
                        )
                    if sections:
                        raise _Disagreement(
                            ONE_GRAPH, "the mermaid block sits after a verb section"
                        )
                    mermaid, in_mermaid = [], True
                continue
            if marker == fence:
                fence, in_mermaid = None, False
                continue
        if in_mermaid and mermaid is not None:
            mermaid.append(line)
            continue
        if fence is None and (m := LOOP_HEADING.match(line)):
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                if seen_h1:
                    raise _Disagreement(ONE_GRAPH, "two H1s")
                seen_h1 = True
                continue
            if mermaid is None:
                raise _Disagreement(
                    ONE_GRAPH,
                    f"heading {text!r} before the graph; only the paragraph sits there",
                )
            if level != 2:
                raise _Disagreement(
                    THREE_VERB_SECTIONS,
                    f"heading {text!r} is H{level}; the verb sections are H2s",
                )
            sections.append((text, []))
            continue
        if mermaid is None:
            if seen_h1:
                before.append(line)
        elif sections:
            sections[-1][1].append(line)
        elif line.strip():
            raise _Disagreement(
                THREE_VERB_SECTIONS,
                f"text between the graph and the first verb heading: {line.strip()!r}",
            )
    if mermaid is None:
        raise _Disagreement(ONE_GRAPH, "no mermaid block")
    paragraphs = [p for p in "\n".join(before).split("\n\n") if p.strip()]
    if len(paragraphs) != 1:
        raise _Disagreement(
            ONE_GRAPH,
            f"{len(paragraphs)} paragraphs before the graph; the encoding is one",
        )
    return mermaid, sections


def _entries_of(sections: list[tuple[str, list[str]]]) -> dict[str, tuple[str, str]]:
    """Map node id → (verb, entry text), from the three verb sections in order."""
    names = [text for text, _ in sections]
    if names != list(VERBS):
        raise _Disagreement(
            THREE_VERB_SECTIONS,
            f"verb sections are {names}; the encoding is {list(VERBS)} in that order",
        )
    entries: dict[str, tuple[str, str]] = {}
    for heading, lines in sections:
        verb = VERB_OF[heading]
        for line in lines:
            if not line.strip():
                continue
            if m := LOOP_ENTRY_PARTS.match(line):
                node, rest = m.group(1), m.group(2)
                if node in entries:
                    raise _Disagreement(
                        THREE_VERB_SECTIONS, f"`{node}` has two entries"
                    )
                entries[node] = (verb, rest)
            elif line.startswith((" ", "\t")) and entries:
                node = next(reversed(entries))
                entries[node] = (
                    entries[node][0],
                    entries[node][1] + " " + line.strip(),
                )
            else:
                raise _Disagreement(
                    THREE_VERB_SECTIONS,
                    f"{heading}: not an entry, `- `id` — …`: {line.strip()!r}",
                )
    return entries


def _graph_of(mermaid: list[str]) -> tuple[set[str], list[tuple[str, str]]]:
    """The node ids and (source, target) edges of a Mermaid flowchart."""
    lines = [line.strip() for line in mermaid if line.strip()]
    if not lines or not lines[0].startswith(("flowchart", "graph")):
        raise _Disagreement(ONE_GRAPH, "the mermaid block is not a flowchart")
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    for stmt in lines[1:]:
        if MERMAID_DIRECTIVE.match(stmt):
            continue
        if "&" in stmt:
            raise _Disagreement(
                ONE_GRAPH,
                f"`&` fan-out is not read; write one edge per line: {stmt!r}",
            )
        ids = []
        for term in MERMAID_ARROW.split(stmt):
            m = MERMAID_NODE.match(term.strip())
            if not m:
                raise _Disagreement(
                    ONE_GRAPH, f"cannot read node {term.strip()!r} in {stmt!r}"
                )
            ids.append(m.group(1))
            nodes.add(m.group(1))
        edges.extend(zip(ids, ids[1:], strict=False))
    return nodes, edges


def _check_entry(repo: Repo, path: str, node: str, verb: str, rest: str) -> None:
    """One entry's condition and links."""
    if not any(phrase in rest for phrase in CONDITION_OF[verb]):
        raise _Disagreement(
            ENTRIES_STATE_CONDITIONS,
            f"`{node}` states no condition ({' / '.join(CONDITION_OF[verb])})",
        )
    links = INLINE_LINK.findall(rest)
    if verb == "yield":
        if not links and "the user" not in rest and "the principal" not in rest:
            raise _Disagreement(
                ENTRIES_STATE_CONDITIONS,
                f"`{node}` names no receiver: the user, the principal, or a linked Loop",
            )
        for link in links:
            if _type_of(repo, _loop_link(repo, path, link)) != LOOP_TYPE:
                raise _Disagreement(
                    ENTRIES_STATE_CONDITIONS,
                    f"`{node}` yields to {link!r}, which is not typed Loop",
                )
        return
    if not links:
        what = "runbook" if verb == "act" else "Standard"
        raise _Disagreement(ENTRIES_STATE_CONDITIONS, f"`{node}` links no {what}")
    target = _loop_link(repo, path, links[0])
    for link in links[1:]:
        _loop_link(repo, path, link)
    if verb == "verification" and _type_of(repo, target) != STANDARD_TYPE:
        raise _Disagreement(
            ENTRIES_STATE_CONDITIONS,
            f"`{node}` verifies {links[0]!r}; a verification links a file typed Standard",
        )


def _loop_link(repo: Repo, path: str, link: str) -> str:
    """The repo file a Loop entry's link reaches; raises when it reaches none."""
    target = _resolve(path, link, repo.name, "")
    if target not in repo.files:
        raise _Disagreement(ENTRIES_STATE_CONDITIONS, f"link {link!r} does not resolve")
    return target


def _type_of(repo: Repo, path: str) -> str | None:
    """The frontmatter ``type`` of a tracked markdown file; None for any other."""
    doc = repo.markdown.get(path)
    if doc is None or doc.frontmatter is None:
        return None
    return doc.frontmatter.get("type")


def _parent_head(heads: dict[str, str], path: str) -> str | None:
    """The head file in the nearest directory above ``path``'s own; None at the top."""
    here = posixpath.dirname(path)
    while here:
        here = posixpath.dirname(here)
        if here in heads:
            return heads[here]
    return None


def _reached(graph: dict[str, set[str]], root: str) -> set[str]:
    """Every file a chain of links leads to from ``root``, ``root`` included."""
    seen = {root}
    frontier = [root]
    while frontier:
        for target in graph.get(frontier.pop(), set()):
            if target not in seen:
                seen.add(target)
                frontier.append(target)
    return seen


def _typed(repo: Repo, doctype: str) -> Iterator[tuple[str, MarkdownFile]]:
    """Every markdown file whose frontmatter ``type`` is ``doctype``.

    A file under ``workstreams/`` may carry a type before it moves to that
    type's home, and that type's form rules do not bind it there; only
    ``Workstream``, whose home is ``workstreams/``, and ``Standard``, a draft
    Standard there, are read there.
    """
    for path, doc in sorted(repo.markdown.items()):
        if path.startswith(WORKSTREAMS) and doctype not in (
            WORKSTREAM_TYPE,
            STANDARD_TYPE,
        ):
            continue
        if doc.frontmatter is not None and doc.frontmatter.get("type") == doctype:
            yield path, doc


def _workstream_name(repo: Repo, path: str) -> str | None:
    """The name of the directory of ``path``'s head file; None if none is above it."""
    here = posixpath.dirname(path)
    while here.startswith(WORKSTREAMS):
        if f"{here}/{HEAD_FILE}" in repo.markdown:
            return posixpath.basename(here)
        here = posixpath.dirname(here)
    return None


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
    resolved = md.resolve_target(source, target, repo_name, harness_root or None)
    return resolved.path if resolved.kind == "repo" else ""


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
