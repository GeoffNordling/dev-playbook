---
type: Decision-Record
title: Delete the Judgments Subsystem
description: Delete every part of the LLM-judge judgment machinery — declarations, library, seen-set, workflow, sweep skill, standard, and cache gate — because a stochastic verifier can hold no gate, an ungated one needs the user to run it and the user stopped, and the doc-type program replaced its largest population with a deterministic check; spec-tools leaves the GOVERNED roster in the same change
date: 2026-09-07
status: accepted
---

# Delete the Judgments Subsystem

A **judgment** was a yes/no claim about named files, ruled on by an LLM
judge, declared as YAML and keyed by content, with a machine-local
seen-set holding what had passed. The whole subsystem is deleted: the
declarations, `dev_playbook.judgments`, `dev_playbook.skipcache`, the
`judgments-run` and `judgments-lint` scripts, the `judgments` workflow,
the `judgments-sweep` skill, the Semantic Validation card and its
bundle, the `SKIP_JUDGMENTS` / `NO_JUDGMENT_CACHE` cache gate, and every
test and prose mention. It is deleted because it had already stopped
working, in five recorded steps that nobody wrote down as one decision.

## Context

The verifier is stochastic, so it could never hold a gate. Off the gate
it needed the user to run it by hand, and the user stopped. Then the
doc-type program built a deterministic replacement for its largest
family. The repository's own history says so:

1. **Built, gated** (#98–#186, June–July). "Build-standard honesty
   judged, not assumed": 25 declarations, 14 of them per-card honesty
   checks, armed at a pytest gate.
2. **The gate could not hold** (#200, 2026-07-14). The armed gate blocked
   subagents: a cache miss's only remedy is the sweep, a subagent has no
   Workflow tool, so `make check` was a dead end. The fix was the
   two-tier `SKIP_JUDGMENTS` split, which made the gate skip by default.
3. **The verdicts were not trusted** (#230, 2026-07-22). The sweep skill
   was rewritten around judge fallibility — "low-intelligence, stochastic
   processes we run constantly; they will produce false positives" — with
   a fix-attempt cap and an escalation path to the user.
4. **The burden was measured** (#395, 2026-08-06). The simplification
   audit's prime evidence: the judgments gate "touched all 21 recent
   substantive merges with recorded false positives and hand-recorded
   'green' verdicts."
5. **The gate came off, and nothing replaced it** (#398/#399 and #406,
   2026-08-11). Judgments left routine enforcement — "Slow. Stochastic
   and brittle" — for a "periodic sweep". #406 then found periodic had no
   scheduler, no cron, no routine behind it: it meant whenever the user
   ran the skill. The last sweep recorded anything on 2026-08-14. It
   never ran again.

By 2026-09-05, PR #475 cut 27 of the 31 declarations. Fourteen were the
per-card honesty checks, which the card generator's `--check` now
verifies deterministically — a judge replaced by a lint, which is the
doctrine working. What remained was four declarations, none cached, three
of them judging the judgments subsystem's own documentation: roughly
1,100 lines of Python, 272 of JavaScript, 1,900 of tests, and 5,100 words
of prose serving one hand-run procedure with no user.

## Decision

Delete all of it. A verifier that cannot sit at a gate, and that no
schedule and no person runs, checks nothing; keeping the machinery only
costs every reader who meets it.

**spec-tools leaves the `GOVERNED` roster.** spec-tools was the one repo
that gated its judgments, 17 of them, and so the one standing argument
for keeping the machinery. It is orphaned and out of favor: no live
project uses it, and it is not a priority.
[0027](/docs/decisions/0027-registry-refactor-rulings.md) already ruled
that it may break. Removing it from the roster records that it is no
longer governed, so the audit says nothing about it.

## Consequences

- **`make check` is the push gate.** `check-judgments-cache` is gone from
  the Makefile, both canonical fragments, and both pre-commit configs;
  the pre-push hook's entry is `make check`.
- **Every detector is now a lint.** [CONTEXT.md](/CONTEXT.md#governance)
  defined a Detector as a lint if deterministic code and an "audit in the
  narrow sense" if an LLM judge. Judgments were that branch's only
  instance, so the branch is dropped and the Audit cell contract
  ([Card Catalog](/standards/standard/cards.md#audit-cites-a-lint)) cites
  a lint or a third-party detector, never a judgment link.
- **The `tests/agent_review/` mirror-layout exception is gone**, reversing
  that clause of
  [0021](/docs/decisions/0021-scope-directories-and-spec-item-return.md).
  The `unit` and `integration` scope directories stand; the directory the
  exception named never existed in this repo.
- **The Deslop regression gate candidate loses its named mechanism.** It
  stays in [Candidates](/CANDIDATES.md) with no mechanism proposed.
- **`prose.judgment-spelling` is untouched.** It governs the American
  spelling of an ordinary English word, not this subsystem.
- **Restoration is one revert.** Every deleted file is intact at
  `8d689d6`, the commit this change branched from.
