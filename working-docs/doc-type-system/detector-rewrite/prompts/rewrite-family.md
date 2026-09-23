---
type: General-Sheet
title: Rewrite Family Prompt
description: The launch prompt for one Opus agent rewriting one family's checks — what it reads, the five steps from report to retired script, how a check, its test, and its Standard are written, the report shape, and its conduct inside the Ralph loop
---

# Rewrite Family Prompt

The prompt one Opus agent receives to build one family of the
detector rewrite, as one iteration of the Ralph loop in
[Rewrite Plan](/working-docs/doc-type-system/detector-rewrite/plan.md#phase-3-one-family-at-a-time).
The loop's task line names this file and fills the slots below; the
agent reads this file and follows it. The family's triage report is
the specification: the agent builds what the report says, and
decides nothing the report has settled.

## Slots

The task line in `PLAN.md` supplies three values:

- `<family>`: the id namespace and the directory, `python` for
  `python.*` and `standards/python/`.
- `<retires>`: the old detectors this step deletes, by name, or
  `nothing`.
- `<report path>`:
  `working-docs/doc-type-system/detector-rewrite/rewrite/<family>.md`.

## Role

You build the `<family>` family: one check per rule the family's
triage report keeps, restates, or builds, one test per check, the
family's Standards edited to the report, and the old detectors in
`<retires>` deleted. You write `<report path>` and answer the loop.
Work in the current directory, a checkout of dev-playbook.

## What you read, in this order

1. [Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md):
   Principles, Constraints, Decided.
2. [Triage](/working-docs/doc-type-system/detector-rewrite/triage.md),
   Rulings that calibrate the rest; then the family's report,
   `working-docs/doc-type-system/detector-rewrite/triage/<family>.md`,
   whole, Escalations included: each escalation carries its ruling.
3. The scaffold you build on: `src/dev_playbook/model.py`,
   `src/dev_playbook/check_registry.py`, `src/dev_playbook/sources.py`,
   `src/dev_playbook/checks/shell.py`, and
   `tests/dev_playbook/test_check_registry.py`. Read them before
   writing any code.
4. The family's Standards, every `.md` under `standards/<family>/`,
   and the rule shape they obey,
   [A rule: heading, predicate, trailer](/standards/doc-type/standard-conventions.md#a-rule-heading-predicate-trailer).
5. Today's checks, the functions the report cites by `path:line`.
   Read each one before replacing it, so the new function decides
   what the old one decided and the report's restatement.
6. Where the family's report cites
   [Detector Fixes](/working-docs/doc-type-system/detector-rewrite/detector-fixes.md),
   the rows it cites.

## The five steps

1. **The checks.** `src/dev_playbook/checks/<module>.py`, `<module>`
   the family with hyphens as underscores. One function per rule,
   decorated `@check("<family>.<slug>")`, reading the model and
   nothing else. A rule the report leaves to ruff, shellcheck, shfmt,
   pre-commit's manifest validator, or `workspace-lint` is registered
   by name, `tool_check(id, hook="<name>", module=__name__)`, and
   gets no function.
2. **The tests.** `tests/dev_playbook/checks/test_<module>.py`, one
   test per function named `test_<slug with underscores>`, the name
   the meta-test looks for.
3. **The Standards.** Every rule of the family edited to the report:
   a restated body pasted from the report's blockquote, a deleted
   rule removed, a new rule added, a stochastic conversion made by
   changing the trailer's kind. Headings never change.
4. **The retirement.** Every detector in `<retires>` deleted: the
   script under `scripts/`, its package module where only that script
   imports it, its tests, its roster line, and every mention in docs.
5. **The gate.** `make check` green, `scripts/playbook-lint .` clean,
   and `uv run playbook check .` clean, on the repo as it stands. A
   new check that fails today does not enter the suite.

## Writing a check

- **The signature.** `def <name>(repo: Repo) -> Iterator[Finding]`,
  yielding `Finding(path, line, message)`; `line` is `None` for a
  file-level finding. The runner stamps the rule id. The function
  name is the slug with underscores, or a shorter name where the
  slug is long.
- **The model is the only input.** `repo.files` is every tracked
  path, `repo.markdown[path]` a parsed markdown file,
  `repo.python[path]` a parsed Python file with its `ast` tree,
  `repo.text(path)` any file's text, `repo.executable` the paths with
  the executable bit. No `open`, no `Path.read_text`, no `git`, no
  `subprocess`. A check that must read sibling repos on this machine
  is tagged `@check(id, needs=[WORKSPACE])` and is the one exception.
- **Data out of a Standard.** Where the rule reads a table or list a
  Standard's body holds, add a `Section` constant to `sources.py` and
  read it as `repo.markdown[S.path].section(S.heading)`; the test in
  `test_sources.py` pins every constant on its own. Never scan a
  Standard for a heading by text inside a check.
- **One rule, one function.** A helper two checks share is a private
  function in the same module. Nothing shared between families yet:
  the family after you will move it to `model.py` or a helper module
  if it recurs, and say so in its report.
- **Plain code.** Short functions, a docstring that states the rule
  in one sentence, no framework, no class where a function does.
  `make check` runs ruff, mypy strict, and the docstring rules over
  what you write.

## Writing a test

- **Build a repo in memory.** `Repo.from_files(Path("/r"), {path:
  bytes})`, with one member that passes and one that fails, and call
  the function directly. Assert the findings' paths and lines, and
  that the passing member yields none.
- **A test obeys the testing Standard.** No private-name access from
  a test, no `if` or `try` in a test body, the file mirrored under
  `tests/dev_playbook/checks/`.
- **The meta-test is the roster.** `make check` fails until every
  function has its named test and every registered id is a
  deterministic heading of its family. Read the failure; it names
  the missing test or the wrong id.

## Editing a Standard

- **A restated body.** Replace the first paragraph, and the block or
  table where the report restates one, with the report's blockquote,
  word for word. Where the report says the old sentence becomes the
  Why, move it into the `> **Why.**` block after the trailer.
- **A deleted rule.** Remove the heading, its body, its trailer, and
  its Why. Where the deletion empties a condition heading, remove the
  condition too. Then fix every link that pointed at the heading:
  `scripts/ref-lint .` names each one, and each is repointed at the
  nearest surviving rule or dropped, as the phase 2 commit did.
- **A new rule.** Added where the report places it, in the rule
  shape: heading, body, trailer, Why. A new rule enters only when
  its check is clean on this repo today.
- **The map.** Where rules leave or arrive, the file's `description`
  and its row in the directory's `index.md` say what the file now
  holds. The `population` changes only where the report says.

## Retiring a detector

For each name in `<retires>`, delete and repoint:

- `scripts/<name>` and `tests/test_<name with underscores>.py`.
- The package module under `src/dev_playbook/` that only this script
  imported, with its test under `tests/dev_playbook/`; a module
  another surviving script imports stays.
- The `"<name>"` entry in `DETECTORS` in
  `src/dev_playbook/playbook_lint.py`, and the tuples naming the
  script in `tests/test_rule_registry.py`.
- The row in the table of `scripts/README.md`, and every sentence in
  `scripts/README.md`, `scripts/index.md`, and elsewhere outside
  `working-docs/` that names the script. `grep -rn` finds them.

## The report file

Write `<report path>`, one file, in the shape of the triage reports:

- Frontmatter: `type: General-Sheet`, a `title` of the family's name,
  a one-sentence `description` with no closing period.
- An H1, then **Built**, an H2: one line per registered id, the
  function or hook name, and where the report's restatement went.
- **Deleted**, an H2: each rule removed and the links repointed.
- **Retired**, an H2: each file deleted, or `None.`
- **Set aside**, an H2: a rule the report builds whose check fails
  this repo today, with the finding that failed; the rule leaves the
  Standard and lives only here. `None.` where none.
- **Measured**, an H2: the wall time of `uv run playbook check .` and
  of `scripts/playbook-lint .` after your change, one line each.
- **Acronyms**, an H2, `None.` or the list.

Then add one row for the file to
`working-docs/doc-type-system/detector-rewrite/rewrite/index.md`, in
alphabetical order, and one entry to the Progress list of
[Rewrite Plan](/working-docs/doc-type-system/detector-rewrite/plan.md),
`**Step <n>, <family>, <date>.**`, that links the report and states
in two or three sentences what landed.

## The answer to the loop

The loop's own steps govern the rest: check the task off in
`PLAN.md`, append one line to `PROGRESS.md`, commit, and report the
count of tasks left. A point the report and the plan do not settle
is a judgment call: take the smallest step that keeps the gate green
and record it under your `PROGRESS.md` entry, never silently. The
sources win over a better idea.

## Conduct

- Edit only what the five steps name: `src/dev_playbook/checks/`,
  `src/dev_playbook/sources.py` and its test, the new test file,
  `standards/<family>/`, the retired files and the sentences that
  named them, links `ref-lint` reports, the report, its index row,
  the plan's Progress, `PLAN.md`, and `PROGRESS.md`. Nothing else
  under `working-docs/`; never the triage report; never the ROOT;
  never a checkpoint marker.
- Never edit a rule's heading, `model.py`, or `check_registry.py`.
  A change either needs is a judgment call in `PROGRESS.md`, and the
  work goes on without it.
- Never fix the repo to pass a new check. A failing new check is set
  aside, per the report file above.
- Bash: literal command names only. No loop variable, command
  substitution, `eval`, or `xargs` as the command. Never chain `cd`.
- Commit only at the loop's commit step, only on a green gate.

## Acronyms

None.
