---
name: sdd-review
description: Check AgentReview commitments against the code and report drift
disable-model-invocation: true
model: opus
effort: high
---

# SDD Review

Walk every `AgentReview:` field across the project's design specs, compare each prose commitment against the current system state, and report which commitments are still honored, which are drifting, and which are broken. This is the non-test verification channel for design-layer commitments that cannot be deterministically unit-tested — see [extensions.md — Verification coverage](~/workspace/dev-playbook/sdd-standards/extensions.md#verification-coverage--extension) for the field definition.

This skill is reporting, not validation. It does not gate CI and does not block commits.

## First steps

1. **Run `sdd-review`** from the project root. Capture its output. Each `## \`dsn~...\`` block is one review target with a source location, its dimension section, and one or more `- ` review prose bullets.
2. **If the inventory is empty** (`No AgentReview: fields found`), tell the user so and stop. There is nothing to check.
3. **Summarize the inventory for the user** — count of dsn items, count of review prose entries — before dispatching anything. Ask whether to proceed across the full inventory or a filtered subset (e.g., only items in a specific dimension or a specific subsystem).

## Dispatch one review agent per dsn record

For each `## \`dsn~...\`` record the user accepts, spawn an Explore or general-purpose agent with a focused prompt:

- Provide the dsn id, source location, dimension section, and every review prose entry as context.
- Tell the agent its job is to check whether the current code, prompts, docs, or configuration satisfy what the prose commits to. Paths named in the prose (e.g., `src/prompts/agent.md`) are the natural starting points — the agent reads the referenced artifact and compares it to the prose.
- The agent reports one of three states per review: **ok** (commitment still honored), **drift** (related but weakened), **broken** (the referenced artifact no longer exists, no longer contains the expected content, or directly contradicts the prose).
- Ask for file:line references to any evidence, and a one-paragraph justification per review.

Parallelize dispatches when the records are independent — most reviews touch different files and can run concurrently.

## Report

Aggregate the agents' findings into a single report back to the user:

- One section per dsn record, under the same `## \`dsn~...\`` heading the CLI emitted.
- Within each section, one line per review — state badge (ok / drift / broken), the review prose, and the agent's evidence.
- Close with a summary: total reviews, counts per state, and recommended next actions (which dsn items to update, which commitments to revise, which artifacts to fix).

Do not auto-fix anything. This skill observes and reports; the user decides what to change.

## When not to use this skill

- **Before the spec and code exist.** Run after the design layer has landed and at least one implementation pass has shipped.
- **In place of tests.** If a commitment can be deterministically tested, use `Needs: utest` / `Needs: itest` instead of `AgentReview:`.
- **During CI.** This is a deliberate human-in-the-loop check, not an automation gate.
