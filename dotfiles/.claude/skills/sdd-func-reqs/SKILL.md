---
name: sdd-func-reqs
description: Write or update functional requirements
disable-model-invocation: true
model: opus
effort: high
---

# SDD Func Reqs

Help the user write or update functional requirements for the project.

Before starting, read this reference end to end. If it is missing, stop and tell the user:

- [Spec format walkthrough](~/workspace/dev-playbook/sdd-standards/spec-format.md) — how RFC 2119 obligations, EARS sentence templates, OFT Requirement-Enhanced Markdown, and workspace extensions combine in a spec file. The walkthrough links into each per-standard document as needed.

Throughout the rest of this skill it is referred to as the *spec format walkthrough*.

The user provides free-form input describing what they want to specify or what area needs updating.

## First Steps

1. Check for a handoff file at `<project_root>/.claude/sdd-handoff.md`. If it exists, read it for issue context and scope.
2. Read the project's existing specs if they exist:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - The project's `CLAUDE.md`
3. Tell the user what you found — whether specs exist and their current state.

## Interview

Use the interview pattern to collaborate with the user on requirements. Ask clarifying questions about behavior, scope, and edge cases before drafting. The goal is to surface decisions and ambiguities early.

- If specs exist, identify what needs updating and propose changes.
- If no specs exist, scaffold `specs/functional_requirements.md` and draft requirements from the user's input.

## Drafting

- Write requirements following the spec format walkthrough: EARS sentence templates with RFC 2119 modal verbs for prose, OFT Requirement-Enhanced Markdown for structure and traceability.
- Every requirement gets a unique OFT specification item ID in `type~name~revision` format (e.g., `req~auth.login-validation~1`). Use `req` as the type. See the spec format walkthrough for naming rules and required keywords (`Status:`, `Covers:`, `Needs:`).
- Ask the user whether anything belongs in an out-of-scope section. If yes, capture it. If no, include the section with an explicit `NA` so it is clear the question was asked and answered.
- Present the draft to the user and iterate until they are satisfied.

## Output

This skill produces spec documentation only — no code, no tests.

## Wrapping Up

When the user approves the final draft, commit your changes and push the branch.
