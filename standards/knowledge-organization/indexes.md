---
type: Standard
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
bundle per the [OKF SPEC](/docs/mirrors/okf-spec.md), the whole
repository: an agent triages a document by its frontmatter and navigates
between documents by the per-directory `index.md`, loading a body only
when the document is relevant.

> **Why.** An `index.md` is authored, never generated: a generator
> could copy the descriptions, but the introduction and the order are
> the writer's judgment.

## No OKF type

The frontmatter of an `index.md` has no `type` key.

`knowledge-organization.no-okf-type` · deterministic

## Introduction between H1 and listing

An `index.md` has at least one line of prose between its H1 and its
first listed entry. A heading and an `Ordering:` line are not prose.

`knowledge-organization.introduction-between-h1-and-listing` · deterministic

## Opening sentence names what the directory holds

The introduction of an `index.md` opens with a single sentence naming
what the directory holds, in that directory's own vocabulary; where the
listing's sole entry carries a `description` that already says what the
directory holds, the sentence says what the directory is for instead.

`knowledge-organization.opening-sentence-names-what-the-directory-holds` · stochastic

> **Why.** Restating the path is no introduction: "the files in
> `standards/`" tells a reader nothing the H1 did not.

## One entry per concept document and child directory

An `index.md` has exactly one bullet for each concept document in its
directory and one for each child directory's `index.md`, and no other
`-`, `*`, or `+` bullet outside a fenced code block or a blockquote. Each bullet is a link whose target starts `/`.
A concept document's bullet ends with ` — ` and that document's
frontmatter `description`, character for character.

`knowledge-organization.one-entry-per-concept-document-and-child-directory` · deterministic

## Alphabetical unless declared otherwise

In an `index.md`, the `README.md` bullet, where there is one, is the
first bullet. The concept-document bullets come next, then the
child-directory bullets, and each group is sorted by link text,
ignoring case. A line that starts `Ordering:` above the first bullet
turns off the sorting and the group order, and never moves the
`README.md` bullet.

`knowledge-organization.alphabetical-unless-declared-otherwise` · deterministic

> **Why.** A reader cannot tell unstated meaning from randomness, so
> an order that means something declares itself.

## The root index

The `index.md` at the repository root.

### OKF version declared

The `index.md` at the repository root declares `okf_version` in its
frontmatter.

`knowledge-organization.okf-version-declared` · deterministic
