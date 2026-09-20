---
type: Standard-Ruleset
title: Cross-References
description: The cross-reference grammar — root-absolute Links in-bundle, workspace Citations across repos, the rootless forms, and fragment anchors that match a heading's slug
population: "a reference from an authored document to a workspace file, directory, or skill, except inside a fenced code block, or from inside a numbered Decision Record"
---

# Cross-References

A reference from one document to another, or to a directory or a skill.
Which form it takes depends on where the target lives, this repo or
another, and on whether the referencing file has a fixed repo root, a
single repo it is always read from. Both link forms are inline; there
is no separate citations section. A fenced code block, triple backticks
or `~~~`, may hold `~/workspace/` and `/`-root paths in shell examples
or sample output, and a reference inside it is out of scope. A numbered
[Decision Record](/standards/decisions/records.md) is exempt as a
source, since a record frozen at merge goes stale as its referents
move; references to a record are checked like any other.

The reasoning behind the rules is the
[Knowledge Organization Guide](/docs/guides/knowledge-organization.md).

## Reference resolves

A reference names a file or a directory that exists. A root-absolute
target resolves against the repository root of the checkout the
referencing file is read in; a `~/workspace/<repo>/` target naming that
same repository resolves against that checkout too, and a
`~/workspace/<repo>/` target naming any other repository resolves at
its absolute path under `~/workspace/`.

`knowledge-organization.reference-resolves` · deterministic

## Fragment anchor matches the slug

A reference that appends `#anchor` to a markdown file names in that
anchor the GitHub slug of a heading the file carries.

`knowledge-organization.fragment-anchor-matches-the-slug` · deterministic

## Stable named anchor

A reference's `#anchor` names its target heading by the words of the
heading and carries no number that is the heading's position in the
file. Where the target numbers every heading by position and carries no
other anchor, the reference drops the anchor and names the concept the
heading carries in the link text.

`knowledge-organization.stable-named-anchor` · deterministic

## Citation, another repo

A reference to a file or directory in a repository other than the
referencing file's own is an inline link whose target is the full
workspace path, beginning `~/workspace/<repo>/`.

`knowledge-organization.citation-another-repo` · deterministic

## Skill invocation

A reference to a skill is its bare slash invocation, `/<skill-name>`,
with no link and no code markup.

`knowledge-organization.skill-invocation` · deterministic

## Fixed repo root

The referencing file has a fixed repo root: no segment of its path
inside the repository is `skills`, `rules`, or `agents`.

`knowledge-organization.fixed-repo-root` · deterministic

### Link, same bundle

A reference to a file or directory in the referencing file's own
repository is an inline link whose target is a root-absolute path,
beginning `/` and naming the path from the repository root.

`knowledge-organization.link-same-bundle` · deterministic

## No fixed repo root

The referencing file has no fixed repo root: a segment of its path
inside the repository is `skills`, `rules`, or `agents`.

`knowledge-organization.no-fixed-repo-root` · deterministic

### Workspace path for a stable location

A reference to a file at a stable location in the referencing file's
own repository is an inline link whose target is the full
`~/workspace/<repo>/<path>` path, unless the target is inside the
referencing file's own skill bundle.

`knowledge-organization.workspace-path-for-a-stable-location` · deterministic

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
