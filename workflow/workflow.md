# Workflow

Standard worfklow for how ideas become merged PRs in a workspace repo.

# Main concepts that we need to flesh out in documentation somewhere in ~/workflow/ directory:
All pre-existing documentation, workflow standards, skills, tooling, etc. is open for modification, deletion, and addition. We are re-writing the workflow and are not bound by prior convention.

Workflow is based on a state machine using GH Issues. A workflow graph of nodes and edges is clearly defined in a central location.

GH Issue labels are defined in a central location and relayed to GH via [bootstrap-labels](~/workspace/dev-playbook/tools/bin/bootstrap-labels).

Human and agents collaborate to move issues along the graph from beginning to end, with a spectrum of permissions and authority to take actions and transitions. This is supported by well-organized and factored /skills and /tools scripts. Many /skills and /tools will need modification to fit the new workflow.

Aim for maximum "finger on the wheel" agentic development using Claude Code's "claude agents" view. Fully "hands off the wheel" AFK development is out of scope since we rely on "interactive" Claude Code sessions using "claude agents" view (documented in agent-view-adoption.md). UPDATE THIS REFERENCE IMMEDIATELY PER WORKSPACE FILE REFERENCE STANDARD

Since Claude Code "claude agents" view relies on worktrees, we need to understand how worktrees are created, entered, existed, and deleted. Our old workflow relied on manual worktree creation and cleanup; we now expect to use to "claude agents" native worktree tooling.

Current system security contraints require user yubikey tap for both `git pull` and `git push`. We are open to relaxing this requirement but will keep it in place tentatively while we develop the workflow.

Document and intentionally scope permissions granted to Claude Code agents.

Explore "sandboxing" methods (Claude Code native and third-party alternatives such as Pocock's sandcastle, etc.). Have not explored these at all yet. Not sure if they are useful.

The `/improve-codebase-architecture` skill seems very useful but was not integrated in the old workflow. Look for opportunities to integrate into new workflow.

# Old, pre-existing sections that need new consideration. We may delete or modify these based on how they fit into the new standard.

## Issue body format (the brief is the body)

The issue body IS the agent brief. Use this format:

```markdown
**Summary:** one-line description

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate

**Blocked by:** #<issue-number> (or "None")
```

Brief principles, applied when writing or revising:

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. Do not reference file paths or line numbers — they go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

## Vertical-slice rules (when one idea becomes many issues)

Break a plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.

Publish issues in dependency order so the `Blocked by` field can reference real issue numbers.