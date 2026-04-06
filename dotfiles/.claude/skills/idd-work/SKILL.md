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

## Agent Identity

The FIRST line of your FIRST message MUST be exactly:

```
<<<AGENT:idd-work>>>
```

Output it verbatim with no other text on that line. This is a machine-readable sentinel for transcript consumers.

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

GitHub requires at least one commit on the branch before a PR can be created.
Create an empty commit (e.g., `git commit --allow-empty`) and push before
running `gh pr create`.

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

The handoff file is a context briefing, not a design brief. Give the agent
the context it needs to make good decisions; do not make those decisions for
it. State the problem, the current state, and any hard constraints. Do not
prescribe the solution, enumerate implementation steps, or tell the agent
which files, fields, or modules to change. Overwrite it entirely each time.

Format:

```markdown
# IDD Handoff

- **Issue:** #<number> - <title>
- **Branch:** <branch name>
- **PR:** #<pr number>
- **Phase:** <func-reqs | design | red-green | green>
- **Scope:** <one-sentence description of what this phase covers>

## Context

<Brief summary of what has been done so far and what remains. Include
hard constraints, decisions from prior phases, and things to look out
for that are relevant to the scope of the agent's session.>
```

## Reviewing Agent Output

When an SDD agent finishes, review its commits for correctness and scope.
Understand what each phase is expected to produce:

- **Func-reqs agent**: updates `specs/functional_requirements.md` only.
- **Design agent**: updates `specs/design.md` and may also write
  implementation stubs (new files, new fields, `raise NotImplementedError`
  bodies). This is expected; stubs give the red agent something to write
  tests against.
- **Red agent**: writes tests that fail against the stubs.
- **Green agent**: implements the stubs so tests pass.

Flag only genuinely wrong changes (incorrect logic, unrelated file
modifications, spec contradictions). Trust the agent's judgment on
approach and organization.

If the review is clean, proceed directly: present your review, recommend
the next phase, and write the handoff file in one response. Do not wait
for user approval between reviewing and writing the handoff. If you find
something wrong or ambiguous that needs the user's input, stop and
escalate before writing the handoff.

## Ongoing Coordination

This skill stays alive as the dispatcher terminal. When the user returns
after an SDD phase completes:

1. Re-orient from durable artifacts (follow the Session Handoff sequence
   again).
2. Update the PR description per the **PR Description** section of the
   development workflow standard.
3. Recommend the next phase or declare the issue complete.
4. Write a new handoff file if another phase is needed.

### After Green Phase — Cleanup Check

Grep the branch diff for `# noqa: F401 (stub)` markers. The design agent
adds these to suppress lint on imports that are unused until stubs are
implemented. After the green phase, the imports should be live; remove the
`# noqa` comments. If any import is still unused, investigate why.

### After Green Phase — Operational Review

Before declaring the issue complete, review the operational impact of the
changes. Ask: "if someone pulls main after this merges, does everything
just work?" Look for:

- Data files, databases, or caches that are incompatible with the new code
- Config changes, new environment variables, or new dependencies
- Anything that requires manual action beyond `git pull`

If the answer is "no, something breaks," fix it before moving on.

### E2E Verification

After the green phase, if the project has real data or representative
inputs available, run the actual code against them — not just unit tests.
Pick a representative sample and verify the full pipeline produces correct
output. Unit tests check contracts; e2e checks that the system actually
works. If no real data is available, note this to the user and skip.

Wait for user confirmation before running E2E verification.

### Git Hygiene

Before closing the loop, verify the working tree is fully clean and pushed:

1. Run `git status` to check for uncommitted or untracked changes. SDD
   agents sometimes make changes without committing them.
2. If there are uncommitted changes, review, commit, and push them.
3. Confirm `git status` shows a clean tree and the branch is up to date
   with the remote.

## Completion

When all phases are done and tests pass:

1. Update the PR description with a final summary.
2. Delete the handoff file (`<project_root>/.claude/idd-handoff.md`).
3. Tell the user the PR is ready for review.
4. Wait for the user to confirm the PR is merged and the branch is deleted,
   then check out `main` and pull.
