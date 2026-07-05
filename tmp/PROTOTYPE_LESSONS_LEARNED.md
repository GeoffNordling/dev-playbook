# Phase 4 — knowledge capture from the prototype run

This is NOT a plan. It is everything the prototype implementation of Phase 4
learned, written by the last agent to see that full conversation before the
rewind. The reader's job is to turn this into a proper plan (likely a Ralph
loop powered by Opus). Trust these facts over compaction summaries — several
of them exist precisely because a compaction summary was wrong.

The prototype landed as commit `95fd487 "prototype phase 4"` and is being
reverted. It DID reach the goal state (repo-audit 33 → 4 findings, 402/404
tests passing, mypy-strict clean, all hooks green except known-deferred
items), so the destination is proven reachable. What failed was the process:
scope pulled forward across unit boundaries, a `--no-verify` commit, and a
rushed feel throughout. Redo the process, reuse the knowledge.

The file name PLAN.md is deliberate: `md.classify` in lib/md.py special-cases
`PLAN.md` as excluded-transient, so okf-lint ignores it. Any other root-level
.md name breaks okf-lint (index omission + missing frontmatter). Delete this
file when Phase 4 truly completes.

## Ground truth that invalidated the original plan

- **tools/ is FOUR import namespaces, not one.** `tools/lib/` (md, pyast,
  gitrepo), `tools/src/judgments/`, `tools/src/skipcache/`, and
  `tools/transcript_export/` (flat, at tools/ root). Plus `tools/bin/` (11
  scripts) and `tools/tests/` (~22 files). The compaction summary before the
  prototype had silently reduced this to "bin/, lib/, tests/". Re-inventory
  from disk; do not trust summaries.
- **tools/pyproject.toml carries things the root pyproject must inherit:**
  `[project.scripts]` console entries (judgments-run/judgments-lint), a
  pyyaml>=6.0 runtime dep, `[tool.uv.build-backend] module-name` override
  (which becomes UNNECESSARY at root — uv_build's default for project name
  `dev-playbook` is exactly `src/dev_playbook`), pytest `pythonpath` and mypy
  `mypy_path`/`explicit_package_bases` config.
- **repo-audit demands exactly one package `src/dev_playbook/`**
  (check_src_package). So all four namespaces fold in as
  `dev_playbook.{md,pyast,gitrepo}` modules plus `dev_playbook.judgments`,
  `dev_playbook.skipcache`, `dev_playbook.transcript_export` subpackages.
- **`tool.uv.package = False` findings vanish once src/ exists** — that
  repo-audit branch only applies to no-src python repos; with src/ the
  `[build-system] uv_build` pins apply instead.

## Verified mechanics (all of these worked; reuse verbatim)

- Moves via `git mv` → git detected 58 renames; history preserved. Sequence
  used: lib/*→src/dev_playbook/, src/{judgments,skipcache}→src/dev_playbook/,
  transcript_export→src/dev_playbook/, bin/*→scripts/, tests→tests/,
  README→scripts/README.md; delete tools/{index.md,Makefile,pyproject.toml,
  uv.lock}; `rm -rf tools` afterwards (only gitignored caches remain).
- Import rewrite: sed on `^from lib import` → `from dev_playbook import`,
  and `^(from|import) (judgments|skipcache|transcript_export)` →
  `dev_playbook.`-prefixed, across src/ tests/ scripts/. Verify with a grep
  for un-prefixed and double-prefixed names.
- Path shims after the move (scripts/x → parents[1] = repo root):
  - python-lint, okf-lint, ref-check, repo-audit, transcript-export:
    `sys.path.insert(0, …parents[1])` → `…parents[1] / "src"`.
  - judgments-run/judgments-lint: expression `parents[1] / "src"` is
    ALREADY correct post-move (tools/→src becomes root/→src); imports only.
  - sweep and repo-audit: `HOOK_REPO_ROOT = parents[2]` → `parents[1]`.
- Test path constants: `parents[1]/"bin"/x` → `parents[1]/"scripts"/x`;
  `parents[2]` → `parents[1]` (tests moved up one level). Files:
  test_{repo_audit,sweep,okf_lint,python_lint,ref_check,judgments_lint,
  skipcache}.py. TOOLS_DIR/tools_dir variables renamed REPO_ROOT/repo_root.
- Root artifacts generated FROM canonical (guarantees the compare passes):
  `cp standards/canonical/.python-version .python-version`;
  `sed 's/<code-roots>/src tests/' standards/canonical/Makefile.python > Makefile`.
- Root pyproject.toml = canonical pins + carried extras. Extras confirmed
  legal (additions are free): pyyaml dep, console scripts (rewritten to
  `dev_playbook.judgments.runner:run_cli` / `…loader:lint_cli`),
  `[tool.judgments] paths`, pytest `pythonpath = ["src", "tests"]` (tests/
  needed for bare `import transcript_fakes` in two test files), mypy
  `mypy_path = ["src", "tests"]` + `explicit_package_bases = true`, ruff
  `extend-exclude = ["dotfiles/.agents", "dotfiles/.dhub"]` (replaces the
  old per-hook exclude; works under pre-commit because ruff-pre-commit
  passes --force-exclude). dev group ruff floor bumps to >=0.15.20.
- `uv lock` + `uv sync` worked in-sandbox (cache hit; network not needed).
  `dev-playbook==0.1.0` installs editable; uv_build finds src/dev_playbook
  with no module-name override.
- .pre-commit-config.yaml canonical shape that repo-audit accepts in
  self-mode: header comment (free) → `default_install_hook_types:
  [pre-commit, pre-push]` + `repos:` (must be contiguous) → ruff block
  verbatim (rev v0.15.20, ids ruff-check/ruff-format, NO args) → shellcheck
  block → `repo: local` with make-check lines verbatim FIRST, then dogfood
  hooks appended inside the same block (repo-audit, python-lint, ref-check,
  okf-lint, internal-skill-audit, judgments-lint, validate-manifest), all
  entries `scripts/<x>`. The pinned dev-playbook segment is skipped in
  self-mode. This exact file exists in the reverted commit — recover with
  `git show 95fd487:.pre-commit-config.yaml` (same for any other artifact).
- okf-lint requires: scripts/index.md created (`# scripts/ — index` + one
  README bullet, no frontmatter), root index.md bullet tools/→scripts/,
  scripts/README.md frontmatter title/description updated.
- ref-check finds exactly 4 broken links post-move:
  orient-workspace-meta SKILL.md (~/workspace…/tools/README.md),
  standards/judgments/declarations.md ×2 (/tools/src/judgments/*.py),
  workflow/workflow.md (/tools/bin/bootstrap-labels).
- judgments/doc-consistency.yaml reference paths need
  tools/src/judgments/ → src/dev_playbook/judgments/ (judgments-lint
  validates existence).

## Bugs discovered (fix these deliberately this time, not in passing)

1. **repo-audit `<code-roots>`:** included any existing MYPY_ROOTS dir, but
   mypy exits 2 on a dir with zero .py files — and scripts/ holds only
   extensionless scripts. Fix: include a root only if it holds .py files
   (pass python_files into check_makefile). dev-playbook's Makefile
   typecheck line is therefore `uv run mypy src tests`. Empirically
   verified: `mypy <dir-without-py>` → "There are no .py[i] files" exit 2.
2. **test_repo_audit.py `hook_repo_files()`:** `for name in
   CANONICAL.iterdir(): … name.read_text()` — crashes with
   IsADirectoryError once anything drops a dir there. And something DOES:
   ruff walks up, finds standards/canonical/pyproject.toml (the template!),
   and seeds standards/canonical/.ruff_cache/. Fix the fixture
   (`if name.is_file()`) AND expect the canonical-template-as-fake-project
   nuisance to recur with other tools.
3. **PEP 723 floor drift:** scripts declared a 3.11/3.14 mix; nothing
   enforced it. USER RULING (final, do not re-ask): all scripts pin
   `requires-python = ">=3.14"`, and repo-audit gains a check that each
   executable script's PEP 723 floor equals the repo's .python-version
   (rule id `script-python` in the prototype; 2 tests). Note the prototype
   agent itself AUTHORED fresh ">=3.11" blocks by copying neighbors —
   boilerplate gets copied, so check what you copy against the standard.
4. **String-form module refs escape import-rewrite seds:**
   test_skipcache.py had `"import skipcache.seen; …"` inside a subprocess
   -c program string. Audit with bare-name greps (`grep -rn 'skipcache'`
   etc.) and judge every hit; anchored/clever patterns missed this one.

## Landmines still armed (prototype did NOT defuse)

- **shellcheck has never actually run.** Newly wired via the canonical
  config; can't install in-sandbox (no network); skipped at commit time
  (commit touched no .sh). Four tracked shell files await their first-ever
  lint at CI --all-files or a manual `uvx pre-commit run shellcheck
  --all-files` (needs network/user terminal). Unknown finding count.
- **The standard has no adoption-in-progress story.** Any repo mid-migration
  fails repo-audit on every commit until fully conformant — the prototype
  had to commit `--no-verify`. This WILL bite all 7 consumer repos in
  Phase 6. Worth raising as a design question (SKIP env? staged severity?
  documented `--no-verify` migration protocol?) rather than repeating the
  bypass silently.
- **scripts/README.md body still describes the old tools/ layout** (only
  frontmatter was fixed in the prototype). Full rewrite was deferred to U3
  and never happened.
- **CLAUDE.md `## Build` and CONTEXT.md `## Example dialogue` +
  `## Flagged ambiguities` sections: never written** (the 3 doc-shape
  findings). Also ci.yml byte-swap (U2) never happened. These plus staging
  uv.lock are the 4 residual findings at prototype end.
- **Judgments D1/D2 never declared; cache never filled.** The 2 pytest
  failures (judgments-standard-matches-loader,
  run-judgments-skill-matches-tooling) remain, plus the planned new
  declarations (D1: standards/build prose matches canonical artifacts +
  manifest; D2: tooling ⊆ docs) and a /run-judgments session.

## Process lessons (why we're redoing this)

- **Green-bar-at-every-checkpoint pulls work forward.** Lint gates forced
  U3/U4 items (index restructure, judgment YAML paths, README frontmatter)
  into U1. Either plan those into the keystone unit honestly, or decide
  upfront which hooks may stay red at which checkpoints (and say so).
- **The gates caught every catchable mistake.** pytest caught the sed miss
  and the fixture bug; okf-lint/ref-check caught every doc hole; repo-audit
  tracked 33→4 exactly as designed. The redo can lean on them as the Ralph
  loop's fitness function: the loop's done-condition is repo-audit exit 0 +
  full suite green + the judgment cache filled.
- **Planning probes paid off; do them again if anything is uncertain.** The
  two live experiments (mypy on a .py-less dir; the import inventory greps)
  each caught a real bug pre-implementation. Cheap, decisive.
- **Communication:** the human interrupted long silent thinking three times
  across the session. Narrate or act; don't deliberate silently for minutes.
  And when the human sends a note-to-self, "okay" suffices.
- **User rulings already made (do not re-litigate):** scripts stay fat (no
  shim-into-src refactor — keeps the diff scoped; ask before opportunistic
  refactors); 3.14 script floors + repo-audit enforcement (see bug 3);
  keystone-first direction itself was ratified ("Good plan").

## End-state metrics the redo should meet or beat

- repo-audit: 33 findings → 0 (prototype reached 4, all in deferred units).
- Layers inferred: base, python, src, scripts.
- pytest: 404 collected, everything green except judgment-cache tests until
  /run-judgments fills the cache; then fully green.
- mypy strict: clean over src + tests (45 files). ruff check/format: clean.
- All hooks pass a real `pre-commit run --all-files`, and a commit passes
  WITHOUT --no-verify at final state.
- The full prototype diff is recoverable at `95fd487` (reverted but in the
  reflog/history) — consult it for any mechanical detail not captured here.
