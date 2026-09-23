---
type: General-Sheet
title: Triage
description: The method of the detector rewrite's triage — the verdicts, how a row is escalated, the user's rulings that calibrate every family, and the one report per family
---

# Triage

The 150 deterministic rules, family by family, each kept, rewritten,
or deleted. The reports are the specification the package is written
to ([Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md)).
A rule is cited by its id and the line of its heading.

## Method

- **Verdicts.** Keep: the sentence is plain and the check, where one
  exists, decides it. Rewrite: the sentence is restated plain, split,
  or merged; a null rule gains its check. Delete: the rule binds
  nothing a governed repo would fail, restates another, or is about
  dev-playbook's own checker. Stochastic: the sentence is worth
  keeping and no function can decide it; the user rules on each.
- **Escalation.** A row the triager cannot settle goes to the user
  with the heading line, what the rule means in plain words, the
  proposal, and how the proposal differs from today's sentence and
  from today's enforcement. The user's rulings calibrate the rows
  that follow.
- **Plain rules.** A rewrite names the file, the value, and the
  comparison, per
  [Principles](/working-docs/doc-type-system/detector-rewrite/ROOT.md#principles).
  The heading never changes; the meaning holds unless the rule is
  split or merged.

## The reports

One per family under `triage/`. `build` and `python` by hand, the
calibration sample; the other ten by one Opus agent each, launched
with
[Triage Family Prompt](/working-docs/doc-type-system/detector-rewrite/prompts/triage-family.md).

- [Build](/working-docs/doc-type-system/detector-rewrite/triage/build.md)
- [Decisions](/working-docs/doc-type-system/detector-rewrite/triage/decisions.md)
- [Distribution](/working-docs/doc-type-system/detector-rewrite/triage/distribution.md)
- [Doc-Type](/working-docs/doc-type-system/detector-rewrite/triage/doc-type.md)
- [Harness](/working-docs/doc-type-system/detector-rewrite/triage/harness.md)
- [Knowledge Organization](/working-docs/doc-type-system/detector-rewrite/triage/knowledge-organization.md)
- [Prose](/working-docs/doc-type-system/detector-rewrite/triage/prose.md)
- [Python](/working-docs/doc-type-system/detector-rewrite/triage/python.md)
- [Shell](/working-docs/doc-type-system/detector-rewrite/triage/shell.md)
- [Standard](/working-docs/doc-type-system/detector-rewrite/triage/standard.md)
- [Testing](/working-docs/doc-type-system/detector-rewrite/triage/testing.md)
- [Tracking](/working-docs/doc-type-system/detector-rewrite/triage/tracking.md)

The ten agents landed 2026-09-22: 37 rules kept, 71 restated, 11
deleted, 27 escalated, plus four proposed new rules. The 27 were
ruled 2026-09-23 by the four general rulings below, each report's
Escalations section carrying its verdicts: 13 items built as
proposed or narrowed, 12 rules deleted, 1 made stochastic, 2 fixed
in the repo now and built. The one check that fails the repo as it
stands, scripts under ruff, is a Planned item in the ROOT. Three new
rules accepted, one rejected.

## Rulings that calibrate the rest

- **A rule about the checker itself is a test, not a rule.** Ruled on
  `build.every-canonical-file-has-a-rule-and-every-rule-a-file`.
  Applies to every rule whose member is dev-playbook's own checking
  code rather than a governed repo.
- **A rule the user cannot read is restated plain, heading fixed,
  meaning held.** Three of the first three escalations were
  unreadable. Two were deleted for reasons of their own, one restated
  as two. Unclear wording alone never deletes a rule.
- **A tool's own configuration is the rule.** Where ruff, shellcheck,
  or shfmt decides a rule, the rule says the tool reports nothing
  under the canonical configuration and names what that
  configuration selects. A sentence that promises more than the tool
  enforces is replaced, not kept beside it.
- **Fix the cause in this repo.** A gap that exists because a file
  never reaches the tool is closed in the canonical files, not by
  narrowing the rule. Consumer repos are not a reason to narrow.
- **The repo as it stands is acceptable.** Ruled 2026-09-23 on the
  agents' escalations. The rewrite refactors rules and checks; it
  adds no check that fails today. A new check that passes today is
  implemented. A new check that fails today is deleted, or set aside
  on a list of checks to add later; it does not enter the suite, and
  its rule leaves the Standard, to live only on that list. This
  moves the python ruling that sent scripts to ruff to the ROOT's
  Planned list: that fix reformats three scripts today. A small fix
  to the repo is allowed where the user approves it by name.
- **No rule micromanages how code is written.** Ruled 2026-09-23 on
  `shell.glue-only`. A rule that does not shape high-level guidance
  or comprehension goes, however sound. Also deleted on that ground:
  `testing.fixture-lives-in-the-narrowest-conftest`, the sentence
  limit on a candidates entry, and the two GitHub epic and ticket
  rules.
- **New rules.** Ruled 2026-09-23: the global source's first `###`
  heading is `Read the standards`, yes; `README.md` is typed
  `README`, yes; only `CONTEXT.md` is typed `Vocabulary`, no, the
  user wants other Vocabulary files open.
- **A deterministic body narrows to what the code decides.** Where
  the sentence promises more than the check reads, the sentence
  narrows. Where no function can decide the sentence at all, the
  rule becomes stochastic. In doubt, delete or downgrade; the user
  trusts the triager's judgment and rules on no more single rows.
- **The detector-script rules go.** Dev-playbook has no detector
  script on exit, and consumers are not a reason to keep a rule.
- **Loop stays as it is.** The six Loop rules and their checks are
  kept; the Loop workstream follows this one.

## Acronyms

None.
