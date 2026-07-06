"""Build the file graph of a repository, per the instrument spec.

The contract is /instruments/file-graph.md: every in-scope file (per
``gitrepo.git_files``) becomes a node in exactly one bucket, gitignored
files are counted per ignore pattern, and every detected reference becomes
a typed, directed edge. :func:`build_graph` returns the spec's machine
artifact as a dict; the ``file-graph`` script serializes it.

Markdown mechanics (fence skipping, link extraction, frontmatter, the
concept/harness classification) come from :mod:`dev_playbook.md`, so the
graph's grammar cannot drift from ``ref-check`` and ``okf-lint``.
"""

import re
import subprocess
from collections import Counter, deque
from collections.abc import Set as AbstractSet
from pathlib import Path, PurePosixPath

from dev_playbook import gitrepo, md

CODE_EXTENSIONS = {".py", ".sh", ".js"}
CONFIG_EXTENSIONS = {
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".lock",
    ".html",
    ".cfg",
    ".ini",
}
CONFIG_NAMES = {"Makefile"}
# Mirrors scripts/ref-check: sources with no fixed repo root (skills, rules,
# box artifacts) legitimately use the Citation form for same-repo targets.
ROOTLESS_SEGMENTS = {"skills", "rules", "box"}
FORMAL_FORMS = {"link", "citation", "resource"}
CORE_BUCKETS = {"concept", "index"}
# A path-shaped token in prose or code: a ~/workspace citation, a
# root-absolute path of two or more segments, or a relative path ending in a
# known extension.
PATH_TOKEN_PATTERN = re.compile(
    r"(?:~/workspace/[\w./\-]+"
    r"|(?<![\w.])/[\w\-]+(?:/[\w.\-]+)+"
    r"|(?<![\w./\-])[\w\-]+(?:/[\w.\-]+)*/[\w.\-]+"
    r"\.(?:md|py|sh|js|yaml|yml|json|toml)(?![\w/]))"
)
URL_SCHEME_PATTERN = re.compile(r"^[a-z][a-z0-9+.-]*:")


def bucket(relpath: str, repo_root: Path) -> str:
    """Assign one bucket to an in-scope file, first matching test wins.

    The taxonomy is the spec's node-accounting table
    (/instruments/file-graph.md). The three ``harness-`` buckets are one
    family — files the Claude Code harness loads into agent context —
    subdivided by origin and load time. ``dev_playbook.md.classify`` is the
    reference encoding of the concept/harness boundary; this function only
    refines its ``harness`` answer.
    """
    parts = PurePosixPath(relpath).parts
    name = parts[-1]
    if ".agents" in parts:
        return "harness-skill-thirdparty"
    kind = md.classify(relpath)
    if kind in CORE_BUCKETS:
        return kind
    if "skills" in parts or name == "SKILL.md":
        return "harness-skill-authored"
    if relpath.endswith(".md") and kind == "harness":
        return "harness-session"
    suffix = PurePosixPath(relpath).suffix
    if suffix in CODE_EXTENSIONS:
        return "code"
    if (repo_root / relpath).stat().st_mode & 0o111:
        return "code"  # extensionless executables: hook and script entry points
    if suffix in CONFIG_EXTENSIONS or name.startswith(".") or name in CONFIG_NAMES:
        return "config"
    if relpath.startswith("standards/build/canonical/"):
        return "config"  # canonical templates: Makefile.base, CLAUDE.md.standards
    return "unclassified"


def ignored_census(repo_root: Path) -> dict[str, int]:
    """Count gitignored files per matching ignore rule (``source:pattern``).

    The aggregate grain of the spec's node accounting: ignored files get
    counted, never enumerated as nodes.
    """
    listing = subprocess.run(
        [
            "git",
            "-C",
            str(repo_root),
            "ls-files",
            "--others",
            "-i",
            "--exclude-standard",
            "-z",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    files = [f for f in listing.stdout.split("\0") if f]
    if not files:
        return {}
    probe = subprocess.run(
        ["git", "-C", str(repo_root), "check-ignore", "-v", "--stdin", "-z"],
        input="\0".join(files),
        capture_output=True,
        text=True,
    )
    if probe.returncode not in (0, 1):
        raise RuntimeError(f"git check-ignore failed: {probe.stderr}")
    # -v -z emits <source> NUL <linenum> NUL <pattern> NUL <pathname> NUL
    fields = probe.stdout.split("\0")
    counts = Counter(
        f"{fields[i]}:{fields[i + 2]}" for i in range(0, len(fields) - 3, 4)
    )
    return dict(counts.most_common())


# --- edge extraction ---------------------------------------------------------


def resolve_target(
    raw: str, source_rel: str, repo_name: str, repo_root: Path
) -> tuple[str, str]:
    """Resolve a raw reference target to ``(target, kind)``.

    ``kind`` is ``internal`` (target is a repo-relative path), ``external``
    (target lies outside this repo and stays as written), or ``url``
    (schemes and non-paths — not an edge). A fragment suffix is dropped;
    edges are file-grained.
    """
    text = raw.partition("#")[0]
    if not text:
        return source_rel, "internal"  # pure-anchor self reference
    if URL_SCHEME_PATTERN.match(text):
        return raw, "url"
    if text.startswith("~/workspace/"):
        segments = text[len("~/workspace/") :].split("/")
        if segments[0] == repo_name:
            return "/".join(segments[1:]), "internal"
        return text, "external"
    if text.startswith("/"):
        return text.lstrip("/"), "internal"
    resolved = (repo_root / PurePosixPath(source_rel).parent / text).resolve()
    try:
        return str(resolved.relative_to(repo_root)), "internal"
    except ValueError:
        return str(resolved), "external"  # relative path escaping the repo


def markdown_edges(relpath: str, repo_root: Path, repo_name: str) -> list[dict]:
    """Extract the markdown reference-grammar edges of one file.

    Covers the formal forms (``link``, ``citation``, ``resource``) with
    ``ref-check`` status semantics, plus off-grammar ``relative`` links.
    """
    text = (repo_root / relpath).read_text(encoding="utf-8", errors="replace")
    fixed_root = not (ROOTLESS_SEGMENTS & set(PurePosixPath(relpath).parts))
    edges = []

    def add(raw: str, form: str, line: int) -> None:
        target, kind = resolve_target(raw, relpath, repo_name, repo_root)
        if kind == "url":
            return
        if kind == "internal":
            status = "ok" if (repo_root / target).exists() else "broken"
            if form == "citation" and fixed_root:
                status = "wrong-form"
        else:
            expanded = Path(target).expanduser()
            status = "ok" if expanded.exists() else "broken"
        edges.append(
            {
                "source": relpath,
                "target": target,
                "kind": kind,
                "form": form,
                "line": line,
                "status": status,
            }
        )

    frontmatter, _ = md.parse_frontmatter(text)
    if frontmatter and isinstance(frontmatter.get("resource"), str):
        add(frontmatter["resource"], "resource", 0)

    for line_num, line in md.lines_outside_fences(text):
        stripped = md.INLINE_CODE_PATTERN.sub("", line)
        for _label, target in md.MD_LINK_PATTERN.findall(stripped):
            if target.startswith("~/workspace/"):
                add(target, "citation", line_num)
            elif target.startswith("/"):
                add(target, "link", line_num)
            elif not URL_SCHEME_PATTERN.match(target):
                add(target, "relative", line_num)
        # Bare citations outside link syntax; link targets already handled.
        remainder = md.MD_LINK_PATTERN.sub(r"\1", stripped)
        for match in md.WORKSPACE_REF_PATTERN.finditer(remainder):
            add(match.group(0), "citation", line_num)
    return edges


def path_token_edges(
    relpath: str,
    repo_root: Path,
    repo_name: str,
    known: set[str],
    form: str,
    skip: AbstractSet[tuple[str, str]] = frozenset(),
) -> list[dict]:
    """Heuristic edges from path-shaped tokens that resolve to in-scope files.

    The ``code-ref`` extractor for non-markdown files, and the ``prose-path``
    extractor for markdown (tokens in code spans and fences that the grammar
    treats as prose but a reading agent follows). A token is tried as written
    — source-relative or root-absolute — then as root-relative; tokens that
    resolve to nothing in scope are prose, not edges.
    """
    text = (repo_root / relpath).read_text(encoding="utf-8", errors="replace")
    edges = []
    for line_num, line in enumerate(text.splitlines(), 1):
        for match in PATH_TOKEN_PATTERN.finditer(line):
            raw = match.group(0)
            target, kind = resolve_target(raw, relpath, repo_name, repo_root)
            if kind != "internal":
                continue
            if target not in known:
                target = raw.partition("#")[0].lstrip("/")
                if target not in known:
                    continue
            if target == relpath or (relpath, target) in skip:
                continue
            edges.append(
                {
                    "source": relpath,
                    "target": target,
                    "kind": "internal",
                    "form": form,
                    "line": line_num,
                    "status": "ok",
                }
            )
    return edges


def bundle_edges(files: list[str]) -> list[dict]:
    """Structural edges: ``SKILL.md`` is the hub of its bundle directory."""
    hubs = {
        str(PurePosixPath(rel).parent): rel
        for rel in files
        if PurePosixPath(rel).name == "SKILL.md"
    }
    return [
        {
            "source": hub,
            "target": rel,
            "kind": "internal",
            "form": "bundle",
            "line": 0,
            "status": "ok",
        }
        for hub_dir, hub in hubs.items()
        for rel in files
        if rel != hub and rel.startswith(hub_dir + "/")
    ]


# --- queries -----------------------------------------------------------------


def reachability(nodes: dict[str, str], edges: list[dict], seeds: list[str]) -> dict:
    """Breadth-first reach from ``seeds`` along markdown edges, with distances.

    The spec's motivating query. An edge is walkable when its source is a
    markdown file, its target is an in-scope node, and it is not broken
    (``wrong-form`` still names a real file a reader can follow).
    """
    adjacency: dict[str, list[str]] = {}
    for edge in edges:
        if (
            edge["kind"] == "internal"
            and edge["status"] != "broken"
            and edge["source"].endswith(".md")
            and edge["target"] in nodes
        ):
            adjacency.setdefault(edge["source"], []).append(edge["target"])
    distance = {seed: 0 for seed in seeds if seed in nodes}
    queue = deque(distance)
    while queue:
        current = queue.popleft()
        for neighbor in adjacency.get(current, []):
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                queue.append(neighbor)
    unreached = sorted(rel for rel in nodes if rel not in distance)
    return {
        "seeds": sorted(seed for seed in seeds if seed in nodes),
        "reached": dict(sorted(distance.items(), key=lambda kv: (kv[1], kv[0]))),
        "reached_by_distance": dict(sorted(Counter(distance.values()).items())),
        "unreached_by_bucket": dict(
            Counter(nodes[rel] for rel in unreached).most_common()
        ),
        "unreached": unreached,
    }


def components(nodes: dict[str, str], edges: list[dict]) -> list[list[str]]:
    """Undirected components of concept+index nodes over formal edges.

    One component means the OKF bundle hangs together; more is
    fragmentation, and the spec calls it a finding.
    """
    core = {rel for rel, b in nodes.items() if b in CORE_BUCKETS}
    adjacency: dict[str, set[str]] = {rel: set() for rel in core}
    for edge in edges:
        if (
            edge["form"] in FORMAL_FORMS
            and edge["kind"] == "internal"
            and edge["source"] in core
            and edge["target"] in core
        ):
            adjacency[edge["source"]].add(edge["target"])
            adjacency[edge["target"]].add(edge["source"])
    seen: set[str] = set()
    result = []
    for start in sorted(core):
        if start in seen:
            continue
        component = []
        queue = deque([start])
        seen.add(start)
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        result.append(sorted(component))
    return sorted(result, key=len, reverse=True)


# --- orchestration -----------------------------------------------------------


def build_graph(repo_root: Path) -> dict:
    """Build the spec's machine artifact for the checkout at ``repo_root``.

    Returns the full document: nodes with buckets, typed edges, the
    ignored-pattern census, and the five query results.
    """
    repo_name = gitrepo.canonical_repo_name(repo_root)
    files = gitrepo.git_files(repo_root)
    known = set(files)
    nodes = {rel: bucket(rel, repo_root) for rel in files}

    edges: list[dict] = []
    for rel in files:
        if rel.endswith(".md"):
            found = markdown_edges(rel, repo_root, repo_name)
            found += path_token_edges(
                rel,
                repo_root,
                repo_name,
                known,
                "prose-path",
                skip={(e["source"], e["target"]) for e in found},
            )
            edges.extend(found)
        else:
            edges.extend(path_token_edges(rel, repo_root, repo_name, known, "code-ref"))
    edges.extend(bundle_edges(files))

    seeds = sorted(rel for rel, b in nodes.items() if b == "harness-session")
    touched = {e["source"] for e in edges if e["kind"] == "internal"}
    touched |= {e["target"] for e in edges if e["kind"] == "internal"}
    return {
        "repo": repo_name,
        "root": str(repo_root),
        "nodes": nodes,
        "edges": edges,
        "ignored": ignored_census(repo_root),
        "queries": {
            "census": {
                "nodes_by_bucket": dict(Counter(nodes.values()).most_common()),
                "edges_by_form": dict(Counter(e["form"] for e in edges).most_common()),
                "edges_by_status": dict(
                    Counter(e["status"] for e in edges).most_common()
                ),
            },
            "reachability": reachability(nodes, edges, seeds),
            "components": components(nodes, edges),
            "orphans": {rel: nodes[rel] for rel in sorted(known - touched)},
            "defects": [e for e in edges if e["status"] != "ok"],
        },
    }
