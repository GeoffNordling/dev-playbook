#!/usr/bin/env python3
"""chaingen — reconstruct a runbook's Reference chain from its encoded file.

Prototype implementing REFERENCE-CHAIN-ENCODING.md's certified transform: slice, never
interpret. Cut points are the keyword, the markdown
link(s), the `with` splitter, nested braces, and the first semicolon.
Everything between cut points is opaque verbatim text. A `#fragment` on a
read/launch/run link target splits off as a `§ fragment` annotation on the
edge, after failing loud unless it matches a heading slug in the target.
A `{Never {…}}` span wraps one primitive span and renders a prohibition
edge — `never <verb>`, the wrapped payload's kernel as target, possibly
empty. A bucket prefix opens a linkless payload and names the target
node: `{Write to GitHub …}` / `{Write to scratch …}` pick the write
bucket, `{Read from GitHub …}` the GitHub read.

Usage:
    chaingen.py            regenerate chains.txt — every runbook in the
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
    "if": "condition",
    "never": "never",
}

# A Never span wraps one primitive span and flips it from assertion to
# prohibition. Only these keywords can be prohibited; the label keeps each
# keyword's own verb — commit stays "commits", not the assertion fold to
# "writes", since no git block exists to disambiguate.
NEVER_LEXICON = {
    "write": "writes",
    "commit": "commits",
    "merge": "merges",
}

NODE_DATA_KEYS = ("tools", "model", "effort", "allowed-tools", "disallowed-tools")

# Bucket prefixes: a fixed literal opening a linkless payload picks the
# target node. Write buckets serve assertion and prohibition alike, so
# {Never {Write to GitHub}} draws the same GitHub node.
WRITE_BUCKETS = (("to GitHub", "GitHub"), ("to scratch", "scratch"))
READ_BUCKET = ("from GitHub", "GitHub")

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

CODE_RE = re.compile(r"`([^`]+)`")

LABEL_FIELD = 8  # ─reads───► : label plus dashes fill 8 columns
SEP = "    "  # segment separator on an edge line


class LintError(Exception):
    """A grammar violation in an encoded file."""


# ── frontmatter ──────────────────────────────────────────────────────────


def split_frontmatter(text, path):
    """Split a runbook file into its frontmatter dict and body text."""
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


def split_bucket(payload, prefix):
    """The rest of a payload opening with the bucket prefix, or None."""
    pat = r"\s+".join(re.escape(w) for w in prefix.split())
    m = re.match(pat + r"\b", payload, re.IGNORECASE)
    if not m:
        return None
    return payload[m.end() :].strip()


def one_code(payload, where):
    """Extract a linkless payload's single inline-code target and the remainder."""
    codes = CODE_RE.findall(payload)
    if len(codes) != 1:
        raise LintError(
            f"{where}: a linkless Read needs exactly one inline-code target, "
            f"found {len(codes)}"
        )
    return codes[0], collapse(CODE_RE.sub(" ", payload, count=1))


# ── target classification ────────────────────────────────────────────────


def repo_root(start):
    """Walk up from `start` to the enclosing repository root."""
    d = os.path.abspath(start)
    while d != "/":
        if os.path.exists(os.path.join(d, ".git")):
            return d
        d = os.path.dirname(d)
    raise LintError(f"no repo root above {start}")


def resolve(link_target, source_file):
    """Resolve a link target to an on-disk path; fail if it does not exist."""
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
    return path


def classify(link_text, link_target, source_file):
    """Render a link target as a node, or as the link text for a non-runbook."""
    real = os.path.realpath(resolve(link_target, source_file))
    base = os.path.basename(real)
    if base == "SKILL.md":
        name, ntype = os.path.basename(os.path.dirname(real)), "Skill"
    elif "/agents/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Agent"
    elif "/standards/" in real:
        name, ntype = base[:-3] if base.endswith(".md") else base, "Standard"
    elif "/scripts/" in real or re.search(r"\.(sh|py|bash)$", base):
        # the path segment types extensionless scripts (repo-lint,
        # judgments-run), the same rule agents/ uses
        name, ntype = base, "Script"
    else:
        return link_text  # not a runbook: the link text travels verbatim
    return f"[{name}] {ntype}"


# ── fragment anchors ─────────────────────────────────────────────────────
# Mirrors dev_playbook.md's github_slug/heading_slugs — the package is not
# importable from this standalone prototype, so the regexes are copied.

SLUG_BACKTICK = re.compile(r"`([^`]*)`")
SLUG_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
SLUG_STAR = re.compile(r"(\*{1,2})(.+?)\1")
SLUG_UNDERSCORE = re.compile(r"(?<!\w)(_{1,2})(?=\S)(.+?)(?<=\S)\1(?!\w)")
SLUG_DROP = re.compile(r"[^\w\s\-]")
SLUG_WHITESPACE = re.compile(r"\s")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})\s*(.*)$")


def github_slug(heading):
    """GitHub's anchor slug for a heading."""
    text = SLUG_BACKTICK.sub(r"\1", heading)
    text = SLUG_LINK.sub(r"\1", text)
    text = SLUG_STAR.sub(r"\2", text)
    text = SLUG_UNDERSCORE.sub(r"\2", text)
    text = SLUG_DROP.sub("", text.lower())
    return SLUG_WHITESPACE.sub("-", text)


def heading_slugs(path):
    """Slugs of every heading in the file at `path`, fenced code skipped."""
    slugs, fence = set(), None
    with open(path) as f:
        for line in f:
            m = FENCE_RE.match(line)
            if m:
                run, info = m.group(1), m.group(2)
                if fence is None:
                    fence = run
                    continue
                if run[0] == fence[0] and len(run) >= len(fence) and not info:
                    fence = None
                    continue
            if fence is None and (h := HEADING_RE.match(line)):
                slugs.add(github_slug(h.group(1)))
    return slugs


def split_anchor(link_target, source_file, where):
    """Split a #fragment off a link target; the fragment must name a heading."""
    target, _, fragment = link_target.partition("#")
    if not fragment:
        return link_target, ""
    if not target.endswith(".md"):
        raise LintError(f"{where}: #fragment on a non-markdown target: {link_target}")
    if fragment not in heading_slugs(resolve(target, source_file)):
        raise LintError(f"{where}: no heading slugs to '#{fragment}' in {target}")
    return target, fragment


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
        if (
            key == "read"
            and (rest := split_bucket(payload, READ_BUCKET[0])) is not None
        ):
            # GitHub state read: no on-disk target exists, the prefix is
            # the whole address.
            if LINK_RE.search(payload):
                raise LintError(f"{where}: a from-GitHub Read carries a link")
            return Edge(label, READ_BUCKET[1], collapse(kernel(rest)))
        if key == "read" and not LINK_RE.search(payload):
            # Runtime-bound target: a file in the invoking repo, named as
            # inline code per the cross-reference standard's varied-location
            # row. No on-disk resolution — the node is the token verbatim.
            token, rest = one_code(payload, where)
            return Edge(label, f"`{token}`", collapse(kernel(rest)))
        _text, target, rest = one_link(payload, where)
        target, anchor = split_anchor(target, source_file, where)
        node = classify(_text, target, source_file)
        annotation = SEP.join(
            s for s in (f"§ {anchor}" if anchor else "", collapse(kernel(rest))) if s
        )
        return Edge(label, node, annotation)
    if key == "write":
        for prefix, node in WRITE_BUCKETS:
            if (rest := split_bucket(payload, prefix)) is not None:
                return Edge(label, node, collapse(kernel(rest)))
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
    """All edges of a body in document order, conditions stamped."""
    edges = []
    for span in scan_spans(body):
        key, payload = keyword_of(span)
        if key == "never":
            if len(span.children) != 1:
                raise LintError(
                    f"Never at offset {span.start} must wrap exactly one span"
                )
            if collapse(payload):
                raise LintError(
                    f"Never at offset {span.start} carries prose outside its span"
                )
            child = span.children[0]
            stripped = child.text.lstrip()
            # the keyword is the leading alpha run — a semicolon may follow
            # it directly ({Never {Write; …}})
            m = re.match(r"[A-Za-z]+", stripped)
            word = m.group(0) if m else ""
            if word.lower() not in NEVER_LEXICON:
                raise LintError(
                    f"Never cannot prohibit {word!r} at offset {child.start}"
                )
            inner = stripped[len(word) :].strip()
            target, annotation = collapse(kernel(inner)), ""
            if word.lower() == "write":
                for prefix, node in WRITE_BUCKETS:
                    if (rest := split_bucket(inner, prefix)) is not None:
                        target, annotation = node, collapse(kernel(rest))
                        break
            edges.append(
                Edge("never " + NEVER_LEXICON[word.lower()], target, annotation)
            )
            continue
        if key == "if":
            if not span.children:
                raise LintError(f"condition at offset {span.start} nests no span")
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
                    raise LintError(
                        f"condition nested in condition at offset {child.start}"
                    )
                if ckey == "never":
                    raise LintError(
                        f"Never nested in condition at offset {child.start}"
                        " is not supported"
                    )
                edge = edge_from_span(ckey, cpayload, child, body, source_file)
                edge.condition = "if " + condition
                edges.append(edge)
        else:
            edges.append(edge_from_span(key, payload, span, body, source_file))
    return edges


# ── rendering ────────────────────────────────────────────────────────────


def render_edge(edge, last):
    """Render one edge line — dashed when conditional, solid otherwise."""
    corner = "└" if last else "├"
    if edge.condition:
        arrow = f"{corner} ╌ {edge.label} ╌ ►"
    else:
        pad = "─" * max(1, LABEL_FIELD - len(edge.label))
        arrow = f"{corner}─{edge.label}{pad}►"
    segments = [s for s in (edge.target, edge.annotation, edge.condition) if s]
    if not segments:  # a total prohibition: bare arrow, empty node slot
        return f"  {arrow}"
    return f"  {arrow} " + SEP.join(segments)


def render_unit(path):
    """Render one runbook file as its full chain, header plus edges."""
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


def all_runbooks(claude_dir):
    """Every runbook in the corpus: agents/*.md, then skills/*/SKILL.md."""
    runbooks = sorted(glob.glob(os.path.join(claude_dir, "agents", "*.md")))
    runbooks += sorted(glob.glob(os.path.join(claude_dir, "skills", "*", "SKILL.md")))
    return runbooks


def unit_name(path):
    """A runbook's display name: the skill's directory or the agent's basename."""
    base = os.path.basename(path)
    if base == "SKILL.md":
        return os.path.basename(os.path.dirname(path))
    return base[: -len(".md")]


def main(argv):
    """Write chains.txt, or with --check diff against it."""
    here = os.path.dirname(os.path.abspath(__file__))
    chains_path = os.path.join(here, "chains.txt")
    runbooks = all_runbooks(os.path.join(here, "..", "..", "dotfiles", "dot-claude"))
    rendered = []
    for p in runbooks:
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
            print(f"OK: chains.txt matches all {len(runbooks)} runbooks")
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
    print(f"wrote {len(runbooks)} chains to {chains_path}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except LintError as e:
        print(f"lint: {e}", file=sys.stderr)
        sys.exit(1)
