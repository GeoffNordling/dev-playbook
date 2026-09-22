---
type: General-Sheet
title: Rule Rulings
description: Every rule in standards/ with its ruling and the text the ruling needs, by family, plus the Guides the moved rules land in, the repo changes, the contested calls, and the order of the step 11 pass
---

# Rule Rulings

One row per rule in `standards/`, from the step 11 audit: the ruling on
the rule, and beside it the text the ruling needs — the new sentence, the
`> **Why.**` block, the Guide the rule moves to, or the block the rule
keeps its sentence over. The rulings came from one sort of all 284
trailers by the decidability test, kept per rule in
[Rules by family](#rules-by-family) below.
[Rule Audit Decision Sheet](/working-docs/doc-type-system/doc-type-system/rule-audit/decision-sheet.md)
is the evidence behind them, the auditors' findings and the reviewers'
verdicts; where a verdict and a ruling differ, the ruling stands and
[Contested calls](#contested-calls) says why.

The ruling per rule is final. An agent applying this document applies the
ruling as written and never re-judges it. Where the file no longer
matches a row — the rule is already gone, its sentence already changed,
or a why block already stands — the agent leaves that rule as it is and
reports the row with both readings; the orchestrator rules from the
principles of
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles).
Any count a reader tallies from the tables is not a test an agent must
satisfy: a family whose result differs reports the difference and the
rows behind it, and the rows are what is checked.

The rulings were reconciled after step 10 closed. The Explanation type is
gone, so every why this document names is a `> **Why.**` block after the
rule's trailer
([The rule shape](/standards/doc-type/standard-conventions.md#the-rule-shape));
the verbatim-mirror type is `Mirror`; Runbook's chain is the chain; and a
Guide is written in Sequence, Step, and Reference
([Instruction Encoding](/doc-types/guide/encoding.md)). The sort covered
the 284 trailers of its day. Nine rules written since, to the principles,
are outside it and stand as written: the seven of `guide-conventions.md`,
and `doc-type.the-documents-why` and `doc-type.a-why-states-no-predicate`
in `standard-conventions.md`. The sort's
`knowledge-organization.typed-explanation` row is void and is not below;
the rule went with the type.

The pass applies the Principles of
[Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles):
a predicate is a test over state; kind is judged from the sentence; a
scoping heading is not a rule; and the three working policies. Their
permanent home after the pass is `standard-conventions.md` itself: a
predicate is a test over state, and kind is judged from the sentence,
become the why block of
[Decidable predicates](/standards/doc-type/standard-conventions.md#decidable-predicates);
a scoping heading is not a rule becomes the why block of
[The rule shape](/standards/doc-type/standard-conventions.md#the-rule-shape).
The three working policies are audit policy, a reason for no rule, and
stay in the strand root. A Standard holds only predicates, so none of
them is written as a rule.

## Guides

Where the rules that are not predicates go. Each rule's current text is the seed; the Guide is organised by the work, not by the rule list, and written in Sequence, Step, and Reference per [Instruction Encoding](/doc-types/guide/encoding.md) and [Guide Conventions](/standards/doc-type/guide-conventions.md): a run of actions is a sequence, a thing consulted is a reference, and the headings read down are the gist. Every Guide gets an `index.md` row under `guides/`. The Guides are written before the rules they take are deleted, so the seed text is still in place. The sheet rules these rows `delete; intent to guide`; the two readings agree, the rule leaves the Standard and its intent lands here.

- **`guides/writing-a-detector.md`** (new Guide; read before writing a first-party detector). The detector contract: exit 0 clean, 1 findings, 2 cannot run; `--list-rules`; the finding line; an absent surface is clean; why the gate must not write. Takes: `standard.exit-codes`, `standard.list-rules`, `standard.finding-format`, `standard.an-absent-surface-is-clean`.
- **`guides/design-and-testing.md`** (new Guide; read before writing code or tests). Deep modules, ports and adapters, dependencies accepted not constructed; the testing philosophy: observable outcomes, fakes at ports, the lightest double, one concept per test; fail loudly; docstrings say what a thing does; a sourced fragment mutates the parent shell only. Takes: `modules.deep-not-shallow`, `modules.internal-seams-stay-inside`, `modules.two-adapters-or-no-seam`, `modules.dependencies-are-accepted-not-constructed`, `modules.a-port-at-a-process-boundary`, `modules.the-interface-is-the-test-surface`, `python.docstring-content`, `python.fail-loudly`, `shell.bounded-to-shell-integration`, `testing.arrange-act-assert`, `testing.one-concept-per-test`, `testing.expected-values-come-from-outside-the-code`, `testing.assert-on-observable-outputs`, `testing.assert-on-outcomes-not-call-sequences`, `testing.name-by-capability-not-mechanism`, `testing.replace-dont-layer`, `testing.no-test-of-a-non-deterministic-decision`, `testing.the-lightest-double`, `testing.double-at-the-port`, `testing.fakes-for-stateful-dependencies`, `testing.one-fake-per-interface`, `testing.fakes-implement-only-what-callers-use`, `testing.mocks-at-boundaries-only`, `testing.fixtures-for-setup-and-teardown`, `testing.narrowest-fixture-scope`.
- **`guides/repo-settings.md`** (`standards/tracking/repo-settings.md` retyped `Guide` and moved; read when creating or auditing a governed repo on GitHub). The GitHub side of tracking: origin, merge settings, branch protection, the label set bootstrap-labels mints, one tracker per repo. Takes: `tracking.github-origin`, `tracking.squash-only-merges`, `tracking.default-branch-protection`, `tracking.valid-labels`, `tracking.one-home`.
- **`guides/governed-repo.md`** (new Guide; read when adding a repo to the workspace or writing a Decision Record). Which repos are governed and where the roster lives; what one Decision Record covers; a merged record is frozen; a working set is published on main. Takes: `distribution.the-roster`, `decisions.scope`, `decisions.immutable-after-merge`, `knowledge-organization.a-set-stands-on-main`.
- **`guides/writing-for-agents.md`** (existing Guide; read before writing a runbook or skill). A step ends on the condition that tells the agent the work is done; it joins the reference `Steps and completion criteria`. Takes: `doc-type.steps-end-on-a-completion-criterion`.

## Repo changes

Small, named, and confirmed by a reviewer as oversights. Each is one commit-sized edit in the PR. None has landed yet.

- `doc-type.interactive-skills-inherit`: three skills gain `model: inherit`: runbook-creator, enable-repo-governance, update-standards-pin.
- `harness.one-rule-per-heading`: `dotfiles/dot-claude/CLAUDE.md`: the repeatable-work rule moves under `## Behaviors`.
- `knowledge-organization.terms-that-cross-sets`: `CONTEXT.md` gains entries for strand and bucket.
- `knowledge-organization.the-link-tree`: this set's `ROOT.md` links the `rule-audit/` files; `software-factory/ROOT.md` is frozen pending deletion and stays.
- `knowledge-organization.acronyms`: acronym appendix added to `body-drain.md`, `personal-notes.md`, and every file under `rule-audit/` that lacks one, all but this one.
- `knowledge-organization.the-opening-sentence`: `docs/writing-improvement-process/index.md` and `doc-types/runbook/index.md` open by naming their contents.
- `prose.no-slop-tics`: `harness-recipes/README.md`: two flourishes cut.
- `prose.heading-casing`: rule gains "the `Considered Options` heading of a Decision Record is exempt"; `wayfinder/SKILL.md` heading recased.
- `prose.grammatical-parallelism`: four `prose/conventions.md` headings made parallel; their ids follow in `verifiers.yaml`, `working-documentation-sets.md`, `agents/doc-set-deslopper.md`.
- `knowledge-organization.no-agent-instructions-or-decisions`: the settings-symlink design in `dotfiles/README.md` becomes a Decision Record; the README keeps a pointer.
- `prose.third-person`: `you` rewritten to third person in six declarative documents, `guides/writing-for-agents.md` the largest at eleven uses.
- `standard.thin-shims`: the five shims that carry rule logic move it into the package, in the detector step.

## Contested calls

Rows where the reviewer disagreed with the auditor, decided here.

| rule | reviewer | decision |
|---|---|---|
| [doc-type.steps-end-on-a-completion-criterion](/standards/doc-type/runbook-conventions.md#steps-end-on-a-completion-criterion) | reviewer: delete, two skills end steps on actions | guide: the idea is sound and unchecked; it joins `writing-for-agents.md` |
| [knowledge-organization.inline-code-for-a-varying-location](/standards/knowledge-organization/cross-references.md#inline-code-for-a-varying-location) | reviewer: keep, no conflict with `index.md` | keep |
| [knowledge-organization.terms](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#terms) | reviewer: keep, "seam" is Feathers' term and the other set is frozen | keep |
| [knowledge-organization.no-agent-instructions-or-decisions](/standards/knowledge-organization/readme-content.md#no-agent-instructions-or-decisions) | reviewer: repo change, the README argues a design | repo change: one Decision Record, small and named |
| [prose.point-at-canonical-artifacts](/standards/prose/conventions.md#point-at-canonical-artifacts) | reviewer: rewrite, not subsumed by one-home | rewrite as the reviewer's sentence |
| [prose.block-form-fits-its-content](/standards/prose/conventions.md#block-form-fits-its-content) | reviewer: keep the predicate, fix one bullet | keep; bullet edited |
| [prose.third-person](/standards/prose/conventions.md#third-person) | reviewer: repo change, the cited files are plain prose | repo change: six files, mechanical edits |
| [prose.name-concepts-once-use-consistently](/standards/prose/conventions.md#name-concepts-once-use-consistently) | reviewer: keep, two concepts not one | keep |
| [decisions.template](/standards/decisions/records.md#template) | reviewer: rewrite, delete loses the frontmatter contract | rewrite: frontmatter and H1; the sentence-count line leaves the template |
| [doc-type.one-sentence](/standards/doc-type/doc-type.md#one-sentence) | reviewer: rewrite, only the "what it does" clause is taste | rewrite |
| [build.lockfile-committed](/standards/build/skeleton.md#lockfile-committed) | reviewer: keep because repo-lint emits the id | delete; the check goes with it |
| [distribution.a-pinned-rev](/standards/distribution/channel.md#a-pinned-rev) | reviewer: keep because workspace-lint emits the id | delete; the check goes with it |

## Detector fixes

The 16 rules whose detector tests less than the sentence. The sentence stands in this PR; the detector closes the gap named in the decision sheet's Weak checks section in the detector phase, with the thin-shim moves and the `doc-type.one-base` check. Not in this PR.

`build.pre-commit-configyaml`, `build.the-source-directory`, `doc-type.entries-point-and-condition`, `doc-type.references-one-level-deep`, `doc-type.three-verb-sections`, `knowledge-organization.fragment-anchor-matches-the-slug`, `knowledge-organization.h1`, `knowledge-organization.link-same-bundle`, `knowledge-organization.ordering`, `knowledge-organization.the-listing`, `knowledge-organization.types`, `prose.no-first-person`, `prose.the-repo-vocabulary`, `standard.the-boundary-table`, `tracking.closed-fences`, `tracking.wayfinder-body`.

## Verifier and boundary tables

`verifiers.yaml` loses 80 rows, the deletes, Guide moves, and conditions. Trailer changes: `doc-type.one-base` to deterministic, `standard.read-only` to stochastic, `tracking.artifacts` to stochastic. Both tables are regenerated by `verifier-table --write` and `boundary-table --write` after the edits and must round-trip clean.

## Order

This document designs phase one. Phase two is planned in the strand root, not here.

**Phase one, documents, this PR.** Rules move to their right homes, judged sentences change, the Guides and why blocks are written into the shapes step 10 built, trailers and the two yaml tables update. Script edits are only what the gate forces: a detector that emits a deleted rule id stops emitting it, and the tables round-trip clean. No detector logic changes and no new check is written.

1. Guides first: the four new Guides and the Writing for Agents reference, one agent per Guide, from the rule text still in place.
2. Family passes, one agent per family, in parallel: conditions stripped, deletes and Guide-move rules removed with their why blocks, new sentences pasted, why blocks written, trailers changed. Each agent edits its family's Standards only and reports every row it could not apply.
3. The Principles into `standard-conventions.md`'s why blocks, with the doc-type family pass.
4. Repo changes, one agent, from the list above.
5. The orchestrator: emitters of deleted ids silenced with their tests; regenerate the two tables; `playbook-lint` and `make test` pass; `pre-commit run --all-files` no slower than before.
6. PR for the user to merge.

**Phase two, detectors.** Step 12 of [Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned), after this PR merges. Not designed here.

A delete takes the rule, its trailer, its `verifiers.yaml` row, and its
why block, and a detector check that emits the id goes with it. The
emitters: `testing_lint` for `testing.access-only-public-names` and
`testing.no-logic-in-tests`, `workspace_lint` for
`distribution.a-pinned-rev`, and the `mypy` entry of `DEPENDENCY_RULES`
in `verifier_table.py`, which names `python.annotated-signatures` alone
and goes with it, as does `mypy` from `boundaries.yaml`. Their tests go
with the checks. Every Guide-move row is deleted the same way.

A condition loses its trailer line and its `verifiers.yaml` row; the
heading and its sentence stay, and no why block is added to a condition.
The shape is written once, in the rewritten
[doc-type.the-rule-shape](/standards/doc-type/standard-conventions.md#the-rule-shape).
standards-lint learns it in the detector phase; until then an H2 without
a trailer is unenforced, as it is today.

## Rules by family

One `###` subsection per Standard family directory under `standards/`,
in alphabetical order of directory name; within a family, rows are in
`standards/` file order. `text` is empty where the ruling needs none.

### build

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `build.ciyml` | build/canonical.md | deterministic | keep |  | Byte compare of the repo copy against a file in this checkout; no judgment. |
| `build.python-version` | build/canonical.md | deterministic | keep |  | Byte compare of the repo copy against a file in this checkout; no judgment. |
| `build.pre-commit-configyaml` | build/canonical.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Verbatim block match with stated allowances and a named exemption; every term reads from files. |
| `build.makefile` | build/canonical.md | deterministic | keep |  | Fragment choice and the code-roots substitution both read from the tree; verbatim compare follows. |
| `build.artifactsmk` | build/canonical.md | deterministic | keep |  | Where the file exists, its variable and its rule targets are read from the file itself. |
| `build.pyprojecttoml` | build/canonical.md | deterministic | keep |  | Named TOML keys are compared to pinned values; placeholders resolve from the repo directory name. |
| `build.gitignore` | build/canonical.md | deterministic | keep |  | Pattern containment against a file in this checkout; comments and order explicitly free. |
| `build.one-version-set` | build/canonical.md | deterministic | residue to predicate; intent to explanation | Sentence: Every version the canonical artifacts pin in more than one file carries the same value in each<br>Why: The pins are meant to be the latest stable releases, bumped together; that is why a version pinned in two files must agree. | "Latest stable release" is a fact on the internet, not in the files; trailer says deterministic but no file decides it. |
| `build.the-source-directory` | build/canonical.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Listing the directory and the Standard's own rules decides both clauses; binds dev-playbook, not each governed repo. |
| `build.name-mapping` | build/python.md | deterministic | rewrite (new sentence in text) | Sentence: The root `pyproject.toml` sets `project.name` to the repository's own name lowercased, the directory holding the shared `.git` and so the same from the main checkout and every worktree, `My-Repo` to `my-repo`, and the import package is that name with each hyphen an underscore, `my_repo`. | The repo directory name and pyproject.toml are both in the checkout; the mapping is mechanical. |
| `build.entry-points` | build/python.md | deterministic | rewrite (new sentence in text) | Sentence: `[project.scripts]` in the root `pyproject.toml` is absent, or every entry under it has the value `<module>:main`, where `<module>` is a module inside the import package and that module defines `main`. | Absence or an exact value string, plus a main defined in a named file; all readable. |
| `build.scripts` | build/python.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Defines which files the level-three shebang rule binds; names no obligation a repo can fail. |
| `build.shebang-and-inline-metadata` | build/python.md | deterministic | keep |  | First line and inline block are read from the file; the floor is read from .python-version. |
| `build.required-files` | build/skeleton.md | deterministic | keep |  | Existence of named paths at stated places; no judgment. |
| `build.root-only-files` | build/skeleton.md | deterministic | keep |  | Existence and location of three named files across the tree; no judgment. |
| `build.no-other-future-work-file` | build/skeleton.md | deterministic | keep |  | Absence of four named filenames at any depth; no judgment. |
| `build.runnables-live-in-scripts` | build/skeleton.md | deterministic | keep |  | Sentence forbids two named root directories; the heading states the reason, the sentence is the check. |
| `build.dependencies-live-in-pyprojecttoml` | build/skeleton.md | deterministic | keep |  | Absence of one named filename anywhere in the tree; the heading states the reason. |
| `build.python` | build/skeleton.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names the layer the uv.lock rule binds; a repo without pyproject.toml is outside it, not failing. |
| `build.uvlock-and-python-version` | build/skeleton.md | deterministic | keep |  | Tracked state and existence both read from the tree at one commit, not from history. |
| `build.python-package` | build/skeleton.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names the layer the one-package rule binds; the tree diagram is illustration, not obligation. |
| `build.one-package-under-src` | build/skeleton.md | deterministic | keep |  | Entry count under src/ and the name from the mapping are both read from the checkout. |
| `build.python-source` | build/skeleton.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names the layer the tests-present rule binds; a disjunction over tree facts, not an obligation. |
| `build.tests-present` | build/skeleton.md | deterministic | keep |  | Existence and non-emptiness of one directory; no judgment. |
| `build.javascript` | build/skeleton.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names the layer the lockfile rule binds; a repo without package.json is outside it, not failing. |
| `build.lockfile-committed` | build/skeleton.md | deterministic | delete |  | One of five named files tracked beside package.json; read from the tree at one commit. |

### decisions

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `decisions.the-bar` | decisions/records.md | stochastic | keep |  | Hard to reverse, surprising, a real trade-off: a reader judges these from the record and the repo it sits in. |
| `decisions.scope` | decisions/records.md | stochastic | delete; intent to guide | Guide: `guides/governed-repo.md` | "The repo it governs" and "governs several repos" range over other checkouts; a placement instruction to the writer. |
| `decisions.the-directory` | decisions/records.md | deterministic | keep |  | The directory listing decides it: numbered records, one index.md, one README.md, nothing else. |
| `decisions.sequential-numbering` | decisions/records.md | deterministic | keep |  | Filenames in one directory decide padding, uniqueness, and the gapless run. |
| `decisions.slug-case` | decisions/records.md | deterministic | delete |  | The filename alone decides kebab-case. |
| `decisions.template` | decisions/records.md | deterministic | rewrite (new sentence in text) | Sentence: A Decision Record's frontmatter holds `type: Decision-Record`, a `title`, a `description`, and a `date`; its body opens with an H1 repeating the `title`. | Frontmatter keys, the H1 echoing title, and a one-to-three sentence opener are all read off the file. |
| `decisions.context-decision-and-reason` | decisions/records.md | stochastic | rewrite (new sentence in text) | Sentence: A Decision Record's body gives the context the decision was made in, the decision itself, and the reason for it. | A reader decides from the opening sentences whether context, decision, and reason are each present; what counts is a judgment call. |
| `decisions.date` | decisions/records.md | deterministic | residue to predicate; intent to explanation | Sentence: A Decision Record's `date` frontmatter key holds a `YYYY-MM-DD` date or `null`<br>Why: The date is the day the decision was made, not the writing day, and null where that day is unrecoverable. | No file says what day the decision was made; only the format survives. Class differs from the deterministic trailer. |
| `decisions.immutable-after-merge` | decisions/records.md | deterministic | delete; intent to guide | Guide: `guides/governed-repo.md` | Byte-identity against the first commit on `main` lives in git history, not in the files at one commit. Class differs from trailer. |
| `decisions.status-vocabulary` | decisions/records.md | deterministic | keep |  | The `status` value is absent or one of four stated strings; a string comparison. |
| `decisions.supersession-target` | decisions/records.md | deterministic | keep |  | The `status` number and the sibling filenames in the same directory decide it. |
| `decisions.optional-sections` | decisions/records.md | deterministic | delete |  | Section headings and their emptiness are read off the body. |
| `decisions.external-convention-evaluation` | decisions/records.md | stochastic | strip trailer and verifier row; heading stays as scope |  | Scopes the level-three rule below it, naming which records pin what they examined; not an obligation every record can fail. |
| `decisions.what-was-examined` | decisions/records.md | stochastic | residue to predicate; intent to explanation | Sentence: A Decision Record whose decision is a verdict on something outside the workspace names the source and pins at least one of the repository SHA and the release or version examined.<br>Residue: A Decision Record whose decision is a verdict on something outside the workspace names the source and carries a repository SHA or a release version and a `YYYY-MM-DD` date it was read<br>Why: *stands.* The pin lets a later reader tell whether the thing judged has changed since; the record's own `date` is the day it was read. | Whether the pinned state is the state the author actually examined, and the day they read it, are in the author's mind. |

### distribution

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `distribution.one-published-id` | distribution/channel.md | deterministic | keep |  | One file in the publishing repo against a stated shape, no judgment; vacuous in consumer checkouts, which hold no manifest. |
| `distribution.a-publisher-dogfoods-its-manifest` | distribution/channel.md | deterministic | keep |  | Compares the hook ids of two files in the same repo; the guard clause scopes it, no judgment call. |
| `distribution.a-valid-manifest` | distribution/channel.md | deterministic | keep as predicate-det; the tool is a pure function of the files |  | Validity is whatever `pre-commit validate-manifest` returns when run; no repo file states the shape. Trailer says deterministic. |
| `distribution.a-pinned-rev` | distribution/channel.md | deterministic | delete |  | Presence of a `rev` in the repo's own config, publisher exempt; freshness of the rev is explicitly not required. |
| `distribution.the-roster` | distribution/channel.md | deterministic | delete; intent to guide | Guide: `guides/governed-repo.md` | Which repos are governed is a decision, and the second clause reads other repos' checkouts. Trailer says deterministic. |

### doc-type

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `doc-type.registered` | doc-type/doc-type.md | deterministic | keep |  | Two tables in this repo name the directory; the reader compares names with no judgment. |
| `doc-type.a-verb-set` | doc-type/doc-type.md | stochastic | keep |  | Which words of `definition.md` prose are the verbs is a judgment call before the two sets can be compared. |
| `doc-type.one-base` | doc-type/doc-type.md | stochastic | retrailer deterministic; add check in detector rewrite |  | The class shape is stated exactly and the pseudocode block shows the nesting; the stochastic trailer reflects only the missing extractor. |
| `doc-type.a-composition-rule` | doc-type/doc-type.md | stochastic | keep |  | Whether `contract-shape.md` states every pointer, its doc-types, its Targets, and its count is a completeness judgment. |
| `doc-type.an-encoding` | doc-type/doc-type.md | stochastic | keep |  | "Each markdown construct an instance uses" must first be enumerated by judgment before the map can be checked. |
| `doc-type.held-to-a-standard` | doc-type/doc-type.md | stochastic | keep |  | Matching a Standard's prose `population` phrase to the doc-type's instances is a judgment call. |
| `doc-type.one-sentence` | doc-type/doc-type.md | stochastic | rewrite (new sentence in text) | Sentence: `definition.md` opens with one sentence that says what one instance is. | Whether the opening sentence says what one instance is and what the doc-type does is taste. |
| `doc-type.one-graph` | doc-type/loop-conventions.md | deterministic | keep |  | Order of H1, paragraph, and fenced block, and the flowchart's statement kinds, are read straight off the file. |
| `doc-type.what-the-paragraph-says` | doc-type/loop-conventions.md | stochastic | keep |  | Whether the paragraph names the driven state and its target state is a reading judgment. |
| `doc-type.three-verb-sections` | doc-type/loop-conventions.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Heading names, their order, and each list line's shape compare to a stated shape. |
| `doc-type.nodes-and-entries-agree` | doc-type/loop-conventions.md | deterministic | keep |  | Node ids and entry ids compare as sets; the sentence defines receiver itself. |
| `doc-type.edges-follow-the-shape` | doc-type/loop-conventions.md | deterministic | keep |  | Each edge's target is classed by which verb section carries its entry, already fixed by graph and lists. |
| `doc-type.entries-point-and-condition` | doc-type/loop-conventions.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Fixed condition phrases, link counts, target types, and in-repo link resolution all read from files. |
| `doc-type.an-act-links-a-runbook` | doc-type/loop-conventions.md | deterministic | keep |  | The link resolves inside the repo, so whether the target is a skill bundle's `SKILL.md` or an agent definition is file-checkable. |
| `doc-type.front-matter` | doc-type/runbook-conventions.md | deterministic | keep |  | The YAML key set per kind is a stated shape; a reader compares the block to it with no judgment. |
| `doc-type.name-matches-its-home` | doc-type/runbook-conventions.md | deterministic | keep |  | `name` against directory or file stem is a string comparison inside the checkout. |
| `doc-type.kebab-case-name` | doc-type/runbook-conventions.md | deterministic | keep |  | Kebab-case is a pattern over one frontmatter value. |
| `doc-type.description` | doc-type/runbook-conventions.md | deterministic | keep |  | Character count, sentence count, and the literal words `Use when` are all read off the string. |
| `doc-type.description-states-what-and-when` | doc-type/runbook-conventions.md | stochastic | keep |  | Whether a sentence states what the runbook does, or names invoking contexts, is a judgment about meaning. |
| `doc-type.model-and-effort` | doc-type/runbook-conventions.md | deterministic | keep |  | Both values are checked against closed enumerations given in the rule. |
| `doc-type.body-opens-with-an-h1` | doc-type/runbook-conventions.md | deterministic | keep |  | The first non-blank line after the front matter either is an H1 or is not. |
| `doc-type.steps-end-on-a-completion-criterion` | doc-type/runbook-conventions.md | stochastic | guide | Guide: `guides/writing-for-agents.md` | A reader must decide what counts as a step and whether its last sentence is a completion condition. |
| `doc-type.carries-its-chain` | doc-type/runbook-conventions.md | stochastic | rewrite (new sentence in text) | Block: exemption clause becomes "except an edge the span vocabulary cannot carry". | Deciding which edges the runbook's contract has, before checking spans, is a reading of the body. |
| `doc-type.skill` | doc-type/runbook-conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the eleven level-three rules beneath it to skills; not an obligation a runbook can fail. Trailer implies a predicate. |
| `doc-type.bundle-layout` | doc-type/runbook-conventions.md | deterministic | keep |  | Each file under `references/` and `scripts/` is matched against links and invocations in `SKILL.md`. |
| `doc-type.model-invocation-flag` | doc-type/runbook-conventions.md | deterministic | keep |  | The value is boolean or it is not. |
| `doc-type.interactive-skills-inherit` | doc-type/runbook-conventions.md | stochastic | keep; repo change (see Repo changes) |  | Whether a skill runs several turns with the user is judged from its body, not read off a field. |
| `doc-type.tool-fields` | doc-type/runbook-conventions.md | deterministic | keep |  | Space-separated tool specs are a stated syntax over one frontmatter value. |
| `doc-type.disallowed-tools-restate-nothing` | doc-type/runbook-conventions.md | deterministic | delete |  | Both the field and the `settings.json` beside the skills root sit in this checkout; the overlap is a set comparison. |
| `doc-type.arguments` | doc-type/runbook-conventions.md | deterministic | keep |  | A non-empty list of bare kebab-case names is a shape over one value. |
| `doc-type.no-argument-placeholder` | doc-type/runbook-conventions.md | deterministic | keep |  | Absence of two literal strings in the body. |
| `doc-type.references-one-level-deep` | doc-type/runbook-conventions.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Links between `.md` files in one directory are read from the files themselves. |
| `doc-type.skillmd-at-most-500-lines` | doc-type/runbook-conventions.md | deterministic | keep |  | A line count against a stated number. |
| `doc-type.agent` | doc-type/runbook-conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the single level-three rule beneath it to agents; not an obligation a runbook can fail. Trailer implies a predicate. |
| `doc-type.tools` | doc-type/runbook-conventions.md | deterministic | keep |  | A non-empty comma-separated string of tool names is a stated syntax over one value. |
| `doc-type.the-population` | doc-type/standard-conventions.md | deterministic | residue to predicate; intent to explanation | Sentence: A file typed `Standard` names the population its rules bind in its frontmatter: a `population` key holding one phrase.<br>Why: standards-lint reports a Standard without a population. What a detector reports is not part of the predicate, so the clause lives here. | The clause "standards-lint reports a Standard without one" states what a script does when run, which no member can fail. |
| `doc-type.the-rule-shape` | doc-type/standard-conventions.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Why: The first paragraph is the predicate every member is held to; the block or table is the target state it compares against. An H2 without a trailer is a condition: it names which members the rules under it bind. | Mostly structural, but "the predicate every member is held to" and "a heading that is a condition" need judgment; trailer says deterministic. |
| `doc-type.decidable-predicates` | doc-type/standard-conventions.md | stochastic | keep |  | Deciding whether a predicate asks for taste or compares two members is itself a judgment. |

### harness

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `harness.no-frontmatter` | harness/claude-content.md | deterministic | keep |  | "opens on its content, with no YAML frontmatter block" reads the file's first bytes; no judgment. |
| `harness.operational-scope` | harness/claude-content.md | stochastic | keep |  | "holds only how to operate" needs a reader to judge what counts as operating knowledge against project description. |
| `harness.one-scope` | harness/claude-content.md | stochastic | residue to predicate; intent to explanation | Sentence: A nested <dir>/CLAUDE.md states no rule already stated in the root file above it.<br>Why: A rule sits at the widest scope where it is true: machine-wide in the global source, repo-wide in the root file, only the delta in a nested file. A repo can check one part of that, the nested file against its root. | "the widest scope where it is true" reaches machine-wide and other repos' sessions, not files here; trailer says stochastic. |
| `harness.global-file` | harness/claude-content.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the three H3 rules below it to the global source; the link to ~/.claude is machine state, not repo. Trailer says deterministic. |
| `harness.two-sections` | harness/claude-content.md | deterministic | keep |  | "H2 headings outside fenced code blocks are exactly ... in that order" compares a stated shape to the file. |
| `harness.required-rules` | harness/claude-content.md | deterministic | keep |  | "carries the headings ... both outside fenced code blocks" is a literal heading match. |
| `harness.one-rule-per-heading` | harness/claude-content.md | stochastic | keep; repo change (see Repo changes) |  | "a dispositional stance ... an operating rule for a named situation" needs a judgment on each heading's content. |
| `harness.members` | harness/files.md | deterministic | residue to predicate; intent to explanation | Sentence: Every file under .claude/ or dotfiles/dot-claude/ in a governed repo matches a member row of the table below.<br>Why: Claude Code fixes which files it reads; the table is the workspace's record of that set, and the predicate holds the repo to the table. | "every file the harness consumes" is set by Claude Code, not by repo files; the table's completeness is a kept intention. Trailer says deterministic. |
| `harness.location` | harness/files.md | deterministic | rewrite (new sentence in text) | Block: the tree block gains the optional `agents/` bundle line the repo already uses. | Named paths <skills root>/<name>/SKILL.md and <agents root>/<name>.md are checked by listing the roots. |

### knowledge-organization

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `knowledge-organization.glossary-only` | knowledge-organization/context-content.md | stochastic | keep |  | Reader decides from the file, but "no implementation detail, no specification, no scratch note" is a judgment about content |
| `knowledge-organization.vocabulary-type` | knowledge-organization/context-content.md | deterministic | keep |  | A frontmatter key equals a stated literal; no judgment |
| `knowledge-organization.the-language-section` | knowledge-organization/context-content.md | deterministic | keep |  | Presence of a named heading; no judgment |
| `knowledge-organization.entry-shape` | knowledge-organization/context-content.md | deterministic | rewrite (new sentence in text) | Block: the example block is rewritten to match `CONTEXT.md`: no colon after the bold term, one H3 group shown. | The section states the shape as a template, so an entry is compared to it mechanically |
| `knowledge-organization.tight-definitions` | knowledge-organization/context-content.md | stochastic | rewrite (new sentence in text) | Sentence: An entry's definition in a repo's `CONTEXT.md` is at most two sentences: one that says what the term is, and at most one more that sharpens it; where a concept document defines the term the definition links that document. | "one sentence that says what the term is" is taste; the linking clause needs judging which document defines the term |
| `knowledge-organization.project-terms-only` | knowledge-organization/context-content.md | stochastic | keep |  | "specific to the project's context" and "used beyond the set that defines it" are judgment calls over the repo's files |
| `knowledge-organization.reference-resolves` | knowledge-organization/cross-references.md | deterministic | residue to predicate; intent to explanation | Sentence: A reference names a file or a directory that exists in the referencing file's own repository<br>Why: A `~/workspace/<repo>/` target naming another repository resolves against that repo's main checkout. A repo cannot check the other side from its own files, so the predicate binds same-repo targets. | The clause resolving a `~/workspace/<repo>/` target for another repository reads that repo's checkout, outside this repo's files |
| `knowledge-organization.fragment-anchor-matches-the-slug` | knowledge-organization/cross-references.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | The GitHub slug is computed from the target's heading text; no judgment |
| `knowledge-organization.stable-named-anchor` | knowledge-organization/cross-references.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Sentence: A reference's `#anchor` carries no number that is the heading's position in the file; where the target numbers every heading by position and carries no other anchor, the reference carries no anchor.<br>Why: *stands.* An anchor names the concept the heading carries and so survives a renumbering; a positional number breaks on the next insert. | Trailer says deterministic, but "names the concept the heading carries in the link text" is a judgment call |
| `knowledge-organization.citation-another-repo` | knowledge-organization/cross-references.md | deterministic | rewrite (new sentence in text) | Block: the file's `population` phrase and preamble gain `except inside a code block, fenced or indented`; the rule sentence stands. | The written form of the link alone decides it; no judgment |
| `knowledge-organization.skill-invocation` | knowledge-organization/cross-references.md | deterministic | rewrite (new sentence in text) | Sentence: A reference to a skill names it by its slash invocation, `/<skill-name>`. | Bare `/<skill-name>` with no link and no code markup is a form check |
| `knowledge-organization.fixed-repo-root` | knowledge-organization/cross-references.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Trailer says deterministic, but the heading exists to scope the level-three rule Link, same bundle; no member can fail it |
| `knowledge-organization.link-same-bundle` | knowledge-organization/cross-references.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Root-absolute inline link is a form check on the reference itself |
| `knowledge-organization.no-fixed-repo-root` | knowledge-organization/cross-references.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Trailer says deterministic, but the heading scopes its three level-three rules; it names which files they bind |
| `knowledge-organization.workspace-path-for-a-stable-location` | knowledge-organization/cross-references.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Sentence: A reference to a file in the referencing file's own repository is an inline link whose target is the full `~/workspace/<repo>/<path>` path, unless the target is inside the referencing file's own skill bundle.<br>Why: The condition above says what stable means: a location fixed relative to the repo root. | Trailer says deterministic, but "at a stable location" turns on whether the path varies between repos, a judgment call |
| `knowledge-organization.relative-path-inside-the-bundle` | knowledge-organization/cross-references.md | deterministic | keep |  | Sibling, `references/`, or parent inside the bundle is decided by path comparison |
| `knowledge-organization.inline-code-for-a-varying-location` | knowledge-organization/cross-references.md | stochastic | keep |  | The list of varying paths is open, so deciding what counts as varying is a judgment call |
| `knowledge-organization.frontmatter-block` | knowledge-organization/document-types.md | deterministic | keep |  | A delimited block whose YAML parses as a mapping is read off the file with no judgment |
| `knowledge-organization.types` | knowledge-organization/document-types.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | The `type` value is matched against the table in this very section and the repo's own root index frontmatter |
| `knowledge-organization.title` | knowledge-organization/document-types.md | deterministic | keep |  | Key present and value non-empty; read straight off the frontmatter |
| `knowledge-organization.description` | knowledge-organization/document-types.md | deterministic | keep |  | Non-empty and no trailing period are both mechanical; the content claim sits in the separate description-voice rule |
| `knowledge-organization.description-voice` | knowledge-organization/document-types.md | stochastic | rewrite (new sentence in text) | Sentence: A concept document's `description` is a sentence fragment in the present tense that names what the document is, what it governs, or, for a `Decision-Record`, the decision it records. | Whether a fragment is present tense and names what the document governs is a reader's judgment |
| `knowledge-organization.resource` | knowledge-organization/document-types.md | deterministic | keep |  | Leading `/` or a URI scheme is a stated shape; the rule does not require the target to exist |
| `knowledge-organization.resource-names-the-asset` | knowledge-organization/document-types.md | stochastic | keep |  | Telling the described asset from a companion that only supports it is a judgment call |
| `knowledge-organization.no-tags-or-timestamp` | knowledge-organization/document-types.md | deterministic | keep |  | Absence of two named keys is read off the frontmatter |
| `knowledge-organization.recipe-description` | knowledge-organization/document-types.md | deterministic | keep |  | A typed conditional predicate, not a scoping heading; no level-three rules sit under it |
| `knowledge-organization.typed-standard` | knowledge-organization/document-types.md | deterministic | keep |  | Type value and file path are both in the checkout |
| `knowledge-organization.typed-loop` | knowledge-organization/document-types.md | deterministic | keep |  | Type value and file path are both in the checkout |
| `knowledge-organization.typed-guide` | knowledge-organization/document-types.md | deterministic | keep |  | Type value and file path are both in the checkout |
| `knowledge-organization.an-index-in-every-directory` | knowledge-organization/documentation-sets/documentation-sets.md | deterministic | keep |  | Directory listing and frontmatter type decide it; no judgment call. |
| `knowledge-organization.body-inside-its-concern` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | keep |  | Whether a section is one a reader expected from the description is taste. |
| `knowledge-organization.rows-inside-the-set` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | keep |  | Whether a row lies inside the concern the introduction names is a judgment call. |
| `knowledge-organization.one-home` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | residue to predicate; intent to explanation | Sentence: A fact, rule, or decision has one home, the member whose concern is the thing the fact binds and the most general such member where the fact still holds; every other document in this repo links there and states the fact without its reason.<br>Why: *stands.* The same holds across repos: another repo links here rather than restating. A repo cannot check the other side. | The "another repo" clause reads outside the checkout; trailer says stochastic, but the cross-repo obligation makes it intention, residue repo-scoped. |
| `knowledge-organization.distinct-concerns` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | keep |  | Whether two rows answer the same question is a judgment on one index. |
| `knowledge-organization.distinct-from-the-parent` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | keep |  | Compares two introductions; naming a concern the parent does not is taste. |
| `knowledge-organization.terms-defined-once` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | delete |  | What counts as a definition, and which member the term is the concern of, is judgment. |
| `knowledge-organization.terms-that-cross-sets` | knowledge-organization/documentation-sets/documentation-sets.md | stochastic | keep; repo change (see Repo changes) |  | CONTEXT.md sits in the repo; what the set coins and who uses it is a judgment call. |
| `knowledge-organization.speculative-voice` | knowledge-organization/documentation-sets/working-documentation-sets.md | stochastic | rewrite (new sentence in text) | Sentence: Every member of a working documentation set writes a guess as a guess, and the set's `ROOT.md` declares the set speculative. | Whether a guess reads as a guess is taste; the closing sentence only scopes the exemption. |
| `knowledge-organization.the-link-tree` | knowledge-organization/documentation-sets/working-documentation-sets.md | deterministic | keep; repo change (see Repo changes) |  | Link paths from ROOT.md are traceable in the files with no judgment. |
| `knowledge-organization.where-a-set-lives` | knowledge-organization/documentation-sets/working-documentation-sets.md | deterministic | rewrite (new sentence in text) | Sentence: A working documentation set is one directory under `working-docs/` at the repo root, `working-docs/<work>/`, holding the set's `index.md`, its `ROOT.md`, and its members under lowercase kebab-case names, flat or in subdirectories, except a member whose kind fixes its name (`README.md`, `PROMPT.md`, `SKILL.md`, `CLAUDE.md`, a Python module). | Path, index.md, ROOT.md, and kebab-case member names are all read off the tree. |
| `knowledge-organization.a-set-stands-on-main` | knowledge-organization/documentation-sets/working-documentation-sets.md | deterministic | delete; intent to guide | Guide: `guides/governed-repo.md` | Presence on main is branch state, not files at one commit; trailer says deterministic but no file decides it. |
| `knowledge-organization.working-docs-holds-only-sets` | knowledge-organization/documentation-sets/working-documentation-sets.md | deterministic | keep |  | A directory listing decides it; it binds working-docs/ itself, not a member set. |
| `knowledge-organization.worklist` | knowledge-organization/documentation-sets/working-documentation-sets.md | deterministic | keep |  | Bold item names, Planned and Completed sections, and one ROOT.md per strand are structural. |
| `knowledge-organization.buckets` | knowledge-organization/documentation-sets/working-documentation-sets.md | stochastic | rewrite (new sentence in text) | Sentence: Every fact in a member of a working documentation set sits under a named section, its bucket, and a bucket holds facts of its own type only; the section under the member's H1, which says what the member is and what it is for, is exempt. | Whether a bucket holds facts of one type, and when none of them fits, is judgment. |
| `knowledge-organization.terms` | knowledge-organization/documentation-sets/working-documentation-sets.md | stochastic | keep |  | What the work coins and which members use it is judgment; the placement then follows. |
| `knowledge-organization.acronyms` | knowledge-organization/documentation-sets/working-documentation-sets.md | stochastic | keep; repo change (see Repo changes) |  | Appendix presence is mechanical, but what counts as an acronym is a judgment call. |
| `knowledge-organization.typeless` | knowledge-organization/indexes.md | deterministic | keep |  | Absence of a frontmatter key; no judgment |
| `knowledge-organization.the-introduction` | knowledge-organization/indexes.md | deterministic | keep |  | Presence of prose between the H1 and the first listed entry; no judgment |
| `knowledge-organization.the-opening-sentence` | knowledge-organization/indexes.md | stochastic | keep; repo change (see Repo changes) |  | Whether the sentence names what the directory holds "in that directory's own vocabulary" is taste |
| `knowledge-organization.the-listing` | knowledge-organization/indexes.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Directory contents and typed frontmatter give the expected set, and the description is compared verbatim |
| `knowledge-organization.ordering` | knowledge-organization/indexes.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Case-insensitive alphabetical order, the README entry's place, and the `Ordering:` marker are all mechanical |
| `knowledge-organization.the-root-index` | knowledge-organization/indexes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Trailer says deterministic, but the heading is a bare noun phrase scoping the level-three rule OKF version declared |
| `knowledge-organization.okf-version-declared` | knowledge-organization/indexes.md | deterministic | keep |  | Presence of a frontmatter key on one named file; no judgment |
| `knowledge-organization.h1` | knowledge-organization/readme-content.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Presence of an H1 heading; no judgment |
| `knowledge-organization.the-purpose-sentence` | knowledge-organization/readme-content.md | stochastic | keep |  | Whether the sentence "says what the repo or directory holds or is for" is a judgment call |
| `knowledge-organization.no-agent-instructions-or-decisions` | knowledge-organization/readme-content.md | stochastic | keep; repo change (see Repo changes) |  | What counts as an instruction addressed to an agent or an architecture decision is a judgment call |
| `knowledge-organization.no-roster-of-harness-injected-files` | knowledge-organization/readme-content.md | stochastic | keep |  | Decidable from the README, but what counts as a file the harness injects is a judgment call |
| `knowledge-organization.global-table` | knowledge-organization/type-registry.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which member the three level-three rules bind, the global table; not an obligation a member can fail |
| `knowledge-organization.row-shape` | knowledge-organization/type-registry.md | deterministic | keep |  | Backticked, Title Case, hyphen-joined is a stated shape, with `README` given as a conforming example |
| `knowledge-organization.row-description` | knowledge-organization/type-registry.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Sentence: Every row of the `## Types` table below its header holds, in its second cell, non-empty text on one line.<br>Why: The second cell is a description a reader picks the type by. | Non-empty and one-line are mechanical but judging a cell as a description of the type is not; trailer says deterministic |
| `knowledge-organization.alphabetical-order` | knowledge-organization/type-registry.md | deterministic | keep |  | Case-insensitive sort of the first cells is decided by comparison alone |
| `knowledge-organization.local-declaration` | knowledge-organization/type-registry.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which member the three level-three rules bind, a consumer's `okf_types` mapping; the YAML block is an example |
| `knowledge-organization.mapping-entry-shape` | knowledge-organization/type-registry.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Sentence: Each entry's key is a type name in Title Case, hyphen-joined for a multi-word name, and its value is non-empty text on one line.<br>Why: The value is a description a reader picks the type by. | Key shape is mechanical but judging the value as a description of the type is not; trailer says deterministic |
| `knowledge-organization.alphabetical-keys` | knowledge-organization/type-registry.md | deterministic | keep |  | Case-insensitive sort of the mapping keys is decided by comparison alone |
| `knowledge-organization.add-never-shadow` | knowledge-organization/type-registry.md | deterministic | keep |  | Both sides compared are in hand, the Standard's own table and the repo's root index frontmatter |

### modules

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `modules.deep-not-shallow` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "small against the behaviour behind it" is a judgment on one module; design guidance rather than a check, so a guide home would suit. |
| `modules.internal-seams-stay-inside` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Decidable from the source, but "exists only for the module's own tests" is a judgment about why a seam is there. |
| `modules.two-adapters-or-no-seam` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | A reader counts adapters in the repo, but what satisfies the interface at a seam is a judgment call. |
| `modules.dependencies-are-accepted-not-constructed` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Near-mechanical over one module body, but the file never fixes what counts as a dependency rather than a plain value. |
| `modules.a-port-at-a-process-boundary` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | A predicate over one module, not a condition: no child rules sit under it. Judging which reaches leave the process decides it. |
| `modules.the-interface-is-the-test-surface` | modules/design.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Files hold the interface and the implementation, but what counts as a distinct behaviour is a judgment. |
| `modules.results-are-returned-not-written` | modules/design.md | stochastic | delete |  | Mutation is visible in source, but separating delivering a result from doing the work is a judgment call. |

### prose

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `prose.one-rule-one-place` | prose/conventions.md | stochastic | rewrite (new sentence in text) | Sentence: Each rule the document states lives in the lead sentence of its section, except a statement of the document's own scope, which sits in the section under the H1. | A reader decides it from the document, but judges what counts as a rule and as the lead sentence. |
| `prose.current-state-and-next-steps-only` | prose/conventions.md | stochastic | keep |  | Decidable from the document; judgment on what counts as past state and when history still binds. |
| `prose.point-at-canonical-artifacts` | prose/conventions.md | stochastic | rewrite (new sentence in text) | Sentence: Where a file is itself the standard, the document links that file rather than reproducing its contents; naming one entry as a worked example is not reproduction. | Decidable from the document and the referenced file; judgment on what counts as restating contents. |
| `prose.open-with-purpose` | prose/conventions.md | stochastic | rewrite (new sentence in text) | Sentence: The opening states what the document is for and what a reader should be able to do after reading; an `index.md` and a `README.md` answer instead to the opening-sentence and purpose-sentence rules of the knowledge-organization Standard. | The opening is in the file; judgment on whether purpose and payoff are stated. |
| `prose.declare-before-use` | prose/conventions.md | stochastic | keep |  | Decidable from the document; judgment on what counts as a concept and as leaning on it. |
| `prose.block-form-fits-its-content` | prose/conventions.md | stochastic | keep | Block: the `Table vs repeated structure` bullet becomes: the same shape with the same fields two or more times is a table; anything fewer or uneven is prose with bold leads. | Blocks are in the file; judgment on parallel items, derailing asides, and even structure. |
| `prose.declarative-present-tense` | prose/conventions.md | stochastic | rewrite (new sentence in text) | Sentence: Every sentence is in the present tense, except a sentence reporting a measurement or an incident that happened, and except in a member of a working documentation set, which may write a guess as a guess. | Every sentence is in the file; judgment on tense in mixed clauses and on the working-set exemption. |
| `prose.positive-statement` | prose/conventions.md | stochastic | keep |  | Decidable from the document; judgment on when the prohibition is itself the rule. |
| `prose.no-slop-tics` | prose/conventions.md | stochastic | keep; repo change (see Repo changes) |  | The tic catalog is a repo file, so it is decidable, but each tic needs a judgment call. |
| `prose.harness-loaded-agent-instructions` | prose/conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which documents the child rule binds, not an obligation a document can fail; trailer says deterministic. |
| `prose.no-first-person` | prose/conventions.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Three words and their stated exemptions compared against the file text; no judgment call. |
| `prose.declarative-documents` | prose/conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the third-person child rule by path and filename; not an obligation; trailer says deterministic. |
| `prose.third-person` | prose/conventions.md | stochastic | keep; repo change (see Repo changes) |  | Decidable from the document; mood and third person need a judgment call beyond the word `you`. |
| `prose.name-concepts-once-use-consistently` | prose/conventions.md | stochastic | keep |  | Decidable from the document; judgment on which names denote one concept. |
| `prose.terminology-the-person-is-the-user` | prose/conventions.md | stochastic | rewrite (new sentence in text) | Sentence: One actor, the dispatcher, reviewer, and approver, is the `user` throughout the document, its frontmatter, code spans, and fenced blocks included, never a synonym, in any case, plural, or compound. A numbered Decision Record is exempt. | Decidable from the document; judgment on which words are synonyms for the actor. |
| `prose.the-banned-word` | prose/conventions.md | deterministic | rewrite (new sentence in text) | Sentence: The file does not contain a word the workspace vocabulary bans, `WORKSPACE_VOCABULARY` in `src/dev_playbook/prose_lint.py`, bare or plural, in any case, alone or in a compound, its frontmatter, code spans, and fenced blocks included. | Word match over tracked files against a listed exemption file; no judgment. Binds the repo, not one document. |
| `prose.the-repo-vocabulary` | prose/conventions.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Word match over tracked files under directories the vocabulary file names; no judgment. Binds the repo, not one document. |
| `prose.spelling` | prose/conventions.md | deterministic | keep |  | One spelling compared against the file text with stated exemptions; no judgment. |
| `prose.heading-casing` | prose/conventions.md | stochastic | keep; repo change (see Repo changes) |  | Headings are in the file; judgment on proper nouns, code identifiers, and sentence case. |
| `prose.grammatical-parallelism` | prose/conventions.md | stochastic | keep; repo change (see Repo changes) |  | Decidable from the document; judgment on what counts as the same grammatical shape. |

### python

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `python.empty-init` | python/style.md | deterministic | keep |  | Whether the file holds any non-whitespace character is read straight off the file, no judgment. |
| `python.docstrings` | python/style.md | deterministic | keep |  | Presence of a docstring on each module, class, function, and method is visible in the file; exemptions named by filename and prefix. |
| `python.docstring-content` | python/style.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "Says in plain English what it does" is a taste call a reader makes, not a stated shape. |
| `python.fail-loudly` | python/style.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Deciding whether a value "always exists" and whether a fallback covers real runtime state is a judgment call. |
| `python.module-layout` | python/style.md | deterministic | delete |  | The four-part statement order, including which constants are derived, is read off the file with no judgment. |
| `python.no-future-annotations` | python/style.md | deterministic | keep |  | One import line's presence, and the parent directory names that exempt it, are both in the checkout. |
| `python.helper-justification` | python/style.md | stochastic | delete |  | "Substantial in body" and "distinct concern at another abstraction level" are judgment calls; only multi-use is countable. |
| `python.helper-placement` | python/style.md | deterministic | delete |  | Position relative to the calling function, or inside a `# ---` banner section, is read off the file. |
| `python.formatted-by-ruff-format` | python/style.md | deterministic | keep |  | Answer lives in what ruff format outputs when run, not in any repo file; class differs from the deterministic trailer. |
| `python.annotated-signatures` | python/style.md | deterministic | delete |  | Each parameter and return annotation is present or absent in the signature; the self and cls exemption is named. |

### shell

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `shell.bash-declared` | shell/conventions.md | deterministic | keep |  | A shebang naming bash or a shellcheck directive is read off the file's first lines with no judgment. |
| `shell.shellcheck-clean` | shell/conventions.md | deterministic | keep |  | The verdict lives in what shellcheck prints when run, not in any repo file; trailer says deterministic. |
| `shell.disable-carries-a-reason` | shell/conventions.md | stochastic | keep |  | The same-line comment is in the file, but whether it gives a reason the suppression is safe is judgment. |
| `shell.formatting` | shell/conventions.md | deterministic | keep |  | The bar is what shfmt writes when run; no repo file holds those bytes. Trailer says deterministic. |
| `shell.executable-scripts` | shell/conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the two level-three rules under it by naming which shell files are executable scripts, though phrased as an obligation. |
| `shell.glue-only` | shell/conventions.md | deterministic | keep |  | The colon lists three file-readable tests: no function, no array, no positional parameter. |
| `shell.strict-mode` | shell/conventions.md | deterministic | keep |  | Two exact lines compared against the file's opening, with the explanation allowing a comment between them. |
| `shell.sourced-fragments` | shell/conventions.md | deterministic | strip trailer and verifier row; heading stays as scope |  | A path test that scopes the three level-three fragment rules, not an obligation a shell file can fail. |
| `shell.no-shebang-no-strict-mode` | shell/conventions.md | deterministic | keep |  | Absence of two literal lines, decided by reading the fragment. |
| `shell.dialect-directive` | shell/conventions.md | deterministic | keep |  | A literal opening directive compared against the fragment's first line. |
| `shell.bounded-to-shell-integration` | shell/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | What counts as mutating the parent shell, against parsing or an algorithm, is a judgment call on one fragment. |

### standard

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `standard.read-only` | standard/detectors.md | deterministic | rewrite (gate mode changes nothing tracked); stays stochastic | Sentence: A first-party detector run without an explicit write flag leaves everything git tracks as it found it; `verifier-table --write` and `boundary-table --write` are enforcement, and a dependency the verifier table names may write at its gate, `ruff-format` and `shfmt -w`. | Behaviour at run time over any repo, and a dependency's source is not in this checkout. Trailer says deterministic; no file decides it. |
| `standard.an-absent-surface-is-clean` | standard/detectors.md | deterministic | guide (detector contract) | Guide: `guides/writing-a-detector.md` | Exit status and silence are run-time facts, and the population includes dependencies whose code is absent. Trailer says deterministic. |
| `standard.the-verifier-table` | standard/detectors.md | deterministic | keep |  | Shape stated in full; generator and inputs are repo files, so a reader can compare the committed table. |
| `standard.an-emitted-id-is-a-rule-heading` | standard/detectors.md | deterministic | keep |  | Claimed ids are constants in detector source and the generator's dependency map; rule headings sit under standards/. A cross-file compare. |
| `standard.an-address-exists` | standard/detectors.md | deterministic | keep |  | Every named address resolves against .pre-commit-config.yaml or pyproject.toml, both repo files. |
| `standard.a-consumer-adds-only-its-own-rules` | standard/detectors.md | deterministic | keep; undecidable only from a consumer checkout |  | A consumer's checkout does not hold dev-playbook's shipped table; the union clause describes the reader, not a member. Trailer says deterministic. |
| `standard.the-boundary-table` | standard/detectors.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Shape stated in full and derived from committed wiring: the pre-commit config, make check, and the workflows. |
| `standard.every-address-runs-somewhere` | standard/detectors.md | deterministic | keep |  | Boundary table plus the ungated registry in src/dev_playbook/boundary_table.py; both are repo files. |
| `standard.a-skip-is-machine-state` | standard/detectors.md | stochastic | keep |  | What counts as machine-local input is a judgment call, and a machine's own SKIP is uncommitted; only committed skips are visible. |
| `standard.a-first-party-detector` | standard/detectors.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Scopes the seven level-three rules beneath it to detectors hosted at scripts/<name>; it names members, not an obligation one can fail. |
| `standard.thin-shims` | standard/detectors.md | deterministic | keep; restate as a shape (import-path line plus one call) and retrailer deterministic | Sentence: The script holds no rule logic: apart from its shebang and inline metadata block, its statements are at most one that puts the host repo's package on `sys.path`, one import from that package, and one call of the imported entry point. | Holding no rule logic of its own is a judgment over the body; the import-and-call shape is checkable. Trailer says deterministic. |
| `standard.git-runs-against-the-given-root` | standard/detectors.md | deterministic | keep residue (GIT_DIR cleared in source) as deterministic; behaviour clause to explanation | Sentence: A first-party detector that runs git clears the variables `git rev-parse --local-env-vars` lists from the child environment.<br>Why: *stands.* Clearing git's local environment variables is what makes a detector address the repo it was given when a hook runs it under an ambient `GIT_DIR`. | Addressing the right repo under an ambient GIT_DIR is run-time behaviour; only the mechanism that yields it is greppable in source. |
| `standard.the-hosting-pattern` | standard/detectors.md | deterministic | rewrite (new sentence in text) | Sentence: A first-party detector is reachable from its repo's published hook, named in the `playbook-lint` roster, wired as a `scripts/` hook its `.pre-commit-config.yaml` and `.pre-commit-hooks.yaml` both carry, or registered as an ungated audit, and has a row in a `scripts/README.md` script table where the repo has that file. | Compares .pre-commit-hooks.yaml and the scripts/README.md validation table against the scripts present; all repo files. |
| `standard.offered-by-the-canonical-template` | standard/detectors.md | deterministic | rewrite (new sentence in text) | Sentence: A first-party detector the repo carrying `standards/build/canonical/` publishes in `.pre-commit-hooks.yaml` is a hook of that canonical `.pre-commit-config.yaml`'s pinned dev-playbook block, which offers exactly the ids that manifest publishes. | Compares scripts/ against the pinned block of standards/build/canonical/.pre-commit-config.yaml; both are in the repo. |
| `standard.list-rules` | standard/detectors.md | deterministic | guide (detector contract) | Guide: `guides/writing-a-detector.md` | What a script prints under a flag, and its exit, are run-time output; no file holds the printed list. Trailer says deterministic. |
| `standard.finding-format` | standard/detectors.md | deterministic | guide (detector contract) | Guide: `guides/writing-a-detector.md` | Describes a printed line, and a finding is not a member of the population; no file holds it. Trailer says deterministic. |
| `standard.exit-codes` | standard/detectors.md | deterministic | guide (detector contract) | Guide: `guides/writing-a-detector.md` | Exit status over three run outcomes a reader cannot reach from files. Trailer says deterministic. |
| `standard.directory-layout` | standard/tree.md | deterministic | rewrite (new sentence in text) | Sentence: Every immediate subdirectory of `standards/` is a Standard directory: it holds at least one file typed `Standard`, and every other `.md` file under it, `index.md` aside, is typed `Standard`; the only flat `.md` files under `standards/` are `README.md` and `index.md`. | Directory contents and frontmatter types compare directly; the closing standards-lint clause names the checker, which the boundary table owns. |
| `standard.the-statement` | standard/tree.md | deterministic | keep |  | The opening sentence's template and the catalog's repeat compare literally; whether it truly names the governed question needs some judgment. |
| `standard.the-catalog` | standard/tree.md | deterministic | keep |  | Order, membership, and verbatim wording all compare against standards/index.md and the directory indexes. |
| `standard.no-shadowing` | standard/tree.md | deterministic | keep; undecidable only from a consumer checkout |  | A consumer's checkout does not hold dev-playbook's published directory names; the closing clause names the gate, which the boundary table owns. |

### testing

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `testing.pytest` | testing/conventions.md | deterministic | delete |  | The suite's own files declare the runner: pytest imports, fixtures, conftest.py; no judgment call. Binds tooling, not code style. |
| `testing.test-file-naming` | testing/conventions.md | deterministic | keep |  | A file name matches a glob. Near-tautological, since the population is already defined as the test_*.py files. |
| `testing.mirror-source-structure` | testing/conventions.md | deterministic | keep |  | Compares a test path against a src path by a stated construction; the accepted scope set is fixed, so no judgment call. |
| `testing.conftest-hierarchy` | testing/conventions.md | deterministic | keep |  | Which tests use a fixture, and which directory is narrowest, both resolve by name from the files. |
| `testing.arrange-act-assert` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | A reader decides which statement is the one action under test; that call is taste. |
| `testing.one-concept-per-test` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "One behavior or scenario" and "a facet of that one behavior" are judgment calls over a test body. |
| `testing.no-logic-in-tests` | testing/conventions.md | deterministic | delete |  | Named statement kinds in a named scope; an AST walk decides it with no judgment. |
| `testing.expected-values-come-from-outside-the-code` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "The way the code under test computes it" is a judgment about two pieces of code. |
| `testing.access-only-public-names` | testing/conventions.md | deterministic | delete |  | Leading-underscore identifiers and dotted-path segments decide it by name alone. |
| `testing.assert-on-observable-outputs` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | What counts as an observable output rather than internal state is a judgment call. |
| `testing.assert-on-outcomes-not-call-sequences` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "The minimum that verifies the contract" and the unless-clause both need a reader's judgment. |
| `testing.name-by-capability-not-mechanism` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "Survives an implementation swap" is judged against a name, not compared to a stated shape. |
| `testing.replace-dont-layer` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Phrased as an author's act, but one commit decides it: is the module covered, do the lower unit tests still exist. |
| `testing.no-test-of-a-non-deterministic-decision` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | What counts as a non-deterministic component beyond the three examples is a judgment call. |
| `testing.the-lightest-double` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "Lightest thing that verifies the behavior" and "cheap and deterministic" are taste. |
| `testing.double-at-the-port` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Whether a seam is the port the code defines, rather than the network client, is a judgment call. |
| `testing.fakes-for-stateful-dependencies` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Whether the tests exercise a dependency's state or logic is judged, not compared to a stated shape. |
| `testing.one-fake-per-interface` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Which doubles stand for the same interface is a judgment call over the suite. |
| `testing.fakes-live-in-the-test-tree` | testing/conventions.md | stochastic | keep |  | Path check, but identifying which module is a fake, and "beside the tests that use it", are judged. |
| `testing.fakes-implement-only-what-callers-use` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | Method sets compare mechanically once a reader has judged which classes are fakes. |
| `testing.mocks-at-boundaries-only` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | The three boundaries scope the sentence but bind no child rules; whether a dependency is one is judged. |
| `testing.the-mocking-library` | testing/conventions.md | deterministic | delete |  | An import of unittest.mock decides it; which double a test uses is code style. |
| `testing.fixtures-for-setup-and-teardown` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | What counts as ad-hoc setup code, rather than the act under test, is a judgment call. |
| `testing.narrowest-fixture-scope` | testing/conventions.md | stochastic | guide | Guide: `guides/design-and-testing.md` | "The narrowest scope that works" needs a reader to judge what would still work. |

### tracking

| id | file | trailer | ruling | text | note |
|---|---|---|---|---|---|
| `tracking.one-home` | tracking/candidates.md | stochastic | delete; intent to guide | Guide: `guides/repo-settings.md` | Deciding it reads the GitHub tracker; the explanation says the author makes the call and no detector checks it. Trailer says stochastic. |
| `tracking.entry-shape` | tracking/candidates.md | deterministic | keep mechanical part deterministic; judgment clause to explanation | Sentence: An entry is one list item: a bolded name, an em dash, then at most two sentences, with no fields, no acceptance criteria, and no checkboxes.<br>Why: *stands.* The name is short and the sentences state intent; a candidate is a seed, not a specification. | The list-item shape is mechanical, but "short name", "sentences of intent" and "no acceptance criteria" are what-counts-as judgments; trailer says deterministic. |
| `tracking.structure` | tracking/candidates.md | stochastic | keep |  | Nesting under a heading is mechanical; "achieves its parent's outcome" and "carries no other meaning" are judgment calls. Matches the trailer. |
| `tracking.written-for-the-user` | tracking/issue-shapes.md | stochastic | keep |  | "readable unaided by a user who sees only the issue" is a taste call a reader can make on one body. |
| `tracking.behavioural-not-procedural` | tracking/issue-shapes.md | stochastic | keep |  | "as interfaces and behavioural contracts, never the steps that get there" is a judgment on one body. |
| `tracking.one-goal` | tracking/issue-shapes.md | stochastic | keep |  | "could slip indefinitely with the outcome still standing" is a judgment; the `phase:intake` clause reaches other issues in the same tracker. |
| `tracking.user-intent` | tracking/issue-shapes.md | stochastic | residue to predicate; intent to explanation | Sentence: An issue's `User intent` section is written in the user's voice, not an agent's paraphrase.<br>Why: *stands.* The section holds the user's own words, never an agent's paraphrase; only the user can vouch for that, so the predicate asks for the user's voice. | Whether the text is the user's own words lives in the session, not in any file; only voice survives as a decidable residue. |
| `tracking.closed-fences` | tracking/issue-shapes.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Counting fence openers and closers in the body needs no judgment. |
| `tracking.build-leaf` | tracking/issue-shapes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which issues the four child rules bind; no issue can fail it. Class differs from the deterministic trailer. |
| `tracking.build-labels` | tracking/issue-shapes.md | deterministic | keep |  | Label counts compared against `src/dev_playbook/label_scheme.json`, a file in this repo. |
| `tracking.build-headings` | tracking/issue-shapes.md | deterministic | keep |  | The fenced block states the exact heading set; fenced headings are excluded mechanically. |
| `tracking.prohibited-surfaces` | tracking/issue-shapes.md | stochastic | delete |  | "whose touching is a real hazard" is a judgment call about each named path. |
| `tracking.artifacts` | tracking/issue-shapes.md | deterministic | retrailer; trailer to stochastic |  | Fence presence and backtick count are read straight off the body. |
| `tracking.spike` | tracking/issue-shapes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which issues the two child rules bind; no issue can fail it. Class differs from the deterministic trailer. |
| `tracking.spike-labels` | tracking/issue-shapes.md | deterministic | keep |  | Label counts and the `tests:no` value compare against the label scheme file. |
| `tracking.spike-headings` | tracking/issue-shapes.md | deterministic | keep |  | Three named bold headings, with the fenced-heading exclusion stated. |
| `tracking.session-leaf` | tracking/issue-shapes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which issues the three child rules bind; no issue can fail it. Class differs from the deterministic trailer. |
| `tracking.session-labels` | tracking/issue-shapes.md | deterministic | keep |  | Presence and absence of label families, checked against the label scheme file. |
| `tracking.session-headings` | tracking/issue-shapes.md | deterministic | keep |  | Six named bold headings, plus a permitted literal `Out of scope` text. |
| `tracking.a-stable-body` | tracking/issue-shapes.md | stochastic | keep |  | What counts as a worklist, an open question, or a running decision is a judgment on the body. |
| `tracking.epic` | tracking/issue-shapes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Names which issues the four child rules bind; no issue can fail it. Class differs from the deterministic trailer. |
| `tracking.category-only` | tracking/issue-shapes.md | deterministic | keep |  | Exactly one `category:*` value plus three absences, checked against the label scheme file. |
| `tracking.epic-headings` | tracking/issue-shapes.md | deterministic | keep |  | Two named bold headings read straight off the body. |
| `tracking.no-child-list` | tracking/issue-shapes.md | stochastic | keep |  | What counts as "listing its sub-issues" against prose that merely cites issue numbers is a judgment. |
| `tracking.standing-rulings` | tracking/issue-shapes.md | deterministic | delete |  | Whether the rulings under the heading form a numbered list is read off the markdown. |
| `tracking.wayfinder-map-or-ticket` | tracking/issue-shapes.md | deterministic | strip trailer and verifier row; heading stays as scope |  | Defines map and decision ticket to scope the three child rules; no issue can fail it. Class differs from the deterministic trailer. |
| `tracking.wayfinder-labels` | tracking/issue-shapes.md | deterministic | keep |  | Label values and absences compare against the label scheme file. |
| `tracking.wayfinder-body` | tracking/issue-shapes.md | deterministic | keep; detector fix (decision sheet, Weak checks) |  | Named sections at any heading level, read off the body. |
| `tracking.ticket-parentage` | tracking/issue-shapes.md | deterministic | keep |  | The parent relationship and the parent's `wayfinder:map` label are both read from the tracker. |
| `tracking.valid-labels` | tracking/label-scheme.md | deterministic | delete; intent to guide | Guide: `guides/repo-settings.md` | The labels sit on GitHub, minted from the scheme data by bootstrap-labels and audited over gh api; no repo file decides it. Trailer says deterministic. |
| `tracking.github-origin` | tracking/repo-settings.md | deterministic | delete; intent to guide | Guide: `guides/repo-settings.md` | The origin remote is git-local config, not a file at a commit; the author chooses where it points. Trailer says deterministic. |
| `tracking.squash-only-merges` | tracking/repo-settings.md | deterministic | delete; intent to guide | Guide: `guides/repo-settings.md` | The merge settings live in GitHub's Settings UI, set by hand and only audited; no file in the checkout holds them. Trailer says deterministic. |
| `tracking.default-branch-protection` | tracking/repo-settings.md | deterministic | delete; intent to guide | Guide: `guides/repo-settings.md` | The ruleset lives on GitHub behind the Administration permission, set by hand; no repo file decides which rules are in force. Trailer says deterministic. |

## Acronyms

- **AST** — Abstract Syntax Tree.
- **H1, H2, H3** — markdown heading levels one to three.
- **OKF** — Open Knowledge Format.
- **PR** — pull request.
- **SHA** — the hash naming a git commit.
- **TOML** — Tom's Obvious Minimal Language, the format of `pyproject.toml`.
- **UI** — user interface.
- **URI** — Uniform Resource Identifier.
- **WHY** — the reason behind a rule, as opposed to the rule.
- **YAML** — YAML Ain't Markup Language.
