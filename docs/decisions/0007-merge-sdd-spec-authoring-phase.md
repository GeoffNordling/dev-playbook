---
type: Decision Record
title: Merge SDD Spec Authoring into One Phase
description: Merge sdd-requirements and sdd-design into a single sdd-specs phase authoring the whole feat/req/dsn hierarchy in one interview
---

# Merge SDD Spec Authoring into One Phase

## Context

The SDD path split spec authoring into two sequential HITL nodes: `sdd_requirements` authored the `feat`/`req` layer, then handed off to `sdd_design`, which authored the `dsn` layer. Each was its own worktree commit, its own `phase:*` label, and — critically — its own locked scope: requirements owned `feat`/`req` and was told to leave `dsn` alone; design owned `dsn`. [Decision Record 0005](0005-issue-workflow-reorganization.md) kept the two parallel and explicitly retained the `sdd-requirements` name "parallel to `sdd-design`."

Real use showed the dividing line is artificial. `feat`, `req`, and `dsn` are one interdependent hierarchy, not two phases, and the hard handoff between them produced three frictions:

**Interdependence severed.** A sharper name or shape discovered at the `req` level wants to cascade to the `dsn` that covers it — but `dsn` was out of the requirements node's scope, so the agent froze rather than make the obviously-correct paired edit.

**Revision cascade has no atomic home.** A `feat`/`req` revision bump breaks every revision-pinned `Covers:`/`Depends:` reference to the prior revision; the dependent `dsn` must catch up *in the same commit*, because "no dangling reference" is a construction-time **consistency** rule (a breach raises — see spec-tools ADR-0007) and is never WIP-exempt. The scope-locked handoff forbade the requirements node from touching `dsn`, so no single node could produce a green, standard-compliant commit when a revision bumped. The only escapes were a red tree or editing the `req` in place against the standard's `SHALL`-bump rule.

**Authoring was the lone split.** Review is already joint — `sdd_agent_spec_review` reviews the `feat`/`req`/`dsn` items as one artifact. Authoring was the one place that pretended the layers were separable.

## Decision

Merge `sdd_requirements` and `sdd_design` into a single HITL node, **`sdd_specs`** (`/sdd-specs`, `phase:sdd-specs`), that authors the whole `feat`/`req`/`dsn` hierarchy in one interview, one worktree session, one green commit, then hands off to `sdd_agent_spec_review`.

What merges is the *phase*; what stays is the *altitude*. A `req` still says what holds, a `dsn` still says how — the skill holds that distinction explicitly. What goes is the committed, scope-locked boundary in the middle of one continuous act of design. The author moves between levels freely and cascades a change across them in a single pass, with the user's agreement.

- **Name.** `sdd_specs` (plural), not `sdd_design` — the latter would misread as design-only when the node owns the entire spec.
- **Skill.** The merged `sdd-specs` skill keeps the seven-section interview skeleton both predecessors shared, fuses each section's content (requirements' behavior areas with design's data/API/module areas; one plan-synthesis hierarchy; one drafting pass; one review rubric), sets `WIP: true` on each `feat` once, runs `make check` once, and advances the label to `sdd_agent_spec_review`.
- **Labels.** `bootstrap-labels` retires `phase:sdd-requirements` and `phase:sdd-design`, mints `phase:sdd-specs`.

This resolves the first and third frictions outright and the second for the `feat`↔`req`↔`dsn` layer — the cascade is now intra-node and atomic. A revision bump that breaks a *committed verifier* marker (`@pytest.mark.covers("dsn~…~0")`) still crosses the `sdd_specs`→`sdd_tdd` boundary, since verifiers are deliberately authored downstream; that residual seam is moot for greenfield work and is tracked as a separate spec-tools issue, not addressed here.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep the split; relax the scope lock so `sdd_requirements` may edit `dsn` references | Still two commits, two label flips, two cold agent contexts for one act of design. The cascade still spans the boundary; the freeze just moves. Merging removes the boundary rather than patching it. |
| One mega-skill running every SDD phase (spec → tdd → review) in sequence | Rejected for the reason Decision Record 0005 rejected `/intake-then-build`: each phase is a distinct interaction mode and benefits from a fresh agent context. Spec authoring is *one* mode (the interview), so merging only the two authoring phases keeps that property; folding in TDD or review would not. |
| Leave the workflow; make the validator tolerate a stale cross-layer revision | A real option, but a spec-standard/model change in spec-tools, orthogonal to the workflow's shape — and it addresses only the second friction, not the severed interdependence or the review asymmetry. Pursue on its own track. |

## Consequences

- Two skills removed (`sdd-requirements`, `sdd-design`); one added (`sdd-specs`).
- `workflow.md`: the two SDD authoring nodes collapse to one in the graph; the `(human, work)` example and the skills table fold to a single `/sdd-specs` row (HITL; escalates only on a stale base).
- `bootstrap-labels`: two phase labels retired, one added. Re-run per repo to mint `phase:sdd-specs`; the retired labels linger until deleted by hand (the script only adds, on this path).
- Any in-flight issue sitting at `phase:sdd-requirements` or `phase:sdd-design` needs a one-time relabel to `phase:sdd-specs`.
- `intake`'s `mode:sdd` entry and `sdd-tdd`'s spec-amendment escape hatch retarget to `sdd-specs`.
- Supersedes Decision Record 0005's "`sdd-requirements` keeps its name — parallel to `sdd-design`": the parallel split it preserved is what this removes.
- The `sdd_specs`→`sdd_tdd` revision-cascade seam (stale verifier markers) is tracked as a separate spec-tools issue.
