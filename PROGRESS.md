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
