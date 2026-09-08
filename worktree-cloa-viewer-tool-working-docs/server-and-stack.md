---
type: General-Sheet
title: Server and Stack
description: The cloa-viewer command, the server's four jobs, live update by one-way push, the Python and TypeScript stack, and how checks run
---

# Server and Stack

The server is the one program that makes the page exist: it generates
the view files, watches them, and serves the page that shows them. The
files it writes are the
[Contract](/worktree-cloa-viewer-tool-working-docs/contract.md) and the
generators it runs are the
[Registry](/worktree-cloa-viewer-tool-working-docs/registry.md). The
parent is [CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md).

## The command

`cloa-viewer [checkout ...]` is the only command. It refreshes each
checkout, starts the server, and prints the address to open. With no
argument the checkout is the repo that contains the current directory.
There are no subcommands in v1. A browser page cannot watch a disk on its
own, so some program must run while the page is open, and this command
is that program.

## The server's four jobs

- **Refresh** — run every registered generator for a checkout, validate
  each view file against the envelope and its kind schema before writing
  it, and write the refresh record.
- **Watch the checkout** — on any change to a tracked file, wait a short
  settle time, then refresh. Each of the three current generators runs
  in under a tenth of a second on this repo, so a full refresh on every
  change is affordable.
- **Watch the state directory** — on any view file written or removed,
  push an event to every open page.
- **Serve** — the page, the view files, the schemas, the kind list, the
  checkout's HEAD, and the arrangement, which the page saves back.

## Live update

The push is one-way, server to page: each event names a view file and
whether it changed or was removed, and the page fetches the file,
validates it, and re-renders that one panel. The page reconnects a
dropped stream on its own; the banner shows until it does. The page's
only writes, arrangement saves, are ordinary requests.

## The stack

Python with uv on the server side, in this repo's project, sharing
`md.py` and `gitrepo.py` with `dev_playbook` for frontmatter, links,
slugs, and the tracked file list. The server's own dependencies stay out
of what a repo that depends on dev-playbook installs.

TypeScript and React on the page side, built once into static files the
server serves. A graph library arrives with the force-graph kind, not
before.

JSON Schema is the bridge: the server validates before it writes, the
page validates before it renders, both against the same files.

Package shape, the guess: one directory per kind under `src/cloa_viewer/`
holding its schema and generator, and the page under `web/` inside it
with one renderer directory per kind. Library choices are made at the
first build, not here.

## Checks

Python: ruff, mypy, and pytest through `make check` as today. Generator
tests run against fixture checkouts and validate every output file
against its schema.

Page: the type check and the renderer tests run through a local
pre-commit hook block, the extension point the canonical config grants
([Canonical Artifacts](/standards/build/canonical.md#pre-commit-configyaml)).
`check` runs the whole hook suite, so it covers them without a change to
a canonical target.

Open: whether a browser smoke test joins the checks or stays a manual
step in Chrome during development.

## Acronyms

None.
