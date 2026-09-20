---
type: General-Sheet
title: Body Drain
description: The prompt one agent loads to drain one ruleset — the target shape of a rule, the id and kind it proposes, the five-verdict rubric for the body, the detector check, the exactness a deterministic predicate keeps, and the rows it returns
---

# Body Drain

The prompt for step 1 of the doc-type system's refactor: one agent
owns one ruleset, reads it, its sibling rulesets, and the detector that
checks it, and returns one row per rule. It edits nothing.

## Your input

The launch prompt names one file, `standards/<name>/<topic>.md`. Read
it whole. Read the other `.md` files in the same `standards/<name>/`
directory, so you can see a rule a sibling already decides. Read
`working-docs/doc-type-system/doc-type-system/writing-predicates.md`
once for the litmus a predicate passes. Read the detector code the
check below leads you to. Read nothing else: no root, no index, no
Standard outside your directory, and no other file in `working-docs/`.
Everything you need is in this file.

## The target shape

After this pass a rule is a heading, a predicate, and a trailer,
nothing else. The predicate is everything between the heading and the
trailer, a list of exemptions included when the check needs one. It is
written so deterministic code can lift it verbatim into a judge's
prompt, alone or concatenated with other rules, so it names its member
and reads as a complete claim with no pronoun that points outside it.
The trailer is one line:

```
`<name>.<slug>` · deterministic
```

`<name>` is the directory under `standards/`; `<slug>` is the heading's
GitHub slug, lowercased, punctuation dropped, spaces to hyphens. A
condition, an H2 that holds H3s, is a rule too and carries the same
trailer. Prose between the H1 and the first H2 is the population's
elaboration and is out of scope; do not report on it.

## The kind

Propose one per rule. Ask how the verifier would work. A script can
decide it: deterministic, whether or not the script exists today. Only
a judge with a prompt can decide it: stochastic. Neither: the predicate
fails the litmus, and your verdict says so.

## The detector check

Before judging any body, find the detector that emits this ruleset's
ids. Run each detector's `--list-rules` and keep the ids whose prefix
is `<name>`:

```
scripts/repo-lint --list-rules; scripts/python-lint --list-rules; scripts/testing-lint --list-rules; scripts/ref-lint --list-rules; scripts/okf-lint --list-rules; scripts/decisions-lint --list-rules; scripts/harness-files-lint --list-rules; scripts/prose-lint --list-rules; scripts/standards-lint --list-rules; scripts/loop-lint --list-rules; scripts/workspace-lint --list-rules
```

For each id that belongs to a rule in your file, read the code that
emits it, under `src/dev_playbook/` or in `scripts/`, and hold the
predicate to what the code decides, in both directions:

- Every exemption, threshold, or special case the code honors that the
  predicate does not state is folded into the predicate, never deleted.
- Every clause the predicate states that the code does not decide is
  cut from it. A rule is checked whole or not at all; no rule is half
  checked. A cut clause that is itself a constraint on the member
  becomes a rule of its own, with the kind the litmus gives it and no
  verifier yet. A cut clause that is not a constraint goes.

You never change a script, and you never propose stochastic for a
clause a script could decide.

## The rubric

Split the body into sentences and give each one a home. The verdict
for the rule is what the body as a whole needs.

- **delete** — the body holds only enforcement wiring (which script,
  which gate), pointers to other Standards, or a reason. All of it goes.
- **fold** — the body holds an exemption, a definition, or a special
  case that changes what passes, or the predicate says more than the
  detector decides. You write the whole new predicate.
- **split** — a body sentence, or a clause the detector check cut, is
  itself a constraint on the member with its own truth value. It becomes
  a rule of its own, and you write its heading, predicate, and trailer.
- **redundant** — another rule already decides everything this one
  decides, in this file or a sibling in `standards/<name>/`. The rule
  goes, and you name the rule that covers it.
- **keep** — the rule has no body and its predicate matches the
  detector.

A rule may need fold and split both; give both, the fold row first.
Redundant wins over every other verdict. Judge every rule with fresh
eyes: the tree is months old, and a rule earns its place only by
deciding something no other rule decides.

## The rows

Return rows and nothing else: no preamble, no summary, no advice. One
block per rule in file order, and a condition's block before its
rules':

```
### <name>.<slug> · <kind> · <verdict>
<for fold: the complete new predicate, heading excluded>
<for split: the new heading, then the predicate, then the trailer>
<for redundant: the id of the rule that covers it>
<for delete or keep: nothing>
```

Then one closing block:

```
### detector ids
<detector id> → <name>.<slug>     one line per id the detector emits for a rule in this file
<detector id> → none              one line per id with prefix <name> that matches no rule here
```

A predicate that fails the litmus gets the verdict `fails-litmus` and
one sentence saying which of the three tests it fails. Propose no
rewrite for it.
