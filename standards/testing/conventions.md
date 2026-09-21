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

The reasoning behind the rules is the
[Test Design Explanation](/standards/testing/explanation.md).

## pytest

A governed repo's Python test suite runs on pytest.

`testing.pytest` · deterministic

## Test file naming

Every test file in the suite is named `test_*.py`.

`testing.test-file-naming` · deterministic

## Mirror source structure

A `test_*.py` file under `tests/` whose name, with the `test_` prefix
removed, is the file name of a module under `src/` other than an
`__init__.py` sits at that module's mirror: `tests/`, then the module's
directory path below `src/`, then the file name with `test_` prefixed, so
that `src/auth/login.py` is tested at `tests/auth/test_login.py`; or at
that same path beneath one of the two scope directories `unit` and
`integration`, as `tests/unit/auth/test_login.py`. Where the file name
belongs to more than one module under `src/`, the mirror of any one of
them satisfies the rule.

`testing.mirror-source-structure` · deterministic

## Conftest hierarchy

A fixture lives in the `conftest.py` of the narrowest directory whose tests
use it.

`testing.conftest-hierarchy` · deterministic

## Arrange-Act-Assert

The body of a `test_*` function sets up its conditions, then performs the
one action under test, then verifies the result, in that order and with no
setup after the action.

`testing.arrange-act-assert` · stochastic

## One concept per test

Each test verifies one behavior or scenario, and every assertion in it
verifies a facet of that one behavior.

`testing.one-concept-per-test` · stochastic

## No logic in tests

The body of a `test_*` function holds no `if`/`else` statement and no
`try`/`except` statement, except inside a function or a class defined
within that body.

`testing.no-logic-in-tests` · deterministic

## Expected values come from outside the code

A test's expected value is a known-good literal, a worked example, or the
spec, and never a value the test recomputes the way the code under test
computes it.

`testing.expected-values-come-from-outside-the-code` · stochastic

## Access only public names

A test reaches a module that is not itself a test module only through
identifiers that do not begin with an underscore: not an imported name, not
a segment of an imported module path, and not an attribute reached through
an imported name. An identifier
that begins and ends with a double underscore, such as `__init__` or
`__iter__`, is public. A module is a test module where any segment of its
dotted path is `tests` or `conftest` or begins with `test_`.

`testing.access-only-public-names` · deterministic

## Assert on observable outputs

A test's assertions are on observable outputs: return values, state changes
such as a record stored or a file written, and raised exceptions.

`testing.assert-on-observable-outputs` · stochastic

## Assert on outcomes, not call sequences

Where a test uses a mock, its assertion is the minimum that verifies the
contract — "the record is in the store" rather than "insert was called once
with these arguments" — unless a call count, an argument shape, or a call
ordering is itself the contract.

`testing.assert-on-outcomes-not-call-sequences` · stochastic

## Name by capability, not mechanism

A test's name states the capability under test and survives an
implementation swap: `test_request_includes_trace_id`, not
`test_structlog_processor_adds_trace_id`.

`testing.name-by-capability-not-mechanism` · stochastic

## Replace, don't layer

Once a module is covered through its own interface, the unit tests on the
smaller pieces beneath it are deleted rather than kept.

`testing.replace-dont-layer` · stochastic

## No test of a non-deterministic decision

No test asserts on the output of a non-deterministic component such as an
LLM call, a network request, or a source of randomness.

`testing.no-test-of-a-non-deterministic-decision` · stochastic

## The lightest double

A dependency is doubled with the lightest thing that verifies the behavior
under test — a real object, then a fake, then a mock — and a real
implementation that is cheap and deterministic is used as it is.

`testing.the-lightest-double` · stochastic

## Double at the port

Where the code under test reaches a dependency over the network, the test
doubles the port that code defines for the dependency rather than the
network client itself.

`testing.double-at-the-port` · stochastic

## Fakes for stateful dependencies

A dependency whose state or logic the tests exercise, and a dependency
several tests share, is faked rather than mocked.

`testing.fakes-for-stateful-dependencies` · stochastic

## One fake per interface

The suite holds one fake for an interface, and every test that doubles that
interface uses it.

`testing.one-fake-per-interface` · stochastic

## Fakes live in the test tree

A fake lives under `tests/`, in `tests/fakes.py` or beside the tests that
use it.

`testing.fakes-live-in-the-test-tree` · stochastic

## Fakes implement only what callers use

A fake implements only the methods its callers call.

`testing.fakes-implement-only-what-callers-use` · stochastic

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

`testing.mocks-at-boundaries-only` · stochastic

## The mocking library

A mock in the suite is built with `unittest.mock`.

`testing.the-mocking-library` · deterministic

## Fixtures for setup and teardown

Construction and cleanup go through pytest fixtures rather than ad-hoc
setup code in a test body.

`testing.fixtures-for-setup-and-teardown` · stochastic

## Narrowest fixture scope

A fixture takes the narrowest scope that works: function, the default, then
class, then module, then session.

`testing.narrowest-fixture-scope` · stochastic
