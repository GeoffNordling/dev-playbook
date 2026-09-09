---
type: General-Sheet
title: Documentation Sets Reality Check
description: Session record of auditing the repo's documentation sets against the Documentation Sets standard — the six problems found, examples, and proposed rule changes; delete when the standard is settled
---

# Documentation Sets: the reality check

Session record, 2026-09-09, branch `worktree-cloa-viewer-tool`. Written
to survive compaction. Paths are root-absolute in the worktree
`/home/geoff/workspace/dev-playbook/.claude/worktrees/cloa-viewer-tool`.
Temporary: delete this file and its row in the root `index.md` when the
standard is settled and the auditors come back clean.

## What we committed

The general Standard is
`/standards/knowledge-organization/documentation-sets/documentation-sets.md`.
Population: "a documentation set, the concept documents one index.md
owns, except a numbered Decision Record among them". Six rules, each an
H2 whose first paragraph is the predicate:

1. `an-index-in-every-directory` — a subdirectory holding concept
   documents carries its own `index.md` and is a child set, never
   absorbed. okf-lint: `knowledge-organization.index-present`.
2. `body-inside-its-concern` — every section of a member answers the one
   question its `description` names.
3. `child-inside-its-parent` — a child index's opening sentence narrows
   the parent's.
4. `one-home` — a fact is stated in the one member whose concern is the
   most general where it holds; every other document links there.
5. `distinct-concerns` — no two members declare overlapping
   descriptions.
6. `terms-defined-once` — a term a set coins and uses in more than one
   member is defined once, in `CONTEXT.md`.

Beside it, the one special case so far:
`/standards/knowledge-organization/documentation-sets/working-documentation-sets.md`, the
further rules of a working documentation set (speculative voice, reached
from the root, where a set lives, worklist, buckets, terms, acronyms).

Indexes' `the-introduction` is the set's concern; okf-lint checks only
presence (`knowledge-organization.index-intro`), meaning is judgment.
`CONTEXT.md` defines *Documentation set* and *Concern*.

Commits: `0cd88a3` (the Standard), `0bf1048` (every card moved to
`standards/<name>/card.md` so a card and its Standards are one set),
`0b5c759` (okf-lint's two rules; absorption no longer legal).

## Why we checked reality first

Before wiring an auditor into the Knowledge Organization card's Audit
and Enforce cells, we wanted to see what the rules do when they meet the
repo as it stands: how far the docs sit from the rules, and where the
rules themselves are wrong. A set is deterministic, one per `index.md`,
so a scratchpad script (`sets.py`, beside this file) enumerated the 22
sets. Four Opus auditors then read one shared prompt and each took one
tree: `standards/`, `doc-types/`, `docs/`, and the root group (root,
`dotfiles/`, `scripts/`, `harness-recipes/`). `software-factory/` and
the CLOA working set were ruled out of scope.

The auditors found many duplications and out-of-concern sections. Those
are expected: there was no standard, so there is slop, and it is fixed
after the standard settles. The pointers for that later pass are under
"The slop backlog" at the end of this file; the raw reports were not
kept.

The focus now is the other kind of finding: content that should exist
and that the rules as written cannot sanction.

## The auditor prompt

`/tmp/claude-1000/-home-geoff-workspace-dev-playbook/3fd5c2b3-528b-46d6-9e39-7b1125c57676/scratchpad/set-audit.md`

Launch line, one per tree, Opus pinned, `general-purpose` agent:
"Read <that path> and follow it. Your assignment: `standards/` and every
set nested in it." The prompt fixes the report shape: Findings, Standard
defects, Conversion effort, Questions. It is the first draft of a
general documentation-set auditor, the agent the Knowledge Organization
card would cite once it works.

## The six problems

Progress: 1 settled in `2dca7d7` (one-home admits a view, "a new form
its own concern needs"; no tiebreak, no examples). 2 settled,
uncommitted (a definition is a fact; home is the coining member, and
`CONTEXT.md` only for a term used beyond its set; Doc Conventions
`:137-139` and CONTEXT.md Content's lead already agree, so no companion
edit). The `detectors.md` lead is a view under 1. 3 settled, uncommitted: the
rule is now prediction, "a reader who chose it from the index finds
nothing in the body they did not expect"; fixed sections and reasons
pass, a vague description is Document Types' problem, not this rule's.
4 settled, uncommitted: population exempts a `type: Reference` mirror;
`standards/index.md` intro names `references/`; Card Catalog's claim
stays. 5 settled, uncommitted: rule binds the rows of an index, member
or child set; the boundary is drawn in the lead paragraphs, linked both
ways, not in the descriptions; definition/encoding "Where a Standard
lives" is a real doc finding. 6 settled, uncommitted:
child-inside-its-parent became `rows-inside-the-set`, binding every row,
member or child, to the intro sentence; `cards.md:66` anchor updated.
Next: commit, re-run the four auditors with the shared prompt.

### 1. one-home: a restatement at a different grain reads as a second home

**Rule.** "A fact, rule, or decision is stated in one member, the one
whose concern is the most general where the fact still holds; every
other document links there."

**Conflict.** The repo is built on restating one thing at several
levels of abstraction: a card summarizes its Standards, a contract shape
collapses a Standard into pseudocode, a Standard's lead names the
population term `CONTEXT.md` defines, a catalog row repeats a
description. The rule has no concept of a view, so each is a second
home. Card Catalog carved distinct-concerns out for the card
(`/standards/standard/cards.md:62-66`) and did not carve one-home out.
And when two homes are general on different axes the rule names no
winner.

**Examples.**

- `/doc-types/standard-card/contract-shape.md:78` states
  `location = path == f"standards/{name}/card.md"`;
  `/standards/standard/cards.md:25-29` (Directory layout) states the
  same rule as the repo's obligation. The two trees already link each
  other both ways (`cards.md:38` → `encoding.md#naming`;
  `/doc-types/standard-card/encoding.md:52` → `cards.md#directory-layout`),
  which is what the rule prescribes for the loser, and neither is the
  loser. Six of the doc-types auditor's findings turn on this one case.
  `/doc-types/doc-type-system.md:132` asserts the split ("A doc-type
  declares what a contract shape *is*; it never binds anyone to use it")
  and names no home.
- `/standards/shell/card.md:24-29` lists the Standard's section names in
  its Audit cell; `/standards/tracking/card.md:40-43` restates
  `candidates.md:17-19`; `/standards/harness/card.md:26-36` and
  `/standards/python/card.md:18-31` summarize the same way. A card's
  whole job is to summarize, so every card's Audit and Enforce prose is a
  finding. The shell roster, which rots on a rename, is the case that
  should still fail.
- `/docs/machines.md:40-53` and `/standards/standard/gates.md:63-75`
  (Skips) each state "a machine-local check is skipped and announces
  itself", each link the other, and each disclaim half ("which machine
  skips what is recorded in Machines" / "which gates this affects is
  recorded in Gates"). The rule cannot choose between a gate concern and
  a machine concern for a fact about a gate on a machine.
- `/standards/standard/detectors.md:11-13` and `gates.md:11-13` restate
  a `CONTEXT.md` term in their lead because the Standard doc-type
  requires the lead to name the population.

**Proposed change.** Add to one-home: a document whose concern is to
restate a home at another grain (a card's cells, a contract shape, a
generated view, a population lead, an index row) is a view of the home
and links it, never a second home. Tiebreak: the home of a rule is the
document whose population the rule binds; the doc-type's shape is its
view. For Machines versus Gates the fact binds detectors, so Gates.

### 2. terms-defined-once: a member whose concern is coining a vocabulary cannot obey it

**Rule.** "A term a set coins and uses in more than one member is
defined once, in the repo's `CONTEXT.md`."

**Conflict.** Several members exist to define a closed vocabulary, and
the vocabulary is used in the members beside them. The rule sends every
such term to `CONTEXT.md`, which CONTEXT.md Content calls a
disambiguation center ("when several words compete for one concept, one
is picked and the rest retired") with one-or-two-sentence entries and
"Glossary only". Terms that need exposition cannot go there. And Doc
Conventions contradicts the rule outright.

**Examples.**

- `/doc-types/runbook/contract-shape.md:104`: "This vocabulary is
  closed: the tables above are all of it. A new operation, node type, or
  bucket is an edit here before its first use." Node, edge, bucket, and
  span are used in `definition.md:16`, `encoding.md`, and
  `residual-ledger.md:17`. The rule would move their definitions out of
  the file the set names as the single point of edit.
  `/doc-types/doc-type.md:16-41` is the same case for operation,
  composition rule, shape, instance, grain; `:119-129` for layer and
  primitive map. `/doc-types/standard/contract-shape.md:17` for
  population, predicate, condition.
- `/standards/modules/design.md:73-79` defines *seam* and carries the
  `_Avoid_` ruling CONTEXT.md's entry shape exists for ("The workspace
  word is *seam*, never *boundary*"); used in
  `/standards/testing/conventions.md:159-163`. This is the one term in
  the `standards/` tree that competes with another word. The other
  dozen (governed repo, layer, card, port, adapter, Candidate, leaf,
  epic, bundle, the two loads, working documentation set) do not.
  *Governed repo* is used in ten population lines and defined nowhere.
- `/docs/system-legibility.md:14-45` defines *Slop* across a definition,
  a mechanism, and a consequence; `/CONTEXT.md:18-19` defines it
  differently ("Output that diverges from the user's intent, or that the
  user cannot read", the output, not the system). Glossary-only forbids
  the three paragraphs; the two definitions disagree.
- `/standards/prose/conventions.md:136-138`: a doc uses `CONTEXT.md`'s
  terms "with no obligation to extend it", against
  `standard.md:84-85`, which obliges it.

**Proposed change.** A term is defined once, in the member whose concern
it is; it goes to `CONTEXT.md` when no member owns it or when a
competing word is retired; exposition beyond the definition stays in the
member; every other document links the definition. Rewrite the Doc
Conventions sentence to match. The two *Slop* definitions are a doc fix.

### 3. body-inside-its-concern: sections a doc-type fixes, and reasons beside rules

**Rule.** "A member's body stays inside its concern: every section
answers the one question the description names."

**Conflict.** A doc-type fixes sections no description names: a
recipe's "Running it", an Acronyms appendix, a Standard's population
lead, a README's floor and the depth README Content says "grows with
the project". A rule's reason, which Doc Conventions deliberately keeps
beside the rule, answers "why", which no description names either. And
the rule has no test for a description that is too broad, so it rewards
vagueness.

**Examples.**

- `/harness-recipes/recipes/ralph-loop.md:43-56` and
  `scatter-gather.md:52-70` both end with "Running it", the same shape
  in both; neither description names invocation.
  `/doc-types/doc-type.md:145`, `doc-type-system.md:152`,
  `runbook/contract-shape.md:113`, `runbook/encoding.md:187`,
  `runbook/residual-ledger.md:345` each end with `## Acronyms`;
  `working.md:100` mandates it for working sets only, so a permanent
  set's appendix is unruled and inconsistently applied.
- `/standards/build/canonical.md:90-120` "The reasons behind the pins"
  says why each pinned value is what it is, and says why it is there
  ("each a choice that looks reversible until the reason is read").
  `/standards/prose/conventions.md:30-31` keeps a reason beside a rule
  where "the present is unintelligible without it".
- `/scripts/README.md` carries Setup, two script inventories, a library
  map, a run-environment contract, and a CLI how-to (`:150-175`) under
  one description; `/standards/knowledge-organization/readme-content.md:11-13`
  says a README's depth grows. Three of the root group's four sets have
  a README as their only member, so a README cannot be audited at all
  without contradicting a neighbouring Standard.
- Breadth: `/docs/headless.md`'s description is five words ("Running
  Claude Code headless on subscription"), so a 30-line permission
  experiment at `:118-147` passes; `/docs/measurement-derivation.md`'s
  description enumerates its sections and fails for the two it did not
  list (`:227` Session-to-issue binding, `:254` Cost enrichment). Same
  directory; the precise author takes the finding.

**Proposed change.** A section the member's type fixes, and a rule's
reason, are inside the concern. For breadth, one clause in Document
Types' description rule: the description covers the body's span, so a
description any section fits is Document Types' finding.

### 4. A `type: Reference` mirror, and a child that is not a card directory

**Rules.** The population, and `child-inside-its-parent`: "the child
index's introduction narrows what the parent's names."

**Conflict.** A vendored mirror cannot be edited to fit any rule; every
neighbouring Standard already exempts it and this one does not. And a
child set of a kind the parent's intro does not name fails
child-inside-its-parent by construction.

**Examples.**

- `/standards/references/okf-spec.md` is 458 lines of upstream OKF spec.
  Exemptions exist at `/standards/prose/conventions.md:5` ("except
  `type: Reference`"), `/standards/prose/card.md:25-27`, and
  `/standards/standard/detectors.md:137-146`. Documentation Sets exempts
  only a numbered Decision Record (`standard.md:18-21`).
- `/standards/index.md:3-5` says "every standard is one directory here,
  holding its card"; `/standards/references/index.md:3-4` is a child
  with no card and no question sentence. `/standards/standard/cards.md:64-67`
  claims child-inside-its-parent "holds by construction: every question
  narrows *the catalog*", which is true of card directories only.

**Proposed change.** The population exempts `type: Reference` beside the
Decision Record. The catalog intro naming both kinds of child, and Card
Catalog's "by construction" claim, are doc fixes.

### 5. distinct-concerns: twenty-word descriptions cannot carry a boundary

**Rule.** "No two members of a set declare overlapping concerns … they
merge, or the boundary between them is redrawn into both descriptions."

**Conflict.** Document Types caps a description at "roughly one breath,
twenty words as a soft limit" (`document-types.md:58-61`). Every real
boundary the repo draws lives in a lead paragraph. The two rules cannot
both be met. Overlap below the description, at section level, is
invisible to the rule.

**Examples.**

- `/standards/build/python.md:14-16` and `/standards/python/style.md:14-19`
  draw the repo-level/file-level boundary in their leads; the two card
  descriptions ("the Python project" / "how Python source is written —
  … module layout") send a reader to both rows.
- `/standards/testing/card.md:10-12` claims "everything inside
  `tests/` is this card's"; `/standards/python/style.md:5` has
  population "any `.py` file" with no test exclusion, and `:36-45`
  rules on test functions directly. Two cards claim the same files.
- `/doc-types/standard/definition.md:4` ends "and where it lives",
  `encoding.md:4` ends "and where the file sits", and both carry a
  `## Where a Standard lives` section (`definition.md:25`,
  `encoding.md:78`).
- `/docs/system-legibility.md:4` and `/docs/working-in-loops.md:4` both
  open "The doctrine —", and the detector principle appears in both
  (`system-legibility.md:129-136`, `working-in-loops.md:23,159-162`).

**Proposed change.** Where two descriptions touch, each lead paragraph
draws the boundary and links the other; the descriptions still must not
read as one question. Section-level overlap stays one-home's.

### 6. Nothing binds a member to its own set's concern

**Rule.** None. `child-inside-its-parent` binds index to index;
`body-inside-its-concern` binds body to description. The member-level
twin, a member's description inside the set's intro sentence, is
missing.

**Conflict.** A member can sit in a set whose concern it does not fit
and violate nothing, and a set intro can leave a member unnamed.

**Examples.**

- `/docs/measurement-derivation.md`, a live derivation spec carrying a
  fail-loud contract at `:76-83`, sits under `docs/`'s "working papers —
  a mixture of notes, unenforced policies, intentions, and
  explorations". (The user ruled `docs/` passes as a deliberately loose
  set; the question is whether that ruling should be a rule's clause.)
- `/standards/build/index.md:3-5` names "the file skeleton, the
  canonical artifacts, and the Python project" and not `bootstrap.md`, a
  Guide; `/standards/harness/index.md:3-5` names neither `files.md` nor
  `writing-for-agents.md`. Sibling indexes (`standard/`,
  `knowledge-organization/`, `tracking/`) each add a sentence for their
  guide.
- `/docs/index.md:18`'s row for `writing-improvement-process/` carries
  one member's description ("the catalog of recurring problems"), not
  the set's; the set's own intro
  (`/docs/writing-improvement-process/index.md:3`) restates the path.

**Proposed change.** Add a rule, "Member inside its set": a member's
description lies inside the concern the set's index declares. It gives
the tree of sets its meaning.

## Also found, outside the six

- **Harness-owned prose is outside the population.** The 55 files under
  `/dotfiles/dot-claude/` are harness-owned, so no rule reaches them:
  `/harness-recipes/recipes/ralph-loop.md:30-31` states the check-gate
  rule and `/dotfiles/dot-claude/skills/ralph-setup/SKILL.md` §5 restates
  it, and one-home is silent. That is the population as designed; state
  it in the lede and leave harness prose to Runbook Conventions.
- **one-home's "most general home" half is not auditable alone.**
  `scatter-gather.md:63-69` states the Workflow `args` serialization
  contract once, in the specific recipe, though `ralph-loop.md:49` is
  bound by it too. Duplication is findable; a lone fact sitting too low
  is not.
- **Types-table cells carry rules.** `/standards/knowledge-organization/document-types.md:39-50`:
  `Candidate-List` says "one per repo", `README` says "filename
  `README.md` ⟺ `type: README`"; `type-registry.md:50-55` bans that
  only for a local extension.
- **`okf_version` on non-root indexes.** `/doc-types/index.md:2` and
  its three child indexes carry `okf_version: "0.1"`;
  `scripts/okf-lint:581` requires it on the root only; no other index
  has it.
- **`/docs/decisions/README.md`** is mandated by
  `/standards/decisions/records.md:50-60` and its whole body is a
  pointer to its own index.
- **`/standards/prose/slop-tics.md`** is a set member typed
  `General-Sheet`, not a Define pointer; is a non-Standard member judged
  for distinct-concerns against the Standards beside it?
- `/docs/working-in-loops.md:98-101` asserts "Loop is a doc-type" with
  a generated registry; no Loop row exists in
  `/doc-types/doc-type-system.md` and no registry exists.

## Conversion effort, if the six changes land

Most sets rated small or medium by their auditors. `standards/` and
`doc-types/standard-card/` rated large only because they wait on
problem 1.

## The slop backlog

Pointers only, in the auditors' order, for the fix pass after the
standard settles. A → names the home the auditor proposed. Some of
these dissolve if problems 1 to 3 are ruled as proposed.

Root group:

- `/README.md:40` sync-dotfiles note → `/dotfiles/README.md:57`;
  `:20-30` "What belongs here" → `/index.md:7-9`.
- `/dotfiles/README.md:43-46` one-file-every-machine →
  `/docs/machines.md:29-34`; `:47-52` symlink failure detection is out
  of concern.
- `/scripts/index.md:9-16` a paragraph after the listing describes
  chaingen, cardgen, rulegen, labelgen, each with a home already.
  `/scripts/README.md:22-35` belongs/does-not-belong → the index;
  `:116-124` consumer clone → `/standards/distribution/channel.md:11-16`;
  `:150-175` transcript-export how-to is out of concern.
- `/harness-recipes/README.md:20-24` billing → `/docs/headless.md:19-20`.
  `/harness-recipes/recipes/index.md:3-4` repeats the parent intro word
  for word; collapse the level or give the parent its own concern.

`docs/`:

- `/docs/measurement-derivation.md:52` → `/docs/machines.md:32-33`;
  `/docs/machines.md:42` → `/standards/standard/gates.md#skips`.
- `/docs/headless.md:143` states a fence status that
  `/docs/sandboxing.md:17-33` owns and contradicts.
- `/docs/system-legibility.md:46` and `:171` define CLOA twice more
  after `/CONTEXT.md:21-22`; `:55` coins *rubber stamping*, used in
  `/docs/writing-improvement-process.md:38,45,71`, no CONTEXT entry;
  `:152` "The vocabulary API" restates CONTEXT.md Content's rules.
- `/docs/writing-improvement-process.md:87` platform facts and `:66`
  Principles are out of concern; `:93` the `claude -p --resume
  --fork-session` fact → `/docs/headless.md:101-113`.
- Immutability of a record is stated at `/docs/decisions/README.md:4`,
  `/docs/decisions/index.md:3-4`, and `/docs/index.md:17` →
  `/standards/decisions/records.md#immutability`.
- `/docs/writing-improvement-process/writing-improvement-problems.md:11`
  → `/docs/writing-improvement-process.md:23-27`.

`doc-types/`:

- `/doc-types/doc-type-system.md:115` The bundle and `:132` Shape and
  obligation → `/doc-types/doc-type.md`; `:45` Skill and Agent rows point
  at contract-shape while Standard rows point at definition.
- `/doc-types/runbook/encoding.md:20` provenance paragraph (doctest, CNL,
  STE, a planned lint) is out of concern; `:164` ↔
  `/standards/harness/runbook-conventions.md:125`.
- `/doc-types/runbook/contract-shape.md:34` location rule ↔
  `runbook-conventions.md#location`; `:81` edges at the definition site ↔
  `runbook-conventions.md:118`.
- `/doc-types/runbook/residual-ledger.md:23` entry form ↔
  `/doc-types/standard/residual-ledger.md:20` → `/doc-types/doc-type.md`;
  `:27` Accepted classes sits under the wrong H2.
- `/doc-types/standard-card/contract-shape.md:11` redefines *standard
  card* (home `definition.md:9`); `:21` and `:23` restate
  `/standards/standard/cards.md`; `encoding.md:49` and `definition.md:52`
  likewise; `encoding.md:57` Naming governs every filename under
  `standards/`, wider than its description.
- `/doc-types/standard/contract-shape.md:62` ↔ `encoding.md:94`
  (rulegen); `definition.md:19` ↔ `encoding.md:69` (one thing);
  `contract-shape.md:46` ↔ `encoding.md:80` (the path).

`standards/`:

- `/standards/README.md:14-16` → `/standards/standard/cards.md:25-31`.
- `/standards/python/style.md:42-43` → `/standards/testing/conventions.md:72-76`.
- `/standards/standard/consuming.md:38-42` restates the detector
  contract it links; `cards.md:113-116` → `indexes.md:51-54`.
- `/standards/build/bootstrap.md:44` → `channel.md:91-92`; `:71-72` →
  `repo-settings.md:11-14`; `:78-80` → `channel.md:48-49`.
  `/standards/build/canonical.md:29-31` and `/standards/build/card.md:32-34`
  → `gates.md:63-75`.
- `/standards/knowledge-organization/indexes.md:78-92` The root index
  contradicts its own Typeless rule; `document-types.md:87-94` Under
  standards/ is a location rule owned elsewhere; `indexes.md:57-58` →
  `documentation-sets/documentation-sets.md:32-34`.
- `/standards/harness/writing-for-agents.md:81-103` Skill mechanics is
  out of concern; *completion criteria* defined at
  `runbook-conventions.md:111-114` and `writing-for-agents.md:50`;
  `files.md:36-38` → `runbook-conventions.md:24-28`.
- `/standards/prose/conventions.md:33-35` → `records.md:112-120`;
  `/standards/decisions/records.md:55-57` → `cross-references.md:17-20`.
- `/standards/modules/design.md:132-150` Results are returned is not in
  the description.
- `/standards/tracking/card.md:57-58` → `repo-settings.md:11-14`;
  `repo-settings.md:77-80` ↔ `gates.md:56-61` mutual.
- `CONTEXT.md` entries the auditors expected and did not find: governed
  repo, standard card, layer, bundle (two senses: OKF and skill),
  working documentation set, the two loads, context pointer, seam,
  adapter, port, Candidate, leaf, epic, residual, node, edge, bucket,
  span, cell, pointer, population, predicate, condition, rubber
  stamping. *Rule* at `/CONTEXT.md:77` is a different sense from the
  Standard doc-type's. Which of these belong there depends on problem 2.
