# SDD Simulation

A thought experiment that stress-tests the workspace spec standard by
walking through a fictional design of `spec-tools`.

## Purpose

Evaluate the **spec standard**, not design `spec-tools`.

`spec-tools` is the theme — familiar enough to give the specs we draft
realistic shape (multiple modules, real coverage chains), yet far enough
from the actual rewrite that we feel free to push on awkward cases.

The deliverable is a list of findings about the standard: where it is
expressive, where it is silent, where it forces awkward choices.

## Scope

- **Granularity**: modules, classes, named functions, public types.
  Implementation code is out of scope.
- **Artifacts**: `feat`, `req`, `dsn` items per
  [the spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md).
  Tests are declared via `Needs:`, never written.
- **Conformance**: every item conforms to the current standard. Where
  the standard is unclear or awkward, the conformant choice is made and
  the friction is logged as a finding.

## Out of scope

- The real `spec-tools` rewrite tracked by issue #16. Decisions made
  here are not authoritative for that work.
- Implementation code, test code, behavior validation.

## Layout

- `specs/` — simulated `feat` / `req` / `dsn` items, organized by module
- `findings.md` — observations about the standard (created when we have any)
