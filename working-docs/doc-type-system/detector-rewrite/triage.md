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
- [Python](/working-docs/doc-type-system/detector-rewrite/triage/python.md)

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

## Acronyms

None.
