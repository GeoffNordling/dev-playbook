---
name: sdd-agentreviews
description: Verify `AgentReview:` commitments against the artifacts they name and report drift. Use when closing an SDD issue (final-check sweep before opening the PR), or when the user asks to audit `AgentReview:` lines for a chosen scope of items.
disable-model-invocation: false
model: opus
effort: xhigh
---

# SDD AgentReviews

Verify `AgentReview:` commitments against the artifact (code, prompt, behaviour) each names. Dispatches review subagents per item and reports drift.

Two invocation paths:

- From `sdd-tdd`'s closing-the-phase step. The caller computes the in-scope item IDs from the branch diff and passes them in the invocation.
- Directly by the user, scoped to whatever they specify (a focused area, items changed since a date, the whole project).

## Read first

- [Spec standard §6.9 `AgentReview:`](~/workspace/spec-tools/sdd-standards/spec-standard.md#69-agentreview) — what `AgentReview:` is, when it is the right primitive, what its prose conveys.

## First steps

1. Read the project's `CLAUDE.md`.
2. **Determine scope.** If the invoking context provides an explicit list of item IDs (e.g., from `sdd-tdd`: "audit these items: dsn~..., req~..."), audit exactly that list. Otherwise ask the user — by area, by date range, whole project, etc.

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
