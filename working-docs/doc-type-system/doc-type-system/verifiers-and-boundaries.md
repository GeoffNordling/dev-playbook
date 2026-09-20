---
type: General-Sheet
title: Verifiers and Boundaries
description: Step 1's holistic pass over the drained rulesets — every rule id with what decides it today, every detector id with the rule it maps to, the boundaries and what each runs, and the overlaps, restorations, and deferrals the read across Standards found
---

# Verifiers and Boundaries

The output of step 1's holistic pass in
[The system](/working-docs/doc-type-system/doc-type-system/ROOT.md#planned):
the two tables steps 2 and 3 build for real, drawn once by hand from the
drained rulesets and the detectors as they stand, and what reading them
across Standards found. The tables are a snapshot, not a source: step 2
replaces the first with data the table lint checks, and step 3 replaces
the second with config the boundaries read.

## Counts

| What | Count |
|---|---|
| Rules in the tree | 251 |
| Deterministic | 168 |
| Stochastic | 83 |
| Rules with a verifier today | 98 |
| Deterministic rules with no verifier | 71 |
| Ids the eleven detectors emit | 79 |
| Emitted ids whose id is a rule heading | 9 |

## Verifier table

One row per rule id. The verifier is the script or tool that decides the
rule today, with the id the script emits where it differs from the rule's;
a dash is a null row. A stochastic rule's verifier is the judge step 2
builds, so its row is null here by construction.


### build/canonical.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `build.ciyml` | det | repo-lint | `build.canonical-bytes` |
| `build.python-version` | det | repo-lint | `build.canonical-bytes` |
| `build.pre-commit-configyaml` | det | repo-lint | `build.canonical-block` |
| `build.makefile` | det | repo-lint | `build.canonical-block` |
| `build.artifactsmk` | det | — |  |
| `build.pyprojecttoml` | det | repo-lint | `build.canonical-value` |
| `build.gitignore` | det | repo-lint | `build.canonical-block` |
| `build.the-source-directory` | det | repo-lint | `build.self-audit` |

### build/python.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `build.name-mapping` | det | repo-lint |  |
| `build.entry-points` | det | — |  |
| `build.scripts` | det | — |  |
| `build.shebang-and-inline-metadata` | det | repo-lint | `build.script-python`<br>`build.script-shebang` |

### build/skeleton.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `build.required-files` | det | repo-lint | `build.required-file` |
| `build.root-only-files` | det | repo-lint | `build.forbidden` |
| `build.no-other-future-work-file` | det | repo-lint | `tracking.rogue-future-work-file` |
| `build.runnables-live-in-scripts` | det | repo-lint | `build.forbidden` |
| `build.dependencies-live-in-pyprojecttoml` | det | repo-lint | `build.forbidden` |
| `build.python` | det | — |  |
| `build.uvlock-and-python-version` | det | repo-lint | `build.required-file` |
| `build.python-package` | det | — |  |
| `build.one-package-under-src` | det | repo-lint | `build.name-mapping` |
| `build.python-source` | det | — |  |
| `build.tests-present` | det | repo-lint | `build.required-file` |
| `build.javascript` | det | — |  |
| `build.lockfile-committed` | det | repo-lint | `build.required-file` |

### decisions/records.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `decisions.the-bar` | sto | — |  |
| `decisions.scope` | sto | — |  |
| `decisions.the-directory` | det | — |  |
| `decisions.sequential-numbering` | det | decisions-lint |  |
| `decisions.slug-case` | det | — |  |
| `decisions.template` | det | — |  |
| `decisions.context-decision-and-reason` | sto | — |  |
| `decisions.date` | det | — |  |
| `decisions.immutable-after-merge` | det | — |  |
| `decisions.status-vocabulary` | det | decisions-lint |  |
| `decisions.supersession-target` | det | — |  |
| `decisions.optional-sections` | det | — |  |
| `decisions.external-convention-evaluation` | sto | — |  |
| `decisions.what-was-examined` | sto | — |  |

### distribution/channel.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `distribution.a-publisher-dogfoods-its-manifest` | det | repo-lint | `distribution.dogfood` |
| `distribution.a-valid-manifest` | det | pre-commit validate-manifest |  |
| `distribution.a-pinned-rev` | det | workspace-lint | `distribution.pin` |

### harness/claude-content.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `harness.no-frontmatter` | det | — |  |
| `harness.operational-scope` | sto | — |  |
| `harness.one-scope` | sto | — |  |
| `harness.global-file` | det | — |  |
| `harness.two-sections` | det | harness-files-lint | `harness.global-claude-shape` |
| `harness.required-rules` | det | harness-files-lint | `harness.global-claude-rules` |
| `harness.one-rule-per-heading` | sto | — |  |

### harness/runbook-conventions.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `harness.location` | det | — |  |
| `harness.front-matter` | det | harness-files-lint | `harness.parse`<br>`harness.required-field`<br>`harness.unknown-field` |
| `harness.name-matches-its-home` | det | harness-files-lint | `harness.name-match` |
| `harness.kebab-case-name` | det | harness-files-lint | `harness.name-format` |
| `harness.description` | det | harness-files-lint | `harness.description-length`<br>`harness.description-sentences`<br>`harness.description-trigger`<br>`harness.description-type` |
| `harness.description-states-what-and-when` | sto | — |  |
| `harness.model-and-effort` | det | harness-files-lint | `harness.effort-value`<br>`harness.model-value` |
| `harness.body-opens-with-an-h1` | det | harness-files-lint | `harness.body-h1` |
| `harness.steps-end-on-a-completion-criterion` | sto | — |  |
| `harness.carries-its-chain` | sto | — |  |
| `harness.skill` | det | — |  |
| `harness.bundle-layout` | det | — |  |
| `harness.model-invocation-flag` | det | harness-files-lint | `harness.dmi-type` |
| `harness.interactive-skills-inherit` | sto | — |  |
| `harness.tool-fields` | det | harness-files-lint | `harness.tools-format` |
| `harness.disallowed-tools-restate-nothing` | det | — |  |
| `harness.arguments` | det | harness-files-lint | `harness.arguments-format` |
| `harness.no-argument-placeholder` | det | — |  |
| `harness.references-one-level-deep` | det | harness-files-lint | `harness.references-depth` |
| `harness.skillmd-at-most-500-lines` | det | — |  |
| `harness.agent` | det | — |  |
| `harness.tools` | det | harness-files-lint | `harness.tools-format` |

### knowledge-organization/context-content.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.glossary-only` | sto | — |  |
| `knowledge-organization.vocabulary-type` | det | — |  |
| `knowledge-organization.the-language-section` | det | repo-lint | `knowledge-organization.doc-shape` |
| `knowledge-organization.entry-shape` | det | — |  |
| `knowledge-organization.tight-definitions` | sto | — |  |
| `knowledge-organization.project-terms-only` | sto | — |  |

### knowledge-organization/cross-references.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.reference-resolves` | det | ref-lint | `knowledge-organization.broken-reference` |
| `knowledge-organization.fragment-anchor-matches-the-slug` | det | ref-lint | `knowledge-organization.broken-reference` |
| `knowledge-organization.stable-named-anchor` | det | — |  |
| `knowledge-organization.citation-another-repo` | det | — |  |
| `knowledge-organization.skill-invocation` | det | — |  |
| `knowledge-organization.fixed-repo-root` | det | — |  |
| `knowledge-organization.link-same-bundle` | det | ref-lint | `knowledge-organization.wrong-form-citation` |
| `knowledge-organization.no-fixed-repo-root` | det | — |  |
| `knowledge-organization.workspace-path-for-a-stable-location` | det | — |  |
| `knowledge-organization.relative-path-inside-the-bundle` | det | — |  |
| `knowledge-organization.inline-code-for-a-varying-location` | sto | — |  |

### knowledge-organization/document-types.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.frontmatter-block` | det | okf-lint | `knowledge-organization.frontmatter` |
| `knowledge-organization.types` | det | okf-lint | `knowledge-organization.type` |
| `knowledge-organization.title` | det | okf-lint |  |
| `knowledge-organization.description` | det | okf-lint | `knowledge-organization.description-shape` |
| `knowledge-organization.description-voice` | sto | — |  |
| `knowledge-organization.resource` | det | okf-lint |  |
| `knowledge-organization.resource-names-the-asset` | sto | — |  |
| `knowledge-organization.no-tags-or-timestamp` | det | — |  |
| `knowledge-organization.recipe-description` | det | okf-lint | `knowledge-organization.resource` |
| `knowledge-organization.typed-standard-card-or-standard-ruleset` | det | okf-lint | `knowledge-organization.type-location` |
| `knowledge-organization.typed-loop` | det | okf-lint | `knowledge-organization.type-location` |

### knowledge-organization/documentation-sets/documentation-sets.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.an-index-in-every-directory` | det | okf-lint | `knowledge-organization.index-present` |
| `knowledge-organization.body-inside-its-concern` | sto | — |  |
| `knowledge-organization.rows-inside-the-set` | sto | — |  |
| `knowledge-organization.one-home` | sto | — |  |
| `knowledge-organization.distinct-concerns` | sto | — |  |
| `knowledge-organization.distinct-from-the-parent` | sto | — |  |
| `knowledge-organization.terms-defined-once` | sto | — |  |
| `knowledge-organization.terms-that-cross-sets` | sto | — |  |

### knowledge-organization/documentation-sets/working-documentation-sets.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.speculative-voice` | sto | — |  |
| `knowledge-organization.the-link-tree` | det | — |  |
| `knowledge-organization.where-a-set-lives` | det | — |  |
| `knowledge-organization.a-set-stands-on-main` | det | — |  |
| `knowledge-organization.working-docs-holds-only-sets` | det | — |  |
| `knowledge-organization.worklist` | det | — |  |
| `knowledge-organization.buckets` | sto | — |  |
| `knowledge-organization.terms` | sto | — |  |
| `knowledge-organization.acronyms` | sto | — |  |

### knowledge-organization/indexes.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.typeless` | det | — |  |
| `knowledge-organization.the-introduction` | det | okf-lint | `knowledge-organization.index-intro` |
| `knowledge-organization.the-opening-sentence` | sto | — |  |
| `knowledge-organization.the-listing` | det | okf-lint | `knowledge-organization.index` |
| `knowledge-organization.ordering` | det | okf-lint | `knowledge-organization.index-ordering` |
| `knowledge-organization.the-root-index` | det | — |  |
| `knowledge-organization.okf-version-declared` | det | okf-lint | `knowledge-organization.index` |

### knowledge-organization/loop-conventions.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.one-graph` | det | loop-lint | `knowledge-organization.loop-graph` |
| `knowledge-organization.what-the-paragraph-says` | sto | — |  |
| `knowledge-organization.three-verb-sections` | det | loop-lint | `knowledge-organization.loop-sections` |
| `knowledge-organization.nodes-and-entries-agree` | det | loop-lint | `knowledge-organization.loop-nodes` |
| `knowledge-organization.edges-follow-the-shape` | det | loop-lint | `knowledge-organization.loop-edges` |
| `knowledge-organization.entries-point-and-condition` | det | loop-lint | `knowledge-organization.loop-entries` |
| `knowledge-organization.an-act-links-a-runbook` | det | loop-lint | `knowledge-organization.loop-entries` |

### knowledge-organization/readme-content.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.h1` | det | repo-lint | `knowledge-organization.doc-shape` |
| `knowledge-organization.the-purpose-sentence` | sto | — |  |
| `knowledge-organization.no-agent-instructions-or-decisions` | sto | — |  |
| `knowledge-organization.no-roster-of-harness-injected-files` | sto | — |  |

### knowledge-organization/type-registry.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `knowledge-organization.global-table` | det | — |  |
| `knowledge-organization.row-shape` | det | okf-lint | `knowledge-organization.registry-row` |
| `knowledge-organization.row-description` | det | okf-lint | `knowledge-organization.registry-row` |
| `knowledge-organization.alphabetical-order` | det | okf-lint | `knowledge-organization.registry-row` |
| `knowledge-organization.local-declaration` | det | okf-lint | `knowledge-organization.registry-location` |
| `knowledge-organization.mapping-entry-shape` | det | okf-lint | `knowledge-organization.registry-row` |
| `knowledge-organization.alphabetical-keys` | det | okf-lint | `knowledge-organization.registry-row` |
| `knowledge-organization.add-never-shadow` | det | okf-lint | `knowledge-organization.registry-row` |

### modules/design.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `modules.deep-not-shallow` | sto | — |  |
| `modules.internal-seams-stay-inside` | sto | — |  |
| `modules.two-adapters-or-no-seam` | sto | — |  |
| `modules.dependencies-are-accepted-not-constructed` | sto | — |  |
| `modules.a-port-at-a-process-boundary` | sto | — |  |
| `modules.the-interface-is-the-test-surface` | sto | — |  |
| `modules.results-are-returned-not-written` | sto | — |  |

### prose/conventions.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `prose.one-rule-one-place` | sto | — |  |
| `prose.current-state-and-next-steps-only` | sto | — |  |
| `prose.point-at-canonical-artifacts` | sto | — |  |
| `prose.open-with-purpose` | sto | — |  |
| `prose.declare-before-use` | sto | — |  |
| `prose.block-form-fits-its-content` | sto | — |  |
| `prose.declarative-present-tense` | sto | — |  |
| `prose.positive-statement` | sto | — |  |
| `prose.no-slop-tics` | sto | — |  |
| `prose.harness-loaded-agent-instructions` | det | — |  |
| `prose.no-first-person` | det | prose-lint | `prose.agent-facing-voice` |
| `prose.declarative-documents` | det | — |  |
| `prose.third-person` | sto | — |  |
| `prose.name-concepts-once-use-consistently` | sto | — |  |
| `prose.terminology-the-person-is-the-user` | sto | prose-lint | `prose.banned-word` |
| `prose.spelling` | det | prose-lint | `prose.judgment-spelling` |
| `prose.heading-casing` | sto | — |  |
| `prose.grammatical-parallelism` | sto | — |  |

### python/style.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `python.empty-init` | det | python-lint |  |
| `python.docstrings` | det | ruff check (D) |  |
| `python.docstring-content` | sto | — |  |
| `python.fail-loudly` | sto | — |  |
| `python.module-layout` | det | — |  |
| `python.no-future-annotations` | det | python-lint |  |
| `python.helper-justification` | sto | — |  |
| `python.helper-placement` | det | — |  |
| `python.formatted-by-ruff-format` | det | ruff format |  |
| `python.annotated-signatures` | det | mypy |  |

### shell/conventions.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `shell.bash-declared` | det | — |  |
| `shell.shellcheck-clean` | det | shellcheck |  |
| `shell.disable-carries-a-reason` | sto | — |  |
| `shell.formatting` | det | shfmt |  |
| `shell.executable-scripts` | det | — |  |
| `shell.glue-only` | det | — |  |
| `shell.strict-mode` | det | — |  |
| `shell.sourced-fragments` | det | — |  |
| `shell.no-shebang-no-strict-mode` | det | — |  |
| `shell.dialect-directive` | det | — |  |
| `shell.bounded-to-shell-integration` | sto | — |  |

### standard/detectors.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `standard.read-only` | det | — |  |
| `standard.an-absent-surface-is-clean` | det | — |  |
| `standard.a-first-party-detector` | det | — |  |
| `standard.thin-shims` | det | — |  |
| `standard.git-runs-against-the-given-root` | det | — |  |
| `standard.the-hosting-pattern` | det | standards-lint | `standard.hook-surfaces` |
| `standard.offered-by-the-canonical-template` | det | standards-lint | `standard.hook-surfaces` |
| `standard.card-namespaced-rule-ids` | det | standards-lint | `standard.rule-matrix` |
| `standard.list-rules` | det | — |  |
| `standard.finding-format` | det | — |  |
| `standard.exit-codes` | det | — |  |

### testing/conventions.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `testing.pytest` | det | — |  |
| `testing.test-file-naming` | det | — |  |
| `testing.mirror-source-structure` | det | testing-lint | `testing.mirror-layout` |
| `testing.conftest-hierarchy` | det | — |  |
| `testing.arrange-act-assert` | sto | — |  |
| `testing.one-concept-per-test` | sto | — |  |
| `testing.no-logic-in-tests` | det | testing-lint | `testing.no-logic` |
| `testing.expected-values-come-from-outside-the-code` | sto | — |  |
| `testing.access-only-public-names` | det | testing-lint | `testing.no-private-access` |
| `testing.assert-on-observable-outputs` | sto | — |  |
| `testing.assert-on-outcomes-not-call-sequences` | sto | — |  |
| `testing.name-by-capability-not-mechanism` | sto | — |  |
| `testing.replace-dont-layer` | sto | — |  |
| `testing.no-test-of-a-non-deterministic-decision` | sto | — |  |
| `testing.the-lightest-double` | sto | — |  |
| `testing.double-at-the-port` | sto | — |  |
| `testing.fakes-for-stateful-dependencies` | sto | — |  |
| `testing.one-fake-per-interface` | sto | — |  |
| `testing.fakes-live-in-the-test-tree` | sto | — |  |
| `testing.fakes-implement-only-what-callers-use` | sto | — |  |
| `testing.mocks-at-boundaries-only` | sto | — |  |
| `testing.the-mocking-library` | det | — |  |
| `testing.fixtures-for-setup-and-teardown` | sto | — |  |
| `testing.narrowest-fixture-scope` | sto | — |  |

### tracking/issue-shapes.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `tracking.written-for-the-user` | sto | — |  |
| `tracking.behavioural-not-procedural` | sto | — |  |
| `tracking.one-goal` | sto | — |  |
| `tracking.user-intent` | sto | — |  |
| `tracking.closed-fences` | det | — |  |
| `tracking.build-leaf` | det | — |  |
| `tracking.build-labels` | det | workspace-lint | `tracking.tuple-valid` |
| `tracking.build-headings` | det | workspace-lint | `tracking.issue-brief-shape` |
| `tracking.spike` | det | — |  |
| `tracking.spike-labels` | det | workspace-lint | `tracking.tuple-valid` |
| `tracking.spike-headings` | det | workspace-lint | `tracking.issue-brief-shape` |
| `tracking.session-leaf` | det | — |  |
| `tracking.session-labels` | det | workspace-lint | `tracking.session-shape` |
| `tracking.session-headings` | det | workspace-lint | `tracking.issue-brief-shape` |
| `tracking.a-stable-body` | sto | — |  |
| `tracking.epic` | det | — |  |
| `tracking.category-only` | det | workspace-lint | `tracking.epic-shape` |
| `tracking.epic-headings` | det | workspace-lint | `tracking.epic-shape` |
| `tracking.no-child-list` | sto | — |  |
| `tracking.standing-rulings` | det | — |  |
| `tracking.wayfinder-map-or-ticket` | det | — |  |
| `tracking.wayfinder-labels` | det | workspace-lint | `tracking.wayfinder-shape` |
| `tracking.wayfinder-body` | det | workspace-lint | `tracking.wayfinder-shape` |
| `tracking.ticket-parentage` | det | workspace-lint | `tracking.wayfinder-shape` |

### tracking/label-scheme.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `tracking.valid-labels` | det | workspace-lint | `tracking.label-scheme` |

### tracking/repo-settings.md

| Rule id | Kind | Verifier today | Emits |
|---|---|---|---|
| `tracking.github-origin` | det | workspace-lint | `tracking.remote` |
| `tracking.squash-only-merges` | det | workspace-lint | `tracking.settings` |
| `tracking.default-branch-protection` | det | workspace-lint | `tracking.branch-protection` |

## Emitted ids

One row per id a detector emits today, with the rule heading it maps to
at step 2. A blank rule is an orphan check; its note says what happens.

| Emitted id | Detector | Rule at step 2 | Note |
|---|---|---|---|
| `decisions.sequential-numbering` | decisions-lint | `decisions.sequential-numbering` |  |
| `decisions.status-vocabulary` | decisions-lint | `decisions.status-vocabulary` |  |
| `harness.arguments-format` | harness-files-lint | `harness.arguments` |  |
| `harness.body-h1` | harness-files-lint | `harness.body-opens-with-an-h1` |  |
| `harness.description-length` | harness-files-lint | `harness.description` |  |
| `harness.description-sentences` | harness-files-lint | `harness.description` |  |
| `harness.description-trigger` | harness-files-lint | `harness.description` |  |
| `harness.description-type` | harness-files-lint | `harness.description` |  |
| `harness.dmi-type` | harness-files-lint | `harness.model-invocation-flag` |  |
| `harness.effort-value` | harness-files-lint | `harness.model-and-effort` |  |
| `harness.front-matter` | harness-files-lint | `harness.front-matter` |  |
| `harness.global-claude-rules` | harness-files-lint | `harness.required-rules` |  |
| `harness.global-claude-shape` | harness-files-lint | `harness.two-sections` |  |
| `harness.model-value` | harness-files-lint | `harness.model-and-effort` |  |
| `harness.name-format` | harness-files-lint | `harness.kebab-case-name` |  |
| `harness.name-match` | harness-files-lint | `harness.name-matches-its-home` |  |
| `harness.parse` | harness-files-lint | `harness.front-matter` |  |
| `harness.references-depth` | harness-files-lint | `harness.references-one-level-deep` |  |
| `harness.required-field` | harness-files-lint | `harness.front-matter` |  |
| `harness.tools-format` | harness-files-lint | `harness.tool-fields`, `harness.tools` |  |
| `harness.unknown-field` | harness-files-lint | `harness.front-matter` |  |
| `knowledge-organization.loop-edges` | loop-lint | `knowledge-organization.edges-follow-the-shape` |  |
| `knowledge-organization.loop-entries` | loop-lint | `knowledge-organization.entries-point-and-condition`, `knowledge-organization.an-act-links-a-runbook` |  |
| `knowledge-organization.loop-graph` | loop-lint | `knowledge-organization.one-graph` |  |
| `knowledge-organization.loop-nodes` | loop-lint | `knowledge-organization.nodes-and-entries-agree` |  |
| `knowledge-organization.loop-sections` | loop-lint | `knowledge-organization.three-verb-sections` |  |
| `knowledge-organization.description` | okf-lint | `knowledge-organization.description` |  |
| `knowledge-organization.description-shape` | okf-lint | `knowledge-organization.description` |  |
| `knowledge-organization.frontmatter` | okf-lint | `knowledge-organization.frontmatter-block` |  |
| `knowledge-organization.index` | okf-lint | `knowledge-organization.the-listing`, `knowledge-organization.okf-version-declared` |  |
| `knowledge-organization.index-intro` | okf-lint | `knowledge-organization.the-introduction` |  |
| `knowledge-organization.index-ordering` | okf-lint | `knowledge-organization.ordering` |  |
| `knowledge-organization.index-present` | okf-lint | `knowledge-organization.an-index-in-every-directory` |  |
| `knowledge-organization.registry-location` | okf-lint | `knowledge-organization.local-declaration` | a migration check on a legacy registry document; step 2 decides whether it stays |
| `knowledge-organization.registry-row` | okf-lint | `knowledge-organization.row-shape`, `knowledge-organization.row-description`, `knowledge-organization.alphabetical-order`, `knowledge-organization.mapping-entry-shape`, `knowledge-organization.alphabetical-keys`, `knowledge-organization.add-never-shadow` | one id over six rules; the split is read from the code at step 2 |
| `knowledge-organization.resource` | okf-lint | `knowledge-organization.resource`, `knowledge-organization.recipe-description` |  |
| `knowledge-organization.title` | okf-lint | `knowledge-organization.title` |  |
| `knowledge-organization.type` | okf-lint | `knowledge-organization.types` |  |
| `knowledge-organization.type-location` | okf-lint | `knowledge-organization.typed-standard-card-or-standard-ruleset`, `knowledge-organization.typed-loop` |  |
| `prose.agent-facing-voice` | prose-lint | `prose.no-first-person` |  |
| `prose.banned-word` | prose-lint | `prose.terminology-the-person-is-the-user` | decides one word of a stochastic rule, and scans code and config beyond the prose population; step 2 gives it its own heading |
| `prose.judgment-spelling` | prose-lint | `prose.spelling` |  |
| `python.empty-init` | python-lint | `python.empty-init` |  |
| `python.no-future-annotations` | python-lint | `python.no-future-annotations` |  |
| `knowledge-organization.broken-reference` | ref-lint | `knowledge-organization.reference-resolves`, `knowledge-organization.fragment-anchor-matches-the-slug` |  |
| `knowledge-organization.wrong-form-citation` | ref-lint | `knowledge-organization.link-same-bundle` |  |
| `build.canonical-block` | repo-lint | `build.pre-commit-configyaml`, `build.makefile`, `build.gitignore` |  |
| `build.canonical-bytes` | repo-lint | `build.ciyml`, `build.python-version` |  |
| `build.canonical-value` | repo-lint | `build.pyprojecttoml` |  |
| `build.forbidden` | repo-lint | `build.runnables-live-in-scripts`, `build.dependencies-live-in-pyprojecttoml`, `build.root-only-files` |  |
| `build.name-mapping` | repo-lint | `build.name-mapping`, `build.one-package-under-src` | also decides `one-package-under-src`, a skeleton rule |
| `build.required-file` | repo-lint | `build.required-files`, `build.uvlock-and-python-version`, `build.tests-present`, `build.lockfile-committed` |  |
| `build.script-python` | repo-lint | `build.shebang-and-inline-metadata` |  |
| `build.script-shebang` | repo-lint | `build.shebang-and-inline-metadata` |  |
| `build.self-audit` | repo-lint | `build.the-source-directory` |  |
| `distribution.dogfood` | repo-lint | `distribution.a-publisher-dogfoods-its-manifest` |  |
| `knowledge-organization.doc-shape` | repo-lint | `knowledge-organization.h1`, `knowledge-organization.the-language-section` | one id, two rules in two rulesets; splits at step 2 |
| `tracking.rogue-future-work-file` | repo-lint | `build.no-other-future-work-file` | the rule is build's, not tracking's; renamed at step 2 |
| `standard.card-directory` | standards-lint |  | cards.md, undrained; retires at step 4 |
| `standard.card-layout` | standards-lint |  | cards.md, undrained; retires at step 4 |
| `standard.card-question` | standards-lint |  | cards.md, undrained; retires at step 4 |
| `standard.card-shadows-upstream` | standards-lint |  | cards.md, undrained; retires at step 4 |
| `standard.catalog-order` | standards-lint |  | cards.md, undrained; retires at step 4 |
| `standard.hook-surfaces` | standards-lint | `standard.the-hosting-pattern`, `standard.offered-by-the-canonical-template` | the closure leg moves to the boundary table at step 3 |
| `standard.rule-matrix` | standards-lint | `standard.card-namespaced-rule-ids` | superseded by the table lint at step 2 |
| `testing.mirror-layout` | testing-lint | `testing.mirror-source-structure` |  |
| `testing.no-logic` | testing-lint | `testing.no-logic-in-tests` |  |
| `testing.no-private-access` | testing-lint | `testing.access-only-public-names` |  |
| `distribution.pin` | workspace-lint | `distribution.a-pinned-rev` |  |
| `tracking.branch-protection` | workspace-lint | `tracking.default-branch-protection` |  |
| `tracking.epic-shape` | workspace-lint | `tracking.category-only`, `tracking.epic-headings` |  |
| `tracking.issue-brief-shape` | workspace-lint | `tracking.build-headings`, `tracking.spike-headings`, `tracking.session-headings` |  |
| `tracking.label-scheme` | workspace-lint | `tracking.valid-labels` |  |
| `tracking.no-blocked-label` | workspace-lint |  | no rule; subsumed by `tracking.valid-labels` (the scheme has no blocked label); retires at step 2 |
| `tracking.remote` | workspace-lint | `tracking.github-origin` |  |
| `tracking.session-shape` | workspace-lint | `tracking.session-labels` |  |
| `tracking.settings` | workspace-lint | `tracking.squash-only-merges` |  |
| `tracking.tuple-valid` | workspace-lint | `tracking.build-labels`, `tracking.spike-labels` |  |
| `tracking.wayfinder-shape` | workspace-lint | `tracking.wayfinder-labels`, `tracking.wayfinder-body`, `tracking.ticket-parentage` |  |

| Tool | Rule | Where it runs |
|---|---|---|
| ruff format | `python.formatted-by-ruff-format` | pre-commit hook `ruff-format`; `make format-check` at pre-push |
| ruff check | `python.docstrings` through the `D` family | pre-commit hook `ruff-check`; `make lint` at pre-push |
| mypy | `python.annotated-signatures` | `make typecheck` at pre-push only |
| shellcheck | `shell.shellcheck-clean` | pre-commit hook |
| shfmt | `shell.formatting` | pre-commit hook |
| pre-commit validate-manifest | `distribution.a-valid-manifest` | inside playbook-lint, where the repo has a manifest |

## Boundary table

The boundaries as this repo and the canonical config station them today.
A consumer repo has the same rows without the two dev-playbook-only hooks.

| Boundary | Fires | Runs |
|---|---|---|
| pre-commit | every commit | `ruff-check`, `ruff-format`, `shellcheck`, `shfmt`, `playbook-lint` (the ten detectors of `DETECTORS` and `validate-manifest`); in dev-playbook also `web-typecheck` |
| pre-push | every push, `make check` | `ruff format --check`, `ruff check`, `mypy`, `pytest`, then `pre-commit run --all-files`, the pre-commit row again |
| CI | push and pull request to `main` | `pre-commit run --all-files` with `SKIP: ref-lint,web-typecheck`, the pre-commit row minus ref-lint's two ids; no tests |
| on demand | the user runs `scripts/workspace-lint` | workspace-lint's eleven ids, `UNGATED_AUDITS` |
| loop check | none | `loops/` holds only its index; no Loop exists yet |

Facts step 3 reads from this table:

- The `SKIP` in the canonical `ci.yml` is honored by playbook-lint per
  detector name, so `ref-lint` has no CI leg in any governed repo, for
  the reason the [Build Guide](/docs/guides/build.md#ci-runs-no-tests)
  gives; `web-typecheck` in the same `SKIP` names a hook only
  dev-playbook has, carried into every consumer's copy by the
  byte-identical rule.
- `mypy` and `pytest` run at pre-push only, so `python.annotated-signatures`
  and every test have no commit leg and no CI leg.
- Every null row above is ungated by construction, whatever the table says.

## What the read across Standards found

Fixed in this pass:

- **One id, two rules.** `knowledge-organization.entry-shape` was the
  trailer of both CONTEXT.md Content's and Type Registry's `Entry shape`;
  the registry's heading is now `Mapping entry shape`.
- **A definition stated twice.** File Skeleton's `Python source` restated
  The Python Project's definition of a Python file under `scripts/`; it
  now links [Scripts](/standards/build/python.md#scripts).
- **Three rules the drains dropped, restored.** Decision Record
  Conventions' immutability, as
  [Immutable after merge](/standards/decisions/records.md#immutable-after-merge);
  Cross-References' bare skill invocation, as
  [Skill invocation](/standards/knowledge-organization/cross-references.md#skill-invocation),
  since the population still names a reference to a skill; and a rule
  for the `validate-manifest` step playbook-lint already runs, as
  [A valid manifest](/standards/distribution/channel.md#a-valid-manifest).
- **Eight guides.** The drains of build, decisions, distribution,
  harness, knowledge-organization, prose, python, and shell had cut
  teaching, the reasons and worked examples behind the rules; each is
  restored at `docs/guides/<name>.md`, and every ruleset with a guide
  links it before its first rule. `docs/guides/modules.md` and
  `testing.md` were typed `General-Sheet` and are now `Guide`.

Kept, with the reason:

- File Skeleton's `Required files` names `.gitignore`,
  `.pre-commit-config.yaml`, `Makefile`, and `ci.yml`, whose existence the
  canonical rules imply. The skeleton rule is the one list of what
  exists; implication is not restatement.
- Decision Record Conventions' `Template` names `title` and
  `description`, which Document Types requires of every concept
  document. A template shows every key.
- Documentation Sets' `Terms that cross sets` and CONTEXT.md Content's
  `Project terms only` are the two sides of one criterion, each stated
  from its own population.

Deferred, each named in the plan step that owns it:

- Step 2: the emitted-id renames above; `prose.banned-word`, whose
  rule cannot be written in `prose/conventions.md` today because the
  check has no escape for the word's one legitimate mention; the
  `doc-shape` and `registry-row` splits; `no-blocked-label` retiring.
- Step 3: the two `ci.yml` facts above.
- Step 4: `knowledge-organization.typed-standard-card-or-standard-ruleset`
  loses the card; `harness/files.md`, `harness/writing-for-agents.md`,
  and `knowledge-organization/file-roles.md` have a guide to fold into.
- Step 10: every verifier here is a claim read from code, not a run;
  the three restored rules and `a-valid-manifest` are new predicates
  no run has yet confirmed.

## Acronyms

- **CI** — Continuous Integration.
