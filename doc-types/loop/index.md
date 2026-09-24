---
okf_version: "0.1"
---

# doc-types/loop/ — index

The Loop doc-type: the document that drives a state toward a target
state — its definition, contract shape, encoding, and residual ledger.
No generated view lives here: a Loop's view is the Mermaid graph in its
own file.

- [Acts, Verifications, and Yields](/doc-types/loop/contract-shape.md) — Loop's contract shape — acts, verifications, and yields, peers ordered by the graph, iterated to drive a workstream — in prose, and the graph every Loop is drawn as
- [Acts, Verifications, and Yields Encoding](/doc-types/loop/encoding.md) — The layer below the shape — how a Loop's file writes its graph, its acts, its verifications, and its yields so a check can read them, and where the file sits
- [Loop](/doc-types/loop/definition.md) — What a loop is — a document that drives a state toward a target state by iteratively taking prescribed actions and validating against prescribed standards — its four verbs, the family it serves, and where it lives
- [Loop Residual Ledger](/doc-types/loop/residual-ledger.md) — Loop's residual record — what acts, verifications, and yields cannot express, one entry per Loop that has one
