---
type: Standard
title: Cross-References
description: The cross-reference grammar — root-absolute Links in-bundle, workspace Citations across repos, the rootless forms, fragment anchors that match a heading's distinct slug, and the link text that names the target
population: "a reference from an authored document to a workspace file, directory, or skill, except inside a code block, fenced or indented, or from inside a numbered Decision Record"
---

# Cross-References

A reference from one document to another, or to a directory or a skill.
Which form it takes depends on where the target lives, this repo or
another, and on whether the referencing file has a fixed repo root, a
single repo it is always read from. Both link forms are inline; there
is no separate citations section. A code block, fenced or indented, may
hold `~/workspace/` and `/`-root paths in shell examples or sample
output, and a reference inside it is out of scope. A numbered
[Decision Record](/standards/decisions/records.md) is exempt as a
source, since a record frozen at merge goes stale as its referents
move; references to a record are checked like any other.

> **Why.** The wrapper records intent: an inline link means "go open
> this"; inline code means "this file exists conceptually", the right
> form for a file whose location varies between repos; a bare
> `/<skill-name>` is how a skill is invoked.

## Reference resolves

A reference names a file or a directory that exists in the referencing
file's own repository.

`knowledge-organization.reference-resolves` · deterministic

> **Why.** A `~/workspace/<repo>/` target naming another repository
> resolves against that repo's main checkout. A repo cannot check the
> other side from its own files, so the predicate binds same-repo
> targets.

## Fragment anchor matches the slug

A reference that appends `#anchor` to a markdown file names in that
anchor the GitHub slug of a heading the file carries.

`knowledge-organization.fragment-anchor-matches-the-slug` · deterministic

## Headings slugify distinctly

No two headings of a markdown file carry the same GitHub slug.

`knowledge-organization.headings-slugify-distinctly` · deterministic

> **Why.** GitHub disambiguates a repeated slug by appending the
> heading's position, so the second heading's anchor is positional and
> breaks the moment the file is reordered, the failure
> [stable named anchor](#stable-named-anchor) bars.

## Stable named anchor

A reference's `#anchor` carries no number that is the heading's
position in the file; where the target numbers every heading by
position and carries no other anchor, the reference carries no anchor.

`knowledge-organization.stable-named-anchor` · deterministic

> **Why.** A positional anchor, `#223-revision` or an in-prose
> `§2.10`, breaks silently the moment its target is renumbered or
> reordered, while a stale named anchor names a slug the file does
> not carry.

## Link text names heading or title

A reference's link text is the target heading's text, or the target
document's title where the heading does not fit the citing sentence.

`knowledge-organization.link-text-names-heading-or-title` · stochastic

> **Why.** A heading is a proposition and a citation is most often a
> noun phrase inside a sentence, so the two forms collide; the title is
> the noun phrase naming the same target, and the anchor carries the
> precision the text drops.

## Workspace path for another repo

A reference to a file or directory in a repository other than the
referencing file's own is an inline link whose target is the full
workspace path, beginning `~/workspace/<repo>/`.

`knowledge-organization.workspace-path-for-another-repo` · deterministic

> **Why.** The full workspace path resolves to that repo's main
> checkout, its published state, and the form is self-describing: the
> repo name is in the path, so no external convention is needed to
> read it.

## Slash invocation for a skill

A reference to a skill names it by its slash invocation,
`/<skill-name>`.

`knowledge-organization.slash-invocation-for-a-skill` · deterministic

## Fixed repo root

The referencing file has a fixed repo root: no segment of its path
inside the repository is `skills`, `rules`, or `agents`.

### Root-absolute path in the same repo

A reference to a file or directory in the referencing file's own
repository is an inline link whose target is a root-absolute path,
beginning `/` and naming the path from the repository root.

`knowledge-organization.root-absolute-path-in-the-same-repo` · deterministic

> **Why.** A root-absolute path resolves against the reader's own
> checkout root, so it points at the copy that matches the checkout
> the reader is in, main checkout or per-issue worktree. A
> `~/workspace/<this-repo>/` path jumps to the main checkout from
> inside a worktree, a different and possibly stale copy.

## No fixed repo root

The referencing file has no fixed repo root: a segment of its path
inside the repository is `skills`, `rules`, or `agents`.

### Workspace path for a stable location

A reference to a file in the referencing file's own repository is an
inline link whose target is the full `~/workspace/<repo>/<path>` path,
unless the target is inside the referencing file's own skill bundle.

`knowledge-organization.workspace-path-for-a-stable-location` · deterministic

> **Why.** A runbook, a skill bundle, an agent definition, or a
> global rule under `~/.claude/` is loaded from arbitrary repos, so a
> leading `/` in one has no root to resolve against; the full
> workspace path is the one form that resolves from anywhere.

### Relative path inside the bundle

A reference to a file inside the referencing file's own skill bundle, a
sibling, a file under `references/`, or the parent, is an inline link
whose target is a path relative to the referencing file.

`knowledge-organization.relative-path-inside-the-bundle` · deterministic

### Inline code for a varying location

A reference to a file whose path varies between repositories,
`CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, or `Makefile`, or to a
directory, `docs/decisions/`, is inline code.

`knowledge-organization.inline-code-for-a-varying-location` · stochastic
