---
type: General-Sheet
title: Document Types, Type Registry, and Indexes Rule Audit
description: The rule audit over the knowledge-organization/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Document Types, Type Registry, and Indexes Rule Audit

Three Standards of the `knowledge-organization/` family carry 28 rules:
13 in
[Document Types](/standards/knowledge-organization/document-types.md),
8 in [Type Registry](/standards/knowledge-organization/type-registry.md),
and 7 in [Indexes](/standards/knowledge-organization/indexes.md). Every
trailer states the right kind: 0 rules move from deterministic to
stochastic and 0 move the other way. Two rules break — `description-voice`
against 29 Decision Records, and `the-opening-sentence` against two
indexes. Five are weakly checked: `types`, `local-declaration`,
`the-listing`, `ordering`, and `the-root-index`. Eight have no check at
all: `description-voice`, `resource`, `resource-names-the-asset`,
`no-tags-or-timestamp`, `global-table`, `row-description`, `typeless`,
and `the-opening-sentence` — five of those eight are deterministic, so a
script could decide them today. Three are low value:
`resource-names-the-asset`, `no-tags-or-timestamp`, and `global-table`.
One detector, `scripts/okf-lint`, decides all 15 checked rules.

| id | rule | kind | proposed | check | state | overlap | value | note |
|----|------|------|----------|-------|-------|---------|-------|------|
| `knowledge-organization.frontmatter-block` | A concept document opens with a `---`-delimited frontmatter block whose YAML is a mapping. | deterministic | deterministic | full | holds | none | high | Test: `md.parse_frontmatter` returns a dict. okf-lint `check_types` reports absent, malformed, and non-mapping frontmatter alike. 145 concept docs pass. |
| `knowledge-organization.types` | A concept document's frontmatter has a `type` key whose value names one row of the table below, or one entry of the `okf_types` mapping in the frontmatter of the repo's own root `index.md` ([Type Registry](/standards/knowledge-organization/type-registry.md#local-declaration)). | deterministic | deterministic | weak | holds | none | high | The code ignores `okf_types` in apex mode, so the predicate's second disjunct is dead in dev-playbook. 145 docs draw on 10 of the table's 13 types. |
| `knowledge-organization.title` | A concept document's frontmatter has a `title` key with a non-empty value. | deterministic | deterministic | full | holds | none | high | Test: `fm.get("title")` is truthy. All 145 concept docs carry one. |
| `knowledge-organization.description` | A concept document's frontmatter has a `description` key whose value is non-empty and does not end with a period. | deterministic | deterministic | full | holds | none | high | Test: non-empty, and `rstrip()` does not end in `.`. All 145 pass. |
| `knowledge-organization.description-voice` | A concept document's `description` is a sentence fragment in the present tense that names what the document is or what it governs. | stochastic | stochastic | none | breaks | none | high | 29 Decision Records name the decision in the imperative, not the document. See the escalation. |
| `knowledge-organization.resource` | A concept document's `resource`, where present, is a repo-root path beginning with `/` or an external URI. | deterministic | deterministic | none | holds | none | high | Test: the frontmatter value starts with `/` or carries a URI scheme. 3 members, all conforming. No verifier row. |
| `knowledge-organization.resource-names-the-asset` | A concept document's `resource`, where present, names the asset the document describes, never a companion file that only supports it. | stochastic | stochastic | none | holds | none | low | 3 members: the OKF spec's upstream URL and two workflow `.js` files. The explanation already carries the worked example. |
| `knowledge-organization.no-tags-or-timestamp` | A concept document's frontmatter has no `tags` key and no `timestamp` key. | deterministic | deterministic | none | holds | none | low | No member carries either key and nothing in the repo writes frontmatter. 29 records carry `date`, 30 Standards carry `population`; neither is banned. |
| `knowledge-organization.recipe-description` | A concept document typed `Recipe-Description` has a `resource` key with a non-empty value. | deterministic | deterministic | full | holds | none | high | Test: `RESOURCE_REQUIRED_TYPES`. Both members, `harness-recipes/recipes/ralph-loop.md` and `scatter-gather.md`, carry one. |
| `knowledge-organization.typed-standard` | A concept document typed `Standard` lives under `standards/`. | deterministic | deterministic | full | holds | none | high | Test: `rel.startswith("standards/")`. All 30 Standard-typed docs comply. `standard.directory-layout` states the converse; neither subsumes the other. |
| `knowledge-organization.typed-loop` | A concept document typed `Loop` lives under `loops/`. | deterministic | deterministic | full | holds | none | high | Test: `rel.startswith("loops/")`. Vacuous today — `loops/index.md` says "None is written yet". |
| `knowledge-organization.typed-guide` | A concept document typed `Guide` lives under `guides/`. | deterministic | deterministic | full | holds | none | high | Test: `rel.startswith("guides/")`. All 6 Guide-typed docs are under `guides/`. |
| `knowledge-organization.typed-explanation` | A concept document typed `Explanation` is `standards/<name>/explanation.md`. | deterministic | deterministic | full | holds | none | high | Test: `EXPLANATION_PATH` full-match. All 13 Explanations sit one per Standard directory; `documentation-sets/` has none, as the regex demands. |
| `knowledge-organization.global-table` | The declaration is the `## Types` table of `standards/knowledge-organization/document-types.md`, in the repo that carries `standards/build/canonical/`. | deterministic | deterministic | none | holds | none | low | okf-lint raises and exits 2 on an unusable registry rather than emitting this id. The lead paragraph of type-registry.md already states the same fact. |
| `knowledge-organization.row-shape` | Every row of the `## Types` table below its header holds, in its first cell, one backticked type name in Title Case, hyphen-joined for a multi-word name: `Decision-Record`, `Candidate-List`, `README`. | deterministic | deterministic | full | holds | `knowledge-organization.mapping-entry-shape` | high | Test: `BACKTICK_NAME` plus `TYPE_NAME`. All 13 rows pass. `mapping-entry-shape` states the same name shape for the consumer's mapping. |
| `knowledge-organization.row-description` | Every row of the `## Types` table below its header holds, in its second cell, a non-empty one-line description of what the type is. | deterministic | deterministic | none | holds | `knowledge-organization.mapping-entry-shape` | high | Test: cell 2 non-empty and single-line; "of what the type is" is purpose, not a further test. All 13 rows pass. `parse_registry` already splits the cells. |
| `knowledge-organization.alphabetical-order` | The rows of the `## Types` table are in alphabetical order by type name, compared case-insensitively. | deterministic | deterministic | full | holds | `knowledge-organization.alphabetical-keys` | high | Test: `_is_alphabetical`. The 13 rows run `Candidate-List` to `Vocabulary` in order. Same predicate as `alphabetical-keys`, other population. |
| `knowledge-organization.local-declaration` | The declaration is the `okf_types` mapping in the frontmatter of the root `index.md` of a repo that does not carry `standards/build/canonical/`, one entry per document type the repo declares for itself. | deterministic | deterministic | weak | holds | none | high | The code tests two things only: `okf_types` is a mapping, and no legacy registry document remains. See the escalation. Vacuous here — dev-playbook is apex. |
| `knowledge-organization.mapping-entry-shape` | Each entry's key is a type name in Title Case, hyphen-joined for a multi-word name, and its value is a non-empty one-line description of the type. | deterministic | deterministic | full | holds | `knowledge-organization.row-shape` | high | Test: `_is_type_name` on the key, non-empty newline-free string on the value. Vacuous here; fixtures in `tests/test_okf_lint.py` cover it. |
| `knowledge-organization.alphabetical-keys` | The keys of the `okf_types` mapping are in alphabetical order by type name, compared case-insensitively. | deterministic | deterministic | full | holds | `knowledge-organization.alphabetical-order` | high | Test: `_is_alphabetical` over the keys that passed the shape test. Vacuous here; fixtures cover it. |
| `knowledge-organization.add-never-shadow` | No key of the `okf_types` mapping equals a type name of the `## Types` table, or an earlier key of the same mapping, compared case-insensitively. | deterministic | deterministic | full | holds | none | high | Test: lowercased key against the lowercased upstream set and the keys seen so far. Vacuous here; fixtures cover both arms. |
| `knowledge-organization.typeless` | An `index.md` carries no OKF `type`. | deterministic | deterministic | none | holds | none | high | Test: no `type` key in the index's frontmatter. 39 indexes checked; 9 carry frontmatter and all 9 hold `okf_version` alone. `md.classify` routes an index past `check_types`, so nothing decides this id. |
| `knowledge-organization.the-introduction` | An `index.md` holds prose between its H1 and its first listed entry. | deterministic | deterministic | full | holds | none | high | Test: `check_index_intro` wants one non-empty line that is neither a heading nor the `Ordering:` marker. All 39 indexes carry one. |
| `knowledge-organization.the-opening-sentence` | The introduction of an `index.md` opens with a single sentence naming what the directory holds, in that directory's own vocabulary; where the listing's sole entry carries a `description` that already says what the directory holds, the sentence says what the directory is for instead. | stochastic | stochastic | none | breaks | none | high | Two indexes restate their own path and add nothing. See the escalation. |
| `knowledge-organization.the-listing` | An `index.md` lists, as a bullet holding a root-absolute markdown link and exactly once each, every concept document in its own directory and every child directory's own `index.md`, and lists nothing else; each concept document's entry carries that document's frontmatter `description` verbatim. | deterministic | deterministic | weak | holds | `standard.the-catalog` | high | "exactly once each" is not tested for child-index bullets. All 39 indexes list what they own. `standard.the-catalog` restates this for `standards/index.md` and cites it. |
| `knowledge-organization.ordering` | Within each group of an `index.md`'s listing, the concept documents and then the child-directory links, entries are in alphabetical order by link title, compared case-insensitively, and a `README.md` entry is the first entry of the whole listing; an introduction line beginning `Ordering:`, one before the first listed entry, releases the alphabetical order of both groups and never the `README.md` entry's place. | deterministic | deterministic | weak | holds | `standard.the-catalog` | high | The README-first test reads the concept group only, and the group order itself is untested. All 39 indexes obey both. |
| `knowledge-organization.the-root-index` | The `index.md` at the repository root. | deterministic | deterministic | weak | holds | none | high | The sentence is a noun phrase, so it states no predicate; the code tests that the file exists. `index.md` is present at the root. See the escalation. |
| `knowledge-organization.okf-version-declared` | The `index.md` at the repository root declares `okf_version` in its frontmatter. | deterministic | deterministic | full | holds | none | high | Test: `okf_version` in the root index's frontmatter. The root declares `okf_version: "0.1"`. Eight non-root indexes declare it too, which the predicate neither asks for nor forbids. |

## Escalations

### `knowledge-organization.description-voice` — A concept document's `description` is a sentence fragment in the present tense that names what the document is or what it governs

The predicate asks for a fragment that names **what the document is or what
it governs**. Every one of the 29 Decision Records under `docs/decisions/`
instead names the decision, in the imperative:

- `docs/decisions/0001-adopt-matt-pocock-conventions.md:4` —
  `description: Adopt Matt Pocock's repository conventions wholesale — ...`
- `docs/decisions/0029-retire-instruments.md:4` —
  `description: Delete the Instruments standard, the Instrument-Spec type,
  and both instruments — ...`
- `docs/decisions/0012-one-published-hook.md:4` —
  `description: Collapse the published per-detector hook ids into one
  playbook-lint aggregate ...`

This is not drift. The Decision Record template mandates it:
`standards/decisions/records.md:76` holds
`description: {One-line summary of the decision, for triage and the index}`,
and `standards/decisions/explanation.md:74` calls the `description` "the
record's triage line". A summary of a decision is not a name for the
document. Twenty-six of the 29 open with a bare verb — `Adopt`, `Decline`,
`Cut`, `Reorganize`, `Remove`, `Collapse`, `Delete` — so the two Standards
give a writer of a Decision Record two incompatible instructions.

No detector decides this rule; the verifier row is null
(`standards/verifiers.yaml:107`), which is why the conflict has stood.

**Proposal.** Rewrite the predicate so it states what the repo does on
purpose:

> A concept document's `description` is a sentence fragment in the present
> tense that names what the document is, what it governs, or, for a
> `Decision-Record`, the decision it records.

A repo change would mean rewriting 29 immutable records, which
`decisions.immutable-after-merge` forbids outright. A delete would drop the
only statement of what a `description` sounds like, and 145 index rows carry
that description verbatim, so a reader needs it.

### `knowledge-organization.the-opening-sentence` — The introduction of an `index.md` opens with a single sentence naming what the directory holds, in that directory's own vocabulary

The explanation is explicit about the failure mode: "Restating the path is
not an introduction: 'the files in `standards/`' tells a reader nothing the
H1 did not"
(`standards/knowledge-organization/explanation.md:173`). Two of the repo's
39 indexes do exactly that.

- `docs/writing-improvement-process/index.md:3` — H1 is
  `# docs/writing-improvement-process/ — index`; the opening sentence is
  "The writing-improvement process's files." The sentence restates the
  directory name and the word "files", and names nothing the H1 did not.
  The index lists two entries, so the sole-entry clause does not apply.
- `doc-types/runbook/index.md:7` — H1 is `# doc-types/runbook/ — index`;
  the opening sentence is "The Runbook doc-type." Its three sibling
  indexes each name the thing: `doc-types/loop/index.md` opens "The Loop
  doc-type: the document that drives a state toward a target state — its
  definition, contract shape, encoding, and residual ledger."

okf-lint checks presence only — `check_index_intro`'s docstring says "what
the sentence says is a reviewer's judgment" — so neither is reported.

**Proposal.** Change the repo. Both sentences are oversights rather than
intent: 37 of the 39 indexes already name their subject in the directory's
own vocabulary, and `doc-types/runbook/index.md` sits beside two siblings
written to the full pattern, so the form the repo wants is not in doubt.
The files that change are `docs/writing-improvement-process/index.md` and
`doc-types/runbook/index.md`, one sentence each.

### `knowledge-organization.types` — A concept document's frontmatter has a `type` key whose value names one row of the table below, or one entry of the `okf_types` mapping in the frontmatter of the repo's own root `index.md`

The code is stricter than the predicate, not looser. `scripts/okf-lint:805`
sets `apex_mode` from the presence of
`standards/build/canonical/.pre-commit-config.yaml`, and lines 808-809 then
take the registry from the `## Types` table alone. The comment above them,
line 801, says so outright: "its okf_types key, were one ever written, is
ignored." `check_local_types` runs only in the else branch, at line 813.
`tests/test_okf_lint.py:951`,
`test_apex_mode_ignores_okf_types`, pins that behavior.

So in dev-playbook the predicate's second disjunct accepts a type that the
code rejects. The neighbouring Standard already says why: the
`local-declaration` predicate scopes `okf_types` to "a repo that does not
carry `standards/build/canonical/`". `document-types.md` carries no such
scope.

### `knowledge-organization.local-declaration` — The declaration is the `okf_types` mapping in the frontmatter of the root `index.md` of a repo that does not carry `standards/build/canonical/`, one entry per document type the repo declares for itself

The code emits this id at two sites only. `scripts/okf-lint:352` reports
`okf_types` that is not a mapping. `scripts/okf-lint:418` reports a legacy
registry **document** left at either historical path. Three things the
predicate states go untested:

- **Where the mapping lives.** Nothing reports an `okf_types` mapping in a
  non-root `index.md`, or in a document under the consumer's own
  `standards/` tree other than the two legacy paths.
- **The apex exclusion.** A repo that carries
  `standards/build/canonical/` and also declares `okf_types` draws no
  finding; apex mode reads the key and discards it in silence.
- **One entry per type.** Nothing tests that each declared type is one the
  repo actually uses, nor that a type the repo uses is declared — an
  undeclared type surfaces under `types` instead, against the document
  rather than against the declaration.

### `knowledge-organization.the-listing` — An `index.md` lists, as a bullet holding a root-absolute markdown link and exactly once each, every concept document in its own directory and every child directory's own `index.md`, and lists nothing else

Two clauses go untested.

- **"exactly once each", for child indexes.** `scripts/okf-lint:644` folds
  the parsed child links into a set, `listed_child_set = set(listed_children)`,
  before comparing. A concept document listed twice is reported — the
  `Counter` at line 609 does that, and `tests/test_okf_lint.py:521` covers
  it — but a child `index.md` bullet repeated twice is silently collapsed.
- **"lists nothing else", for a non-link item.** `parse_index` keeps only
  lines matching `INDEX_BULLET`, which demands `[text](/root-absolute)`. A
  bullet carrying bare text, or a relative link, is dropped rather than
  reported. The omission it causes still surfaces, as "omits concept doc",
  but the stray row itself never does.

A third difference runs the other way and is not a weakness: the code
assigns a concept document to the **nearest** index at or above it, not to
its own directory. `knowledge-organization.an-index-in-every-directory`
keeps the two readings equal in practice, and the repo has no directory that
holds a concept document without an `index.md`.

### `knowledge-organization.ordering` — Within each group of an `index.md`'s listing, the concept documents and then the child-directory links, entries are in alphabetical order by link title, compared case-insensitively, and a `README.md` entry is the first entry of the whole listing

Two clauses go untested.

- **"the first entry of the whole listing".** `scripts/okf-lint:745-751`
  splits the bullets into `child_titles` and `group_a`, then looks for the
  `README.md` entry inside `group_a` alone. A child-directory bullet placed
  above the `README.md` bullet leaves `readmes[0] == 0`, so no finding is
  emitted although the README is no longer first in the file.
- **The group order itself.** The predicate names two groups in order, "the
  concept documents and then the child-directory links". `check_index_ordering`
  sorts each group's titles but never tests that every concept bullet
  precedes every child bullet. An index that interleaves them passes.

All 39 indexes obey both clauses today, so this is latent, not live.

### `knowledge-organization.the-root-index` — The `index.md` at the repository root

The predicate is a noun phrase. It has no verb and states nothing that can
be true or false of a member, so no member can break it and no script can
decide it as written. This is the condition heading of
`okf-version-declared`, and `doc-type.the-rule-shape` does allow a level-two
heading to be a condition — but the heading also carries a trailer,
`` `knowledge-organization.the-root-index` · deterministic ``
(`standards/knowledge-organization/indexes.md:70`), and a verifier row
naming `scripts/okf-lint` (`standards/verifiers.yaml:149`).

The code tests something the sentence does not say. `scripts/okf-lint:563`
returns a single finding, "repository root index.md is missing", when no
`index.md` sits at the root, and returns early — every other index check is
skipped for that run. The repo passes: `index.md` is present and declares
`okf_version: "0.1"`.

## Detectors

**`scripts/okf-lint`** is the only detector this family names, and it
decides all 15 checked rules. It walks the repository's markdown through
`md.find_md_files`, splits it with `md.classify` into concept documents,
indexes, harness-owned files and excluded ones, and runs four passes.
`check_types` reads each concept document's frontmatter and emits
`frontmatter-block`, `types`, `title`, `description`, `recipe-description`
and the four `typed-*` rules. `check_indexes` builds the ownership map and
emits `the-listing`, `an-index-in-every-directory`, `the-root-index` and
`okf-version-declared`. `check_index_intro` and `check_index_ordering` emit
`the-introduction` and `ordering`. A fifth pass depends on the mode:
`check_registry` in apex mode emits `row-shape` and `alphabetical-order`
against the `## Types` table, and in consumer mode `check_local_types` and
`check_legacy_registry` emit `local-declaration`, `mapping-entry-shape`,
`alphabetical-keys` and `add-never-shadow` against the root index's
`okf_types`.

The script is not a thin shim: it holds its rule logic inline rather than
in `src/dev_playbook/`, unlike `scripts/standards-lint` and its siblings.
That is `standard.thin-shims`' business, not this family's, but it means
the family's whole checking surface sits in one 842-line file.

**`src/dev_playbook/md.py`** decides the family's boundary rather than any
rule of it. `classify` returns `"index"` for any `index.md`, which is why
no concept-document rule ever reaches one — and why
`knowledge-organization.typeless` has no detector. `parse_frontmatter`
decides `frontmatter-block`, `content_lines` and `lines_outside_fences`
keep a fenced example from reading as a listing entry, and
`find_md_files` scopes the walk to `git ls-files`, so `node_modules/` and
`.venv/` never enter the population.

**`src/dev_playbook/findings.py`** renders every finding line and prints
`--list-rules`. It decides no rule of this family; it fixes the output
format that `standard.finding-format` states.

Three docstrings in `scripts/okf-lint` name a rule id that does not exist,
`knowledge-organization.registry-row`: `check_registry`'s, at both of its
mentions, and `check_local_types`'. The code at those sites emits
`ROW_SHAPE`, `ALPHABETICAL_ORDER`, `LOCAL_DECLARATION`,
`MAPPING_ENTRY_SHAPE`, `ALPHABETICAL_KEYS` and `ADD_NEVER_SHADOW` instead.
The ids are defined as module constants precisely so `RULES` cannot drift
from what is emitted, and it has not; only the prose around them is stale.

## Acronyms

- **H1** — markdown heading level one.
- **OKF** — Open Knowledge Format.
- **URI** — Uniform Resource Identifier.
- **URL** — Uniform Resource Locator.
- **YAML** — YAML Ain't Markup Language.
