---
name: sdd-red
description: Write tests from the spec in the red phase of spec-driven TDD
disable-model-invocation: true
---

# SDD Red

Write tests from the spec. This is the "red" phase of spec-driven TDD — tests are written to express requirements as executable behavior.

The user provides free-form input describing what feature or requirements to write tests for.

## Critical Rule — Test Isolation

Do NOT write real implementation code. Implementation happens in a separate agent session using `/sdd-green`.

Tests and implementation are written by separate agent contexts so that the tests express requirements independently from the code that satisfies them. This forces the implementation agent to write code that satisfies requirements as expressed in the tests, rather than writing tests that pass whatever code it happened to produce.

**Stubs are created by the design phase.** The `/sdd-design` skill produces interface stubs (modules, classes, function signatures) as part of its output. Tests import from these stubs. If a stub is missing or its signature needs to change, propose a spec or design amendment to the user rather than creating or modifying stubs directly.

**Modify the environment, don't work around it.** If the tests need something that doesn't exist (a fixture file, a directory structure, a test helper), create it. If a change requires updating the interface (adding a parameter, renaming a function), propose the change to the user. The functional spec and design spec are living documents; when the environment changes, update the specs to match. Always get user approval before modifying specs or interfaces.

## Workflow Context

This skill is part of a spec-driven TDD workflow following SDD conventions. It typically runs in parallel with `/sdd-green` in a separate terminal — red produces tests, green implements against them. The user controls pacing across both agents.

**Do not commit changes automatically.** Present your changes for the user to review the diffs. Only commit when the user explicitly asks.

## First Steps

1. Glob for `<skill_base_dir>/references/*.md` (where `<skill_base_dir>` is shown in "Base directory for this skill" at the top of this prompt) and read every file found. These references govern structure, naming, assertions, mocking patterns, and behavioral focus for all tests you write. If no files are found, tell the user that no reference files were found at that path and ask how to proceed.
2. Read the project's specs. Check for:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - `specs/design.md` or, if split, `specs/design/index.md`
   - The project's `CLAUDE.md` for project-specific testing conventions or overrides
   - Any existing test files to understand the project's testing patterns
3. Check for `tests/RED_STATUS.md` — a scratchpad tracking coverage progress, active patterns, and open questions for the red phase. If it exists, read it. Update it frequently as you work: after completing each requirement group, when patterns change, and when open questions are resolved or new ones arise. Keep it current and forward-looking — remove information that is no longer relevant.
4. Tell the user what you found and align on which requirements are in scope for this round of test writing.

## Mandatory Plan Gate

**Never write code without an approved plan.** Before producing any code — tests or implementation — present a written plan to the user that covers:

1. **Scope.** Which requirements or categories you will address in this pass.
2. **Approach.** How you intend to address them — key decisions, patterns, and trade-offs.

Wait for explicit user approval before writing any code. If the user asks questions or requests changes, revise the plan and re-present it. Do not treat silence as approval.

This is a hard gate. Skipping it — for any reason, including apparent simplicity or time pressure — is a process failure.

## How to Write Tests

Follow the testing conventions loaded in step 1.

**Contract-first when no code exists.** When writing tests before implementation, the tests define the interface contract. Keep it minimal: use the spec's language for names, only include parameters the spec implies, and don't invent configuration the spec doesn't mention. If you find yourself specifying constructor arguments that feel like implementation choices, you're over-prescribing — step back and test the behavior from further out.

**Note non-deterministic gaps.** When a requirement spans a non-deterministic boundary (LLM call, network request), decompose it: test the deterministic parts, note the non-deterministic gap in `RED_STATUS.md`.

## Pacing

The goal is to maximize both agentic efficiency and the value of human check-ins. The right step size is one where the human provides meaningful course corrections; not rubber-stamping every move, and not prescribing a full restart because the agent went too far off course. One requirement category (e.g., Discovery, Parsing) is the default unit of autonomous work between human reviews.

**One category at a time.** If the functional requirements or design doc are organized into categories or sections, do not attempt to cover them all in one pass. During the alignment step (First Steps, step 4), propose an ordering of categories to the user. Then work the first category only. After completing that category (tests written, committed, traced), stop and wait. The user will hand off to the green agent to implement and make the tests pass. Do not start the next category until the user confirms the green agent has finished and tells you to proceed.

**Test plan before test code.** Before writing any tests for a category, present a test plan to the user and get approval. The plan lists each test with its requirement ID, what it checks, and any fixture or environment changes needed. Do not write test code until the plan is approved.

Within a category, check whether implementation code already exists. This determines your per-requirement pacing; a single project will often have both situations.

- **Code exists:** batch by module or feature area. The design is stable; read the code and write tests across multiple related requirements in one pass.
- **No code exists:** one requirement at a time. Each test applies design pressure to the emerging interface, and you need that feedback loop to stay tight.

## Writing Tests

- **Every requirement in the design spec must have test coverage**, regardless of its obligation level (SHALL, SHOULD, or MAY). The design spec is the contract; if a requirement appears there, it must be tested. Non-mandatory requirements that were not included in the design spec do not need tests.
- Mark every test with the requirement ID it covers using `@pytest.mark.req("REQ-AREA-NNN")` (AREA is 3–6 uppercase letters, NNN is a 3-digit number, e.g. `@pytest.mark.req("REQ-PARSE-001")`). Every test SHALL reference at least one requirement ID. Many tests per requirement is normal (happy path, edge cases, error cases). Many requirements per test should be limited to integration or scenario tests that inherently span multiple behaviors.
- Use the **interview pattern**: if requirements are ambiguous about expected behavior, ask the user before writing tests that encode assumptions. Answers that reveal spec gaps or ambiguities SHALL be flagged to the user for spec updates, not handled ad hoc.
- **Prefer general over specific.** Derive test data from registries, configs, or the codebase rather than hardcoding specific names, IDs, or values that could change. Tests should survive additions, removals, and renames without edits. When a behavior applies to a class of things (e.g., all agents, all schemas), loop over the class rather than picking one example.
- **Every test must have a docstring** describing what it verifies.

## Output

- Test files that cover the in-scope requirements.
- Run the tests to confirm they execute without errors (import failures, syntax errors, fixture problems). Test *failures* (assertion errors) are expected and normal — this is the red phase. Tests that pass because the implementation already exists are a neutral observation, not a success. Do not celebrate passing tests or frame them as achievements. The success metric for this skill is accurate, complete coverage of the spec.
- Run `/Volumes/workplace/dev-tools/.venv/bin/sdd-trace` from the project root to verify all in-scope requirements have test coverage and all tests reference valid requirement IDs. The tool auto-detects `specs/` and `tests/` directories (override with `--specs`/`--tests` if needed). It exits 0 when every requirement is covered and no orphaned markers exist. Use `--detail <AREA> [<AREA> ...]` to drill into specific area codes if gaps are found (always a single invocation — never run the tool multiple times with different areas). Present the results to the user.
- **Run the project's lint, format, and typecheck commands before presenting your changes** (check `CLAUDE.md` or `Makefile` for the exact commands). When a check fails, self-correct rather than accumulating errors across tasks.
- Wait for user review before finishing.
