#!/usr/bin/env python3
"""chaingen — reconstruct a unit's Reference chain from its encoded file.

Prototype for To-do item 1 of EDGE-ENCODING.md. Implements the certified
transform: slice, never interpret. Cut points are the keyword, the markdown
link(s), the `with` splitter, nested braces, and the first semicolon.
Everything between cut points is opaque verbatim text.

Usage:
    chaingen.py            regenerate chains.txt — every unit in the
                           corpus (dotfiles/dot-claude agents and
                           skills), blank-line separated
    chaingen.py --check    regenerate in memory and diff against
                           chains.txt; exit 1 on drift
"""

import difflib
import glob
import os
import re
import sys

LEXICON = {
    "read": "reads",
    "commit": "writes",
    "write": "writes",
    "report": "reports",
    "launch": "does",
    "run": "does",
    "override": "overrides",
    "if": "guard",
}

NODE_DATA_KEYS = ("tools", "model", "effort", "allowed-tools")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

LABEL_FIELD = 8  # ─reads───► : label plus dashes fill 8 columns
SEP = "    "  # segment separator on an edge line


class LintError(Exception):
    """A grammar violation in an encoded file."""


# ── frontmatter ──────────────────────────────────────────────────────────


def split_frontmatter(text, path):
    """Split a unit file into its frontmatter dict and body text."""
    lines = text.split("\n")
    if lines[0] != "---":
        raise LintError(f"{path}: no frontmatter")
    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        raise LintError(f"{path}: unterminated frontmatter") from None
    meta = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    return meta, "\n".join(lines[end + 1 :])


def parse_arguments(meta):
    """Read the `arguments` frontmatter list — names only."""
    raw = meta.get("arguments", "")
    if not raw:
        return []
    if not (raw.startswith("[") and raw.endswith("]")):
        raise LintError(f"arguments not a list: {raw!r}")
    return [a.strip() for a in raw[1:-1].split(",") if a.strip()]


# ── span scanner ─────────────────────────────────────────────────────────
# Walks the body character by character. Backtick-delimited code (inline
# spans and fences alike) is inert: braces inside it never open or close
# a span, but its characters are captured verbatim into payloads.


class Span:
    """One braced span: payload text with nested spans elided."""

    def __init__(self, start):
        """Open a span at byte offset `start`."""
        self.start = start
        self.text = ""  # payload with nested spans elided
        self.children = []


def scan_spans(body):
    """Collect top-level spans, nesting capped at two deep."""
    spans, stack = [], []
    in_code = False
    i = 0
    while i < len(body):
        c = body[i]
        if c == "`":
            in_code = not in_code
        if not in_code:
            if c == "{":
                span = Span(i)
                if stack:
                    if len(stack) >= 2:
                        raise LintError(f"nesting deeper than two at offset {i}")
                    stack[-1].children.append(span)
                stack.append(span)
                i += 1
                continue
            if c == "}":
                if not stack:
                    raise LintError(f"unbalanced '}}' at offset {i}")
                span = stack.pop()
                span.end = i
                if not stack:
                    spans.append(span)
                i += 1
                continue
        if stack:
            stack[-1].text += c
        i += 1
    if stack:
        raise LintError(f"unclosed '{{' at offset {stack[-1].start}")
    if in_code:
        raise LintError("unbalanced backtick")
    return spans


def keyword_of(span):
    """Split a span into its lexicon keyword and payload."""
    stripped = span.text.lstrip()
    word = stripped.split(None, 1)[0] if stripped else ""
    key = word.lower()
    if key not in LEXICON:
        raise LintError(f"unknown keyword {word!r} in span at offset {span.start}")
    payload = stripped[len(word) :].strip()
    return key, payload


# ── slicing helpers ──────────────────────────────────────────────────────


def collapse(text):
    """Collapse whitespace runs — spans wrap across source lines."""
    return " ".join(text.split())


def kernel(text):
    """The first semicolon (outside inline code) ends the chain's view."""
    in_code = False
    for i, c in enumerate(text):
        if c == "`":
            in_code = not in_code
        elif c == ";" and not in_code:
            return text[:i]
    return text


def one_link(payload, where):
    """Extract the payload's single markdown link and the remainder."""
    links = LINK_RE.findall(payload)
    if len(links) != 1:
        raise LintError(f"{where}: expected exactly one link, found {len(links)}")
    text, target = links[0]
    remainder = collapse(LINK_RE.sub(" ", payload, count=1))
    return text, target, remainder


# ── target classification ────────────────────────────────────────────────


def repo_root(start):
    """Walk up from `start` to the enclosing repository root."""
    d = os.path.abspath(start)
    while d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    raise LintError(f"no repo root above {start}")


def classify(link_text, link_target, source_file):
    """Render a link target as a node, or as the link text for a non-unit."""
    if link_target.startswith("~"):
        path = os.path.expanduser(link_target)
        # Same-repo resolution: a ~/workspace/<repo>/… path naming the repo
        # the source file lives in resolves inside that file's own checkout
        # (main or worktree), not the literal main checkout.
        m = re.match(r"~/workspace/([^/]+)/(.*)", link_target)
        if m:
            main = os.path.expanduser(f"~/workspace/{m.group(1)}")
            root = repo_root(os.path.dirname(source_file))
            if root == main or root.startswith(main + os.sep):
                path = os.path.join(root, m.group(2))
        # ~/.claude/ is this meta-repo's dotfiles/dot-claude tree, stowed;
        # from inside the repo it resolves to the checkout's own tree.
        m = re.match(r"~/\.claude/(.*)", link_target)
        if m:
            stowed = os.path.join(
                repo_root(os.path.dirname(source_file)), "dotfiles", "dot-claude"
            )
            if os.path.isdir(stowed):
                path = os.path.join(stowed, m.group(1))
    elif link_target.startswith("/"):
        path = os.path.join(
            repo_root(os.path.dirname(source_file)), link_target.lstrip("/")
        )
    else:
        path = os.path.join(os.path.dirname(source_file), link_target)
    if not os.path.exists(path):
        raise LintError(f"link target does not exist: {link_target} -> {path}")
    real = os.path.realpath(path)
    vendored = "/.agents/" in real
    base = os.path.basename(real)
    if base == "SKILL.md":
        name, ntype = os.path.basename(os.path.dirname(real)), "Skill"
    elif "/agents/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Agent"
    elif "/standards/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Standard"
    elif re.search(r"\.(sh|py|bash)$", base):
        name, ntype = base, "Script"
    else:
        return link_text  # not a unit: the link text travels verbatim
    braces = "{{{}}}" if vendored else "[{}]"
    return f"{braces.format(name)} {ntype}"


# ── git bucket ───────────────────────────────────────────────────────────


def git_detail(body, after):
    """Read the git command after a Commit span: -C repo, subcommands in order."""
    for line in body[after:].split("\n"):
        stripped = line.strip()
        if stripped.startswith("git "):
            repo_m = re.search(r"-C\s+(\S+)", stripped)
            if not repo_m:
                raise LintError("git command block without -C")
            subs, seen = [], set()
            for m in re.finditer(r"git\s+(?:-C\s+\S+\s+)?([a-z-]+)", stripped):
                if m.group(1) not in seen:
                    seen.add(m.group(1))
                    subs.append(m.group(1))
            return f"git({repo_m.group(1)}: {', '.join(subs)})"
    raise LintError("Commit span with no git command block after it")


# ── edge construction ────────────────────────────────────────────────────


class Edge:
    """One chain edge: label, target, annotation, condition."""

    def __init__(self, label, target, annotation="", condition=""):
        """Build an edge; annotation and condition default empty."""
        self.label = label
        self.target = target
        self.annotation = annotation
        self.condition = condition


def edge_from_span(key, payload, span, body, source_file):
    """Slice one edge span into an Edge per its keyword's rule."""
    label = LEXICON[key]
    where = f"span at offset {span.start}"
    if key in ("read", "launch", "run"):
        _text, target, rest = one_link(payload, where)
        node = classify(_text, target, source_file)
        return Edge(label, node, collapse(kernel(rest)))
    if key == "write":
        return Edge(label, "local file", collapse(kernel(payload)))
    if key == "commit":
        return Edge(label, git_detail(body, span.end), collapse(kernel(payload)))
    if key == "report":
        return Edge(label, "outcome: str", collapse(kernel(payload)))
    if key == "override":
        left, sep, right = payload.partition(" with ")
        if not sep:
            raise LintError(f"{where}: Override without 'with'")
        ltext, ltarget, lrest = one_link(left, where + " (left of with)")
        rtext, rtarget, rrest = one_link(right, where + " (right of with)")
        lnode = classify(ltext, ltarget, source_file)
        rnode = classify(rtext, rtarget, source_file)
        annotation = SEP.join(
            s
            for s in (collapse(kernel(lrest)), f"with {rnode}", collapse(kernel(rrest)))
            if s
        )
        return Edge(label, lnode, annotation)
    raise LintError(f"{where}: keyword {key!r} is not an edge")


def edges_of(body, source_file):
    """All edges of a body in document order, guard conditions stamped."""
    edges = []
    for span in scan_spans(body):
        key, payload = keyword_of(span)
        if key == "if":
            if not span.children:
                raise LintError(f"guard at offset {span.start} nests no span")
            # condition: raw text between the keyword and the first nested
            # span, trailing comma dropped
            condition = collapse(
                kernel(
                    body[span.start + 1 : span.children[0].start]
                    .lstrip()[len(key) :]
                    .strip()
                    .rstrip(",")
                )
            )
            for child in span.children:
                ckey, cpayload = keyword_of(child)
                if ckey == "if":
                    raise LintError(f"guard nested in guard at offset {child.start}")
                edge = edge_from_span(ckey, cpayload, child, body, source_file)
                edge.condition = "if " + condition
                edges.append(edge)
        else:
            edges.append(edge_from_span(key, payload, span, body, source_file))
    return edges


# ── rendering ────────────────────────────────────────────────────────────


def render_edge(edge, last):
    """Render one edge line — dashed when guarded, solid otherwise."""
    corner = "└" if last else "├"
    if edge.condition:
        arrow = f"{corner} ╌ {edge.label} ╌ ►"
    else:
        pad = "─" * max(1, LABEL_FIELD - len(edge.label))
        arrow = f"{corner}─{edge.label}{pad}►"
    segments = [edge.target]
    if edge.annotation:
        segments.append(edge.annotation)
    if edge.condition:
        segments.append(edge.condition)
    return f"  {arrow} " + SEP.join(segments)


def render_unit(path):
    """Render one unit file as its full chain, header plus edges."""
    with open(path) as f:
        text = f.read()
    meta, body = split_frontmatter(text, path)
    real = os.path.realpath(path)
    ntype = "Agent" if "/agents/" in real else "Skill"
    braces = "{{{}}}" if "/.agents/" in real else "[{}]"
    data = ", ".join(f"{k}: {meta[k]}" for k in meta if k in NODE_DATA_KEYS)
    header = f"{braces.format(meta['name'])} {ntype}" + (f" · {data}" if data else "")
    edges = [Edge("args", a) for a in parse_arguments(meta)]
    edges += edges_of(body, os.path.abspath(path))
    lines = [header]
    for i, edge in enumerate(edges):
        lines.append(render_edge(edge, i == len(edges) - 1))
    return "\n".join(lines) + "\n"


# ── entry ────────────────────────────────────────────────────────────────


def all_units(claude_dir):
    """Every unit in the corpus: agents/*.md, then skills/*/SKILL.md."""
    units = sorted(glob.glob(os.path.join(claude_dir, "agents", "*.md")))
    units += sorted(glob.glob(os.path.join(claude_dir, "skills", "*", "SKILL.md")))
    return units


def unit_name(path):
    """A unit's display name: the skill's directory or the agent's basename."""
    base = os.path.basename(path)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(path))
    return base[: -len(".md")]


def main(argv):
    """Write chains.txt, or with --check diff against it."""
    here = os.path.dirname(os.path.abspath(__file__))
    chains_path = os.path.join(here, "chains.txt")
    units = all_units(os.path.join(here, "..", "..", "dotfiles", "dot-claude"))
    rendered = []
    for p in units:
        try:
            rendered.append(render_unit(p))
        except LintError as e:
            raise LintError(f"{unit_name(p)}: {e}") from None
    text = "\n".join(rendered)
    if argv == ["--check"]:
        if not os.path.exists(chains_path):
            print("DRIFT: chains.txt does not exist")
            return 1
        with open(chains_path) as f:
            want = f.read()
        if text == want:
            print(f"OK: chains.txt matches all {len(units)} units")
            return 0
        print("DRIFT:")
        sys.stdout.writelines(
            difflib.unified_diff(
                want.splitlines(keepends=True),
                text.splitlines(keepends=True),
                "chains.txt",
                "regenerated",
            )
        )
        return 1
    if argv:
        print(__doc__)
        return 2
    with open(chains_path, "w") as f:
        f.write(text)
    print(f"wrote {len(units)} chains to {chains_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except LintError as e:
        print(f"lint: {e}", file=sys.stderr)
        sys.exit(1)
