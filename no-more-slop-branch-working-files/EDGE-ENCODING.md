---
type: General-Sheet
title: Edge Encoding
description: The one-to-one primitive map from Reference chain to skill prose — the ruled encodings, the holes, and the residual ledger
---

# Edge Encoding

The lower-level design under
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md):
machine-parseable structure inside skill and agent prose, so deterministic
code can generate the Reference chains that file defines. Same working-file
conventions as its siblings: speculative voice, deleted when the results
merge. The exemplar files being edited live in `edge-examples/`; the live
skills stay untouched until the design settles.

Acronyms used here, defined once: CLOA — Correct Level of Abstraction.
CNL — Controlled Natural Language, an engineered subset of a natural
language with restricted vocabulary and grammar so machines can parse what
a reader reads. STE — ASD-STE100 Simplified Technical English, one
specific CNL from aerospace, aimed at readers rather than machines.

## Three readers

Every encoding decision must serve three readers, in priority order:

1. **The executing agent** — the primary customer. Skill prose commands the
   agent in natural imperative English; nothing may clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parser that generates chains and the lint
   that enforces the grammar. Served by subtle helpers, never by machine
   notation embedded in prose.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What we adopt 100%
is our own small grammar below, to be specified as a standard card and
enforced by our lint.

## The theory

Every higher-level primitive maps one-to-one to exactly one lower-level
expression — `reports` in the chain is `{Report …}` in the prose, and
nothing else is. A skill is then rewritten using only the map, and
whatever prose refuses to fit is a **residual**, tracked in the ledger
below. A valuable residual amends the shared primitive structure; a
worthless one is reworded away. This is
[the EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#the-loop)
run at a lower level — still generating primitives in partnership with
the user to minimize residuals, with the skill file as the target
artifact and the map as the current abstraction set. The earlier
sentence-by-sentence retrofit ran the loop backwards, and every retrofit
surfaced a fresh complexity; the map runs it forwards.

## The primitive map

| Higher primitive | Lower expression | Status |
|---|---|---|
| node type + ownership | file path | **Ruled** (derived) |
| node data (`model`, `effort`, `allowed-tools`) | frontmatter, verbatim | **Ruled** (derived) |
| unit summary | frontmatter `description` | **Ruled** (derived) |
| args | frontmatter `arguments` list — name only | **Ruled** (derived) |
| reads | `{Read <one link>}` | **Ruled** |
| writes — git bucket | `{Commit …}` + fenced command | **Ruled** |
| writes — other buckets | — | **Hole** |
| reports | `{Report <payload>}` | **Ruled** |
| guard | `{If <condition>, {…}}` containment | **Ruled** |
| does → Agent / Skill / Script / Workflow | — | **Hole** |
| overrides … with … | — | **Hole** |

The ruled rows, in detail:

- **args** — fully derived from the harness-native frontmatter field:
  `arguments: [friction]` declares the edge and the name; the chain
  shows the name alone. No type (`$ARGUMENTS` is text substitution, so
  every arg is a string — remembered, not encoded), no annotation (the
  name must carry the meaning, same rule as code), no `argument-hint`
  (its only harness function is the `/` autocomplete popup), no
  `## Name: $ARGUMENTS` heading, no placeholder in the body. Multi-arg
  comes free: wayfinder declares `arguments: [idea, map, ticket]`.
  Harness facts behind the ruling (official skills docs): `$ARGUMENTS`
  substitution is harness-implemented; a file with no placeholder gets
  the argument text appended to the rendered content as
  `ARGUMENTS: <input>`, so nothing is dropped; `$name` placeholders are
  positional with shell-style splitting — on unquoted free text they
  grab one word — so free-text skills must not use them. Verification
  step before porting to live skills: one live test that the append
  fallback fires unchanged when `arguments:` is declared. Ripple: the
  skill standards' `## Name: $ARGUMENTS` heading convention and
  `argument-hint` guidance retire when this merges.
- **guard** — `{If <condition>, {edge span} …}`: the guard nests the
  span(s) it guards, so binding is containment, never sentence
  adjacency. The text between the keyword `if` and the first nested
  span is the condition, lifted verbatim (trailing comma dropped);
  every nested span fires under that condition and draws dashed; prose
  in the body ("and stop") stays uncoded. This spends the two-deep
  nesting cap — guard at depth one, edges at depth two, never deeper.
  A span nested nowhere is unconditional (solid). Unbraced `if` stays
  plain prose and fires nothing. (Supersedes `{only where …}` and the
  same-sentence adjacency rule: the distinctive phrase and the
  heuristic are both jobs the braces already do.)
- **reads** — `{Read <payload containing exactly one link>}`. The one
  markdown link or citation in the span is the edge target; other words in
  the span are annotation. Two reads means two spans; zero or two links in
  one span fails the lint.
- **writes, git bucket** — `{Commit …}` declares the edge; the fenced
  command block in the same step supplies the machine detail — repo from
  `-C`, operations from the git subcommands. The lint requires the block
  and fails span/block disagreement.
- **reports** — `{Report <payload>}`. The name is the constant default
  `outcome`, the type the constant `str` (a skill's report to its caller
  is prose); the annotation is the payload after the keyword, verbatim.
  Named or non-str reports (candidate-promote's `issue_number: int`) and
  multiple reports (handoff) are outside the covering set, unruled.

## Grammar mechanics

- **Braced span.** `{keyword payload}` — the one inline form. Every span
  opens with a fixed keyword from the grammar's lexicon; the keyword types
  the span and the remainder is payload. Keywords match case-insensitively
  so sentence-initial `{Read …}` stays natural. Flat by default; nesting is
  reserved and capped at two deep — the guard spends it.
- **Delimiter.** `{…}` won on merit: the skill corpus is nearly free of
  braces outside code spans, angle brackets are the workspace's placeholder
  convention (`<issue>`, `<repo>`), and a space-free `<tag>` vanishes in
  rendered HTML. Greenfield mindset stands — a collision alone never vetoes
  a choice.
- **Code contexts are inert.** Spans are interpreted only outside code
  spans and fenced blocks.
- **Unmarked prose is never an edge.** The marker declares; the parser
  infers nothing. log-friction's "carrying a proposed fix if the user
  gave one" fires no edge and needs no special rule — unbraced `if` is
  the deliberate tier for conditional logic left out of the chain.
- **Imperative in, third-person out.** Keywords are agent-facing commands
  (`Read`, `Commit`, `Report`); deterministic code translates to the
  chain's edge labels (`reads`, `writes`, `reports`) as the third-party
  observer. The higher level renamed `returns` to `reports` so this
  translation is always the bare `+s`, never a word swap.

## Proposal procedure

Every encoding proposal is presented on screen in parts, approved together
by one ruling:

1. **The target.** The Reference chain fragment being encoded, drawn in
   [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
   notation — only the edges this proposal covers, nothing projected
   forward.
2. **The prose.** The exemplar's before and after — the diff that would
   land.
3. **The certification.** A trace from every element of the target
   fragment to the exact source token that yields it — a span keyword, a
   link, a fenced command, a frontmatter field, a path segment. Approval
   certifies that deterministic code parsing the after-prose reconstructs
   the target fragment exactly; the trace is the contract the future
   parser implements.

## Residual ledger

Per exemplar: what the full rewrite could not express in the map. Each
entry awaits a verdict — valuable (amends the shared structure) or not
(reworded away).

### log-friction

The rewrite converges: every sentence is a primitive, an accounted
internal, or one of these residuals.

1. **Behavior-mode block** — "Run to completion without asking the user
   anything … fire-and-forget …". The higher level already ledgers this
   category (orchestrate's whole body, diagnosing-bugs' secret-redaction
   rule) as remembered-not-primitive. It recurs; strongest candidate for
   a future primitive.
2. **Control flow** — "and stop" in the nothing-to-record bullet. Early
   exit has no primitive; it rides as uncoded payload words the agent
   obeys.
3. **Rationale prose** — "An imperfect entry is cheap: the log is
   append-only prose …". Not an instruction — why-text calibrating the
   agent's judgment. No primitive expresses justification.

Accounted: the three unbraced `If` bullets (the deliberate
uncoded-conditional tier); step 2's entry-writing and step 3's staging
detail (internal program below the CLOA); the working-tree edit itself
(subsumed by the git commit edge, exactly as the ledger's chain models
it).

## Principles ruled this session

- **Skills are programs.** No narrative intro; the body is instructions,
  as if it were a program. The one-sentence summary lives in the
  frontmatter `description`, whose meaning we may redefine as needed.
- **No shadow prose.** Prose that restates a primitive must either become
  the marked edge or be reworded away. log-friction's deleted intro
  ("Append one entry … and commit it") was the ruling case.
- **Declared versus derived.** Node type and ownership derive from path;
  node data (`model`, `effort`, `allowed-tools`) from frontmatter; the
  summary from `description`; args from the frontmatter `arguments`
  list. Edges, guards, and reports are
  declared inline. No file describes another file's behavior — subtrees
  are stitched by following does-edges into the target file's own
  declarations.
- **Workflow.** `edge-examples/` is committed at verbatim original
  content; the encoding under design rides as uncommitted edits so the
  diff against HEAD shows exactly what the encoding changes; a ruled
  edge's edit is committed. Commits run the document linters; the
  test-suite hook is skipped (`SKIP=make-check` on push).
- **Acronyms defined once**, at the top of anything we write.

## Holes in the map

Each hole has its exemplar waiting in the covering set — four skills
plus one agent file; no skill fires both a does→Agent and a does→Script
edge.

| Hole | Exemplar |
|---|---|
| does → Agent | document-deslop ("launch the `deslopper` subagent") |
| does → Skill | grill-with-docs ("Run a /grilling session") |
| does → Script | usage-report (its `report.sh` run) |
| overrides … with … | grill-with-docs ("Where /domain-modeling says …") |
| writes — other buckets | local file, GitHub, scratch, cache — each when its sentence comes up |

Also open, beyond the map:

- **Scrub the skill standards.** The rulings here invalidate parts of
  the published skill-authoring surface: the describing markdown
  documents (the skill-conventions Standard and anything teaching the
  `## Name: $ARGUMENTS` heading or `argument-hint`), the linting
  scripts (`scripts/skill-lint` and friends must stop expecting the
  old forms and start enforcing the map), and the live skills
  themselves. A full scrub when the design ports.
- Where the grammar's standard card lives.
- The lint and parser themselves.
- The old two-sided question — whether an unmarked link to a known
  unit should require a waiver — parked.
