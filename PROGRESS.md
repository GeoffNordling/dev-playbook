# Progress log

The running memory of this Ralph loop. Each iteration appends one line to the
log — what it did and what is next — newest at the bottom. A fresh agent reads
this before starting, to see what earlier iterations did.

Two writers, two audiences. Iterations write judgment calls for the checkpoint
reviewer to read at the next checkpoint. The reviewer writes decisions for the
user to read at PR time.

## Recording a judgment call

Where the plan and its sources do not settle a point, do not stop and do not
decide it silently. Take the smallest step that keeps the check gate green, then
add one indented line under your own entry in the log, in this shape:

    - judgment: <what was unsettled> → <what you did>, because <why>

One line, every time. The entry is a pointer, not the evidence: whoever reviews
reads the diff and the artifact anyway.

Write one even when you are fairly sure. The cost of a recorded call is a line;
the cost of a silent wrong turn is every task built on top of it. A reviewer
rules on each call at the next checkpoint and writes the ruling into the plan —
accepted calls become Working notes, reverted ones become a fix task.

## Decisions

Written by the checkpoint reviewer, never by an iteration. One line for each
change that moved the plan away from the shape the user approved at setup, and
for anything the reviewer chose not to do that the user would expect. The user
reads this at PR time and nowhere earlier, so it is the whole account of how
the run drifted from what was agreed.

    - <checkpoint>: <what changed in the plan> — <what made it change>

<!-- the reviewer appends below this line -->

- Checkpoint after Step 9: Step 9a added before Step 10, the model gaining the canonical sources and the repository's name, with leave to edit `model.py` for it — Step 7 built the seven canonical checks to compare nothing in a repo without `standards/build/canonical/`, which every consumer is, and put a git call in one check; both leave the approved shape, model-only checks that work wherever the package runs, unless the model carries the two inputs before Step 11 retires `repo-lint`.

## Log

<!-- iterations append one line each below this line -->

- Step 1, python: `checks/python.py` with two functions and two ruff hook registrations, `test_python.py`, `style.md` edited to the triage, `python-lint` retired, report `rewrite/python.md` written; next is Step 2, testing, after the checkpoint.
    - judgment: the docstring rule's old Why was not addressed by the triage → kept it after the old sentence in the new Why, because it explains the `test_` exception that the old sentence names.
    - judgment: the triage drops the future-import exception but gives no blockquote → cut the `unless ...` clause and kept the rest of the sentence as written, because that is the smallest edit that matches the ruling.
    - judgment: the hook names for the two ruff rules → `ruff-check` and `ruff-format`, the hook ids in `.pre-commit-config.yaml`, because the triage names only the tool.
    - judgment: `docs/decisions/0011` names `python-lint` in its Consequences → dropped the name from its list, because the prompt says to remove every mention outside `working-docs/`; an Accepted record now has a changed body.
    - judgment: `pyast.py` stays, since `testing-lint` and `repo-lint` import it → rewrote its module docstring without the retired name.
- Step 2, testing: `checks/testing.py` with two functions, `test_testing.py`, `conventions.md` edited to the triage with the fixture rule deleted, `testing-lint` and `testing_lint.py` retired, report `rewrite/testing.md` written; next is Step 3, decisions, after the checkpoint.
    - judgment: the function names → `carries_test_prefix` and `mirrors_source_tree`, not the slugs, because a module-level `test_...` function in `checks/testing.py` would break the new prefix rule itself and pytest would try to collect it.
    - judgment: the prefix rule reads `.py` files only → an extensionless Python script is outside it, because the blockquote says "Every `.py` file".
    - judgment: the conventions.md intro still says "A rule about where a fixture or a fake lives binds the suite" and the population still names `conftest.py` → left both, because the prompt changes the population only where the report says and names only the description and index row.
    - judgment: the fixture deletion leaves the directory's intro in `standards/testing/index.md` and its row in `standards/index.md` naming "the conftest hierarchy" → edited both to match the new description, because they describe what the directory now holds.
    - judgment: `docs/decisions/0021` says "testing-lint flags every scoped mirror" as history → reworded to "the test-mirror check", because the Guardrail wants no mention outside `working-docs/`; an Accepted record has a changed body again.
- Step 3, decisions: `checks/decisions.py` with six functions (two ported, four new), `test_decisions.py`, the six bodies of `records.md` replaced by the triage blockquotes, `decisions-lint` and `decisions_lint.py` retired, report `rewrite/decisions.md` written; next is Step 4, prose, after the checkpoint.
    - judgment: the triage says the new directory check "replaces" `UnclassifiedRecordsFile` in `scripts/ref-lint` → left `ref-lint` untouched, because `ref-lint` is not in this step's retirements and retires in Step 11.
    - judgment: the numbering and status checks read records at any depth under `docs/decisions/`, as the old checks did → kept that, because the triage says "check unchanged"; the supersession target is looked up at the top level only, as its check text says `docs/decisions/NNNN-*.md`.
    - judgment: the directory rule's antecedent "has a record" → a top-level `<digits>-<slug>.md` file, because the population names numbered files directly under `docs/decisions/`.
    - judgment: the H1 half is not checked when `title` is absent or not a string → skipped it there, because the missing key is already this rule's finding and an empty `title` is okf-lint's, one fault one finding as the triage asks.
    - judgment: `doc-types/standard/residual-ledger.md` says "decisions-lint reports it" → reworded to "the numbering check reports it", because the Guardrail wants no mention outside `working-docs/`.
- Step 4, prose: `checks/prose.py` with five functions (four ported, one new rule for the vocabulary file), `test_prose.py`, `conventions.md` edited to the triage with the new rule after `No word the repo bans`, `prose-lint` and `prose_lint.py` retired, report `rewrite/prose.md` written; next is Step 5, tracking.
    - judgment: `repo_init.py` imports `prose_lint` for the banned word, so the prompt would keep the module → repointed `repo_init` at `checks.prose.word_pattern(WORKSPACE_WORD)` and deleted `prose_lint.py`, because keeping the whole detector module contradicts the Guardrail that the retired name appears nowhere outside `working-docs/`; the repo-name test moved to `test_repo_init.py`.
    - judgment: the triage says the Standard names the banned word but the restated body does not → named it in a new Why block under `No banned word`, and a test reads that section through a new `sources.BANNED_WORD`, because the body must stay the blockquote word for word.
    - judgment: the triage drops only the `md.classify` "excluded" skip → every check keeps the population's exceptions (`type: Mirror`, `.prose-lint-exempt` paths) and the old structural skip of the two declaration files, because the population still names them and the old detector skipped both files.
    - judgment: `.prose-lint-exempt` listed the two retired files → replaced them with `src/dev_playbook/checks/prose.py`, which holds the word as a constant; the new test builds the word from the constant and needs no entry.
    - judgment: "directories that exist in the repo" over a model of tracked files → a directory exists when a tracked file sits under it; an empty vocabulary file passes as a mapping with no entries, as the old `vocabulary` accepted it.
    - judgment: a malformed vocabulary file or entry → the well-formed rule reports it and `no-word-the-repo-bans` bans only the well-formed entries, one fault one finding.
    - judgment: `tests/test_set_deslop_coverage.py` failed on the new heading → added `the-vocabulary-file-is-well-formed` to its deterministic exempt set, because no auditor reads a deterministic rule.
    - judgment: the retired name also sits inside the file names `.prose-lint-exempt` and `.prose-lint-vocabulary` → left them, because the Standard and the triage name both files; only the detector's name was removed.
- Step 5, tracking: `checks/tracking.py` with one function (`one_list_item_per_entry`, new) and fourteen `workspace-lint` registrations, `test_tracking.py`, four Standards edited to the triage with `outcome-and-decomposition-rationale` and `ticket-under-a-map` deleted, nothing retired, report `rewrite/tracking.md` written; next is Step 6, distribution, after the checkpoint.
    - judgment: the triage says the "carries" to "has" change applies to the five species definitions but gives no blockquote → changed only that verb in each definition line, and left "carries" in the stochastic rules and the intro, because the triage names only the species definitions beside its rows.
    - judgment: two links in `working-docs/software-factory/` pointed at the deleted `#outcome-and-decomposition-rationale` → repointed both at `#no-child-list`, because it is the surviving rule on an epic's body, which both sentences describe; their prose still says the epic body carries the outcome and rationale, which no rule now requires.
    - judgment: the population "a repo's CANDIDATES.md" → the check reads the root `CANDIDATES.md` only, and a list item is a line opening with `-`, `*`, `+`, or `N.`/`N)` outside a fence, because the Standard puts the file at the root and the model's content lines already skip fences.
- Step 6, distribution: `checks/distribution.py` with one function (`dogfoods_its_manifest`, ported to read both YAML files through the model) and one `validate-manifest` registration, `test_distribution.py`, `channel.md` edited to the triage with `one-published-hook-id` deleted, nothing retired, report `rewrite/distribution.md` written; next is Step 7, build.
    - judgment: the triage says a test asserting one published hook "goes in with" the rewrite's change of the manifest entry → did not add it, because `.pre-commit-hooks.yaml` publishes two ids (`playbook-lint`, `playbook-check`) until the cutover, so the test would fail today.
    - judgment: the hook name for `the-manifest-validates` → `validate-manifest`, the step name `playbook_lint.VALIDATE_MANIFEST` runs, because the triage names only "pre-commit's manifest validator".
    - judgment: a manifest or config that is not YAML → one file-level finding on that file under the dogfood rule, not a crash, because the model does not parse YAML and a traceback would stop every other check; malformed shapes yield no ids.
    - judgment: the deleted rule's subject in the map → the description, the directory intro and row, and the `standards/index.md` row now say "a valid manifest and a publisher's local block"; the opening paragraph was left, because it describes the hook repository, not the one-id rule.
- Step 7, build: `checks/build.py` with eighteen functions (sixteen ported from `repo-lint`, `one-version-set` restated, the entry-point check new), `test_build.py`, `canonical.md` edited to the triage with `artifactsmk-lists-every-artifact-and-its-file-rule` and `every-canonical-file-has-a-rule-and-every-rule-a-file` deleted, `sources.CANONICAL_FILES` pinned by a new test, nothing retired, report `rewrite/build.md` written; next is Step 8, harness.
    - judgment: the canonical source a copy is compared against is not in a consumer's model, and the installed `playbook-check` package does not ship `standards/build/canonical/` → the seven canonical checks read the source from the model and compare nothing where the repo does not track that directory, because the prompt allows only the model as input; consumers keep these compares through `repo-lint` only, and the canonical files must reach the package before Step 11 retires it.
    - judgment: the triage splits `one-version-set` into "two rules" but the heading may not change and it lists no new rule → both blockquote paragraphs went under the one heading and one function decides both halves, over the canonical source files only, because the ruff half names the canonical files and the heading is about the canonical pins.
    - judgment: the model does not carry the repository's name → `names_the_project_and_package` calls `gitrepo.canonical_repo_name(repo.root)`, the one git call in a check, because `repo.root` is the worktree directory and would misname this repo; its test builds a real `git init` directory named `My-Repo`.
    - judgment: the import package for `one-package-under-src`, the `known-first-party` pin, and the entry-point check → `project.name` with hyphens as underscores, not the repository's name, because that needs no git and a wrong `project.name` is the name-mapping rule's one finding.
    - judgment: "that module defines `main`" → a top-level `def`, assignment, or import binding the name `main`, because a re-export such as `from x import main` satisfies the console-script loader.
    - judgment: `test_check_cli.py::test_clean_repo_exits_0` ran the real registry over a repo holding only `README.md`, which `files-every-repo-carries` now flags → gave it a fake registry with one check that finds nothing, because the test is about the exit code, not the roster; this edits a file outside the prompt's list.
    - judgment: `repo-lint` still emits the deleted `every-canonical-file-has-a-rule-and-every-rule-a-file` id → left `repo-lint` untouched, because it retires in Step 11, as Step 3 left `ref-lint`.
    - judgment: `tests_present` as the function name is collected by pytest when the test file imports it → named it `has_tests`.
- Step 8, harness: `checks/harness.py` with six functions (two ported from `harness-files-lint`, three gaining a check, `read_the_standards_first` new), `test_harness.py`, `claude-content.md` and `files.md` edited to the triage with the new rule after `Two required rules`, nothing retired, report `rewrite/harness.md` written; next is Step 9, standard.
    - judgment: the triage labels the new rule "`### Read the standards` first", whose slug would open on a hyphen → heading `Read the standards first`, id `harness.read-the-standards-first`, because the meta-test needs the heading slug to equal the id's slug.
    - judgment: the Why at `claude-content.md:22` still says `### Read the standards` "must be the first heading in the file", which the triage calls wrong since `# Global` comes first → left it, because the ruling accepted the new rule over the alternative of correcting the Why, and the prompt restates only rule bodies.
    - judgment: the `statusline.sh` row's Class, Role, and Content standard are not given by the triage → `code`, "run as code to draw the status line", "none yet", after the `hooks/` and workflows rows.
    - judgment: "under `.claude/`" → the repo-root `.claude/` and `dotfiles/dot-claude/` only, not a nested `<dir>/.claude/`, and no skip for dot-directories or `synced/` under a skills root as `harness-files-lint` had, because the blockquotes name the two roots and no exception.
    - judgment: a skill directory without `SKILL.md` is reported on the directory path, line None, since the model has no file to anchor it; every other stray entry on its own path.
    - judgment: the `claude-content.md` description and index row said "the two sections and required rules" → now "the two sections, the required rules, and the first rule", because a rule arrived.
- Step 9, standard: `checks/standard.py` with five functions (four ported from `standards-lint`, the governing-sentence check new), `test_standard.py`, `sources.STANDARD_DIRECTORIES` pinned by a new test, `tree.md` and `detectors.md` edited to the triage with the three escalated rules deleted, nothing retired, report `rewrite/standard.md` written; next is Step 10, doc-type, after the checkpoint.
    - judgment: "in dev-playbook" and "a repo other than dev-playbook" → a repo is dev-playbook where it tracks `standards/build/canonical/.pre-commit-config.yaml`, the probe `standards-lint` used, because the model has no repo name and Step 7 keys on the same directory.
    - judgment: a repo with directories under `standards/` but no `standards/index.md` → one file-level finding on the catalog path; a repo with no such directory gets none, because `standards-lint` failed the first and passed the second.
    - judgment: the deleted git-root rule's only link, in `guides/consuming.md` step 2, sat in a sentence wholly about that rule → dropped the sentence, and dropped the parenthetical link to the hosting rule in step 3, because no surviving rule states either clause; the guide is outside the prompt's edit list except for these links.
    - judgment: the condition heading `A first-party detector` now holds only `Offered by the canonical template`, whose restated body no longer says "first-party" → kept the condition, because the prompt removes a condition only when a deletion empties it.
    - judgment: `standards-lint` still emits the deleted `standard.every-detector-is-reachable-and-listed` → left it, because it retires in Step 10, as Step 7 left `repo-lint`.
    - judgment: the directory index's intro in `standards/standard/index.md` still says "the detectors, and the boundaries", and the boundary rules left in phase 2 → left it, because this step deleted no boundary rule.
- Step 9a, fix: `Repo` gains `name` (`from_git` through `gitrepo.canonical_repo_name`, `from_files` defaulting to the root's directory name) and `canonical` (the seven files from `src/dev_playbook/canonical/`, a shipped copy the built wheel carries and `test_sources.py` pins byte-identical to the tree); the seven canonical checks compare against `repo.canonical`, the name check reads `repo.name`, and `checks/build.py` no longer imports `gitrepo`; next is Step 10, doc-type.
    - judgment: tests need their own sources and names → `from_files` takes optional `name=` and `canonical=` overrides, defaulting to the root's name and the shipped copy, because the fake sources in `test_build.py` keep each test small and independent of the real files.
    - judgment: the pre-commit block check skipped the dev-playbook `rev` block in every repo, harmless while only dev-playbook had a source → now skips it only where the repo tracks `standards/build/canonical/`, because the rule exempts that repo alone and consumers are now compared.
    - judgment: `one-version-set` reads the carried sources in every repo and still reports on `standards/build/canonical/` paths → kept it running everywhere, because the shipped copy is pinned to the tree, so a consumer can never get a finding from it.
    - judgment: the shipped `src/dev_playbook/canonical/pyproject.toml` tripped the root-only rule in both `checks/build.py` and `scripts/repo-lint` → exempted the shipped directory beside the canonical one in both (new `sources.SHIPPED_CANONICAL_DIR`), because it is quoted material; this edits `repo-lint`, which retires in Step 11.
