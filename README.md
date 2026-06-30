---
type: README
title: dev-playbook
description: The dev-playbook meta repo — workspace standards, workflow definitions, agent configuration, CLI tools, and reusable harness patterns
---

# dev-playbook

Standards and tools for djinn wrangling across a multi-repo workspace.

> *"Often, when we find a recurring problem, something that happens over and over again, we pull the team together, ask them to try harder, do better – essentially, we ask for good intentions. This rarely works… When you are asking for good intentions, you are not asking for a change… because people already had good intentions. But if good intentions don't work, what does? Mechanisms work."*  
> — Amazon leadership principles
>
> *"…to succeed in executing spontaneous and unconscious technique, it is necessary to train in it in a highly conscious fashion."*  
> — Miyamoto Musashi
>
> *"A little bit of slope makes up for a lot of intercept."*  
> — John Osterhaus, Stanford Lecture

## What belongs here

- Cross-project standards and conventions
- Formal standards governing the workspace
- Agent configuration (skills, rules, settings)
- CLI tools and shared libraries for workspace automation

## What does NOT belong here

- Project-specific documentation — put it in that project's repo
- Application code

## The workspace

All repos live under a single root directory: `~/workspace/`. One meta repo governs everything else: **dev-playbook** (this repo).

## What's here

One row per top-level directory. Follow the linked index for the contents of each.

| Directory | Purpose |
|-----------|---------|
| [`standards/`](standards/README.md) | Cross-project engineering standards and conventions. |
| [`workflow/`](workflow/README.md) | How an idea moves from intake to shipped code — the state machine, gates, and agent-autonomy decisions. |
| [`protocols/`](protocols/README.md) | Augmented skills that decompose a complex problem formally before executing it (e.g. Align, Map, Execute). |
| `dotfiles/` | Agent configuration (skills, rules, settings), Stow-symlinked into `$HOME`. Run `dotfiles/bin/sync-dotfiles.sh` after adding or removing files — from the main checkout only; it relinks live `$HOME`, so it's a human step, never run from a per-issue worktree. |
| [`tools/`](tools/README.md) | CLI utilities for workspace automation. |
| [`harness-recipes/`](harness-recipes/README.md) | Reusable patterns for getting leverage out of the Claude Code harness. |
| `docs/` | Supplementary documentation and architecture decision records (`docs/adr/`). |

