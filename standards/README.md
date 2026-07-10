---
type: README
title: Standards
description: Cross-project engineering standards that apply to every repository in the workspace
---

# Standards

Cross-project engineering standards that apply to all repositories in the
workspace.

## How this directory reads

Every flat `.md` here (besides this README and `index.md`) is a **standard
card**: the four-cell record — define, audit, enforce, adopt — locating one
standard's contract, checkers, gates, and adoption helpers. Every directory
holds content the cards point into: a standard's contract prose (`build/`
behind `build.md`), templates, or vendored references. The rule is the
tree: **flat = card, directory = content**. The contract behind the cards
themselves is [Standards and Standard Cards](/standards/standard/format.md).

## Rules live here; their subjects live elsewhere

Each standard files its *rules* in this directory; the population it
governs lives wherever that population naturally lives:

| Rules | Governed population |
|---|---|
| `build/` | every repo tree in the workspace |
| `claude-code/` | the harness files in every repo |
| `instrument/` | the specs in `instruments/` |
| `standard/` | the cards in this very directory |

The last row is the one loop: the meta-standard's population is the cards
themselves, which tempts a reader to mistake this directory for a
governance hierarchy. It is not — everything here is under the
meta-standard **in form only** (the card format), while each standard's
substance governs its own population, one rung down. A rejection always
cites exactly one rung up: a bad Makefile is rejected by `build/`, never by
`standard/format.md`; an unspecced device by `instrument/format.md`, never
by a datasheet spec.

The full catalog is [`index.md`](/standards/index.md).
