---
name: sdd-tdd
description: Implement features via vertical-slice TDD against committed `Interface:` declarations. Use when an SDD-mode issue is in `phase/build` and the design has pinned `Interface:` lines, or when the user asks to drive implementation via red/green/refactor against an SDD spec.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD TDD

Vertical-slice TDD against the `Interface:` declarations committed in the design spec. Implementation proceeds in **chunks** — each chunk begins with a plan gate, runs an inner red/green/refactor loop per slice, and closes with a dedicated whole-chunk refactor pass and diff review.

## First steps

1. **Required reading — do not skip.** Use the Read tool on each file below before any other action. If any file is missing or unreadable, stop and surface that to the user — do not proceed without the standards loaded.
   - [Spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — keyword reference, coverage chain, ID format.
   - [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md) — pytest structure, naming, fixtures, behavioural focus.
   - [Python conventions](~/workspace/dev-playbook/standards/python-conventions.md) — docstring rules, fail-loudly, annotation style.
   - [Workflow standard](~/workspace/dev-playbook/standards/workflow.md) — labels, worktree convention, PR mechanics, spec-tools bootstrap caveat.

   After reading, post exactly this confirmation line to the user before proceeding: `Loaded: spec-standard, testing-conventions, python-conventions, workflow`.

   When considering an `Interface:` amendment (see "Spec amendment" below), also read [Lessons](~/workspace/spec-tools/sdd-standards/lessons.md) at that point.
2. **Run `pwd`.** The dispatcher cd's into the worktree before invoking this skill, but the env header's CWD was captured before that. Trust `pwd`, not the header — composing paths from a stale CWD lands outside the worktree.
3. **Require an issue number** in `$ARGUMENTS`. If empty, stop and tell the user to invoke via `/sdd <N>`.
4. Run `gh-show $ARGUMENTS` to load the issue. The body IS the contract.
5. If `pwd` did not already show a worktree path, resolve the worktree per the [workflow standard](~/workspace/dev-playbook/standards/workflow.md#branch-and-worktree).
6. Read the project's specs (`specs/functional_requirements/` and `specs/design/`, or flat-file equivalents).
7. Read the project's `CLAUDE.md`.
8. Read existing code under `src/` and tests under `tests/` — there may be partial work or stubs from prior cycles.
9. Run the test suite to see the current state.
10. Tell the user what you found, align on scope, then move to the plan gate for the first chunk.

## Mandatory plan gate

A **chunk** is a coherent piece of implementation work — typically the slices that cover one `dsn`, or a small cluster of tightly related `dsn`s. Implementation proceeds one chunk at a time; every chunk starts with a plan.

Before starting a chunk, present a plan covering:

- **Scope.** Which `dsn`(s) and which behaviours the chunk will cover.
- **Slice ordering.** The sequence of inner red/green/refactor slices you intend to drive.
- **Ambiguities.** Anything in the spec you anticipate needing to clarify.

Wait for explicit user approval. Silence is not approval.

## The chunk loop (outer)

For each approved chunk:

1. Run the inner slice loop until every behaviour in the chunk's scope is covered with passing tests.
2. **Whole-chunk refactor pass.** With the suite green, step back and review every module the chunk touched for refactor candidates not visible inside any single slice — duplication across modules, deeper-module opportunities now that several call sites exist, abstraction misalignments, primitive obsession. Run the test suite after each refactor step. Refactors that would change a committed `Interface:` or that surface structural problems beyond one module's seam are gated — see "Spec amendment" below.
3. Run the lint, format, and typecheck commands defined in `CLAUDE.md` or `Makefile`. Resolve any failures.
4. Run /commit. Pause for the user's diff review and approval.
5. Propose the plan for the next chunk and return to the plan gate. End the skill when the user signals no further chunks.

## The slice loop (inner)

Each slice is one test, one implementation, then a brief refactor.

**Red.** Pick one observable behaviour under one `req~…` or `dsn~…`. Write a single failing test exercising that behaviour through the public surface declared by the relevant `dsn`'s `Interface:`. Mark every test with `@pytest.mark.covers("<id>")` naming the closest upstream item — typically the `dsn` whose `Needs: utest` / `Needs: itest` declared the obligation. Run the suite to confirm the test fails for the expected reason.

**Stub on first contact.** When a test imports a symbol that has no stub yet, create the stub matching its `Interface:` declaration verbatim — same parameter names, kinds, annotations, and return annotation. Body is `raise NotImplementedError` for functions and methods, `pass` for `__init__`. Do not pre-stub symbols not yet under test.

**Green.** Write the minimal implementation that makes the failing test pass. Do not add code for behaviours the next test will exercise. Run the suite to confirm green.

**Refactor.** With the suite green, look for refactor candidates inside the module: extract duplication, deepen modules, simplify primitives. Run tests after each step. Refactors that would change a committed `Interface:` are gated — see "Spec amendment" below.

Refactor candidate catalogue:

- **Duplication** → Extract function/class
- **Long methods** → Break into private helpers (keep tests on public interface)
- **Shallow modules** → Combine or deepen
- **Feature envy** → Move logic to where data lives
- **Primitive obsession** → Introduce value objects
- **Existing code** the new code reveals as problematic

For test-quality patterns and mocking guidance, see [testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md).

## Spec amendment

When refactor pressure (per-slice or whole-chunk) would change a committed `Interface:`, or surfaces structural problems beyond what fits behind one module's seam, stop. The change goes through spec amendment — the SDD Triangle in action — not direct architecture work in this skill.

Describe the proposed amendment to the user: which `dsn` is affected, what the new `Interface:` would look like, what motivated the change. Wait.

The user decides whether to:

- Apply the amendment in this terminal — edit the spec (update `Interface:` lines; on revision, follow [spec-standard §3.3](~/workspace/spec-tools/sdd-standards/spec-standard.md#33-revision)). Then continue with stub, test, implementation in that order. During initial greenfield implementation no pinned consumers exist yet — edit in place at revision `0` and do not bump.
- Defer to a fresh `sdd-design` pass — do not edit the spec; pause this terminal until the design phase produces the amendment, then resume.
- Reject the change and direct a different approach.

Never edit a spec without an explicit approval gesture in this turn.

Bugs that surface during implementation are spec gaps. Flag the gap, propose the spec amendment that closes it, and wait for the same routing decision before changing the code.

## Closing the phase

When all chunks are complete, the suite is green, lint/format/typecheck pass, and the user has approved every diff:

1. **Final check sweep — leave the tree green.** Run the full test suite, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). The chunk loop runs these per-chunk, but a final whole-tree pass catches cross-chunk regressions and any drift since the last chunk. All must pass; if anything fails, fix it and re-run. Do not push a red branch.
2. Run /commit if there are uncommitted changes.
3. Push (the user runs this — YubiKey tap required): `git push -u origin <branch>`.
4. Open the PR: `gh pr create --body "Closes #<N> ..."`. The `Closes` token is mandatory.
5. Bump the issue's phase label:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase/build" --add-label "phase/review"
   ```
6. **Remind the user before exiting:** "After the PR merges, `git pull` on `main` (YubiKey tap required) and run `worktree-sweep` to clean up the worktree."

## Session handoff

A chunk may not fit in one session. Before stopping, post a comment on the issue documenting current state: which slices are done, which are next, any decisions made, any spec amendments pending. The next session's cold-start reads the issue body and the most recent comment.
