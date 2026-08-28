---
type: General-Sheet
title: External Skill Verdicts
description: The workspace's verdict on every external skill it has evaluated — skill, verdict, date, and reason, grouped by source
---

# External Skill Verdicts

One row per external skill the workspace has evaluated: the verdict, the date
of the last evaluation, and the reason. Three verdicts:

- **verbatim** — adopted: copied into `dotfiles/dot-claude/skills/`
  unmodified.
- **adapt** — adopted: copied likewise, with modifications.
- **reject** — not adopted.

An adopted copy is owned from the moment it lands
([0025](/docs/decisions/0025-retire-verbatim-skill-adoption.md)): it answers
to every workspace standard and drifts from upstream freely. Re-evaluation is
manual — the user reads upstream when so moved and updates the rows by hand.
The row is the whole record of a ruling.

## mattpocock/skills

| Skill | Verdict | Date | Reason |
|---|---|---|---|
| ask-matt | reject | 2026-08-08 | A hand-maintained prose router competes with the factory graph |
| claude-handoff | reject | 2026-08-01 | The authored `handoff` mirrors upstream's production `handoff`, which is the correct end state |
| code-review | reject | 2026-08-08 | Its two-axis workflow duplicates `code-pr-review` and the factory's review nodes, and is wired to upstream's tracker plumbing |
| codebase-design | **verbatim** | 2026-08-08 | The single home for the workspace's architecture vocabulary, and a dependency of `improve-codebase-architecture` |
| diagnosing-bugs | **verbatim** | 2026-08-08 | Builds the reproduction loop before hypothesizing, then ranks loop techniques and tests falsifiable hypotheses |
| domain-modeling | **verbatim** | 2026-08-01 | — |
| git-guardrails-claude-code | reject | 2026-08-01 | The PAT makes the guarded operations impossible |
| grill-me | reject | 2026-08-01 | Redundant with `grill-with-docs` |
| grill-with-docs | **adapt** | 2026-08-08 | A thin front door onto `/grilling` + `/domain-modeling`; the one modification enables model invocation for the four workspace call sites |
| grilling | **verbatim** | 2026-08-01 | Round-by-round frontier questioning in a mandated question-and-recommendation format |
| handoff | reject | 2026-08-01 | Harvested near-verbatim into the authored `handoff` |
| implement | reject | 2026-08-01 | The factory graph does this with more rigor |
| improve-codebase-architecture | **verbatim** | 2026-08-08 | The workspace's only architecture-scanning capability — hot-spot scoping, subagent exploration under the deletion test, then grilling the candidate picked |
| loop-me | reject | 2026-08-01 | Belongs to mission-control |
| migrate-to-shoehorn | reject | 2026-08-01 | TypeScript-only |
| prototype | **verbatim** | 2026-08-01 | The logic branch builds a self-contained HTML demo rather than a terminal TUI |
| research | **verbatim** | 2026-08-01 | — |
| resolving-merge-conflicts | reject | 2026-08-08 | Not necessary |
| scaffold-exercises | reject | 2026-08-01 | Bound to upstream's course business |
| setup-matt-pocock-skills | reject | 2026-08-01 | Its job is served by workspace standards |
| setup-pre-commit | reject | 2026-08-01 | A competing Node toolchain for a problem `pre-commit` solves |
| setup-ts-deep-modules | reject | 2026-08-01 | TypeScript-only |
| tdd | reject | 2026-08-08 | Its mandatory user stop breaks the autonomous build node, its loop excludes refactoring, and `software-factory/tdd.md` is the workspace's TDD procedure |
| teach | reject | 2026-08-01 | Personal productivity, outside the factory's domain |
| to-questionnaire | reject | 2026-08-08 | A solo developer has no third party to send a questionnaire to |
| to-spec | reject | 2026-08-08 | Too complicated to land today, and it may conflict with `wayfinder` and the authored `wayfinder-to-build` |
| to-tickets | reject | 2026-08-08 | Too complicated to land today, and it may conflict with `wayfinder` and the authored `wayfinder-to-build` |
| triage | reject | 2026-08-08 | Its label and role vocabulary were rejected outright; the redundancy check and verify-the-claim moves already live in `intake` |
| wait-what | **verbatim** | 2026-08-08 | A three-line corrective: re-pitch the last message in Simplified Technical English, using `CONTEXT.md` vocabulary |
| wayfinder | **verbatim** | 2026-08-01 | — |
| wizard | reject | 2026-08-28 | Nothing in the workspace references it, and its `template.sh` is past the shell standard's glue-only boundary |
| writing-beats | reject | 2026-08-01 | Journey-based structure fights the workspace's current-state reference prose |
| writing-for-agents | **verbatim** | 2026-08-08 | The craft layer for any document an agent consumes |
| writing-fragments | reject | 2026-08-01 | Idea capture lives in mission-control |
| writing-shape | reject | 2026-08-08 | Sits in upstream's unpromoted `in-progress` tier |

## marimo-team/skills

| Skill | Verdict | Date | Reason |
|---|---|---|---|
| marimo-batch | reject | 2026-08-28 | Referenced by nothing in the workspace |
| marimo-notebook | reject | 2026-08-28 | Referenced by nothing in the workspace |
