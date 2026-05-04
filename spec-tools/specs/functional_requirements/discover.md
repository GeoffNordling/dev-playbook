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
set of spec files reachable from that root. The discoverer
`SHALL NOT` include `index.md` files (the navigation tables of
folder-form spec directories) in the returned set. If the project
root has no recognized spec layout, the discoverer `SHALL` raise
to signal misconfiguration.

Rationale:
A single entry point that handles either layout removes a class of
duplicate logic from every consumer. Index files carry navigation
metadata rather than spec content; the discoverer surfaces only
spec content so consumers do not re-implement the filtering rule.
A missing or unrecognized layout indicates a configuration error;
raising lets callers handle the case explicitly.

Covers:
- feat~discover~0

Needs:
- dsn
