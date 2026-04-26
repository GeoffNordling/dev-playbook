# Discover

Simulated specs for the `spec-tools` discover module. See
[../README.md](../README.md) for the simulation's purpose.

## Feature

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

## Requirements

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
