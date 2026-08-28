---
type: Decision-Record
title: Retire Verbatim Skill Adoption
description: Adopt external skills by copying into the owned tree instead of installing vendored bytes — the ten adopted bundles become owned copies, three unused ones are deleted, and the skills CLI, lock file, and mirror symlinks retire
date: 2026-08-28
status: accepted
---

# Retire Verbatim Skill Adoption

Through [0020](/docs/decisions/0020-pocock-skills-sweep-2026-08.md), a
`verbatim` verdict meant an unowned install: the `skills` CLI wrote the bundle
into `dotfiles/.agents/skills/`, a lock file pinned its folder hash, a symlink
mirrored it into `dotfiles/dot-claude/skills/`, and every workspace gate
exempted the tree because the bytes were upstream's to write. The `no-more-slop`
branch made that untenable: its corpus requires every runbook to carry the edge
encoding, an encoding is an edit, and vendored bytes cannot be edited.

**Decision: adoption is by copy.** An adopting verdict copies the bundle into
`dotfiles/dot-claude/skills/`, where it is owned from the moment it lands —
subject to every workspace standard, free to drift from upstream, with later
upstream deltas folded in by editing the copy. The alternative — keep some
skills verbatim and accept model-generated chains for them, outside the
deterministic system — was rejected: one corpus, one contract.

What moved:

- The ten adopted mattpocock bundles (`codebase-design`, `diagnosing-bugs`,
  `domain-modeling`, `grilling`, `improve-codebase-architecture`, `prototype`,
  `research`, `wait-what`, `wayfinder`, `writing-for-agents`) became owned
  copies, byte-identical at the moment of copy.
- Three bundles were deleted rather than converted. `wizard`: nothing in the
  workspace references it, and owning it would put its `template.sh` — past
  the shell standard's glue-only boundary — on the workspace's own books.
  `marimo-batch` and `marimo-notebook`: adopted without a recorded ruling and
  referenced by nothing. The stale `pymc-modeling` ledger row — a skill with
  no ruling record — was dropped with them.
- The install machinery retired: the `skills` CLI, `.skill-lock.json`, the
  `dotfiles/.agents/` tree, the mirror symlinks and `sync-dotfiles` mirror
  step, and the gate exemptions for vendored trees — including the
  `EXTERNALLY_MANAGED_ROOTS` registry in `src/dev_playbook/external.py`,
  deleted outright since no vendored tree can exist under the new policy.
  `is_verbatim_doc` (`type: Reference` mirrors) is untouched.
- The shell standard's externally-managed exemption — added at 0020 for
  `wizard` — retired with the tree it exempted.

The ledger's verdict vocabulary keeps its four words; `verbatim` and `adapt`
now describe how the copy arrived, not a lock-tracked install. The sweep
(`pocock-sweep`) survives with one change of mechanism: rulings land as copies
and edits on the sweep branch, never as CLI installs on main.
