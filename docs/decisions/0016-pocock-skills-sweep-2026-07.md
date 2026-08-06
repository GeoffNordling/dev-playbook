---
type: Decision-Record
title: Matt Pocock Skills Sweep — Verdicts at the 2026-07 Pin
description: Per-skill verdicts from the sweep of mattpocock/skills at pin 2ab9580 — five installed verbatim, eleven harvested, twenty-four rejected — with the reversals the sweep produced
date: 2026-08-01
---

# Matt Pocock Skills Sweep — Verdicts at the 2026-07 Pin

Between 2026-07-28 and 2026-08-01 the workspace swept the whole of `mattpocock/skills`, pinned at `2ab958093e83e0ec752e6c1c5932da465bf23e0c` — 41 skills across six tiers. This record holds the verdict for each, so the same source is not re-evaluated from scratch. It was written on 2026-08-01 at the close of tracking epic [#293](https://github.com/GeoffNordling/dev-playbook/issues/293), from the rulings in [#256](https://github.com/GeoffNordling/dev-playbook/issues/256), [#262](https://github.com/GeoffNordling/dev-playbook/issues/262), [#267](https://github.com/GeoffNordling/dev-playbook/issues/267), and the chunk issues and merged PRs beneath them.

Three verdicts, plus one bookkeeping value:

- **verbatim** — installed from upstream and pin-owned, never edited by us.
- **adapt** — the technique harvested into our own authored material; the upstream skill itself not installed.
- **reject** — considered and declined.
- **never considered** — present at the pin, but no user ruling exists. Recorded as-is rather than backfilled.

Prior Pocock decisions this record does not restate: [0001](0001-adopt-matt-pocock-conventions.md) (adopt his conventions), [0004](0004-remove-pocock-direct-dependency.md) (cut the direct dependency, absorb the conventions), [0006](0006-harvest-pocock-prototype-and-handoff.md) (harvest `prototype` and `handoff`).

## Verdicts

| Skill | Tier | Verdict | Disposition |
|---|---|---|---|
| design-an-interface | deprecated | reject | Superseded upstream by `codebase-design`; 0004 ruled no annotation needed |
| qa | deprecated | adapt | "Steps to reproduce" heading → `standards/tracking/issue-authoring.md` |
| request-refactor-plan | deprecated | adapt — **ruled, not landed** | Fowler's small-step rule ruled "incorporate"; landing site deferred to #276, which closed unbuilt |
| ubiquitous-language | deprecated | reject | Already absorbed at 0004; ours is deliberately divergent |
| ask-matt | engineering | reject | A hand-maintained prose router competes with the factory graph |
| code-review | engineering | adapt — **ruled, not landed** | Fowler's 12-smell baseline ruled to land in the review skills; deferred to #276, which closed unbuilt |
| codebase-design | engineering | adapt | Skill unadopted, but two uncovered fragments — the port test-double category and "replace, don't layer" — → `standards/testing/conventions.md` |
| diagnosing-bugs | engineering | reject | Catalogued as the largest true gap, then dropped in the 2026-07-31 rescope |
| domain-modeling | engineering | **verbatim** | Installed, lock-tracked |
| grill-with-docs | engineering | adapt | Ours rewritten as a thin front door onto `/grilling` + `/domain-modeling`, mirroring upstream's decomposition; upstream not installed — its `disable-model-invocation: true` would break our four call sites |
| implement | engineering | reject | The factory graph already does this with more rigor |
| improve-codebase-architecture | engineering | **never considered** | An agent proposed a narrow harvest; no user ever ruled |
| prototype | engineering | **verbatim** | Installed, lock-tracked; the authored fork deleted |
| research | engineering | **verbatim** | Installed, lock-tracked |
| resolving-merge-conflicts | engineering | reject | Catalogued adapt, then dropped in the 2026-07-31 rescope |
| setup-matt-pocock-skills | engineering | reject | Its job is served by workspace standards |
| tdd | engineering | adapt | Tautological-test warning → `standards/testing/conventions.md`; seam forethought → `build/references/tdd.md` |
| to-spec | engineering | adapt | Prototype-snippet exception → `issue-authoring.md`. Its sketch-the-seams fragment went to #273, which closed unimplemented |
| to-tickets | engineering | adapt | Expand–contract migration rule → `issue-authoring.md § Vertical-slice rules` |
| triage | engineering | adapt | Redundancy check and verify-the-claim → `intake/SKILL.md`; the label and role vocabulary hard-rejected |
| wayfinder | engineering | **verbatim** | Installed, lock-tracked, plus an accommodation package — five `wayfinder:*` labels, a lint exemption, tracker-operations rules |
| batch-grill-me | in-progress | reject | An unpromoted upstream experiment |
| claude-handoff | in-progress | reject | **Reversed** — see below |
| loop-me | in-progress | reject | Belongs to mission-control, not here |
| setup-ts-deep-modules | in-progress | reject | TypeScript-only |
| to-questionnaire | in-progress | reject | Declined, and generalized into the in-progress-tier policy below |
| wizard | in-progress | reject | Speculative, Node-flavored, in-progress tier |
| writing-beats | in-progress | reject | Journey-based structure fights our current-state reference prose |
| writing-fragments | in-progress | reject | Idea capture lives in mission-control |
| writing-shape | in-progress | adapt | Format-argument checklist → `standards/prose/conventions.md` |
| git-guardrails-claude-code | misc | reject | The PAT already makes the guarded operations impossible; 0012 rules against a second published hook |
| migrate-to-shoehorn | misc | reject | TypeScript-only |
| scaffold-exercises | misc | reject | Bound to his course business |
| setup-pre-commit | misc | reject | A competing Node toolchain for a problem `pre-commit` already solves |
| edit-article | personal | reject | Thinner than our `doc-rewrite` / `doc-format` |
| obsidian-vault | personal | reject | Hardcoded to his machine |
| grill-me | productivity | reject | Redundant with `grill-with-docs`; dropped at 0004 |
| grilling | productivity | **verbatim** | Installed, lock-tracked |
| handoff | productivity | reject | Already harvested near-verbatim at 0006; this sweep found no substantive delta, so no edit was made |
| teach | productivity | reject | Personal productivity, outside the factory's domain |
| writing-great-skills | productivity | adapt | Became `standards/claude-code/skill-writing.md`, copied and modified with a provenance note |

**Tally:** 5 verbatim · 11 adapt · 24 reject · 1 never considered.

## The in-progress-tier policy

Nothing from an upstream author's experimental or in-progress tier is installed. What its own author has not committed to, we do not take a dependency on.

Harvesting an *idea* from such a skill is a different act and remains allowed — which is why `writing-shape` (in-progress) was harvested into the prose standard in the same pass that rejected `claude-handoff` (in-progress) as an install.

## Reversals this sweep produced

**The mid-sweep catalog was overturned.** #262's matrix (2026-07-28) tallied 0 adopt · 16 adapt · 25 reject and called zero-adopt "the honest read." All five eventual verbatim installs were catalogued weaker that day — `domain-modeling` as reject, the rest as adapt — and were upgraded later in the same sweep. That catalog is a snapshot mid-sweep, not a verdict.

**`claude-handoff`.** Ruled a harvest on 2026-07-28 (take its `--bg` background-launch mode into our `handoff`), reversed 2026-08-01 on in-progress-tier grounds. Our `handoff` already mirrors his production `productivity/handoff`, which is the correct end state; no edit was made.

**Pre-agreed seams.** The `tdd` harvest was first ruled as a rule requiring seams to be agreed with the user in advance, landing in the testing standard. Reversed 2026-08-01: no such rule exists in the testing standard, and `build/references/tdd.md` instead carries autonomous seam forethought, respecting seams where a brief happens to name them.

**`diagnosing-bugs` and `resolving-merge-conflicts`** were both catalogued as adapt — the first called the largest true gap — and both dropped whole in the 2026-07-31 rescope. No rationale beyond the owner's ruling is recorded.

**`qa`.** A delta-check reported no back-port warranted; the owner reversed it the same day, and the reproduction-steps heading landed.

## Ruled but not landed

Two adapt verdicts have no artifact. Both Fowler fragments — `code-review`'s 12-smell baseline and `request-refactor-plan`'s small-step rule — were ruled to be incorporated, but their landing site was deferred to the factory-node dedup review, issue #276, which has since closed with nothing built. Neither fragment exists in the repo today. They are recorded here as decided, not delivered, so that a future pass can tell the difference between a verdict nobody executed and a verdict nobody made.
