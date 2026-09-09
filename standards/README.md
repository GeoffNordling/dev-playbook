---
type: README
title: Standards
description: Cross-project engineering standards that apply to every repository in the workspace
---

# Standards

Cross-project engineering standards that apply to all repositories in the
workspace.

## How this directory reads

Every directory here except `references/` is one standard. Its `card.md`
is the **standard card**: the four-cell record — define, audit, enforce,
adopt — locating the standard's contract, checkers, gates, and adoption
helpers. Beside the card sit the Standards its Define cell points at
(`build/skeleton.md` beside `build/card.md`), any templates, and the
guides that serve them. The rule is the tree: **one directory, one
standard**; `references/` holds vendored mirrors. The contract behind the
cards themselves is the Standard-Card doc-type
([doc-types/standard-card/](/doc-types/standard-card/index.md)).

## Rules live here; their subjects live elsewhere

Each standard files its *rules* in this directory; the population it
governs lives wherever that population naturally lives:

| Rules | Governed population |
|---|---|
| `build/` | every repo tree in the workspace |
| `harness/` | the harness files in every repo |
| `standard/` | the cards in this very directory |

The last row is the one loop: the meta-standard's population is the cards
themselves, which tempts a reader to mistake this directory for a
governance hierarchy. It is not — everything here is under the
meta-standard **in form only** (the card format), while each standard's
substance governs its own population, one rung down. A rejection always
cites exactly one rung up: a bad Makefile is rejected by `build/`, never by
`standard/`.

The full catalog is [`index.md`](/standards/index.md).
