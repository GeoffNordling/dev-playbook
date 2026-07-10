---
type: Vocabulary
title: dev-playbook Vocabulary
description: The repo's vocabulary disambiguation center — the architecture terms and the governance terms (Audit, Detector, Gate, Enforcement, Finding), used exactly
---

# dev-playbook Vocabulary

The repo's vocabulary disambiguation center. When several words compete for
one concept, this file picks one and lists the rest as aliases to avoid —
consistent language is the whole point. Two clusters live here today: the
**architecture** vocabulary used in every suggestion about module design, and
the **governance** vocabulary that names how standards are checked and
blocked.

## Language

### Architecture

Shared vocabulary for every suggestion about module architecture. Use these
terms exactly — don't substitute "component," "service," "API," or
"boundary."

**Module**
Anything with an interface and an implementation. Deliberately scale-agnostic — applies equally to a function, class, package, or tier-spanning slice.
_Avoid_: unit, component, service.

**Interface**
Everything a caller must know to use the module correctly. Includes the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics.
_Avoid_: API, signature (too narrow — those refer only to the type-level surface).

**Implementation**
What's inside a module — its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth**
Leverage at the interface — the amount of behavior a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behavior sits behind a small interface. A module is **shallow** when the interface is nearly as complex as the implementation.

**Seam** _(from Michael Feathers)_
A place where you can alter behavior without editing in that place. The *location* at which a module's interface lives. Choosing where to put the seam is its own design decision, distinct from what goes behind it.
_Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter**
A concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what's inside).

**Leverage**
What callers get from depth. More capability per unit of interface they have to learn. One implementation pays back across N call sites and M tests.

**Locality**
What maintainers get from depth. Change, bugs, knowledge, and verification concentrate at one place rather than spreading across callers. Fix once, fixed everywhere.

### Governance

How a standard is checked against the repository and where nonconformance is
blocked. The gate rungs are defined once in
[enforcement.md](/standards/build/enforcement.md); this fixes the words.

**Audit**
A run of one or more detectors; read-only — it never mutates the repository and never blocks by itself.
_Avoid_: check (too broad — a check may block; an audit never does).

**Detector**
The read-only script that inspects the repository against one standard and emits findings; it never mutates the repository. One detector per card is the north star.

**Gate**
An automatic, unmanned blocking point on the path to main. There are exactly three, with fixed rung names: **commit gate** (the pre-commit suite), **push gate** (`make check`, via the pre-push stage), **CI gate** (thin CI).
_Avoid_: venue (retired — say **gate**, or a rung name).

**Enforcement**
An audit stationed at a gate — the audit's findings block the path to main there. Enforcement is automatic and continuously in effect; a one-time human code review is not enforcement.

**Finding**
One output line from a detector, in GNU format: `file:line: card.rule message` — a colon after the location, single spaces, a repo-relative path. The `:line` is omitted for a file-level finding (e.g. `README.md: docs.readme-missing …`). The rule id is namespaced by the card whose question it answers.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.
- A **Detector** inspects the repository against one standard and emits **Findings**; an **Audit** is a run of one or more **Detectors**; stationed at a **Gate**, that audit becomes **Enforcement**.
- There are exactly three **Gates** on the path to main: commit gate, push gate, CI gate.

## Example dialogue

> **Dev:** "I want to swap the Postgres store for an in-memory fake in tests. Is the fake a new **Module**?"
> **Reviewer:** "No — the store is one **Module** with one **Interface**. The fake is another **Adapter** at the same **Seam**: you're altering behavior at a place you don't edit."
> **Dev:** "So the **Seam** is the store's **Interface**?"
> **Reviewer:** "The **Seam** is *where* that **Interface** lives — the call site you can redirect — not the **Interface** itself. Keep the **Interface** small and the **Module** stays **deep**: one small surface, a lot of behavior behind it."
> **Dev:** "And that depth is worth it because…?"
> **Reviewer:** "It's the same **Depth** paying out twice — **Leverage** for the callers (the fake pays back across every test) and **Locality** for us (a store bug is fixed in one **Implementation**, not chased across call sites)."

> **Dev:** "repo-audit reported a **Finding**. Does that block my commit?"
> **Reviewer:** "Only because it runs at the **commit gate**. The audit itself is read-only — it just emits **Findings**. It's the **Gate** it's stationed at that blocks; run by hand, it isn't **Enforcement** at all."

## Flagged ambiguities

- "boundary" was used for both the location of an interface and the interface itself — resolved: say **Seam** for the location, **Interface** for the surface. "boundary" is retired (collides with DDD's bounded context).
- "component" / "service" / "unit" all floated as names for the same thing — resolved: **Module** is the single scale-agnostic term; the others are aliases to avoid.
- "depth" was read two ways — the implementation-to-interface line ratio (Ousterhout) vs. leverage at the interface — resolved: **Depth** here means leverage (see Rejected framings).
- "interface" was narrowed to the type signature or a class's public methods — resolved: **Interface** includes every fact a caller must know (invariants, ordering, error modes, config), not just the signature.
- "venue" was used informally for a blocking point — resolved: say **Gate**, or one of the three rung names (commit gate, push gate, CI gate). "venue" is retired.
- "check" and "audit" were blurred — resolved: an **Audit** is read-only and never blocks; a **Gate** is what blocks. A check that blocks is a gate; a check that only reports is an audit.
- "audit" and "detector" were blurred — the same read-only, gate-stationed role was defined with near-identical language in two files — resolved: a **Detector** is the script; an **Audit** is a run of one or more detectors.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.
