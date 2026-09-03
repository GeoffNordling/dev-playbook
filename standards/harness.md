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
  and agent definition under a repo's runbook roots: the front matter, the
  name, the description, model and effort, the body's H1, and the depth of
  `references/`. In dev-playbook only, the global CLAUDE.md source's two
  sections and required rules

Both Standards draw the coverage line themselves: a rule names the
`harness.*` id that checks it, and a rule that names none has no
detector, so a reviewer checks it. `SKILL.md` under 500 lines draws an
advisory with no rule id.

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
