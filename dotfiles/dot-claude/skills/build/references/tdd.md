# Test-First Discipline

How the work is carried out when the issue carries `tests:yes`. Read
[testing conventions](~/workspace/dev-playbook/standards/testing/conventions.md)
end-to-end first — pytest structure, naming, fixtures, behavioral focus.

Under this discipline a piece of the scope is a **chunk**: the slices covering
one acceptance criterion, or a small cluster of tightly related ones. A chunk is
carried out by running the slice loop until every behavior in its scope is
covered by a passing test, then closing with the whole-chunk refactor pass. The
gate and the commit are build's own steps, unchanged.

Three things ride along in build's plan: the chunk's seams, its slice ordering,
and the current state of the suite — run `make test` before the first chunk to
see it.

**Choose the seams first.** A **seam** is a public surface where a behavior is
observable without reaching inside the code that produces it. Work out the seams
the chunk's tests cut at before writing the first test; if the brief names seams, respect them.

## The slice loop

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior the brief calls for. Write a single
failing test exercising it through the public surface. Run `make test`; confirm
it fails for the expected reason.

**Never modify a written test.** Once a test is written, make it pass by
changing code; where you feel the need to change the test instead, escalate.

**Stub on first contact.** When a test names a symbol with no stub yet, create
the stub it needs — you design the signature here, since the brief pins
behavior, not interfaces. Body is `raise NotImplementedError` for functions and
methods, `pass` for `__init__`. Don't pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass.
Don't add code for behaviors not yet tested. Run `make test`; confirm green.

**Refactor.** With the suite green, apply the slice-scope candidates in
[the refactor catalogue](~/workspace/dev-playbook/software-factory/refactor-catalogue.md).
Run `make test` after each step.

## The whole-chunk refactor pass

With every behavior in the chunk's scope covered and the suite green, apply the
catalogue's chunk-scope candidates across every module the chunk touched — what
no single slice could see. Run `make test` after each step. Then the chunk goes
to build's gate and commit.

## Escalations

These add to build's own triggers and take its `ESCALATE:` line:

- **Stuck test.** A slice's test won't pass after two implementation attempts.
- **A written test looks wrong.** You want to change a test you already wrote —
  surface why; the user decides whether you mis-encoded it or the brief needs to
  change.
- **A refactor reaches past one module's seam.** Either pass surfaces a
  structural problem wider than the module you're in — surface it rather than
  widening the change on your own.
