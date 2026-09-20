---
type: General-Sheet
title: Module Design Guide
description: The thinking behind the module-design rules — depth and the deletion test, seams and adapters, ports at a process boundary, and the diagrams and examples that teach them
---

# Module Design Guide

The guide behind
[Module Design Conventions](/standards/modules/design.md), the ruleset
that holds a module to one shape. The ruleset states each rule as a
predicate a reviewer can decide; this guide carries the vocabulary, the
reasoning, the diagrams, and the examples that make the rules
intelligible. Nothing here is enforced; every rule is in the ruleset.

A module is anything with an interface and an implementation. The class
is deliberately scale-agnostic: a function, a class, a package, and a
tier-spanning slice are each a module, judged alike.

A module has exactly one **interface**, the surface it presents to its
callers and to its tests. The interface is everything a caller must know
to use the module correctly: the type signature, and with it the
invariants, the ordering constraints, the error modes, the required
configuration, and the performance characteristics. The
**implementation** is what sits inside the module, its body of code.

## Deep, not shallow

A module's interface is small against the behaviour behind it. An
interface nearly as complex as the implementation it fronts is shallow,
and a shallow module is deepened or combined with its neighbours until
the behaviour outweighs the surface.

**Depth** is leverage at the interface: the amount of behaviour a caller
or a test exercises per unit of interface it has to learn. Depth is a
property of the interface, not of the implementation, and it is measured
against that interface: a deep module is internally composed of small,
swappable parts, and those parts are not part of the interface.

A deep module, a small interface over a large implementation:

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

A shallow module, a large interface over a thin implementation:

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

## The deletion test

The quickest way to tell a deep module from a pass-through: imagine
deleting it. Deleting a deep module pushes its complexity out across its
callers, where it reappears N times. Deleting a pass-through relocates
the same code once, leaving the total complexity unchanged. A module
that fails the deletion test fails
[Deep, not shallow](/standards/modules/design.md#deep-not-shallow); the
test is the heuristic, the rule is the rule.

## Seams and adapters

A **seam** (Michael Feathers) is a place where behaviour is altered
without editing in that place: the location at which a module's
interface lives. Where to put the seam is its own design decision,
separate from what goes behind it. An internal seam is private to the
implementation; the external seam is the interface itself. The workspace
word is *seam*, never *boundary*, which is overloaded with the bounded
context of domain-driven design.

A module has internal seams as well as the external seam at its
interface. A test's use of an internal one is not a reason to lift it
onto the interface
([Internal seams stay inside](/standards/modules/design.md#internal-seams-stay-inside)).

An **adapter** is a concrete thing that satisfies an interface at a
seam. The word names a role, the slot the thing fills, not its
substance: a Postgres repository is a small adapter with a large
implementation, and an in-memory fake is a large adapter with a small
one. *Adapter* is the word when the seam is the topic, *implementation*
otherwise.

One adapter means a hypothetical seam; two mean a real one. A
single-adapter seam is indirection
([Two adapters, or no seam](/standards/modules/design.md#two-adapters-or-no-seam)).

## Dependencies are accepted, not constructed

A module takes each of its dependencies as a parameter and constructs
none of them in its own body
([Dependencies are accepted, not constructed](/standards/modules/design.md#dependencies-are-accepted-not-constructed)).

```typescript
// Accepted
function processOrder(order, paymentGateway) {}

// Constructed
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

## A port at a process boundary

The port is the interface at the seam where a module reaches out of its
own process. The module owns the logic behind it, and the transport, an
HTTP, gRPC, or queue client in production and a third party's library
where the service is theirs, is one adapter satisfying that port. A test
injects an in-memory or mock adapter in its place
([Testing Conventions](/standards/testing/conventions.md)).

The boundary is the process. A dependency the module reaches inside its
own process, pure computation, in-memory state, or a store with a local
test stand-in such as PGLite for Postgres, is served by an internal seam
and needs no port at the interface
([A port at a process boundary](/standards/modules/design.md#a-port-at-a-process-boundary)).

## The interface is the test surface

Callers and tests cross the same seam. A behaviour reachable only past
the interface means the module is the wrong shape, and the interface is
redrawn until the behaviour is reachable
([The interface is the test surface](/standards/modules/design.md#the-interface-is-the-test-surface)).

## Results are returned, not written

A module that computes a value returns it rather than mutating the
caller's argument
([Results are returned, not written](/standards/modules/design.md#results-are-returned-not-written)).

```typescript
// Returned
function calculateDiscount(cart): Discount {}

// Written into the caller's argument
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

The rule reaches the caller's argument alone. A module that writes a
file, sends a message, or stores a record is doing its work, and the
port at a process boundary governs how it reaches across the process
boundary to do so.
