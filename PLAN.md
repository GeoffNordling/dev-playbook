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

- Every task is one family, done by the procedure in
  `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`.
  Read that file first; it names what else to read and in what order.
- The specification of a family is its triage report,
  `working-docs/doc-type-system/detector-rewrite/triage/<family>.md`. Its
  Escalations section carries the user's ruling on each item.
- A family's module is the family with hyphens as underscores:
  `doc-type` is `src/dev_playbook/checks/doc_type.py` and
  `tests/dev_playbook/checks/test_doc_type.py`.
- A rule that `scripts/workspace-lint` decides today stays with it and is
  registered `tool_check(id, hook="workspace-lint", module=__name__)`;
  `workspace-lint` itself is not edited.
- A new check that fails this repo today is set aside in the report, not
  fixed in the repo. The repo as it stands is acceptable.
- The check gate is `make check`. The old gate, `scripts/playbook-lint .`, and
  the new one, `uv run playbook check .`, run side by side until cut over.
- The commit step commits the family's work as one commit on this branch.
- A deleted rule leaves no mention of its subject behind: the Standard's
  opening paragraph, its `description`, the directory `index.md` intro and
  row, and the directory's row in `standards/index.md` all say what the file
  now holds. The `population` line still changes only where the report says.

## Tasks

- [x] Step 1, family `python`, retires `python-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/python.md`.
      Verify: `uv run playbook checks --family python` lists exactly the
      deterministic trailers under `standards/python/`; `git ls-files
      scripts/python-lint` prints nothing; the report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [x] checkpoint -->

- [x] Step 2, family `testing`, retires `testing-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/testing.md`.
      Verify: `uv run playbook checks --family testing` lists exactly the
      deterministic trailers under `standards/testing/`; `git ls-files
      scripts/testing-lint` prints nothing; the report exists; the Guardrails
      of `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [x] checkpoint -->

- [ ] Step 3, family `decisions`, retires `decisions-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/decisions.md`.
      Verify: `uv run playbook checks --family decisions` lists exactly the
      deterministic trailers under `standards/decisions/`; `git ls-files
      scripts/decisions-lint` prints nothing; the report exists; the Guardrails
      of `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 4, family `prose`, retires `prose-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/prose.md`.
      Verify: `uv run playbook checks --family prose` lists exactly the
      deterministic trailers under `standards/prose/`; `git ls-files
      scripts/prose-lint` prints nothing; the report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 5, family `tracking`, retires nothing; `workspace-lint` is
      untouched. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/tracking.md`.
      Verify: `uv run playbook checks --family tracking` lists exactly the
      deterministic trailers under `standards/tracking/`; `scripts/workspace-lint`
      and `src/dev_playbook/workspace_lint.py` are unchanged in the range; the
      report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 6, family `distribution`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/distribution.md`.
      Verify: `uv run playbook checks --family distribution` lists exactly the
      deterministic trailers under `standards/distribution/`; the report
      exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 7, family `build`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/build.md`.
      Verify: `uv run playbook checks --family build` lists exactly the
      deterministic trailers under `standards/build/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->

- [ ] Step 8, family `harness`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/harness.md`.
      Verify: `uv run playbook checks --family harness` lists exactly the
      deterministic trailers under `standards/harness/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->

- [ ] Step 9, family `standard`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/standard.md`.
      Verify: `uv run playbook checks --family standard` lists exactly the
      deterministic trailers under `standards/standard/`; the report exists;
      the Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->

- [ ] Step 10, family `doc-type`, retires `harness-files-lint` and
      `standards-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/doc-type.md`.
      Verify: `uv run playbook checks --family doc-type` lists exactly the
      deterministic trailers under `standards/doc-type/`; `git ls-files
      scripts/harness-files-lint scripts/standards-lint` prints nothing; the
      report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 11, family `knowledge-organization`, retires `okf-lint`,
      `ref-lint`, and `repo-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`.
      Verify: `uv run playbook checks --family knowledge-organization` lists
      exactly the deterministic trailers under
      `standards/knowledge-organization/`; `git ls-files scripts/okf-lint
      scripts/ref-lint scripts/repo-lint` prints nothing; `DETECTORS` in
      `src/dev_playbook/playbook_lint.py` holds only `"loop-lint"`; the report
      exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [ ] checkpoint -->

- [ ] Step 12, family `shell`, retires nothing; the two tool-decided rules in
      `src/dev_playbook/checks/shell.py` stay as they are. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/shell.md`.
      Verify: `uv run playbook checks --family shell` lists exactly the
      deterministic trailers under `standards/shell/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->
