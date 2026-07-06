---
type: Standard
title: Standards and Standard Cards
description: What a standard is and the standard-card format — four pointer cells that catalog every standard for one-hop lookup
---

# Standards and Standard Cards

Returning to a topic months later should not require re-deriving shared
understanding over several turns of conversation. Each standard therefore
gets a **standard card**: a small fixed-format record that tells a human or
agent where to look. The card does not define the standard — the files it
points at do that. It aggregates pointers so a thought that originates at
the abstract level ("how do we do X here?") resolves to concrete files in
one hop.

## What a standard is

A standard is named by the question it governs, not by the current answer.
"How knowledge is organized in markdown" is a standard; the OKF spec is
today's answer, pointed at by its define cell. The litmus: if the
implementation could be swapped while the name stays true, it is a
standard.

- **Membership is non-exclusive.** A file may belong to more than one
  standard at once. Standards are overlapping views over the repository,
  not a partition of it — pointers, not directory placement, say what
  belongs to what.
- **A standard may have sub-standards,** one level deep.

## What a standard is not

Not everything normative is a standard. A device built to serve a purpose
— an artifact format, a tool, a template — is an answer, not a governed
question, and so belongs inside a cell rather than in the catalog. Such
devices are **instruments** ([instruments/](/instruments/index.md)); each
carries a prescriptive contract of its own, typed `Instrument Spec`.

## The card

A card is a markdown file at `standards/<name>.md` with
`type: Standard Card` frontmatter: a heading, one sentence naming the
governed question, then exactly four cells as sections. Each cell holds
annotated pointers; an empty cell states an explicit "none" so gaps stay
visible. Cards are thin — often just a handful of pointers — and never
restate the content of their targets.

- **Define** — the contract: prose documents and canonical reference
  files.
- **Audit** — read-only deviation detection: the tools that report
  nonconformance without blocking anything.
- **Enforce** — blocking gates: the venues where nonconformance stops a
  commit, a check run, or a merge.
- **Adopt** — anything that helps bring a repository into conformance,
  such as templates or migration procedures. Often "none": the generic
  path is an agent reading the define cell and fixing the repository.

The living exemplars are the cards themselves: [Build](/standards/build.md)
and [Meta-Standard](/standards/standard.md) — the latter is this standard's own
card, since the meta-standard is an instance of the format it defines.

## The catalog

The catalog of all standards is [standards/index.md](/standards/index.md).
okf-lint's index rule already forces that index to list every card with a
matching description, so catalog completeness is enforced by the existing
hook suite rather than by new tooling.

## Drift

Standards drift at two grains, each with its own detector:

1. **Fine grain** — a specific document or passage must keep meaning what
   it meant when validated.
   [Judgments](/instruments/judgments/index.md) cover this: the
   content-addressed cache expires a verdict the moment the underlying
   bytes change.
2. **Contract grain** — a change to a define cell obligates rework across
   adopting repositories. This is a version bump of the standard,
   propagated and verified by workspace-level sweeps.
