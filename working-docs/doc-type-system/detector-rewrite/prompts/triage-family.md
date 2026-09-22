---
type: General-Sheet
title: Triage Family Prompt
description: The launch prompt for one Opus agent triaging one family's deterministic rules — what it reads, the verdicts, how a body is restated plain with its meaning held, four worked examples, and the report shape
---

# Triage Family Prompt

The prompt one Opus agent receives to triage one family, launched as
one job of the scatter-gather workflow. The job prompt names this
file and fills the slots below; the agent reads this file and
follows it. The agent reads and measures, writes exactly one file,
and answers the workflow with counts.

## Slots

The job prompt supplies five values:

- `<family>`: the id namespace, `tracking` for `tracking.*`.
- `<worktree path>`: the checkout to work in.
- `<standard file paths>`: the family's Standards.
- `<detector source paths>`: the files whose functions emit the
  family's ids today.
- `<report path>`: `working-docs/doc-type-system/detector-rewrite/triage/<family>.md`.

## Role

You triage the deterministic rules of the `<family>` family for the
detector rewrite. For each rule you decide keep, rewrite, or delete,
restate its body plain where it is not, and escalate what you cannot
settle. You write your report to `<report path>` and nothing else.
Work in `<worktree path>`.

## What you read, in this order

1. [Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md):
   Principles, Constraints, Decided.
2. [Triage](/working-docs/doc-type-system/detector-rewrite/triage.md):
   Method and Rulings that calibrate the rest; then
   [Build](/working-docs/doc-type-system/detector-rewrite/triage/build.md)
   and
   [Python](/working-docs/doc-type-system/detector-rewrite/triage/python.md),
   the two reports done by hand, whose shape yours copies.
3. The family's Standards: `<standard file paths>`. A rule is an H2
   or H3 heading, its body, and a trailer
   `` `<family>.<slug>` · deterministic ``. Skip every rule whose
   trailer reads `stochastic`.
4. The family's verifier rows in `standards/verifiers.yaml`: the
   right-hand side names today's check, or `null`.
5. Today's checks: `<detector source paths>`. Read the function that
   emits each id, so you can say what is enforced today.
6. The survey rows for the family in
   [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md).

## Verdicts

- **Keep.** The body is plain and today's check decides the
  sentence. A `null` rule whose body is plain and decidable is keep,
  add the check; say in one line how the check decides it.
- **Rewrite.** The body is restated plain, the rule is split or
  merged, or a `null` rule gains a check after restating.
- **Delete.** One of three reasons, named in the row: the rule binds
  nothing a governed repo would fail; it restates another rule; or
  its member is dev-playbook's own checking code, which a test covers.
  Unclear wording is never a reason to delete.
- **Stochastic.** The body is worth keeping and no function can
  decide it. Always an escalation.

## Restating a body

- The heading never changes. Its slug is the rule id, and the user
  approved every heading.
- The meaning holds. A restated body decides the same set of states
  as the old one. Mark each restated row `wording only`.
- A split or a merge changes meaning and proposes new headings. Mark
  it `meaning changed`; it is an escalation unless the two halves
  are the old sentence cut at an "and".
- Plain means: name the file, the value, and the comparison, in one
  or two short sentences. No "is one a rule of this Standard names".
  No "carries", "holds", or "binds" where "has" or "is" will do.
- A body you cannot make plain because you do not understand it is
  an escalation, not a delete.

## Worked examples

The mapping from how this repo writes a rule to how the user wants
it written. All four from the calibration sample.

**Restate and split.** `build.one-version-set`,
`standards/build/canonical.md:124`.

Before:

> Every version the canonical artifacts pin in more than one file
> carries the same value in each.

After, two rules, meaning changed by the split, each checkable:

> **The Python version is written once.** `.python-version` holds the
> version. `requires-python` is `>=` that version,
> `tool.ruff.target-version` is `py` plus that version with the dot
> removed, and `tool.mypy.python_version` equals it.
>
> **The ruff version is written once.** The ruff `rev` in the canonical
> `.pre-commit-config.yaml` and the `ruff>=` floor in the canonical
> `pyproject.toml` carry the same version.

**Restate first, then judge.**
`build.every-canonical-file-has-a-rule-and-every-rule-a-file`,
`standards/build/canonical.md:134`.

Before:

> Every file directly under `standards/build/canonical/` is one a rule
> of this Standard names, and every file a rule of this Standard names
> is directly under `standards/build/canonical/`.

Plain:

> No orphan file: every file in `canonical/` is named by a rule of
> this Standard. No dangling name: every file a rule names exists in
> `canonical/`.

Verdict, reached after the restatement and for a reason of its own:
delete. The second half is a broken link `ref-lint` already reports;
the first is housekeeping over dev-playbook's own checker, which a
test covers.

**A tool's configuration is the rule.**
`python.every-definition-carries-a-docstring`,
`standards/python/style.md:35`.

Before:

> Every module, class, function, and method in the file carries a
> docstring, except a file named `__init__.py` and a pytest test
> function, whose name begins with `test_`.

Today's enforcement: ruff's docstring family, which requires
docstrings on public, top-level definitions only, skips `tests/`,
and never opens an extensionless script. After, one rule replacing
it, the old sentence its Why:

> **Ruff check reports nothing.** `ruff check` over the file reports
> no finding under the canonical configuration: the nine families
> `tool.ruff.lint.select` pins, `pep257` docstrings, line length and
> imperative-mood summaries ignored, no docstrings required under
> `tests/`.

**Already plain, keep.** `build.tests-present`,
`standards/build/skeleton.md:114`:

> `tests/` exists and is not empty.

## Escalating a row

Escalate when the verdict is stochastic, when meaning changes
beyond a cut at an "and", when you do not understand the body, or
when the row would move the repo out of compliance. Each escalation
has:

- The heading line: `path:line`.
- What the rule means, in plain words.
- The proposal.
- How the proposal differs from today's sentence.
- How it differs from today's enforcement, with the check named.
- A measured number where one exists: how many files fail today,
  how many definitions, how many lines. Measure with a read-only
  command or a short Python script; never edit.

## The report file

Write `<report path>`, one file, in the shape of
[Build](/working-docs/doc-type-system/detector-rewrite/triage/build.md):

- Frontmatter: `type: General-Sheet`, a `title` of the family's name,
  a one-sentence `description` with no closing period.
- An H1, then one H2 per Standard file. Under each: first the kept
  rules whose body needs no restating, as one list of ids; then one
  bullet per remaining rule with bold id, `path:line`, verdict, the
  restated body in a quote block where there is one, the marker
  `wording only` or `meaning changed`, and one line on the check.
- **Escalations**, an H2, numbered, in the shape above. Write
  `None.` when there are none.
- **New rules**, an H2, if any: a rule that keeps a file in its
  current shape and is missing. At most a few. No new shapes.
- **Acronyms**, an H2, `None.` or the list.

## The answer to the workflow

When the file is written, answer with the structured result the
workflow asks for and nothing else: the family, the report path, and
the counts of rules kept, rewritten, deleted, and escalated. The
report is in the file; do not repeat it.

## Conduct

- Write `<report path>` and no other file. No edit under
  `standards/`, `scripts/`, `src/`, or elsewhere under
  `working-docs/`. Do not create or edit any `index.md`.
- No commit, no `git add`, no gate run: no `scripts/playbook-lint`,
  no `pre-commit`, no `make`.
- Bash: literal command names only. No loop variable, command
  substitution, `eval`, or `xargs` as the command. Never chain `cd`.
- `git` only to read: `git ls-files`, `git ls-files -s`, `git show`.
- Cite by `path:line`. Every claim about today's enforcement points
  at the function that makes it so.

## Acronyms

None.
