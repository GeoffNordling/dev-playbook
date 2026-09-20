---
type: Guide
title: Decisions Guide
description: The thinking behind the Decision Record rules — the bar with worked examples, where a record lives, how a new record is numbered, why a record is frozen after merge, and what the optional sections are for
---

# Decisions Guide

The guide behind
[Decision Record Conventions](/standards/decisions/records.md), the
ruleset that binds a numbered record under a repo's `docs/decisions/`.
This guide carries the examples and the reasoning; nothing here is
enforced.

## The bar

A record records a decision that is hard to reverse, surprising without
its context, and the outcome of a real trade-off, all three at once
([The bar](/standards/decisions/records.md#the-bar)). An
easy-to-reverse decision is simply reversed, not recorded. An
unsurprising one raises no questions. One with no real alternative
leaves nothing to record beyond "we did the obvious thing."

Decisions that clear the bar:

- **Architectural shape.** "We're using a monorepo." "The write model
  is event-sourced, the read model is projected into Postgres."
- **Integration patterns between contexts.** "Ordering and Billing
  communicate via domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus,
  auth provider, deployment target. Not every library, just the ones
  that would take a quarter to swap out.
- **Boundary and scope decisions.** "Customer data is owned by the
  Customer context; other contexts reference it by ID only." The
  explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path.** "We're using manual
  SQL instead of an ORM because X." Anything where a reasonable reader
  would assume the opposite; these stop the next engineer from
  "fixing" something that was deliberate.
- **Constraints not visible in the code.** "We can't use AWS because of
  compliance requirements." "Response times must be under 200ms
  because of the partner API contract."
- **Rejected alternatives when the rejection is non-obvious.** When
  GraphQL was considered and REST won for subtle reasons, the record
  stops GraphQL being proposed again in six months.

## Where a record lives

A record sits in the repo of the thing it governs
([Scope](/standards/decisions/records.md#scope)): a decision about one
repo is recorded in that repo's `docs/decisions/`, and a decision about
the workspace, a standard, a cross-repo convention, or the software
factory is recorded in dev-playbook. The directory is created lazily,
with the first record.

`ref-lint` classifies every file it finds there. A numbered record is
exempt as a reference source, since an immutable record goes stale as
its referents move; `index.md` and `README.md` are validated like any
other document; and any other file stops the run rather than being
silently exempted.

## Numbering a new record

A writer numbering a new record scans `docs/decisions/` for the highest
existing number and increments by one, so the sequence has no gaps
([Sequential numbering](/standards/decisions/records.md#sequential-numbering)).
`decisions-lint` reports a number that is not zero-padded to four
digits, a duplicate, and a gap.

## A record can be one paragraph

The value is in recording that a decision was made and why, not in
filling out sections. A record is a concept document, so it carries the
standard `type`, `title`, and `description` frontmatter; the
`description` is the record's triage line and feeds
`docs/decisions/index.md`, and on a one-sentence record it echoes the
body, since the description serves triage and the body is the record.

A record written after the fact carries the decision's date, not the
writing date, and where that day is genuinely unrecoverable the key
holds `null` rather than a guess
([Date](/standards/decisions/records.md#date)).

## Why a record is frozen after merge

Before its introducing pull request merges, a record is ordinary
development-branch work and is edited freely. After merge, the body is
never rewritten, neither to match later state nor to correct a decision
that was reversed
([Immutable after merge](/standards/decisions/records.md#immutable-after-merge)).
Thereafter only the `status` key changes, and a reversal or a
replacement is a new record that sets the old one's `status` to
`superseded by NNNN`. A record that needs no status omits the key. This
is why a record is the one exemption from
[Current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only):
it is a dated record of a past decision, the choice made, the
alternatives rejected, and the context that forced it.

## The optional sections

Beyond the template a record carries at most two further sections
([Optional sections](/standards/decisions/records.md#optional-sections)):

- **Considered Options** — the rejected alternatives, when they are
  worth remembering.
- **Consequences** — the non-obvious downstream effects, when they
  need to be called out.

Most records carry neither.

## An external-convention evaluation

A record whose decision is a verdict on something outside the
workspace, a skill, a skill collection, a framework, or a technique,
pins the exact state it examined, so a later reader can tell whether
the verdict still applies. A record that adopted nothing is a record
all the same.
