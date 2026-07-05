---
type: Standard
title: Cross-References
description: The cross-reference grammar — root-absolute Links in-bundle, workspace Citations across repos, fragment anchors
---

# Cross-References

A cross-reference points from one document to another. Which form it takes
depends on whether the target lives in the **same bundle** (this repo) or
in **another repo**. Both forms are inline — there is no separate citations
section.

## Link — same bundle

A reference to another document in *this* repo uses a **root-absolute
path**: a target beginning with `/`, interpreted relative to the bundle
root (the repo root).

```markdown
[doc-conventions.md](/standards/doc-conventions.md)
```

A root-absolute link resolves against the reader's *own* checkout root —
the current working directory's repo — so it is **worktree-safe**: it
points at the copy of the file that matches the checkout the reader is
already in, whether that's the main checkout or a per-issue worktree. A
same-repo reference `SHALL NOT` be written as `~/workspace/<this-repo>/…` —
from inside a worktree that absolute path silently jumps to the main
checkout, yielding a different (possibly stale) copy than the one the
reader is working in. `ref-check` enforces this: a same-repo citation in a
fixed-root file fails as `wrong-form`, whether or not the target exists.

The deciding factor is whether the referencing file has a **fixed repo
root** — a single repo it is always read from. Concept documents do, and so
does a repo's own `CLAUDE.md` (Claude Code only loads it when the session
is already inside that repo), so both use the Link form for same-repo
targets. Files with **no fixed repo root** — skills and global `~/.claude/`
config such as `rules/`, loaded across arbitrary repos — have no root for
`/` to resolve against, so they use the Citation form even for a same-repo
target (see [skill-conventions.md — Cross-references](/standards/skill-conventions.md#cross-references)).

## Citation — another repo

A reference to a document in a *different* repo uses its **full workspace
path**, beginning with `~/workspace/`:

```markdown
[SDD standards index](~/workspace/spec-tools/sdd-standards/README.md)
```

A cross-repo citation always resolves to that repo's canonical main
checkout, which is the intended behavior — it references another repo's
published state, not whatever worktree is currently open.
`~/workspace/<repo>` is self-describing: the repo name is in the path, so
no external convention is needed to interpret it.

VS Code does not expand `~/` in markdown links, and it resolves a leading
`/` against the filesystem root rather than the bundle root, so neither
form is clickable from the editor
([vscode#103542](https://github.com/microsoft/vscode/issues/103542)).
Accepted — agents are the primary audience, and both forms are what the
`ref-check` linter (`/tools/bin/ref-check`) validates. Anything else —
backticked filenames like `` `conftest.py` ``, slash-skill invocations like
`/commit` — is treated as prose by `ref-check`.

## Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain
`~/workspace/` paths or `/`-root paths in shell examples or sample output;
`ref-check` skips them. For example:

```bash
# Run ref-check from any workspace repo:
python3 ~/workspace/dev-playbook/tools/bin/ref-check .
```

## Fragment anchors

A cross-reference `MAY` append `#anchor` to target a specific heading in a
markdown file. The anchor `MUST` match the heading's GitHub slug —
`ref-check` computes and validates the slug, so a stale or misspelled
anchor fails the commit.

**Prefer a stable named anchor over a positional one.** A numbered fragment
(`#223-revision`) or an in-prose heading-number citation (`§2.10`,
`§2.2.3`) breaks silently the moment its target is renumbered or
reordered — nothing flags the stale anchor. Where the target heading
carries a stable named slug, cite that. Where the target numbers every
heading positionally and exposes no stable anchor, name the **concept** the
heading carries and drop the number, so a reader finds it by name rather
than by a position that drifts.
