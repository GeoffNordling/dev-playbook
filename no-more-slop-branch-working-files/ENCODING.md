---
type: General-Sheet
title: Encoding
description: The layer below the Reference chain — the spec a writer follows to encode chain edges in runbook prose
---

# Encoding

The layer below
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md):
how chain edges are written inside runbook prose, so deterministic
code can generate every chain. This file is the spec for the writer of
that prose. The primitive map below is the join between the two
layers — one lower expression per higher primitive. The parser is
`parser/chaingen.py`, which writes every chain to `parser/chains.txt`
and fails on drift via `--check`. Same working-file conventions as the
branch plan sets out.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What we adopt 100%
is our own small grammar below, to be specified as a standard card and
enforced by our lint.

## The primitive map

Every higher primitive is either **derived** from the runbook's file or
**declared** in its body as a braced span.

The derived primitives:

| Primitive | Source | Detail |
| --------- | ------ | ------ |
| node type | the file path | `agents/` is an Agent, `SKILL.md` a Skill, `scripts/` or a script extension a Script |
| node data | frontmatter, verbatim | — |
| runbook summary | frontmatter `description` | — |
| args | frontmatter `arguments` list | names only — the name carries the meaning; no placeholder in the body |

The declared primitives:

| Primitive | Span |
| --------- | ---- |
| reads | `{Read <one link>}` |
| reads — GitHub | `{Read from GitHub …}` |
| writes — local file | `{Write …}` |
| writes — GitHub | `{Write to GitHub …}` |
| writes — scratch | `{Write to scratch …}` |
| writes — git | `{Commit …}` + fenced command |
| does — Agent | `{Launch <one link>}` |
| does — Skill or Script | `{Run <one link>}` |
| overrides … with … | `{Override <link> … with <link> …}` |
| reports | `{Report …}` |
| condition | `{If <condition>, {…}}` |
| prohibition | `{Never {…}}` |

Keywords are imperative — commands to the executing agent; the chain's
edge labels are their third-person translation.

Two live uses. In each, the span is the prose as it stands in the
runbook file, and the edge below it is what the deterministic parser
generates from that span. A simple read, from intake:

```
{Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md);
the brief formats, brief principles, and the readiness bar}

  ├─reads───► [issue-authoring] Standard
```

A condition nesting a read, from design:

```
{If §2 settled that the public surface is load-bearing,
{Read [design-it-twice.md](references/design-it-twice.md)} and work through it}

  ├ ╌ reads ╌ ► design-it-twice.md    if §2 settled that the public surface is load-bearing
```

## The span

A span is `{keyword payload}`: flat by default, nested at most two
deep — `If` and `Never` spend the cap. The keyword matches
case-insensitively, and a span may wrap across source lines. Spans
count only outside code spans and fenced blocks, and unmarked prose is
never an edge — unbraced `if` is the deliberate way to keep a
condition out of the chain.

**Targets.** Where the table says `<one link>`, exactly one markdown
link in the payload names the target; every other word is annotation —
instruction to the executing agent, never read by the parser. One
target per span: two reads are two spans. A does-link points at the
live harness path (`~/.claude/skills/…`, `~/.claude/agents/…`). A
`#fragment` on any link must match a heading in the target file. A
linkless `{Read}` may instead carry one inline-code target
(`` {Read `CONTEXT.md` …} ``), taken verbatim.

```
{Run [/grilling](~/.claude/skills/grilling/SKILL.md) once to sharpen the raw idea}
```

The link is the target; "once to sharpen the raw idea" is annotation.

**Buckets.** The keyword picks the write bucket — `Commit` is git,
`Write` is local file — unless the payload opens with `to GitHub` or
`to scratch`; `from GitHub` does the same for `Read`. A `{Commit …}`
span requires a fenced git command block in the same step, and span
and block must agree.

```
{Write to scratch a self-ignoring `.datasheet/` directory}
```

The `to scratch` prefix picks the bucket; bare `{Write …}` would be
the local-file bucket.

**Splitters.** In `{If <condition>, {…}}`, the text before the first
nested span is the condition, lifted verbatim; every nested span fires
under it. In `{Override … with …}`, the word `with` splits the
payload — one link on each side, the overridden clause before, the
replacement after. In every payload, the first `;` ends what travels
to the chain: front the kernel, elaborate after the semicolon.

```
{Write the target document in place; it must say the same things
without committing any of the named tics}
```

"the target document in place" travels to the chain; everything after
the semicolon stays in the file.

**Prohibition.** `{Never {…}}` wraps exactly one span — inner keyword
`Write`, `Commit`, or `Merge` — and flips it from action to ban. A ban
the vocabulary cannot carry stays plain prose, recorded in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

```
{Never {Commit}} — leave the changes in the working tree for review.
```

The span is the braces alone; the prose after the dash stays outside
it.

**Reports.** `{Report …}` reports the constant `outcome: str` — a
runbook's report is prose — with the payload as annotation.

```
{Report one line: worktree and branch removed, main at that commit}
```

The edge is `outcome: str`; the whole payload rides as annotation.

## The prose

The spans sit inside ordinary runbook prose, which follows three
rules. Skills are programs: no narrative intro, the body is
instructions, and the one-sentence summary lives in the frontmatter
`description`. No shadow prose: a sentence that restates a primitive
either becomes the marked span or is reworded away. No file describes
another file's behavior: node data and subtrees come from the target's
own file, stitched by following does-edges.

## The code

The parser slices, never interprets: it cuts each span at fixed
points — the keyword, the links, the splitters — and every word
between cuts is an opaque string. All else — how an edge draws, how a
name resolves, how whitespace collapses — belongs to the generator
alone: `parser/chaingen.py` is the ruling, `parser/chains.txt` is the
reference drawing, and `--check` holds them to zero drift.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
