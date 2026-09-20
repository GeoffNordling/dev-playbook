---
type: Standard-Ruleset
title: Indexes
description: The index.md file — typeless, an introduction naming what the directory holds, a listing of every concept document with its description, alphabetical unless declared otherwise, authored not generated
population: "an index.md"
---

# Indexes

The `index.md` of a directory, the navigational listing that lets an
agent see what the directory holds, and read each document's one-line
`description`, without opening every file. A repo's agent-navigated
documentation is one
[Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog)
bundle per the [OKF SPEC](/standards/references/okf-spec.md), the whole
repository: an agent triages a document by its frontmatter and navigates
between documents by the per-directory `index.md`, loading a body only
when the document is relevant.

## Typeless

An `index.md` carries no OKF `type`.

`knowledge-organization.typeless` · deterministic

## The introduction

An `index.md` holds prose between its H1 and its first listed entry.

`knowledge-organization.the-introduction` · deterministic

## The opening sentence

The introduction of an `index.md` opens with a single sentence naming
what the directory holds, in that directory's own vocabulary; where the
listing's sole entry carries a `description` that already says what the
directory holds, the sentence says what the directory is for instead.

`knowledge-organization.the-opening-sentence` · stochastic

## The listing

An `index.md` lists, as a bullet holding a root-absolute markdown link
and exactly once each, every
concept document in its own directory and every child directory's own
`index.md`, and lists nothing else; each concept document's entry
carries that document's frontmatter `description` verbatim.

`knowledge-organization.the-listing` · deterministic

## Ordering

Within each group of an `index.md`'s listing, the concept documents and
then the child-directory links, entries are in alphabetical order by
link title, compared case-insensitively, and a `README.md` entry is the
first entry of the whole listing; an introduction line beginning
`Ordering:`, one before the first listed entry, releases the
alphabetical order of both groups and never the `README.md` entry's
place.

`knowledge-organization.ordering` · deterministic

## The root index

The `index.md` at the repository root.

`knowledge-organization.the-root-index` · deterministic

### OKF version declared

The `index.md` at the repository root declares `okf_version` in its
frontmatter.

`knowledge-organization.okf-version-declared` · deterministic
