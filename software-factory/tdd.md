---
type: Guide
title: Test-First Discipline
description: The test-first discipline `tests:yes` work runs under — the chunk, the slice loop, and the whole-chunk refactor pass
---

# Test-First Discipline

How the work is carried out when the issue carries `tests:yes`. Read
[testing conventions](/standards/testing/conventions.md)
end-to-end first — pytest structure, naming, fixtures, behavioral focus.

Under this discipline a piece of the scope is a **chunk**: the slices covering
one acceptance criterion, or a small cluster of tightly related ones. A chunk is
carried out by running the slice loop until every behavior in its scope is
covered by a passing test, then closing with the whole-chunk refactor pass. The
gate and the commit are build's own steps, unchanged.

Things ride along in build's plan: the chunk's seams, its slice ordering, and
the current state of the suite — run `make test` before the first chunk to see
it.

**Choose the seams first.** A **seam** is a place where a test can replace or
observe behavior without reaching inside the code that produces it. Work out the
seams the chunk's tests cut at before writing the first test. A brief may name
seams; where it does, respect them.

## The slice loop

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior the brief calls for. Write a single
failing test exercising it through the public surface. Run `make test`; confirm
it fails for the expected reason.

**Never modify a written test.** Once a test is written, make it pass by
changing code; changing the test instead is an escalation.

**Stub on first contact.** When a test names a symbol with no stub yet, create
the stub it needs — the signature is designed here, since the brief pins
behavior, not interfaces. Body is `raise NotImplementedError` for functions and
methods, `pass` for `__init__`. Don't pre-stub symbols not yet under test.

**Fixtures define the contract.** A fixture that constructs an object, a fake
included, is the interface contract the Green step implements against; keep it
minimal, only the parameters the spec implies.

**Green.** Write the minimal implementation that makes the failing test pass.
Don't add code for behaviors not yet tested. Run `make test`; confirm green.

**Refactor.** With the suite green, apply
[the refactor catalogue](/software-factory/refactor-catalogue.md)
**inside the module just touched** — its duplication, its shallow seams, its
primitives. Run `make test` after each step.

## The whole-chunk refactor pass

With every behavior in the chunk's scope covered and the suite green, apply the
catalogue across **every module the chunk touched** — what no single slice could
see: duplication spread between modules, a module worth deepening now that
several call sites exist, abstraction misalignments, primitive obsession. Run
`make test` after each step. Then the chunk goes to build's gate and commit.

## Escalations

These add to build's own escalation triggers, and end the session the same way —
`outcome: escalated`, with the reason in `gist`:

- **Stuck test.** A slice's test won't pass after two implementation attempts.
- **A written test looks wrong.** Changing an already-written test seems
  necessary — surface why; the user decides whether the behavior was mis-encoded
  or the brief needs to change.
- **A refactor reaches past one module's seam.** Either pass surfaces a
  structural problem wider than the module in hand — surface it rather than
  widening the change.
