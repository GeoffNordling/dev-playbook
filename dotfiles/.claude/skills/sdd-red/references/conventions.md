# Testing Conventions

These are default testing conventions. The project's `CLAUDE.md` may override any of these.

## Framework

Use pytest. All test files follow the `test_*.py` naming convention.

## Organization

- **Mirror source structure.** Test files mirror the source directory layout: `src/auth/login.py` -> `tests/auth/test_login.py`. This scales naturally and avoids naming collisions.
- **Conftest hierarchy.** Place `conftest.py` at each directory level for fixtures relevant to that scope. Root `conftest.py` holds shared fixtures; subdirectory `conftest.py` files hold domain-specific fixtures.
- **Requirement markers.** Every test is marked with the requirement it covers: `@pytest.mark.req("REQ-XXX-NNN")`. This enables traceability verification via `sdd-trace`.

## Test Structure

- **Arrange-Act-Assert.** Every test has three clear sections: set up the conditions, perform the action, verify the result. Separate them with blank lines for readability.
- **One concept per test.** Each test verifies one behavior or scenario. Multiple assertions are fine when they all verify aspects of the same concept.
- **Descriptive names.** Test names read like behavior descriptions: `test_login_rejects_expired_token`, not `test_login_2`. The name should tell you what broke without reading the test body.
- **No logic in tests.** No if/else, no try/except in test bodies. Tests are boring and linear.

## Behavioral Focus

Tests verify **what** the system does, not **how** it does it. This is the single most important principle in this document.

- **Assert on observable outputs.** Return values, side effects (messages sent, records written), raised exceptions. Never assert on internal state, private attributes, or implementation details.
- **Name by capability, not mechanism.** `test_request_includes_trace_id`, not `test_structlog_processor_adds_trace_id`. The test should survive an implementation swap without changes.
- **Test behavior, not implementation.** Assert on inputs, outputs, and side effects. Do not assert on internal state or call sequences.

## The Humble Object Pattern

When testing systems with non-deterministic components (LLM calls, network requests, randomness), apply the Humble Object pattern: extract all testable logic away from the non-deterministic boundary, leaving the non-deterministic part as thin as possible.

**Test the deterministic machinery:**
- Input parsing and validation
- Routing and dispatch logic
- Prompt/request assembly
- Output/response parsing
- Formatting and delivery

**Do not test the non-deterministic decision itself.** "Does the LLM give a good answer?" is an evaluation question, not a test question. Measure it through observability and evals.

The mock point IS the boundary. Mock the non-deterministic component to test everything around it.

## Fixtures and Setup

- **Use fixtures for setup and teardown.** Standardize construction and cleanup through pytest fixtures rather than ad-hoc setup code in test bodies.
- **Narrowest scope.** Use the narrowest fixture scope that works: function (default) > class > module > session. Shared state between tests causes flaky failures.
- **Fixtures define the contract.** When writing tests before implementation, fixtures that construct objects serve as the interface contract for the green agent. Keep them minimal — only the parameters the spec implies.

## Mocking

- **Mock boundaries, not internals.** Mock external services (APIs, databases, third-party libraries). Do not mock your own code — if you need to mock internal modules to test something, the design likely needs refactoring.
- **Non-deterministic components are natural mock boundaries.** Mock the LLM client, HTTP client, or external API to test everything around it.
