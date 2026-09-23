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
- Since Step 3, `checks/decisions.py` decides the `docs/decisions/` directory
  rule that `scripts/ref-lint` also checks as `UnclassifiedRecordsFile`. Both
  run until Step 11 retires `ref-lint`; nothing moves from `ref-lint` early.
- A deleted rule leaves no mention of its subject behind: the Standard's
  opening paragraph, its `description`, the directory `index.md` intro and
  row, and the directory's row in `standards/index.md` all say what the file
  now holds. The `population` line still changes only where the report says.
- A retired detector's package module goes even where a surviving module
  imports it for one helper: the helper moves to the check module and the
  import is repointed, as Step 4 did for `repo_init.py` and `prose_lint.py`.
  The retired name then appears nowhere outside `working-docs/`.
- Since Step 9a, the package ships `src/dev_playbook/canonical/`, a copy of
  `standards/build/canonical/` that `test_sources.py` pins byte-identical; an
  edit to a canonical file edits both. `Repo.canonical` and `Repo.name` carry
  the sources and the repository's name, and a test overrides either through
  `Repo.from_files(..., name=, canonical=)`.

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

- [x] Step 3, family `decisions`, retires `decisions-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/decisions.md`.
      Verify: `uv run playbook checks --family decisions` lists exactly the
      deterministic trailers under `standards/decisions/`; `git ls-files
      scripts/decisions-lint` prints nothing; the report exists; the Guardrails
      of `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [x] checkpoint -->

- [x] Step 4, family `prose`, retires `prose-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/prose.md`.
      Verify: `uv run playbook checks --family prose` lists exactly the
      deterministic trailers under `standards/prose/`; `git ls-files
      scripts/prose-lint` prints nothing; the report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

- [x] Step 5, family `tracking`, retires nothing; `workspace-lint` is
      untouched. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/tracking.md`.
      Verify: `uv run playbook checks --family tracking` lists exactly the
      deterministic trailers under `standards/tracking/`; `scripts/workspace-lint`
      and `src/dev_playbook/workspace_lint.py` are unchanged in the range; the
      report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [x] checkpoint -->

- [x] Step 6, family `distribution`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/distribution.md`.
      Verify: `uv run playbook checks --family distribution` lists exactly the
      deterministic trailers under `standards/distribution/`; the report
      exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

- [x] Step 7, family `build`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/build.md`.
      Verify: `uv run playbook checks --family build` lists exactly the
      deterministic trailers under `standards/build/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

- [x] Step 8, family `harness`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/harness.md`.
      Verify: `uv run playbook checks --family harness` lists exactly the
      deterministic trailers under `standards/harness/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

- [x] Step 9, family `standard`, retires nothing. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/standard.md`.
      Verify: `uv run playbook checks --family standard` lists exactly the
      deterministic trailers under `standards/standard/`; the report exists;
      the Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [x] checkpoint -->

- [x] Step 9a, fix: the model carries what two build checks lack. Today the
      seven canonical checks in `src/dev_playbook/checks/build.py` read their
      source from `standards/build/canonical/` in the model, so a repo that
      does not track that directory gets no comparison and no finding; and
      `names_the_project_and_package` calls `gitrepo.canonical_repo_name`, the
      one git call in a check. For this task alone, `src/dev_playbook/model.py`
      may be edited. `Repo` gains `canonical`, a mapping of the seven file
      names in `sources.CANONICAL_FILES` to bytes, filled by both constructors
      from a copy of `standards/build/canonical/` shipped inside the package,
      so the wheel carries it; a test pins the shipped copy byte-identical to
      the tree. `Repo` gains `name`, the repository's name, set by `from_git`
      through `gitrepo.canonical_repo_name` and by a `from_files` argument
      defaulting to the root's directory name. The canonical checks compare
      against `repo.canonical`, the name check reads `repo.name`, and no
      check imports `gitrepo`. Verify: `grep -n gitrepo
      src/dev_playbook/checks/build.py` prints nothing; a test in
      `tests/dev_playbook/checks/test_build.py` builds a repo with no
      `standards/build/canonical/` and a `ci.yml` unlike the shipped one and
      gets one finding; `make check`, `scripts/playbook-lint .`, and
      `uv run playbook check .` are clean.

- [x] Step 10, family `doc-type`, retires `harness-files-lint` and
      `standards-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/doc-type.md`.
      Verify: `uv run playbook checks --family doc-type` lists exactly the
      deterministic trailers under `standards/doc-type/`; `git ls-files
      scripts/harness-files-lint scripts/standards-lint` prints nothing; the
      report exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

- [x] Step 11, family `knowledge-organization`, retires `okf-lint`,
      `ref-lint`, and `repo-lint`. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`.
      Verify: `uv run playbook checks --family knowledge-organization` lists
      exactly the deterministic trailers under
      `standards/knowledge-organization/`; `git ls-files scripts/okf-lint
      scripts/ref-lint scripts/repo-lint` prints nothing; `DETECTORS` in
      `src/dev_playbook/playbook_lint.py` holds only `"loop-lint"`; the report
      exists; the Guardrails of
      `working-docs/doc-type-system/detector-rewrite/plan.md` hold.

<!-- [x] checkpoint -->

- [x] Step 12, family `shell`, retires nothing; the two tool-decided rules in
      `src/dev_playbook/checks/shell.py` stay as they are. Report:
      `working-docs/doc-type-system/detector-rewrite/rewrite/shell.md`.
      Verify: `uv run playbook checks --family shell` lists exactly the
      deterministic trailers under `standards/shell/`; the report exists; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->

- [ ] Step 12a, rework: the `knowledge-organization` family to its sentences.
      A rule-by-rule audit of Step 11 found each item below; fix every one,
      in `src/dev_playbook/checks/knowledge_organization.py`, its test file
      `tests/dev_playbook/checks/test_knowledge_organization.py`, and the
      family's Standards under `standards/knowledge-organization/`, and
      nothing the item does not name. For this task alone
      `src/dev_playbook/model.py` and `src/dev_playbook/md.py` may be edited,
      only for items 8, 9, and 10. This is not a family build, so the five
      steps and the report shape of
      `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`
      do not apply; its sections Writing a check, Writing a test, Editing a
      Standard, and Conduct do, read them first. Then read, in this order:
      the Standards under `standards/knowledge-organization/`; the check
      module and its test file; `src/dev_playbook/model.py` and
      `src/dev_playbook/md.py`; the family's triage report
      `working-docs/doc-type-system/detector-rewrite/triage/knowledge-organization.md`,
      whose blockquotes and Escalations are the wording and rulings the items
      cite; and the family's rewrite report
      `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`.
      The retired `okf-lint` and `ref-lint` an item names are read with
      `git show 863746d:scripts/okf-lint` and `git show 863746d:scripts/ref-lint`.
      A test for each behaviour an item changes, one passing and one failing
      member each. Every rule heading stays as it is. The work is one commit.
      1. `every-member-reached-from-rootmd` is restored to
         `standards/knowledge-organization/documentation-sets/working-documentation-sets.md`
         with the triage's blockquote as its body, its check, and its test;
         escalation 6 ruled it built in full, and Step 11 set it aside. The
         one failure it reports is the twelve reports under
         `working-docs/doc-type-system/detector-rewrite/rewrite/`, linked
         only from their `index.md`: fix that by linking each report from its
         family's row in the step table of
         `working-docs/doc-type-system/detector-rewrite/plan.md`, the one
         edit under `working-docs/` this task allows outside the report.
         The report's Set aside becomes `None.` and Built gains the id.
      2. Escalation 4 ruled `~/.claude/` a target form in both
         `workspace-path-for-another-repo` and
         `workspace-path-for-a-stable-location`; the checks accept it, the two
         bodies in `cross-references.md` do not say so. Add it to each body.
         And the checks stop skipping such a target: `reference-resolves` and
         `fragment-anchor-matches-the-slug` resolve `~/.claude/<rest>` to
         `dotfiles/dot-claude/<rest>` where the repo tracks that directory,
         and skip it only where it does not; `stable-named-anchor` tests the
         anchor's form on every `.md` target, in this repo or another, since
         the form needs no file; `relative-path-inside-the-bundle` treats
         `~/.claude/skills/<name>/` as the linking file's own bundle only when
         that file is under `dotfiles/dot-claude/skills/<name>/`, not on a
         name match from anywhere.
      3. `type-registry.md`'s `population` and opening still describe a
         `## Types` table that no file has. Both now name the registry as the
         table under `type names a registered type` in `document-types.md`.
      4. `indexes.md` checks, each to its sentence:
         `introduction-between-h1-and-listing` reports an `index.md` with no
         H1; `one-entry-per-concept-document-and-child-directory` reads only
         the bullets of the listing, the run of bullets before the first H2,
         not a bullet under a later heading, compares a bullet's ending with
         ` — ` and the description, not the whole rest of the line, and finds
         child indexes through the model's classification, not a raw
         `index.md` basename anywhere; `alphabetical-unless-declared-otherwise`
         honours an `Ordering:` line only above the first bullet of any kind.
         `term-definition-avoid-line` in `context-content.md` reads the `##
         Language` section, never an H1 of the same slug, and its test covers
         the no-definition-line and the two-`_Avoid_:`-lines cases; the
         `Ordering:` test asserts the group order is off too.
      5. `one-list-of-items-state-by-section` reads only the bullets directly
         under each `## Planned` and `## Completed`, not those under a `###`
         inside, and every such section, not the first.
         `one-directory-under-working-docs` tests the whole file name against
         the rule, not the text before the first dot.
      6. `okf-version-declared` reports a repo with no root `index.md`, the
         case the old `okf-lint` caught, since a missing index declares
         nothing.
      7. `readmemd-is-typed-readme` reports a `README.md` with no `type` key.
      8. Link scanning, in the model: a `~/workspace/` path inside a link's
         text is read as a bare path, as `ref-lint` read it; and a list item's
         continuation paragraph is measured from the item's content column,
         so its links are not taken for indented code; and a bare path's
         trailing `.`, `,`, `;`, or `:` is not part of the path, so
         `Read ~/workspace/demo/a.md.` resolves.
      9. Helpers duplicated across modules are hoisted to one place, `md.py`
         or `model.py`: the kebab-case pattern in `knowledge_organization.py`
         and `doc_type.py`; the is-this-dev-playbook test in
         `knowledge_organization.py`, `build.py`, and `standard.py`; the
         link-target resolver in `knowledge_organization.py` and
         `doc_type.py`; the workspace-path pattern beside `md.py`'s; and the
         bare-path scan that copies the model's link line mapping.
      10. The module-level `@cache` on `_slugs_on_disk`, which reads another
         repo's headings, is scoped to one run, keyed on the `Repo` or held on
         it, so a long-lived process never reads a stale answer.
      Verify: `make check` green, `scripts/playbook-lint .` and
      `uv run playbook check .` clean; `uv run playbook checks --family
      knowledge-organization` lists every deterministic trailer under
      `standards/knowledge-organization/`, the restored one included; the
      Guardrails of `working-docs/doc-type-system/detector-rewrite/plan.md`
      hold.

<!-- [ ] checkpoint -->

- [ ] Step 12b, rework: the model reads every file the way a reader does and
      never crashes the run on a bad one. Four items, each with its own test
      in `tests/dev_playbook/test_model.py` or the owning check's test file.
      For this task alone `src/dev_playbook/model.py` and
      `src/dev_playbook/md.py` may be edited. Read first the sections Writing
      a check, Writing a test, and Conduct of
      `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`,
      then `src/dev_playbook/model.py`, `src/dev_playbook/md.py`, and the
      two checks named below in `src/dev_playbook/checks/knowledge_organization.py`.
      The parser ruling in
      `working-docs/doc-type-system/detector-rewrite/ROOT.md` keeps the
      hand-rolled scanner; extend it, do not replace it. The work is one
      commit.
      1. Frontmatter that is not a YAML mapping, `---\n- a\n---`, raises
         `ModelError` today and stops every check; it becomes one finding on
         that file from `frontmatter-a-yaml-mapping`, and every other check
         runs, treating the file as one with no frontmatter.
      2. A `type` value that is a list raises `TypeError` in
         `type-names-a-registered-type`; it becomes one finding on that file.
      3. A setext heading, a line of text over a line of `=` or `-`, is a
         heading to the model, with its level, slug, and line number, so
         `readme-holds-an-h1` and `headings-slugify-distinctly` see it.
      4. A link whose text wraps across two or more line breaks is found, as
         one across a single break already is.
      Verify: the four tests pass; `make check` green; both gates clean;
      `uv run playbook check .` still reports zero findings on this repo.

<!-- [ ] checkpoint -->
