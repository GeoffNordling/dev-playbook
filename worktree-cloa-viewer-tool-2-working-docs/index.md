# worktree-cloa-viewer-tool-2-working-docs/ — index

The working documentation set for cloa-viewer, the local visual IDE that
shows a checkout's fact base in the browser. Start at the root.

Ordering: reading order.

- [CLOA Viewer](/worktree-cloa-viewer-tool-2-working-docs/ROOT.md) — The plan for cloa-viewer, a local visual IDE that shows a checkout's fact base in the browser as registered views read from files on disk
- [Contract](/worktree-cloa-viewer-tool-2-working-docs/contract.md) — The on-disk contract between server and viewer — the state directory, view file paths, identities, the envelope, the arrangement, the refresh record, and the failure rules
- [Registry](/worktree-cloa-viewer-tool-2-working-docs/registry.md) — The registered kinds — what an entry consists of, the two kinds built, the CLOA views to come, and the kinds deferred
- [Design](/worktree-cloa-viewer-tool-2-working-docs/design.md) — How a panel is designed — the design space as selections from the fact base, and the renderer ideas recorded for the runbook views, none of them settled
- [Viewer](/worktree-cloa-viewer-tool-2-working-docs/viewer.md) — The page in the browser — its fixed regions, the tree, panels and the arrangement, everything about one file, the checkout toggle, refresh, and how failure shows
- [Server](/worktree-cloa-viewer-tool-2-working-docs/server.md) — The cloa-viewer command, the server's jobs, and live update by one-way push
- [Stack](/worktree-cloa-viewer-tool-2-working-docs/stack.md) — The Python and TypeScript stack, JSON Schema as the bridge between them, the package shape, and how checks run
- [Fact Base](/worktree-cloa-viewer-tool-2-working-docs/fact-base.md) — The fact base — one deterministic object of nodes and edges extracted from a checkout, every view a selection from it, and how the doc-type build loop and its residuals apply to every object it holds
- [Ralph Fact Base](/worktree-cloa-viewer-tool-2-working-docs/fact-base-ralph.md) — The definitions behind the simulated fact base for the Ralph loop subsystem — its terms, the extractors that yield each fact, the views selected from it, and the facts no extractor reaches
