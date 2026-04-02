---
name: sdd-trace
description: Run traceability checks verifying requirement IDs across spec, design, and tests
---

# SDD Trace

Run traceability checks to verify that requirement IDs are consistent across the functional spec, design spec, and test markers. Use this mid-workflow to catch drift between artifacts.

The user may provide free-form input describing what to focus on. If no input is given, run the full trace and report what you find.

## What It Checks

`sdd-trace` verifies bidirectional traceability across three artifacts:

- **Functional spec to tests** (always checked): every requirement ID in the functional spec has at least one `@pytest.mark.req()` marker in tests, and every test marker references an existing requirement ID
- **Functional spec to design spec** (checked when design spec exists): every requirement ID in the functional spec is referenced in the design spec, and every requirement ID in the design spec exists in the functional spec

## Workflow

1. Run `/Volumes/workplace/dev-tools/.venv/bin/sdd-trace` from the project root. The tool auto-detects `specs/` and `tests/` directories. This prints a compact summary: area code counts, requirement totals, design coverage, and test coverage. To drill into specific areas, use `--detail <AREA> [<AREA> ...]` (e.g., `--detail ERR AQD`).
2. Read the output. If exit code is 0, everything traces cleanly. If exit code is 1, there are gaps.
3. Present the results to the user. For any gaps found:
   - **Untested requirements**: requirement IDs in the functional spec with no test markers
   - **Unmapped requirements**: requirement IDs in the functional spec with no reference in the design spec
   - **Orphaned test markers**: test markers referencing requirement IDs that don't exist in the functional spec
   - **Orphaned design refs**: design spec references to requirement IDs that don't exist in the functional spec
4. If the current conversation has context about what's being worked on (a design session, a red/green cycle, a spec update), call out which gaps are relevant to the work in progress vs. pre-existing.
