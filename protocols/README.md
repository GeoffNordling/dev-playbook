---
type: README
title: Protocols
description: Formal human–agent collaboration protocols — problem-decomposition algorithms and the skills that operationalize them
---

# Protocols

We find it useful to approach complex problems by first decomposing them formally: name the primitives, define their relationships, and impose algorithmic structure. This organizes the mind, exposes gaps, and supports consistent implementation.

In that spirit, this playbook defines a **protocol** as an augmented skill with two components:
- **Formulation** (`formulation.md`). A pseudo-mathematical algorithm that lets us step back from the particulars of a project and reason about the workflow itself. When we are always zoomed in — this codebase, this bug, this spec — we optimize locally but never examine the system we are operating within. The formulation gives us a general, abstract vocabulary for that system: objects we can name, relationships we can question, constraints we can tighten or relax. It uses the skeleton of a formal framework, but is pre-rigorous. The objects are not precise enough to support proofs. The notation imposes discipline on our thinking without claiming rigor it does not have.
- **Skill** (`SKILL.md`). A faithful, plain-language translation of the algorithm that an agent executes directly. We have a strong prior belief (not tested) that invoking the formulation directly would degrade the executing agent's performance by diverting attention from the task to the notation. This translation may also emphasize specific operational details that do not naturally fit within the formal specification. Align, Map, Execute's skill is [protocol-align-map-execute](/dotfiles/dot-claude/skills/protocol-align-map-execute/SKILL.md).

A protocol's formulation lives under `protocols/`; its skill lives in the dotfiles skills tree that Stow links into `~/.claude/`, which is where Claude Code discovers it.

Protocols are written to be **frontier-invariant**. The capabilities of AI models advance rapidly — what an agent cannot do reliably today it may do well tomorrow. A protocol that encodes assumptions about current capability becomes obsolete with each advance. Instead, protocols define relationships between abstract objects (scope, capability, step size) and let the operational parameters adjust as the frontier moves. The algorithm is general; the specifics of each application may change.

The protocols are listed in [`index.md`](/protocols/index.md).

## Field notes

### V0: structure reduces variance

After completing v0 of Align, Map, Execute, we questioned whether the
protocol describes anything beyond a well-run Claude Code session. The
core loop — align on intent, search the space, present a summary, human
directs, agent acts — is what a competent user already does intuitively.

The value is not in prescribing new behavior. It is in naming and
structuring the objects. When the workflow is implicit, every session
produces a bespoke, unrepeatable interaction. The agent gives whatever
summary feels natural; the human steers by instinct. This works, but
the variance is high. There is no artifact to evaluate, no structure to
improve, and no vocabulary for discussing what went wrong.

Naming the objects and defining their relationships makes the workflow
**improvable**. After a session, a meta-agent can evaluate specific
objects — "Was $M$ faithful? Was $\sigma$ appropriate? Did $A$ drift?"
— rather than answering the vague question "how could this conversation
be better?" Over time, this produces supervised examples of how to
improve each component.

Structure reduces variance. That is the contribution.

### V1: facets and the map's matrix structure

The first execution of Align, Map, Execute revealed that the agent
could not construct a useful map. The instruction said the map should be
"organized according to the alignment" — the agent interpreted this
freely and produced random artifacts that did not meet $H$ (defined as
human intent when writing this algorithm!).

The fix was to introduce $F$ (facets) as a separate primitive and define
$M$ as a matrix: $F$ defines the columns, regions from surveying $S$
define the rows. This makes the Phase 1 → Phase 2 handoff mechanical:
Phase 1 produces the operating model ($A$), the human provides the
evaluation dimensions ($F$), and Phase 2 applies $F$ to $S$ to fill in
the cells.
