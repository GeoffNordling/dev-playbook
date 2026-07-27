---
type: Decision-Record
title: The Workspace Spans Machines — Differences Live in Two Files
status: accepted
description: Confine every machine difference to two files named by machine key, and allow a check to be skipped only where its input is machine-local rather than held in the repository
---

# The Workspace Spans Machines — Differences Live in Two Files

The workspace ran on one machine and its configuration assumed so. It now runs
on three: an air-gapped Fedora **primary** where development happens, and two
Windows/WSL **secondaries** kept identical under the single machine key `wsl`.
Two rules keep that from becoming three configurations. **Every machine
difference lives in `dotfiles/settings/<machine>.json` or
`dotfiles/.bashrc.d/machine-env.sh`, both named by machine key** — a difference
anywhere else is a bug. And **a check may be skipped on a machine only where
its input is machine-local rather than held in the repository**, because there
the detector would report the environment as a defect in the code.

Two checks qualify, and only two: `ref-lint` resolves Citations against sibling
repos a secondary deliberately does not clone, and the judgments cache gate
reads a `~/.cache/skipcache` seen-set that only the primary fills. Both
announce the skip on every run. The primary carries every repo and the cache,
so nothing goes permanently unchecked — it is checked on the machine that can
check it.

## Considered Options

**Symlink a whole per-machine settings file.** Claude Code reads exactly one
user-scope settings file and offers no local override layer, so each machine's
file would have to carry a full copy of the shared settings. Two copies of one
policy drift. Rejected in favor of generating the file from a shared
`base.json` plus a machine fragment, merged with Claude Code's own cross-scope
semantics.

**Skip the whole push gate on a secondary.** The simplest way to stop a machine
failing checks it cannot run, and the reason a branch reached `origin` with a
type error in it: the gate was absent, not lenient. Rejected. A secondary runs
mypy, pytest and the full hook suite like the primary, and stands down only the
one check it cannot fill.

**A branch or a clone per machine.** Rejected — the machines would diverge
silently, which is the failure this record exists to prevent.

## Consequences

`make check-judgments` honors `NO_JUDGMENT_CACHE`, so the push gate arms the
judgment cache gate only where a cache exists. That is a canonical-artifact
change and reaches consumer repos when their pinned `rev` moves, not at once.

A new machine costs two files and one branch in `machine-env.sh`. The
inventory, and what each machine skips, is
[machines.md](/docs/machines.md); which gates that touches is
[enforcement.md](/standards/build/enforcement.md).

Both local gates live in `.git/`, which no clone carries, so each machine
installs them itself. A machine that never did reports nothing and blocks
nothing — the quiet failure mode that made this record necessary.
