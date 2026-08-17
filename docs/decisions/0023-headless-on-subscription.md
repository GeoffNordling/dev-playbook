---
type: Decision-Record
title: Begin Using claude -p
status: accepted
description: Adopt headless claude -p, on the expectation that subscription billing for it holds long-term
date: 2026-08-17
---

# Begin Using claude -p

The workspace had recorded that Anthropic confines subscription billing to
attended sessions, which ruled headless out before it was ever weighed. The
claim was never true. **The workspace begins using `claude -p`, on the
expectation that subscription billing for it holds long-term.** Anthropic
withdrew that coverage once and restored it, and the support article states it
plainly; [headless.md](/docs/headless.md) carries the evidence and tracks where
the policy stands. Direct API and Agent SDK use remains out of scope on cost,
unchanged by this record.

## Consequences

**A configured API key silently outranks the subscription login**, and
Anthropic documents that in non-interactive mode the key is always used when
present. That moves the workspace to per-token billing with no warning, so
[`headless-probe`](/scripts/headless-probe) guards twelve credential sources
before any call and aborts on one finding.

**Path-scoped permission rules do not take effect headless** — not as allow
rules, not as deny rules, not from CLI flags and not from a settings file, and
the failure is silent. So the write fence an attended session gets from
`EnterWorktree` has no configuration substitute, and the container in
[sandboxing.md](/docs/sandboxing.md) is the only fence left for work with no
user attached.
