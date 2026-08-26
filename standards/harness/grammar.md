---
type: Standard
title: Instruction Grammar
description: The braced-span grammar and its ontology — the node kinds, the edge vocabulary, and the closed keyword lexicon that make skill and agent bodies machine-readable
---

# Instruction Grammar

Governs the bodies of the two files that define **runbooks**: skill bodies
(`SKILL.md`) and agent definitions (`agents/*.md`). No other file in
[the harness-file registry](/standards/harness/files.md) carries this
grammar — `CLAUDE.md`, rules, settings, and hooks are context and
configuration, not runbooks, and a braced span in them means nothing.

A **runbook** is documentation that acts: invoked by name, arguments in, a
report out, effects on state. Its body stays natural imperative English
for the executing agent; the grammar adds the minimum structure that
deterministic code can parse, so tooling reconstructs the runbook's
**Reference chain** — the declared tree of what it does, reads, and
writes, plus its call signature — without a model in the loop.

The grammar serves three readers, in priority order: the executing agent
(the prose commands it; nothing may clutter that), the user (who reads
the file as plain English), and deterministic code (served by the
braces, never by machine notation embedded in prose).

## Node kinds

Every chain node is typed by kind:

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

## Edges

A runbook declares its behavior as edges. **Edges live at the definition
site**: an edge belongs to the file whose text contains the instruction,
and a chain is stitched by following does-edges into each target file's
own declarations — no file describes another file's behavior.

- **does** — run a behavior some documentation defines: a Standard's
  verb where one exists (the deslopper agent does the prose standard's
  enforcement), the whole runbook where the doc is the definition
  (grill-with-docs does grilling).
- **reads** — consulted, not run.
- **writes** — produce or mutate state outside the chain, typed by
  bucket: `git` or `local file`.
- **overrides … with …** — substitute a clause of another runbook's
  instructions at runtime, leaving its file untouched.
- **args** — the values the caller hands in at invocation; each is a
  string, and each dies with the call.
- **reports** — the value handed back to the caller; unlike a write, a
  report never lands in state. A report is `outcome: str` — a runbook's
  report to its caller is prose.

Any edge may carry a **condition**: the circumstance under which it
fires. A conditional edge is still the same edge — the condition changes
when it fires, never what it is.

## The braced span

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

Keywords are imperative commands to the executing agent; the chain's
edge labels are their third-person forms. Per keyword:

- **Read.** The one link in the payload is the edge target; every other
  word is annotation. Two reads means two spans; zero or two links in
  one span is an error.
- **Write.** The local-file bucket. The payload is wholly opaque — the
  target is usually runtime-bound (the deslopper's arrives in its
  launching prompt) — so no link is required and none is interpreted.
- **Commit.** The git bucket. The span declares the edge; the fenced
  command block in the same step supplies the machine detail — the repo
  from `-C`, the operations from the git subcommands. A span without its
  block, or a block that disagrees with its span, is an error.
- **Report.** The payload is the report's content, verbatim —
  log-friction ends with `{Report one line with the entry's short name,
  and that the push landed}`.
- **Launch.** The link is the agent definition at its live harness
  path — document-deslop launches
  `[deslopper](~/.claude/agents/deslopper.md)`. The target's model,
  effort, and tools come from that file's own frontmatter; the launching
  runbook restates none of them. Non-link words are annotation and ride the
  edge — document-deslop's `model: sonnet` pin travels there as a
  launch-time instruction.
- **Run.** The same shape, with the verb natural to skills and scripts.
  The link, never the verb, decides the target's kind: a `SKILL.md` is a
  Skill, a script file is a Script — usage-report runs its bundled
  `scripts/report.sh`.
- **Override.** The literal word `with` splits the payload: the link
  before it is the overridden runbook and the words around it name the
  clause; the link after it is the replacement, and the words after it
  carry the operative detail. Exactly one link per side. grill-with-docs
  overrides /domain-modeling's "ADR" clause with the workspace's
  Decision Record conventions.
- **If.** The condition, and the only span that nests. The text between
  the keyword and the first nested span is the condition, lifted
  verbatim (a trailing comma is dropped); every nested span fires only
  under it — log-friction's `{If there is something to record, {commit
  and push}}`. Nesting is capped at two deep, and the condition spends
  it: condition at depth one, edges at depth two, never deeper.

## Slicing, never interpreting

Deterministic code touches only fixed cut points: the keyword, the
markdown link(s), the `with` splitter, nested braces, and the first
semicolon. Every word between cut points is opaque annotation — a real
instruction to the executing agent, carried verbatim for display, never
parsed and never load-bearing to code. In
`{Run a [/grilling](~/.claude/skills/grilling/SKILL.md) session}`, "a"
and "session" are glue the code does not read.

- **The first semicolon ends the chain's view.** In any sliced payload,
  text after the first `;` is file-only elaboration; the kernel before
  it travels to the chain. Front the kernel: the deslopper's
  `{Write the target document in place; it must say the same things …}`
  puts "the target document in place" on the edge and the rest in the
  file only.
- **Code contexts are inert.** Spans count only outside code spans and
  fenced blocks.
- **Unmarked prose is never an edge.** The brace declares; the parser
  infers nothing. An unbraced "if" is the deliberate tier for
  conditional logic left off the chain — log-friction's "carrying a
  proposed fix if the user gave one" fires nothing.

## Declared and derived

No fact is stated twice. Everything the chain shows either derives from
structure the file already has or is declared exactly once:

| Fact | Source |
|---|---|
| Node kind | the file's path |
| Node data | frontmatter `model`, `effort`, `tools`, `allowed-tools`, verbatim |
| Runbook summary | frontmatter `description` |
| args | frontmatter `arguments` list |
| Edges, conditions, reports | braced spans in the body |

## The `arguments` key

A runbook that takes input declares each argument by name in its
frontmatter:

```yaml
arguments: [friction]
```

Names only, kebab-case, and the name must carry the meaning — invocation
input is text substitution, so every argument is a string and a type
would distinguish nothing. The body carries no placeholder
(`$ARGUMENTS`, `$0`): the harness appends the invocation input after the
body as `ARGUMENTS: <text>`, whole and unsplit, and the executing agent
never sees the argument's name — the name carries meaning for the user
and the chain. A multi-argument runbook lists more names:
`arguments: [idea, map, ticket]`.

## The vocabulary is closed

The eight keywords are the whole lexicon, and the forms above are the
whole grammar. A new keyword, write bucket, or span form requires an
edit here before its first use.
