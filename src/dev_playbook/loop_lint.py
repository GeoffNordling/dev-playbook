"""Check every Loop's Mermaid graph against the prose around it.

loop-lint is the detector behind Loop Conventions
(standards/knowledge-organization/loop-conventions.md), the Standard that
binds a document typed ``Loop`` to the Loop doc-type's encoding
(doc-types/loop/encoding.md). It walks a repo's markdown files once (via
dev_playbook.md.find_md_files, so gitignore-aware and worktree-scoped),
keeps the files under ``loops/`` typed ``Loop``, and reads each one the
way the encoding cuts it: one paragraph, one fenced ``mermaid`` flowchart,
then three H2s, ``Acts``, ``Checks``, ``Yields``, each a list with one entry
per node, ``- `id` — <link>, fires when … / yields when …``. A node under
no heading is a receiver, the user or another loop a yield hands control
to. Five rules:

  - **loop-graph** — one paragraph before one ``mermaid`` flowchart the
    detector can read; nothing else before the graph.
  - **loop-sections** — the three verb H2s, in order, and nothing else
    after the graph; every list line is an entry with a backticked node
    id, each id once.
  - **loop-nodes** — every entry is a node of the graph; every node has an
    entry or is a receiver some yield leads to.
  - **loop-edges** — an act leads to an act or a check, a check to a check
    or a yield, a yield back to an act or out to a receiver, a receiver
    back to an act.
  - **loop-entries** — an act links a file; a check links a card's Audit
    cell, ``standards/<card>/card.md#audit``; a yield names the user or
    links a Loop; every entry states its condition.

The detector stops at a file's first disagreement, since each rule reads
the cut the one before it made, and goes on to the next file. It writes
nothing: a Loop's view is the graph GitHub renders. A repo with no
``loops/`` tree is clean by construction, the optional-surface shape
(standards/standard/detectors.md).

Output:
    stdout — one finding per line, ``file: knowledge-organization.loop-… message``.
    stderr — one readable summary line.
    exit   — 0 clean, 1 findings, 2 cannot run.

Usage:
    loop-lint [directory]
    loop-lint --list-rules
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from dev_playbook import md
from dev_playbook.findings import print_rules, render

# Every rule id this detector can emit, namespaced by the card whose question
# it answers. Each is a module-level constant so RULES cannot drift from what
# the detector emits.
LOOP_GRAPH = "knowledge-organization.loop-graph"
LOOP_SECTIONS = "knowledge-organization.loop-sections"
LOOP_NODES = "knowledge-organization.loop-nodes"
LOOP_EDGES = "knowledge-organization.loop-edges"
LOOP_ENTRIES = "knowledge-organization.loop-entries"

RULES = (LOOP_GRAPH, LOOP_SECTIONS, LOOP_NODES, LOOP_EDGES, LOOP_ENTRIES)

LOOPS_DIR = "loops"
LOOP_TYPE = "Loop"
CARD_TYPE = "Standard-Card"
AUDIT_CELL = "audit"
VERBS = ("Acts", "Checks", "Yields")
VERB_OF = {"Acts": "act", "Checks": "check", "Yields": "yield"}
RECEIVER = "receiver"
# What each kind of node may lead to. A receiver is a node under no heading.
MAY_LEAD_TO = {
    "act": {"act", "check"},
    "check": {"check", "yield"},
    "yield": {"act", RECEIVER},
    RECEIVER: {"act"},
}
CONDITION_OF = {
    "act": ("fires when", "fires every iteration"),
    "check": ("fires when", "fires every iteration"),
    "yield": ("yields when",),
}

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(\S*)\s*$")
ENTRY_RE = re.compile(r"^[-*]\s+`([^`]+)`\s+—\s+(.*\S)\s*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
# A Mermaid node: an id and an optional shape from the flowchart set —
# [text], (text), ([text]), [[text]], [(text)], ((text)), >text], {text},
# {{text}}. The label inside is opaque.
NODE_RE = re.compile(
    r"^([A-Za-z_][\w-]*)"
    r"(\(\[.*?\]\)|\[\[.*?\]\]|\[\(.*?\)\]|\(\(.*?\)\)|\{\{.*?\}\}"
    r"|\[.*?\]|\(.*?\)|\{.*?\}|>.*?\])?$"
)
# An arrow between two node terms, with an optional |label|.
ARROW_RE = re.compile(r"\s*(?:-->|-\.->|==>|---|-\.-|===)(?:\|[^|]*\|)?\s*")
# Statements that draw nothing the detector reads.
DIRECTIVE_RE = re.compile(
    r"^(%%|subgraph\b|end$|direction\b|classDef\b|class\b|style\b|linkStyle\b)"
)

Sections = list[tuple[str, list[str]]]
Entries = dict[str, tuple[str, str]]


class Disagreement(Exception):
    """The first place a Loop's graph and prose disagree, under one rule."""

    def __init__(self, rule: str, message: str) -> None:
        """Record the rule the disagreement falls under, and the message."""
        super().__init__(message)
        self.rule = rule


# --- the file: paragraph, graph, verb sections ------------------------------


def slice_loop(body: str) -> tuple[list[str], Sections]:
    """Cut a Loop's body into (mermaid lines, H2 sections after the graph).

    Before the fence: the H1 and exactly one paragraph. The fence: one
    ``mermaid`` block. After it: H2s only, each with the lines beneath it.
    """
    before: list[str] = []
    mermaid: list[str] | None = None
    sections: Sections = []
    fence: str | None = None
    in_mermaid = seen_h1 = False
    for line in body.split("\n"):
        if m := FENCE_RE.match(line):
            marker, info = m.group(1)[0], m.group(2)
            if fence is None:
                fence = marker
                if info == "mermaid":
                    if mermaid is not None:
                        raise Disagreement(
                            LOOP_GRAPH, "two mermaid blocks; the encoding is one"
                        )
                    if sections:
                        raise Disagreement(
                            LOOP_GRAPH, "the mermaid block sits after a verb section"
                        )
                    mermaid, in_mermaid = [], True
                continue
            if marker == fence:
                fence, in_mermaid = None, False
                continue
        if in_mermaid and mermaid is not None:
            mermaid.append(line)
            continue
        if fence is None and (m := HEADING_RE.match(line)):
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                if seen_h1:
                    raise Disagreement(LOOP_GRAPH, "two H1s")
                seen_h1 = True
                continue
            if mermaid is None:
                raise Disagreement(
                    LOOP_GRAPH,
                    f"heading {text!r} before the graph; only the paragraph sits there",
                )
            if level != 2:
                raise Disagreement(
                    LOOP_SECTIONS,
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
            raise Disagreement(
                LOOP_SECTIONS,
                f"text between the graph and the first verb heading: {line.strip()!r}",
            )
    if mermaid is None:
        raise Disagreement(LOOP_GRAPH, "no mermaid block")
    paragraphs = [p for p in "\n".join(before).split("\n\n") if p.strip()]
    if len(paragraphs) != 1:
        raise Disagreement(
            LOOP_GRAPH,
            f"{len(paragraphs)} paragraphs before the graph; the encoding is one",
        )
    return mermaid, sections


def entries_of(sections: Sections) -> Entries:
    """Map node id → (verb, entry text), from the three verb sections in order."""
    names = [text for text, _ in sections]
    if names != list(VERBS):
        raise Disagreement(
            LOOP_SECTIONS,
            f"verb sections are {names}; the encoding is {list(VERBS)} in that order",
        )
    entries: Entries = {}
    for heading, lines in sections:
        verb = VERB_OF[heading]
        for line in lines:
            if not line.strip():
                continue
            if m := ENTRY_RE.match(line):
                node, rest = m.group(1), m.group(2)
                if node in entries:
                    raise Disagreement(LOOP_SECTIONS, f"`{node}` has two entries")
                entries[node] = (verb, rest)
            elif line.startswith((" ", "\t")) and entries:
                node = next(reversed(entries))
                entries[node] = (
                    entries[node][0],
                    entries[node][1] + " " + line.strip(),
                )
            else:
                raise Disagreement(
                    LOOP_SECTIONS,
                    f"{heading}: not an entry, `- `id` — …`: {line.strip()!r}",
                )
    return entries


# --- the graph ----------------------------------------------------------------


def graph_of(mermaid: list[str]) -> tuple[set[str], list[tuple[str, str]]]:
    """The node ids and (source, target) edges of a Mermaid flowchart."""
    lines = [line.strip() for line in mermaid if line.strip()]
    if not lines or not lines[0].startswith(("flowchart", "graph")):
        raise Disagreement(LOOP_GRAPH, "the mermaid block is not a flowchart")
    nodes: set[str] = set()
    edges: list[tuple[str, str]] = []
    for stmt in lines[1:]:
        if DIRECTIVE_RE.match(stmt):
            continue
        if "&" in stmt:
            raise Disagreement(
                LOOP_GRAPH,
                f"`&` fan-out is not read; write one edge per line: {stmt!r}",
            )
        ids = []
        for term in ARROW_RE.split(stmt):
            m = NODE_RE.match(term.strip())
            if not m:
                raise Disagreement(
                    LOOP_GRAPH, f"cannot read node {term.strip()!r} in {stmt!r}"
                )
            ids.append(m.group(1))
            nodes.add(m.group(1))
        edges.extend(zip(ids, ids[1:], strict=False))
    return nodes, edges


# --- the entries: pointers and conditions -------------------------------------


def _resolve(link: str, loop_path: Path, root: Path) -> Path:
    """The file a link points at: root-absolute ``/…`` or relative to the Loop."""
    target = link.split("#", 1)[0]
    path = (
        root / target.lstrip("/")
        if target.startswith("/")
        else loop_path.parent / target
    )
    if not path.is_file():
        raise Disagreement(LOOP_ENTRIES, f"link {link!r} does not resolve")
    return path


def _type_of(path: Path) -> str | None:
    meta, _ = md.parse_frontmatter(path.read_text())
    return meta.get("type") if meta else None


def check_entry(node: str, verb: str, rest: str, loop_path: Path, root: Path) -> None:
    """One entry's pointer and condition."""
    if not any(phrase in rest for phrase in CONDITION_OF[verb]):
        raise Disagreement(
            LOOP_ENTRIES,
            f"`{node}` states no condition ({' / '.join(CONDITION_OF[verb])})",
        )
    links = LINK_RE.findall(rest)
    if verb == "yield":
        if not links and "the user" not in rest:
            raise Disagreement(
                LOOP_ENTRIES, f"`{node}` names no receiver: the user or a linked Loop"
            )
        for link in links:
            if _type_of(_resolve(link, loop_path, root)) != LOOP_TYPE:
                raise Disagreement(
                    LOOP_ENTRIES,
                    f"`{node}` yields to {link!r}, which is not typed Loop",
                )
        return
    if not links:
        what = "runbook" if verb == "act" else "card"
        raise Disagreement(LOOP_ENTRIES, f"`{node}` links no {what}")
    target = _resolve(links[0], loop_path, root)
    if verb == "check":
        fragment = links[0].partition("#")[2]
        if _type_of(target) != CARD_TYPE or fragment != AUDIT_CELL:
            raise Disagreement(
                LOOP_ENTRIES,
                f"`{node}` checks {links[0]!r}; a check links a card's Audit cell, "
                f"`standards/<card>/card.md#{AUDIT_CELL}`",
            )


# --- one Loop -----------------------------------------------------------------


def check_loop(loop_path: Path, root: Path) -> int:
    """Every rule over one Loop; returns its node count or raises Disagreement."""
    meta, body = md.parse_frontmatter(loop_path.read_text())
    mermaid, sections = slice_loop(body)
    entries = entries_of(sections)
    nodes, edges = graph_of(mermaid)
    for node in entries:
        if node not in nodes:
            raise Disagreement(
                LOOP_NODES, f"`{node}` has an entry but is not a node of the graph"
            )
    kind = {node: entries[node][0] if node in entries else RECEIVER for node in nodes}
    yielded_to = {t for s, t in edges if kind[s] == "yield"}
    for node in sorted(nodes):
        if kind[node] == RECEIVER and node not in yielded_to:
            raise Disagreement(
                LOOP_NODES, f"`{node}` has no entry and no yield leads to it"
            )
    for s, t in edges:
        if kind[t] not in MAY_LEAD_TO[kind[s]]:
            raise Disagreement(
                LOOP_EDGES,
                f"edge `{s}` → `{t}` is {kind[s]} → {kind[t]}; the shape does not allow it",
            )
    for node, (verb, rest) in entries.items():
        check_entry(node, verb, rest, loop_path, root)
    return len(nodes)


def loop_files(root: Path) -> list[Path]:
    """Every file typed Loop under loops/, by git listing."""
    loops = []
    for path in md.find_md_files(root):
        rel = path.relative_to(root)
        if rel.parts[0] != LOOPS_DIR or path.name in {"index.md", "README.md"}:
            continue
        if _type_of(path) == LOOP_TYPE:
            loops.append(path)
    return loops


def main(argv: list[str] | None = None) -> int:
    """Check every Loop under a repo's loops/; print findings; return the exit code."""
    parser = argparse.ArgumentParser(
        prog="loop-lint",
        description="Check every Loop's Mermaid graph against the verb sections around it.",
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
        loops = loop_files(root)
    except subprocess.CalledProcessError as err:
        print(f"loop-lint: cannot list files in {root}: {err}", file=sys.stderr)
        return 2

    findings: list[str] = []
    counted = 0
    for path in loops:
        rel = str(path.relative_to(root))
        try:
            counted += check_loop(path, root)
        except Disagreement as err:
            findings.append(render(rel, err.rule, str(err)))

    for line in findings:
        print(line)
    if findings:
        print(
            f"loop-lint: {len(findings)} finding(s) across {len(loops)} loop(s)",
            file=sys.stderr,
        )
        return 1
    print(
        f"loop-lint: clean ({len(loops)} loop(s), {counted} node(s), graph and prose agree)",
        file=sys.stderr,
    )
    return 0
