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

- [x] Step 12c, rework: what the Step 12b audit found. Two model defects
      and five rule sentences that say more than their checks test. The
      ruling for every item: the sentence of a rule and the code of its
      check say the same thing; where the code does less than the sentence,
      the sentence is reduced to the code; where a model feature cannot be
      made right simply, it is deleted. Headings never change. One commit.
      Read first the sections Writing a check, Writing a test, Editing a
      Standard, and Conduct of
      `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`,
      then `src/dev_playbook/model.py`, `src/dev_playbook/md.py`, and each
      rule named below in its Standard beside its check function. Seven
      items.
      1. Setext headings leave the model. The scanner 12b added in
         `model.py` makes false headings: `Intro.\n\n---\nText\n---\n` gives
         an H2 "--- Text" where the first `---` is a thematic break;
         `- item\ncontinued\n---` and `> quote\ncontinued\n---` give an H2
         "continued"; a table with no outer pipes over `---` becomes a
         heading. A correct scanner needs paragraph tracking the model does
         not have, this repo holds no setext heading, no Standard names the
         heading form, and `md.heading_slugs` reads ATX only for a file
         in another repo, so the two readers already disagreed. The user's
         ruling: the old form is prohibited by a rule, detected, and
         tested; the model reads `#` headings only. Two parts.
         (a) Delete the setext branch from `model.py`, its tests, and the
         two lines of the module docstring that describe it; a heading to
         the model is an ATX heading, `#` to `######`.
         (b) Add one rule to `standards/knowledge-organization/cross-references.md`
         directly after `## Headings slugify distinctly`, heading
         `## ATX headings only`, body: "A heading is a line of one to six
         `#` then a space. Outside a fenced code block and outside the
         frontmatter block, no line made only of three or more `=` or `-`
         sits directly under a line of text." Trailer
         `` `knowledge-organization.atx-headings-only` · deterministic ``.
         Why blockquote: "A `---` under a line of text is a heading to one
         renderer and a divider to another, so the model reads `#`
         headings only and this rule keeps the two forms apart; a divider
         has a blank line above it." Write the check
         `atx_headings_only` in `checks/knowledge_organization.py` reading
         `doc.content` (the lines outside fences) and skipping the
         frontmatter block's lines; a table separator such as
         `| --- | --- |` holds `|` and is not "only `=` or `-`". Test: a
         file with `Text\n---` yields one finding at the underline's line;
         a file with `Text\n\n---` and one with a table yield none. Where
         this repo has a line the new check flags, insert one blank line
         above the underline, the divider the author meant, so the check
         lands clean rather than set aside. The Standard's `description`,
         the directory index row, and the family's report Built list say
         what the file now holds, per the Editing a Standard section.
         Record in `PROGRESS.md` the reversal of 12b item 3 with this
         reason.
      2. Frontmatter that is YAML but not a mapping, `---\n- a\n---` or
         `---\nfoo\n---`, is read by the model as no frontmatter since 12b,
         so `_body` in `src/dev_playbook/checks/doc_type.py` (near line
         529) takes the `---` fence as the body's first line, and on an
         `index.md` or `CLAUDE.md` nothing reports the bad block at all,
         a silent skip. The user's ruling: such a file stops the run fast
         and loud. Revert 12b item 1: the model raises `ModelError` naming
         the file for frontmatter that is YAML but not a mapping, exactly
         as it does for frontmatter that is not YAML; delete the
         read-as-no-frontmatter path, the docstring lines that describe
         it, and its tests; add one test in
         `tests/dev_playbook/test_model.py` that `---\n- a\n---` raises
         `ModelError` naming the path. `frontmatter-a-yaml-mapping` and its
         sentence stay as they are: its check reports a concept document
         with no block, and the mapping half is enforced by the model's
         stop, which its docstring says in one line. 12b item 2, a
         list-valued `type` as a finding, stays. Record in `PROGRESS.md`
         the reversal of 12b item 1 with this reason.
      3. `standards/knowledge-organization/cross-references.md`, rule
         `Root-absolute path in the same repo`. The check passes any
         `~/.claude/` target, `[x](~/.claude/random/notes.md)` included,
         and passes a same-file `[b](#x)`; the sentence limits `~/.claude/`
         to "a file the harness loads from there" and calls every relative
         target a finding. The body becomes: "In a file with a fixed repo
         root, a reference to a file or a directory of the same repo is a
         link whose target starts `/` and is the path from the repo root,
         or starts `~/.claude/`. A relative target other than a same-file
         `#anchor`, and a `~/workspace/<this repo>/` path as a link's
         target, as a link's text, or bare, are findings." Then read
         `Workspace path for another repo` beside its check: where the
         code does not test "for a file the harness loads from there", that
         clause is reduced to "or `~/.claude/`" the same way.
      4. Same file, rule `Reference resolves`. `[x](../../nope.md)` in
         `d/a.md` climbs out of the repo and gets no finding from this
         check, since `workspace-path-for-another-repo` reports it. After
         "a relative target is read from the linking file's directory."
         add: "A relative target that climbs above the checkout root is not
         this rule's finding."
      5. Same file, rule `Stable named anchor`. The check reads a `.md`
         target or a same-file anchor only, so `[x](/dir/#3-foo)` passes.
         The body's opening "The `#anchor` of a reference does not" becomes
         "The `#anchor` of a reference to a `.md` file, or to a heading of
         the same file, does not".
      6. `standards/knowledge-organization/indexes.md`, rule `One entry per
         concept document and child directory`. The check flags a `-`,
         `*`, or `+` bullet at any indent, and not `> - x` in a blockquote
         nor `1. x`. Confirm that against the code, then make the phrase
         "and no other bullet outside a fenced code block" name exactly
         the shapes the code flags, for example "and no other `-`, `*`, or
         `+` bullet outside a fenced code block or a blockquote".
      7. `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`:
         the Restated list gains one line per rule items 2 to 6 changed,
         each naming the rule and the reason in one clause, and the line
         for any rule already listed there from the Step 12a fix is
         updated rather than doubled.
      Verify: `grep -ci setext src/dev_playbook/model.py` prints 0; the
      tests of items 1 and 2 pass; `uv run playbook checks --family
      knowledge-organization` lists 37 ids, `atx-headings-only` among
      them, equal to the deterministic trailers; `uv run playbook check .`
      reports zero findings; `make check` green; `scripts/playbook-lint .`
      clean.

<!-- [x] checkpoint -->

- [ ] Step 12d, fix: three things the checkpoint after Step 12c found in
      `standards/knowledge-organization/cross-references.md` beside
      `src/dev_playbook/checks/knowledge_organization.py`. The ruling as
      before: the sentence of a rule and the code of its check say the
      same thing; a sentence is reduced to its check. Headings never
      change. One commit. Read first the sections Writing a check,
      Writing a test, Editing a Standard, and Conduct of
      `working-docs/doc-type-system/detector-rewrite/prompts/rewrite-family.md`.
      Three items.
      1. Rule `ATX headings only`, check `atx_headings_only`. The check
         reads `repo.markdown.values()`, every markdown file, a numbered
         Decision Record (`docs/decisions/NNNN-slug.md`) included; the
         Standard's `population` exempts a record, and a record is frozen,
         so a finding in one demands an edit the repo forbids. The loop
         reads `_sources(repo)` instead, as every other check of this
         Standard does, and the docstring says so in one line. Test: add
         to `test_atx_headings_only` that
         `{"docs/decisions/0001-x.md": "# A\n\nText\n---\n"}` yields no
         finding. The sentence: the check flags a `---` under any
         non-blank content line, `Text\n---\n---\n` at both underlines,
         so "sits directly under a line of text" becomes "sits directly
         under a line that is not blank".
      2. Rule `Root-absolute path in the same repo`. `[x](../../nope.md)`
         in `d/a.md` climbs above the checkout root and gets no finding
         from this check (`_resolve` returns kind `outside`, not `repo`);
         `workspace-path-for-another-repo` reports it. The body's "A
         relative target other than a same-file `#anchor`," becomes "A
         relative target other than a same-file `#anchor` or one that
         climbs above the checkout root,".
      3. Rule `Workspace path for a stable location`, check
         `workspace_path_for_a_stable_location`. A `~/.claude/` target
         resolves into the repo, starts neither `/` nor a relative path,
         so the check passes every one and never tests "for a file the
         harness loads from there". The body's "or `~/.claude/` for a
         file the harness loads from there" becomes "or `~/.claude/`",
         the cut Step 12c made to `Workspace path for another repo`.
      Then in
      `working-docs/doc-type-system/detector-rewrite/rewrite/knowledge-organization.md`
      the Restated list: the `root-absolute-path-in-the-same-repo` line
      gains the climb clause, a `workspace-path-for-a-stable-location`
      line is added, and the `atx-headings-only` Built line notes the
      record exemption.
      Verify: `grep -c "loads from there"
      standards/knowledge-organization/cross-references.md` prints 0;
      `grep -c "repo.markdown.values" src/dev_playbook/checks/knowledge_organization.py`
      prints 0 (it prints 1 before the task); the test of item 1 passes;
      `uv run playbook check .` reports zero findings; `make check` green;
      `scripts/playbook-lint .` clean.

<!-- [ ] checkpoint -->
