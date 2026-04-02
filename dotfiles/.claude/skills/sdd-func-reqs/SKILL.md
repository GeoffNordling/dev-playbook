---
name: sdd-func-reqs
description: Write or update functional requirements for the project
disable-model-invocation: true
---

# SDD Func Reqs

Help the user write or update functional requirements for the project. The user provides free-form input describing what they want to specify or what area needs updating.

## First Steps

1. Read the spec-driven-development standard for spec conventions:
   - **Mac (Darwin):** `/Volumes/workplace/dev-playbook/standards/spec-driven-development.md`
   - **WSL:** `~/workspace/dev-playbook/standards/spec-driven-development.md`
2. Read the project's existing specs if they exist:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - The project's `CLAUDE.md`
3. Tell the user what you found — whether specs exist and their current state.

## Interview

Use the interview pattern to collaborate with the user on requirements. Ask clarifying questions about behavior, scope, and edge cases before drafting. The goal is to surface decisions and ambiguities early.

- If specs exist, identify what needs updating and propose changes.
- If no specs exist, scaffold `specs/functional_requirements.md` and draft requirements from the user's input.

## Drafting

- Write requirements in EARS notation with RFC 2119 modal verbs, as prescribed by the spec-driven-development standard.
- Every requirement gets a unique, stable `REQ-{AREA}-{NNN}` identifier (AREA is 3–6 uppercase letters, NNN is a 3-digit number).
- Include an explicit out-of-scope section.
- Present the draft to the user and iterate until they are satisfied.

## Output

This skill produces spec documentation only — no code, no tests.
