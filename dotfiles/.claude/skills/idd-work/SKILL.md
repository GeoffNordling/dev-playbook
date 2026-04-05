---
name: idd-work
description: Dispatch and coordinate issue-driven development across SDD phases
disable-model-invocation: true
---

# IDD Work

Pick up, coordinate, and drive development work on a GitHub issue. This skill
is the dispatcher for issue-driven development; it owns the outer workflow
loop while the SDD agents own the inner phases (functional requirements,
design, red, green).

The user provides an issue number, URL, or description, plus any optional
context.

## First Steps

1. Read the development workflow standard; it governs this skill's behavior:
   - **Mac (Darwin):** `/Volumes/workplace/dev-playbook/standards/development-workflow.md`
   - **WSL:** `~/workspace/dev-playbook/standards/development-workflow.md`
2. Follow the **Session Handoff** sequence from that standard to reconstruct
   context from durable artifacts.
3. Read `CLAUDE.md` and check whether `specs/` exists (indicating SDD).
4. Present findings: the issue, any existing work, and the current state of
   durable artifacts. Recommend the next phase (see below). Wait for the
   user to confirm before proceeding.

## Scaffolding

If no branch or PR exists yet, scaffold them per the **Branch and Draft PR**
section of the development workflow standard. Get user approval first.

## Phase Recommendation

Based on the state of durable artifacts, recommend the next SDD phase:

- No functional requirements for this feature -> functional requirements
- Requirements exist but no design spec coverage -> design
- Design exists but tests are missing -> red and green (parallel; tell the
  user to open two terminals)
- Tests exist but failing -> green

Always wait for explicit user approval before proceeding.

## Handoff File

When the user approves a phase, write a handoff file at
`<project_root>/.claude/idd-handoff.md` (gitignored). The SDD agent reads
this file on startup for context.

The handoff file is a context briefing, not a log. Overwrite it entirely
each time. Format:

```markdown
# IDD Handoff

- **Issue:** #<number> - <title>
- **Branch:** <branch name>
- **PR:** #<pr number>
- **Phase:** <func-reqs | design | red-green | green>
- **Scope:** <what this phase should focus on>

## Context

<Brief summary of what has been done so far and what remains. Include
any decisions or constraints from the issue or prior phases that the
SDD agent needs to know.>
```

## Ongoing Coordination

This skill stays alive as the dispatcher terminal. When the user returns
after an SDD phase completes:

1. Re-orient from durable artifacts (follow the Session Handoff sequence
   again).
2. Update the PR description per the **PR Description** section of the
   development workflow standard.
3. Recommend the next phase or declare the issue complete.
4. Write a new handoff file if another phase is needed.

Always wait for user confirmation before recommending or writing.

## Completion

When all phases are done and tests pass:

1. Update the PR description with a final summary.
2. Tell the user the PR is ready for review.
