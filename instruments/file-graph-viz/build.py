#!/usr/bin/env python3
"""Assemble the self-contained file-graph viz.

Inlines three things into the template, producing a single `viz.html` that
renders from file:// with no external requests:

- `__D3__`       — the vendored d3 bundle.
- `__DATA__`     — the graph JSON (nodes, edges, queries).
- `__CONTENTS__` — a {path: text} map of every node file's raw source, so the
  viewer can show a document's text on click. Read from the repo at build time.

Any injected text is `</`-escaped to `<\\/` before insertion so a file that
itself contains `</script>` cannot terminate the inline script early. This only
touches the injected strings, never the template's own tags.

Regenerate the JSON first with `python3 gen-graph.py`.
"""

import json
from pathlib import Path

here = Path(__file__).parent
root = here.resolve().parents[1]
MAX_BYTES = 200_000  # a node file bigger than this is elided, not inlined


def safe(text: str) -> str:
    """Neutralize `</script>` (and any `</…`) inside injected script text."""
    return text.replace("</", "<\\/")


tpl = (here / "viz.template.html").read_text()
d3 = (here / "d3.min.js").read_text()
data = (here / "file-graph.json").read_text().strip()
graph = json.loads(data)

contents: dict[str, str | None] = {}
elided = 0
for rel in graph["nodes"]:
    raw = (root / rel).read_bytes()
    if len(raw) > MAX_BYTES:
        contents[rel] = None
        elided += 1
        continue
    try:
        contents[rel] = raw.decode("utf-8")
    except UnicodeDecodeError:
        contents[rel] = None
        elided += 1

out = (
    tpl.replace("__D3__", d3)
    .replace("__DATA__", safe(data))
    .replace("__CONTENTS__", safe(json.dumps(contents)))
)
assert not any(p in out for p in ("__D3__", "__DATA__", "__CONTENTS__")), (
    "placeholder not substituted"
)
(here / "viz.html").write_text(out)
print(
    f"wrote viz.html ({len(out):,} bytes) — "
    f"{len(contents)} files inlined, {elided} elided"
)
