---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly; currently the module-architecture set (Module, Interface, Depth, Seam, Adapter, Leverage, Locality)
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent instead of each doc reinventing it. Extensible: terms are added here as they're pinned down. The current terms cover module architecture; use them exactly — don't substitute "component," "service," "API," or "boundary." Consistent language is the whole point.

## Language

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

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Example dialogue

> **Dev:** "I want to swap the Postgres store for an in-memory fake in tests. Is the fake a new **Module**?"
> **Reviewer:** "No — the store is one **Module** with one **Interface**. The fake is another **Adapter** at the same **Seam**: you're altering behavior at a place you don't edit."
> **Dev:** "So the **Seam** is the store's **Interface**?"
> **Reviewer:** "The **Seam** is *where* that **Interface** lives — the call site you can redirect — not the **Interface** itself. Keep the **Interface** small and the **Module** stays **deep**: one small surface, a lot of behavior behind it."
> **Dev:** "And that depth is worth it because…?"
> **Reviewer:** "It's the same **Depth** paying out twice — **Leverage** for the callers (the fake pays back across every test) and **Locality** for us (a store bug is fixed in one **Implementation**, not chased across call sites)."

## Flagged ambiguities

- "boundary" was used for both the location of an interface and the interface itself — resolved: say **Seam** for the location, **Interface** for the surface. "boundary" is retired (collides with DDD's bounded context).
- "component" / "service" / "unit" all floated as names for the same thing — resolved: **Module** is the single scale-agnostic term; the others are aliases to avoid.
- "depth" was read two ways — the implementation-to-interface line ratio (Ousterhout) vs. leverage at the interface — resolved: **Depth** here means leverage (see Rejected framings).
- "interface" was narrowed to the type signature or a class's public methods — resolved: **Interface** includes every fact a caller must know (invariants, ordering, error modes, config), not just the signature.

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.
