---
type: General-Sheet
title: Predicate Pass Design
description: The step 10 design the user approves before any Standard changes — where the principles land, the rule count by family before and after, every new sentence, Explanation line, and Guide the rulings call for, the repo changes, the contested calls, the verifier-table delta, and the order of the edits
---

# Predicate pass design

What step 10 changes, for approval before any edit under `standards/`, `guides/`, `scripts/`, or `src/`. The ruling for every rule is the `ruling` column of [Rule Sort Sheet](/working-docs/doc-type-system/doc-type-system/rule-audit/sort-sheet.md), the one record of what happens to each rule. [Rule Audit Decision Sheet](/working-docs/doc-type-system/doc-type-system/rule-audit/decision-sheet.md) is evidence, the auditors' findings and the reviewers' verdicts; where a verdict and a ruling differ, the ruling stands and the Contested calls section below says why. This document holds only what those sheets do not: the new text, the small repo changes, the contested calls, and the order.

## Principles

The pass applies the Principles of [Doc-Type System](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles): a predicate is a test over state; kind is judged from the sentence; a scoping heading is not a rule; and the three working policies. Their permanent home after the pass is `standards/doc-type/explanation.md`, as the WHY of the rule-shape and population rules, so the next audit reads them beside the rules they explain. A Standard holds only predicates, so none of them is written as a rule.

## Count by family

Rules before and after, by trailer kind. A rule leaves as a delete, a move to a Guide, or a condition losing its trailer.

| family | before det | before stoch | after det | after stoch | delete | guide | condition |
|---|---|---|---|---|---|---|---|
| build | 26 | 0 | 20 | 0 | 1 | 0 | 5 |
| decisions | 9 | 5 | 6 | 3 | 2 | 2 | 1 |
| distribution | 5 | 0 | 3 | 0 | 1 | 1 | 0 |
| doc-type | 26 | 12 | 24 | 10 | 1 | 1 | 2 |
| harness | 6 | 3 | 5 | 3 | 0 | 0 | 1 |
| knowledge-organization | 45 | 21 | 39 | 20 | 1 | 1 | 5 |
| modules | 0 | 7 | 0 | 0 | 1 | 6 | 0 |
| prose | 6 | 14 | 4 | 14 | 0 | 0 | 2 |
| python | 7 | 3 | 4 | 0 | 4 | 2 | 0 |
| shell | 9 | 2 | 7 | 1 | 0 | 1 | 2 |
| standard | 20 | 1 | 14 | 2 | 0 | 4 | 1 |
| testing | 7 | 17 | 3 | 1 | 4 | 16 | 0 |
| tracking | 24 | 9 | 13 | 8 | 2 | 5 | 5 |
| **all** | 190 | 94 | 142 | 62 | 17 | 39 | 24 |

Of the 204 rules that stay, 133 keep their sentence, 42 get the new sentence below, 2 change trailer only, and 16 keep their sentence and get a detector fix.

## New sentences

The predicate as it will read. A residue row keeps the file-checkable part; its intent moves to the Explanation line in the next section. A rewrite row takes the reviewer's sentence where one exists and the auditor's where the reviewer agreed.

| rule | kind after | new sentence |
|---|---|---|
| [standard.thin-shims](/standards/standard/detectors.md#thin-shims) | deterministic | The script holds no rule logic: apart from its shebang and inline metadata block, its statements are at most one that puts the host repo's package on `sys.path`, one import from that package, and one call of the imported entry point. |
| [standard.git-runs-against-the-given-root](/standards/standard/detectors.md#git-runs-against-the-given-root) | deterministic | A first-party detector that runs git clears the variables `git rev-parse --local-env-vars` lists from the child environment. |
| [standard.read-only](/standards/standard/detectors.md#read-only) | stochastic | A first-party detector run without an explicit write flag leaves everything git tracks as it found it; `verifier-table --write` and `boundary-table --write` are enforcement, and a dependency the verifier table names may write at its gate, `ruff-format` and `shfmt -w`. |
| [build.one-version-set](/standards/build/canonical.md#one-version-set) | deterministic | Every version the canonical artifacts pin in more than one file carries the same value in each |
| [decisions.date](/standards/decisions/records.md#date) | deterministic | A Decision Record's `date` frontmatter key holds a `YYYY-MM-DD` date or `null` |
| [decisions.what-was-examined](/standards/decisions/records.md#what-was-examined) | stochastic | A Decision Record whose decision is a verdict on something outside the workspace names the source and pins at least one of the repository SHA and the release or version examined. |
| [doc-type.the-population](/standards/doc-type/standard-conventions.md#the-population) | deterministic | A file typed `Standard` names the population its rules bind in its frontmatter: a `population` key holding one phrase. |
| [harness.one-scope](/standards/harness/claude-content.md#one-scope) | stochastic | A nested <dir>/CLAUDE.md states no rule already stated in the root file above it. |
| [harness.members](/standards/harness/files.md#members) | deterministic | Every file under .claude/ or dotfiles/dot-claude/ in a governed repo matches a member row of the table below. |
| [knowledge-organization.reference-resolves](/standards/knowledge-organization/cross-references.md#reference-resolves) | deterministic | A reference names a file or a directory that exists in the referencing file's own repository |
| [knowledge-organization.one-home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home) | stochastic | A fact, rule, or decision has one home, the member whose concern is the thing the fact binds and the most general such member where the fact still holds; every other document in this repo links there and states the fact without its reason. |
| [tracking.user-intent](/standards/tracking/issue-shapes.md#user-intent) | stochastic | An issue's `User intent` section is written in the user's voice, not an agent's paraphrase. |
| [doc-type.the-rule-shape](/standards/doc-type/standard-conventions.md#the-rule-shape) | deterministic | Each rule of a Standard is a heading, a first paragraph, at most one block or table stating the target state, and last a trailer line, `` `<name>.<slug>` · deterministic `` or `` `<name>.<slug>` · stochastic ``; a level-three heading sits only under a level-two heading that carries no trailer, which scopes it. |
| [knowledge-organization.stable-named-anchor](/standards/knowledge-organization/cross-references.md#stable-named-anchor) | deterministic | A reference's `#anchor` carries no number that is the heading's position in the file; where the target numbers every heading by position and carries no other anchor, the reference carries no anchor. |
| [knowledge-organization.workspace-path-for-a-stable-location](/standards/knowledge-organization/cross-references.md#workspace-path-for-a-stable-location) | deterministic | A reference to a file in the referencing file's own repository is an inline link whose target is the full `~/workspace/<repo>/<path>` path, unless the target is inside the referencing file's own skill bundle. |
| [knowledge-organization.row-description](/standards/knowledge-organization/type-registry.md#row-description) | deterministic | Every row of the `## Types` table below its header holds, in its second cell, non-empty text on one line. |
| [knowledge-organization.mapping-entry-shape](/standards/knowledge-organization/type-registry.md#mapping-entry-shape) | deterministic | Each entry's key is a type name in Title Case, hyphen-joined for a multi-word name, and its value is non-empty text on one line. |
| [tracking.entry-shape](/standards/tracking/candidates.md#entry-shape) | deterministic | An entry is one list item: a bolded name, an em dash, then at most two sentences, with no fields, no acceptance criteria, and no checkboxes. |
| [build.name-mapping](/standards/build/python.md#name-mapping) | deterministic | The root `pyproject.toml` sets `project.name` to the repository's own name lowercased, the directory holding the shared `.git` and so the same from the main checkout and every worktree, `My-Repo` to `my-repo`, and the import package is that name with each hyphen an underscore, `my_repo`. |
| [build.entry-points](/standards/build/python.md#entry-points) | deterministic | `[project.scripts]` in the root `pyproject.toml` is absent, or every entry under it has the value `<module>:main`, where `<module>` is a module inside the import package and that module defines `main`. |
| [decisions.template](/standards/decisions/records.md#template) | deterministic | A Decision Record's frontmatter holds `type: Decision-Record`, a `title`, a `description`, and a `date`; its body opens with an H1 repeating the `title`. |
| [decisions.context-decision-and-reason](/standards/decisions/records.md#context-decision-and-reason) | stochastic | A Decision Record's body gives the context the decision was made in, the decision itself, and the reason for it. |
| [doc-type.one-sentence](/standards/doc-type/doc-type.md#one-sentence) | stochastic | `definition.md` opens with one sentence that says what one instance is. |
| [knowledge-organization.tight-definitions](/standards/knowledge-organization/context-content.md#tight-definitions) | stochastic | An entry's definition in a repo's `CONTEXT.md` is at most two sentences: one that says what the term is, and at most one more that sharpens it; where a concept document defines the term the definition links that document. |
| [knowledge-organization.skill-invocation](/standards/knowledge-organization/cross-references.md#skill-invocation) | deterministic | A reference to a skill names it by its slash invocation, `/<skill-name>`. |
| [knowledge-organization.description-voice](/standards/knowledge-organization/document-types.md#description-voice) | stochastic | A concept document's `description` is a sentence fragment in the present tense that names what the document is, what it governs, or, for a `Decision-Record`, the decision it records. |
| [knowledge-organization.speculative-voice](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#speculative-voice) | stochastic | Every member of a working documentation set writes a guess as a guess, and the set's `ROOT.md` declares the set speculative. |
| [knowledge-organization.where-a-set-lives](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#where-a-set-lives) | deterministic | A working documentation set is one directory under `working-docs/` at the repo root, `working-docs/<work>/`, holding the set's `index.md`, its `ROOT.md`, and its members under lowercase kebab-case names, flat or in subdirectories, except a member whose kind fixes its name (`README.md`, `PROMPT.md`, `SKILL.md`, `CLAUDE.md`, a Python module). |
| [knowledge-organization.buckets](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md#buckets) | stochastic | Every fact in a member of a working documentation set sits under a named section, its bucket, and a bucket holds facts of its own type only; the section under the member's H1, which says what the member is and what it is for, is exempt. |
| [prose.one-rule-one-place](/standards/prose/conventions.md#one-rule-one-place) | stochastic | Each rule the document states lives in the lead sentence of its section, except a statement of the document's own scope, which sits in the section under the H1. |
| [prose.point-at-canonical-artifacts](/standards/prose/conventions.md#point-at-canonical-artifacts) | stochastic | Where a file is itself the standard, the document links that file rather than reproducing its contents; naming one entry as a worked example is not reproduction. |
| [prose.open-with-purpose](/standards/prose/conventions.md#open-with-purpose) | stochastic | The opening states what the document is for and what a reader should be able to do after reading; an `index.md` and a `README.md` answer instead to the opening-sentence and purpose-sentence rules of the knowledge-organization Standard. |
| [prose.declarative-present-tense](/standards/prose/conventions.md#declarative-present-tense) | stochastic | Every sentence is in the present tense, except a sentence reporting a measurement or an incident that happened, and except in a member of a working documentation set, which may write a guess as a guess. |
| [prose.terminology-the-person-is-the-user](/standards/prose/conventions.md#terminology-the-person-is-the-user) | stochastic | One actor, the dispatcher, reviewer, and approver, is the `user` throughout the document, its frontmatter, code spans, and fenced blocks included, never a synonym, in any case, plural, or compound. A numbered Decision Record is exempt. |
| [prose.the-banned-word](/standards/prose/conventions.md#the-banned-word) | deterministic | The file does not contain a word the workspace vocabulary bans, `WORKSPACE_VOCABULARY` in `src/dev_playbook/prose_lint.py`, bare or plural, in any case, alone or in a compound, its frontmatter, code spans, and fenced blocks included. |
| [standard.the-hosting-pattern](/standards/standard/detectors.md#the-hosting-pattern) | deterministic | A first-party detector is reachable from its repo's published hook, named in the `playbook-lint` roster, wired as a `scripts/` hook its `.pre-commit-config.yaml` and `.pre-commit-hooks.yaml` both carry, or registered as an ungated audit, and has a row in a `scripts/README.md` script table where the repo has that file. |
| [standard.offered-by-the-canonical-template](/standards/standard/detectors.md#offered-by-the-canonical-template) | deterministic | A first-party detector the repo carrying `standards/build/canonical/` publishes in `.pre-commit-hooks.yaml` is a hook of that canonical `.pre-commit-config.yaml`'s pinned dev-playbook block, which offers exactly the ids that manifest publishes. |
| [standard.directory-layout](/standards/standard/tree.md#directory-layout) | deterministic | Every immediate subdirectory of `standards/` is a Standard directory: it holds at least one file typed `Standard`, and every other `.md` file under it, `index.md` aside, is typed `Standard` or `Explanation`; the only flat `.md` files under `standards/` are `README.md` and `index.md`. |

Rules whose sentence stands and whose block or exemption changes:

- [doc-type.carries-its-chain](/standards/doc-type/runbook-conventions.md#carries-its-chain): exemption clause becomes "except an edge the span vocabulary cannot carry".
- [harness.location](/standards/harness/files.md#location): the tree block gains the optional `agents/` bundle line the repo already uses.
- [knowledge-organization.entry-shape](/standards/knowledge-organization/context-content.md#entry-shape): the example block is rewritten to match `CONTEXT.md`: no colon after the bold term, one H3 group shown.
- [knowledge-organization.citation-another-repo](/standards/knowledge-organization/cross-references.md#citation-another-repo): the file's `population` phrase and preamble gain `except inside a code block, fenced or indented`; the rule sentence stands.
- [prose.block-form-fits-its-content](/standards/prose/conventions.md#block-form-fits-its-content): the `Table vs repeated structure` bullet becomes: the same shape with the same fields two or more times is a table; anything fewer or uneven is prose with bold leads.

## Explanation lines

One paragraph each in the family's `explanation.md`, under the rule's anchor: the why that left the predicate.

| rule | Explanation line |
|---|---|
| [standard.git-runs-against-the-given-root](/standards/standard/detectors.md#git-runs-against-the-given-root) | Clearing git's local environment variables is what makes a detector address the repo it was given when a hook runs it under an ambient `GIT_DIR`. |
| [build.one-version-set](/standards/build/canonical.md#one-version-set) | The pins are meant to be the latest stable releases, bumped together; that is why a version pinned in two files must agree. |
| [decisions.date](/standards/decisions/records.md#date) | Already present at `explanation.md`: the date is the day the decision was made, not the writing day, and null where that day is unrecoverable. |
| [decisions.what-was-examined](/standards/decisions/records.md#what-was-examined) | The pin lets a later reader tell whether the thing judged has changed since; the record's own `date` is the day it was read. |
| [doc-type.the-population](/standards/doc-type/standard-conventions.md#the-population) | standards-lint reports a Standard without a population. What a detector reports is not part of the predicate, so the clause lives here. |
| [harness.one-scope](/standards/harness/claude-content.md#one-scope) | A rule sits at the widest scope where it is true: machine-wide in the global source, repo-wide in the root file, only the delta in a nested file. A repo can check one part of that, the nested file against its root. |
| [harness.members](/standards/harness/files.md#members) | Claude Code fixes which files it reads; the table is the workspace's record of that set, and the predicate holds the repo to the table. |
| [knowledge-organization.reference-resolves](/standards/knowledge-organization/cross-references.md#reference-resolves) | A `~/workspace/<repo>/` target naming another repository resolves against that repo's main checkout. A repo cannot check the other side from its own files, so the predicate binds same-repo targets. |
| [knowledge-organization.one-home](/standards/knowledge-organization/documentation-sets/documentation-sets.md#one-home) | The same holds across repos: another repo links here rather than restating. A repo cannot check the other side. |
| [tracking.user-intent](/standards/tracking/issue-shapes.md#user-intent) | The section holds the user's own words, never an agent's paraphrase; only the user can vouch for that, so the predicate asks for the user's voice. |
| [doc-type.the-rule-shape](/standards/doc-type/standard-conventions.md#the-rule-shape) | The first paragraph is the predicate every member is held to; the block or table is the target state it compares against. An H2 without a trailer is a condition: it names which members the rules under it bind. |
| [knowledge-organization.stable-named-anchor](/standards/knowledge-organization/cross-references.md#stable-named-anchor) | An anchor names the concept the heading carries and so survives a renumbering; a positional number breaks on the next insert. |
| [knowledge-organization.workspace-path-for-a-stable-location](/standards/knowledge-organization/cross-references.md#workspace-path-for-a-stable-location) | The condition above says what stable means: a location fixed relative to the repo root. |
| [knowledge-organization.row-description](/standards/knowledge-organization/type-registry.md#row-description) | The second cell is a description a reader picks the type by. |
| [knowledge-organization.mapping-entry-shape](/standards/knowledge-organization/type-registry.md#mapping-entry-shape) | The value is a description a reader picks the type by. |
| [tracking.entry-shape](/standards/tracking/candidates.md#entry-shape) | The name is short and the sentences state intent; a candidate is a seed, not a specification. |

## Guides

Where the rules that are not predicates go. Each rule's current text is the seed; the Guide is organised by the work, not by the rule list. Every Guide gets an `index.md` row under `guides/`.

- **`guides/writing-a-detector.md`** (new Guide; read before writing a first-party detector). The detector contract: exit 0 clean, 1 findings, 2 cannot run; `--list-rules`; the finding line; an absent surface is clean; why the gate must not write. Takes: `standard.exit-codes`, `standard.list-rules`, `standard.finding-format`, `standard.an-absent-surface-is-clean`.
- **`guides/design-and-testing.md`** (new Guide; read before writing code or tests). Deep modules, ports and adapters, dependencies accepted not constructed; the testing philosophy: observable outcomes, fakes at ports, the lightest double, one concept per test; fail loudly; docstrings say what a thing does; a sourced fragment mutates the parent shell only. Takes: `modules.deep-not-shallow`, `modules.internal-seams-stay-inside`, `modules.two-adapters-or-no-seam`, `modules.dependencies-are-accepted-not-constructed`, `modules.a-port-at-a-process-boundary`, `modules.the-interface-is-the-test-surface`, `python.docstring-content`, `python.fail-loudly`, `shell.bounded-to-shell-integration`, `testing.arrange-act-assert`, `testing.one-concept-per-test`, `testing.expected-values-come-from-outside-the-code`, `testing.assert-on-observable-outputs`, `testing.assert-on-outcomes-not-call-sequences`, `testing.name-by-capability-not-mechanism`, `testing.replace-dont-layer`, `testing.no-test-of-a-non-deterministic-decision`, `testing.the-lightest-double`, `testing.double-at-the-port`, `testing.fakes-for-stateful-dependencies`, `testing.one-fake-per-interface`, `testing.fakes-implement-only-what-callers-use`, `testing.mocks-at-boundaries-only`, `testing.fixtures-for-setup-and-teardown`, `testing.narrowest-fixture-scope`.
- **`guides/repo-settings.md`** (`standards/tracking/repo-settings.md` retyped `Guide` and moved; read when creating or auditing a governed repo on GitHub). The GitHub side of tracking: origin, merge settings, branch protection, the label set bootstrap-labels mints, one tracker per repo. Takes: `tracking.github-origin`, `tracking.squash-only-merges`, `tracking.default-branch-protection`, `tracking.valid-labels`, `tracking.one-home`.
- **`guides/governed-repo.md`** (new Guide; read when adding a repo to the workspace or writing a Decision Record). Which repos are governed and where the roster lives; what one Decision Record covers; a merged record is frozen; a working set is published on main. Takes: `distribution.the-roster`, `decisions.scope`, `decisions.immutable-after-merge`, `knowledge-organization.a-set-stands-on-main`.
- **`guides/writing-for-agents.md`** (existing Guide; read before writing a runbook or skill). A step ends on the condition that tells the agent the work is done. Takes: `doc-type.steps-end-on-a-completion-criterion`.

## Deletes

Rule, trailer, verifier row, and Explanation paragraph all go; a detector check that emits the id goes with it.

`build.lockfile-committed`, `decisions.optional-sections`, `decisions.slug-case`, `distribution.a-pinned-rev`, `doc-type.disallowed-tools-restate-nothing`, `knowledge-organization.terms-defined-once`, `modules.results-are-returned-not-written`, `python.annotated-signatures`, `python.helper-justification`, `python.helper-placement`, `python.module-layout`, `testing.access-only-public-names`, `testing.no-logic-in-tests`, `testing.pytest`, `testing.the-mocking-library`, `tracking.prohibited-surfaces`, `tracking.standing-rulings`.

## Conditions

The 24 rows in the sort sheet's Conditions group lose their trailer line and their `verifiers.yaml` row; the heading and its sentence stay. The shape is written once, in the rewritten [doc-type.the-rule-shape](/standards/doc-type/standard-conventions.md#the-rule-shape) above, and standards-lint learns it: an H2 without a trailer must have at least one H3 rule under it.

## Repo changes

Small, named, and confirmed by a reviewer as oversights. Each is one commit-sized edit in the PR.

- `doc-type.interactive-skills-inherit`: three skills gain `model: inherit`: runbook-creator, enable-repo-governance, update-standards-pin.
- `harness.one-rule-per-heading`: `dotfiles/dot-claude/CLAUDE.md`: the repeatable-work rule moves under `## Behaviors`.
- `knowledge-organization.terms-that-cross-sets`: `CONTEXT.md` gains entries for strand and bucket.
- `knowledge-organization.the-link-tree`: this set's `ROOT.md` links the `rule-audit/` files; `software-factory/ROOT.md` is frozen pending deletion and stays.
- `knowledge-organization.acronyms`: acronym appendix added to `body-drain.md`, `personal-notes.md`, and every file under `rule-audit/`.
- `knowledge-organization.the-opening-sentence`: `docs/writing-improvement-process/index.md` and `doc-types/runbook/index.md` open by naming their contents.
- `prose.no-slop-tics`: `harness-recipes/README.md`: two flourishes cut.
- `prose.heading-casing`: rule gains "the `Considered Options` heading of a Decision Record is exempt"; `wayfinder/SKILL.md` heading recased.
- `prose.grammatical-parallelism`: four `prose/conventions.md` headings made parallel; their ids follow in `verifiers.yaml`, `explanation.md`, `working-documentation-sets.md`, `agents/doc-set-deslopper.md`.
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

The 16 rules whose detector tests less than the sentence. The sentence stands; the detector closes the gap named in the decision sheet's Weak checks section. Done in the detector step with the thin-shim moves, the `doc-type.one-base` check, and the removal of checks for deleted ids.

`build.pre-commit-configyaml`, `build.the-source-directory`, `doc-type.entries-point-and-condition`, `doc-type.references-one-level-deep`, `doc-type.three-verb-sections`, `knowledge-organization.fragment-anchor-matches-the-slug`, `knowledge-organization.h1`, `knowledge-organization.link-same-bundle`, `knowledge-organization.ordering`, `knowledge-organization.the-listing`, `knowledge-organization.types`, `prose.no-first-person`, `prose.the-repo-vocabulary`, `standard.the-boundary-table`, `tracking.closed-fences`, `tracking.wayfinder-body`.

## Verifier and boundary tables

`verifiers.yaml` loses 80 rows, the deletes, Guide moves, and conditions. Trailer changes: `doc-type.one-base` to deterministic, `standard.read-only` to stochastic, `tracking.artifacts` to stochastic. Both tables are regenerated by `verifier-table --write` and `boundary-table --write` after the edits and must round-trip clean.

## Order of the edits

1. `standards/doc-type/`: the rule-shape rewrite and the Principles paragraphs in its `explanation.md`. This is the doc-type definition change and waits for approval of this document.
2. Conditions: strip trailers and verifier rows; standards-lint gains the H2-without-trailer shape.
3. Deletes and Guide moves: write the four Guides, then remove the rules and their Explanation paragraphs.
4. New sentences and Explanation lines, family by family.
5. Repo changes.
6. Regenerate the two tables; standards-lint, verifier-table, and boundary-table pass.
7. Detector step: weak-check fixes, thin-shim moves, the one-base check, dropped checks for deleted ids; `pre-commit run --all-files` at least as fast as before.
8. PR for the user to merge.

## Acronyms

- **H1, H2, H3** — markdown heading levels one to three.
- **PR** — pull request.
- **SHA** — the hash naming a git commit.
- **WHY** — the reason behind a rule, as opposed to the rule.
