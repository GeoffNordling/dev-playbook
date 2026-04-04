---
name: sdd-design
description: Design system structure bridging functional requirements and implementation
disable-model-invocation: true
---

# SDD Design

Collaborate with the user to design the system's structure before implementation begins. The design spec is the bridge between the functional spec and the red/green implementation phase.

The [spec-driven-development standard](standards/spec-driven-development.md) (in the dev-playbook repo) defines what belongs in `design.md`, when it's warranted, and how it relates to ADRs. Follow those conventions.

**Do not commit changes automatically.** Present your changes for the user to review the diffs. Only commit when the user explicitly asks.

The user provides free-form input describing what they want to design or what feature they're working on.

## First Steps

1. **Run traceability check.** Run `/Volumes/workplace/dev-tools/.venv/bin/sdd-trace` from the project root. This shows a compact summary of requirement coverage. Use `--detail <AREA> [<AREA> ...]` to drill into specific area codes if needed (always a single invocation — never run the tool multiple times with different areas). Interpret the results based on the stage of design:
   - **Starting out** (no design spec yet): expect 0% coverage — every requirement will show as unmapped. This is normal. Use the list of unmapped requirements as your backlog of what needs designing.
   - **Mid-design** (design spec partially written): some requirements will be mapped, others won't. Focus the session on the unmapped ones — these are the gaps to fill next.
   - **Wrapping up** (design spec nearly complete): coverage should be approaching 100%. Any remaining gaps are what's left to address before the design is done.
   If the tool exits with code 2 (configuration error, e.g. no specs directory), that's fine — it means the project hasn't set up specs yet. Note it and continue.
2. Read the project's specs and architecture artifacts. Check for:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - `specs/design.md` or, if split, `specs/design/index.md`
   - `docs/adr/` for prior architectural decisions (check `README.md` for the index)
   - `diagrams/` for architecture diagrams (check `README.md` or `CLAUDE.md` for conventions, then read the diagram scripts)
   - The project's `CLAUDE.md`
3. Tell the user what you found and what you understand the current state to be. Include the traceability summary: how many requirements are mapped vs. unmapped, and which unmapped requirements are candidates for this session. If `design.md` already exists, summarize what's already there and ask what section to extend next. If it does not exist, align on what specifically is being designed before proceeding.

## Deciding Whether a Design Spec Is Needed

Ask yourself: would a red agent be forced to invent class names, module boundaries, or function signatures while writing tests? If yes, a design spec is needed. If the functional spec directly implies the implementation, it may be skipped.

## Drafting the Design Spec

- **Start with the data model.** Define entities, their fields, containment relationships, and ownership before discussing pipelines or modules. Then define behavior on objects (methods they own). The processing pipeline should emerge from how the objects compose, not the other way around.
- **Be precise about operations.** When a field is computed or aggregated, specify the exact operation (sum, min, max, count, derived). "Aggregated from X" is not a design; it defers the decision.
- **Stay at a moderate level of abstraction.** The design spec names modules, classes, their fields, and how they relate. It does not prescribe serialization formats, internal algorithms, or implementation details. When in doubt, propose the simpler option and let the user escalate complexity.
- **Prefer explicit structures over design pattern abstractions.** If a fixed containment hierarchy works, say that. Do not reach for Composite, Strategy, or other named patterns unless the problem genuinely requires that generality.
- **Keep the design doc forward-looking.** Only describe the current design. Do not reference discarded alternatives, prior iterations, or the reasoning path. That belongs in ADRs.
- **Order sections to follow the pipeline.** Sections should appear in the order they execute. If discovery happens before parsing, discovery comes first in the doc.
- Use the **interview pattern**: ask the user clarifying questions about architectural preferences before drafting anything. Incorporate answers into the design spec, not as side conversation.
- Draft or update `specs/design.md` (or files within `specs/design/` if split).
- Use RFC 2119 modal verbs (SHALL, SHOULD, MAY) consistently.
- Reference relevant ADRs for the reasoning behind individual decisions rather than re-explaining them.
- If a significant new architectural decision is made during this process, propose an ADR for it.
- Present the draft to the user and wait for approval. Iterate until they are satisfied.

## Output

This skill produces an updated design spec and interface stubs. No implementation code, no tests.

- An updated design spec (approved by the user), or a clear decision that no design spec is needed, with an explanation of why the functional spec is sufficient.
- **Interface stubs.** After the design spec is approved, create stub modules, classes, and functions matching the design spec's module layout and interfaces. Stubs define the interface shape only: function/method signatures with `raise NotImplementedError`, classes with empty bodies or `__init__` with `pass`, and modules with just enough to make `import` succeed. Stubs reflect the spec's vocabulary and the design doc's structure. The red agent writes tests against these stubs; the green agent replaces them with real code.
  - **Do not use `from __future__ import annotations`** unless a concrete forward reference requires it.
- **Run the project's lint, format, and typecheck commands before presenting your changes** (check `CLAUDE.md` or `Makefile` for the exact commands). When a check fails, self-correct rather than accumulating errors across tasks.
