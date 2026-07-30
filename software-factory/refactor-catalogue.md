---
type: Guide
title: Refactor Catalogue
description: The refactor candidates a build node looks for at slice and chunk scope, and the step-size rule governing them
---

# Refactor Catalogue

What to look for when the suite is green and the next move is structural, and
how large that move is allowed to be.

## Step size

**Make each step as small as it can be.** A refactoring step is one
behavior-preserving move — extract this function, rename this symbol, move this
method to where its data lives — and `make test` runs green after it. Prefer the
smallest move that changes the shape at all: the smaller the step, the shorter
the window in which the program is not demonstrably working, and the cheaper the
revert when a step turns out wrong.

## The candidates

Each entry is a cue — what the code looks like when the candidate is present —
and the move it calls for.

- **Duplication → extract a function or class.** *Cue:* the same computation or
  the same sequence of calls appears in two places, and editing one means
  remembering the other. *Move:* name it once and call it twice; where the
  duplicated shape carries state as well as behavior, the extraction is a class.
- **Long method → break into private helpers.** *Cue:* the body needs a comment
  per section, or a reader has to hold several unrelated things at once to
  follow it. *Move:* lift each section into a named private helper, leaving the
  method as the sequence of its steps. Tests stay on the public interface — the
  helpers are an internal detail, not a new surface to cover.
- **Shallow module → combine or deepen.** *Cue:* the interface is nearly as wide
  as the implementation behind it, so a caller learns as much by reading the
  module as by using it. *Move:* push work behind the interface until the module
  carries real weight, or fold it into its single caller when there is nothing
  to push.
- **Feature envy → move the logic to its data.** *Cue:* a function reaches
  repeatedly through another object to gather what it needs, and reads more
  about that object than about its own. *Move:* relocate the logic onto the type
  that owns the data, and let the caller ask for the answer instead of the
  parts.
- **Primitive obsession → introduce a value object.** *Cue:* a `str`, `int`, or
  tuple carries a rule about its own validity, and that rule is re-checked at
  every use. *Move:* give it a type that enforces the rule at construction, so
  the checks collapse to one.
- **Existing code the new code reveals as problematic.** *Cue:* the change lands
  cleanly, but it makes an older seam, name, or duplication visibly wrong in a
  way it was not before. *Move:* fix it in its own step, separate from the
  change that exposed it.

## The two scopes

The catalogue is applied twice, at different reach.

- **Slice scope.** With the suite green after one behavior lands, the candidates
  are looked for **inside the module just touched** — its duplication, its
  shallow seams, its primitives. `make test` runs after each step.
- **Chunk scope.** With a whole chunk green, **every module the chunk touched**
  is reviewed for what no single slice could see: duplication spread across
  modules, a module worth deepening now that several call sites exist,
  abstraction misalignments, primitive obsession. `make test` runs after each
  step.

Both scopes share one escalation trigger — a refactor that surfaces a structural
problem beyond one module's seam — and the citing skill states it, with its own
terminal line and wording.

For test-quality patterns and mocking guidance, see
[testing conventions](/standards/testing/conventions.md).
