---
type: ADR
title: Same-Repo Resolution — Keep the Written Form, Resolve Reader-Side
description: Resolve intra-repo workspace citations against the reader's own checkout via a reader-side rule, keeping the written path form unchanged
---

# Same-Repo Resolution — Keep the Written Form, Resolve Reader-Side

## Context

Rootless files — skills, global `~/.claude/` rules, and box artifacts — have no
fixed repo root, so they cite even a same-repo document by its full
`~/workspace/<repo>/…` path (the cross-reference grammar mandates this; a
`/`-absolute Link has no root to resolve against). At runtime an agent follows
that literal path into the repo's **main** checkout. Harmless while the bytes
match; wrong the moment a session runs inside an issue worktree whose copy of
the cited file differs from main — every same-repo read silently reaches past
the worktree into stale, pre-change content. It bit hardest in doc review, where
the cited standards *are* the change under review: on issue #145's
doc review the reviewer's first reads returned pre-change content, recovering
only by hand-rewriting paths into the worktree.

The linter was already worktree-correct: `scripts/ref-audit` resolves a same-repo
citation against the *invoking* checkout (`citation_actual()`), so a worktree
validates its own working copy. The correct interpretation existed only inside
the linter — no equivalent rule bound the agent at read time.

## Decision

Keep `~/workspace/<repo>/…` as the sole written form for rootless files, and
define its meaning with a reader-side rule — **same-repo resolution**: a
`~/workspace/<repo>/…` path whose `<repo>` is the repo the session is working in
resolves inside the reader's own checkout (main or worktree); a path into a
different repo resolves as written, to that repo's main checkout. The rule
governs all same-repo file access — reads and writes — not just citation
following.

The normative definition lives in `standards/docs/cross-references.md` under the
stable anchor `#same-repo-resolution`. It is copied verbatim into the global
`dotfiles/dot-claude/CLAUDE.md`, the one carrier an agent reliably holds
mid-flight before it has read any standard; `skill-conventions.md` and the
`edit-in-dev-playbook` rule reference the term rather than restating it. The
escape hatch (a deliberate comparison against published main-checkout state is
legitimate — say so when you do it) lives inside the canonical block, so no
carrier grows its own drifting caveat.

## Alternatives considered

- **Change the written form** (issue #164 branch B) — swap the absolute
  same-repo path for a positionally-safe form and teach `ref-audit` to flag the
  old form for rootless sources too. Rejected: the *same* reference must resolve
  differently by reader position — a globally-loaded skill running in another
  repo's worktree must still resolve a dev-playbook citation to dev-playbook's
  **main** checkout, while the same skill inside a dev-playbook worktree must
  resolve it to that worktree. No static written form encodes reader-relative
  meaning; only a reader-side rule can. This is *the* reason the form is kept.

- **A blocking `PreToolUse` guard** — intercept file access and rewrite or
  reject main-checkout paths from a worktree. Rejected: it breaks the legitimate
  published-state comparison the rule explicitly permits, and it is enforcement
  machinery beyond this prose-scoped change. Revisitable if stale reads recur
  despite the stated rule.

## Consequences

- Two copies of the logic is the floor: the durable standard plus the
  session-injected `CLAUDE.md` copy, annotated `keep in sync`. The runtime
  carrier cannot be a pointer — it must be readable before any standard is
  loaded.
- `ref-audit` and `tests/test_ref_audit.py` are unchanged. The linter already
  implements these semantics at commit time (`citation_actual()` resolves
  in-repo citations against the invoking checkout), so the runtime rule aligns
  the agent *with* the linter rather than changing it — the diff is
  markdown-only, no published-hook change, no rev bump.
