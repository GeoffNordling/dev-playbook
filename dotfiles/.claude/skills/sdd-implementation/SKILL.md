---
name: sdd-implementation
description: Implement features via vertical-slice TDD against committed `Interface:` declarations
disable-model-invocation: true
model: opus
effort: xhigh
---

# SDD Implementation

Vertical-slice TDD against the `Interface:` declarations committed in the design spec. Implementation proceeds in **chunks** — each chunk begins with a plan gate, runs an inner red/green/refactor loop per slice, and closes with a dedicated whole-chunk refactor pass and diff review. The user provides free-form input describing what to build or which area to focus on.

## Read first

- [Spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md) — keyword reference, coverage chain, ID format.
- [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioral focus.
- [Python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style, and the other code-level standards that apply to everything you write in this skill.

When considering an `Interface:` amendment (see "Spec amendment" below), also read [Lessons](~/workspace/dev-playbook/sdd-standards/lessons.md).

## First steps

1. Check for `<project_root>/.claude/sdd-handoff.md`. If it exists, read it.
2. Read the project's specs (`specs/functional_requirements/` and `specs/design/`, or their flat-file equivalents).
3. Read the project's `CLAUDE.md`.
4. Read existing code under `src/` and existing tests under `tests/` — there may be partial work or stubs from prior cycles.
5. Run the test suite to see the current state.
6. Tell the user what you found and align on scope. Then move to the plan gate for the first chunk.

## Working with the spec collection

We are bootstrapping `spec-tools`; deterministic spec validation is not available yet. Verify by hand: that each test's `@pytest.mark.covers(...)` ID exists in the spec, that stub signatures match each `Interface:` line verbatim, that every `Needs: utest` / `Needs: itest` declaration is satisfied by at least one marker-bearing test. A future revision of this skill will invoke `spec-tools` for `Interface:` validation and coverage checks.

## Mandatory plan gate

A **chunk** is a coherent piece of implementation work — typically the slices that cover one `dsn`, or a small cluster of tightly related `dsn`s. Implementation proceeds one chunk at a time, and every chunk starts with a plan.

Before starting a chunk, present a plan covering:

- **Scope.** Which `dsn`(s) and which behaviors the chunk will cover.
- **Slice ordering.** The sequence of inner red/green/refactor slices you intend to drive.
- **Ambiguities.** Anything in the spec you anticipate needing to clarify.

Wait for explicit user approval. Silence is not approval. Do not begin the inner slice loop until the chunk plan is approved.

## The chunk loop (outer)

For each approved chunk:

1. Run the inner slice loop (next section) until every behavior in the chunk's scope is covered with passing tests.
2. **Whole-chunk refactor pass.** With the suite green, step back and review every module the chunk touched for refactor candidates that were not visible inside any single slice — duplication across modules, deeper-module opportunities now that several call sites exist, abstraction misalignments, primitive obsession. This is a dedicated pass, distinct from the per-slice refactor inside the inner loop. Run the test suite after each refactor step. Refactors that would change a committed `Interface:` are gated — see "Spec amendment" below.
3. Run the lint, format, and typecheck commands defined in `CLAUDE.md` or `Makefile`. Resolve any failures.
4. Report to the user: what was implemented, any spec amendments made, any decisions warranting discussion. Pause for diff review and approval before commit.
5. Propose the plan for the next chunk and return to the plan gate. End the skill when the user signals no further chunks for this session.

## The slice loop (inner)

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behavior under one `req~…` or `dsn~…`. Write a single failing test that exercises that behavior through the public surface declared by the relevant `dsn`'s `Interface:`. Mark every test with `@pytest.mark.covers("<id>")` naming the closest upstream item — typically the `dsn` whose `Needs: utest` / `Needs: itest` declared the obligation. The marker is the spec-coverage invariant. Run the test suite to confirm the new test fails for the expected reason.

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
