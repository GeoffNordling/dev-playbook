---
name: sdd-design
description: Design system structure from functional requirements
disable-model-invocation: true
model: opus
effort: high
---

# SDD Design

Collaborate with the user to design the system's structure before implementation begins. The design spec is the bridge between the functional spec and the red/green implementation phase.

Before starting, read both of these references end to end:

- [Spec writing reference](~/workspace/dev-playbook/sdd-standards/writing.md) — OFT format for spec items, including the `Interface:` keyword.
- [Design-layer standard](~/workspace/dev-playbook/sdd-standards/design-layer.md) — the four principles that govern design items, coverage chain, and revision policy.

Throughout the rest of this skill they are referred to as the *writing reference* and the *design-layer standard*.

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
4. **Tell the user what you found** and what you understand the current state to be. Include the traceability summary: how many requirements are mapped vs. unmapped, and which unmapped requirements are candidates for this session. If `design.md` already exists, summarize what's already there and ask what section to extend next. If it does not exist, align on what specifically is being designed before proceeding.

## Brownfield Reconnaissance

Before deciding on or drafting anything, read the existing code the feature touches. For each new capability, work out whether it extends an existing class or module, or introduces a new one, and what public surface each functional requirement needs. Record the reasoning for each extend-vs-new and surface choice in the corresponding dsn's `Rationale:` field when you later draft it.

## Deciding Whether a Design Spec Is Needed

Ask yourself: would a red agent be forced to invent class names, module boundaries, or function signatures while writing tests? If yes, a design spec is needed. If the functional spec directly implies the implementation, it may be skipped.

## Drafting the Design Spec

- **Start with the data model.** Define entities, their fields, containment relationships, and ownership before discussing pipelines or modules. Then define behavior on objects (methods they own). The processing pipeline should emerge from how the objects compose, not the other way around.
- **Be precise about operations.** When a field is computed or aggregated, specify the exact operation (sum, min, max, count, derived). "Aggregated from X" is not a design; it defers the decision.
- **Author `Interface:` entries for committed public surfaces.** When a dsn commits to a public callable, class, or method, declare its signature with an `Interface:` entry. One signature per line; repeat for multiple related signatures (e.g., a class plus its public methods). Format and annotation convention are in the writing reference.
- **Prefer explicit structures over design pattern abstractions.** If a fixed containment hierarchy works, say that. Do not reach for Composite, Strategy, or other named patterns unless the problem genuinely requires that generality.
- **Do not restate functional requirements.** The design spec documents decisions that are not already specified in the functional requirements: module boundaries, data structures, configuration choices, mechanism details. If a functional requirement fully specifies a behavior (e.g., exit code values, output format rules), the design spec should reference the requirement's OFT ID for traceability but not repeat the specification. Only add design-spec text when there is a genuine design decision beyond what the functional spec prescribes.
- **Keep the design doc forward-looking.** Only describe the current design. Do not reference discarded alternatives, prior iterations, or the reasoning path. That belongs in ADRs.
- **Order sections to follow the pipeline.** Sections should appear in the order they execute. If discovery happens before parsing, discovery comes first in the doc.
- **Use the interview pattern.** Ask the user clarifying questions about architectural preferences before drafting anything. Incorporate answers into the design spec, not as side conversation.
- **Draft or update `specs/design.md`** (or files within `specs/design/` if split).
- **Use RFC 2119 modal verbs** (SHALL, SHOULD, MAY) consistently.
- **Structure design items as OFT spec items.** Use `dsn` type IDs (e.g., `dsn~auth.login-validation~1`). Each design item `SHALL` include a `Covers:` link to the `req` item(s) it satisfies and a `Needs:` declaration for required downstream coverage (typically `utest` and/or `itest`). See the writing reference for the full item anatomy.
- **Non-mandatory requirements are optional to include in design.** SHOULD and MAY requirements do not need to appear in the design spec. However, any requirement that is included in the design spec — regardless of its obligation level — must be implemented and tested like all other designed requirements. Including a non-mandatory requirement in design is a commitment to deliver it.
- **Reference relevant ADRs** for the reasoning behind individual decisions rather than re-explaining them.
- **Propose an ADR** if a significant new architectural decision is made during this process.
- **Present the draft to the user** and wait for approval. Iterate until they are satisfied.

## Output

This skill produces an updated design spec and interface stubs. No implementation code, no tests.

- **Updated design spec.** Approved by the user, or a clear decision that no design spec is needed with an explanation of why the functional spec is sufficient.
- **Interface stubs.** After the design spec is approved, create stub modules, classes, and functions matching each `Interface:` declaration in the spec. Stub signatures match the `Interface:` entry exactly — same parameter names, kinds, annotations, and return annotation. `pytest-sdd`'s interface validator fails at pytest collection time if a stub diverges from its committed `Interface:`. Stub bodies are minimal: `raise NotImplementedError` for functions/methods, empty `__init__` with `pass` for classes, and just enough in modules to make `import` succeed. The red agent writes tests against these stubs; the green agent replaces them with real code.
  - **Preserve old implementations.** When stubbing something that replaces an existing implementation, comment out the old code and bracket it with `# --- old implementation ---` / `# --- end old implementation ---` markers above the `raise NotImplementedError`. Do not delete the old code; the red and green agents benefit from seeing the prior logic.
  - **Do not use `from __future__ import annotations`** unless a concrete forward reference requires it and the user explicitly approves.
- **Mark temporarily unused imports.** Commenting out old implementations can leave imports unused until the green agent writes the real code. Add `# noqa: F401 (stub)` to these imports so pre-commit hooks and linters don't remove them. The green agent is responsible for removing all `noqa: F401 (stub)` comments as a cleanup step when it finishes.
- **Run the project's lint, format, and typecheck commands before presenting your changes** (check `CLAUDE.md` or `Makefile` for the exact commands). When a check fails, self-correct rather than accumulating errors across tasks.
