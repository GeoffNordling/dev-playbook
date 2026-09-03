---
type: Standard
title: Module Design Conventions
description: The deep-module contract — depth, the deletion test, the seam rules, and the port at a process boundary
population: "a module in a governed repo's source: anything with an interface and an implementation"
---

# Module Design Conventions

A module in a governed repo's source: anything with an interface and an
implementation. The class is deliberately scale-agnostic, and a function, a
class, a package, and a tier-spanning slice are each a member, bound alike.

A module has exactly one **interface**, the surface it presents to its callers
and to its tests. The interface is everything a caller must know to use the
module correctly: the type signature, and with it the invariants, the ordering
constraints, the error modes, the required configuration, and the performance
characteristics. The **implementation** is what sits inside the module, its
body of code.

The rules hold a module to one shape, deep: a large amount of behaviour behind
a small interface, reachable through that interface. The tests that cross a
module's interface are
[Testing Conventions](/standards/testing/conventions.md).

## Deep, not shallow

A module's interface is small against the behaviour behind it. An interface
nearly as complex as the implementation it fronts is shallow, and a shallow
module is deepened or combined with its neighbours until the behaviour
outweighs the surface.

**Depth** is leverage at the interface: the amount of behaviour a caller or a
test exercises per unit of interface it has to learn. Depth is a property of
the interface, not of the implementation, and it is measured against that
interface: a deep module is internally composed of small, swappable parts, and
those parts are not part of the interface.

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

Deleting a module pushes its complexity out across its callers, where it
reappears N times. A module whose deletion relocates the same code once,
leaving the total complexity unchanged, is a pass-through.

## Internal seams stay inside

A module's interface exposes no seam that exists only for the module's own
tests. A module has internal seams as well as the external seam at its
interface, and a test's use of an internal one is not a reason to lift it onto
the interface.

A **seam** (Michael Feathers) is a place where behaviour is altered without
editing in that place: the location at which a module's interface lives. Where
to put the seam is its own design decision, separate from what goes behind it.
An internal seam is private to the implementation; the external seam is the
interface itself. The workspace word is *seam*, never *boundary*, which is
overloaded with the bounded context of domain-driven design.

## Two adapters, or no seam

A seam a module presents carries at least two adapters, typically one for
production and one for tests. One adapter means a hypothetical seam; two mean
a real one. A single-adapter seam is indirection.

An **adapter** is a concrete thing that satisfies an interface at a seam. The
word names a role, the slot the thing fills, not its substance: a Postgres
repository is a small adapter with a large implementation, and an in-memory
fake is a large adapter with a small one. *Adapter* is the word when the seam
is the topic, *implementation* otherwise.

## Dependencies are accepted, not constructed

A module takes each of its dependencies as a parameter and constructs none of
them in its own body.

```typescript
// Accepted
function processOrder(order, paymentGateway) {}

// Constructed
function processOrder(order) {
  const gateway = new StripeGateway();
}
```

## A port at a process boundary

A dependency a module reaches across a process boundary, a service the
workspace owns or a third party it does not control, sits behind a **port** at
the module's own interface, and the transport is an injected adapter.

The port is the interface at the seam. The module owns the logic behind it,
and the transport, an HTTP, gRPC, or queue client in production and a third
party's library where the service is theirs, is one adapter satisfying that
port. A test injects an in-memory or mock adapter in its place
([Testing Conventions](/standards/testing/conventions.md)).

The boundary is the process. A dependency the module reaches inside its own
process, pure computation, in-memory state, or a store with a local test
stand-in such as PGLite for Postgres, is served by an internal seam and needs
no port at the interface.

## The interface is the test surface

Every behaviour of a module is reachable through its interface. Callers and
tests cross the same seam, so a behaviour reachable only past the interface
means the module is the wrong shape, and the interface is redrawn until the
behaviour is reachable.

## Results are returned, not written

A module that computes a value returns it rather than mutating the caller's
argument.

```typescript
// Returned
function calculateDiscount(cart): Discount {}

// Written into the caller's argument
function applyDiscount(cart): void {
  cart.total -= discount;
}
```

The rule reaches the caller's argument alone. A module that writes a file,
sends a message, or stores a record is doing its work, and
[A port at a process boundary](#a-port-at-a-process-boundary) governs how it
reaches across the process boundary to do so.
