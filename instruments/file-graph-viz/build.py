#!/usr/bin/env python3
"""Assemble the self-contained file-graph viz.

Inlines the vendored d3 bundle (`__D3__`) and the graph JSON (`__DATA__`)
into the template, producing a single `viz.html` that renders from file://
with no external requests. Regenerate the JSON first with
`scripts/file-graph -o instruments/file-graph-viz/file-graph.json .`.
"""

from pathlib import Path

here = Path(__file__).parent
tpl = (here / "viz.template.html").read_text()
d3 = (here / "d3.min.js").read_text()
data = (here / "file-graph.json").read_text().strip()

out = tpl.replace("__D3__", d3).replace("__DATA__", data)
assert "__D3__" not in out and "__DATA__" not in out, "placeholder not substituted"
(here / "viz.html").write_text(out)
print(f"wrote viz.html ({len(out):,} bytes)")
