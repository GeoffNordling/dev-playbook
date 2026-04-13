---
name: sdd-func-reqs
description: Write or update functional requirements
disable-model-invocation: true
model: opus
effort: high
---

# SDD Func Reqs

Help the user write or update functional requirements for the project. The user provides free-form input describing what they want to specify or what area needs updating.

## Agent Identity

The FIRST line of your FIRST message MUST be exactly:

```
<<<AGENT:sdd-func-reqs>>>
```

Output it verbatim with no other text on that line. This is a machine-readable sentinel for transcript consumers.

## First Steps

1. Check for a handoff file at `<project_root>/.claude/sdd-handoff.md`. If
   it exists, read it for issue context and scope.
2. Read the spec writing reference for spec conventions:
   `~/workspace/dev-playbook/standards/spec-driven-development/writing.md`
2. Read the project's existing specs if they exist:
   - `specs/functional_requirements.md` or, if split, `specs/functional_requirements/index.md` (then load relevant files based on the index)
   - The project's `CLAUDE.md`
3. Tell the user what you found — whether specs exist and their current state.

## Interview

Use the interview pattern to collaborate with the user on requirements. Ask clarifying questions about behavior, scope, and edge cases before drafting. The goal is to surface decisions and ambiguities early.

- If specs exist, identify what needs updating and propose changes.
- If no specs exist, scaffold `specs/functional_requirements.md` and draft requirements from the user's input.

## Drafting

- Write requirements following the spec format reference: EARS sentence templates with RFC 2119 modal verbs for prose, OFT Requirement-Enhanced Markdown for structure and traceability.
- Every requirement gets a unique OFT specification item ID in `type~name~revision` format (e.g., `req~auth.login-validation~1`). Use `req` as the type. See the spec format reference for naming rules and required keywords (`Status:`, `Covers:`, `Needs:`).
- Include an explicit out-of-scope section.
- Present the draft to the user and iterate until they are satisfied.

## Output

This skill produces spec documentation only — no code, no tests.

## Wrapping Up

When the user approves the final draft, commit your changes and push the branch.
