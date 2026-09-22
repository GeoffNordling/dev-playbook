---
type: Decision-Record
title: The Live Settings File Is the Authority
description: Keep ~/.claude/settings.json a stowed symlink that Claude Code writes through, with one settings file for every machine and a session-start check for the symlink's one failure mode, the repo carrying settings between machines rather than enforcing them
date: 2026-08-28
status: accepted
---

# The Live Settings File Is the Authority

`~/.claude/settings.json` is a stowed symlink to `dot-claude/settings.json`,
and Claude Code writes settings changes through it, verified 2026-08-28 on
version 2.1.250: toggle a setting in a session and the change lands in the
main checkout as an ordinary uncommitted edit, on whatever branch is checked
out there. The decision: leave it that way. The repo is the carrier that
syncs settings between machines, not a source of authority to enforce —
committing and pushing those edits is the user's, like any other change.

Two consequences hold the design together:

- **One file serves every machine.** A hook that must not run somewhere
  guards itself at runtime (`hooks/play-sound`, `hooks/measure-event`)
  instead of living in a per-machine settings variant.
- **The one failure left is the symlink itself.** If a future Claude Code
  version replaces the symlink with a regular file instead of writing through
  it, the repo silently stops receiving changes —
  `hooks/session-start-settings-link` checks for exactly that at every
  session start.

## Considered Options

- **Copy the settings file instead of symlinking it.** Rejected: a copy
  makes the repo the authority, and every session's own edits then have to
  be found and carried back by hand.
- **A settings variant per machine.** Rejected: the machines run the same
  configuration, and a hook that must not run somewhere already decides that
  at runtime.
