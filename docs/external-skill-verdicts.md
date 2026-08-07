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

- **verbatim** — installed unmodified through the `skills` CLI and tracked in
  `dotfiles/.agents/.skill-lock.json`, never edited here
  ([skill-management.md](/standards/claude-code/skill-management.md)).
- **adapt** — the idea harvested into authored workspace material; the upstream
  skill itself is not installed.
- **reject** — not adopted, reason recorded.
- **unruled** — present at the pin, awaiting a ruling.
  [0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md) records this value
  as *never considered*.

## Direction of the sweep

The sweep walks from the upstream package into the workspace standards, never
the reverse. Workspace material enters scope only where the upstream package
currently speaks on its subject; a workspace rule the package says nothing about
is outside the sweep, whatever its condition.

## Tier policy

Nothing from a tier its upstream author has not promoted is installed — what an
author has not committed to, the workspace takes no dependency on
([0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md)). Harvesting an
*idea* out of such a skill is a different act and stays allowed, which is why
`writing-shape` was harvested from the same tier that supplies several of the
rejects below.

A tier promotion upstream voids a reject that rests on this policy: the row
reopens as `unruled`, and the next sweep dockets it. Rows whose reject rests on
the tier are marked in their notes.

## mattpocock/skills

Pinned at `2ab958093e83e0ec752e6c1c5932da465bf23e0c` — 41 skills across six
tiers, ruled in full by
[0016](/docs/decisions/0016-pocock-skills-sweep-2026-07.md): 5 verbatim, 11
adapt, 24 reject, 1 unruled. The lock file pins each install by skill-folder
hash rather than by this commit, so a re-sweep resolves the package pin from
upstream. Ruling-record numbers are Decision Records in
[docs/decisions/](/docs/decisions/index.md).

| Skill | Tier | Verdict | Reason | Ruling record | Notes |
|---|---|---|---|---|---|
| design-an-interface | deprecated | reject | Superseded upstream by `codebase-design` | 0016, 0004 | — |
| qa | deprecated | adapt | "Steps to reproduce" heading → `standards/tracking/issue-authoring.md` | 0016 | — |
| request-refactor-plan | deprecated | adapt | Fowler's small-step rule ruled to be incorporated | 0016 | Ruled, not landed — the landing site went to #276, which closed unbuilt |
| ubiquitous-language | deprecated | reject | Already absorbed at 0004; the workspace's version is deliberately divergent | 0016, 0004 | — |
| ask-matt | engineering | reject | A hand-maintained prose router competes with the factory graph | 0016 | — |
| code-review | engineering | adapt | Fowler's 12-smell baseline ruled to land in the review skills | 0016 | Ruled, not landed — deferred to #276, which closed unbuilt |
| codebase-design | engineering | adapt | Two uncovered fragments — the port test-double category and "replace, don't layer" — → `standards/testing/conventions.md` | 0016 | The skill itself unadopted |
| diagnosing-bugs | engineering | reject | Catalogued as the largest true gap, then dropped in the 2026-07-31 rescope | 0016 | — |
| domain-modeling | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked |
| grill-with-docs | engineering | adapt | The authored version is a thin front door onto `/grilling` + `/domain-modeling`, mirroring upstream's decomposition | 0016 | Upstream not installed — its `disable-model-invocation: true` would break the four workspace call sites |
| implement | engineering | reject | The factory graph already does this with more rigor | 0016 | — |
| improve-codebase-architecture | engineering | **unruled** | An agent proposed a narrow harvest; no user ruling exists | 0016 | — |
| prototype | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked; the authored fork deleted |
| research | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked |
| resolving-merge-conflicts | engineering | reject | Catalogued adapt, then dropped in the 2026-07-31 rescope | 0016 | — |
| setup-matt-pocock-skills | engineering | reject | Its job is served by workspace standards | 0016 | — |
| tdd | engineering | adapt | Tautological-test warning → `standards/testing/conventions.md`; seam forethought → `build/references/tdd.md` | 0016 | — |
| to-spec | engineering | adapt | Prototype-snippet exception → `issue-authoring.md` | 0016 | Its sketch-the-seams fragment went to #273, which closed unimplemented |
| to-tickets | engineering | adapt | Expand–contract migration rule → `issue-authoring.md § Vertical-slice rules` | 0016 | — |
| triage | engineering | adapt | Redundancy check and verify-the-claim → `intake/SKILL.md` | 0016 | The label and role vocabulary hard-rejected |
| wayfinder | engineering | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked, plus an accommodation package — five `wayfinder:*` labels, a lint exemption, tracker-operations rules |
| batch-grill-me | in-progress | reject | An unpromoted upstream experiment | 0016 | Rests on the tier policy |
| claude-handoff | in-progress | reject | The authored `handoff` already mirrors his production `productivity/handoff`, which is the correct end state | 0016 | Rests on the tier policy |
| loop-me | in-progress | reject | Belongs to mission-control, not here | 0016 | — |
| setup-ts-deep-modules | in-progress | reject | TypeScript-only | 0016 | — |
| to-questionnaire | in-progress | reject | Declined, and its ruling generalized into the tier policy | 0016 | Rests on the tier policy |
| wizard | in-progress | reject | Speculative and Node-flavored | 0016 | Rests on the tier policy |
| writing-beats | in-progress | reject | Journey-based structure fights the workspace's current-state reference prose | 0016 | — |
| writing-fragments | in-progress | reject | Idea capture lives in mission-control | 0016 | — |
| writing-shape | in-progress | adapt | Format-argument checklist → `standards/prose/conventions.md` | 0016 | — |
| git-guardrails-claude-code | misc | reject | The PAT already makes the guarded operations impossible | 0016, 0012 | 0012 rules against a second published hook |
| migrate-to-shoehorn | misc | reject | TypeScript-only | 0016 | — |
| scaffold-exercises | misc | reject | Bound to his course business | 0016 | — |
| setup-pre-commit | misc | reject | A competing Node toolchain for a problem `pre-commit` already solves | 0016 | — |
| edit-article | personal | reject | Thinner than the authored `doc-rewrite` / `doc-format` | 0016 | — |
| obsidian-vault | personal | reject | Hardcoded to his machine | 0016 | — |
| grill-me | productivity | reject | Redundant with `grill-with-docs` | 0016, 0004 | — |
| grilling | productivity | **verbatim** | Installed unmodified from the pin | 0016 | Lock-tracked |
| handoff | productivity | reject | Already harvested near-verbatim at 0006, with no substantive delta at this pin | 0016, 0006 | — |
| teach | productivity | reject | Personal productivity, outside the factory's domain | 0016 | — |
| writing-great-skills | productivity | adapt | Became `standards/claude-code/skill-writing.md`, copied and modified with a provenance note | 0016 | — |

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
