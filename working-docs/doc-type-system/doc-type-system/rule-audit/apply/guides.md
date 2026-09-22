---
type: General-Sheet
title: Guide Work Orders
description: The five Guides step 11 writes — one bullet each naming the file, when it is read, its gist, and the rules it takes
---

# Guide Work Orders

The five Guide work orders, one bullet each. A Guide agent loads [Guide Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/guide-prompt.md) and one bullet.

Where the rules that are not predicates go. Each rule's current text is the seed; the Guide is organised by the work, not by the rule list, and written in Sequence, Step, and Reference per [Instruction Encoding](/doc-types/guide/encoding.md) and [Guide Conventions](/standards/doc-type/guide-conventions.md): a run of actions is a sequence, a thing consulted is a reference, and the headings read down are the gist. Every Guide gets an `index.md` row under `guides/`. The Guides are written before the rules they take are deleted, so the seed text is still in place. The family pass deletes the rules after the Guides are written.

- **`guides/writing-a-detector.md`** (new Guide; read before writing a first-party detector). The detector contract: exit 0 clean, 1 findings, 2 cannot run; `--list-rules`; the finding line; an absent surface is clean; why the gate must not write. Takes: `standard.exit-codes`, `standard.list-rules`, `standard.finding-format`, `standard.an-absent-surface-is-clean`.
- **`guides/design-and-testing.md`** (new Guide; read before writing code or tests). Deep modules, ports and adapters, dependencies accepted not constructed; the testing philosophy: observable outcomes, fakes at ports, the lightest double, one concept per test; fail loudly; docstrings say what a thing does; a sourced fragment mutates the parent shell only. Takes: `modules.deep-not-shallow`, `modules.internal-seams-stay-inside`, `modules.two-adapters-or-no-seam`, `modules.dependencies-are-accepted-not-constructed`, `modules.a-port-at-a-process-boundary`, `modules.the-interface-is-the-test-surface`, `python.docstring-content`, `python.fail-loudly`, `shell.bounded-to-shell-integration`, `testing.arrange-act-assert`, `testing.one-concept-per-test`, `testing.expected-values-come-from-outside-the-code`, `testing.assert-on-observable-outputs`, `testing.assert-on-outcomes-not-call-sequences`, `testing.name-by-capability-not-mechanism`, `testing.replace-dont-layer`, `testing.no-test-of-a-non-deterministic-decision`, `testing.the-lightest-double`, `testing.double-at-the-port`, `testing.fakes-for-stateful-dependencies`, `testing.one-fake-per-interface`, `testing.fakes-implement-only-what-callers-use`, `testing.mocks-at-boundaries-only`, `testing.fixtures-for-setup-and-teardown`, `testing.narrowest-fixture-scope`.
- **`guides/repo-settings.md`** (`standards/tracking/repo-settings.md` retyped `Guide` and moved; read when creating or auditing a governed repo on GitHub). The GitHub side of tracking: origin, merge settings, branch protection, the label set bootstrap-labels mints, one tracker per repo. Takes: `tracking.github-origin`, `tracking.squash-only-merges`, `tracking.default-branch-protection`, `tracking.valid-labels`, `tracking.one-home`.
- **`guides/governed-repo.md`** (new Guide; read when adding a repo to the workspace or writing a Decision Record). Which repos are governed and where the roster lives; what one Decision Record covers; a merged record is frozen; a working set is published on main. Takes: `distribution.the-roster`, `decisions.scope`, `decisions.immutable-after-merge`, `knowledge-organization.a-set-stands-on-main`.
- **`guides/writing-for-agents.md`** (existing Guide; read before writing a runbook or skill). A step ends on the condition that tells the agent the work is done; it joins the reference `Steps and completion criteria`. Takes: `doc-type.steps-end-on-a-completion-criterion`.

## Acronyms

None.
