---
type: General-Sheet
title: External Skill Verdicts
description: The standing verdict on every skill in each external upstream skill package, one row per skill, with the record that ruled it
---

# External Skill Verdicts

The workspace's standing verdict on every skill in each external upstream skill
package it tracks — one row per upstream skill, stating where that skill stands
today. A recurring sweep reads this ledger, compares it against the upstream
package at its current pin, and dockets only the deltas: a skill the package has
added, removed, or moved to another tier, and any row still `unruled`.

This is a current-state record, not a history. Every row cites the Decision
Record that ruled it, and the reasoning lives there.

## Verdict vocabulary

A sweep rules on whole skills. A verdict covers the skill entire: upstream prose
is never mined for fragments to fold into workspace material, and an idea inside
a rejected skill is rejected with it, reevaluated only when the skill is.

- **verbatim** — installed unmodified through the `skills` CLI and tracked in
  `dotfiles/.agents/.skill-lock.json`, never edited here
  ([skill-management.md](/standards/claude-code/skill-management.md)).
- **adapt** — adopted, carrying the minimal named modification that fits it to a
  workspace constraint the upstream author has no view on.
- **reject** — not adopted, reason recorded.
- **unruled** — present at the pin, awaiting a ruling.
  [0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md) records this value
  as *never considered*.

Through 0016, **adapt** meant something else: the skill left uninstalled and an
idea out of it harvested into authored material. Rows carrying that older sense
now read `reject` and say so in their notes. Material those verdicts already
landed stays where it landed — the relabel retires a vocabulary, not the work.

## Direction of the sweep

The sweep walks from the upstream package into the workspace standards, never
the reverse. Workspace material enters scope only where the upstream package
currently speaks on its subject; a workspace rule the package says nothing about
is outside the sweep, whatever its condition.

## Supersede rule

Verbatim-equivalent workspace content yields to an installed skill: a definition
or procedure an installed skill states when invoked is not also stated in
`CONTEXT.md` or a standard, which would leave two sources of truth for one rule.
Genuine adaptations — workspace machinery built around an adopted technique —
stay authored, and each sweep checks them for creep rather than for removal.
Running that duplication check is part of every sweep.

These are the adaptations it checks. The question at each is whether an
installed skill has grown to cover it, never whether it should exist.

| File | Why it stays authored |
|---|---|
| [testing/conventions.md](/standards/testing/conventions.md) | `tdd` is rejected, and the file is mostly workspace-original pytest material. |
| [build/references/tdd.md](/dotfiles/dot-claude/skills/build/references/tdd.md) | The factory's own TDD procedure, wired to briefs and gates, with deliberate divergences from upstream's — autonomous seam forethought, in-loop refactor passes. |
| [design/references/design-it-twice.md](/dotfiles/dot-claude/skills/design/references/design-it-twice.md) | An adaptation wired into the `/design` node: Opus pinning, worktrees, the synthesis diet. |
| [skill-conventions.md](/standards/claude-code/skill-conventions.md) | The binding format layer, almost entirely workspace-original, and it wins where `/writing-for-agents` collides with it. |

## Tier policy

Nothing from a tier its upstream author has not promoted is installed — what an
author has not committed to, the workspace takes no dependency on
([0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md)). Under the
whole-skill rule above, an unpromoted skill is not mined for ideas either: 0016
allowed that and no longer does.

A tier promotion upstream voids a reject that rests on this policy: the row
reopens as `unruled`, and the next sweep dockets it. Rows whose reject rests on
the tier are marked in their notes. Both rows this reached at `v1.2.3` —
`wizard` and `to-questionnaire` — were reopened and ruled afresh on their
merits.

## mattpocock/skills

Pinned at release `v1.2.3` (`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`) — 35
skills across four tiers, swept in full by
[0020](/docs/decisions/0020-pocock-skills-sweep-2026-08.md): 11 verbatim, 1
adapt, 23 reject. The plugin ships engineering and productivity; in-progress and
misc are a skills-CLI-only channel. The lock file pins each install by
skill-folder hash rather than by this commit, so a re-sweep resolves the package
pin from upstream. Ruling-record numbers are Decision Records in
[docs/decisions/](/docs/decisions/index.md).

| Skill | Tier | Verdict | Reason | Ruling record | Notes |
|---|---|---|---|---|---|
| ask-matt | engineering | reject | A hand-maintained prose router competes with the factory graph | 0016, 0020 | A proposal to harvest its phase-boundaries decision tree was declined at 0020 |
| code-review | engineering | reject | Its two-axis workflow duplicates `code-pr-review` and the factory's review nodes, and is wired to his tracker plumbing | 0016, 0020 | Relabeled from the older adapt. One exception ruled at 0020: its structural-smell baseline landed in `software-factory/refactor-catalogue.md` and `code-pr-review` |
| codebase-design | engineering | **verbatim** | The single home for the workspace's architecture vocabulary, and a dependency of `improve-codebase-architecture` | 0020 | Reverses 0016's adapt; `CONTEXT.md` and `standards/modules.md` now defer to it. Model-invoked |
| diagnosing-bugs | engineering | **verbatim** | Builds the reproduction loop before hypothesizing, then ranks loop techniques and tests falsifiable hypotheses | 0020 | Reverses 0016's reject, which 0016 itself recorded as unexplained. Model-invoked |
| domain-modeling | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked; byte-identical at this pin |
| grill-with-docs | engineering | adapt | A thin front door onto `/grilling` + `/domain-modeling`, mirroring upstream's decomposition | 0016, 0020 | The one modification is invocation mode: upstream's `disable-model-invocation: true` would break the four workspace call sites |
| implement | engineering | reject | The factory graph already does this with more rigor | 0016 | — |
| improve-codebase-architecture | engineering | **verbatim** | The workspace's only architecture-scanning capability — hot-spot scoping, subagent exploration under the deletion test, then grilling the candidate picked | 0020 | Was `unruled` at 0016. User-invoked; its HTML report needs a CDN at view time |
| prototype | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked. Substantive at this pin: the logic branch builds a self-contained HTML demo rather than a terminal TUI |
| research | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked; byte-identical at this pin |
| resolving-merge-conflicts | engineering | reject | Not necessary | 0016, 0020 | The 2026-07-31 reject carried no recorded rationale; 0020 records this one |
| setup-matt-pocock-skills | engineering | reject | Its job is served by workspace standards | 0016 | `standards/tracking/tracker-operations.md` was seeded from its GitHub tracker file and delta-checks against this pin |
| tdd | engineering | reject | Its mandatory user stop breaks the autonomous build node, its loop excludes refactoring, and `build/references/tdd.md` is already the workspace's TDD procedure | 0016, 0020 | Relabeled from the older adapt; 0020 records all three reasons |
| to-spec | engineering | reject | Too complicated to land today, and it may conflict with `wayfinder` and the authored `wayfinder-to-build` | 0020 | **Reevaluate next sweep** |
| to-tickets | engineering | reject | Too complicated to land today, and it may conflict with `wayfinder` and the authored `wayfinder-to-build` | 0020 | **Reevaluate next sweep** |
| triage | engineering | reject | Its label and role vocabulary were hard-rejected at 0016 | 0016, 0020 | Relabeled from the older adapt; the redundancy check and verify-the-claim moves stay where 0016 landed them in `intake/SKILL.md` |
| wayfinder | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked, plus an accommodation package — five `wayfinder:*` labels, a lint check, tracker-operations rules, two judgments — which this pin leaves untouched |
| wizard | engineering | **verbatim** | Generates staged interactive bash wizards for procedures only the user can carry out | 0020 | Its tier reject was voided by promotion out of in-progress. Its `template.sh` exceeds the shell standard's glue-only boundary, resolved by exempting externally-managed trees. Model-invoked |
| claude-handoff | in-progress | reject | The authored `handoff` already mirrors his production `productivity/handoff`, which is the correct end state | 0016 | Rests on the tier policy |
| loop-me | in-progress | reject | Belongs to mission-control, not here | 0016 | — |
| setup-ts-deep-modules | in-progress | reject | TypeScript-only | 0016 | — |
| writing-beats | in-progress | reject | Journey-based structure fights the workspace's current-state reference prose | 0016 | — |
| writing-fragments | in-progress | reject | Idea capture lives in mission-control | 0016 | — |
| writing-shape | in-progress | reject | Not adopted | 0016, 0020 | Relabeled from the older adapt, and rests on the tier policy. The format-argument checklist stays where 0016 landed it in `standards/prose/conventions.md` |
| git-guardrails-claude-code | misc | reject | The PAT already makes the guarded operations impossible | 0016, 0012 | 0012 rules against a second published hook |
| migrate-to-shoehorn | misc | reject | TypeScript-only | 0016 | — |
| scaffold-exercises | misc | reject | Bound to his course business | 0016 | — |
| setup-pre-commit | misc | reject | A competing Node toolchain for a problem `pre-commit` already solves | 0016 | — |
| grill-me | productivity | reject | Redundant with `grill-with-docs` | 0016, 0004 | — |
| grilling | productivity | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked. Substantive at this pin: round-by-round frontier questioning in a mandated question-and-recommendation format replaces one question at a time |
| handoff | productivity | reject | Already harvested near-verbatim at 0006, with no substantive delta at this pin | 0016, 0006 | — |
| teach | productivity | reject | Personal productivity, outside the factory's domain | 0016 | — |
| to-questionnaire | productivity | reject | A solo developer has no third party to send a questionnaire to | 0016, 0020 | Its tier reject was voided by promotion out of in-progress; the row reopened and was re-rejected on its merits |
| wait-what | productivity | **verbatim** | A three-line corrective: re-pitch the last message in Simplified Technical English, using `CONTEXT.md` vocabulary | 0020 | New upstream skill. User-invoked, so it costs no context load; its first-person voice is covered by the prose standard's vendored exemption |
| writing-for-agents | productivity | **verbatim** | The craft layer for any document an agent consumes | 0020 | Renamed from `writing-great-skills`, reversing 0016's adapt. Supersedes the two workspace files seeded from it. Model-invoked; `skill-conventions.md` wins where the two collide |

Seven rows retired at this pin — their skills no longer exist upstream:
`design-an-interface`, `qa`, `request-refactor-plan`, `ubiquitous-language`,
`edit-article`, `obsidian-vault`, `batch-grill-me`. Material their verdicts
landed stays where it landed, and the rulings remain readable at
[0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md).

## marimo-team/skills

A flat package with no tiers. No pin sweep is recorded for this source, so the
rows below cover the two installed skills, not the package's full roster.

| Skill | Tier | Verdict | Reason | Ruling record | Notes |
|---|---|---|---|---|---|
| marimo-batch | — | **verbatim** | Installed verbatim; lock-tracked | unrecorded | — |
| marimo-notebook | — | **verbatim** | Installed verbatim; lock-tracked | unrecorded | — |

## pymc-labs/pymc-modeling

A single-skill package. No pin sweep is recorded for this source.

| Skill | Tier | Verdict | Reason | Ruling record | Notes |
|---|---|---|---|---|---|
| pymc-modeling | — | **verbatim** | Installed verbatim; lock-tracked | unrecorded | — |
