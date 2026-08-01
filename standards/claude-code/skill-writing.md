---
type: Standard
title: Skill Writing
description: How a skill is written so it behaves predictably — invocation, the description, the information hierarchy, splitting, pruning, leading words, and the failure modes
---

# Skill Writing

A skill exists to wrangle determinism out of a stochastic system.
**Predictability** — the agent taking the same *process* every run, not
producing the same output — is the root virtue; every lever below serves it.

**Bold terms** are defined in
[skill-glossary.md](/standards/claude-code/skill-glossary.md), which carries
the full meaning of each.

This is the advisory layer.
[skill-conventions.md](/standards/claude-code/skill-conventions.md) is the
binding one — the closed frontmatter vocabulary, the description format, and
the bundle layout that [skill-lint](/scripts/skill-lint) enforces at the
commit gate. Where a lever below touches either, it defers to conventions by
link and restates nothing.

This document was seeded from
`skills/productivity/writing-great-skills/SKILL.md` in
[mattpocock/skills](https://github.com/mattpocock/skills), pinned at
`2ab958093e83e0ec752e6c1c5932da465bf23e0c`, then modified to meet this
workspace's constraints — its declarative voice and spelling, and the closed
frontmatter vocabulary and two-sentence description rule that
`skill-conventions.md` binds. Its sibling `GLOSSARY.md` at the same pin is
seeded as [skill-glossary.md](/standards/claude-code/skill-glossary.md). The
pin is what a later sweep delta-checks both files against.

## Invocation

Two choices, trading different costs:

- A **model-invoked** skill is reachable by the agent, which can fire it
  autonomously, *and* by other skills; the human can still type its name. It
  contributes to **context load** — its **description** sits in the window
  every turn. Mechanics: `disable-model-invocation: false`, and a description
  whose trigger sentence names the contexts that should fire it.
- A **user-invoked** skill is out of the agent's reach: only the human, typing
  its name, can invoke it, and no other skill can. Zero context load, but it
  spends **cognitive load** — the human is the index that must remember it
  exists. Mechanics: `disable-model-invocation: true`. Its description is
  still authored and still bound to the same form; what changes is that no
  model reads it.

Both fields answer to
[skill-conventions.md — Required fields](/standards/claude-code/skill-conventions.md#required-fields).

Model-invocation is chosen only when the agent must reach the skill on its
own, or another skill must. A skill that only ever fires by hand is
user-invoked and pays no context load.

When user-invoked skills multiply past what the human can remember, that
piled-up cognitive load is cured by a **router skill**: one user-invoked skill
that names the others and when to reach for each.

## Writing the description

A model-invoked **description** does two jobs — state what the skill is, and
list the **branches** that should trigger it. Every word increases **context
load**, so a description earns even harder pruning than the body:

- **Front-load the skill's leading word** — the description is where it does
  its invocation work.
- **One trigger per branch.** Synonyms that rename a single branch are
  **duplication** — "build features using TDD … asks for test-first
  development" is one branch written twice. Collapse them; keep only genuinely
  distinct branches.
- **Cut identity that's already in the body.** Past the sentence naming what
  the skill does, spend the description on triggers, plus any "when another
  skill needs…" reach clause.

## Information hierarchy

A skill is built from two content types — **steps** and **reference** — that
mix freely: a skill can be all steps, all reference, or both. The core
decision is which to use and where each sits on the **information hierarchy**,
a ladder ranked by how immediately the agent needs the material:

1. **In-skill step** — an ordered action in `SKILL.md`, the primary tier: what
   the agent does, in order. Each step ends on a **completion criterion**, the
   condition that tells the agent the work is done. Make it *checkable* (can
   the agent tell done from not-done?) and, where it matters, *exhaustive*
   ("every modified model accounted for", not "produce a change list") — a
   vague criterion invites **premature completion**.
2. **In-skill reference** — a definition, rule, or fact in `SKILL.md`,
   consulted on demand. Often a legitimately flat peer-set (every rule of a
   review on one rung) — a fine arrangement, not a smell.
3. **External reference** — reference pushed out of `SKILL.md` into a separate
   file, reached by a **context pointer**, loaded only when the pointer fires.
   This spans *disclosed* reference — a sibling file inside the bundle, per
   [skill-conventions.md — References directory](/standards/claude-code/skill-conventions.md#references-directory)
   — through fully **external reference** that lives outside the skill system
   and any skill can point at.

A demanding completion criterion drives thorough **legwork** — the digging the
agent does within the work — whether the skill has steps or not, since "every
rule applied" binds flat reference just as "every step done" binds a sequence.

Push too little down and the top bloats; push too much and material the agent
actually needs is hidden. That tension is the whole decision.

**Progressive disclosure** is the move down the ladder — out of `SKILL.md`
into a linked file — so the top stays legible. Mechanics: a linked `.md` file
in the skill folder, named for what it holds. Some skills are used in more
than one way, and each distinct way is a **branch** — different runs taking
different paths through the skill. Branching is the cleanest disclosure test:
inline what every branch needs, and push behind a pointer what only some
branches reach. A **context pointer**'s *wording*, not its target, decides
when and how reliably the agent reaches the material.

Where the ladder decides *how far down* a piece sits, **co-location** decides
*what sits beside it* once there: a concept's definition, rules, and caveats
belong under one heading rather than scattered, so reading one part brings its
neighbors with it.

## When to split

**Granularity** is how finely skills are divided, and each cut spends one of
the two loads, so a cut is made only when it earns the spend. Two cuts:

- **By invocation** — split off a **model-invoked** skill where there is a
  distinct **leading word** that should trigger it on its own, or where
  another skill must reach it. The new always-loaded **description** costs
  **context load**, so that independent reach has to be worth it.
- **By sequence** — split a run of **steps** where the steps still ahead (a
  step's **post-completion steps**) tempt the agent to rush the one in front
  of it (**premature completion**). Keeping them out of view encourages more
  **legwork** on the current task.

## Pruning

Keep each meaning in a **single source of truth**: one authoritative place, so
changing the behavior is a one-place edit.

Check every line for **relevance**: does it still bear on what the skill does?

Then hunt **no-ops** sentence by sentence, not just line by line: run the
no-op test on each sentence in isolation, and when one fails, delete the whole
sentence rather than trim words from it. Be aggressive — most prose that fails
should go, not be rewritten.

## Leading words

A **leading word** is a compact concept already living in the model's
pretraining that the agent thinks with while running the skill (e.g. *lesson*,
*fog of war*, *tracer bullets*). Repeated throughout the text — though not
necessarily, since a strong leading word might be needed only once — it
accumulates a distributed definition and anchors a whole region of behavior in
the fewest tokens, by recruiting priors the model already holds.

It serves predictability twice. In the body it anchors *execution*: the agent
reaches for the same behavior every time the word appears. In the description
it anchors *invocation*: when the same word lives in the human's prompts,
docs, and code, the agent links that shared language to the skill and fires it
more reliably.

Hunt for opportunities to refactor skills onto leading words. A triad spelled
out at three sites (**duplication**), a description spending a sentence to
gesture at one idea — each is a passage begging to **collapse** into a single
token. Examples include:

- "fast, deterministic, low-overhead" → *tight* — one quality restated across
  a phase — into a single pretrained word (a *tight* loop).
- "a loop you believe in" → *red* — converts a fuzzy gate into a binary
  observable state (the loop goes *red* on the bug, or it doesn't).

The collapse wins twice over: fewer tokens, *and* a sharper hook for the agent
to hang its thinking on. Assume every skill is carrying restatements that
leading words retire, and go find them.

## Failure modes

These diagnose issues a skill's user may be having with it.

- **Premature completion** — ending a step before it's genuinely done,
  attention slipping to *being done*. Defense, in order: sharpen the
  completion criterion first (cheap, local); only if it is irreducibly fuzzy
  *and* the rush is observed, hide the post-completion steps by splitting (the
  sequence cut).
- **Duplication** — the same meaning in more than one place. Costs maintenance
  and tokens, and inflates a meaning's prominence on the ladder past its real
  rank.
- **Sediment** — stale layers that settle because adding feels safe and
  removing feels risky. The default fate of any skill without a pruning
  discipline.
- **Sprawl** — a skill simply too long, even when every line is live and
  unique. Hurts readability and maintainability and wastes tokens. The cure is
  the ladder: disclose **reference** behind pointers, and split by **branch**
  or sequence so each path carries only what it needs.
- **No-op** — a line the model already obeys by default, so load buys nothing.
  The test: does it change behavior versus the default? A weak leading word
  (*be thorough*, when the agent is already thorough-ish) is a no-op; the fix
  is a stronger word (*relentless*), not a different technique.
- **Negation** — steering by prohibition backfires: *don't think of an
  elephant* names the elephant and makes it more available, not less. Prompt
  the **positive** — state the target behavior so the banned one is never
  spoken; keep a prohibition only as a hard guardrail that cannot be phrased
  positively, and even then pair it with what to do instead. This is the
  skill-body case of the workspace rule in
  [prose/conventions.md — Voice](/standards/prose/conventions.md#voice).
