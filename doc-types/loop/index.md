---
okf_version: "0.1"
---

# doc-types/loop/ — index

The Loop doc-type: the document that drives a state toward a target
state — its definition, contract shape, encoding, and residual ledger.
No generated view lives here: a Loop's view is the Mermaid graph in its
own file, checked by `scripts/loopgen --check`.

- [Acts, Checks, and Yields](/doc-types/loop/contract-shape.md) — Loop's contract shape — acts, checks, and a set of yield conditions, iterated — in prose, one screen of pseudocode, and the graph every Loop is drawn as
- [Acts, Checks, and Yields Encoding](/doc-types/loop/encoding.md) — The layer below the shape — how a Loop's file writes its graph, its acts, its checks, and its yields for loopgen, and where the file sits
- [Loop](/doc-types/loop/definition.md) — What a loop is — a document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards — the family it serves, and where it lives
- [Loop Residual Ledger](/doc-types/loop/residual-ledger.md) — Loop's residual record — what acts, checks, and yields cannot express, one entry per Loop that has one
