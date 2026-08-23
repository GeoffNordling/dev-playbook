---
type: Guide
title: Refactor Catalogue
description: The structural candidates — the cue and the move for each — and the step-size rule governing a refactor step
---

# Refactor Catalogue

What to look for when the next move is structural, and how large that move is
allowed to be.

## Step size

**Make each step as small as it can be.** A refactoring step is one
behavior-preserving move, and `make test` runs green after it. The smaller
the step, the shorter the window in which the program is not demonstrably
working, and the cheaper the revert when a step turns out wrong.

Where a change lands cleanly but leaves an older seam, name, or duplication
visibly wrong in a way it was not before, that fix is its own step, separate
from the change that exposed it.

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
  method as the sequence of its steps. Tests stay on the public interface —
  the helpers are an internal detail.
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
- **Mysterious name → rename it.** *Cue:* a function, variable, or type whose
  name does not reveal what it does or holds. *Move:* rename it; where no
  honest name comes, the murk is in the design.
- **Data clumps → bundle them into a type.** *Cue:* the same few fields or
  parameters keep travelling together. *Move:* give the group one type and
  pass that.
- **Repeated switches → replace with polymorphism.** *Cue:* the same `if`- or
  `match`-cascade on the same type recurs in more than one place. *Move:*
  dispatch on the type itself, or collapse the cascades to one map both sites
  share.
- **Message chains → hide the walk.** *Cue:* long `a.b().c().d()` navigation
  that couples the caller to a structure two objects away. *Move:* put one
  method on the first object that answers the question directly.
- **Middle man → cut the delegate.** *Cue:* a class or function whose body is
  mostly forwarding to something else. *Move:* call the real target directly and
  delete the pass-through.
- **Refused bequest → prefer composition.** *Cue:* a subclass or implementer
  ignores or overrides most of what it inherits. *Move:* drop the inheritance
  and hold the thing it actually needs.
- **Speculative generality → delete it.** *Cue:* abstraction, parameters, or
  hooks serving a need the brief does not have. *Move:* inline it back until a
  real caller shows up.
- **Divergent change → split the module.** *Cue:* one file is edited for several
  unrelated reasons. *Move:* separate it so each module changes for one reason.
- **Shotgun surgery → gather what changes together.** *Cue:* one logical change
  forces scattered edits across many files. *Move:* pull the scattered pieces
  into the one module that owns the concern. The inverse of divergent change.

For test-quality patterns and mocking guidance, see
[testing conventions](/standards/testing/conventions.md).
