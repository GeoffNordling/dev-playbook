---
type: Decision-Record
title: Tooling Verdicts from the 2026-05 Third-Party Audit
description: Preserve the 2026-05-08 tooling audit's verdicts and revisit conditions — claude-code-transcripts, roborev, Superset, and two Superpowers watch-threads — from the retired third-party survey
date: 2026-05-08
---

# Tooling Verdicts from the 2026-05 Third-Party Audit

On 2026-05-08 a third-party tooling audit reached verdicts that were recorded only in a survey document (`docs/third-party-survey.md`, retired and deleted 2026-08-01). This record, written at the retirement, preserves the verdicts and revisit conditions that existed nowhere else. The survey's Pocock and Superpowers adoption decisions are already covered by [0001](0001-adopt-matt-pocock-conventions.md), [0003](0003-decline-superpowers.md), [0004](0004-remove-pocock-direct-dependency.md), and [0006](0006-harvest-pocock-prototype-and-handoff.md); agentsview (adopted, in regular use) is documented in the workspace's live docs.

## claude-code-transcripts (Simon Willison) — not adopting; keep as parsing reference

Soft-abandoned upstream (last commit 2026-02-12; the `web` subcommand broken by Anthropic API changes). Valuable not as a dependency but as the canonical inventory of why flattening Claude Code's session JSONL is hard: branching via `parentUuid` (file order ≠ logical order; walk the DAG, keep the live leaf), sidechain traffic interleaved in the same file, the content-block zoo with results paired to calls by ID not position, injected wrappers (`<system-reminder>` etc.) in user content, compaction events replacing turns with summaries, tool-result blowups needing truncation, and continuous undocumented format drift.

Lessons banked for any future workspace flattener: aim for good-enough-for-LLM-input, not fidelity; prefer hook-based capture (`SessionStart`, `PostToolUse`, `Stop`…) over JSONL post-processing for going-forward capture; and pull parsing logic from upstream PRs #82 (markdown export), #93 (web path against the new APIs), #91 (Cowork + refactor), #88 (PDF/DOCX) before they bitrot.

## roborev (Wes McKinney) — not adopting

Per-commit continuous review priced for someone with effectively free tokens; for a workspace paying retail on solo work, per-commit auto-review is the wrong economic shape. Kept as the reference point for "what does code review look like when tokens are free?"

## Superset — blocked on platform

macOS-only desktop orchestrator isolating each parallel agent in its own git worktree. Revisit if a Linux build ships, or if the parallel-worktree-per-agent pattern becomes worth reimplementing against bare `git worktree` plus a launcher script.

## Superpowers watch-threads (supplementing 0003)

Two threads from the declined framework carry conditions [0003](0003-decline-superpowers.md) does not:

- **`requesting-code-review`** — a self-contained review-dispatch template; revisit if `/sdd-agentreviews` (which is `AgentReview:`-only) proves insufficient as the workspace's only review skill.
- **`systematic-debugging`** — 4-phase root-cause investigation bundling three reusable sub-patterns: root-cause-tracing, defense-in-depth, condition-based-waiting. The named sub-patterns are preserved here as the harvest pointer.
