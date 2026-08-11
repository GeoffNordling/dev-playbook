---
type: Standard
title: Testing Conventions
description: Default pytest conventions — structure, behavioral focus, test doubles, fixtures, and humble objects
---

# Testing Conventions

These are default testing conventions. Individual projects may supercede.

## Framework

Use pytest. All test files follow the `test_*.py` naming convention.

## Organization

- **Mirror source structure.** Test files mirror the source directory layout: `src/auth/login.py` -> `tests/auth/test_login.py`. This scales naturally and avoids naming collisions. The mirror — flat, or beneath a recognized scope directory — is the one accepted location; the package path is always required.
- **Scope directories.** A suite may interpose one recognized scope directory between `tests/` and the mirror: `unit` and `integration` each mirror `src/` beneath them (`tests/unit/auth/test_login.py`). A third, `tests/agent_review/`, holds judgment gate tests ([cache-gate.md](/standards/judgments/cache-gate.md)); their free-form stems are never measured against source modules. The set is fixed — any other directory in that position is a misplacement, not a scope.
- **Conftest hierarchy.** Place `conftest.py` at each directory level for fixtures relevant to that scope. Root `conftest.py` holds shared fixtures; subdirectory `conftest.py` files hold domain-specific fixtures.

## Test structure

- **Arrange-Act-Assert.** Every test has three clear sections: set up the conditions, perform the action, verify the result. Separate them with blank lines for readability.
- **One concept per test.** Each test verifies one behavior or scenario. Multiple assertions are fine when they all verify aspects of the same concept.
- **Descriptive names.** Test names read like behavior descriptions: `test_login_rejects_expired_token`, not `test_login_2`. The name alone conveys what the test verifies.
- **No logic in tests.** No if/else, no try/except in test bodies. Tests are boring and linear.
- **Expected values come from outside the code.** A known-good literal, a worked example, or the spec supplies the expected value. A *tautological* test recomputes it the way the code under test computes it, so it passes by construction and can never disagree with the code.

## Behavioral focus

Tests verify **what** the system does, not **how** it does it. This is the single most important principle in this document.

- **Access only public names.** Tests exercise identifiers without a leading underscore. Private helpers (`_foo`, `_Tokenizer`) are reached through the public interfaces that call them. Python dunder protocol methods (`__init__`, `__iter__`, etc.) count as public.
- **Assert on observable outputs.** Return values, state changes (records stored, files written), raised exceptions. Never assert on internal state, private attributes, or implementation details.
- **Assert on outcomes, not call sequences.** Prefer "the record is in the store" over "insert was called once with these arguments." When using mocks, assert on the minimum necessary to verify the contract; do not over-specify call counts, argument shapes, or call ordering unless the ordering is part of the contract.
- **Name by capability, not mechanism.** `test_request_includes_trace_id`, not `test_structlog_processor_adds_trace_id`. The test should survive an implementation swap without changes.
- **Replace, don't layer.** Once tests cover a module through its own interface, the unit tests on the smaller pieces underneath are waste — delete them rather than keeping both layers.

## The humble object pattern

When testing systems with non-deterministic components (LLM calls, network requests, randomness), apply the Humble Object pattern: extract all testable logic away from the non-deterministic boundary, leaving the non-deterministic part as thin as possible.

**Test the deterministic machinery:**
- Input parsing and validation
- Routing and dispatch logic
- Prompt/request assembly
- Output/response parsing
- Formatting and delivery

**Do not test the non-deterministic decision itself.** "Does the LLM give a good answer?" is an evaluation question, not a test question. Measure it through observability and evals.

## Test doubles

Choose the lightest test double that verifies the behavior under test: a real object, a fake, or a mock. A dependency reached over the network gets a **port** built for it first, and the double then sits at that seam.

### Real objects (integration tests)

Use the real implementation when it is cheap and deterministic. A real database in a temp directory, an in-process HTTP server, and real parsers operating on fixture files are all examples. Integration tests that exercise the real dependency give the highest confidence but are slower and harder to isolate.

### Fakes (the default for dependencies with state or logic)

A fake is a working, simplified implementation of a real interface, built for testing. It has real logic inside; just simpler. A store backed by an in-memory dict instead of a real database, an email sender that appends to a list instead of hitting an SMTP server.

**Prefer fakes when:**
- The dependency has state or logic that tests need to exercise (stores, queues, caches).
- Multiple tests share the same dependency; a fake is written once and reused across the suite.
- Tests need to survive refactoring; fakes couple to the interface, not the implementation.

Fakes live in the test directory (e.g., `tests/fakes.py` or alongside the tests that use them). They only implement the methods that callers actually use; they do not replicate production complexity.

**Fakes as fixtures.** Fakes are often provided through pytest fixtures. A fixture that constructs a fake implementation serves as the interface contract for the code under test.

### Mocks (side effects, failures, thin boundaries)

Use `unittest.mock` to:
- **Verify a side effect happened**; an email was sent, a metric was recorded, an audit log was written. The interaction itself is the observable outcome.
- **Simulate failure modes** that are hard to trigger with a fake; network timeouts, disk full, API 500s.
- **Stub a non-deterministic or expensive boundary**; the LLM client, an external API, a cloud service. The Humble Object pattern identifies these boundaries.

**Do not mock internal implementation details.** Needing a mock deep inside the code under test signals a design problem — extract an interface and use a fake instead. Where a function-level dependency genuinely must be isolated, mock at the boundary (the function's entry point), not deep in the call chain.

### Ports (services you own, reached over the network)

A service you own but call over the network — an internal API, a queue consumer — has no local stand-in to swap in and is too slow to call for real. Give it a **port**: the interface at the seam, owned by the calling module. The logic stays in that module; the transport is an injected **adapter** — an HTTP, gRPC, or queue client in production, an in-memory adapter in tests. The `/codebase-design` skill covers when a seam earns its keep.

## Fixtures and setup

- **Use fixtures for setup and teardown.** Standardize construction and cleanup through pytest fixtures rather than ad-hoc setup code in test bodies.
- **Narrowest scope.** Use the narrowest fixture scope that works: function (default) > class > module > session. Shared state between tests causes flaky failures.
- **Fixtures define the contract.** When writing tests before implementation, fixtures that construct objects (including fakes) serve as the interface contract for the green agent. Keep them minimal; only the parameters the spec implies.

