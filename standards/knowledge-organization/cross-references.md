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
[prose/conventions.md](/standards/prose/conventions.md)
```

A root-absolute link resolves against the reader's *own* checkout root —
the current working directory's repo — so it points at the copy of the
file that matches the checkout the reader is already in, whether that's
the main checkout or a per-issue worktree. A same-repo reference
`SHALL NOT` be written as `~/workspace/<this-repo>/…` — from inside a
worktree that absolute path silently jumps to the main checkout, yielding
a different (possibly stale) copy than the one the reader is working in.
`ref-lint` enforces this: a same-repo citation in a fixed-root file fails
as `wrong-form`, whether or not the target exists.

The deciding factor is whether the referencing file has a **fixed repo
root** — a single repo it is always read from. Concept documents do, and so
does a repo's own `CLAUDE.md` (Claude Code only loads it when the session
is already inside that repo), so both use the Link form for same-repo
targets. Files with **no fixed repo root** — skills and global `~/.claude/`
config such as `rules/` and `agents/`, loaded across arbitrary repos — have
no root for `/` to resolve against, so they use the Citation form even for a
same-repo target (see [skill-conventions.md — Cross-references](/standards/harness/skill-conventions.md#cross-references)).
That same-repo Citation resolves per
[Same-repo resolution](/standards/knowledge-organization/cross-references.md#same-repo-resolution)
below, against the reader's own checkout.

## Citation — another repo

A reference to a document in a *different* repo uses its **full workspace
path**, beginning with `~/workspace/`:

```markdown
[Friction log](~/workspace/mission-control/friction/log.md)
```

A cross-repo citation always resolves to that repo's canonical main
checkout — it references another repo's published state.
`~/workspace/<repo>` is self-describing: the repo name is in the path, so
no external convention is needed to interpret it.

VS Code does not expand `~/` in markdown links, and it resolves a leading
`/` against the filesystem root rather than the bundle root, so neither
form is clickable from the editor
([vscode#103542](https://github.com/microsoft/vscode/issues/103542)).
Accepted — agents are the primary audience, and both forms are what the
`ref-lint` linter (`/scripts/ref-lint`) validates. Anything else —
backticked filenames like `` `conftest.py` ``, slash-skill invocations like
`/commit` — is treated as prose by `ref-lint`.

## Same-repo resolution

The definition below is the **canonical wording**, pinned and reused
byte-for-byte by the session-level carriers (`dotfiles/dot-claude/CLAUDE.md`
and the `edit-in-dev-playbook` rule) that an agent holds before it has read
any standard. It is deliberately in the agent-facing second person —
reproduced here verbatim rather than paraphrased to this Standard's
declarative third person — so the copies stay identical.

**Same-repo resolution:** a `~/workspace/<repo>/…` path whose `<repo>` is the repo your session is working in — its main checkout or any of its worktrees — resolves inside your own checkout: substitute your checkout root for `~/workspace/<repo>/`. A path into a different repo resolves as written, to that repo's main checkout. Touching your repo's main checkout from a worktree is legitimate only as a deliberate comparison against published state — say so when you do it.

The written form is kept because no static path can encode this: the same
`~/workspace/<repo>/…` citation must resolve to a different checkout
depending on where the reader stands — a globally-loaded skill resolves a
dev-playbook citation to dev-playbook's main checkout from another repo's
worktree, but to the worktree when run inside a dev-playbook worktree — so
the meaning has to be a reader-side rule. `ref-lint` already resolves
same-repo citations this way, against the invoking checkout, so this rule
states at read time what the linter has enforced at commit time all along;
the [same-repo-resolution Decision Record](/docs/decisions/0009-same-repo-resolution.md)
records why the alternatives were rejected.

## Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain
`~/workspace/` paths or `/`-root paths in shell examples or sample output;
`ref-lint` skips them. For example:

```bash
# Run ref-lint from any workspace repo:
~/workspace/dev-playbook/scripts/ref-lint .
```

## Fragment anchors

A cross-reference `MAY` append `#anchor` to target a specific heading in a
markdown file. The anchor `MUST` match the heading's GitHub slug —
`ref-lint` computes and validates the slug, so a stale or misspelled
anchor fails the commit.

**Prefer a stable named anchor over a positional one.** A numbered fragment
(`#223-revision`) or an in-prose heading-number citation (`§2.10`,
`§2.2.3`) breaks silently the moment its target is renumbered or
reordered — nothing flags the stale anchor. Where the target heading
carries a stable named slug, cite that. Where the target numbers every
heading positionally and exposes no stable anchor, name the **concept** the
heading carries and drop the number, so a reader finds it by name rather
than by a position that drifts.
