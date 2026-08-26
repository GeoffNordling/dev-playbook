---
type: General-Sheet
title: Edge Encoding
description: The one-to-one primitive map from Reference chain to skill prose — the ruled encodings, the holes, and the port roster
---

# Edge Encoding

The lower-level design under
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md):
machine-parseable structure inside skill and agent prose, so deterministic
code can generate the Reference chains that file defines. Same working-file
conventions as
[the branch plan](/no-more-slop-branch-working-files/NO-MORE-SLOP.md) sets
out.

Acronyms used here, defined once: CNL — Controlled Natural Language, an
engineered subset of a natural language with restricted vocabulary and
grammar so machines can parse what a reader reads. STE — ASD-STE100
Simplified Technical English, one specific CNL from aerospace, aimed at
readers rather than machines. CLOA is in the branch plan's
[terms](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#terms).

## Three readers

Every encoding decision must serve the readers below, in priority order:

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

Every higher-level primitive maps one-to-one to a lower-level
expression — `reports` in the chain is `{Report …}` in the prose, and
nothing else is. A skill is then rewritten using only the map, and
whatever prose refuses to fit is a residual, recorded at the moment of
porting in the
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md)
— a record, not a queue for rulings. During the design phase, residuals
drove the map: a valuable one amended the shared primitive structure, a
worthless one was reworded away. This is
[the EM loop](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#the-loop)
run at a lower level — still generating primitives in partnership with
the user to minimize residuals, with the skill file as the target
artifact and the map as the current abstraction set. The general rule —
the loop is the same algorithm at any layer, joined by a map written to
a stateful location — is stated in
[Layer invariance](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md#layer-invariance).
The earlier sentence-by-sentence retrofit ran the loop backwards, and
every retrofit surfaced a fresh complexity; the map runs it forwards.

## The primitive map

| Higher primitive | Lower expression | Status |
|---|---|---|
| node type + ownership | file path | **Ruled** (derived) |
| node data (`model`, `effort`, `allowed-tools`) | frontmatter, verbatim | **Ruled** (derived) |
| unit summary | frontmatter `description` | **Ruled** (derived) |
| args | frontmatter `arguments` list — name only | **Ruled** (derived) |
| reads | `{Read <one link>}` | **Ruled** |
| writes — git bucket | `{Commit …}` + fenced command | **Ruled** |
| writes — local file | `{Write <payload>}` | **Ruled** |
| writes — GitHub / scratch | — | **Hole** |
| reports | `{Report <payload>}` | **Ruled** |
| guard | `{If <condition>, {…}}` containment | **Ruled** |
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
  results): the invented `arguments:` key is inert to the harness; the
  `ARGUMENTS: <input>` append fires unchanged with it declared; and
  frontmatter is stripped from rendered content — the executing agent
  never sees the argument name, which therefore carries meaning for
  the user and the chain only. Side findings: the skills directory
  rescans live (no session restart needed), and
  `disable-model-invocation: true` blocks the Skill tool itself, not
  just spontaneous invocation. Input reaches the agent appended after
  the whole body as `ARGUMENTS: <text>`; a future complicated skill
  could reintroduce a `$ARGUMENTS` placeholder for mid-body injection
  — noted, out of scope. Ripple: the
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
  heuristic are both jobs the braces do.)
- **reads** — `{Read <payload containing exactly one link>}`. The one
  markdown link or citation in the span is the edge target; other words in
  the span are annotation. Two reads means two spans; zero or two links in
  one span fails the lint.
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
  `skills/` segment; ownership from the *resolved* path — a vendored
  skill's harness symlink resolves into `.agents/skills/`, drawing the
  chain's curly braces, while an owned skill resolves into the dotfiles
  `dot-claude` tree. One span per edge: grill-with-docs fires two, the
  /grilling session and /domain-modeling active throughout.
- **does → Script** — `{Run <payload containing exactly one link>}`,
  the same expression as does → Skill: the verb never carries the
  target type, the linked path does. A link to a `SKILL.md` is a Skill;
  a link to a script file (usage-report's `scripts/report.sh`) is a
  Script, named by its filename, in-bundle when the link is relative to
  the skill's own directory.
- **overrides** — `{Override <one link + clause words> with
  <one link + detail words>}`. The literal word `with` splits the
  payload, the way the guard's comma-after-condition does: the link
  before `with` is the overridden unit and the words around it name the
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
  reserved and capped at two deep — the guard spends it.
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
  instruction to that agent — and the code reads none of them. The
  guard's condition follows the same rule: lifted verbatim between two
  cut points, sliced, not understood.
- **The first semicolon ends the chain's view.** In any sliced payload —
  a span's annotation or a guard's condition — text after the first `;`
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
  four spaces; empty segments are dropped.
- A solid arrow pads its label to eight columns (`├─reads───►`); a
  guarded edge draws dashed (`├ ╌ reads ╌ ►`) and carries
  `if <condition>` as the rightmost segment.
- Targets render: a unit as `[name] Type` or `{name} Type`, the name
  from the resolved path (a SKILL.md's directory, an agent's or
  standard's basename, a script's filename); a non-unit read target as
  the link text verbatim (`friction/log.md`); a report as
  `outcome: str`; a local-file write as `local file`; a git write as
  `git(<repo>: <subcommands>)` — repo from `-C`, subcommands in command
  order, deduplicated.
- The node header is `[name] Type · <node data>`: the recognized
  frontmatter keys (`tools`, `model`, `effort`, `allowed-tools`)
  verbatim, in frontmatter order. The header's braces follow the same
  ownership rule as targets — a unit whose realpath resolves into
  `.agents/` renders `{name}`, so `{grilling}` heads its own chain the
  same way it appears on grill-with-docs's does edge. args edges lead;
  body edges follow in document order.
- Whitespace inside a slice collapses to single spaces — spans wrap
  across source lines.

## Proposal procedure

Every encoding proposal is presented on screen in parts, approved together
by one ruling:

1. **The target.** The Reference chain fragment being encoded, drawn in
   [CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md)
   notation — only the edges this proposal covers, nothing projected
   forward.
2. **The prose.** The exemplar's before and after — the diff that would
   land.
3. **The transform.** The planned deterministic rules, walked as a
   literal map from the after-prose to the target fragment: each source
   token on the left, the rule that fires on it, and the chain element
   it emits on the right — step by step until the whole fragment is
   rebuilt and nothing in it is unexplained. Approval certifies the
   transform; it is the contract the parser implements. Chains are
   never hand-drawn and never pasted into the terminal: the generator
   writes them all to `parser/chains.txt`, and the user reads them
   there. A chain too noisy to read is a design defect to fix in the
   rules or the prose, never in the output. Prose is written with the
   generator in mind: phrase each span so the text left after excising
   the link reads clean on the edge — no orphaned `'s`,
   `a … session`, or leading punctuation — and demote elaboration
   behind a semicolon so it stays file-only.

## Residual ledger

Per unit, what its full rewrite could not express in the map — each
entry awaiting a verdict. Lives in its own file:
[Residual Ledger](/no-more-slop-branch-working-files/RESIDUAL-LEDGER.md).

## Principles

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
- **One diff per proposal.** A proposal turn lands its full diff
  uncommitted — the unit's encoding, the map's new rows and detail
  bullets, and the ledger's new entries — so the diff against HEAD is
  the whole proposal; one ruling approves and commits it all. Commits
  run the document linters; the test-suite hook is skipped
  (`SKIP=make-check` on push). Proposals edit the live files directly.
- **Acronyms defined once**, at the top of anything we write.

## Port roster

Every unit in the live corpus (`dotfiles/dot-claude/agents/*.md` and
`skills/*/SKILL.md` — the tree `chaingen.py` scans). Checked means ported:
encoded in map language and its chain certified in `parser/chains.txt`.

A **(3P)** mark means third-party verbatim: the skill directory is a
symlink into `dotfiles/.agents/skills/`, whose bytes belong to upstream
(`.skill-lock.json` names the source — mattpocock/skills or
marimo-team/skills). These port last, after the adoption-policy Decision
Record converts them to first-class owned copies — see the port plan in
[No More Slop](/no-more-slop-branch-working-files/NO-MORE-SLOP.md).

Agents:

- [x] deslopper
- [x] adjudicator
- [x] bug-pr-review
- [x] build
- [x] code-pr-review
- [x] doc-pr-review
- [x] open-pr
- [x] set-auditor
- [x] set-deslopper

Skills:

- [x] document-deslop — Review section still unencoded (rides the branch plan's Final Quality Pass)
- [x] grill-with-docs
- [x] log-friction
- [x] usage-report
- [x] agent-view-overwatch
- [x] candidate-promote
- [x] clean-up-branch-worktree
- [ ] codebase-design (3P)
- [x] commit — the `{Commit}` span itself skipped: `git_detail()` requires `-C`, this skill targets the ambient repo (ledgered)
- [x] commit-off
- [x] compact-prep
- [x] datasheet
- [x] design
- [ ] diagnosing-bugs (3P)
- [ ] domain-modeling (3P)
- [x] enable-repo-governance
- [ ] grilling (3P)
- [x] handoff
- [x] idea
- [ ] improve-codebase-architecture (3P)
- [x] intake
- [x] issue-overwatch
- [x] issue-review-claims
- [x] issue-review-simulation
- [x] judgments-sweep
- [ ] marimo-batch (3P)
- [ ] marimo-notebook (3P)
- [x] orchestrate
- [x] pocock-sweep
- [ ] prototype (3P)
- [x] ralph-setup
- [ ] research (3P)
- [x] rewind-compact
- [x] skill-creator
- [x] update-standards-pin
- [x] user-intent-mini-interview
- [ ] wait-what (3P)
- [ ] wayfinder (3P)
- [x] wayfinder-to-build
- [ ] wizard (3P)
- [x] working-doc-set-deslop
- [ ] writing-for-agents (3P)

## To-do

The plan lives in one place: the
[branch plan's Now section](/no-more-slop-branch-working-files/NO-MORE-SLOP.md#now).
This file carries no step list of its own.
