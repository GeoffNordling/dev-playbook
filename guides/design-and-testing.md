---
type: Guide
title: Design and Testing
description: What to settle before writing code or a test — the module's small interface, its ports and accepted dependencies, the loud read of a required value, and the test that names a capability, doubles at the port, and asserts on observable outputs
---

# Design and Testing

How a module is shaped and how the tests that cross its interface are
written.

A module in a governed repo's source: anything with an interface and an
implementation. The class is deliberately scale-agnostic, and a function, a
class, a package, and a tier-spanning slice are each a member, bound alike.

A module has exactly one **interface**, the surface it presents to its callers
and to its tests. The interface is everything a caller must know to use the
module correctly: the type signature, and with it the invariants, the ordering
constraints, the error modes, the required configuration, and the performance
characteristics. The **implementation** is what sits inside the module, its
body of code.

Shaping a module comes first, because the interface it leaves is the surface the
tests cross: writing one test, choosing a double, and setting up and
tearing down all start from that surface. The references between the
sequences hold what is consulted rather than performed — the seams an
interface may present, the shapes a fallback takes, what a docstring and
a sourced fragment carry, and the tests the suite does without.

## Shaping a module

A module is shaped from the outside in:

1. **Keep the interface small against the behaviour.** Keep what a
   caller or a test must learn to use the module little against the
   amount of behaviour that use reaches. The measure is the interface
   alone, so a module composed inside of many small, swappable parts is
   deep as long as those parts stay out of its interface. What deleting
   the module would cost measures its depth: a deep module's complexity
   moves out to each of its callers and reappears once per caller; a
   pass-through's moves once and leaves the total unchanged, so its
   interface adds a surface to learn and takes away no complexity.
2. **Take each dependency as a parameter.** Construct none of them in
   the module's own body.
3. **Put a port at each process boundary.** Put a **port** at the
   module's own interface for each dependency the module reaches across
   a process boundary, a service the workspace owns or a third party it
   does not control: the module holds the logic, and the transport that
   carries the call out of the process satisfies that port. Leave a
   dependency the module reaches inside its own process without a
   port — pure computation, in-memory state, or a store with an
   in-process stand-in the tests use.
4. **Reach every behaviour through the interface.** Callers and tests
   cross the same seam, so a behaviour reachable only from inside the
   module is not a gap in the tests but a sign that the module is the
   wrong shape.

## The seams a module presents

A **seam** is a place where behaviour is altered without editing in that
place. Keep a seam that exists only for the module's own tests inside
the implementation, off the interface.

Give a seam the interface does present at least two adapters, concrete
things that satisfy the interface at that seam; a test's in-memory fake
is one. One adapter makes the seam hypothetical: nothing varies across
it, so the interface buys indirection and no leverage. The second
adapter, a test's in-memory fake included, is the evidence that
behaviour differs across the seam.

## Fallbacks that hide a missing value

Read a value the code requires directly, so a missing one raises. Leave
a fallback only where the missing value is a real runtime state rather
than a programming error, with an inline comment giving that reason.
Each of these shapes, over a value that always exists, hides the missing
value:

- `dict.get(key, default)` where `key` is always present.
- `if x is None: return default`, or `x or default`, conditioning a
  value that always exists.
- `try: ... except Exception: return default`, swallowing the error into
  a sentinel.
- `getattr(obj, "attr", default)` for an attribute the object is
  required to have.
- A default parameter value papering over state the caller always
  supplies.

A fallback that hides a bug delays the failure to a place far from the
cause, where it is much harder to diagnose. The inline comment on a
legitimate fallback is the signal that the author weighed the missing
value.

## What a docstring says

Say in plain English what the module, class, function, or method the
docstring documents does.

## What a sourced fragment holds

Keep a sourced fragment, a shell file under `.bashrc.d/`
([Shell Conventions](/standards/shell/conventions.md)), to what mutates
the parent shell: directory changes, aliases, and completions. The
boundary is the one job a child Python process cannot do: it cannot
change the parent's directory, define its aliases, or register its
completions.

## Writing one test

One test is written in this order:

1. **Name the test for the capability.** Choose a name that states the
   capability under test and survives an implementation swap:
   `test_request_includes_trace_id`, not
   `test_structlog_processor_adds_trace_id`.
2. **Arrange, act, assert.** Set up the conditions, then perform the one
   action under test, then verify the result, in that order and with no
   setup after the action.
3. **Verify one concept.** One behaviour or scenario per test, with
   every assertion in it verifying a facet of that one behaviour.
4. **Take the expected value from outside the code.** A known-good
   literal, a worked example, or the spec, and never a value the test
   recomputes the way the code under test computes it — a test that
   recomputes it that way passes by construction and can never disagree
   with the code.
5. **Assert on observable outputs.** Return values, state changes such
   as a record stored or a file written, and raised exceptions.
6. **Assert on outcomes, not call sequences.** Where the test uses a
   mock, assert the minimum that verifies the contract — "the record is
   in the store" rather than "insert was called once with these
   arguments" — unless a call count, an argument shape, or a call
   ordering is itself the contract. Call counts, argument shapes, and
   call ordering pin the implementation the contract leaves free.

## Choosing a double

A dependency is doubled in this order:

1. **Take the lightest double that verifies the behaviour under test.**
   A real object, then a fake, then a mock; use a real implementation
   that is cheap and deterministic as it is.
2. **Double the port, not the client.** Where the code under test
   reaches a dependency over the network, double the port that code
   defines for the dependency rather than the network client itself.
3. **Fake a stateful or shared dependency.** Fake, rather than mock, a
   dependency whose state or logic the tests exercise and a dependency
   several tests share, and put the fake where
   [Fakes live in the test tree](/standards/testing/conventions.md#fakes-live-in-the-test-tree)
   says. A fake holds real logic, simpler than the production
   implementation's, and couples to the interface rather than the
   implementation, so the tests that use it survive a refactor.
4. **Write one fake per interface.** Write one fake for an interface,
   use it in every test that doubles that interface, and implement in it
   only the methods its callers call.
5. **Keep a mock at a boundary.** A mock stands at a boundary and at
   that boundary's entry point, and deeper in the call chain a fake
   takes its place. The three boundaries a mock stands at:

   - **A side effect that is itself the outcome.** An email was sent, a
     metric recorded, an audit log written; the interaction is what the
     test observes.
   - **A failure mode a fake cannot trigger.** A network timeout, a full
     disk, an API 500.
   - **A non-deterministic or expensive external.** The LLM client, an
     external API, a cloud service.

## Setting up and tearing down

Setup and cleanup leave the test body:

1. **Put construction and cleanup in a pytest fixture.** Keep ad-hoc
   setup code out of the test body.
2. **Give the fixture the narrowest scope that works.** Function, the
   default, then class, then module, then session. State shared between
   tests causes flaky failures.

## Tests to delete and tests not to write

Once a module is covered through its own interface, delete the unit
tests on the smaller pieces beneath it rather than keeping them. Two
layers of coverage over one behaviour is waste: the lower layer pins the
implementation the upper one leaves free to change.

Write no test that asserts on the output of a non-deterministic
component such as an LLM call, a network request, or a source of
randomness. Whether an LLM gives a good answer is an evaluation
question, not a test question; its measure is observability and evals.
