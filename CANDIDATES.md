---
type: Candidate-List
title: Candidates
description: Uncommitted future work — described, not yet promoted to issues
---

# Candidates

## Sandboxing

- **Container fence for AFK nodes** — a headless node can be denied a tool
  outright but never confined to a directory, so unattended work has no
  filesystem boundary at all; a container would give it one. The open questions
  are in [sandboxing.md](/docs/sandboxing.md).

## Standards tooling

- **Skill mirror check** — the Harness card once claimed a
  `harness.skill-mirror` check that an authored skill under
  `dotfiles/dot-claude/skills/` matches its installed copy under
  `~/.claude/skills/`; no detector ever emitted it. Stow makes the two one
  tree, so the check is whether every link resolves and no stray copy sits
  beside it.
- **Slug a code span the way GitHub does** — `github_slug` in
  `src/dev_playbook/md.py` strips backticks before emphasis, so a heading
  holding `__init__` slugs to `initpy` where GitHub keeps the underscores.
  Protect code spans first, then run ref-lint over every anchor in the tree
  to see which ones the fix moves.
