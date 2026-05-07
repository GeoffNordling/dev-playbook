---
name: sdd-review
description: Audit `AgentReview:` commitments across the project at scale and report drift
disable-model-invocation: true
model: opus
effort: xhigh
---

# SDD Review

Periodic maintenance audit of every `AgentReview:` commitment in the project. Dispatches review subagents per item and reports drift between the spec's commitment and the artifact (code, prompt, behavior) it names.

This is not a development-flow skill. Inline `AgentReview:` checks for items being actively built happen in `sdd-implementation`. This skill is the project-wide sweep, run periodically rather than per cycle.

## Read first

- [Spec standard §6.9 `AgentReview:`](~/workspace/spec-tools/sdd-standards/spec-standard.md#69-agentreview) — what `AgentReview:` is, when it is the right primitive, what its prose conveys.

## First steps

1. Read the project's `CLAUDE.md`.
2. Confirm with the user the scope of this audit run — whole project or a subset (e.g., one area, items changed since last audit).

## Working with the spec collection

We are bootstrapping `spec-tools`; the AgentReview inventory is not available programmatically yet. Until then, enumerate by grepping `specs/` for `AgentReview:` lines and reading the surrounding item context. A future revision of this skill will invoke `spec-tools` for the inventory directly.

## Audit

For each in-scope item carrying `AgentReview:`:

1. Read the item's `Description:`, every `AgentReview:` entry, and any artifact paths the prose names.
2. Open the named artifacts. Verify the commitment in the prose holds — the model is instructed correctly, the prompt contains the directive, the convention is followed.
3. For non-trivial verification, dispatch a subagent via the Agent tool with the item's `AgentReview:` text as the task description. Prefer read-only exploration agents.
4. Record one of: **ok** (commitment still honored), **drift** (related but weakened), **broken** (the referenced artifact no longer exists, no longer contains the expected content, or directly contradicts the prose). Capture file:line references to any evidence and a one-paragraph justification per review.

Parallelize dispatches when records are independent — most reviews touch different files and can run concurrently.

## Output

A drift report listing each `AgentReview:` item and its status. For each finding name the item ID, the artifact, and the specific deviation. Close with a summary: total reviews, counts per state, and recommended next actions (which `dsn` items to update, which commitments to revise, which artifacts to fix).

Do not auto-fix anything. This skill observes and reports; the user decides what to change.

## When not to use this skill

- **Before the spec and code exist.** Run after the design layer has landed and at least one implementation pass has shipped.
- **In place of tests.** If a commitment can be deterministically tested, use `Needs: utest` / `Needs: itest` instead of `AgentReview:`.
- **During CI.** This is a deliberate human-in-the-loop check, not an automation gate.
