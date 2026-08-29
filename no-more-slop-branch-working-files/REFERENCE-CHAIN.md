---
type: General-Sheet
title: Reference Chain
description: The one-to-one primitive map from Reference chain to skill prose — the ruled encodings, the holes, and the port roster
---

# Reference Chain

The lower-level design under
[CLOA Abstractions](/no-more-slop-branch-working-files/CLOA-ABSTRACTIONS.md):
machine-parseable structure inside skill and agent prose, so deterministic
code can generate the Reference chains that file defines. Same working-file
conventions as the branch plan sets out.

Acronyms used here, defined once: CNL — Controlled Natural Language, an
engineered subset of a natural language with restricted vocabulary and
grammar so machines can parse what a reader reads. STE — ASD-STE100
Simplified Technical English, one specific CNL from aerospace, aimed at
readers rather than machines. CLOA is in the branch plan's terms.

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

## Abstractions so far

| Noun            | Verbs                         | Is                                                |
| --------------- | ------------------------------ | ------------------------------------------------- |
| Standard        | define, audit, enforce, adopt | A rule the workspace runs under                   |
| Agent           | do                            | Documentation that runs in a fresh context, on its own permission set |
| Skill           | do                            | Documentation that runs in the calling context, on its permissions |
| Script          | do                            | Deterministic code run via the shell — not a direct LLM call |
| Reference chain | edges: does, reads, overrides, writes, args, reports | The declared tree of a runbook's behavior and its call signature — args in, reports out |

- **Standard** is established and live; its open problem is the two-level
  split under [A noun with one or more verbs](#a-noun-with-one-or-more-verbs).
- **Agent and Skill** get one verb, **do**, and no more. Specificity
  comes from the behavior being done, which documentation defines — a
  Standard's verb where one exists (the deslopper does slop-tics.enforce),
  the whole runbook where the doc is the definition (grill-with-docs does
  grilling). The two differ in context binding: an agent runs in a fresh
  context window, a skill in the calling one — an in-process call versus a
  subprocess. A fresh context starts from configuration (the preset
  preload, whose contents are not modeled, the way a call graph does not
  model env vars); a skill starts from here. Permissions ride on the node:
  an agent carries its own set, a skill the calling context's, minus any
  clamp its frontmatter declares. Declared permissions are assumed to take
  effect; harness enforcement fidelity is out of scope. The steps inside a
  skill are that skill's program, file-level detail below the CLOA, never
  an interface.
- **Script** is deterministic code, done with the one verb **do**
  (usage-report's bundled `report.sh`, the repro loop diagnosing-bugs
  copies from its template). Running a script is a does-edge to a
  Script node — marked in-bundle when it ships inside the skill's
  directory — and the script's own reads and writes hang under that
  node. The zoom rule collapses in-bundle documents, never an executed
  script. A sibling **Workflow** noun (deterministic orchestration in
  Claude Code's dynamic-workflow runtime) was dropped 2026-08-25 as
  empirically vacuous: no recorded chain fires a
  does-edge into one — ralph-setup, the closest, reports the
  ralph-loop launch command as a string and never runs it. The noun
  returns if a runbook ever does a workflow.

### Reference chain

A **runbook** is one documentation file, or an abstract object that functions
like one, the way a skill functions like its SKILL.md. Every chain node is
a runbook; the nouns in the table are its types.

The chain's origin: a skill is a command — invoked by name, args in,
reports out, effects on state — and a command's caller is owed a
signature. The Reference chain is that signature written down; an
agent differs only in context binding, so it shares the shape. The
chain carries the order the runbook fires its operations in — not with
full fidelity, because the chain is a collapse of the runbook's program,
and the fine-grained sequencing it drops stays below the CLOA.

Notation: `[x]` self-owned, `{x}` vendored. The edges:

- **does** — run a behavior some documentation defines: a Standard's verb
  where one exists, the whole runbook where the doc is the definition.
- **reads** — consulted, not run.
- **overrides … with …** — substitute a clause in a runbook that cannot be
  edited.
- **writes** — produce or mutate state outside the chain. Write targets
  are typed `bucket(refinement)`: a fixed coarse bucket — git, GitHub,
  local file, local cache, scratch — plus an optional free refinement,
  as in `git(branch)` or `local cache(SQLite)`. The bucket list stays
  fixed and lintable; the refinement is a memory aid, never a new type.
  Targets may re-enter the graph as read sources: design writes the
  brief that build later reads. Scratch writes carry no filenames.
  The refinement stays machine-readable: a comma-separated sequence of
  operations — `git(commit, push)` — never prose and never `+`. A
  target in another repo carries that repo as the refinement's head, so
  crossing a repo boundary is always visible in a write. How the
  generator draws it is in
  [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md#chain-rendering).
- **args** — the value the caller hands in at invocation. Declared by
  name alone: the harness substitutes text, so every arg is a string,
  and a type that applies all the time distinguishes nothing —
  remembered, not encoded. Never lands in state, dies with the call.
  Where the name is declared, and what the harness does and does not
  do with it, is ruled in
  [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md#the-primitive-map).
- **reports** — hand a value back to the caller, user and agent alike:
  ralph-setup reports a launch command to the user, bump-pins reports
  its status enum to update-standards-pin. Unlike a write, a report never
  lands in state — it dies with the call. Unlike args, reports are
  typed as well as named, `report_name: report_type` — a report's type
  varies, so it carries information — commit reports
  `outcome: str` — and an enumerable status is preferred, its values
  listed as a small enum. A reporting runbook declares its report in its
  own file, so the primitive view renders the declaration instead of a
  model regenerating it; the declaration format is ruled in
  [Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md#the-primitive-map).
  The label is the bare third-person form of the skill-prose keyword
  `Report`, so translation adds an `s` and never swaps a word.

Any edge may carry a **guard** — the condition under which it fires. A
guarded edge draws dashed and carries its condition; an unguarded edge
draws solid, and its trailing text is mere annotation. A call inside an
`if` is still a call edge; the condition never changes the edge's type.
The drawn form is in
[Reference Chain](/no-more-slop-branch-working-files/REFERENCE-CHAIN.md#chain-rendering).

Its rules:

- **Nodes are typed** by kind (Standard, Agent, Skill, Script) and by
  ownership — self-owned or vendored. Ownership is a color, not an edge.
  A node may also carry its permission expression and model pin as node
  data, quoted verbatim in the harness's own syntax —
  `allowed-tools: Bash(git *)`, `model: sonnet`, `effort: low` — never
  paraphrased into prose.
- **Edges live at the definition site.** An edge belongs to the document
  whose text contains the instruction — greppable, so the assignment is
  lintable. A root's effects are the union of edges reachable along its
  does-path — the same rule as code, where a write belongs to the frame
  whose source contains the statement.
- **Tree, then graph.** Each runbook declares its own tree; the union across
  roots is the repo graph, where in-degree, hubs, and orphans appear. The
  code parallel is import-linter: a declared dependency contract that
  fails when reality disagrees. A lint-design candidate to evaluate when
  the checker is built: the ontology-guardrails idea
  (`~/workspace/mission-control/ideas/ontology-guardrails.md`) — declared
  rules enforced by a solver.

The chain absorbs skills as signatures, OKF traces, and the OKF graph —
one object, several angles.

Remembered, not primitives:

- **Zoom.** A runbook collapses its internal files (containment is derivable
  from paths — `design/references/` sits under `design/`); zoomed in, they
  appear as nodes inside the runbook boundary with ordinary edges.
- **Doc type.** A read target's frontmatter type (Guide, General-Sheet)
  is noted informally; a type earns a noun only when it demonstrates a
  verb interface, the way Standard did.

### Accepted residuals

The ledger of residuals ruled on and accepted as-is, one line each, so
no run raises the same question twice. A construct listed here is real
but deliberately outside the ontology until a ruling is reversed.

- **Reality probes** — direct shell contact with repo state ("run the
  gate", "confirm the git tree is clean"). A real operation; ruled not
  accounted.
- **Attestation checkpoints** — "report `READ: x`, proceed only after."
  A prompt device that raises the probability the read happens; ruled
  not accounted.
- **Agent-held ephemeral state** — counts and set-aside lists a runbook
  tracks only in its own working memory, persisted nowhere
  (judgments-sweep's fix-attempt cap and skip list); ruled not
  accounted.
- **User interview loops** — a mid-run, multi-round dialogue with the
  user (runbook-creator's "iterate until the user is satisfied";
  grilling's whole body). Conversing is what running in the calling
  context means; ruled not accounted.
- **Behavior-mode setting** — a runbook whose body installs standing
  behavior in the session's ephemeral context and fires no edge at
  invocation (orchestrate: "everything below you is a subagent").
  Ruled residual; admitting it later requires a lintable,
  deterministic form.
- **Vendored platform manifests** — the `agents/openai.yaml` display
  card every vendored bundle ships for another agent platform; bundle
  furniture, referenced by nothing, never an edge.
- **Presentation gestures** — opening an already-written artifact for
  the user (improve-codebase-architecture's `xdg-open` on its report);
  part of reporting the value, never an edge; ruled not accounted.
- **Phase gates** — a step-scoped prohibition inside a runbook's own
  program, lifted by a later step (improve-codebase-architecture's "Do
  NOT propose interfaces yet"); internal sequencing below the CLOA,
  already covered by the steps-are-the-program rule; ruled not
  accounted.
- **Written-artifact semantics** — the schema and state rules of a
  document a runbook writes and later re-reads: wayfinder's map-body
  sections, fog lifecycle, HITL/AFK axis, claim-by-assignment, ticket
  sizing. The artifact's contract lives in the artifact; the chain
  records only the writes and reads that touch it.

## The primitive map

| Higher primitive | Lower expression | Status |
|---|---|---|
| node type + ownership | file path | **Ruled** (derived) |
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
| guard | `{If <condition>, {…}}` containment | **Ruled** |
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
- **prohibition** — `{Never {<primitive> …}}`: the modifier wraps exactly
  one ordinary primitive span, the way the guard nests its edges, and
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
  nesting cap like the guard, so a prohibition cannot sit inside a
  condition — unsupported for now, wanted eventually. Unrelated to
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
  `skills/` segment; ownership from the *resolved* path — every skill
  now resolves into the dotfiles `dot-claude` tree and draws square
  brackets (the curly vendored form retired with verbatim adoption,
  Decision Record 0025). One span per edge: intake's interview beat
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
  payload, the way the guard's comma-after-condition does: the link
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
  four spaces; empty segments are dropped. A total prohibition
  (`└─never commits─►`) drops every segment and ends at the bare arrow.
- A solid arrow pads its label to eight columns (`├─reads───►`); a
  guarded edge draws dashed (`├ ╌ reads ╌ ►`) and carries
  `if <condition>` as the rightmost segment.
- Targets render: a runbook as `[name] Type` or `{name} Type`, the name
  from the resolved path (a SKILL.md's directory, an agent's or
  standard's basename, a script's filename); a non-runbook read target as
  the link text verbatim (`friction/log.md`); a report as
  `outcome: str`; a local-file write as `local file`; a GitHub read or
  write as `GitHub` and a scratch write as `scratch`; a git write as
  `git(<repo>: <subcommands>)` — repo from `-C`, subcommands in command
  order, deduplicated.
- The node header is `[name] Type · <node data>`: the recognized
  frontmatter keys (`tools`, `model`, `effort`, `allowed-tools`,
  `disallowed-tools`) verbatim, in frontmatter order. The header's brackets follow the same
  ownership rule as targets — the generator still knows the curly
  vendored form, but with no vendored runbook left every header and
  target renders `[name]`. args edges lead; body edges follow in
  document order.
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

Per runbook, what its full rewrite could not express in the map — each
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
  node data (`model`, `effort`, `allowed-tools`, `disallowed-tools`)
  from frontmatter; the
  summary from `description`; args from the frontmatter `arguments`
  list. Edges, guards, and reports are
  declared inline. No file describes another file's behavior — subtrees
  are stitched by following does-edges into the target file's own
  declarations.
- **One diff per proposal.** A proposal turn lands its full diff
  uncommitted — the runbook's encoding, the map's new rows and detail
  bullets, and the ledger's new entries — so the diff against HEAD is
  the whole proposal; one ruling approves and commits it all. Commits
  run the full gate, unaided. Proposals edit the live files directly.
- **Acronyms defined once**, at the top of anything we write.

## Port roster

Every runbook in the live corpus (`dotfiles/dot-claude/agents/*.md` and
`skills/*/SKILL.md` — the tree `chaingen.py` scans). Checked means ported:
encoded in map language and its chain certified in `parser/chains.txt`.

A **(3P)** mark means the skill arrived as a third-party copy at Decision
Record 0025, which retired verbatim adoption and converted the vendored
installs to owned bundles (`wizard`, `marimo-batch`, and `marimo-notebook`
were deleted instead). Owned, the ten port the same way as everything
else; the mark records provenance only.

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
- [x] log-friction
- [x] usage-report
- [x] agent-view-overwatch
- [x] candidate-promote
- [x] clean-up-branch-worktree
- [x] commit — the `{Commit}` span itself skipped: `git_detail()` requires `-C`, this skill targets the ambient repo (ledgered)
- [x] commit-off
- [x] compact-prep
- [x] datasheet
- [x] design
- [x] diagnosing-bugs (3P)
- [x] domain-modeling (3P)
- [x] enable-repo-governance
- [x] grilling (3P)
- [x] handoff
- [x] idea
- [x] improve-codebase-architecture (3P)
- [x] intake
- [x] issue-overwatch
- [x] issue-review-claims
- [x] issue-review-simulation
- [x] judgments-sweep
- [x] orchestrate
- [x] prototype (3P)
- [x] ralph-setup
- [x] research (3P)
- [x] rewind-compact
- [x] runbook-creator
- [x] update-standards-pin
- [x] user-intent-mini-interview
- [x] wait-what (3P)
- [x] wayfinder (3P)
- [x] wayfinder-to-build
- [x] working-doc-set-deslop

## To-do

The plan lives in one place: the branch plan's Now section.
This file carries no step list of its own.
