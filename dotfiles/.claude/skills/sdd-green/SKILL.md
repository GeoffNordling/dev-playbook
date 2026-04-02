---
name: sdd-green
description: Make tests pass in the green phase of spec-driven TDD
disable-model-invocation: true
---

# SDD Green

Make the tests pass. This is the "green" phase of spec-driven TDD — implementation code is written to satisfy existing tests.

The user provides free-form input describing what to implement or which area to focus on.

## Critical Rule

Do NOT modify tests. Tests were written by a separate agent session (`/sdd-red`) and represent the acceptance criteria derived from requirements. If a test seems wrong or unclear, stop and discuss with the user rather than changing it.

## Workflow Context

This skill is part of a spec-driven TDD workflow following SDD conventions. It typically runs in parallel with `/sdd-red` in a separate terminal — red produces tests, green implements against them. The user controls pacing across both agents.

Check for test files the red agent has produced before starting each implementation batch.

**Do not commit changes automatically.** Present your changes for the user to review the diffs. Only commit when the user explicitly asks.

## First Steps

1. Read the project's specs. Check for:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - `specs/design.md` or, if split, `specs/design/index.md`
   - The project's `CLAUDE.md`
2. Read existing code under `src/`. This may include full implementations, partial implementations, or stubs created by the red agent to make tests importable. Understand what already exists before writing anything.
3. Read the existing tests to understand what needs to pass. The tests define the behavioral contract — function names, parameters, and expected outputs are your interface specification. Ignore `tests/RED_STATUS.md` if it exists — that is the red agent's working scratchpad, not part of the test contract.
4. Run the tests to see the current state — which pass, which fail. Some tests may already pass against existing code; your scope is the failing tests.
5. Tell the user what you found and align on the scope of implementation before writing code.

## Mandatory Plan Gate

**Never write code without an approved plan.** Before producing any code — tests or implementation — present a written plan to the user that covers:

1. **Scope.** Which requirements or categories you will address in this pass.
2. **Approach.** How you intend to address them — key decisions, patterns, and trade-offs.

Wait for explicit user approval before writing any code. If the user asks questions or requests changes, revise the plan and re-present it. Do not treat silence as approval.

This is a hard gate. Skipping it — for any reason, including apparent simplicity or time pressure — is a process failure.

## Implementation

The goal is to maximize both agentic efficiency and the value of human check-ins. The right step size is one where the human provides meaningful course corrections; not rubber-stamping every move, and not prescribing a full restart because the agent went too far off course. One requirement category (e.g., Discovery, Parsing) is the default unit of autonomous work between human reviews.

- Work one requirement (or small group of related requirements) at a time. After each, run the tests to confirm progress — more tests should pass or remain passing.
- **Write the minimum code to make tests pass.** Do not add features, abstractions, or configurability beyond what the tests require. If only one test calls a function, that function doesn't need to handle five other cases.
- **Humble Object pattern at non-deterministic boundaries.** Some tests will mock non-deterministic components (LLM calls, external APIs). The mock point reveals where the boundary is. Keep the non-deterministic component as thin as possible — a narrow integration point surrounded by testable, deterministic logic. If you find yourself writing complex logic inside the non-deterministic layer that tests can't reach, refactor it out into a testable function.
- Follow the design spec if it exists. If none exists, make straightforward implementation choices and note any significant decisions for the user.
- When implementation diverges from the spec, flag the divergence to the user — the spec needs updating to reflect what was actually built. Do not edit the spec directly.

## Bug-Fix Loop

When a bug arises during development:

1. Flag to the user that the bug reveals a spec gap, describing the correct behavior
2. Implement the fix
3. Flag that a regression test is needed (`/sdd-red`)

Bugs are spec gaps, not just code errors. Each fix is an opportunity to make the spec more complete.

## Completion

- All tests in scope pass.
- Run `/Volumes/workplace/dev-tools/.venv/bin/sdd-trace` from the project root to verify coverage is intact. The tool auto-detects `specs/` and `tests/` directories (override with `--specs`/`--tests` if needed). It exits 0 when every requirement is covered and no orphaned markers exist. Use `--detail <AREA>` to drill into specific area codes if gaps are found. Verify that no previously covered requirements have lost coverage.
- **Run the project's lint, format, and typecheck commands before presenting your changes** (check `CLAUDE.md` or `Makefile` for the exact commands). When a check fails, self-correct rather than accumulating errors across tasks.
- Present a summary to the user: what was implemented, any spec updates made, any decisions that need discussion.
