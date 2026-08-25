---
type: General-Sheet
title: Edge Encoding
description: The inline grammar that makes skill prose machine-parseable — the rules ruled so far and the roster of edges still to encode
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

## The trifecta

Every encoding decision must serve three readers, in priority order:

1. **The executing agent** — the primary customer. Skill prose commands the
   agent in natural imperative English; nothing may clutter that.
2. **The user** — reads the file as plain English.
3. **Deterministic code** — the parser that generates chains and the lint
   that enforces the grammar. Served by subtle helpers, never by machine
   notation embedded in prose.

Inspirations, inspiration only: doctest (fenced blocks inside prose are
legitimate deterministic parse targets) and CNL (constrain the sentence,
never embed notation). STE is loose style inspiration, unenforced. What we
adopt 100% is our own small grammar below, to be specified as a standard
card and enforced by our lint.

## The grammar — ruled so far

- **Braced span.** `{keyword payload}` — the one inline form. Every span
  opens with a fixed keyword from the grammar's lexicon; the keyword types
  the span and the remainder is payload. Keywords match case-insensitively
  so sentence-initial `{Read …}` stays natural. Flat by default; nesting is
  reserved and capped at two deep.
- **Delimiter.** `{…}` won on merit: the skill corpus is nearly free of
  braces outside code spans, angle brackets are the workspace's placeholder
  convention (`<issue>`, `<repo>`), and a space-free `<tag>` vanishes in
  rendered HTML. Greenfield mindset stands — a collision alone never vetoes
  a choice.
- **Code contexts are inert.** Spans are interpreted only outside code
  spans and fenced blocks.
- **Unmarked prose is never an edge.** The marker declares; the parser
  infers nothing. log-friction's "carrying a proposed fix only where the
  user gave one" fires no edge and needs no special rule.
- **Imperative in, third-person out.** Keywords are agent-facing commands
  (`Read`, `Commit`); deterministic code translates to the chain's edge
  labels (`reads`, `writes`) as the third-party observer.

Ruled encodings, one per edge:

- **guard** — `{only where <condition>}`, a trailing clause of the
  edge-firing sentence. At most one per sentence; the condition is the
  payload after the fixed keyword `only where`, lifted verbatim; absence
  means the edge is unconditional (solid, not dashed).
- **reads** — `{read <payload containing exactly one link>}`. The one
  markdown link or citation in the span is the edge target; other words in
  the span are annotation. Two reads means two spans; zero or two links in
  one span fails the lint.
- **writes, git bucket** — `{commit …}` declares the edge; the fenced
  command block in the same step supplies the machine detail — repo from
  `-C`, operations from the git subcommands. The lint requires the block
  and fails span/block disagreement. Other write buckets (local file,
  GitHub, scratch, cache) are unruled; each gets its keyword when its
  exemplar sentence comes up.
- **args** — derived, no inline marker. A heading of the form
  `## <Name>: $ARGUMENTS` declares one argument: the name is the heading
  text lowercased, the type is `str` because the harness's `$ARGUMENTS`
  substitution is always a string. The frontmatter `argument-hint` stays
  display text, not the declaration. The multi-argument form (wayfinder's
  `idea`/`map`/`ticket`) is outside the covering set and stays unruled.

## Proposal procedure

Every encoding proposal is presented on screen in three parts, and one
ruling approves the three together:

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

## Principles ruled this session

- **Skills are programs.** No narrative intro; the body is instructions,
  as if it were a program. The one-sentence summary lives in the
  frontmatter `description`, whose meaning we may redefine as needed.
- **No shadow prose.** Prose that restates a primitive must either become
  the marked edge or be reworded away. log-friction's deleted intro
  ("Append one entry … and commit it") was the ruling case.
- **Declared versus derived.** Node type and ownership derive from path;
  node data (`model`, `effort`, `allowed-tools`) from frontmatter; the
  summary from `description`; args mostly from the existing
  `## Name: $ARGUMENTS` heading form. Edges, guards, and returns are
  declared inline. No file describes another file's behavior — subtrees
  are stitched by following does-edges into the target file's own
  declarations.
- **Workflow.** `edge-examples/` is committed at verbatim original
  content; the encoding under design rides as uncommitted edits so the
  diff against HEAD shows exactly what the encoding changes; a ruled
  edge's edit is committed. Commits run the document linters; the
  test-suite hook is skipped (`SKIP=make-check` on push).
- **Acronyms defined once**, at the top of anything we write.

## The roster

Every edge CLOA-ABSTRACTIONS.md defines, its exemplar sentence, and where
it stands. The minimal covering set is four skills plus one agent file —
no skill fires both a does→Agent and a does→Script edge.

| # | Edge | Exemplar | Status |
|---|---|---|---|
| 1 | guard | log-friction step 3 | **Ruled**, committed |
| 2 | reads | log-friction step 1 | **Ruled**, committed |
| 3 | writes (git bucket) | log-friction step 3 + fenced block | **Ruled**, committed |
| 4 | args | log-friction `## Friction: $ARGUMENTS` | **Ruled**, derived — no diff to commit |
| 5 | returns | log-friction step 4 ("Report in one line …") | Open — name/type unexpressed in prose |
| 6 | does → Agent | document-deslop ("launch the `deslopper` subagent") | Open |
| 7 | does → Skill | grill-with-docs ("Run a /grilling session") | Open |
| 8 | does → Script | usage-report (its `report.sh` run) | Open |
| 9 | overrides | grill-with-docs ("Where /domain-modeling says …") | Open |

Also open, beyond the roster: the remaining write buckets; where the
grammar's standard card lives; the lint and parser themselves; and the
old two-sided question — whether an unmarked link to a known unit should
require a waiver — parked, not dropped.
