#!/usr/bin/env python3
"""Generate this repo's file-graph.json for the viz, seeded on the real CLAUDE.md.

Two caller-scope choices layered on the instrument's standard output:

1. Seed. The instrument's default seed set is the whole `harness-session`
   bucket (scripts/file-graph). The motivating question is narrower — "what
   can an agent that reads only the central, harness-injected CLAUDE.md
   reach?" — so the single seed is the repo root `CLAUDE.md`. The
   `dotfiles/dot-claude/` copies are source for what stow links into
   ~/.claude/, not files injected because you opened this repo, so they are
   deliberately not seeds.

2. Scope. This viz's own scaffolding (`instruments/file-graph-viz/`) is
   excluded: the vendored minified d3 alone spawns hundreds of bogus
   code-ref edges, and the generated artifacts are noise. The subject is
   dev-playbook, not the lens we view it through. Queries are recomputed over
   the filtered graph so census/reachability/components/orphans/defects stay
   consistent.

Run from anywhere; writes file-graph.json beside this script.
"""

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dev_playbook import filegraph  # noqa: E402

SEED = "CLAUDE.md"
EXCLUDE = "instruments/file-graph-viz/"

graph = filegraph.build_graph(REPO_ROOT)

nodes = {r: b for r, b in graph["nodes"].items() if not r.startswith(EXCLUDE)}
edges = [
    e
    for e in graph["edges"]
    if not e["source"].startswith(EXCLUDE)
    and not (e["kind"] == "internal" and e["target"].startswith(EXCLUDE))
]
graph["nodes"] = nodes
graph["edges"] = edges
graph["queries"] = filegraph.compute_queries(nodes, edges, [SEED])

out = Path(__file__).parent / "file-graph.json"
out.write_text(json.dumps(graph, indent=1) + "\n")
reach = graph["queries"]["reachability"]
print(
    f"wrote {out.name}: {len(nodes)} nodes, {len(edges)} edges, "
    f"seed={SEED!r}, {len(reach['reached'])} reached, {len(reach['unreached'])} unreached"
)
