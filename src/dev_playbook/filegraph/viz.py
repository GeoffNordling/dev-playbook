"""Assemble the self-contained file-graph viz from a built graph.

Inlines three things into the template, producing a single HTML file that
renders from file:// with no external requests:

- `__D3__`       — the vendored d3 bundle.
- `__DATA__`     — the graph JSON (nodes, edges, queries).
- `__CONTENTS__` — a {path: text} map of every node file's raw source, so the
  viewer can show a document's text on click. Read from the repo at build time.

The two JSON blobs have every `<` rewritten to its equivalent unicode escape
before insertion, so no substring can terminate the inline script early or trip
the `<!--`/`<script` double-escape trap; `<` only occurs inside JSON string
values, where the escape is equivalent. The trusted d3 bundle is injected as-is. All three placeholders
are substituted in a single pass, so an injected blob that itself contains a
placeholder token cannot be clobbered by a later substitution.

The template and the vendored d3 live in ``assets/`` beside this module;
``scripts/file-graph --html`` is the entry point.
"""

import json
import re
from pathlib import Path

ASSETS = Path(__file__).parent / "assets"
MAX_BYTES = 200_000  # a node file bigger than this is elided, not inlined


def safe(json_text: str) -> str:
    """Rewrite `<` to its unicode escape so injected JSON can't break out of <script>.

    `<` only ever appears inside JSON string values, where the escape is
    equivalent, so this neutralizes `</script>`, `<!--`, and `<script` at once
    without changing the parsed data.
    """
    return json_text.replace("<", "\\u003c")


def build_viz(graph: dict, repo_root: Path, output: Path) -> dict:
    """Render ``graph`` to a self-contained viz HTML at ``output``.

    Node file contents are read from ``repo_root`` (the checkout the graph was
    built over); the template and vendored d3 come from ``assets/``. Returns a
    summary dict — bytes written, files inlined, files elided.
    """
    tpl = (ASSETS / "viz.template.html").read_text()
    d3 = (ASSETS / "d3.min.js").read_text()
    data = json.dumps(graph)

    contents: dict[str, str | None] = {}
    elided = 0
    for rel in graph["nodes"]:
        raw = (repo_root / rel).read_bytes()
        if len(raw) > MAX_BYTES:
            contents[rel] = None
            elided += 1
            continue
        try:
            contents[rel] = raw.decode("utf-8")
        except UnicodeDecodeError:
            contents[rel] = None
            elided += 1

    substitutions = {
        "__D3__": d3,
        "__DATA__": safe(data),
        "__CONTENTS__": safe(json.dumps(contents)),
    }
    for placeholder in substitutions:
        if tpl.count(placeholder) != 1:
            raise SystemExit(
                f"template must contain {placeholder} exactly once, "
                f"found {tpl.count(placeholder)}"
            )
    # Single pass over the template: each placeholder is replaced at its one site
    # and the injected values are never re-scanned, so a blob that itself contains
    # another placeholder token can't be corrupted, and inlined file contents that
    # legitimately mention a token don't trip a post-substitution check.
    pattern = re.compile("|".join(re.escape(p) for p in substitutions))
    out = pattern.sub(lambda m: substitutions[m.group(0)], tpl)
    output.write_text(out)
    return {"bytes": len(out), "inlined": len(contents), "elided": elided}
