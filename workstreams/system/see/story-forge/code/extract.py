#!/usr/bin/env python3
"""Extract the story-forge stories slice into fact-base rows.

The simulated extractor, written once by a Sonnet agent. Every row traces to extractor name + line number. No judgment calls beyond
literal parsing of the file shapes observed by hand in this repo.
"""

import json
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

REPO = Path.home() / "workspace" / "story-forge"
# The rows carry unredacted descriptions, so they are written outside the repo.
OUT = Path(sys.argv[1])

nodes = []
edges = []
notes = []  # facts the format could not hold: (path, line, note)


def relpath(p: Path) -> str:
    """Return a path relative to the story-forge root."""
    return str(p.relative_to(REPO))


def read_lines(p: Path):
    """Read a file, keeping line endings."""
    with open(p, encoding="utf-8") as f:
        return f.readlines()  # keep \n so we can detect trailing newline etc.


# ---------------------------------------------------------------------------
# 1. Story nodes + their frontmatter-derived edges (tagged, related, supplements)
# ---------------------------------------------------------------------------

story_dir = REPO / "stories"
story_files = sorted([p for p in story_dir.glob("*.md") if p.name != "index.md"])
story_ids = {p.stem for p in story_files}  # bare ids, e.g. "spec-tools"

FM_KV = re.compile(r"^([A-Za-z_]+):\s*(.*)$")


def parse_bracket_list(val: str):
    """Parse a YAML flow list such as [a, b]."""
    val = val.strip()
    if val == "null":
        return None
    assert val.startswith("[") and val.endswith("]"), (
        f"unexpected list literal: {val!r}"
    )
    inner = val[1:-1].strip()
    if inner == "":
        return []
    return [x.strip() for x in inner.split(",")]


def parse_bool(val: str):
    """Parse a YAML boolean."""
    val = val.strip()
    assert val in ("true", "false"), f"unexpected bool literal: {val!r}"
    return val == "true"


story_attrs_by_id = {}  # id -> attrs dict, for later cross-checks

for p in story_files:
    lines = read_lines(p)
    rel = relpath(p)
    stem = p.stem
    total_lines = len(lines)

    # frontmatter: line 1 is '---', find closing '---'
    assert lines[0].rstrip("\n") == "---", f"{rel}: line 1 not '---'"
    close_idx = None
    for i in range(1, len(lines)):
        if lines[i].rstrip("\n") == "---":
            close_idx = i  # 0-indexed line index of closing '---'
            break
    assert close_idx is not None, f"{rel}: no closing frontmatter fence"

    fm = {}  # key -> (value_str, line_no (1-indexed))
    for i in range(1, close_idx):
        raw = lines[i].rstrip("\n")
        m = FM_KV.match(raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        fm[key] = (val, i + 1)  # 1-indexed line number

    title = fm["title"][0]
    description = fm["description"][0]
    status = fm["status"][0]
    tags_line = fm["tags"][1]
    tags = parse_bracket_list(fm["tags"][0])
    resume_eligible = parse_bool(fm["resume_eligible"][0])
    leadership_story = parse_bool(fm["leadership_story"][0])
    supp_line = fm["supplemental_context"][1]
    supp_val = fm["supplemental_context"][0].strip()
    supplemental_context = None if supp_val == "null" else supp_val
    related_line = fm["related_stories"][1]
    related_stories = parse_bracket_list(fm["related_stories"][0])

    attrs = {
        "stem": stem,
        "title": title,
        "description": description,
        "status": status,
        "tags": tags,
        "resume_eligible": resume_eligible,
        "leadership_story": leadership_story,
        "supplemental_context": supplemental_context,
        "related_stories": related_stories,
        "total_lines": total_lines,
    }
    story_attrs_by_id[stem] = attrs

    nodes.append(
        {
            "id": rel,
            "type": "Story",
            "provenance": "declared",
            "extractor": "frontmatter",
            "line": 1,
            "attrs": attrs,
        }
    )

    # tagged edges
    for tag in tags:
        target = f"tag:{tag}"
        edges.append(
            {
                "source": rel,
                "relation": "tagged",
                "target": target,
                "order": None,
                "condition": None,
                "detail": None,  # filled after registry known
                "extractor": "frontmatter",
                "line": tags_line,
            }
        )

    # related edges
    if related_stories is not None:
        for rid in related_stories:
            target = f"stories/{rid}.md"
            missing = rid not in story_ids
            edges.append(
                {
                    "source": rel,
                    "relation": "related",
                    "target": target,
                    "order": None,
                    "condition": None,
                    "detail": "missing" if missing else None,
                    "extractor": "frontmatter",
                    "line": related_line,
                }
            )

    # supplements edges
    if supplemental_context is not None:
        target_path = supplemental_context  # as written, e.g. "/career/.../x.md"
        resolved = REPO / target_path.lstrip("/")
        missing = not resolved.exists()
        edges.append(
            {
                "source": rel,
                "relation": "supplements",
                "target": target_path,
                "order": None,
                "condition": None,
                "detail": "missing" if missing else None,
                "extractor": "frontmatter",
                "line": supp_line,
            }
        )

    # ------------------------------------------------------------------
    # Sections (H2s) + contains edges
    # ------------------------------------------------------------------
    heading_idxs = []  # 0-indexed line index of each H2
    for i in range(close_idx + 1, len(lines)):
        raw = lines[i].rstrip("\n")
        if raw.startswith("## ") and not raw.startswith("### "):
            heading_idxs.append(i)

    for order, hidx in enumerate(heading_idxs, start=1):
        heading_text = lines[hidx].rstrip("\n")[3:].strip()
        line_no = hidx + 1
        body_start = hidx + 1
        body_end = (
            heading_idxs[order] if order < len(heading_idxs) else len(lines)
        )  # exclusive, 0-indexed
        body_raw_lines = [lines[i].rstrip("\n") for i in range(body_start, body_end)]
        body_lines_count = sum(1 for ln in body_raw_lines if ln.strip() != "")
        bullets = sum(1 for ln in body_raw_lines if re.match(r"^- ", ln))
        h3_count = sum(1 for ln in body_raw_lines if ln.startswith("### "))
        body_stripped_joined = "\n".join(
            ln.strip() for ln in body_raw_lines if ln.strip() != ""
        )
        is_none = body_stripped_joined.strip() == "None."

        slug = heading_text.lower().replace(" ", "-")
        section_id = f"{rel}#{slug}"

        nodes.append(
            {
                "id": section_id,
                "type": "Section",
                "provenance": "declared",
                "extractor": "headings",
                "line": line_no,
                "attrs": {
                    "heading": heading_text,
                    "order": order,
                    "body_lines": body_lines_count,
                    "bullets": bullets,
                    "is_none": is_none,
                    "h3_count": h3_count,
                },
            }
        )

        edges.append(
            {
                "source": rel,
                "relation": "contains",
                "target": section_id,
                "order": order,
                "condition": None,
                "detail": None,
                "extractor": "headings",
                "line": line_no,
            }
        )

# ---------------------------------------------------------------------------
# 2. Tag nodes from stories/tags.yaml
# ---------------------------------------------------------------------------

tags_yaml = story_dir / "tags.yaml"
tag_lines = read_lines(tags_yaml)
tag_registry = {}  # name -> (list_name, order, comment, line)

current_list = None
order_counters = {"role-specific": 0, "always-on": 0}
ENTRY_RE = re.compile(r"^\s*-\s*(\S+)(.*)$")

for i, raw in enumerate(tag_lines):
    line = raw.rstrip("\n")
    line_no = i + 1
    stripped = line.strip()
    if stripped == "role-specific:":
        current_list = "role-specific"
        continue
    if stripped == "always-on:":
        current_list = "always-on"
        continue
    if current_list is None:
        continue
    # skip pure-comment lines (section headers like "# Technical Domains") and blank lines
    if stripped == "" or stripped.startswith("#"):
        continue
    m = ENTRY_RE.match(line)
    if not m:
        continue
    name = m.group(1)
    rest = m.group(2)
    comment = None
    if "#" in rest:
        comment = rest.split("#", 1)[1].strip()
    order_counters[current_list] += 1
    order = order_counters[current_list]
    tag_registry[name] = (current_list, order, comment, line_no)

    nodes.append(
        {
            "id": f"tag:{name}",
            "type": "Tag",
            "provenance": "declared",
            "extractor": "yaml",
            "line": line_no,
            "attrs": {
                "list": current_list,
                "order": order,
                "comment": comment,
            },
        }
    )

# backfill tagged-edge detail now that registry is known
for e in edges:
    if e["relation"] == "tagged":
        tag_name = e["target"].split(":", 1)[1]
        if tag_name not in tag_registry:
            e["detail"] = "unregistered"

# ---------------------------------------------------------------------------
# 3. Repo-wide scan: mdlinks -> Story ("links" edges), and collect all .md files
# ---------------------------------------------------------------------------

all_md_files = sorted([p for p in REPO.rglob("*.md") if ".git" not in p.parts])

LINK_RE = re.compile(r"\]\(/stories/([A-Za-z0-9_-]+)\.md(?:#[^)]*)?\)")

link_edges = []  # (source_rel, line_no, target_id)
for p in all_md_files:
    lines = read_lines(p)
    rel = relpath(p)
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        for m in LINK_RE.finditer(line):
            sid = m.group(1)
            if sid in story_ids:
                link_edges.append((rel, i + 1, f"stories/{sid}.md"))

for src, line_no, target in link_edges:
    edges.append(
        {
            "source": src,
            "relation": "links",
            "target": target,
            "order": None,
            "condition": None,
            "detail": None,
            "extractor": "mdlink",
            "line": line_no,
        }
    )

# ---------------------------------------------------------------------------
# 4. Projections: frontmatter `sources:` list -> "sources" edges
# ---------------------------------------------------------------------------

projection_files = []
for p in all_md_files:
    lines = read_lines(p)
    if len(lines) >= 2 and lines[0].rstrip("\n") == "---":
        for i in range(1, len(lines)):
            ln = lines[i].rstrip("\n")
            if ln == "---":
                break
            if ln == "sources:":
                projection_files.append((p, lines, i))
                break

sources_edges = []
for p, lines, sources_line_idx in projection_files:
    rel = relpath(p)
    i = sources_line_idx + 1
    while i < len(lines):
        raw = lines[i].rstrip("\n")
        if raw == "---" or (
            raw.strip() and not raw.startswith(" ") and not raw.startswith("-")
        ):
            break
        m = re.match(r"^\s*-\s*(\S+)\s*$", raw)
        if m:
            sid = m.group(1)
            target = f"stories/{sid}.md"
            missing = sid not in story_ids
            sources_edges.append((rel, i + 1, target, missing))
            i += 1
            continue
        if raw.strip() == "":
            break
        i += 1

for src, line_no, target, missing in sources_edges:
    edges.append(
        {
            "source": src,
            "relation": "sources",
            "target": target,
            "order": None,
            "condition": None,
            "detail": "missing" if missing else None,
            "extractor": "frontmatter",
            "line": line_no,
        }
    )

# ---------------------------------------------------------------------------
# 5. Resume files: HTML-comment "cites" edges
# ---------------------------------------------------------------------------

resume_files = []
for p in all_md_files:
    lines = read_lines(p)
    if (
        len(lines) >= 2
        and lines[0].rstrip("\n") == "---"
        and lines[1].rstrip("\n") == "type: Resume"
    ):
        resume_files.append(p)

CITE_BULLET_RE = re.compile(r"<!--\s*stories:\s*([^>]+?)\s*-->")
CITE_UNASSIGNED_RE = re.compile(
    r"<!--\s*unassigned stories \(resume-eligible\):\s*([^>]+?)\s*-->"
)

cites_edges = []
for p in resume_files:
    rel = relpath(p)
    lines = read_lines(p)
    for i, raw in enumerate(lines):
        line = raw.rstrip("\n")
        mu = CITE_UNASSIGNED_RE.search(line)
        if mu:
            ids = [x.strip() for x in mu.group(1).split(",")]
            for sid in ids:
                cites_edges.append((rel, i + 1, sid, "unassigned"))
            continue  # unassigned line is distinct from a bullet-style "stories:" comment
        mb = CITE_BULLET_RE.search(line)
        if mb:
            ids = [x.strip() for x in mb.group(1).split(",")]
            for sid in ids:
                cites_edges.append((rel, i + 1, sid, "bullet"))

for src, line_no, sid, detail in cites_edges:
    target = f"stories/{sid}.md"
    missing = sid not in story_ids
    edges.append(
        {
            "source": src,
            "relation": "cites",
            "target": target,
            "order": None,
            "condition": None,
            "detail": detail if not missing else f"{detail}+missing",
            "extractor": "html-comment",
            "line": line_no,
        }
    )
    if missing:
        notes.append(
            (src, line_no, f"cites edge target '{sid}' is not among the 32 story ids")
        )

# ---------------------------------------------------------------------------
# 6. Node type 4: every OTHER file that is the SOURCE of a sources/links/cites edge
# ---------------------------------------------------------------------------

other_file_sources = set()
for src, _, _, _ in sources_edges:
    other_file_sources.add(src)
for src, _, _ in link_edges:
    other_file_sources.add(src)
for src, _, _, _ in cites_edges:
    other_file_sources.add(src)

# exclude files that are already Story nodes
story_rel_paths = {relpath(p) for p in story_files}
other_file_sources = {s for s in other_file_sources if s not in story_rel_paths}

for rel in sorted(other_file_sources):
    p = REPO / rel
    lines = read_lines(p)
    if len(lines) >= 1 and lines[0].rstrip("\n") == "---":
        close_idx = None
        for i in range(1, len(lines)):
            if lines[i].rstrip("\n") == "---":
                close_idx = i
                break
        type_val = None
        if close_idx is not None:
            for i in range(1, close_idx):
                m = FM_KV.match(lines[i].rstrip("\n"))
                if m and m.group(1) == "type":
                    type_val = m.group(2).strip()
                    break
        if type_val is not None:
            nodes.append(
                {
                    "id": rel,
                    "type": type_val,
                    "provenance": "declared",
                    "extractor": "frontmatter",
                    "line": 1,
                    "attrs": {},
                }
            )
            continue
    # no frontmatter or no type key -> File / fs
    nodes.append(
        {
            "id": rel,
            "type": "File",
            "provenance": "declared",
            "extractor": "fs",
            "line": None,
            "attrs": {},
        }
    )

# ---------------------------------------------------------------------------
# Assemble envelope
# ---------------------------------------------------------------------------

envelope = {
    "envelope": 1,
    "kind": "fact-base",
    "kind_version": 0,
    "title": "fact-base, slice: stories/*.md and every node that cites a story",
    "subject": None,
    "stamp": {
        "commit": "3af571a9b14be7e2d21f02e45906bcdb80c2d4b0",
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generator": "simulated by hand (sonnet agent); no module exists",
    },
    "payload": {"nodes": nodes, "edges": edges},
}

OUT.write_text(json.dumps(envelope, indent=2) + "\n")

# ---------------------------------------------------------------------------
# Report-support computations (printed, not written into the JSON)
# ---------------------------------------------------------------------------


node_type_counts = Counter(n["type"] for n in nodes)
edge_rel_counts = Counter(e["relation"] for e in edges)

print("NODE COUNTS BY TYPE")
for t, c in sorted(node_type_counts.items()):
    print(f"  {t}: {c}")

print("\nEDGE COUNTS BY RELATION")
for r, c in sorted(edge_rel_counts.items()):
    print(f"  {r}: {c}")

print("\nMISSING / UNREGISTERED TARGETS")
for e in edges:
    if e.get("detail") and ("missing" in e["detail"] or e["detail"] == "unregistered"):
        print(
            f"  {e['relation']}: {e['source']}:{e['line']} -> {e['target']} [{e['detail']}]"
        )

print("\nASYMMETRIC related PAIRS")
related_pairs = set()
for e in edges:
    if e["relation"] == "related":
        src_id = e["source"]  # e.g. "stories/x.md"
        tgt_id = e["target"]
        related_pairs.add((src_id, tgt_id))
checked = set()
for a, b in related_pairs:
    if (a, b) in checked:
        continue
    checked.add((a, b))
    if (b, a) not in related_pairs:
        print(f"  {a} -> {b} (no reverse edge {b} -> {a})")

print("\nOTHER FILE NODES (type 4)")
for rel in sorted(other_file_sources):
    print(f"  {rel}")

print("\nSTORY COUNT:", len(story_files))
print("TAG REGISTRY COUNT:", len(tag_registry))

print("\nNOTES (auto-flagged anomalies)")
for n in notes:
    print(f"  {n}")
