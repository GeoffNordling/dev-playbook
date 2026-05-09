---
name: to-issues
description: Break a plan, spec, or PRD into independently-grabbable issues on the project issue tracker using tracer-bullet vertical slices. Use when user wants to convert a plan into issues, create implementation tickets, or break down work into issues.
disable-model-invocation: false
model: opus
effort: xhigh
---

# To Issues

Break a plan into independently-grabbable issues using vertical slices (tracer bullets).

For issue-tracker commands, triage roles, and the issue body template, see the [issue management standard](~/workspace/dev-playbook/standards/issue-management.md).

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes an issue reference (issue number, URL, or path) as an argument, fetch it from the issue tracker and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Issue titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

### 3. Draft vertical slices

Break the plan into **tracer bullet** issues per the [vertical-slice breakdown rules](~/workspace/dev-playbook/standards/issue-management.md#vertical-slice-breakdown).

Each issue is a thin vertical slice that cuts through ALL integration layers end-to-end, NOT a horizontal slice of one layer. Slices may be 'HITL' (require human interaction — architectural decisions, design reviews) or 'AFK' (can be implemented and merged without human interaction). Prefer AFK over HITL where possible.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **User stories covered**: which user stories this addresses (if the source material has them)

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Publish the issues to the issue tracker

For each approved slice, publish a new issue using the [issue body template](~/workspace/dev-playbook/standards/issue-management.md#issue-body-template). Apply the `needs-triage` triage label so each issue enters the normal triage flow.

Publish issues in dependency order (blockers first) so you can reference real issue identifiers in the "Blocked by" field.

Do NOT close or modify any parent issue.
