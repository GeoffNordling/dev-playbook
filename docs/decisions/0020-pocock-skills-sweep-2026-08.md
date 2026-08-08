---
type: Decision-Record
title: Matt Pocock Skills Sweep — Verdicts at v1.2.3
description: Verdict changes from the sweep of mattpocock/skills at release v1.2.3 — six new verbatim installs, the whole-skill vocabulary that retires harvesting, the four principles the sweep minted, and the two undelivered 0016 fragments it closes
date: 2026-08-08
---

# Matt Pocock Skills Sweep — Verdicts at v1.2.3

`mattpocock/skills` moved from the pin
[0016](0016-pocock-skills-sweep-2026-07.md) swept
(`2ab958093e83e0ec752e6c1c5932da465bf23e0c`, 41 skills across six tiers) to
release `v1.2.3` (`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, 35 skills across
four). Seven skills were deleted upstream, one was renamed and restructured, two
were promoted out of the in-progress tier, and one is new. The `personal` tier
is gone and `deprecated` holds nothing but its README.

This record holds what **changed**. The standing verdict on every live skill is
[the ledger](/docs/external-skill-verdicts.md), which this sweep rewrote; go
there to ask where a skill stands today, and here to ask why it moved.

This was also the bootstrap run of a repeatable procedure. The sweep dockets
only deltas against the ledger, escalates each to the user as its own item, and
lands everything in one branch; `/pocock-sweep` was written at the end of this
branch from what actually worked.

## Verdict changes

| Skill | At 0016 | Now | Why it moved |
|---|---|---|---|
| codebase-design | adapt | **verbatim** | 0016's adapt existed only because the content had already been copied wholesale into `CONTEXT.md` and the modules standard. Both now defer to the skill, which becomes the single home for the architecture vocabulary. It is also a dependency of `improve-codebase-architecture`. |
| diagnosing-bugs | reject | **verbatim** | 0016 called it the largest true gap, then dropped it in a rescope whose rationale 0016 itself records as absent. Reinstated on its merits: build the reproduction loop before hypothesizing, rank loop techniques, test falsifiable hypotheses, land the regression test at a correct seam. |
| improve-codebase-architecture | never considered | **verbatim** | An agent had proposed a narrow harvest at 0016 and no user ever ruled. Ruled now: it is the workspace's only architecture-scanning capability, and all three of its dependencies are installed. |
| wizard | reject (tier) | **verbatim** | Promotion to engineering voided a reject that rested on the tier policy, reopening the row. Ruled an install: it generates staged interactive bash wizards for procedures only the user can carry out. |
| writing-great-skills → writing-for-agents | adapt | **verbatim** | Renamed and restructured upstream. The adapt had produced two authored files copied from it; both are deleted and the skill supersedes them. |
| wait-what | — | **verbatim** | New upstream skill. |
| to-questionnaire | reject (tier) | reject (merits) | Promotion to productivity voided the tier reject and reopened the row. Re-rejected on its merits: a solo developer has no third party to send a questionnaire to. |
| code-review | adapt | reject | Relabeled — see the vocabulary change below. Its two-axis workflow duplicates `code-pr-review` and the factory's review nodes, and is wired to his tracker plumbing. |
| tdd | adapt | reject | Relabeled, with three reasons recorded for the first time: its mandatory user stop sits inside the autonomous build node, its loop excludes refactoring and routes it to the rejected `code-review`, and `build/references/tdd.md` is already the workspace's TDD procedure. |
| triage | adapt | reject | Relabeled. Its label and role vocabulary were hard-rejected at 0016 and remain so. |
| writing-shape | adapt | reject | Relabeled. Rests on the tier policy. |
| to-spec | adapt | reject | Too complicated to land today, and it may conflict with `wayfinder` and the authored `wayfinder-to-build`. **Reevaluate next sweep.** |
| to-tickets | adapt | reject | Same reason and the same reevaluate marker. |
| resolving-merge-conflicts | reject | reject | Verdict unchanged, reason supplied: not necessary. The 2026-07-31 reject carried none. |

Five standing verbatim installs took a pin bump. `domain-modeling` and
`research` are byte-identical. Three changed substantively: `grilling` replaced
one-question-at-a-time with round-by-round frontier questioning in a mandated
question-and-recommendation format; `prototype`'s logic branch now builds a
self-contained HTML demo rather than a terminal TUI; `wayfinder` gained an
"always invoke" line for its grilling tickets. The `wayfinder` accommodation
package — five labels, a lint check, tracker-operations rules, two judgments —
is untouched by the bump.

**Result across the live 35: 11 verbatim, 1 adapt, 23 reject.** Four new
model-invoked descriptions now load in every session's context:
`codebase-design`, `diagnosing-bugs`, `wizard`, `writing-for-agents`.

## The vocabulary changed: a sweep rules on whole skills

Through 0016, **adapt** meant the skill was left uninstalled and an idea out of
it was harvested into authored workspace material. That practice is retired. A
verdict now covers a skill entire — install it, install it with the minimal
named modification that fits a workspace constraint its author has no view on,
or decline it — and an idea inside a rejected skill is rejected with it,
reevaluated only when the skill is.

The reason is that harvesting produced verdicts nobody could act on. Two of
0016's eleven adapts named a fragment and a landing site that never existed
(see below), and the rest left the workspace holding paraphrases of prose whose
upstream source kept moving underneath them. A whole-skill verdict is checkable
against the lock file; a harvested idea is checkable against nothing.

Four rows carried the older sense and now read `reject`: `code-review`, `tdd`,
`triage`, `writing-shape`. **The relabel retires a vocabulary, not the work** —
material those verdicts already landed stays exactly where it landed, and each
row's note says where.

`grill-with-docs` is the sole surviving `adapt`, and it fits the new sense: the
skill is adopted as upstream decomposes it, carrying one named modification —
invocation mode, because upstream's `disable-model-invocation: true` would break
the four workspace call sites that invoke it.

## Principles this sweep minted

Four rules that outlive this pin. They govern `/pocock-sweep` and any future
sweep of any upstream.

1. **Skills are the unit of decision** — the whole-skill rule above.
2. **Decisions come from the user.** Every delta is its own docket item carrying
   a recommendation; an agent's report is a lead, never a ruling. "Standing"
   labels only a row whose verdict and delivered artifact are both unchanged.
3. **Supersede rule.** Verbatim-equivalent workspace content yields to an
   installed skill: a definition an installed skill states when invoked is not
   also stated in `CONTEXT.md` or a standard. Genuine adaptations — workspace
   machinery built around an adopted technique — stay authored, and each sweep
   checks them for creep rather than for removal.
4. **The description rule splits by invocation mode.** A model-invoked skill
   keeps the binding two-sentence `Use when` form, which is the auto-invocation
   match surface. A user-invoked skill's description is exactly one sentence,
   the label the user reads in the slash-command list, with the trigger list
   dropped. `scripts/skill-lint` branches on `disable-model-invocation`.

Principle 4 overturns a rule the workspace had argued for explicitly. Three
sites stated the no-carve-out version in as many words — `skill-conventions.md`,
a comment in `skill-lint`, and a test named for it. All three were rewritten.
The reversal is upstream's own position: `writing-for-agents` prescribes trigger
branches for a model-invoked description and a one-line summary for a
user-invoked one.

The one workspace rule that did **not** yield to upstream is
`disable-model-invocation` staying always explicit. Upstream's "could the model
reach for it?" test would set the field wrong here, because the factory
dispatcher's slash commands arrive as agent text input and count as model
invocation. That is a workspace fact upstream has no view on, so
`skill-conventions.md` wins.

## Both of 0016's undelivered fragments are closed

0016 recorded two adapt verdicts as *ruled, not landed* — their landing site was
deferred to issue #276, which closed with nothing built. Neither survives as a
dangling verdict:

- **`code-review`'s structural-smell baseline lands**, by the user's explicit
  ruling this sweep, as an exception to the whole-skill rule. Nine smells joined
  `software-factory/refactor-catalogue.md`'s existing candidate list —
  compressed into that document's own cue-and-move shape, not pasted from
  upstream — and `code-pr-review` gained a dimension that flags them. Every hit
  is a judgment call, never blocking, and a documented standard that endorses
  what a smell would flag suppresses it.
- **`request-refactor-plan`'s small-step rule is formally retired.** Its
  upstream source no longer exists, so there is nothing left to adapt. The
  catalogue's own step-size section already carries the rule.

## Positions declined

Recorded so no future sweep re-finds them and re-litigates.

- **Omitting `disable-model-invocation` when false** — declined; the field stays
  always explicit, for the dispatcher reason above.
- **One-line descriptions for every skill** — declined in favor of the split
  rule, because a model-invoked description is a match surface and a
  user-invoked one is not.
- **Harvesting `ask-matt`'s phase-boundaries decision tree** — declined. A
  hand-maintained prose router competes with the factory graph.
- **A workspace rule translating upstream's `docs/adr/` to `docs/decisions/`** —
  declined. Three installed skills tell an agent to check ADRs; an agent that
  finds no `docs/adr/` will reach `docs/decisions/` without being told.
- **A shell-standard carve-out for wizard-generated scripts, and a fence in the
  TDD reference against `diagnosing-bugs`** — both declined. Those two skills
  are installed as curiosities, and workspace procedures are not complicated to
  accommodate a case that may never arise.

## Corrections to the record

Two claims this sweep's own plan made turned out to be wrong, and are corrected
here rather than left in a deleted planning file:

- **The deleted `skill-writing.md` had no surviving workspace original.** The
  plan named one — "a failing test is fixed, never edited to pass" — as needing
  to be folded forward. It is not original: it restates `build/references/tdd.md`,
  which states it in the skill that actually runs tests. The generalized copy in
  a format standard had no bite, and was retired deliberately rather than lost.
- **`design-it-twice.md` carried no internal-seams passage.** The plan expected
  a supersede-rule trim there; the passage did not exist, so that half of the
  row was a no-op.

## One cut sits outside the sweep's direction

A sweep walks from the upstream package into the workspace, and workspace
material enters scope only where the package currently speaks on its subject.
One change breaks that rule knowingly: `refactor-catalogue.md`'s `## The two
scopes` section was deleted, and upstream speaks on the smell baseline, not on
refactor scopes.

It was cut because its only caller, `build/references/tdd.md`, already stated
both scopes, their reach, and the test cadence, and its closing paragraph
pointed at an escalation trigger stated in that same file. The one fact it
carried alone — which candidates suit which reach — moved into `tdd.md`'s two
refactor passes. The user ruled it rides this branch. It is recorded here so a
later sweep finds a reason rather than an unexplained deletion.
