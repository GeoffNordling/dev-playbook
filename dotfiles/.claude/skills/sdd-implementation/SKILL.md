---
name: sdd-implementation
description: Implement features via vertical-slice TDD against committed `Interface:` declarations
disable-model-invocation: true
model: opus
effort: xhigh
---

# SDD Implementation

Vertical-slice TDD — one test, one implementation, refactor — against the `Interface:` declarations committed in the design spec. The user provides free-form input describing what to build or which area to focus on.

## Read first

- [Spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md) — keyword reference, coverage chain, ID format.
- [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.

When considering an `Interface:` amendment (see "Spec amendment" below), also read [Lessons](~/workspace/dev-playbook/sdd-standards/lessons.md).

## First steps

1. Check for `<project_root>/.claude/sdd-handoff.md`. If it exists, read it.
2. Read the project's specs (`specs/functional_requirements/` and `specs/design/`, or their flat-file equivalents).
3. Read the project's `CLAUDE.md`.
4. Read existing code under `src/` and existing tests under `tests/` — there may be partial work or stubs from prior cycles.
5. Run the test suite to see the current state.
6. Tell the user what you found and align on scope (which requirement or category to slice next).

## Working with the spec collection

We are bootstrapping `spec-tools`; deterministic spec validation is not available yet. Verify by hand: that each test's `@pytest.mark.req(...)` ID exists in the spec, that stub signatures match each `Interface:` line verbatim, that every `Needs: utest` / `Needs: itest` declaration is satisfied by at least one marker-bearing test. A future revision of this skill will invoke `spec-tools` for `Interface:` validation and coverage checks.

## The loop

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior under one `req~…` or `dsn~…`. Write a single failing test that exercises that behavior through the public surface declared by the relevant `dsn`'s `Interface:`. Mark every test with `@pytest.mark.req("req~name~N")` naming the requirement it covers — the marker is the spec-coverage invariant. Run the test suite to confirm the new test fails for the expected reason.

**Stub on first contact.** When a test imports a symbol that has no stub yet, create the stub matching its `Interface:` declaration verbatim — same parameter names, kinds, annotations, and return annotation. Body is `raise NotImplementedError` for functions and methods, `pass` for `__init__`. Do not pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass. Do not add code for behaviors the next test will exercise. Run the test suite to confirm green.

**Refactor.** With the suite green, look for refactor candidates inside the module: extract duplication, deepen modules, simplify primitives. See [refactoring.md](~/workspace/dev-playbook/dotfiles/.agents/skills/tdd/refactoring.md) for the catalogue. Run tests after each refactor step. Refactors that would change a committed `Interface:` are gated — see "Spec amendment" below.

**`AgentReview:` inline.** When implementing a `feat` / `req` / `dsn` that carries `AgentReview:`, verify the commitment against the artifact (code, prompt, etc.) the prose names before declaring the slice done. Surface drift to the user.

For test-quality patterns and mocking guidance, [tests.md](~/workspace/dev-playbook/dotfiles/.agents/skills/tdd/tests.md) and [mocking.md](~/workspace/dev-playbook/dotfiles/.agents/skills/tdd/mocking.md) from the /tdd skill bundle are useful background.

When refactor pressure suggests a structural change bigger than one module — multiple `dsn`s, a different decomposition entirely — ask the user to open a fresh terminal and invoke /improve-codebase-architecture there. Bring back its proposals through the spec-amendment path.

## Spec amendment

When a refactor would change a committed `Interface:`, stop. Describe the proposed amendment to the user: which `dsn` is affected, what the new `Interface:` would look like, what motivated the change. Wait.

The user decides whether to:

- Apply the amendment in this terminal — you then edit the spec (bump the `dsn`'s revision, update `Interface:` lines, update any downstream `dsn`s whose `Covers:` pinned the old revision) and continue with stub, test, implementation in that order.
- Defer to a fresh `sdd-design` pass — do not edit the spec; pause this terminal until the design phase produces the amendment, then resume.
- Reject the change and direct a different approach.

Never edit a spec without an explicit approval gesture in this turn.

Bugs that surface during implementation are spec gaps. Flag the gap to the user, propose the spec amendment that closes it, and wait for the same routing decision before changing the code.

## Completion

- All in-scope tests pass; lint, format, typecheck commands defined in `CLAUDE.md` or `Makefile` pass.
- Summary for the user: what was implemented, any spec amendments made, any decisions warranting discussion.
- Wait for user review before commit.
