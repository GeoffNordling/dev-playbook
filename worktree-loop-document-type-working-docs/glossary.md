---
type: General-Sheet
title: Glossary
description: The conceptual model of the doc-type system as a glossary — one meaning per word, from state and predicate through spec, model, verifier, finding, distribution, and loop, so every other member uses the same words
---

# Glossary

The words of the doc-type system, one meaning each. This is the
conceptual model, what domain-driven design calls the ubiquitous
language: the level above the pseudocode of
[Reference Model](/worktree-loop-document-type-working-docs/reference-model.md)
and above the predicates that will describe the same target. Every
member of the set uses these words in these senses, and the entries
are the seed of the system's eventual context file. Speculative, per
[ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md).

Three levels, top down: the glossary is the words; the reference
model is one witness in pseudocode; the specification is the
predicates.

## Logic

- **State** — everything a predicate may read at one moment: the repo
  tree and the targets outside it.
- **Predicate** — a statement about one member at one moment that is
  true or false. It defines a set: the states where it holds.
- **Rule** — a predicate as it lives in a Standard: an id, a kind, the
  predicate text, and an optional condition. A rule is about one
  member; the Standard lifts it to the state: every member of the
  population satisfies it.
- **Condition** — a rule another rule is under. Where the condition is
  false the rule under it is not evaluated, so its set widens to
  include those states. The word is condition, never guard.
- **Population** — the class of targets a Standard's rules range over.
- **Specification** — a set of predicates taken together. It defines
  the intersection of their sets. A Standard is a spec written as a
  file over a population. Short form: spec.
- **Target state** — the set of states that satisfy a spec. Not one
  state; a set.
- **Reference model** — one state that satisfies the spec, drawn out.
  A witness. Model checking writes the relation as M ⊨ φ: the model
  satisfies the formula. Property-based testing calls the same pair
  example and property. Model and spec are the two written forms of
  one target.

## Verification

- **Verifier** — what decides a rule for a member. A script for a
  deterministic rule, a judge for a stochastic one.
- **Deterministic rule** — its verifier is a function. Same input,
  same answer. Hard set membership.
- **Stochastic rule** — its verifier is a judge with an error rate. A
  noisy classifier of membership. This is the one place statistics
  enters the logic.
- **Finding** — one member and the rule it fails. Evidence that the
  state is outside the set.
- **Audit** — evaluate a spec against a state. Returns the findings.
  Zero findings means the state is in the set, up to judge error.
- **Gate** — an audit at a repo boundary that blocks on findings.

## Statistics

- **Distribution** — the states an act could leave behind, each
  weighted by how likely it is, given the state it starts from and the
  prompt it is given. Some of the weight falls inside the target set,
  some outside. A distribution is not a set and a set is not a
  distribution.
- **Sample** — one state an act did leave behind: one draw from its
  distribution.
- **Loop** — drives a state toward a target state by iteratively
  taking prescribed actions and validating against prescribed
  standards, the one sentence of
  [ROOT.md](/worktree-loop-document-type-working-docs/ROOT.md#terms).
  In this vocabulary: a trajectory of samples that ends when one lands
  in the set or when a yield's condition holds first. Each sample
  starts from the last, with its findings in the prompt, so the
  samples are not independent: the trajectory is a path through state
  space. Check audits the sample, act draws the next one, yield exits
  to the user or another loop.

The two vocabularies meet at one seam. Predicates define a set, with
no probabilities attached. An act is a draw from a distribution over
states, and the draw lands in the set or outside it. A loop does not
change the LLM; it changes what the next draw is given:
check finds where the last sample fell outside, act draws again with
those findings in the prompt, so successive samples land in the set
more often. Deterministic rules decide membership exactly; stochastic
rules decide it with an error rate. Everything else is logic.

## Acronyms

- **LLM** — Large Language Model.
