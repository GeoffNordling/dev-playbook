---
type: General-Sheet
title: Machines
description: The machines the workspace runs on — one Fedora primary and two Windows/WSL secondaries — and what differs between them
---

# Machines

The workspace runs on the machines below, under one user. Nearly all work
happens on the primary; the secondaries exist so the workspace is reachable
from the Windows side of the same hardware. Hardware and OS facts belong to
sysadmin-playbook's
[machines doc](~/workspace/sysadmin-playbook/docs/machines.md); this file
records only what the workspace does per machine key.

| Machine | Role | Notes |
|---|---|---|
| Fedora | **primary** | Dual-booted on the framework laptop. BitLocker keeps the Windows partition unreadable from Fedora, so the two halves share hardware but not data. It is where development happens. |
| Windows 11 desktop | secondary | Ubuntu WSL guest. |
| Windows 11 framework laptop | secondary | Ubuntu WSL guest; the other half of the primary's hardware. |

The secondaries are kept identical and share one configuration, so
everything below treats them as a single machine key, `wsl`. Fedora's key is
`fedora`.

## What differs

Machine differences branch at runtime, keyed on the host:

- Claude Code settings are one shared file,
  `dotfiles/dot-claude/settings.json`, stowed as `~/.claude/settings.json` on
  every machine. Hooks that only make sense on one machine detect the host themselves and exit quietly
  elsewhere, so the settings file never needs a per-machine variant.
- `dotfiles/.bashrc.d/machine-env.sh` — the environment each machine needs,
  branching at runtime the same way.

Everything else is shared, and a difference that appears anywhere else is a
bug.

## What does not run on a secondary

Checks that depend on state local to a machine, rather than present in the
repository, would report the environment as a defect in the code when run on
a secondary. They are skipped there, and each announces the skip on every
run.

- **Judgments.** The seen-set lives in `~/.cache/skipcache`, filled by
  [`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
  runs — the cache is local to the primary, so the sweep
  is a primary-machine activity. Judges never run on a secondary;
  `SKIP_JUDGMENTS=1` turns each gated judgment into a named pytest skip,
  and `NO_JUDGMENT_CACHE=1` keeps the push gate from checking the cache
  either ([Canonical Artifacts](/standards/build/canonical.md#makefile)).
- **`ref-lint`.** Cross-repo Citations resolve only where the cited repo is
  cloned, and a secondary deliberately carries only some of the workspace's
  repos. `SKIP=ref-lint` stands the detector down.

The primary carries every repo and runs every check, so nothing goes
permanently unchecked. Which gates this affects is recorded in
[Gates](/standards/standard/gates.md#skips).
