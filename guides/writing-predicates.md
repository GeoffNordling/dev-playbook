---
type: Guide
title: Writing Predicates
description: How to write a rule so a verifier can decide it — one member, one moment, one bool, the property not the witness, the file it reads named, what not how, the future not the past, no new nouns, the trailer, and what is not a predicate; read before writing a rule
---

# Writing Predicates

The work is writing a rule's predicate so that a script or a judge can
decide it. A predicate and a specification are defined in
[CONTEXT.md](/CONTEXT.md#specification). Test each draft
against the litmus first. The sections after it each give one habit of
a predicate that passes, then the trailer that follows it, then what
is not a predicate at all.

## The litmus: one member, one moment, one bool

The rule is
[Every predicate decidable of one member](/standards/doc-type/standard-conventions.md#every-predicate-decidable-of-one-member).
Write the predicate as if it were `def rule(member) -> bool`. It
passes when:

- **One member.** It reads the member and the state the member sits
  in. It never compares the member to another member.
- **One moment.** It reads what is on disk now. No history, no
  transcript, no "since the last run".
- **One bool.** Two careful reviewers cannot disagree. If they could,
  it is taste, and taste is an objective or a judgment call, not a
  predicate.

Ask of every draft: what would verify it? If the answer is a
check, the rule is deterministic. If the answer is a judge with a
prompt, the rule is stochastic and the predicate is the prompt. If
there is no answer, it is not yet a predicate.

## The predicate specifies the property, not the witness

A reference model is one state that satisfies the spec. Rewriting it
as rules, "the types are Runbook, Standard, and Loop", "the verbs are
these ten", specifies that one state and nothing else. The predicate
generalizes: "every doc-type declares a non-empty set of verbs". Ask
of every draft whether a state the author has not imagined could
satisfy it. If only the drawn one can, it is the witness, not the
property.

What is true of one named member only goes under a condition: a rule
"the doc-type is Runbook", and beneath it the rules for that member.

## The predicate names the file the verifier reads

A verifier opens a file. Write the file: `encoding.md`, not "the
encoding"; `contract-shape.md`, not "the contract shape". The concept
is the mapping, the class, the sentence; the file is where it is
written, and only the file can be read. Where a verifier reads a path
pattern, write the pattern: `doc-types/<name>/`.

## The predicate says what, never how or why

The first paragraph is the predicate and says what is true of the
member. The reason goes after it. The fix goes in a runbook. A
predicate that says "a check rejects…" or "the commit hook
blocks…" has slipped into the wiring of a
gate and is never written in a rule. Cut it and write the
condition the check would decide: "every instance parses under
`encoding.md` into one object of the class".

Replace a vague relation with a decidable one. "States how prose
becomes parts" decides nothing. "Maps each markdown construct to one
part of the class, and every instance parses into one object of it"
decides.

## The predicate describes the future, never forbids the past

A predicate says what is true of the target state. It never prohibits
a shape that exists only today: "no Standard names the script that
runs it" guards against a habit the refactor removes, and once the
shape is gone the rule has nothing to decide. Write the positive
predicate the new shape satisfies, and let the old shape fail it.

## No new nouns

Only a word already defined in one place is used. Prefer
the path, `doc-types/<name>/`, to a coined name for it. Prefer the
industry term to a local one: condition, verifier, specification.
One meaning per word: the word used for a rule's guard is condition,
and the same word is never used in a second sense in the same
document. Where a term is needed, define it once, in Terms,
and link to the definition everywhere else.

## The trailer carries the id and the kind

After the predicate paragraph, one line: the rule id, `<family>.<slug>`,
the directory and the heading's slug, and the kind, deterministic or
stochastic, per
[A rule: heading, predicate, trailer](/standards/doc-type/standard-conventions.md#a-rule-heading-predicate-trailer).
A condition is an H2 with no trailer.

## An objective, a goal, and a permission are not predicates

- **An objective**
  ([CONTEXT.md](/CONTEXT.md#specification))
  ranks states that satisfy the predicates; it is never one of them.
- **A goal** is a predicate with the lifetime of one workstream; it
  lives in the workstream's
  [draft Standard](/CONTEXT.md#governance), which is deleted or
  promoted under `standards/` when the user accepts the workstream.
- **A permission**, "two doc-types may share a verb", is the absence of
  a rule. Write nothing, and say in the introduction that the absence
  is deliberate.
