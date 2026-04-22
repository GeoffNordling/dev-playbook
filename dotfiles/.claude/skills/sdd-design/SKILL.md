---
name: sdd-design
description: Design system structure from functional requirements
disable-model-invocation: true
model: opus
effort: xhigh
---

# SDD Design

Collaborate with the user to produce the design spec for a feature before implementation begins.

Before starting, read every `.md` file under `~/workspace/dev-playbook/sdd-standards/` and `~/workspace/dev-playbook/sdd-tools/` end-to-end. They are the authoritative source for spec structure, the design dimensions, the verification fields, and the CLIs you will invoke during the session. Do not proceed until you have read them.

When your work is complete and approved, commit your changes and push the branch.

The user provides free-form input describing what they want to design or what feature they're working on.

## First Steps

1. **Check for handoff file.** Check for `<project_root>/.claude/sdd-handoff.md`. If it exists, read it for issue context and scope.
2. **Run spec checks.** Run `uv run pytest -m spec` from the project root. Interpret the results based on the stage of design:
   - **Starting out** (no design spec yet): the trace check will fail because `Needs:` declarations in the functional requirements are not satisfied — this is expected. The OFT output lists uncovered requirements; use that as your backlog of what needs designing.
   - **Mid-design** (design spec partially written): some requirements will be covered, others won't. Focus the session on what OFT reports as uncovered.
   - **Wrapping up** (design spec nearly complete): all checks should pass. Any remaining failures indicate gaps to close.
   If `pytest-sdd` is not configured in `pyproject.toml`, the plugin is silently inactive — that's fine for a project just getting started.
3. **Read the project's specs.** Check for:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - `specs/design.md` or, if split, `specs/design/index.md`
   - `docs/adr/` for prior architectural decisions (check `README.md` for the index)
4. **Survey the existing `dsn` surface.** If a design spec exists, run `sdd-index` from the project root to get a one-line-per-`dsn` catalog grouped by dimension. This is your map of what is already committed before you add to it. Skip this step if no design spec exists yet.
5. **Tell the user what you found** and what you understand the current state to be. Include the traceability summary: how many requirements are mapped vs. unmapped, and which unmapped requirements are candidates for this session. If `design.md` already exists, summarize what's already there and ask what section to extend next. If it does not exist, align on what specifically is being designed before proceeding.

## Brownfield Reconnaissance

Before deciding on or drafting anything, read the existing code the feature touches. For each new capability, work out whether it extends an existing class or module, or introduces a new one, and what public surface each functional requirement needs. Record the reasoning for each extend-vs-new and surface choice in the corresponding dsn's `Rationale:` field when you later draft it.

## Deciding Whether a Design Spec Is Needed

Ask yourself: would a red agent be forced to invent class names, module boundaries, or function signatures while writing tests? If yes, a design spec is needed. If the functional spec directly implies the implementation, it may be skipped.

## Drafting the Design Spec

- **Use the interview pattern.** Ask the user clarifying questions about architectural preferences before drafting anything. Incorporate answers into the design spec, not as side conversation.
- **Work the dimensions in canonical order.** Draft Data first, then API Shape, then Algorithms, then Composition. Each dimension builds on the ones before it.
- **Draft or update `specs/design.md`** (or files within `specs/design/` if split).
- **Be precise about operations.** When a field is computed or aggregated, specify the exact operation (sum, min, max, count, derived). "Aggregated from X" is not a design; it defers the decision.
- **Prefer explicit structures over design-pattern abstractions.** If a fixed containment hierarchy works, say that. Do not reach for Composite, Strategy, or other named patterns unless the problem genuinely requires that generality.
- **Do not restate functional requirements.** Reference the `req`'s OFT ID for traceability rather than repeating behavior the functional spec already pins down.
- **Keep the design doc forward-looking.** Only describe the current design. Discarded alternatives and reasoning paths belong in ADRs.
- **Non-mandatory requirements are optional to include.** `SHOULD` and `MAY` requirements do not need to appear in the design spec. However, any requirement included in the design spec — regardless of obligation level — must be implemented and tested like any other designed requirement. Including a non-mandatory requirement is a commitment to deliver it.
- **Reference relevant ADRs** for the reasoning behind individual decisions rather than re-explaining them.
- **Propose an ADR** if a significant new architectural decision emerges during the session.
- **Present the draft to the user** and wait for approval. Iterate until they are satisfied.

## Navigating a Growing `dsn` Collection

As the design spec grows past what fits comfortably in a single prompt, two CLIs compress it to the view you need:

- **`sdd-index`** — one line per `dsn` (id, title, source location) grouped by dimension. Run it when deciding whether to extend an existing `dsn` vs. add a new one, when surveying an unfamiliar dimension before drafting, or when you need the whole commitment inventory at a glance.
- **`sdd-atlas`** — full body of every `dsn` grouped by dimension, including all keyword fields. Run it when `sdd-index`'s one-liners are not enough — e.g., to check for overlap with existing `Interface:` declarations before drafting a new one, or to read `Rationale:` fields before reusing a nearby abstraction.

Rule of thumb: reach for `sdd-index` first; escalate to `sdd-atlas` only when titles don't answer the question.

## Output

This skill produces an updated design spec and interface stubs. No implementation code, no tests.

- **Updated design spec.** Approved by the user, or a clear decision that no design spec is needed with an explanation of why the functional spec is sufficient.
- **Interface stubs.** After the design spec is approved, create stub modules, classes, and functions matching each `Interface:` declaration in the spec. Stub signatures match the `Interface:` entry exactly — same parameter names, kinds, annotations, and return annotation. `pytest-sdd`'s interface validator fails at pytest collection time if a stub diverges from its committed `Interface:`. Stub bodies are minimal: `raise NotImplementedError` for functions/methods, empty `__init__` with `pass` for classes, and just enough in modules to make `import` succeed. The red agent writes tests against these stubs; the green agent replaces them with real code.
  - **Preserve old implementations.** When stubbing something that replaces an existing implementation, comment out the old code and bracket it with `# --- old implementation ---` / `# --- end old implementation ---` markers above the `raise NotImplementedError`. Do not delete the old code; the red and green agents benefit from seeing the prior logic.
  - **Do not use `from __future__ import annotations`** unless a concrete forward reference requires it and the user explicitly approves.
- **Mark temporarily unused imports.** Commenting out old implementations can leave imports unused until the green agent writes the real code. Add `# noqa: F401 (stub)` to these imports so pre-commit hooks and linters don't remove them. The green agent is responsible for removing all `noqa: F401 (stub)` comments as a cleanup step when it finishes.
- **Run the project's lint, format, and typecheck commands before presenting your changes** (check `CLAUDE.md` or `Makefile` for the exact commands). When a check fails, self-correct rather than accumulating errors across tasks.
