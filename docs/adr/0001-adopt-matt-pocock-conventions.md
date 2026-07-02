---
type: ADR
title: Adopt Matt Pocock's Conventions
description: Adopt Matt Pocock's repository conventions wholesale — 4-digit ADRs, per-repo agent config, triage vocabulary, vertical-slice discipline — rejecting only his PRD format
---

# Adopt Matt Pocock's Conventions

**Status:** Superseded by [ADR-0004](0004-remove-pocock-direct-dependency.md) in part

## Context

Matt Pocock published a public agent-skills repository
([github.com/mattpocock/skills](https://github.com/mattpocock/skills))
that bundles a small set of repo conventions: a `docs/adr/` directory
with 4-digit numbering, a `docs/agents/` directory describing the
issue tracker / triage labels / domain doc layout, an `## Agent skills`
block in `CLAUDE.md`, a `CONTEXT.md` glossary at the repo root, an
offer-criteria gate for ADRs (hard-to-reverse + surprising + real
trade-off), a triage state machine with a five-label vocabulary, a
PRD format, and a vertical-slice issue breakdown. Several of his
engineering skills (`tdd`, `to-issues`, `triage`, `grill-with-docs`,
`improve-codebase-architecture`, `zoom-out`, `to-prd`) read directly
from these per-repo files; running them without the conventions
configured produces degraded output.

Before this ADR, dev-playbook had its own subset of these conventions
(an existing `docs/adr/` with 3-digit numbering, an authoritative
testing standard, a cross-reference linter) but no formal issue
management standard, no triage vocabulary, no domain doc layout, and
no PRD or SDD-spec equivalent at the project level beyond ad-hoc
GitHub Issues.

## Decision

**Adopt Matt Pocock's conventions wholesale**, with one rejection and
one adaptation.

### Adopt

- `docs/adr/` with 4-digit numbering, ADR template, and the
  offer-criteria gate (hard-to-reverse + surprising + real trade-off).
  Existing ADRs `001`–`005` renamed to `0001`–`0005`.
- `docs/agents/{issue-tracker,triage-labels,domain}.md` per-repo
  configuration files, scaffolded by `setup-matt-pocock-skills`.
- `## Agent skills` block in `CLAUDE.md` pointing at the above.
- `CONTEXT.md` glossary at the repo root, lazily created by
  `/grill-with-docs` on first ambiguity (not backfilled upfront).
- Triage label vocabulary (`needs-triage`, `needs-info`,
  `ready-for-agent`, `ready-for-human`, `wontfix`) plus the two
  category labels.
- Vertical-slice issue breakdown (tracer bullets, HITL/AFK markers,
  blocked-by chains).
- Architecture vocabulary used in `improve-codebase-architecture`
  (Module / Interface / Depth / Seam / Adapter / Leverage / Locality)
  — adopted implicitly through use of the skill, no standards change
  required.

The vocabulary and slice rules live in the new
[Issue management standard](~/workspace/dev-playbook/standards/workflow.md).
The ADR rules live in the updated
[Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md).

### Reject

**The PRD format and `/to-prd` workflow.** Matt's PRD layer overlaps
with this workspace's spec-driven-development layer
([sdd-standards/](~/workspace/spec-tools/sdd-standards/)). They
cover the same ground — what to build and why, before code exists —
with incompatible primitives (PRDs are prose; SDD specs are
EARS-templated requirements with OFT traceability and machine-verified
test coverage). Running both produces two sources of authority for
the same decisions.

We keep SDD because conventional spec-driven workflows that ship in
public frameworks (Spec Kit, Kiro, OpenSpec, plus Matt's PRD) treat
specs as input prose that drift from code once implementation starts.
We expect that approach to fail in practice with current-state coding
agents, which is why this workspace's SDD extension adds machine-
verified traceability, red/green agent isolation, and engineer-
provided structural commitments at the design layer. The bet is that
the extension makes SDD effective where the conventional form does
not. Adopting Matt's PRD on top of SDD would dilute that bet without
adding capability we lack.

`/to-prd` is therefore not installed. The remaining 8 adopted skills
(`tdd`, `caveman`, `grill-me`, `grill-with-docs`,
`improve-codebase-architecture`, `zoom-out`, `to-issues`, `triage`)
are installed normally.

### Adapt

**GitHub-only issue tracker backend.** `setup-matt-pocock-skills`
offers GitHub, GitLab, local-markdown (`.scratch/`), or "other" as
issue-tracker backends. We configure GitHub only and drop the other
options to keep the standard simple. Local-markdown or the other
backends can be added later if a concrete need surfaces.

## Why adopt

This repository is software, in words. The same standards apply:
machine-checkable structure, low-friction tooling, conventions that
hold up under repeated use. Matt's conventions clear that bar — they
are concrete, internally consistent, and used by a working set of
skills. Adoption was decided immediately on first read.

The "don't run in degraded mode" rule follows from the same standard.
Running engineering skills without the per-repo files they expect
produces lower-quality output than running them with the files in
place. We adopt the conventions the skills assume, not just the
skills themselves.

## Alternatives considered

| Alternative | Why not |
|---|---|
| Adopt Matt's skills but not his conventions (run in degraded mode) | Skills produce noticeably worse output without the per-repo config they read from. |
| Adopt the PRD layer alongside SDD | Two sources of authority for the same pre-implementation decisions; dilutes the SDD-extension bet. |
| Fork Matt's skills to swap PRD for SDD | The only adaptation needed (GitHub-only) is supported by `setup-matt-pocock-skills` as a built-in choice. Fork only if specific friction surfaces post-install. |
| Configure `.scratch/` or "other" issue-tracker backends now | We use GitHub. Add later if a real need appears. |

## Consequences

- Existing ADRs `001-005` renamed to `0001-0005` to match Matt's
  4-digit convention. The single cross-reference in
  `sdd-standards/README.md` and the inline links between ADRs were
  updated.
- New repo files: `docs/agents/issue-tracker.md`,
  `docs/agents/triage-labels.md`, `docs/agents/domain.md`. Generated
  via `setup-matt-pocock-skills`. The `issue-tracker.md` seed's
  reference to PRDs was removed.
- New `## Agent skills` block in `CLAUDE.md`.
- New
  [Issue management standard](~/workspace/dev-playbook/standards/workflow.md)
  documenting the triage state machine, label vocabulary, and
  vertical-slice rules.
- The [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
  amended with the 4-digit ADR rule and offer-criteria gate.
- The [Testing conventions standard](~/workspace/dev-playbook/standards/testing-conventions.md)
  cross-references Matt's `/tdd` while remaining authoritative — we
  do not fork `/tdd`.
- `/to-prd` is not installed and is not authorised for use in this
  workspace.
- The cookiecutter project template (`project-template/`) must propagate
  these conventions so newly-generated repos start in compliance. Tracked
  separately in GeoffNordling/spec-tools#1.
- The SDD-extension bet remains testable. If the extension fails to
  make SDD effective with current-state coding agents in real use,
  this ADR's PRD rejection should be revisited.

## Addendum — 2026-05-19

The original `/to-prd` rejection (lines 60–80, 136) framed the concern as "two sources of authority for the same pre-implementation decisions." A 2026-05-19 re-audit of the upstream skill ([mattpocock/skills `engineering/to-prd`](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-prd/SKILL.md)) surfaced three concrete frictions beyond the original framing, which should anchor any future revisit:

1. **Convention mismatch with post-ADR-0004 canon.** The skill's Process section depends on `/setup-matt-pocock-skills` (dropped in [ADR-0004](0004-remove-pocock-direct-dependency.md)) and applies a `ready-for-agent` triage label not present in the workspace's `phase/*` scheme (canonicalized in [workflow.md](~/workspace/dev-playbook/standards/workflow.md) and enforced by `bootstrap-labels`).
2. **Slot collision with `/intake`.** Both `/to-prd` and the workspace's `/intake` skill want to be the "context → tracked work item" step. Adopting `/to-prd` would force a choice of which workflow is canonical for new work.
3. **The "ephemeral PRD" lifecycle is not enforced by the skill.** Publishing the PRD as a GitHub issue creates a persistent artifact; the discipline of closing or archiving it once `feat`/`req` items exist is not in the skill and would erode under deadline pressure. The PRD template's *Implementation Decisions* and *Testing Decisions* sections in particular overlap `dsn` items and `Needs: utest/itest` markers — encoding those decisions in prose first means `/sdd-design` becomes downstream paperwork rather than the source of truth.

The revisit clause above stands. These three frictions are the specific things any future revisit must address before reversing the rejection.
