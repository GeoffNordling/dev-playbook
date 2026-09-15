---
type: General-Sheet
title: Specifying a Loop
description: How a loop is told what to do without the user present — the predicate, the three written forms an idea takes, and the loop that proposes predicates rather than edits
---

# Specifying a Loop

How work reaches a loop when the user is not there. Speculative, per
[ROOT.md](/worktree-synthesis-notes-working-docs/loop/ROOT.md).

## The predicate

A **predicate** is defined in [Glossary](/worktree-synthesis-notes-working-docs/glossary.md), and
[Writing Predicates](/worktree-synthesis-notes-working-docs/doc-type-system/writing-predicates.md#the-litmus) holds the
litmus a candidate passes before it is one.

A predicate says what is true of a member. It does not say why, which
is the rule's reason, and it does not say how to fix it, which is a
runbook's.

The verifier is a script or a judge; a rule a judge decides is
stochastic and still a predicate. A loop's check audits it like any
other; whether a repo boundary also runs it is that boundary's wiring.
[Writing Predicates](/worktree-synthesis-notes-working-docs/doc-type-system/writing-predicates.md)
is how one is written.

## The three written forms

An instruction spoken in a session is spent when it is carried out. An
idea that is written down outlives the session and reaches a loop. It
takes one of three forms:

| Form | Lifetime | Home | Example |
|---|---|---|---|
| **Goal** | one issue | an issue with acceptance criteria | write `loops/doc-type-system.md` |
| **Predicate** | standing | a rule in a Standard | every `definition.md` has a verbs list |
| **Objective** | standing | a scalar pushed down under the predicates | the fewest verbs across the roster |

Acceptance criteria are predicates with a lifetime of one issue. An
objective is descended by proposing a step, a merge of two verbs, that
the user accepts or vetoes; the predicates and the veto are what
"suffice" means. The software factory runs on goals plus predicates.
The doc-type system so far has neither written, and the standing kind
is the one it is short on.

When an idea arrives, the move is to write its form, not to do the fix.
The fix follows from an accepted predicate failing its check, and a loop or
an agent does it later.

## The loop that proposes

The user's intent is never handed to a loop. The Standard is its
written approximation, grown one predicate at a time, and the loop has
two motions against it:

```
                       the user's intent
                              │ approximated, one predicate at a time
                              ▼
        ┌──────────────────────────────────────────────┐
        │  STANDARD  the accepted predicates, as rules │
        └──────┬───────────────────────────▲───────────┘
               │ checks read               │ an accepted predicate lands
   ┌───────────┼───────────────────────────┼─────────────┐
   │  LOOP     ▼                           │             │
   │   apply: act on failing checks,       │             │
   │          edit only what a failing     │             │
   │          predicate authorizes         │             │
   │   propose: draft candidate predicates,│             │
   │          each with citation or        │             │
   │          marked invented, and the     │             │
   │          members that fail it today   │             │
   │                           │ yield     │             │
   └───────────────────────────┼───────────┼─────────────┘
                               ▼           │
                        the user: yes ─────┘
                                  no ────► kept with its reason, never re-proposed
```

- **Soft guidance and hard predicates go to different acts.** Words such
  as *parallel* and *parsimonious* reach only the proposing act, as what
  kind of candidates to draft. The applying act sees only failing checks.
- **Proposals are predicates, never edits.** Rejecting a predicate
  costs the user five lines; rejecting a diff costs an hour. The loop
  cannot change the system without a predicate authorizing it.
- **Two kinds.** A cited proposal names where the predicate is
  already stated or implied. An invented one says so. The user triages them at
  different speeds.
- **A no is a predicate waiting to be written.** A rejected proposal
  is kept with its reason, and the reason is itself a candidate
  predicate, about the ideas rather than the files. The loop's memory
  is the Standard and the rejections, never a transcript.
- **One loop.** Propose and apply share a loop until the applying act is
  large enough to run unattended for hours; then it is its own loop.
- **The residue.** Intent that resists every form stays the user's. The
  loop surfaces it as a question rather than guessing.

## Acronyms

None.
