---
type: Guide
title: Machines
description: The machines the workspace runs on — one Fedora primary and two Windows/WSL secondaries — and what differs between them
---

# Machines

The workspace runs on three machines under one user. Nearly all work happens on
the primary; the secondaries exist so the workspace is reachable from the
Windows side of the same hardware.

| Machine | Role | Notes |
|---|---|---|
| Fedora | **primary** | Dual-booted on the framework laptop. Air-gapped by intent — it is where development happens. |
| Windows 11 desktop | secondary | Ubuntu WSL guest. |
| Windows 11 framework laptop | secondary | Ubuntu WSL guest; the other half of the primary's hardware. |

The two secondaries are kept identical and share one configuration, so
everything below treats them as a single machine key, `wsl`. Fedora's key is
`fedora`.

## What differs

Machine differences are held in exactly two places, both named by machine key:

- `dotfiles/settings/<machine>.json` — the Claude Code settings that cannot be
  shared. `~/.claude/settings.json` is generated from `base.json` plus this
  fragment, because Claude Code reads one user-scope settings file and offers
  no local override layer to hold the remainder.
- `dotfiles/.bashrc.d/machine-env.sh` — the environment each machine needs,
  branching at runtime rather than by generated file.

Everything else is shared, and a difference that appears anywhere else is a
bug.

## What does not run on a secondary

Two checks depend on state that is local to a machine rather than present in
the repository, so on a secondary they would report the environment as a defect
in the code. Both are skipped there, and both announce the skip on every run.

- **Judgments.** The cache-gate's seen-set lives in `~/.cache/skipcache` and is
  filled by a `judgments-sweep` run. Judgments are neither installed nor
  ever expected to run on a secondary; `SKIP_JUDGMENTS=1` turns each into a
  named pytest skip, and `NO_JUDGMENT_CACHE=1` keeps the push gate from
  checking the cache either ([make.md](/standards/build/make.md)).
- **`ref-lint`.** Cross-repo Citations resolve only where the cited repo is
  cloned, and a secondary deliberately carries only some of the workspace's
  repos. `SKIP=ref-lint` stands the detector down.

The primary carries every repo and runs both, so nothing goes permanently
unchecked — it is checked on the machine that can check it. Which gates this
affects is recorded in
[enforcement.md](/standards/build/enforcement.md).
