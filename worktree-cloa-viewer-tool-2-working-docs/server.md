---
type: General-Sheet
title: Server
description: The cloa-viewer command, the server's jobs, and live update by one-way push
---

# Server

The server is the one program that makes the page exist: it generates
the view files, watches them, and serves the page that shows them. The
files it writes are the
[Contract](/worktree-cloa-viewer-tool-2-working-docs/contract.md) and the
generators it runs are the
[Registry](/worktree-cloa-viewer-tool-2-working-docs/registry.md). What
it is built with is the
[Stack](/worktree-cloa-viewer-tool-2-working-docs/stack.md). The parent is
[CLOA Viewer](/worktree-cloa-viewer-tool-2-working-docs/ROOT.md).

## The command

`cloa-viewer [path ...] [--port N]` is the only command. A path that is
a checkout is shown as it is. A path that is not one, `~/workspace/`
being the case that matters, is scanned: each git repo directly below it,
and every linked worktree of each, found with `git worktree list`,
becomes a checkout. No path means the current directory by the same
rule, so inside a repo it is that repo. A path that yields no checkout
stops the command with an error naming it. The command refreshes each
checkout, starts the server, and prints the address to open. There are
no subcommands in v1. A browser page cannot watch a disk on its own, so
some program must run while the page is open, and this command is that
program.

The usual launch, from any directory, is

```sh
uv run --project ~/workspace/dev-playbook cloa-viewer ~/workspace
```

which runs the code of dev-playbook's main checkout over every checkout
in the workspace. One server is enough: repo, branch, and worktree are
chosen on the page, not on the command line.

## The server's jobs

- **Discover** — turn the paths it was given into the list of checkouts,
  and do it again each time the page asks for the list. A checkout that
  appeared is refreshed and watched; one that vanished is dropped, its
  watcher stopped, and its state directory removed.
- **Refresh** — run every registered generator for a checkout, validate
  each view file against the envelope and its kind schema before writing
  it, and write the refresh record.
- **Watch the checkout** — on any change to a tracked file, wait a short
  settle time, then refresh. Each current generator runs in under a
  tenth of a second on this repo, so a full refresh on every change is
  affordable. A checkout that lies inside another, a worktree
  under the main checkout's `.claude/worktrees/`, is watched on its own
  and ignored by the outer checkout's watcher.
- **Watch the state directory** — on any view file written or removed,
  push an event to every open page.
- **Serve** — the page, the view files, the schemas, the kind list, the
  checkout's HEAD, and the arrangement, which the page saves back.

## Live update

The push is one-way, server to page: each event names a view file and
whether it changed or was removed, and the page fetches the file,
validates it, and re-renders that one panel. The target from a save in
the IDE to the redrawn panel is one second. The page reconnects a
dropped stream on its own; the banner shows until it does. The page's
only writes, arrangement saves, are ordinary requests.

## Acronyms

None.
