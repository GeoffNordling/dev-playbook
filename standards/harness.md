---
type: Standard-Card
title: Harness Files
description: Governs how the files Claude Code loads are written — a CLAUDE.md's content and a runbook's format
---

# Harness Files

Governs how the files Claude Code loads are written — a CLAUDE.md's
content and a runbook's format. Which files the harness loads, and
what it does with each, is the registry
[Claude Code Files](/standards/harness/files.md); the craft behind any
document an agent consumes is
[Writing for Agents](/standards/harness/writing-for-agents.md), read to
write one. The voice every harness-loaded file speaks in is the
[Prose](/standards/prose.md) card's. Claude Code is the only harness in
use.

## Define

- [CLAUDE.md Content](/standards/harness/claude-content.md) — a
  `CLAUDE.md` at any scope: no frontmatter, operational content, one
  scope per rule, and the two sections and required rules of the global
  source in dev-playbook
- [Runbook Conventions](/standards/harness/runbook-conventions.md) — a
  skill bundle or an agent definition: location, front matter, the
  description, model and effort, the H1, completion criteria, the chain,
  and the rules each kind adds

## Audit

- [harness-files-lint](/scripts/harness-files-lint) — every skill bundle
  and agent definition under a repo's runbook roots: the front matter's
  parse and closed vocabulary (`harness.parse`, `harness.front-matter`,
  `harness.required-field`, `harness.unknown-field`); the name's form and
  its match to the bundle directory or file stem (`harness.name-format`,
  `harness.name-match`); the description's type, length, sentence count,
  and trigger sentence (`harness.description-type`,
  `harness.description-length`, `harness.description-sentences`,
  `harness.description-trigger`); the values of `model`, `effort`,
  `disable-model-invocation`, `arguments`, and `tools`
  (`harness.model-value`, `harness.effort-value`, `harness.dmi-type`,
  `harness.arguments-format`, `harness.tools-format`); the body's opening
  H1 (`harness.body-h1`); and the depth of `references/`
  (`harness.references-depth`). In dev-playbook only, the global
  CLAUDE.md source's two sections and required rules
  (`harness.global-claude-shape`, `harness.global-claude-rules`)

No detector reaches Operational scope, One scope, One rule per heading,
Location, Bundle layout, Interactive skills inherit, Tool fields, the
placeholder half of Arguments, Steps end on a completion criterion, or
Carries its chain: a reviewer cites them. SKILL.md under 500 lines draws
an advisory from harness-files-lint with no rule id.

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — its published `playbook-lint` hook dispatches to both harness-files-lint
  and prose-lint at the **commit gate** in every repo's suite;
  harness-files-lint no-ops where a repo authors no runbooks

## Adopt

- [runbook-creator](/dotfiles/dot-claude/skills/runbook-creator/SKILL.md)
  — the scaffold: it reads both Standards end-to-end, interviews the user
  for every front matter field, and writes a conforming skill bundle or
  agent definition; invoke it as /runbook-creator
