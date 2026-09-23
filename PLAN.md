# Plan: detector rewrite, phase 3, one family at a time

A Ralph loop works this file top to bottom. Each iteration, a fresh agent with
no memory reads this plan and the progress log, does the first unchecked task,
checks it off, and commits. Everything it needs to act is here — including the
Working notes below, where earlier iterations leave facts you will need. Add to
them whenever you learn something a future iteration would otherwise rediscover.

## Done when

- `DETECTORS` in `src/dev_playbook/playbook_lint.py` holds only `"loop-lint"`,
  and `scripts/` holds no detector but `loop-lint`.
- `src/dev_playbook/checks/` holds one module per family in the tasks below,
  and `uv run playbook checks` lists every deterministic trailer under
  `standards/` except the loop family's.
- `make check`, `scripts/playbook-lint .`, and `uv run playbook check .` are
  clean on the repo as it stands.
- `working-docs/doc-type-system/detector-rewrite/rewrite/` holds one report per
  task, each listed in its `index.md`.

## When the sources do not settle it

You will hit points this plan and its sources do not answer. Do not stop for
them, and do not decide them silently. Take the smallest step that keeps the
check gate green, record it as a judgment call in the progress log, and carry
on. A reviewer reads every one of them at the next checkpoint and rules.

1. The sources win, even where you can see a better idea. Record the better
   idea as a judgment call instead of acting on it.
2. Stay inside your task. Never edit the sources, reorder the plan, or work a
   task that is not yours.
3. Stop only for something whole and missing that no source names — then set a
   blocker rather than inventing it.

## Working notes

- Steps 1 to 12 are done: one check module per family under
  `src/dev_playbook/checks/`, one test per rule id under
  `tests/dev_playbook/checks/`, one report per family under
  `working-docs/doc-type-system/detector-rewrite/rewrite/`, and every
  old detector retired but `loop-lint` and `workspace-lint`. What remains
  is rework of what the audits found.
- A rework task names what to read; the sections Writing a check, Writing
  a test, Editing a Standard, and Conduct of
  `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`
  apply to every one.
- The sentence of a rule and the code of its check say the same thing.
  Where the code does less than the sentence, the sentence is reduced to
  the code, never the code grown. A rule heading never changes.
- A check that fails this repo today is not set aside silently: the task
  says what to do, and a judgment call goes in the progress log.
- The check gate is `make check`. `scripts/playbook-lint .` and
  `uv run playbook check .` run side by side until cut over; all three
  are clean after every commit.
- The package ships `src/dev_playbook/canonical/`, a copy of
  `standards/build/canonical/` that `test_sources.py` pins byte-identical;
  an edit to a canonical file edits both. `Repo.canonical` and `Repo.name`
  carry the sources and the repository's name, and a test overrides either
  through `Repo.from_files(..., name=, canonical=)`.
- The commit step commits the task's work as one commit on this branch.

## Tasks

- [x] Step 1, family `python`, retired `python-lint`.

<!-- [x] checkpoint -->

- [x] Step 2, family `testing`, retired `testing-lint`.

<!-- [x] checkpoint -->

- [x] Step 3, family `decisions`, retired `decisions-lint`.

<!-- [x] checkpoint -->

- [x] Step 4, family `prose`, retired `prose-lint`.
- [x] Step 5, family `tracking`; `workspace-lint` untouched.

<!-- [x] checkpoint -->

- [x] Step 6, family `distribution`.
- [x] Step 7, family `build`.
- [x] Step 8, family `harness`.
- [x] Step 9, family `standard`.

<!-- [x] checkpoint -->

- [x] Step 9a, fix: the canonical sources and the repo name carried on
      `Repo`, so no check imports `gitrepo` and a consumer repo is compared.
- [x] Step 10, family `doc-type`, retired `harness-files-lint` and
      `standards-lint`.
- [x] Step 11, family `knowledge-organization`, retired `okf-lint`,
      `ref-lint`, and `repo-lint`.

<!-- [x] checkpoint -->

- [x] Step 12, family `shell`.

<!-- [x] checkpoint -->

- [x] Step 12a, rework: ten knowledge-organization items from the Step 11
      audit; `every-member-reached-from-rootmd` restored.

<!-- [x] checkpoint -->

- [x] Step 12a fix: the report's counts, four rule sentences reduced to
      their checks, one trailing-mark fix, dead code removed.
- [x] Step 12b, rework: non-mapping frontmatter and a list-valued `type`
      as findings, setext headings parsed, links wrapping across two line
      breaks found. Items 1 and 3 are reversed by Step 12c.

<!-- [x] checkpoint -->

- [x] Step 12c, rework: the old underline heading form prohibited by a
      rule, detected, and tested; bad frontmatter stops the run again;
      five rule sentences reduced to their checks.

<!-- [x] checkpoint -->

- [x] Step 12d, fix: two things the checkpoint after Step 12c found in
      `standards/knowledge-organization/cross-references.md` beside
      `src/dev_playbook/checks/knowledge_organization.py`. The ruling as
      before: the sentence of a rule and the code of its check say the
      same thing; a sentence is reduced to its check. Headings never
      change. One commit. Read first the sections Writing a check,
      Writing a test, Editing a Standard, and Conduct of
      `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`.
      Two items.
      1. Rule `ATX headings only`, check `atx_headings_only`. The check
         reads `repo.markdown.values()`, every markdown file, a numbered
         Decision Record (`docs/decisions/NNNN-slug.md`) included; the
         Standard's `population` exempts a record, and a record is frozen,
         so a finding in one demands an edit the repo forbids. The loop
         reads `_sources(repo)` instead, as every other check of this
         Standard does, and the docstring says so in one line. Test: add
         to `test_atx_headings_only` that
         `{"docs/decisions/0001-x.md": "# A\n\nText\n---\n"}` yields no
         finding. The sentence stays as it is.
      2. Rule `Workspace path for a stable location`, check
         `workspace_path_for_a_stable_location`. A `~/.claude/` target
         resolves into the repo, starts neither `/` nor a relative path,
         so the check passes every one and never tests "for a file the
         harness loads from there". The body's "or `~/.claude/` for a
         file the harness loads from there" becomes "or `~/.claude/`",
         the cut Step 12c made to `Workspace path for another repo`.
      Then in
      `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`
      the Restated list: a `workspace-path-for-a-stable-location` line is
      added, and the `atx-headings-only` Built line notes the record
      exemption.
      Verify: `grep -c "loads from there"
      standards/knowledge-organization/cross-references.md` prints 0;
      `grep -c "repo.markdown.values" src/dev_playbook/checks/knowledge_organization.py`
      prints 0 (it prints 1 before the task); the test of item 1 passes;
      `uv run playbook check .` reports zero findings; `make check` green;
      `scripts/playbook-lint .` clean.

<!-- [ ] checkpoint -->
