---
type: Standard
title: Working Documentation Sets
description: How the in-process Markdown files of one work stream are organized as a set — root plan, child edges, single-home facts, ledgers, and local terms
---

# Working Documentation Sets

A **working documentation set** is the group of Markdown files one stream of
in-process work accumulates — plans, design notes, ledgers — committed to the
repo and drained into permanent homes or deleted when the work merges. This
standard governs the set level: how the files relate to each other. Each
file's prose answers to the [prose standard](/standards/prose.md); members
typically carry `type: General-Sheet`, the registry's genre for a working
document whose type is not yet settled.

The `/working-doc-set-deslop` skill sends a set through an agent that
audits it against this standard and then fixes what the audit finds,
leaving every edit uncommitted for the user's diff review.

## Shape

A set is a tree: one root file, and child files reached from it by links.

- The root links every member, each with a one-line summary of what it holds.
- A child holds its own detail and links to the root or a sibling for theirs;
  restating another member's content is duplication.
- A working file unreachable from the root is an orphan.

## Next steps

The root holds the set's next steps — current state and what comes next for
the work as a whole. A child may carry its own to-dos for its own topic;
work at one level works that level's list. Plan prose is
edit-in-place and answers to
[current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only).

## Ledgers

A ledger is an append-only member or section: entries are added as they are
ruled and never revised. Outcomes — rulings, finished artifacts, accepted
residuals — go in ledgers rather than plan prose, because append-only text
stays true without maintenance while edit-in-place text decays wherever
attention leaves.

## One home per fact

Each fact, rule, and decision lives in exactly one member; every other
member links. This extends the prose conventions'
[one rule, one place](/standards/prose/conventions.md#one-rule-one-place)
across the set.

## Buckets

A bucket is a named section role a fact type files under — the single home
above, made navigable. The set defines its own bucket names; an audit checks
the set against the names it declares, never against a fixed list. The
canonical buckets, a suggestion for a fresh set:

- **Goal** — what the work is for.
- **Principles** — the judgment calls that guide choices.
- **Constraints** — the hard bounds the work operates under, distinct from
  principles.
- **Terms** — see below.
- **Next steps** — the root's covers the work as a whole, a child's its own
  topic.
- **Ledger** — append-only outcomes.
- **Unfiled** — the escape valve: material fitting no bucket lands here
  explicitly, awaiting triage, instead of being force-fitted or scattered.

## Terms

A term coined by the work and used in more than one member appears in the
root's terms bucket with a one-line definition. The bucket is
exploratory-grade — the settled subset is promoted to `CONTEXT.md` when the
work completes, per
[CONTEXT.md Content](/standards/knowledge-organization/context-content.md).
