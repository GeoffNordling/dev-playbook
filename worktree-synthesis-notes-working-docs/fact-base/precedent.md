---
type: General-Sheet
title: Precedent
description: The fact base's prior art — typed property graphs from Tuple-Attribute and Rigi to Kythe and Glean, and the competitive pass that found no direct competitor
---

# Precedent

The prior art behind
[Fact Base](/worktree-synthesis-notes-working-docs/fact-base/fact-base.md):
the established shape it takes, and what the competitive research pass
of 2026-09-11 found. Speculative, per
[Fact Base Strand](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md).

## Terms

Fact base, extractor, and view are the set's words
([Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms));
receipt and schema are the strand's
([Terms](/worktree-synthesis-notes-working-docs/fact-base/ROOT.md#terms)).
This page defines none.

## The established shape

The shape is established: a typed property graph, facts extracted by
parsers with a source anchor on each fact, views that are only queries.
Holt's Tuple-Attribute language and Rigi in the 1990s, Kythe and Glean
today, C4 and Structurizr for the model-then-views discipline. The
theory applies; the software does not. Those indexers feed on compiler
output for compiled languages at monorepo scale, and this fact base is
a few hundred markdown files with a schema this repo owns. What was
improvised here: the extractable-versus-declared split, the exact row
shape, buckets and directories as nodes, and the extractor names. None of
those choices is load-bearing.

## No direct competitor

A competitive research pass on 2026-09-11
([full report](https://claude.ai/chat/255df4d9-27b8-4a11-9a3e-f6cb54b04ff6))
found no direct competitor. Roughly thirty candidates were checked, and
each covers one to three of the fact base's four load-bearing ideas,
never all four: one typed graph over both code and agent-instruction
prose, a receipt on every row, views as pure selections, and contracts
declared inside the instruction markdown itself. The nearest neighbors
are 2026 research prototypes built for agent systems, AgentFlow's Agent
Dependency Graph and the Repository Intelligence Graph, but both extract
from source code, not markdown, and neither carries receipts. The
nearest markdown-side precedent for the chain's span grammar is Gherkin,
a controlled natural language parsed deterministically to an AST; no
tool combines that with graph extraction.

## Acronyms

- **AST** — Abstract Syntax Tree.
