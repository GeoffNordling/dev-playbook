---
type: Standard
title: Cross-References
description: The cross-reference grammar — root-absolute Links in-bundle, workspace Citations across repos, the rootless forms, fragment anchors that match a heading's distinct slug, `#` headings only, and the link text that names the target
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

The target of a reference exists. A `/` target and a
`~/workspace/<this repo>/` target are read from the checkout root; a
relative target is read from the linking file's directory. A relative
target that climbs above the checkout root is not this rule's finding. A
`~/.claude/<rest>` target is read as `dotfiles/dot-claude/<rest>` where
the repo tracks that directory, and is not checked where it does not. A
`~/workspace/<other repo>/` target is read from that repo's main
checkout on this machine.

`knowledge-organization.reference-resolves` · deterministic

> **Why.** A `~/workspace/<repo>/` target naming another repository
> resolves against that repo's main checkout. A repo cannot check the
> other side from its own files, so the predicate binds same-repo
> targets.

## Fragment anchor matches the slug

In a reference to a `.md` file that ends `#anchor`, the anchor is the
GitHub slug of a heading in that file.

`knowledge-organization.fragment-anchor-matches-the-slug` · deterministic

## Headings slugify distinctly

No two headings in a `.md` file, a numbered Decision Record aside,
have the same GitHub slug.

`knowledge-organization.headings-slugify-distinctly` · deterministic

> **Why.** GitHub disambiguates a repeated slug by appending the
> heading's position, so the second heading's anchor is positional and
> breaks the moment the file is reordered, the failure
> [stable named anchor](#stable-named-anchor) bars.

## ATX headings only

A heading is a line of one to six `#` then a space. Outside a fenced
code block and outside the frontmatter block, no line made only of
three or more `=` or `-` sits directly under a line of text.

`knowledge-organization.atx-headings-only` · deterministic

> **Why.** A `---` under a line of text is a heading to one renderer
> and a divider to another, so the model reads `#` headings only and
> this rule keeps the two forms apart; a divider has a blank line
> above it.

## Stable named anchor

The `#anchor` of a reference to a `.md` file, or to a heading of the
same file, does not have the form of a numbered
heading's slug, a run of digits then a hyphen, such as
`#3-bundle-structure` or `#223-revision`.

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

A reference to a file or a directory in another repo is a link whose
target starts `~/workspace/<repo>/`, or `~/.claude/`. A bare
`~/workspace/<other repo>/`
path outside a link, and a relative target that goes above the repo
root, are findings.

`knowledge-organization.workspace-path-for-another-repo` · deterministic

> **Why.** The full workspace path resolves to that repo's main
> checkout, its published state, and the form is self-describing: the
> repo name is in the path, so no external convention is needed to
> read it.

## Slash invocation for a skill

A reference to a skill names it by its slash invocation,
`/<skill-name>`.

`knowledge-organization.slash-invocation-for-a-skill` · stochastic

## Fixed repo root

The referencing file has a fixed repo root: no segment of its path
inside the repository is `skills`, `rules`, or `agents`.

### Root-absolute path in the same repo

In a file with a fixed repo root, a reference to a file or a directory
of the same repo is a link whose target starts `/` and is the path
from the repo root, or starts `~/.claude/`. A relative target other
than a same-file `#anchor`, and a `~/workspace/<this repo>/` path as a
link's target, as a link's text, or bare, are findings.

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

In a file with no fixed repo root, a reference to a file of the same
repo, outside the file's own skill bundle, is a link whose target
starts `~/workspace/<repo>/`, or `~/.claude/` for a file the harness
loads from there. A `/` target, and a relative target that
goes out of the file's own `skills/<name>/` directory, are findings.

`knowledge-organization.workspace-path-for-a-stable-location` · deterministic

> **Why.** A runbook, a skill bundle, an agent definition, or a
> global rule under `~/.claude/` is loaded from arbitrary repos, so a
> leading `/` in one has no root to resolve against; the full
> workspace path is the one form that resolves from anywhere.

### Relative path inside the bundle

In a skill bundle, a reference to another file of the same bundle is
a link with a relative target. A `/`, `~/workspace/`, or `~/.claude/`
target that resolves inside the linking file's own `skills/<name>/`
directory is a finding.

`knowledge-organization.relative-path-inside-the-bundle` · deterministic

### Inline code for a varying location

A reference to a file whose path varies between repositories,
`CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, or `Makefile`, or to a
directory, `docs/decisions/`, is inline code.

`knowledge-organization.inline-code-for-a-varying-location` · stochastic
