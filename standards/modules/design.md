---
type: Standard
title: Module Design Conventions
description: The deep-module contract — depth, the seam rules, and the port at a process boundary
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
a small interface, reachable through that interface. The reasoning, diagrams,
and examples behind them are the
[Module Design Explanation](/standards/modules/explanation.md); the tests that cross a module's
interface are [Testing Conventions](/standards/testing/conventions.md).

## Deep, not shallow

A module's interface is small against the behaviour behind it: what a caller
or a test must learn to use the module is little against the amount of
behaviour that use reaches. The measure is the interface alone, so a module
composed inside of many small, swappable parts satisfies the rule as long as
those parts stay out of its interface.

`modules.deep-not-shallow` · stochastic

## Internal seams stay inside

A module's interface exposes no seam — a place where behaviour is altered
without editing in that place — that exists only for the module's own tests.

`modules.internal-seams-stay-inside` · stochastic

## Two adapters, or no seam

A seam a module presents carries at least two adapters, concrete things that
satisfy the interface at that seam; a test's in-memory fake is one.

`modules.two-adapters-or-no-seam` · stochastic

## Dependencies are accepted, not constructed

A module takes each of its dependencies as a parameter and constructs none of
them in its own body.

`modules.dependencies-are-accepted-not-constructed` · stochastic

## A port at a process boundary

A dependency a module reaches across a process boundary, a service the
workspace owns or a third party it does not control, sits behind a **port** at
the module's own interface: the module holds the logic, and the transport that
carries the call out of the process satisfies that port. A dependency the
module reaches inside its own process — pure computation, in-memory state, or
a store with an in-process stand-in the tests use — needs no port.

`modules.a-port-at-a-process-boundary` · stochastic

## The interface is the test surface

Every behaviour of a module is reachable through its interface.

`modules.the-interface-is-the-test-surface` · stochastic

## Results are returned, not written

A module that computes a value returns it and does not mutate the caller's
argument to deliver it. The rule reaches the caller's arguments alone: a
module that writes a file, sends a message, or stores a record is doing its
work and satisfies it.

`modules.results-are-returned-not-written` · stochastic
