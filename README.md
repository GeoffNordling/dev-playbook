---
type: README
title: dev-playbook
description: The dev-playbook meta repo — workspace standards, the software factory definition, agent configuration, CLI tools, and reusable harness patterns
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

The top-level directories are listed in [`index.md`](/index.md).

> **`dotfiles/`** — after adding or removing files, run `dotfiles/bin/sync-dotfiles.sh` from the main checkout only; it relinks live `$HOME`, so it's a human step, never run from a per-issue worktree.

