---
type: General-Sheet
title: Encoding
description: The layer below the Reference chain — the primitive map, the grammar, and the rendering that construct chains from runbook prose
---

# Encoding

The layer below
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md):
machine-parseable structure inside runbook prose, so deterministic code
can generate every chain. The primitive map below is the join between
the two layers — one lower expression per higher primitive. The parser
that implements it is `parser/chaingen.py`, which writes every chain to
`parser/chains.txt` and fails on drift via `--check`. Same working-file
conventions as the branch plan sets out.

Inspiration only: doctest (fenced blocks inside prose are legitimate
deterministic parse targets) and CNL (constrain the sentence, never embed
notation). STE is loose style inspiration, unenforced. What we adopt 100%
is our own small grammar below, to be specified as a standard card and
enforced by our lint.

## The primitive map

| Higher primitive | Lower expression | Status |
|---|---|---|
| node type | file path | **Ruled** (derived) |
| node data (`model`, `effort`, `allowed-tools`, `disallowed-tools`) | frontmatter, verbatim | **Ruled** (derived) |
| runbook summary | frontmatter `description` | **Ruled** (derived) |
| args | frontmatter `arguments` list — name only | **Ruled** (derived) |
| reads | `{Read <one link>}` | **Ruled** |
| reads — GitHub | `{Read from GitHub <payload>}` | **Ruled** |
| writes — git bucket | `{Commit …}` + fenced command | **Ruled** |
| writes — local file | `{Write <payload>}` | **Ruled** |
| writes — GitHub | `{Write to GitHub <payload>}` | **Ruled** |
| writes — scratch | `{Write to scratch <payload>}` | **Ruled** |
| reports | `{Report <payload>}` | **Ruled** |
| condition | `{If <condition>, {…}}` containment | **Ruled** |
| prohibition | `{Never {<primitive> …}}` | **Ruled** |
| does → Agent | `{Launch <one link>}` | **Ruled** |
| does → Skill | `{Run <one link>}` | **Ruled** |
| does → Script | `{Run <one link>}` | **Ruled** |
| overrides … with … | `{Override <link> with <link>}` | **Ruled** |

The ruled rows, in detail:

- **args** — fully derived from a frontmatter field this design
  declares: `arguments: [friction]` names the edge and its argument;
  the chain shows the name alone. No type (`$ARGUMENTS` is text substitution, so
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
  grab one word — so free-text skills must not use them. Verified live
  (2026-08-25, probe skill, headless and subagent contexts, byte-identical
  results): the `arguments:` key is inert to the harness; the
  `ARGUMENTS: <input>` append fires unchanged with it declared; and
  frontmatter is stripped from rendered content — the executing agent
  never sees the argument name, which therefore carries meaning for
  the user and the chain only. Side findings: the skills directory
  rescans live (no session restart needed), and
  `disable-model-invocation: true` blocks the Skill tool itself, not
  just spontaneous invocation. Input reaches the agent appended after
  the whole body as `ARGUMENTS: <text>`; a future complicated skill
  could reintroduce a `$ARGUMENTS` placeholder for mid-body injection
  — noted, out of scope. Ripple, since landed:
  [runbook-conventions.md](/standards/harness/runbook-conventions.md)
  declares `arguments` and `scripts/harness-files-lint` enforces its shape
  (`harness.arguments-format`), while the `## Name: $ARGUMENTS` heading
  convention and `argument-hint` are retired — an unknown field now.
- **condition** — `{If <condition>, {edge span} …}`: the condition nests
  the span(s) it gates, so binding is containment, never sentence
  adjacency. The text between the keyword `if` and the first nested
  span is the condition, lifted verbatim (trailing comma dropped);
  every nested span fires under that condition and draws dashed; prose
  in the body ("and stop") stays uncoded. This spends the two-deep
  nesting cap — condition at depth one, edges at depth two, never deeper.
  A span nested nowhere is unconditional (solid). Unbraced `if` stays
  plain prose and fires nothing. (Supersedes `{only where …}` and the
  same-sentence adjacency rule: the distinctive phrase and the
  heuristic are both jobs the braces do.)
- **prohibition** — `{Never {<primitive> …}}`: the modifier wraps exactly
  one ordinary primitive span, the way the condition nests its edges, and
  flips it from assertion to prohibition — a named action this run must
  not take. The inner keyword must be `Write`, `Commit`, or `Merge`
  (`merge` exists only here — no assertion site uses it), extended only
  when a site demands another verb; out-of-vocabulary bans ("ask no
  questions") stay prose, ledgered. The inner payload's kernel is the
  edge's target, verbatim and possibly empty: bare `{Never {Commit}}`
  draws a bare-arrow `never commits` edge, and a write ban's sub-level
  rides the payload — bare `{Never {Write}}` bans local writes,
  `{Never {Write to GitHub}}` the GitHub side. The label keeps the inner
  keyword's own verb (`never commits`, not the assertion fold to
  `writes`) since no git block exists to disambiguate. Spends the
  nesting cap like the condition, so a prohibition cannot sit inside
  one — unsupported for now, wanted eventually. Unrelated to
  `disallowed-tools`, which is node data: the frontmatter claim is
  believed as stated, never checked against harness enforcement.
- **reads** — `{Read <payload containing exactly one link>}`. The one
  markdown link or citation in the span is the edge target; other words in
  the span are annotation. Two reads means two spans; zero or two links in
  one span fails the lint. A `#fragment` on the target names a section:
  the parser splits it off as a `§ fragment` annotation on the edge, and
  fails the lint unless the fragment matches a heading slug in the target
  file (the same applies to Launch and Run targets). A linkless Read may
  instead carry exactly one inline-code target — a file in the invoking
  repo, named per the cross-reference standard's varied-location row
  (`` {Read `CONTEXT.md` …} ``) — which becomes the node verbatim,
  backticks kept, with no on-disk resolution.
- **reads, GitHub** — `{Read from GitHub <payload>}`. The fixed prefix
  `from GitHub` opens the payload and is the whole address — no link, and
  a link in the span fails the lint. The node is `GitHub`; the payload
  kernel after the prefix is annotation (`{Read from GitHub the PR's
  existing threads}`). Covers every `gh` state read — issue bodies, PR
  threads, diffs — that has no on-disk file to link.
- **writes, git bucket** — `{Commit …}` declares the edge; the fenced
  command block in the same step supplies the machine detail — repo from
  `-C`, operations from the git subcommands. The lint requires the block
  and fails span/block disagreement.
- **writes, local file** — `{Write <payload>}`. The keyword picks the
  bucket: Commit → git, Write → local file. The payload is wholly
  opaque — the write target is usually runtime-bound (deslopper's
  arrives in the launching prompt), so no link is required and none is
  interpreted; the chain draws `local file` with the payload verbatim
  as annotation. The hand-drawn parenthetical contents
  (`local file(PLAN.md, PROGRESS.md)`) are not generatable.
- **writes, GitHub / scratch** — `{Write to GitHub <payload>}` /
  `{Write to scratch <payload>}`. A fixed bucket prefix opening the
  payload picks the node — `GitHub` for `gh` writes (issues, PR threads,
  labels, comments), `scratch` for OS-temp and dot-directory scratch
  files — and the kernel after the prefix is annotation. A payload
  opening with neither prefix stays the local-file bucket. The same
  prefixes serve the prohibition side, so `{Never {Write to GitHub}}`
  draws the same `GitHub` node.
- **does → Agent** — `{Launch <payload containing exactly one link>}`.
  The link is the agent definition file at its live harness path
  (document-deslop links `~/.claude/agents/deslopper.md`); the target's
  node type derives from the path's `agents/` segment, and its node data
  (model, effort, tools) comes from that file's own frontmatter, stitched
  by following the edge — the skill restates none of it. The lexicon
  gains Launch → does. Non-link payload words are annotation, same as
  reads; document-deslop's `model: sonnet` pin rides there as a
  launch-time instruction. Supersedes the
  `(Agent tool, subagent_type: …)` parenthetical: the keyword carries
  the mechanism, the link carries the target.
- **does → Skill** — `{Run <payload containing exactly one link>}`.
  Same shape as does → Agent with the verb natural to skills; the
  lexicon gains Run → does. The link is the live harness path
  (`~/.claude/skills/grilling/SKILL.md`); node type from the path's
  `skills/` segment. One span per edge: intake's interview beat
  fires two, the /grilling session and /domain-modeling active
  throughout.
- **does → Script** — `{Run <payload containing exactly one link>}`,
  the same expression as does → Skill: the verb never carries the
  target type, the linked path does. A link to a `SKILL.md` is a Skill;
  a link to a script file is a Script, named by its filename, in-bundle
  when the link is relative to the skill's own directory. A script is
  recognized by a `scripts/` path segment (the rule that types agents by
  `agents/`, covering extensionless entry points like `repo-lint` and
  `judgments-run`) or by a `.sh`/`.py`/`.bash` extension.
- **overrides** — `{Override <one link + clause words> with
  <one link + detail words>}`. The literal word `with` splits the
  payload, the way the condition's trailing comma does: the link
  before `with` is the overridden runbook and the words around it name the
  clause; the link after `with` is the replacement, and the words after
  it carry the operative detail. Exactly two links, one per side, or
  the lint fails.
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
  reserved and capped at two deep — the condition spends it.
- **Delimiter.** `{…}` is the delimiter: the skill corpus is nearly free of
  braces outside code spans, angle brackets are the workspace's placeholder
  convention (`<issue>`, `<repo>`), and a space-free `<tag>` vanishes in
  rendered HTML. A collision alone never vetoes a choice.
- **The parser slices, never interprets.** Inside a span, deterministic
  code touches only fixed cut points: the keyword, the markdown
  link(s), the `with` splitter, nested braces, and the first semicolon.
  Every word between cut points is an opaque verbatim string —
  annotation, carried for display or dropped, never parsed and never
  load-bearing. In
  `{Run a [/grilling](…) session}`, "a" and "session" are glue for the
  executing agent; "throughout" in the sibling span is a real
  instruction to that agent — and the code reads none of them. A
  condition follows the same rule: lifted verbatim between two
  cut points, sliced, not understood.
- **The first semicolon ends the chain's view.** In any sliced payload —
  a span's annotation or a condition — text after the first `;`
  is file-only elaboration; the kernel before it travels to the chain.
  Writers keep chains readable by fronting the kernel: deslopper's
  `{Write the target document in place; it must say the same things …}`
  puts "the target document in place" on the edge and the rest in the
  file only. No semicolon means the whole slice travels.
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

## Chain rendering

The display conventions the generator implements — pinned by
`parser/chaingen.py`, which reproduces every certified emission
byte-for-byte:

- An edge line is arrow, target, annotation, condition, separated by
  four spaces; empty segments are dropped. A total prohibition
  (`└─never commits─►`) drops every segment and ends at the bare arrow.
- A solid arrow pads its label to eight columns (`├─reads───►`); a
  conditional edge draws dashed (`├ ╌ reads ╌ ►`) and carries
  `if <condition>` as the rightmost segment.
- Targets render: a runbook as `[name] Type`, the name
  from the resolved path (a SKILL.md's directory, an agent's or
  standard's basename, a script's filename); a non-runbook read target as
  the link text verbatim (`friction/log.md`); a report as
  `outcome: str`; a local-file write as `local file`; a GitHub read or
  write as `GitHub` and a scratch write as `scratch`; a git write as
  `git(<repo>: <subcommands>)` — repo from `-C`, subcommands in command
  order, deduplicated.
- The node header is `[name] Type · <node data>`: the recognized
  frontmatter keys (`tools`, `model`, `effort`, `allowed-tools`,
  `disallowed-tools`) verbatim, in frontmatter order. args edges lead;
  body edges follow in document order.
- Whitespace inside a slice collapses to single spaces — spans wrap
  across source lines.

## Encoding rules

- **Skills are programs.** No narrative intro; the body is instructions,
  as if it were a program. The one-sentence summary lives in the
  frontmatter `description`, whose meaning we may redefine as needed.
- **No shadow prose.** Prose that restates a primitive must either become
  the marked edge or be reworded away. log-friction's deleted intro
  ("Append one entry … and commit it") was the ruling case.
- **Declared versus derived.** Node type derives from path; node data
  (`model`, `effort`, `allowed-tools`, `disallowed-tools`)
  from frontmatter; the
  summary from `description`; args from the frontmatter `arguments`
  list. Edges, conditions, and reports are
  declared inline. No file describes another file's behavior — subtrees
  are stitched by following does-edges into the target file's own
  declarations.

## Acronyms

- **CNL** — Controlled Natural Language: an engineered subset of a
  natural language with restricted vocabulary and grammar so machines
  can parse what a reader reads.
- **STE** — ASD-STE100 Simplified Technical English: one specific CNL
  from aerospace, aimed at readers rather than machines.
