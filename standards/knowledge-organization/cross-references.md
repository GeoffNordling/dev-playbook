---
type: Standard
title: Cross-References
description: The cross-reference grammar — root-absolute Links in-bundle, workspace Citations across repos, the runbook forms, and fragment anchors that match a heading's slug
population: "a reference from an authored document to a workspace file, directory, or skill, except inside a fenced code block"
---

# Cross-References

A reference from one document to another, or to a directory or a skill.
Which form it takes depends on where the target lives, this repo or
another, and on whether the referencing file has a fixed repo root, a
single repo it is always read from. Both link forms are inline; there
is no separate citations section. A fenced code block, triple backticks
or `~~~`, may hold `~/workspace/` and `/`-root paths in shell examples
or sample output, and ref-lint skips it. ref-lint is the authority
([Knowledge Organization](/standards/knowledge-organization.md)).

## Fragment anchor matches the slug

A reference that appends `#anchor` names the target heading's GitHub
slug.

ref-lint computes and validates the slug, so a stale or misspelled
anchor fails the commit.

## Stable named anchor

An anchor names a heading by a stable slug, never by a position: no
numbered fragment, `#223-revision`, and no in-prose heading number,
`§2.10`.

A positional anchor breaks silently the moment its target is renumbered
or reordered. Where the target numbers every heading positionally and
exposes no stable anchor, the reference names the concept the heading
carries and drops the number, so a reader finds it by name.

## Fixed repo root

A reference from a file with a fixed repo root: a concept document, or
a repo's own `CLAUDE.md`, which Claude Code loads only when the session
is already inside that repo.

### Link, same bundle

A reference to a document in the same repo is a root-absolute path, a
target beginning with `/`, resolved against the bundle root, the repo
root.

```markdown
[prose/conventions.md](/standards/prose/conventions.md)
```

A root-absolute link resolves against the reader's own checkout root,
the current working directory's repo, so it points at the copy that
matches the checkout the reader is in, main checkout or per-issue
worktree. A same-repo reference written `~/workspace/<this-repo>/…`
fails ref-lint as `wrong-form`, whether or not the target exists: from
inside a worktree that path jumps to the main checkout, a different and
possibly stale copy.

### Citation, another repo

A reference to a document in a different repo is its full workspace
path, beginning with `~/workspace/`.

```markdown
[Friction log](~/workspace/mission-control/friction/log.md)
```

A cross-repo citation resolves to that repo's main checkout, its
published state. `~/workspace/<repo>` is self-describing: the repo name
is in the path, so no external convention is needed to interpret it.

## No fixed repo root

A reference from a
[runbook](/standards/harness/runbook-conventions.md), a skill bundle or
agent definition, or from global `~/.claude/` configuration such as
`rules/`: files loaded across arbitrary repos, with no root for `/` to
resolve against.

### Workspace path for a stable location

A reference to a file at a stable workspace location is an inline link
with its full `~/workspace/<repo>/<path>` path, even when that file is
in the same repo.

The same-repo case resolves against the reader's own checkout,
worktree included
([Resolve same-repo paths](/dotfiles/dot-claude/CLAUDE.md#resolve-same-repo-paths)).

### Relative path inside the bundle

A reference to a file inside the same skill bundle, a sibling,
`references/`, or the parent, is an inline link with a relative path:
`[ui.md](references/ui.md)`.

### Inline code for a varying location

A reference to a file in the user's repo whose location varies,
`CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, `Makefile`, or to a
directory, `docs/decisions/`, is inline code.

### Bare skill invocation

A slash-skill invocation is bare, `/<skill-name>`, with no markup.

The wrapper records intent: an inline link means "go open this"; inline
code means "this file exists conceptually". ref-lint treats inline code
and a bare invocation as prose.
