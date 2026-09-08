---
type: General-Sheet
title: Stack
description: The Python and TypeScript stack, JSON Schema as the bridge between them, the package shape, and how checks run
---

# Stack

What the tool is built with and how it is checked. The program these
languages make is the
[Server](/worktree-cloa-viewer-tool-working-docs/server.md); the parent
is [CLOA Viewer](/worktree-cloa-viewer-tool-working-docs/ROOT.md).

## Languages

Python with uv on the server side, in this repo's project, sharing
`md.py` and `gitrepo.py` with `dev_playbook` for frontmatter, links,
slugs, and the tracked file list. The server's own dependencies stay out
of what a repo that depends on dev-playbook installs.

TypeScript and React on the page side, built once into static files the
server serves. A graph library arrives with the force-graph kind, not
before.

JSON Schema is the bridge: the server validates before it writes, the
page validates before it renders, both against the same files.

## Package shape

The guess: one module per kind under
`src/dev_playbook/cloa_viewer/kinds/`, the schemas in one `schemas/`
directory beside them, and the page under `web/` inside the package with
one renderer directory per kind. Library choices are made at the
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
