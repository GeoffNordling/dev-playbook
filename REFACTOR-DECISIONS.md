---
type: General-Sheet
title: Refactor Decisions
description: TEMPORARY — the judgment calls of the workstream refactor of 2026-09-24, one per entry, for the user to review and reverse; delete this file after the review
---

# Refactor Decisions

TEMPORARY. Each entry is a call I made where you might have gone the
other way. Each says what I did and the other way. Delete this file
after the review.

## Decisions

### 1. I applied the term sort without showing it to you first

In the interview you asked to see the sort before any term was edited.
You then told me to proceed and to put doubtful calls here, so I
applied it. Here it is, for review. Every move is a text edit.

| Term | Home now | Why |
|---|---|---|
| predicate, condition, population, specification, target state, objective, reference model | `CONTEXT.md`, Specification | used by standards, doc-types, guides |
| zero findings | `CONTEXT.md`, Governance | used by the Loop contract shape and ralph-checkpoint |
| DocType, part, why, encoding, primitive, residual | `CONTEXT.md`, Doc-types | used by `doc-types/` and standards |
| fact base, extractor, node, edge, view | `CONTEXT.md`, Fact base | used by `doc-types/` pages |
| workstream, loop, yield, stint, driver, principal, iteration, segment, checkpoint | `CONTEXT.md`, Workstreams and loops | used by `doc-types/` and Running a Stint |
| rule, verifier, finding, gate | `CONTEXT.md` already | the old workstream copies deleted |
| deterministic rule, stochastic rule, kind, state | dropped | the Rule, Check, and Judge entries cover the first three; "state" is a plain word |
| distribution, sample | root head file | used only in the root's logic-and-statistics principle |
| receipt, derivation, vocabulary, schema, checkout, envelope | See head file | each used by two or more See children |
| ABox, TBox | fact base head file | used only there |
| CLOA object, view file, subject, kind, registry, panel, state directory, identity, stamp, arrangement, refresh record | viewer head file, as before | viewer only |
| Sandcastle pipeline | dropped | replaced by "the `stint` command" |

The other way: keep more of these in head files, so that `CONTEXT.md`
stays small. It grew by 27 entries.

### 2. I added "segment" to CONTEXT.md

Running a Stint called segment one of the workflow's terms, but no file
defined it. The other way: remove the word from the guide.

### 3. Where the doc-type system's principles went

- "Peers first" is now one sentence in the opening of
  `doc-types/reference-model.md`.
- "Stochasticity is a continuous scale" and "Shape is orthogonal to
  stochasticity" moved to See's Principles.
- The "three working policies" for rules moved to the root's
  Principles, because no workstream writes Standards now. The other
  way: put them in `standards/doc-type/standard-conventions.md`, or
  drop them.
- I dropped "Verbs", "Both forms", and the four predicate principles,
  because the standards and Writing Predicates already hold them.

### 4. What I dropped from Loop and Workstream

- I dropped every Settled item (the drive edge, the menu, the three
  step kinds, the principal as a receiver, the reference model first).
  Each one is already in the reference model or a standard.
- I dropped "Simple and composable", the rule that a Loop definition
  carries no policy.
- I moved "Predicates, not fixes" and "A Loop document for every loop"
  to Drive's Principles.
- I dropped both Completed logs; git history holds them.

### 5. What Specifying a Loop left

- I scrubbed the three written forms, the loop that proposes, the
  split between soft guidance and findings, and the residue into
  Drive's "Think the system through" item.
- I dropped its "The predicate" section, because Writing Predicates
  holds it.
- `doc-types/doc-type.md` cited that page as the build loop's design.
  It now says only that the fact base plans to run the build loop as a
  Loop.

### 6. I deleted System Brief

`see/story-forge/system-brief.md` was stale. It named four doc-types,
mypy, and Personal Notes, and each of its claims restated another file.
The other way: rewrite it as a current brief.

### 7. I kept a Planned item for the stint patches in Drive

You said the `stint` command gets no more development. The item is
housekeeping, not development: after the merge to `main`, delete
`src/dev_playbook/stint/patches/`, or no stint launches. The other way:
drop the item.

### 8. Drive's Done when may already be met

I wrote "The first unattended stint on a real workstream yields to the
user and gets a verdict." The `stint` command already ran live to done
on a test repo (wordcount), and I did not count that run. The other
way: count it and close the Done when.

### 9. I redacted an employer name in the story-forge survey

`story-forge-survey.md` named an employer, which breaks that
workstream's privacy principle. It now reads "one employer's interview
loop". The name is still in the git history of a public repo. The
other way: leave it as it was.

### 10. I kept "The language" in the reference model

`doc-types/reference-model.md` still has the heading `### The language`
and the sentence "The doc-types are the language". The heading names
the pseudocode section, not the component, and both the pseudocode
sync test and the `#the-language` anchors depend on it. The other way:
rename it, and update the test and the anchors.

### 11. The pseudocode sync test is no longer temporary

The test was temporary until the reference model left the workstream.
The model now lives beside the pages it copies, so I removed the
TEMPORARY label and kept the test.

### 12. I made small cuts to the fact base worklist

- "Docs follow the moves" is now one sentence in the Extractors item.
- I dropped "the shims go", because no generator shims exist.
- I dropped the "step 2" and "step 3" references.
- I added a Planned item: "The ontology and its solver".

### 13. Things I found and left as they are

- The See term "vocabulary" collides with the type name
  `type: Vocabulary` of `CONTEXT.md`.
- `uv run mypy src tests` finds 3 errors in the `stint` package
  (`src/dev_playbook/stint/call.py:167`, and
  `tests/dev_playbook/stint/test_stint_call.py:61` and `:182`). They
  are in HEAD and are not from this refactor.
- The acronym VEC in the story-forge survey names the user's state
  employment agency.
