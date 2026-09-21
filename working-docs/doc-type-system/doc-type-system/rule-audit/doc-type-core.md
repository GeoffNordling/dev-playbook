---
type: General-Sheet
title: Doc-Type, Standard, and Loop Conventions Rule Audit
description: The rule audit over the standards/doc-type/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Doc-Type, Standard, and Loop Conventions Rule Audit

Seventeen rules across three Standards: seven in
[Doc-Type](/standards/doc-type/doc-type.md), three in
[Standard Conventions](/standards/doc-type/standard-conventions.md), and
seven in [Loop Conventions](/standards/doc-type/loop-conventions.md).
No rule needs reclassifying in either direction: every trailer already
carries the kind the predicate supports. Two rules break —
`doc-type.one-base`, whose `Finding` class sits outside the base at
`doc-types/standard/contract-shape.md:67`, and
`doc-type.the-rule-shape`, which three separate repo facts contradict.
Two are weakly checked, `doc-type.three-verb-sections` and
`doc-type.entries-point-and-condition`, both by `scripts/loop-lint`.
Eleven have no check at all, four are fully checked, and one,
`doc-type.one-sentence`, is low value. All seven Loop Conventions rules
hold vacuously in this repo: `loops/` holds only its `index.md`, so the
population is empty here, and the rules bind through the published
`playbook-lint` roster in the governed repos instead.

| id | rule | kind | proposed | check | state | overlap | value | note |
|---|---|---|---|---|---|---|---|---|
| `doc-type.registered` | "The doc-type is the ruling of at least one row of the registry rulings table in Doc-Type System, and its directory is a row of doc-types/index.md." | deterministic | deterministic | none | holds | `knowledge-organization.the-listing` | high | Read the rulings table of `doc-types/doc-type-system.md` and the bullets of `doc-types/index.md`; loop, runbook, and standard each appear in both. The listing rule subsumes the index half. |
| `doc-type.a-verb-set` | "`definition.md` states the doc-type's verbs, a non-empty set of single words, and the `operations` of the class in `contract-shape.md` is the same set." | stochastic | stochastic | none | holds | none | high | Judgment: nothing pins where in `definition.md` the verbs sit, and `operations` is pseudocode no extractor parses. act/check/yield, the six runbook verbs, and hold all agree. |
| `doc-type.one-base` | "`contract-shape.md` holds one class that extends `DocType`, declaring `operations` and `frontmatter`; every other class in its block is nested inside that one, extends nothing, and declares no operations." | stochastic | stochastic | none | breaks | none | high | `doc-types/standard/contract-shape.md:67` opens `class Finding:` at column 0, a second top-level class in the block. See Escalations. |
| `doc-type.a-composition-rule` | "`contract-shape.md` states what an instance may point at, which doc-types and which Targets, and how many of each." | stochastic | stochastic | none | holds | none | high | Judgment: "states what an instance may point at" has no syntactic form. All three carry a sentence opening "The composition rule:". |
| `doc-type.an-encoding` | "`encoding.md` maps each markdown construct an instance uses to one part of the class in `contract-shape.md`." | stochastic | stochastic | none | holds | none | high | Judgment: the map is prose. Loop maps the fence, nodes, edge labels and verb H2s; Standard maps the `population` key, headings and trailer; Runbook maps its spans. |
| `doc-type.held-to-a-standard` | "A Standard exists whose population is the instances of the doc-type, so that every file of the type is a member of it." | stochastic | stochastic | none | holds | none | high | Judgment: matching a `population` phrase to a doc-type is a reading. Loop, Runbook and Standard Conventions cover the three. |
| `doc-type.one-sentence` | "`definition.md` opens with one sentence that says what one instance is and what the doc-type does." | stochastic | stochastic | none | holds | none | low | Judgment: whether a sentence says what the doc-type does is taste. The file's frontmatter `description` and its H1 section already tell a reader what an instance is. |
| `doc-type.the-population` | "A file typed `Standard` names the population its rules bind in its frontmatter: a `population` key holding one phrase; standards-lint reports a Standard without one." | deterministic | deterministic | full | holds | none | high | `standards_lint.check_directory_layout` reads each Standard's frontmatter and flags a missing or non-string `population`. All 30 Standards carry exactly one. |
| `doc-type.the-rule-shape` | "Each rule of a Standard is a level-two heading, a first paragraph that is the predicate every member of the population is held to, at most one block or table stating the target state the predicate compares against, and last a trailer line, `` `<name>.<slug>` · deterministic `` or `` `<name>.<slug>` · stochastic ``, where `<name>` is the directory and `<slug>` the heading's GitHub slug; nothing follows the trailer before the next heading." | deterministic | deterministic | none | breaks | `standard.the-verifier-table` | high | Verifier row null. Three breaks: two blocks under one rule, every H3 under a rule not a condition, and a nested Standard's `<name>`. See Escalations. |
| `doc-type.decidable-predicates` | "Each rule's predicate is true or false of one member of the population at one moment, with no comparison to another member and no taste." | stochastic | stochastic | none | holds | none | high | Judgment: "no taste" is itself a reading. One wobble: `standard.an-emitted-id-is-a-rule-heading`'s "no two checks claim the same id" reads as cross-member unless the member is the table. |
| `doc-type.one-graph` | "A document typed `Loop` holds one H1, then one paragraph, then one fenced `mermaid` block, in that order and with nothing else before the fence." | deterministic | deterministic | full | holds | none | high | `loop_lint.slice_loop` and `graph_of` test every clause: two H1s, a heading before the fence, a second fence, paragraph count, the `flowchart`/`graph` opener, `&` fan-out, unreadable nodes. Vacuous: no Loop exists. |
| `doc-type.what-the-paragraph-says` | "In a document typed `Loop`, the paragraph before the graph names the state the loop drives and the target state it drives that state toward." | stochastic | stochastic | none | holds | none | high | Judgment: naming a state is a reading. Vacuous: `loops/` holds only `index.md`. |
| `doc-type.three-verb-sections` | "After the graph, a document typed `Loop` holds three H2s, `Acts`, `Checks`, and `Yields`, in that order and no others, with nothing between the graph and the first of them." | deterministic | deterministic | weak | holds | none | high | `entries_of` skips blank lines, so "one list" per H2 is untested. Vacuous: no Loop exists. See Escalations. |
| `doc-type.nodes-and-entries-agree` | "Every entry of a document typed `Loop` names a node of its graph, and every node of the graph carries an entry or is a receiver, a node with no entry that an edge out of a yield leads to." | deterministic | deterministic | full | holds | none | high | `loop_lint.check_loop` tests both directions against `yielded_to`. Vacuous: no Loop exists. |
| `doc-type.edges-follow-the-shape` | "In a document typed `Loop`, every edge of the graph leads to a step, a node whose entry is an act, a check, or a yield, except an edge out of a yield, which leads to a step or to a receiver, a node with no entry." | deterministic | deterministic | full | holds | none | high | `loop_lint.MAY_LEAD_TO` encodes the predicate exactly, receiver included. Vacuous: no Loop exists. |
| `doc-type.entries-point-and-condition` | "Every entry of a document typed `Loop` states its condition, `fires when …` or `fires every iteration` for an act or a check and `yields when …` for a yield." | deterministic | deterministic | weak | holds | `doc-type.an-act-links-a-runbook` | high | For an act or a check `check_entry` resolves only `links[0]`; the predicate binds every link. Vacuous: no Loop exists. See Escalations. |
| `doc-type.an-act-links-a-runbook` | "The link an act's entry holds names a runbook, a skill bundle's `SKILL.md` or an agent definition." | deterministic | deterministic | none | holds | `doc-type.entries-point-and-condition` | high | Verifier row null; `loop_lint.check_entry` requires only a resolving link for an act. A script would test the target's path against the runbook roots. Vacuous: no Loop exists. |

## Escalations

### `doc-type.one-base` — "`contract-shape.md` holds one class that extends `DocType`, declaring `operations` and `frontmatter`; every other class in its block is nested inside that one, extends nothing, and declares no operations."

The predicate asks that every class in a `contract-shape.md` block other
than the base be nested inside the base.
`doc-types/standard/contract-shape.md` does not do this. Its python
block holds `class Standard(DocType)` with `class Rule` nested inside,
and then, at line 67 and at column 0, a second top-level class:

    class Finding:                    # what a verifier returns for a member that fails a rule
        member: Target                # the thing that failed
        rule:   Standard.Rule         # the rule it failed

`Finding` extends nothing and declares no operations, so it fails only
the nesting clause. The other two doc-types obey: `Runbook` nests
`Edge`, and `Loop` nests `Act`, `Check`, and `Yield`.

The placement is deliberate, not an oversight.
`doc-types/loop/contract-shape.md` imports it as a peer of the base —
`from standard import Finding, Standard` — and
`doc-types/loop/contract-shape.md`'s `Check` declares
`findings: list[Finding]`. A `Finding` is what a verifier returns, not
a part a Standard's markdown encodes, so nesting it inside `Standard`
would put it where `doc-types/standard/encoding.md` maps nothing.
`standards/doc-type/explanation.md` gives the reason for the rule as
"a part is a class nested in its DocType, so that a Rule or an Edge is
never mistaken for a doc-type" — and `Finding` is not a part.

**Proposal.** Rewrite the predicate. Make it read: "`contract-shape.md`
holds one class that extends `DocType`, declaring `operations` and
`frontmatter`; every other class in its block extends nothing and
declares no operations, and a class that is a part of the doc-type is
nested inside that base." This keeps the rule's stated intent — no
second doc-type hiding in the block, every part inside its owner — and
admits the one shared return type the three blocks already depend on.
Changing the repo would break the import in Loop's block, and deleting
the rule would give up the one-doc-type-per-file guarantee the four
blocks rest on.

### `doc-type.the-rule-shape` — "Each rule of a Standard is a level-two heading, a first paragraph that is the predicate every member of the population is held to, at most one block or table stating the target state the predicate compares against, and last a trailer line, `` `<name>.<slug>` · deterministic `` or `` `<name>.<slug>` · stochastic ``, where `<name>` is the directory and `<slug>` the heading's GitHub slug; nothing follows the trailer before the next heading."

Three separate facts of the repo contradict the predicate. No check
decides the rule: `standards/verifiers.yaml:83` is null, and while
`scripts/verifier-table` does read every trailer under `standards/`, it
emits only `standard.the-verifier-table`.

**One. "At most one block or table."**
`standards/doc-type/runbook-conventions.md:26`, the `Front matter`
rule, holds two fenced `yaml` blocks — a skill's block at line 37 and
an agent's at line 49 — each introduced by its own prose line, "A
skill's block:" and "An agent's block:". The rule is the only member of
the whole tree that does this; the other 29 Standards each stay at one
block or table per rule.

**Two. "A level-three heading sits only under a level-two heading that
is a condition."** Every H3 in the tree — 64 of them across twelve
Standards — sits under an H2 that carries its own trailer and therefore
is a rule by this predicate's own first clause. The repo writes a
condition as a rule: `standards/prose/conventions.md:101`,
"Harness-loaded agent instructions", states a membership test and then
carries `prose.harness-loaded-agent-instructions` · deterministic,
after which `### No first person` follows at line 109. The contract
shape agrees with the repo and not with the predicate:
`doc-types/standard/contract-shape.md` declares
`condition: "Rule | None"  # the rule this one is under`, making a
condition a Rule with an id. Two of these H2s are not membership tests
at all but substantive requirements with real verifiers:
`standards/standard/detectors.md:41`, `standard.the-verifier-table`
(verifier `scripts/verifier-table`), and line 74,
`standard.the-boundary-table` (verifier `scripts/boundary-table`), both
of which carry H3s beneath them.

**Three. "`<name>` is the directory."** The seventeen rules in
`standards/knowledge-organization/documentation-sets/documentation-sets.md`
and `working-documentation-sets.md` all carry the prefix
`knowledge-organization`, not `documentation-sets` — for example
`knowledge-organization.an-index-in-every-directory` at
`documentation-sets.md:39`. The code agrees with the repo:
`src/dev_playbook/verifier_table.py:149` computes
`name = rel.split("/")[1]`, the first segment under `standards/`. The
nested layout is endorsed by `doc-types/standard/encoding.md`, which
names these two files as the example of a special-case pair.

**Proposal.** Rewrite the predicate on all three points; the repo's
state is deliberate in each. For the block count, say "any number of
blocks or tables stating the target state the predicate compares
against". For the heading levels, drop the word *condition* from this
rule and say "A level-three heading sits only under a level-two rule,
and is then a rule bound under it" — that covers the membership-test
H2s and `standard.the-verifier-table` alike, and leaves the definition
of a condition to `doc-types/standard/encoding.md`. For the id, say
"where `<name>` is the `standards/<name>/` directory the file sits
under". Changing the repo would mean splitting a rule that reads as one
and renaming seventeen rule ids plus their verifier rows, for no gain.

### `doc-type.three-verb-sections` — "After the graph, a document typed `Loop` holds three H2s, `Acts`, `Checks`, and `Yields`, in that order and no others, with nothing between the graph and the first of them."

The predicate's second sentence adds "Each H2 holds one list whose
every line is an entry". `src/dev_playbook/loop_lint.py:entries_of`
tests every part of this except *one list*: its loop opens with
`if not line.strip(): continue`, so a blank line between two separate
markdown lists under the same H2 is invisible to it, and both lists
read as one run of entries. Everything else is covered — `names !=
list(VERBS)` catches a wrong heading, a wrong order, and a fourth
heading; `ENTRY_RE` catches a line that is not `` - `id` — text ``;
the `node in entries` guard catches a node id with two entries; and
`slice_loop` raises on text between the graph and the first H2 and on
any H3 after the graph.

The gap is narrow, and it cannot be triggered in this repo today, since
`loops/` holds only `index.md`.

### `doc-type.entries-point-and-condition` — "Every entry of a document typed `Loop` states its condition, `fires when …` or `fires every iteration` for an act or a check and `yields when …` for a yield."

The predicate's last sentence reads "Every link in an entry is
root-absolute or relative to the document, and it resolves to a file in
the repo". `src/dev_playbook/loop_lint.py:check_entry` does not test
every link for an act or a check. It collects `links =
LINK_RE.findall(rest)`, then for those two verbs resolves only
`links[0]`:

    target = _resolve(links[0], loop_path, root)

A second or third link in an act's or a check's entry — a pointer at a
guide beside the runbook, say — is never resolved, so a dead link there
passes. The yield branch does iterate `for link in links` and resolves
each, so yields are covered. The condition test and the per-verb
pointer tests are otherwise full.

Like the rule above, the gap cannot be triggered in this repo today:
there is no document typed `Loop`.

## Detectors

**`scripts/loop-lint`** (`src/dev_playbook/loop_lint.py`). The one
detector behind Loop Conventions. It walks the repo's markdown once,
keeps the files under `loops/` typed `Loop`, and cuts each into one
paragraph, one `mermaid` flowchart, and three verb H2s, emitting five of
the Standard's seven ids: `doc-type.one-graph`,
`doc-type.three-verb-sections`, `doc-type.nodes-and-entries-agree`,
`doc-type.edges-follow-the-shape`, and
`doc-type.entries-point-and-condition`. It stops at a file's first
disagreement and moves to the next file, so one Loop yields at most one
finding. It does not decide `doc-type.what-the-paragraph-says` or
`doc-type.an-act-links-a-runbook`: for an act it requires a link that
resolves, never that the target is a runbook. `standards/boundaries.yaml:14`
runs it at commit, push, and ci, and it reaches every governed repo
through the `playbook-lint` roster at `src/dev_playbook/playbook_lint.py:51`.

**`scripts/standards-lint`** (`src/dev_playbook/standards_lint.py`). It
decides one rule of this family, `doc-type.the-population`, inside
`check_directory_layout`: for every tracked `.md` under a
`standards/<dir>/` that is typed `Standard`, it reads the frontmatter
and reports a `population` that is absent, not a string, or blank. Its
other five ids are the meta-standard's, not this family's.
`standards/boundaries.yaml:20` runs it at commit, push, and ci.

**`scripts/verifier-table`** (`src/dev_playbook/verifier_table.py`).
Not a detector of this family, but the code that actually reads the
rule shape. `declared_rules` walks every Standard, and for each trailer
requires that the id equal `<first segment under standards/>.<GitHub
slug of the nearest heading above>`, that a heading exist above it, and
that no id be declared twice — raising `CannotRun` on each rather than
emitting a finding. It emits `standard.the-verifier-table` only, so
none of this counts as a check on `doc-type.the-rule-shape`.

**`tests/test_pseudocode_sync.py`**. A test, not a verifier, and
explicitly temporary. It asserts that each `contract-shape.md` holds
exactly one `python` fence and that the four fences equal the reference
model's text. It parses nothing as Python and tests no class structure,
so it does not decide `doc-type.one-base`.
