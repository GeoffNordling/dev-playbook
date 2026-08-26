---
type: Standard
title: Instruction Grammar
description: The braced-span grammar and its ontology — the node kinds, the edge vocabulary, and the closed keyword lexicon that make skill and agent bodies machine-readable
---

# Instruction Grammar

Governs the body of every **runbook**. Which files those are is
[the harness-file registry](/standards/harness/files.md)'s call — it
classifies every harness file, and no class but the runbook carries
this grammar.

Two representations of one object stand as peers at different levels.
The **runbook** is the written level: documentation that acts — invoked
by name, arguments in, a report out, effects on state — whose body stays
natural imperative English for the executing agent. The **Reference
chain** is the abstract level, constructed from the runbook: the
declared tree of which verbs it executes plus its call
signature — the same behavior re-expressed so compactly that the user
takes in the whole runbook at a glance. The grammar is the one-to-one
join between them: each chain element has exactly one written
expression, so deterministic code constructs the chain from the runbook
without a model in the loop. This document defines the chain's
vocabulary first, then the written form that declares it.

The grammar serves readers in priority order: the executing agent
(the prose commands it; nothing may clutter that), the user (who reads
the file as plain English), and deterministic code (served by the
braces, never by machine notation embedded in prose).

## The Reference chain

The abstract level: nodes typed by kind, connected by a fixed edge
vocabulary.

### Node kinds

| Kind | Is |
|---|---|
| **Skill** | Documentation that runs in the calling context, on the caller's permissions, minus any clamp its own frontmatter declares. |
| **Agent** | Documentation that runs in a fresh context, on its own permission set. |
| **Script** | Deterministic code run via the shell — not a direct LLM call. |
| **Standard** | A rule the workspace runs under — define, audit, enforce, adopt, per [the meta-standard](/standards/standard/format.md). Appears in a chain only as an edge target. |

Kind derives from the target's path — a `skills/` segment makes a Skill,
an `agents/` segment an Agent, a script filename a Script, marked
in-bundle when the link is relative to the runbook's own directory. A node
also carries its **node data** — `model`, `effort`, `tools`,
`allowed-tools` — quoted verbatim from its own frontmatter, never
paraphrased into prose.

### Edges

A runbook declares its behavior as edges. **Edges live at the definition
site**: an edge belongs to the file whose text contains the instruction,
and a chain is stitched by following does-edges into each target file's
own declarations — no file describes another file's behavior.

- **does** — run a behavior some documentation defines: a Standard's
  verb where one exists, the whole runbook where the doc is the
  definition.
- **reads** — consulted, not run.
- **writes** — produce or mutate state outside the chain, typed by
  bucket: `git` or `local file`.
- **overrides … with …** — substitute a clause of another runbook's
  instructions at runtime, leaving its file untouched.
- **args** — the values the caller hands in at invocation; each is a
  string, and each dies with the call. A skill declares them by name in
  its frontmatter, per
  [Skill Conventions](/standards/harness/skill-conventions.md); an
  agent declares none — its input arrives in the launching prompt.
- **reports** — the value handed back to the caller; unlike a write, a
  report never lands in state. A report is `outcome: str` — a runbook's
  report to its caller is prose.

Any edge may carry a **condition**: the circumstance under which it
fires. A conditional edge is still the same edge — the condition changes
when it fires, never what it is.

## The runbook

The written level: how a body declares the chain's edges.

### The braced span

`{keyword payload}` is the one inline form. A span opens with a keyword
from the lexicon; the keyword types the span and the remainder is
payload. Keywords match case-insensitively, so a sentence-initial
`{Read …}` stays natural, and a span may wrap across source lines.

| Keyword | Chain element | Form |
|---|---|---|
| `Read` | reads | `{Read <payload with exactly one link>}` |
| `Write` | writes — local file | `{Write <payload>}` |
| `Commit` | writes — git | `{Commit <payload>}` + a fenced command block in the same step |
| `Report` | reports | `{Report <payload>}` |
| `Launch` | does — Agent | `{Launch <payload with exactly one link>}` |
| `Run` | does — Skill or Script | `{Run <payload with exactly one link>}` |
| `Override` | overrides | `{Override <one link + clause words> with <one link + detail words>}` |
| `If` | condition | `{If <condition>, {edge span} …}` |

This vocabulary is closed: the keywords above are the whole lexicon, and
these forms are the whole grammar. A new keyword, write bucket, or span
form requires an edit here before its first use.

Keywords are imperative commands to the executing agent; the chain's
edge labels are their third-person forms. Per keyword:

- **Read.** The one link is the target; exactly one per span.
- **Write.** Local-file bucket. The payload is opaque; no link is
  interpreted.
- **Commit.** Git bucket. A fenced command block in the same step
  carries the detail — repo from `-C`, operations from the
  subcommands — and must agree with the span.
- **Report.** The payload is the report's content, verbatim.
- **Launch.** The link is the agent definition; its model, effort, and
  tools stay in that file, never restated.
- **Run.** The link decides the kind: a `SKILL.md` is a Skill, a script
  file is a Script.
- **Override.** The word `with` splits the payload — overridden runbook
  before, replacement after; one link per side.
- **If.** The only span that nests. The text before the first nested
  span is the condition, verbatim; each nested span fires only under
  it. Two deep.

### Slicing, never interpreting

Deterministic code touches only fixed cut points: the keyword, the
markdown link(s), the `with` splitter, nested braces, and the first
semicolon. Every word between cut points is opaque annotation — a real
instruction to the executing agent, carried verbatim for display, never
parsed and never load-bearing to code. The words that make a span read
as a natural sentence — an article before the link, a noun after it —
are glue for the executing agent; code reads none of them.

- **The first semicolon ends the chain's view.** In any sliced payload,
  text after the first `;` is file-only elaboration; the kernel before
  it travels to the chain. Front the kernel: open the span with the
  words that belong on the edge, and demote the rest behind the
  semicolon.
- **Code contexts are inert.** Spans count only outside code spans and
  fenced blocks.
- **Unmarked prose is never an edge.** The brace declares; the parser
  infers nothing. Anything left unbraced — a condition, a read, a whole
  step — still binds the executing agent; leaving it unbraced is the
  author's choice to keep it out of the chain.
