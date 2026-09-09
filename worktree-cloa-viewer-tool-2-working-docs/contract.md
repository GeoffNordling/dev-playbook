---
type: General-Sheet
title: Contract
description: The on-disk contract between server and viewer — the state directory, view file paths, identities, the envelope, the arrangement, the refresh record, and the failure rules
---

# Contract

The state directory is the whole interface between the server, which
writes, and the viewer, which reads. Everything either side may rely on
is in this member; the parent is
[CLOA Viewer](/worktree-cloa-viewer-tool-2-working-docs/ROOT.md). Guesses
are marked as guesses.

## The state directory

The state directory is `$XDG_STATE_HOME/cloa-viewer/`, which is
`~/.local/state/cloa-viewer/` when the variable is unset. It holds one
subdirectory per checkout and nothing else.

## The checkout directory

Each checkout gets one subdirectory, named from its absolute path so
that a worktree and its main checkout never share one. The readable
facts, the absolute path, the repo name, and the branch, sit in
`checkout.json` inside it.

A checkout directory holds:

- `checkout.json` — the facts above.
- `refresh.json` — the refresh record.
- `arrangement.json` — the arrangement.
- `<kind>.json` — the one view file of a per-checkout kind, such as
  `index-tree.json`.
- `<kind>/<subject>.json` — a view file of a per-subject kind, mirroring
  the subject's path: `markdown-file/docs/working-in-loops.md.json`,
  `runbook-chain/dotfiles/dot-claude/agents/adjudicator.md.json`.

A view file's identity is its path under the checkout directory. Writing
the same path again replaces the panel in place, which is what live
update needs.

## Identities

An identity is a repo-relative path, with an optional `#slug` naming a
heading by its GitHub slug: `docs/working-in-loops.md#placement`. A
directory identity ends in `/`. The slug rule is the one
[md.py](/src/dev_playbook/md.py) already computes. Every payload field
that names a thing in the checkout holds an identity, so two panels that
name the same thing agree without a lookup table.

## The envelope

Every view file is one JSON object with exactly these top-level fields:

| Field | Holds |
|---|---|
| `envelope` | the integer envelope version, `1` |
| `kind` | the registered kind name |
| `kind_version` | the integer version of that kind's payload schema |
| `title` | the panel's heading |
| `subject` | the identity the file is about, or `null` for a per-checkout kind |
| `stamp` | `commit`, `generated_at` (UTC, RFC 3339), and `generator` (the module name) |
| `payload` | the object the kind's schema governs |

A missing field, an extra field, or a wrong type rejects the whole file.
The envelope schema lives once, in the package's `schemas/` directory;
kind schemas govern `payload` only. The checkout and the repo are not in
the file: the directory says them.

```json
{
  "envelope": 1,
  "kind": "runbook-chain",
  "kind_version": 1,
  "title": "adjudicator",
  "subject": "dotfiles/dot-claude/agents/adjudicator.md",
  "stamp": {
    "commit": "46321be7c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5",
    "generated_at": "2026-09-08T14:02:11Z",
    "generator": "cloa_viewer.kinds.runbook_chain"
  },
  "payload": {}
}
```

## The arrangement

`arrangement.json` is what the user has open, saved per checkout: the
open view files in order, which are pinned, and which tree directories
are expanded. The viewer writes it through the server; nothing else
writes it. It has a schema like any other file here.

## The refresh record

`refresh.json` is the outcome of the last refresh: when it ran, at which
commit, and for each registered kind whether its generator succeeded,
how many view files it wrote, and the error text when it failed. On
success a generator's output replaces its kind's files whole; on failure
those files stay as they were and the record carries the error.

## Failure rules

- A view file that fails the envelope or its kind schema renders as an
  error panel naming the file and the failing field.
- A view file naming a kind the viewer has no renderer for renders as an
  error panel naming the kind.
- A view file whose stamp commit differs from the checkout's HEAD carries
  a stale badge showing both commits. The server reports HEAD; the
  viewer compares.
- A lost connection to the server shows a banner until it returns.
- A failed generator turns the refresh status red, with the error text
  one click away.

## Acronyms

XDG — Cross-Desktop Group. UTC — Coordinated Universal Time. RFC —
Request for Comments.
