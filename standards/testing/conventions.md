---
type: Standard
title: Testing Conventions
description: How a repo's Python test suite is written — the pytest framework, mirror layout, test structure, behavioral focus, doubles, and fixtures
population: "a governed repo's Python test suite: the test_*.py files anywhere in its tree, and the conftest.py and fake modules under tests/"
---

# Testing Conventions

A governed repo's Python test suite is one object: every `test_*.py` file
anywhere in the tree, together with the `conftest.py` files and the fake
modules under `tests/`. A rule about where a fixture or a fake lives binds
the suite as surely as a rule about a test body does. Tests verify **what**
the system does, not **how** it does it, and the five rules from
[Access only public names](#access-only-public-names) to
[Replace, don't layer](#replace-dont-layer) are that principle's checks.
That `tests/` exists at all is
[File Skeleton](/standards/build/skeleton.md#tests-present)'s rule; what
goes where inside it is this Standard's.

## pytest

The suite runs on pytest. Its runner, its fixtures, and its assertion
rewriting are what every rule below assumes.

## Test file naming

Every test file is named `test_*.py`.

The name is also what the detectors collect:
[testing-lint](/scripts/testing-lint) reports nothing about a file whose
name does not begin `test_`, so a misnamed test sits outside
`testing.mirror-layout`, `testing.no-logic`, and
`testing.no-private-access` alike.

## Mirror source structure

A test file naming a module under `src/` sits at that module's mirror
inside `tests/`: `src/auth/login.py` is tested at
`tests/auth/test_login.py`, or at the same path beneath one of the two
scope directories `unit` and `integration`
(`tests/unit/auth/test_login.py`). The package path is always present
(`testing.mirror-layout`).

The scope set is fixed. A directory in that position outside the set is a
misplacement, and the mirror, flat or beneath a scope directory, is the
one accepted location: mirroring scales with the source tree and keeps
two modules of the same stem from colliding.

`tests/agent_review/` is the exception. It holds the judgment gate tests
([cache-gate.md](/standards/semantic-validation/cache-gate.md)), whose
stems are free-form, and no file under it is measured against a source
module.

## Conftest hierarchy

A fixture lives in the `conftest.py` of the narrowest directory whose
tests use it, and the root `conftest.py` holds only what the whole suite
shares.

Each directory level carries its own `conftest.py` for the fixtures of
that scope, so a domain-specific fixture stays with the tests of its
domain.

## Arrange-Act-Assert

A test body has three sections, arrange, act, and assert, separated by
blank lines: it sets up the conditions, performs the action, then verifies
the result.

## One concept per test

Each test verifies one behavior or scenario. Several assertions are fine
where they all verify facets of that one behavior.

## Descriptive names

A test's name reads as the behavior it verifies:
`test_login_rejects_expired_token`, not `test_login_2`. The name alone
conveys what the test checks.

## No logic in tests

The body of a `test_*` function holds no `if`/`else` and no `try`/`except`
(`testing.no-logic`).

Loops, ternaries, comprehension filters, and nested helper definitions
stay legal. A branch or a caught exception is the test deciding what it
ought to be asserting.

## Expected values come from outside the code

A test's expected value is a known-good literal, a worked example, or the
spec.

A *tautological* test recomputes the expected value the way the code under
test computes it, so it passes by construction and can never disagree with
the code.

## Access only public names

A test reaches a non-test module only through identifiers with no leading
underscore: no private import, no private module segment, no private
attribute reach (`testing.no-private-access`).

Private helpers (`_foo`, `_Tokenizer`) are exercised through the public
interfaces that call them. Python dunder protocol methods (`__init__`,
`__iter__`, and their kin) count as public.

## Assert on observable outputs

Assertions are on observable outputs: return values, state changes such as
a record stored or a file written, and raised exceptions.

Internal state, private attributes, and implementation details sit outside
what a test asserts on.

## Assert on outcomes, not call sequences

Where a test uses a mock, its assertion is the minimum that verifies the
contract: "the record is in the store" rather than "insert was called once
with these arguments".

Call counts, argument shapes, and call ordering are asserted only where
the ordering is itself the contract.

## Name by capability, not mechanism

A test's name survives an implementation swap:
`test_request_includes_trace_id`, not
`test_structlog_processor_adds_trace_id`. The capability is what the name
states; the machinery that currently delivers it is not.

## Replace, don't layer

Once a module is covered through its own interface, the unit tests on the
smaller pieces beneath it are deleted rather than kept.

Two layers of coverage over one behavior is waste: the lower layer pins
the implementation the upper one leaves free to change.

## No test of a non-deterministic decision

No test asserts on the output of a non-deterministic component such as an
LLM call, a network request, or a source of randomness. What the suite
covers is the deterministic machinery around that boundary:

- Input parsing and validation
- Routing and dispatch logic
- Prompt and request assembly
- Output and response parsing
- Formatting and delivery

"Does the LLM give a good answer?" is an evaluation question, not a test
question. It is measured through observability and evals.

## The lightest double

A dependency is doubled with the lightest thing that verifies the behavior
under test: a real object, then a fake, then a mock. A real implementation
that is cheap and deterministic is used as it is.

A real database in a temp directory, an in-process HTTP server, and a real
parser over fixture files are all cheap and deterministic. A dependency
reached over the network gets a **port** built for it first, and the
double then sits at that seam
([Module Design](/standards/modules/design.md) covers when a seam earns
its keep).

## Fakes for stateful dependencies

A dependency whose state or logic the tests exercise, and a dependency
several tests share, is faked rather than mocked.

A fake is a working, simplified implementation of a real interface, built
for testing: a store backed by an in-memory dict instead of a database, an
email sender that appends to a list instead of reaching SMTP. It has real
logic inside, just simpler. Stores, queues, and caches are the common
cases; a fake is written once and reused across the suite; and a fake
couples to the interface rather than the implementation, so the tests
using it survive refactoring.

## Fakes live in the test tree

A fake lives under `tests/`, in `tests/fakes.py` or beside the tests that
use it, and implements only the methods its callers use.

Production complexity is not replicated in a fake.

## Mocks at boundaries only

A mock stands at a boundary and at that boundary's entry point, and deeper
in the call chain a fake takes its place. The three boundaries a mock
stands at:

- **A side effect that is itself the outcome.** An email was sent, a
  metric recorded, an audit log written; the interaction is what the test
  observes.
- **A failure mode a fake cannot trigger.** A network timeout, a full
  disk, an API 500.
- **A non-deterministic or expensive external.** The LLM client, an
  external API, a cloud service.

`unittest.mock` is the tool. Where a function-level dependency genuinely
must be isolated, the mock sits at the function's entry point.

## Fixtures for setup and teardown

Construction and cleanup go through pytest fixtures rather than ad-hoc
setup code in a test body.

A fixture that constructs an object, a fake included, is the interface
contract the code under test is written against, and it constructs only
what the test needs.

## Narrowest fixture scope

A fixture takes the narrowest scope that works: function, the default,
then class, then module, then session.

State shared between tests causes flaky failures.
