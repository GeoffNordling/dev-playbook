---
type: General-Sheet
title: Writing Predicates
description: How to write a rule so a verifier can decide it — one member, one moment, one bool, the property not the witness, the file it reads named, what not how, the future not the past, no new nouns, the trailer, and what is not a predicate
---

# Writing Predicates

A predicate and a specification are defined in [Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms).
This guide is how to write one so that a script or a judge can decide
it, learned from the corrections made while writing the doc-type
system's own specification. Speculative, per
[Doc-Type System](/worktree-synthesis-notes-working-docs/doc-type-system/ROOT.md): a guide
for now, and likely the Standard that governs how a predicate is
written once its own sections pass the litmus. The `/write-predicates`
skill will point here.

## The litmus

Write the predicate as if it were `def rule(member) -> bool`. It
passes when:

- **One member.** It reads the member and the state the member sits
  in. It never compares the member to another member.
- **One moment.** It reads what is on disk now. No history, no
  transcript, no "since the last run".
- **One bool.** Two careful reviewers cannot disagree. If they could,
  it is taste, and taste is an objective or a judgment call, not a
  predicate.

Ask of every draft: how would the linter work? If the answer is a
script, the rule is deterministic. If the answer is a judge with a
prompt, the rule is stochastic and the predicate is the prompt. If
there is no answer, it is not yet a predicate.

## Specify the property, not the witness

A reference model is one state that satisfies the spec. Rewriting it
as rules, "the types are Runbook, Standard, and Loop", "the verbs are
these ten", specifies that one state and nothing else. The predicate
generalizes: "every doc-type declares a non-empty set of verbs". Ask
of every draft whether a state the author has not imagined could
satisfy it. If only the drawn one can, it is the witness, not the
property.

What is true of one named member only goes under a condition: a rule
"the doc-type is Runbook", and beneath it the rules for that member.

## Name what the verifier reads

A verifier opens a file. Write the file: `encoding.md`, not "the
encoding"; `contract-shape.md`, not "the contract shape". The concept
is the mapping, the class, the sentence; the file is where it is
written, and only the file can be read. Where a verifier reads a path
pattern, write the pattern: `doc-types/<name>/`.

## Say what, never how or why

The first paragraph is the predicate and says what is true of the
member. The reason goes after it. The fix goes in a runbook. A
predicate that says "a detector rejects…" or "the commit hook
blocks…" has slipped into enforcement, which is the wiring of a
boundary and is never written in a rule. Cut it and write the
condition the detector would decide: "every instance parses under
`encoding.md` into one object of the class".

Replace a vague relation with a decidable one. "States how prose
becomes parts" decides nothing. "Maps each markdown construct to one
part of the class, and every instance parses into one object of it"
decides.

## Describe the future, never forbid the past

A predicate says what is true of the target state. It never prohibits
a shape that exists only today: "no Standard names the script that
runs it" guards against a habit the refactor removes, and once the
shape is gone the rule has nothing to decide. Write the positive
predicate the new shape satisfies, and let the old shape fail it.

## No new nouns

A word that is not already defined in one place is not used. Prefer
the path, `doc-types/<name>/`, to a coined name for it. Prefer the
industry term to a local one: condition, verifier, specification.
One meaning per word: the word used for a rule's guard is condition,
and the same word is never used in a second sense in the same
document. Where a term is needed, define it once, in Terms,
and link to the definition everywhere else.

## The trailer

After the predicate paragraph, one line: the rule id, `<standard>.<slug>`,
and the kind, deterministic or stochastic. A condition is a rule and
carries both too.

## What is not a predicate

- **An objective**
  ([Terms](/worktree-synthesis-notes-working-docs/ROOT.md#terms))
  ranks states that satisfy the predicates; it is never one of them.
- **A goal** is a predicate with the lifetime of one issue; it lives
  in the issue.
- **A permission**, "two doc-types may share a verb", is the absence of
  a rule. Write nothing, and say in the introduction that the absence
  is deliberate.

## Acronyms

None.
