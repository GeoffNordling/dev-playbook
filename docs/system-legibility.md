---
type: General-Sheet
title: System Legibility
description: The doctrine — the user understands the systems they own without reading all of them — and the principles and ambitions that serve it
---

# System Legibility

The doctrine for keeping the workspace's systems understandable by
the user. It motivates the legibility machinery — shared vocabulary,
declared contracts, deterministic gates — and holds future intentions.

## The goal

No more slop! The user will understand systems without
reading all of them directly. **Slop** defeats this. Slop is when the
system is either:

- **Low quality** — diverges from the user's latent intent.
- **Not understood** — critical information is recorded in incomprehensible
  piles of text and code, greppable by AI, but illegible to the user.
  The system may or may not be aligned with user intent; the
  user does not know because they do not comprehend it.

Over time, the user accumulates **intent alignment debt**, a parallel
of tech debt.

## Why slop happens

AI's natural language interface — "programming in words" — is convenient
and magical. Yet, natural langugage is ill-defined, ambiguous, and
high dimensional. Natural language instructions present a faithful
AI with many different ways to obey, all technically valid: the AI picks one.
From the user's perspective, this choice is unpredictable and
unobservable (too costly to observe). Chaining many such instructions
together grows a thick garden forking paths. Some paths align with user intent,
others do not. The user loses track of the AI's specific path; they know only
that the AI is in the garden *somewhere*.

The fundamental problem is stochasticity: each AI action is random,
whether aleatoric (model internals, temperature, etc.) or epistemic
(the user's inability or unwillingness to keep up with the details).
When user's "vibe", they gamble that one random walk through
the garden will just happen to align with their intent.

## The CLOA

The Correct Level of Abstraction: a happy place where the user and the AI
communicate in shared terminology at the correct level
of abstraction to achieve the user's latent goal efficiently. This shared level is a
best-effort approximation of a latent optimum neither party knows a
priori. It is both the highest level of abstraction at which the user can trust the AI
and the lowest level at which the AI needs the user.

Too low (too much detail) and the user stops paying attention: *rubber stamping*.
Too high (not enough detail) and the user is temporarily fooled into thinking
they understand the system: *vibe coding*.
The CLOA changes dynamically depending on the system and the user goal.

### The slop trench

Users who operate off of the CLOA will find themselves in the
**slop trench**. This is a dirty, nasty, sad place; the slop can be deep. Digging
out requires careful, repeated, corrective conversation turns with the
AI to recover and pay off the intent alignment debt.

Users who dig out, but do not reflect on how they got themselves into
the slop trench to begin with, will surely return to it soon.

The only way to stay out of the slop trench is to stop making slop.

## Determinism as a forcing function

Pandas and Git impose
their abstractions uncompromisingly; a wrong mental model of their operations fails fast upon contact with reality.
The solution is determinism. We must deliberately engineer deterministic
forcing functions at the CLOA. By building observation platforms over the
garden, the user maintains sight of the AI and keeps it aligned with their intent.

CLOA platforms are 100% deterministic objects that give the user and AI
one shared view of the system.

### Documentation is code

Documentation is code: it tells agents what to do. An agent is nothing but
documentation, permissions, and a harness. Treat documentation as
a form of code: stochastic and high-dimensional. When faced with
a hard problem in documentation, transform in the mind's eye to code, think of
a solution, then port back to documentation space.

Documentation has three readers, in priority order:

1. **The executing agent** — the primary customer. Runbook prose
   commands the agent in natural imperative English; nothing may
   clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parsers and linters. A light touch
   needed; we prioritize the agent and the user.

### The bedrock of determinism

Declared abstractions descend layer by layer until the target stops
being stochastic. That boundary is **the bedrock of determinism**:
deterministic code, firm and strong, where a claim is checked by
running something that is 100% consistent. The boundary is where
documentation stops and code begins: documentation is the stochastic
thing, code the deterministic one. Code is written above the bedrock
in support of documentation — a parser, a lint — but that support
stands on the bedrock; it does not move the boundary. Abstractions
continue below the bedrock — call graphs, import graphs, industry
tooling — but the mode flips: above, machinery is invented
at great expense in user thought, working sessions, and
supporting code. Below, we often choose pre-existing tools.

### Provenance and the pandas standard

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
  expensive and create slop if not handled carefully. Deterministic backpressure — detectors, linters, gates,
  plain contact with reality — is inviolable and efficient. Prefer it
  wherever it can reach, and prefer claims a lint can check: "skill X
  references skill Y" is greppable; "skill X is clean" is not. Keep
  agentic backpressure tools simple and loop-friendly — a status code
  beats a detailed report.
- **Move slowly in decision space.** Small iterative steps, with
  backpressure from real-world contact. Reality gets a veto;
  we prefer to hear its opinion early and often.
- **Constrain to optimize understanding.** Funnel declarations
  through reduced forms designed for user understanding. A constraint on
  form amortizes reading — learn the shape once, read every instance
  fast — makes location and absence meaningful, and yields rules a
  lint can hold.
- **A document does one thing.** It does that thing predictably and
  in a structured way. What the thing is, and the structure it takes,
  is fixed at the CLOA by the document's type: each doc-type has its
  own CLOA shape and representation — a runbook's chain, a card's four
  cells, a standard's population and rules. Content that does a second
  thing belongs in a second document.

### The vocabulary API

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
