---
type: General-Sheet
title: Registry Audit
description: The audit record behind the registry refactor — every markdown file counted by registry kind, and what the General-Sheet and Guide files hold
---

# Registry Audit

The counts and per-file readings taken on 2026-09-02, the record behind
[Registry Refactor](/no-more-slop-branch-working-files/REGISTRY-REFACTOR.md).
Everything here is observation; no row is a decision.

## Every markdown file by kind

201 tracked `.md` files. `classify()` in `src/dev_playbook/md.py` sorts
them into concept (122), index (21), and harness (58). Every file landed
in a kind from one of the two registries.

The workspace column counts the sibling main checkouts under
`~/workspace`. headless-lab is excluded: its counts mirror this repo's
almost row for row, so it is a copy of dev-playbook rather than a
consumer.

| Kind | Registry | Here | Workspace | Ruling in doc-type-system.md | Machinery today |
|---|---|---|---|---|---|
| Standard | document-types | 34 | 3 | Standard doc-type | `type-location` |
| Decision-Record | document-types | 26 | 19 | absent, so not important | template, numbering, immutability, decisions-lint |
| General-Sheet | document-types | 20 | 32 | absent, so not important | none |
| Standard-Card | document-types | 14 | 2 | Standard doc-type | four cells, standards-lint, catalog index |
| Guide | document-types | 10 | 58 | important, no doc-type | none |
| README | document-types | 7 | ~32 | absent | repo-lint doc-shape |
| Recipe-Description | document-types | 3 | 0 | absent | `resource` required |
| Instrument-Spec | document-types | 2 | 0 | absent | `## Employed by` required |
| Vocabulary | document-types | 1 | 5 | separate, the vocabulary API | repo-lint doc-shape |
| Reference | document-types | 1 | 0 | absent | prose-lint exempt |
| Candidate-List | document-types | 1 | 6 | absent | candidates standard |
| Log | document-types | 0 | 34 | absent | none |
| Survey | document-types | 0 | 6 | absent | none |
| Spec-Item | document-types | 0 | 14 | absent | none here |
| index.md | `classify()` | 21 | — | — | okf-lint listing rule |
| SKILL.md | harness files | 36 | — | Runbook doc-type | chain, chaingen, harness-files-lint |
| agents/*.md | harness files | 9 | — | Runbook doc-type | chain, chaingen, harness-files-lint |
| skill references/*.md | harness files | 9 | — | inside the runbook bundle | none |
| CLAUDE.md | harness files | 2 | — | absent | claude-content standard |
| rules/*.md | harness files | 2 | — | absent | none |

One consumer local extension exists: mission-control's `Idea`, 44
instances.

## What the General-Sheet files hold

Twenty-five files. Each row is a reading of the file's content.

| File | What it holds |
|---|---|
| doc-types/doc-type.md | the definition of the doc-type kind and the loop |
| doc-types/doc-type-system.md | this repo's instantiation and the registry rulings |
| doc-types/runbook/definition.md | the Runbook doc-type's definition |
| doc-types/runbook/contract-shape.md | the Runbook doc-type's shape |
| doc-types/runbook/encoding.md | the Runbook doc-type's encoding spec |
| doc-types/runbook/residual-ledger.md | a table, one row per ported runbook |
| doc-types/standard-card/definition.md | the Standard-Card doc-type's definition |
| doc-types/standard-card/contract-shape.md | the Standard-Card doc-type's shape, with the generated view |
| doc-types/standard-card/encoding.md | the Standard-Card doc-type's encoding spec |
| doc-types/standard-card/residual-ledger.md | empty, every card fits the four cells |
| doc-types/standard/definition.md | the Standard doc-type's definition |
| doc-types/standard/contract-shape.md | the Standard doc-type's shape, with the two-table view |
| doc-types/standard/encoding.md | the Standard doc-type's encoding spec |
| doc-types/standard/residual-ledger.md | empty |
| docs/system-legibility.md | the doctrine |
| docs/writing-improvement-process.md | a process description, its attempts, principles, and platform facts, four H2s |
| docs/writing-improvement-process/writing-improvement-log.md | newest-first entries, one per writing session |
| docs/writing-improvement-process/writing-improvement-problems.md | a catalog of named patterns, each with a countermeasure where one exists |
| docs/external-skill-verdicts.md | a table: skill, verdict, date, reason |
| docs/machines.md | the machines the workspace runs on and what differs |
| docs/headless.md | findings on billing and flags for headless runs |
| docs/sandboxing.md | the sandbox's status after Decision Record 0024 and the intended direction |
| docs/measurement-derivation.md | how captured hook events become metrics, with the assertions run first |
| NO-MORE-SLOP.md | the branch plan, the working set's root |
| PARKING-LOT.md | text evicted from Standards during the ports, one entry each with provenance |

Related facts. The registry defines `Log` as "a chronological
operational record whose entries are appended as events occur".
[Working Documentation Sets](/standards/knowledge-organization/working-documentation-sets.md)
says members "typically carry `type: General-Sheet`". Five of the twenty
files are tables of fixed-shape rows. Ten are the doc-type family's own
files.

## What the Guide files hold

Nine files, all under `software-factory/`. All nine were listed in the
Define cell of the Software Factory card, `standards/software-factory.md`,
since deleted.
The registry defines Guide as "a teaching or procedure doc, read to
learn how to do or think about something, not to be measured against".
Three name themselves a contract in their own title or description:
deviation-contract.md, review-contract.md, and factory-operations.md
("the factory's operating contract"). okf-lint's
`knowledge-organization.type-location` rule forbids `type: Standard`
outside `standards/`.

review-contract.md, 425 lines, carries twelve H2s: The stance, The green
gate, The two severities, Findings are threads, The cycle header, Delta
re-review, Resolution ownership, The verdict and the cap, Suggestion
dispositions, The `gh` mechanics (holding a `jq` script), The report
envelope, Escalation. factory-operations.md, 403 lines, carries seven.

In the consumer repos, Guide has 58 instances and Standard has 3.

## Other readings

- The 34 files typed `Standard` all live under `standards/<name>/`
  directories, the content directories the cards point into.
- Two of them describe themselves as recipes in their own
  description: `standards/standard/consuming.md` and
  `standards/semantic-validation/consuming.md`. A third,
  `standards/build/bootstrap.md`, did until the Build port retyped it
  `Guide`.
- Decision-Record's machinery is a template, sequential numbering, and
  immutability in
  [Decision Record Conventions](/standards/decisions/records.md), and
  `scripts/decisions-lint`.
- The rule/procedure split has one home,
  [File Roles](/standards/knowledge-organization/file-roles.md). Echoes
  only elsewhere: the harness registry's "documentation that acts,
  invoked by name", two rows in external-skill-verdicts.md, and the branch
  plan's completed item.

## Acronyms

None.
