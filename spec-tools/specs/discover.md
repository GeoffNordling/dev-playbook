# Discover

### Spec File Discovery
`feat~discover~0`

Description:
Given a project root, the discoverer `SHALL` enumerate the spec
files the project provides without requiring callers to know whether
the project uses single-file or folder-form layout.

Rationale:
The spec standard admits both layouts. Hiding that detail behind a
single traversal contract lets parse, render, and read-only
consumers share one project-traversal surface.

Needs:
- req

### Project root traversal
`req~discover.traversal~0`

Description:
When the discoverer is given a project root, it `SHALL` return the
set of spec files reachable from that root.

Rationale:
A single entry point that handles either layout removes a class of
duplicate logic from every consumer.

Covers:
- feat~discover~0

Needs:
- dsn

### Public find entry point
`dsn~discover.find~0`

Description:
The discoverer `SHALL` expose a public `find` function that takes a
project root and returns the spec files reachable from that root as
a list of paths.

Rationale:
A single module-level entry point gives every consumer (parse,
analysis, lint) one place to call and hides whether the project
uses single-file or folder-form layout. Without it, each consumer
would re-implement traversal.

Covers:
- req~discover.traversal~0

Needs:
- utest

Interface: discover.find(root: pathlib.Path) -> list[pathlib.Path]
