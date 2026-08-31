---
type: General-Sheet
title: System Legibility
description: The doctrine — the user understands the systems they own without reading all of them — and the principles and ambitions that serve it
---

# System Legibility

The doctrine for keeping the workspace's systems understandable by
the user. It motivates the legibility machinery — shared vocabulary,
declared contracts, deterministic gates — and holds the intentions
that have not yet hardened into anything enforceable. Parts of this
paper may later harden into a Standard card, once they grow audit and
enforce teeth; until then the doctrine lives here.

## The goal

No more slop! The user will understand every system they own without
reading all of it directly. **Slop** defeats this. Slop is when the
system is either:

- **Low quality** — diverges from the user's latent intent.
- **Not understood** — critical information is recorded in incomprehensible
  piles of text and code, greppable by AI, but illegible to the user.
  The things within may or may not be aligned with user intent; the
  user does not know because they do not comprehend it.

Over time, the user accumulates **intent alignment debt**, a parallel
of tech debt.

## The CLOA

The Correct Level of Abstraction: a happy place where the user and the AI
communicate in shared terminology at the correct level
of abstraction to achieve the user's latent goal efficiently. This shared level is a
best-effort approximation of a latent optimum neither party knows a
priori. It is both the highest level of abstraction at which the user can trust the AI
and the lowest level at which the AI needs the user.

Too low (high detail) and the user checks out: they rubber stamp, building
intent alignment debt. Too high (low detail) and the user is temporarily
fooled into thinking they understand what the AI is doing (i.e. vibe coding).
The CLOA changes dynamically based on the system's purpose and the user's goal.

Before AI, deterministic interfaces were forcing functions. Pandas and Git impose
their abstractions uncompromisingly; a wrong mental model exploded on contact
with reality. After AI, natural language combined with AI's modus operandi to paper over uncertainty with fluent confidence (i.e., hallucinate). This enabled vibe coding, but also equipped
unwary users to hide large amounts of intent alignment debt for long periods.
We solve this problem by deliberately engineering customized deterministic
interfaces at the CLOA.

## The slop trench

Users who operate off of the CLOA will find themselves in the
**slop trench**. This is a place where users are buried in slop. Digging
out requires careful, repeated, sequential, corrective conversation turns with the
AI to dig out of the slop and pay off the intent alignment debt.

Users who dig out, but do not reflect on how they got themselves into
the slop trench to begin with, will surely return to it soon.

The only way to stay out of the slop trench is to stop making slop.

## Documentation is code

Documentation does things: agents do things, and an agent is nothing but
documentation, permissions, and a harness. Treat documentation as
a form of code: a stochastic and high-dimensional one. When faced with
a hard problem in documentation, translate to imaginary code, think of
a solution, then port back to documentation space.

Documentation has three readers, in priority order:

1. **The executing agent** — the primary customer. Runbook prose
   commands the agent in natural imperative English; nothing may
   clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parsers and linters. A light touch
   needed; we prioritize the agent and the user.

## The bedrock of determinism

Declared abstractions descend layer by layer until the target stops
being stochastic. That boundary is **the bedrock of determinism**:
deterministic code, firm and strong, where a claim is checked by
running something that is 100% consistent. Abstractions
continue below the bedrock — call graphs, import graphs, industry
tooling — but the mode flips: above, machinery is invented
at great expense in user thought, working sessions, and
supporting code. Below, we often choose pre-existing tools.

## Provenance and the pandas standard

Every abstraction carries a **provenance**: **declared** — invented
here, its contract written in this corpus — or **imported** — someone
else's, taken as a dependency, its contract as given. Imported
systems stand on the bedrock already, and fluency with them is cheap:
years of daily pandas and git taught the user which objects exist and
which methods fit which task, without ever reading inside a method.
That fluency is **the pandas standard**, the target state for
everything declared: a declared abstraction feels like an imported
one to its caller.

## Standing principles

- **Deterministic backpressure over stochastic functions.**
  Stochastic functions — user/AI conversations, prompts, models, agents — are powerful but
  expensive. Deterministic backpressure — detectors, linters, gates,
  plain contact with reality — is inviolable and efficient. Prefer it
  wherever it can reach, and prefer claims a lint can check: "skill X
  references skill Y" is greppable; "skill X is elegant" is not. Keep
  agentic backpressure tools simple and loop-friendly — a status code
  beats a detailed report.
- **Move slowly in decision space.** Small iterative steps, with
  backpressure from real-world contact. Reality has a veto;
  we prefer to hear its opinion early and often.
- **Constrain to optimize understanding.** Funnel declarations
  through reduced forms designed for the user's eyes. A constraint on
  form amortizes reading — learn the shape once, read every instance
  fast — makes location and absence meaningful, and yields rules a
  lint can hold.

## The vocabulary API

`CONTEXT.md` holds the canonical terms for communication: the user
understands it completely, the AI uses its terms, and missing terms
are added with user approval. Zero vibe coding in
that file. It is a public surface for user/AI conversation.

## Ambitions

- **An ontology solver.** The word **ontology** is reserved for a
  future deterministic inventory of the declared abstractions — their
  categories, relations, and axioms — with a solver that validates or
  invalidates operations among them: a type checker for what is
  declared here. Until that exists, the word stays out of the active
  vocabulary.
- **Hardening.** Any part of this doctrine that grows a checkable
  claim moves toward a Standard card with real audit and enforce
  sections.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
