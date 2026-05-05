### Public find entry point
`dsn~discover.find~0`

Description:
The discoverer `SHALL` expose a public `find` function that takes a
project root and returns the spec files reachable from that root as
a list of paths. If the root has no recognized spec layout, `find`
`SHALL` raise `ValueError`.

Rationale:
A single module-level entry point gives every consumer (parse,
analysis, lint) one place to call and hides whether the project
uses single-file or folder-form layout. Without it, each consumer
would re-implement traversal. Raising on unrecognized layouts gives
callers a single binary contract: each call either returns the
spec-file list or raises.

Covers:
- req~discover.traversal~0

Needs:
- utest

Interface: discover.find(root: pathlib.Path) -> list[pathlib.Path]
