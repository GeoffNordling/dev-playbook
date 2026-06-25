# Harvest Pocock's `prototype` and `handoff` Skills

## Context

Matt Pocock published two skills after [ADR-0004](0004-remove-pocock-direct-dependency.md): `engineering/prototype` and `productivity/handoff`. The Pocock entry in [third-party-survey.md](~/workspace/dev-playbook/docs/third-party-survey.md) directs new skills through the [ADR-0003](0003-decline-superpowers.md) rule — adopt only when conventions integrate cleanly, otherwise harvest the technique into an authored skill. Both were evaluated against that rule.

## Decision

**Harvest both into authored skill bundles; install neither as a direct dependency.** Neither fit cleanly verbatim, and both needed adaptation, so the rule points to authoring.

- **`prototype`** → `dotfiles/dot-claude/skills/prototype/` (router plus `references/logic.md` and `references/presentation.md`). Made engine-agnostic — a prototype may be driven by hand or by an autonomous loop. Prototype location is decided *with* the human rather than guessed, defaulting to a top-level `prototypes/<name>/` off the import path. The presentation branch is generalized past Pocock's React-specific UI branch (web / notebook / CLI). The answer is captured to workspace artifacts (commit, ADR, issue, or `NOTES.md`).
- **`handoff`** → `dotfiles/dot-claude/skills/handoff/`. Near-verbatim, adapted to workspace skill front matter; "PRDs" swapped for "specs"; an explicit read-side added (report the temp path plus a paste-ready resume line) since Pocock's skill is write-only. Fills the open/unstructured-session handoff case the SDD issue/worktree flow does not cover.

`/zoom-out` and `/caveman` remain direct Vercel deps because they need zero adaptation; these two needed adaptation, so they are authored instead.

## Considered Options

| Alternative | Why rejected |
|---|---|
| Adopt both as direct Vercel dependencies | Semantic drift on update, and neither fit verbatim — `prototype` carried an execution-model assumption, a React-only UI branch, and a location convention to set; `handoff` referenced a rejected artifact (PRDs) and had no read-side. |
| Decline both | Each fills a real gap the canon lacks: pre-spec design exploration, and handoff for open/unstructured sessions. |

## Consequences

- Two authored bundles added under `dotfiles/dot-claude/skills/`; nothing added to `.agents/.skill-lock.json`.
- `prototype`'s location convention currently also appears in `docs/ralph-loop-prototyping-plan.md`; lifting it out of that doc is a tracked follow-up, and its authoritative home (the skill vs. a row in the [repo-documentation](~/workspace/dev-playbook/standards/repo-documentation.md) Files table) is still open.
- `handoff` discovery relies on the human relaying the temp path; a deterministic-path plus `/resume` convention is a deferred option if the relay proves annoying.
- Third re-application of the [ADR-0003](0003-decline-superpowers.md) rule (after Pocock in ADR-0004).

## Update (2026-06-25)

The Consequences above reference `docs/ralph-loop-prototyping-plan.md`. That file no longer exists — the follow-up to lift `prototype`'s location convention out of it is resolved by the doc's deletion. The reference is left in place for historical record; this note exists so future agents stop flagging it as a broken link.
