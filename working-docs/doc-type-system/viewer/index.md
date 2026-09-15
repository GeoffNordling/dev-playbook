# working-docs/doc-type-system/viewer/ — index

The viewer strand: cloa-viewer, the local visual IDE that draws
registered views of the fact base. Start at the root.

Ordering: the root, then reading order.

- [CLOA Viewer](/working-docs/doc-type-system/viewer/ROOT.md) — The plan for cloa-viewer, a local visual IDE that shows a checkout's fact base in the browser as registered views read from files on disk
- [Contract](/working-docs/doc-type-system/viewer/contract.md) — The on-disk contract between server and viewer — the state directory, view file paths, identities, the envelope, the arrangement, the refresh record, and the failure rules
- [Registry](/working-docs/doc-type-system/viewer/registry.md) — The registered kinds — what an entry consists of, the two kinds built, the CLOA views to come, and the kinds deferred
- [Design](/working-docs/doc-type-system/viewer/design.md) — How a panel is designed — the design space as selections from the fact base, and the renderer ideas recorded for the runbook views, none of them settled
- [Viewer](/working-docs/doc-type-system/viewer/viewer.md) — The page in the browser — its fixed regions, the tree, panels and the arrangement, everything about one file, the checkout toggle, refresh, and how failure shows
- [Server](/working-docs/doc-type-system/viewer/server.md) — The cloa-viewer command, the server's jobs, and live update by one-way push
- [Stack](/working-docs/doc-type-system/viewer/stack.md) — The Python and TypeScript stack, JSON Schema as the bridge between them, the package shape, and how checks run
