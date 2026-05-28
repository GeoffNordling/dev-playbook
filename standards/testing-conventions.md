# Testing Conventions

These are default testing conventions. Individual projects may supercede.

## Framework

Use pytest. All test files follow the `test_*.py` naming convention.

## Organization

- **Mirror source structure.** Test files mirror the source directory layout: `src/auth/login.py` -> `tests/auth/test_login.py`. This scales naturally and avoids naming collisions.
- **Conftest hierarchy.** Place `conftest.py` at each directory level for fixtures relevant to that scope. Root `conftest.py` holds shared fixtures; subdirectory `conftest.py` files hold domain-specific fixtures.
- **Coverage markers.** Every test is marked with the spec item it covers: `@pytest.mark.covers("<id>")`. The ID names the closest upstream item — whichever `feat`, `req`, or `dsn` declared `Needs: utest` (or `Needs: itest`); typically a `dsn`. This is the test's `Covers:` line, expressed in code, and enables traceability verification via `pytest-sdd`. See [sdd-standards/spec-standard.md — ID](~/workspace/spec-tools/sdd-standards/spec-standard.md#22-id) for the format.

## Test Structure

- **Arrange-Act-Assert.** Every test has three clear sections: set up the conditions, perform the action, verify the result. Separate them with blank lines for readability.
- **One concept per test.** Each test verifies one behavior or scenario. Multiple assertions are fine when they all verify aspects of the same concept.
- **Descriptive names.** Test names read like behavior descriptions: `test_login_rejects_expired_token`, not `test_login_2`. The name should tell you what the test does without reading the body.
- **No logic in tests.** No if/else, no try/except in test bodies. Tests are boring and linear.

## Behavioral Focus

Tests verify **what** the system does, not **how** it does it. This is the single most important principle in this document.

- **Access only public names.** Tests exercise identifiers without a leading underscore. Private helpers (`_foo`, `_Tokenizer`) are reached through the public interfaces that call them. Python dunder protocol methods (`__init__`, `__iter__`, etc.) count as public.
- **Assert on observable outputs.** Return values, state changes (records stored, files written), raised exceptions. Never assert on internal state, private attributes, or implementation details.
- **Assert on outcomes, not call sequences.** Prefer "the record is in the store" over "insert was called once with these arguments." When using mocks, assert on the minimum necessary to verify the contract; do not over-specify call counts, argument shapes, or call ordering unless the ordering is part of the contract.
- **Name by capability, not mechanism.** `test_request_includes_trace_id`, not `test_structlog_processor_adds_trace_id`. The test should survive an implementation swap without changes.

## The Humble Object Pattern

When testing systems with non-deterministic components (LLM calls, network requests, randomness), apply the Humble Object pattern: extract all testable logic away from the non-deterministic boundary, leaving the non-deterministic part as thin as possible.

**Test the deterministic machinery:**
- Input parsing and validation
- Routing and dispatch logic
- Prompt/request assembly
- Output/response parsing
- Formatting and delivery

**Do not test the non-deterministic decision itself.** "Does the LLM give a good answer?" is an evaluation question, not a test question. Measure it through observability and evals.

## Test Doubles

There are three kinds of test doubles. Choose the lightest one that verifies the behavior you care about.

### Real objects (integration tests)

Use the real implementation when it is cheap and deterministic. A real database in a temp directory, an in-process HTTP server, and real parsers operating on fixture files are all examples. Integration tests that exercise the real dependency give the highest confidence but are slower and harder to isolate.

### Fakes (the default for dependencies with state or logic)

A fake is a working, simplified implementation of a real interface, built for testing. It has real logic inside; just simpler. A store backed by an in-memory dict instead of a real database, an email sender that appends to a list instead of hitting an SMTP server.

**Prefer fakes when:**
- The dependency has state or logic that tests need to exercise (stores, queues, caches).
- Multiple tests share the same dependency; a fake is written once and reused across the suite.
- You want tests that survive refactoring; fakes couple to the interface, not the implementation.

Fakes live in the test directory (e.g., `tests/fakes.py` or alongside the tests that use them). They only implement the methods that callers actually use; they do not replicate production complexity.

**Fakes as fixtures.** Fakes are often provided through pytest fixtures. A fixture that constructs a fake implementation serves as the interface contract for the code under test.

### Mocks (side effects, failures, thin boundaries)

Use `unittest.mock` when you need to:
- **Verify a side effect happened**; an email was sent, a metric was recorded, an audit log was written. The interaction itself is the observable outcome.
- **Simulate failure modes** that are hard to trigger with a fake; network timeouts, disk full, API 500s.
- **Stub a non-deterministic or expensive boundary**; the LLM client, an external API, a cloud service. The Humble Object pattern identifies these boundaries.

**Do not mock internal implementation details.** If you need to mock deep inside your own code to test something, the design likely needs refactoring; extract an interface and use a fake instead. When you must isolate a function-level dependency within your own code, mock at the boundary (the function's entry point), not deep in the call chain.

## Fixtures and Setup

- **Use fixtures for setup and teardown.** Standardize construction and cleanup through pytest fixtures rather than ad-hoc setup code in test bodies.
- **Narrowest scope.** Use the narrowest fixture scope that works: function (default) > class > module > session. Shared state between tests causes flaky failures.
- **Fixtures define the contract.** When writing tests before implementation, fixtures that construct objects (including fakes) serve as the interface contract for the green agent. Keep them minimal; only the parameters the spec implies.

