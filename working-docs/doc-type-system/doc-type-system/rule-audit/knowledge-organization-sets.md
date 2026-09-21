---
type: General-Sheet
title: Documentation Sets Rule Audit
description: The rule audit over the standards/knowledge-organization/documentation-sets/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Documentation Sets Rule Audit

The two Standards under
`standards/knowledge-organization/documentation-sets/` declare 17 rules:
8 in `documentation-sets.md` and 9 in
`working-documentation-sets.md`. No rule is proposed for
reclassification in either direction — every trailer matches what the
predicate can be decided by. Nine rules break on the tree today:
`one-home`, `terms-that-cross-sets`, `speculative-voice`,
`the-link-tree`, `where-a-set-lives`, `a-set-stands-on-main`,
`buckets`, `terms`, and `acronyms`. No rule is weakly checked, because
only one of the 17 is checked at all: `an-index-in-every-directory`, by
`scripts/okf-lint`, fully. The other 16 rows of
`standards/verifiers.yaml` are `null`, including five rules a script
could decide today. Two rules are low value:
`knowledge-organization.terms-defined-once`, which `one-home` subsumes
by the family's own explanation, and
`knowledge-organization.working-docs-holds-only-sets`, which forbids a
fault nobody commits.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `knowledge-organization.an-index-in-every-directory` | "A set's members sit in the directory of its `index.md`; every subdirectory that holds a concept document, a numbered Decision Record or a `type: Reference` mirror included, carries an `index.md` of its own and is a child set." | deterministic | deterministic | full | holds | `knowledge-organization.the-listing` | high | Test: every directory holding a path `md.classify` calls `concept` also holds `index.md`. Scanned all tracked `.md`; only harness trees (`agents/`, `rules/`, `skills/*/references/`) lack one. |
| `knowledge-organization.body-inside-its-concern` | "A member serves one purpose, the one its description states, so a reader who chose it from the index finds nothing in the body they did not expect." | stochastic | stochastic | none | holds | none | high | Needs judgment: whether a section is a second purpose. Sampled both Standards, `indexes.md`, and the working-set members; each body stays inside its `description`. |
| `knowledge-organization.rows-inside-the-set` | "Every row of an index, member or child set, lies inside the concern the introduction names: a reader who chose the set from its parent's index expects each row they find." | stochastic | stochastic | none | holds | none | high | Needs judgment: whether a row is inside an introduction's concern. Sampled `standards/index.md`, `standards/knowledge-organization/index.md`, `working-docs/doc-type-system/index.md`. |
| `knowledge-organization.one-home` | "A fact, rule, or decision has one home, the member whose concern is the thing the fact binds and the most general such member where the fact still holds; every other document links there, whether it sits in the same set, another set, or another repo, and states the fact without its reason." | stochastic | stochastic | none | breaks | `knowledge-organization.terms-defined-once` | high | `standards/knowledge-organization/explanation.md:141-144` restates `working-docs-holds-only-sets` and the strand definition with no link to either home. |
| `knowledge-organization.distinct-concerns` | "No two rows of an index, member or child set, answer the same question: a reader at the index picks one." | stochastic | stochastic | none | holds | `knowledge-organization.distinct-from-the-parent` | high | Needs judgment: whether two descriptions answer one question. Sampled the three indexes above; no pair collides. |
| `knowledge-organization.distinct-from-the-parent` | "A child set's introduction names a concern its parent's introduction does not." | stochastic | stochastic | none | holds | `knowledge-organization.distinct-concerns` | high | Sibling test, across levels rather than within one index. Checked `documentation-sets/index.md` against its parent and `doc-type-system/doc-type-system/index.md` against its parent. |
| `knowledge-organization.terms-defined-once` | "A term is defined once, in the member whose concern it is, and every other use links that definition." | stochastic | stochastic | none | holds | `knowledge-organization.one-home` | low | The family's explanation says a definition is a fact like any other, so `one-home` subsumes this. Strand roots link the set root's Terms rather than redefine. |
| `knowledge-organization.terms-that-cross-sets` | "A term the set coins and a document outside the set uses has an entry in the repo's `CONTEXT.md`." | stochastic | stochastic | none | breaks | `knowledge-organization.project-terms-only` | high | `strand` and `bucket` are coined here and used at `doc-types/doc-type.md:63` and `standards/harness/claude-content.md:72`; `CONTEXT.md:49-57` has only **Documentation set** and **Concern**. |
| `knowledge-organization.speculative-voice` | "Every member of a working documentation set writes a guess as a guess and sets an open question beside its topic, and the set's `ROOT.md` declares the set speculative." | stochastic | stochastic | none | breaks | `prose.declarative-present-tense` | high | Only 3 of ~29 members carry an open question anywhere. `working-docs/software-factory/docs/tdd.md` is flat imperative throughout. |
| `knowledge-organization.the-link-tree` | "Every member of a working documentation set is reached from the set's `ROOT.md` by a path of links, a second structure over [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory)'s tree of sets." | deterministic | deterministic | none | breaks | none | high | Test: breadth-first walk of markdown links from `ROOT.md`, `index.md` rows excluded. 12 members unreached. |
| `knowledge-organization.where-a-set-lives` | "A working documentation set is one directory under `working-docs/` at the repo root, `working-docs/<work>/`, holding the set's `index.md`, its `ROOT.md`, and its members under lowercase kebab-case names, flat or in subdirectories — the one [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory) makes a set, here named and placed." | deterministic | deterministic | none | breaks | `knowledge-organization.working-docs-holds-only-sets` | high | Test: each `working-docs/*/` holds `index.md` and `ROOT.md`; every other member basename matches `[a-z0-9]+(-[a-z0-9]+)*\.md`. Two members fail. |
| `knowledge-organization.a-set-stands-on-main` | "A working documentation set, the one [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory) makes a set, is present on `main`." | deterministic | deterministic | none | breaks | none | high | Test: `git ls-tree main -- working-docs/<set>` is non-empty. `working-docs/software-factory/` is absent from `main`; it was created on this branch by 329a9b5. |
| `knowledge-organization.working-docs-holds-only-sets` | "`working-docs/` at the repo root, a plain parent to the sets [an index in every directory](/standards/knowledge-organization/documentation-sets/documentation-sets.md#an-index-in-every-directory) makes, holds its own `index.md` and the directories of the sets, and nothing else." | deterministic | deterministic | none | holds | `knowledge-organization.where-a-set-lives` | low | `working-docs/` holds `index.md`, `doc-type-system/`, `software-factory/` and nothing else. Binds one directory against a fault nobody commits. |
| `knowledge-organization.worklist` | "The work of a working documentation set is one list of items, each item a bold name and a body beneath it, and an item's state is the section it sits in, `Planned` or `Completed`, the one past state a member records ([current state and next steps only](/standards/prose/conventions.md#current-state-and-next-steps-only))." | deterministic | deterministic | none | holds | `knowledge-organization.buckets` | high | Test: each strand `ROOT.md` holds one `## Planned` and one `## Completed`; each item opens bold. All four strand roots and `software-factory/ROOT.md` obey. |
| `knowledge-organization.buckets` | "Every fact in a member of a working documentation set sits under a named section, its bucket ([one home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home) made navigable), and a bucket holds facts of its own type only." | stochastic | stochastic | none | breaks | `knowledge-organization.worklist` | high | Lead paragraphs carry facts above the first `##`: `working-docs/software-factory/docs/tdd.md:9-26` defines **chunk** and **seam** there. |
| `knowledge-organization.terms` | "A term coined by the work and used in more than one member of a working documentation set is defined in the `Terms` bucket of one `ROOT.md`: the root of the smallest strand that holds every member using the term, and the set's own root where the term crosses strands, in place of the entry [terms that cross sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md#terms-that-cross-sets) puts in the repo's `CONTEXT.md`." | stochastic | stochastic | none | breaks | `knowledge-organization.terms-defined-once` | high | `seam` is defined at `working-docs/software-factory/docs/tdd.md:23` and used at `refactor-catalogue.md:19`; `working-docs/software-factory/ROOT.md` has no `Terms` bucket. |
| `knowledge-organization.acronyms` | "Every member of a working documentation set ends with an `Acronyms` appendix, holding a bare `None.` where the member uses no acronym, and an acronym is defined in the appendix of the highest member that uses it and in no other member's, in place of a definition above first use ([declare before use](/standards/prose/conventions.md#declare-before-use))." | stochastic | stochastic | none | breaks | `prose.declare-before-use` | high | 14 members carry no `Acronyms` appendix. The appendix-present clause alone is deterministic; finding an acronym in prose is not. |

## Escalations

### `knowledge-organization.one-home` — "A fact, rule, or decision has one home, the member whose concern is the thing the fact binds and the most general such member where the fact still holds"

The predicate continues: "every other document links there, whether it
sits in the same set, another set, or another repo, and states the fact
without its reason."

`standards/knowledge-organization/explanation.md:141-144` states two
facts whose homes are elsewhere and links neither:

- Line 141: "`working-docs/` itself is a plain parent: its `index.md`
  lists the sets, and it holds no `ROOT.md` and no members of its own."
  The home is
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:67-74`,
  the rule `knowledge-organization.working-docs-holds-only-sets`.
- Lines 143-144: "A subdirectory of a set that holds a `ROOT.md` is a
  strand; one that holds none is governed by the nearest `ROOT.md` above
  it." The home is the same file's lead,
  `working-documentation-sets.md:21-24`, which defines **strand** and
  says "`ROOT.md` is the nearest root above the member."

The paragraph around them links every other rule it explains: the
sentence before carries `#where-a-set-lives` and the paragraph after
carries `#the-link-tree`.

**Proposal.** Change the repo: add the two links in
`standards/knowledge-organization/explanation.md`. Every neighbouring
sentence in that same explanation already links its rule, so the two
missing links are an oversight and not a deliberate exception, and the
fix is two link wrappers in one file. Rewriting the predicate to exempt
an Explanation would be wrong, because an Explanation restating a rule
without pointing at it is exactly the drift the rule exists to stop.

### `knowledge-organization.terms-that-cross-sets` — "A term the set coins and a document outside the set uses has an entry in the repo's `CONTEXT.md`."

`CONTEXT.md:49-57`, the `### Documentation sets` section, holds two
entries: **Documentation set** and **Concern**. The set coins more terms
that documents outside it use:

- **strand**, defined at
  `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:21-24`,
  used bare at `doc-types/doc-type.md:63` ("the fact base strand") and
  at `standards/knowledge-organization/explanation.md:143`.
- **bucket**, defined by the rule
  `knowledge-organization.buckets` at
  `working-documentation-sets.md:88-106`, used bare and in a second
  sense at `standards/harness/claude-content.md:72` ("Each rule of the
  global source is one `###` heading under its bucket").
- **child set**, defined at
  `documentation-sets.md:39-46`, used at
  `dotfiles/dot-claude/agents/doc-set-auditor.md` and
  `dotfiles/dot-claude/skills/doc-set-deslop/SKILL.md`, files with no
  fixed repo root that cannot carry a `/` link.

**working documentation set** is the one term that escapes: every
outside use links the Standard
(`standards/prose/conventions.md:82`, `standards/build/explanation.md:77`,
`standards/tracking/explanation.md:89`).

**Proposal.** Change the repo: add **Strand**, **Bucket**, and
**Child set** entries to `CONTEXT.md`'s `### Documentation sets`
section, each a one-sentence gloss linking its definition, the shape
the two entries there already take. The repo plainly wants this — the
section exists, the explanation says a crossing term "earns a
one-sentence gloss in the repo's `CONTEXT.md`", and the rule
`knowledge-organization.project-terms-only` already keeps the glossary
from growing past terms that cross. Three entries close the gap.

### `knowledge-organization.speculative-voice` — "Every member of a working documentation set writes a guess as a guess and sets an open question beside its topic, and the set's `ROOT.md` declares the set speculative."

The third clause holds: `working-docs/doc-type-system/ROOT.md:9` and
`working-docs/software-factory/ROOT.md:9` both open "This set is
speculative".

The first two clauses do not. Of roughly 29 members across the two
working sets, three carry an open question anywhere in the body:
`working-docs/doc-type-system/ROOT.md`,
`working-docs/doc-type-system/doc-type-system/ROOT.md`,
`working-docs/doc-type-system/fact-base/ROOT.md`, plus
`fact-base/fact-base.md`. No member of
`working-docs/software-factory/docs/` carries one, and none marks a
guess: `working-docs/software-factory/docs/tdd.md:23-26` reads "Work out
the seams the chunk's tests cut at before writing the first test", flat
imperative with nothing held open. `working-docs/software-factory/ROOT.md:17`
states why — "Each member is as it was on the day of the move" — so the
state is deliberate for that set.

**Proposal.** Rewrite the predicate so it states what the repo does on
purpose:

> Every member of a working documentation set writes a guess as a
> guess, and the set's `ROOT.md` declares the set speculative and holds
> the set's open questions.

This keeps the two clauses the repo obeys — the marked guess and the
root's declaration — and moves the open question to the root, which is
where the repo actually keeps it in both sets. Requiring an open
question inside every member has produced four instances out of 29 in
two live sets, which is a predicate nobody writes to. Changing the repo
would mean inventing an open question for 25 members, most of them
frozen by the move.

### `knowledge-organization.the-link-tree` — "Every member of a working documentation set is reached from the set's `ROOT.md` by a path of links"

A breadth-first walk of markdown links from each set's `ROOT.md`,
counting only links to `.md` members and skipping `index.md` rows as the
predicate's second sentence requires, leaves 12 members unreached:

- `working-docs/doc-type-system/doc-type-system/rule-audit/PROMPT.md`.
  Its only inbound link in the repo is the `index.md` row at
  `working-docs/doc-type-system/doc-type-system/rule-audit/index.md:8`,
  which the predicate excludes by name.
- All 11 members of `working-docs/software-factory/docs/`:
  `README.md`, `deviation-contract.md`, `factory-operations.md`,
  `node-agent-and-skill-authoring.md`, `pr-feedback.md`,
  `refactor-catalogue.md`, `review-contract.md`,
  `software-factory.md`, `tdd.md`, `user-checkpoints.md`, and the
  set's own `docs/index.md` listing. `working-docs/software-factory/ROOT.md:27`
  names the directory as inline code, "**`docs/`** — the ten files of
  `software-factory/` at the repo root", not as a link, so the walk stops
  at the root.

**Proposal.** Change the repo: turn `working-docs/software-factory/ROOT.md:27`'s
`` **`docs/`** `` into a link to
`/working-docs/software-factory/docs/index.md`, and link the rule-audit
prompt and its reports from the doc-type-system strand's `ROOT.md` step
10 entry. The repo plainly wants this — the doc-type-system set's root
links every other strand and member it owns, and the software-factory
root already links out to the plan that moved it — so the two gaps are
oversights from a bulk move and a new subdirectory. Both fixes are one
link each.

### `knowledge-organization.where-a-set-lives` — "A working documentation set is one directory under `working-docs/` at the repo root, `working-docs/<work>/`, holding the set's `index.md`, its `ROOT.md`, and its members under lowercase kebab-case names"

The directory clauses hold: `working-docs/doc-type-system/` and
`working-docs/software-factory/` each carry an `index.md` and a
`ROOT.md`, and every subdirectory name is lowercase kebab-case.

The member-name clause breaks on two members:

- `working-docs/doc-type-system/doc-type-system/rule-audit/PROMPT.md`,
  listed as a member at `rule-audit/index.md:8`.
- `working-docs/software-factory/docs/README.md`, listed as a member at
  `working-docs/software-factory/docs/index.md`.

Both are `concept` by `src/dev_playbook/md.py:250` `classify`, so both
are members and both are uppercase. The predicate exempts `ROOT.md` by
naming it and exempts nothing else.

**Proposal.** Rewrite the predicate to name the two capitalized
basenames the repo uses on purpose:

> A working documentation set is one directory under `working-docs/` at
> the repo root, `working-docs/<work>/`, holding the set's `index.md`,
> its `ROOT.md`, and its members under lowercase kebab-case names,
> `README.md` and a runbook prompt at `PROMPT.md` excepted, flat or in
> subdirectories.

`README.md` is fixed by `knowledge-organization.ordering`, which gives a
`README.md` entry the first place in a listing, so the repo already
expects that basename inside a set; renaming it would break that rule's
own vocabulary. `PROMPT.md` is a shouting name on purpose, matching
`ROOT.md`, for a file an agent loads rather than reads.

### `knowledge-organization.a-set-stands-on-main` — "A working documentation set, the one an index in every directory makes a set, is present on `main`."

`git ls-tree main -- working-docs/` lists two entries, `index.md` and
`doc-type-system`. `working-docs/software-factory/` is not among them:
it was created on this branch by commit 329a9b5, "Step 4: isolate the
software factory in `working-docs/software-factory/`", and `main`'s
`working-docs/index.md` lists only the one set.

The predicate cannot hold for any set between the commit that creates it
and the merge of the PR that carries it. That window is not an edge
case — it is every new working set's first life.

**Proposal.** Rewrite the predicate so it states the thing the repo
actually wants, that a working set is not branch-local and is never
parked under `docs/`:

> A working documentation set sits under `working-docs/` on every branch
> its work touches, and stays there when the work's branch merges rather
> than being deleted or moved under `docs/`.

Changing the repo would mean merging `working-docs/software-factory/` to
`main` ahead of the refactor it belongs to, which inverts the ordering
the plan set. The intent — a set outlives its branch — survives the
rewrite; the unsatisfiable "present on `main`" test does not.

### `knowledge-organization.buckets` — "Every fact in a member of a working documentation set sits under a named section, its bucket"

The predicate's second half, "a bucket holds facts of its own type
only", and its bucket menu hold on the sample. The first half breaks on
every member that opens with a lead paragraph carrying facts.

`working-docs/software-factory/docs/tdd.md` is the clearest case. Its
first `##` heading is `## The slice loop` at line 28. Above it, lines
9-26 define two terms and state four requirements: line 13, "Under this
discipline a piece of the scope is a **chunk**"; line 19, "Things ride
along in build's plan: the chunk's seams, its slice ordering, and the
current state of the suite"; line 23, "**Choose the seams first.** A
**seam** is a place where a test can replace or observe behavior".

The same shape appears in `working-docs/doc-type-system/viewer/contract.md:9-14`
and in both `ROOT.md` leads, so the lead paragraph is the repo's
convention, not one file's slip.

**Proposal.** Rewrite the predicate to exempt the lead:

> Every fact in a member of a working documentation set sits under a
> named section, its bucket, except the member's lead paragraph, which
> says what the member is and what it is for.

The lead is what a reader meets after choosing the member from the
index, and `knowledge-organization.the-opening-sentence` already
requires the same thing of an `index.md`. Changing the repo would mean
pushing every member's lead under a heading, which buys navigation
nothing and costs the reader the one sentence that orients them.

### `knowledge-organization.terms` — "A term coined by the work and used in more than one member of a working documentation set is defined in the `Terms` bucket of one `ROOT.md`"

`working-docs/doc-type-system/` obeys: the set root's `Terms` bucket
holds the 27 cross-strand words, and each strand root either adds its
own or links back — `working-docs/doc-type-system/loop/ROOT.md:33`
reads "**Loop** — per [Terms](/working-docs/doc-type-system/ROOT.md#terms)".

`working-docs/software-factory/` breaks. Its `ROOT.md` has no `Terms`
bucket at all — its sections are Goal, "What is here, and where it came
from", "What stayed in the tree", Planned, Completed, Acronyms. The set
coins **seam** at `working-docs/software-factory/docs/tdd.md:23` and
uses it in a second member at
`working-docs/software-factory/docs/refactor-catalogue.md:19`, "Where a
change lands cleanly but leaves an older seam, name, or duplication".
It coins **chunk** at `tdd.md:13` and uses it at
`working-docs/software-factory/docs/index.md`.

**Proposal.** Delete nothing and change nothing here; recommend instead
that the rule's scope be read against
`working-docs/software-factory/ROOT.md:17`, "Each member is as it was on
the day of the move". The set is frozen pending a rewrite-or-delete
decision, so the two terms are a known cost of the freeze rather than a
defect in the set. If the user wants the rule green today, the repo
change is one `## Terms` bucket in
`working-docs/software-factory/ROOT.md` holding **seam** and **chunk**,
two entries lifted from `tdd.md` with `tdd.md`'s uses linking there.

### `knowledge-organization.acronyms` — "Every member of a working documentation set ends with an `Acronyms` appendix, holding a bare `None.` where the member uses no acronym"

Fourteen members carry no `Acronyms` appendix:

- `working-docs/doc-type-system/doc-type-system/body-drain.md`
- `working-docs/doc-type-system/doc-type-system/personal-notes.md`
- `working-docs/doc-type-system/doc-type-system/rule-audit/PROMPT.md`
- the eleven members of `working-docs/software-factory/docs/`:
  `README.md`, `deviation-contract.md`, `factory-operations.md`,
  `node-agent-and-skill-authoring.md`, `pr-feedback.md`,
  `refactor-catalogue.md`, `review-contract.md`, `software-factory.md`,
  `tdd.md`, `user-checkpoints.md`, and `index.md`.

The `index.md` files are outside the population — an index is the set's
root and listing, not a member — so the count above excludes them except
where noted. Every member of `working-docs/doc-type-system/viewer/`,
`fact-base/`, and `loop/` obeys, several with a bare `None.`, so the
appendix is a live convention in the doc-type-system set and absent in
the software-factory set and in the three newest doc-type-system
members.

The predicate's first clause is deterministic: a script reads the last
heading of each member. Its second and third clauses are not, because
deciding that a token is an acronym rather than a shouting filename
(`ROOT`, `PROMPT`, `CLAUDE`) is a judgment call. The trailer's
`stochastic` is right for the predicate as written.

**Proposal.** Change the repo: add the appendix to the three
doc-type-system members that lack it, each ending `## Acronyms` with
its acronyms or a bare `None.`. The set plainly wants it — 12 of its 15
members already carry one, including two with a bare `None.` — so the
three gaps are oversights in recently added files. For
`working-docs/software-factory/docs/`, leave the eleven alone: the set
is frozen as it was on the day of the move, and back-filling appendixes
there edits files the repo has deliberately stopped touching.

## Detectors

**`scripts/okf-lint`** is the only check any rule in this family names.
Its `check_indexes` function, `scripts/okf-lint:553-584`, builds the set
of directories holding an `index.md`, walks every concept document, and
emits `knowledge-organization.an-index-in-every-directory` with the
message "directory holds concept documents but no index.md" for each
directory that holds a concept document and no `index.md` of its own.
The same function emits the neighbouring
`knowledge-organization.the-listing` and
`knowledge-organization.the-root-index` ids, which is why this family's
one checked rule rides a script owned by `standards/knowledge-organization/indexes.md`.

**`src/dev_playbook/md.py`** supplies the boundary the detector tests
against. Its `classify` function, lines 250-297, returns `concept` for
every tracked `.md` file that is not `index.md`, `CLAUDE.md`, or
`SKILL.md`, and not under an `agents/`, `rules/`, or
`skills/*/references/` tree. That single function is what makes the
predicate's "a numbered Decision Record or a `type: Reference` mirror
included" clause checked without further code: both classify as
`concept`, so both pull an `index.md` into their directory.

**`tests/test_okf_lint.py`** pins the behavior at lines 340-357: a
directory holding a concept document and no `index.md` produces one
`standards/factory/index.md: knowledge-organization.an-index-in-every-directory`
finding. The test covers presence only; nothing tests the Decision
Record or Reference-mirror clause directly, which is why that clause's
coverage rests on `classify`'s return value rather than on a case of its
own.

The other 16 rules of this family carry `null` in
`standards/verifiers.yaml:97-161`. Five of them state predicates a
script could decide against repo files today —
`knowledge-organization.the-link-tree`,
`knowledge-organization.where-a-set-lives`,
`knowledge-organization.a-set-stands-on-main`,
`knowledge-organization.working-docs-holds-only-sets`, and
`knowledge-organization.worklist` — and four of those five break on the
tree right now. No script reads `working-docs/` for anything beyond the
index rules, so the whole working-set Standard is unchecked.

## Acronyms

- **OKF** — Open Knowledge Format.
