---
type: General-Sheet
title: Reference Chain Encoding
description: The layer below the contract shape — the spec a writer follows to encode chain edges in runbook prose
---

# Reference Chain Encoding

The layer below the
[Reference chain](/doc-types/runbook/contract-shape.md):
how chain edges are written inside runbook prose, so deterministic
code can generate every chain. This file is the spec for the writer of
that prose. The primitive map below is the join between the two
layers — one lower expression per higher primitive. The parser is
`scripts/chaingen`, which writes every chain to `doc-types/runbook/chains.txt`
and fails on drift via `--check`; everything the writer does not
need — how an edge draws, how a name resolves — lives in that code and
nowhere else.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What binds 100% is
the small grammar below, to be specified as a standard card and enforced
by a lint.

## From prose to chain

A chain edge must come out of the same sentence that commands the
executing agent — no writer maintains two copies. The **span** is how
one sentence serves both readers: braces mark the one machine-readable
unit inside otherwise plain prose. The parser slices a span at fixed
cut points — the keyword, the links, the splitters — and every word
between cuts is an opaque string it carries but never reads, so the
payload stays natural language for the agent. The two mix freely in
one sentence, and the boundary cuts both ways: unmarked prose is never
an edge — unbraced `if` is the deliberate way to keep a condition out
of the chain — and prose never restates a span; a sentence that
shadows a primitive becomes the span or is reworded away.

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

The rest of this file builds that trip up piece by piece: which
primitives come from where, and the rules for writing each span.

## The primitive map

Every higher primitive is either **derived** from the runbook's file or
**declared** in its body as a span. The primitives themselves are
declared in
[contract-shape.md](/doc-types/runbook/contract-shape.md), never
here — this map only gives each one its written form. The lexicon is
closed the same way: a new span form is an edit to this file, and its
primitive an edit to contract-shape.md, before first use.

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
| reads — launch prompt | `{Read from the launch prompt …}` |
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

## Writing the spans

A span is `{keyword payload}`: flat by default, nested at most two
deep — `If` and `Never` spend the cap. The keyword matches
case-insensitively, a span may wrap across source lines, and spans
count only outside code spans and fenced blocks. The rules for each
declared form, refining the table above:

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

  ├─does────► [/grilling] Skill
```

The link is the target; "once to sharpen the raw idea" is annotation.

**Buckets.** The keyword picks the write bucket — `Commit` is git,
`Write` is local file — unless the payload opens with `to GitHub` or
`to scratch`; `from GitHub` and `from the launch prompt` do the same
for `Read` — the latter for material the caller assigns at dispatch,
which no link can name. A `{Commit …}`
span requires a fenced git command block in the same step, and span
and block must agree.

```
{Write to scratch a self-ignoring `.datasheet/` directory}

  ├─writes──► scratch
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

  ├─writes──► the target document in place
```

"the target document in place" travels to the chain; everything after
the semicolon stays in the file.

**Prohibition.** `{Never {…}}` wraps exactly one span — inner keyword
`Write`, `Commit`, or `Merge` — and flips it from action to ban. A ban
the vocabulary cannot carry stays plain prose, recorded in the
[residual-ledger.md](/doc-types/runbook/residual-ledger.md).

```
{Never {Commit}} — leave the changes in the working tree for review.

  ├─never commits───►
```

The span is the braces alone; the prose after the dash stays outside
it.

**Reports.** `{Report …}` reports the constant `outcome: str` — a
runbook's report is prose — with the payload as annotation.

```
{Report one line: worktree and branch removed, main at that commit}

  └─reports──► outcome: str
```

The edge is `outcome: str`; the whole payload rides as annotation.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
