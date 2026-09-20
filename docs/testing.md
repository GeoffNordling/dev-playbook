---
type: General-Sheet
title: Test Design Guide
description: The thinking behind the testing rules — what a test verifies, the tautological test, the non-deterministic boundary, the ladder of doubles, what a fake is, where a mock stands, and why layered coverage is waste
---

# Test Design Guide

The guide behind
[Testing Conventions](/standards/testing/conventions.md), the ruleset
that governs a governed repo's Python test suite. The ruleset states each
rule as a predicate a reviewer can decide; this guide carries the
vocabulary, the reasoning, and the examples that make the rules
intelligible. Nothing here is enforced; every rule is in the ruleset.

## What a test verifies

Tests verify **what** the system does, not **how** it does it. Five rules
in the ruleset, from
[Access only public names](/standards/testing/conventions.md#access-only-public-names)
to
[Replace, don't layer](/standards/testing/conventions.md#replace-dont-layer),
are that principle's checks. Private helpers such as `_foo` and
`_Tokenizer` are exercised through the public interfaces that call them,
and internal state, private attributes, and implementation details sit
outside what a test asserts on. A test's name states the capability, and
the machinery that currently delivers it is not in the name: a name
that survives an implementation swap is the one that was about the
behavior all along.

## The tautological test

A *tautological* test recomputes the expected value the way the code under
test computes it, so it passes by construction and can never disagree with
the code. The expected value therefore comes from outside the code: a
known-good literal, a worked example, or the spec
([Expected values come from outside the code](/standards/testing/conventions.md#expected-values-come-from-outside-the-code)).

## Why a test body holds no branch

A branch or a caught exception in a test body is the test deciding what it
ought to be asserting. Loops, ternaries, comprehension filters, and nested
helper definitions carry no such decision and stay legal
([No logic in tests](/standards/testing/conventions.md#no-logic-in-tests)).

## Why the layout mirrors the source

Mirroring scales with the source tree and keeps two modules of the same
file name from colliding, which is why the mirror, flat or beneath one of
the two scope directories, is the one accepted location and the scope set
is fixed
([Mirror source structure](/standards/testing/conventions.md#mirror-source-structure)).
Each directory level carries its own `conftest.py` for the fixtures of that
scope, so a domain-specific fixture stays with the tests of its domain and
the root `conftest.py` holds only what the whole suite shares
([Conftest hierarchy](/standards/testing/conventions.md#conftest-hierarchy)).

## The non-deterministic boundary

No test asserts on the output of a non-deterministic component: an LLM
call, a network request, a source of randomness. What the suite covers is
the deterministic machinery around that boundary:

- Input parsing and validation
- Routing and dispatch logic
- Prompt and request assembly
- Output and response parsing
- Formatting and delivery

"Does the LLM give a good answer?" is an evaluation question, not a test
question. It is measured through observability and evals
([No test of a non-deterministic decision](/standards/testing/conventions.md#no-test-of-a-non-deterministic-decision)).

## The ladder of doubles

A dependency is doubled with the lightest thing that verifies the behavior
under test: a real object, then a fake, then a mock. A real implementation
that is cheap and deterministic is used as it is: a real database in a
temp directory, an in-process HTTP server, and a real parser over fixture
files are all cheap and deterministic
([The lightest double](/standards/testing/conventions.md#the-lightest-double)).

A dependency reached over the network gets a **port** built for it first,
and the double then sits at that seam; the
[Module Design Guide](/docs/design.md) covers when a seam earns its keep
([Double at the port](/standards/testing/conventions.md#double-at-the-port)).

## What a fake is

A fake is a working, simplified implementation of a real interface, built
for testing: a store backed by an in-memory dict instead of a database, an
email sender that appends to a list instead of reaching SMTP. It has real
logic inside, just simpler. Stores, queues, and caches are the common
cases. A fake is written once and reused across the suite, it implements
only the methods its callers use, so production complexity is not
replicated in it, and it couples to the interface rather than the
implementation, so the tests using it survive refactoring
([Fakes for stateful dependencies](/standards/testing/conventions.md#fakes-for-stateful-dependencies)).

## Where a mock stands

A mock stands at a boundary and at that boundary's entry point; deeper in
the call chain a fake takes its place. Where a function-level dependency
genuinely must be isolated, the mock sits at the function's entry point.
A mock's assertion is the minimum that verifies the contract, because call
counts, argument shapes, and call ordering pin the implementation the
contract leaves free
([Mocks at boundaries only](/standards/testing/conventions.md#mocks-at-boundaries-only)).

## Why layered coverage is waste

Two layers of coverage over one behavior is waste: the lower layer pins
the implementation the upper one leaves free to change. Once a module is
covered through its own interface, the unit tests on the smaller pieces
beneath it go
([Replace, don't layer](/standards/testing/conventions.md#replace-dont-layer)).

## Fixtures

A fixture that constructs an object, a fake included, is the interface
contract the code under test is written against, and it constructs only
what the test needs
([Fixtures for setup and teardown](/standards/testing/conventions.md#fixtures-for-setup-and-teardown)).
A fixture takes the narrowest scope that works because state shared
between tests causes flaky failures
([Narrowest fixture scope](/standards/testing/conventions.md#narrowest-fixture-scope)).
