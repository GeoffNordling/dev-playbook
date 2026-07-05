# Plan: dev-playbook self-alignment to its own build standard

A Ralph loop works this file top to bottom. Each iteration, a fresh agent with
no memory reads this plan and the progress log, does the first unchecked task,
checks it off, and commits. Everything it needs to act is here — including the
Working notes below, where earlier iterations leave facts you will need. Add to
them whenever you learn something a future iteration would otherwise rediscover.

dev-playbook ships a build standard (standards/build/) with canonical
artifacts (standards/canonical/) and a structural conformance hook
(repo-audit). This plan brings dev-playbook itself into full conformance:
Python consolidates from `tools/` into the standard layout (`src/dev_playbook`
package, `scripts/`, `tests/` at the root), root config files become
canonical, docs gain their required sections, and enforcement is wired up
last.

## Done when

- `scripts/repo-audit` exits 0 against this repo.
- `make check` is green, and a full `uv run pytest` is green with zero
  `--deselect` flags (the judgment cache is filled).
- `tools/` no longer exists: the single package is `src/dev_playbook/`,
  executables live in `scripts/`, tests in `tests/`, and the repo has
  exactly one `pyproject.toml`.
- `.github/workflows/ci.yml` and `.python-version` are byte-identical to
  their canonical artifacts; the Makefile and `.pre-commit-config.yaml`
  carry the canonical blocks; repo-audit is wired into the dogfood hook
  block.
- The final commit passed the full hook suite — repo-audit included — with
  no `--no-verify` and no skips.

## Rules for every iteration

- Do exactly ONE unchecked task, in order. Do not pull later tasks forward;
  if you find an adjacent problem, record it in Working notes instead of
  fixing it — unless it blocks getting YOUR task's gate green.
- Never read anything under `tmp/`. It is archived material for humans,
  off-limits to loop agents.
- Never `git commit --no-verify`. If you cannot get the gate green, stop and
  report a blocker instead.
- The gate is `make check` at the repo root. Two pytest tests are known-red
  until task 5 fills the judgment cache:
  `tests/test_judgments_gate.py::test_judgment_cached[judgments-standard-matches-loader]`
  `tests/test_judgments_gate.py::test_judgment_cached[run-judgments-skill-matches-tooling]`
  The Makefile `test` target carries `--deselect` flags for exactly those
  two. Keep the deselects intact until task 5 removes them.
- Do not add repo-audit or shellcheck to `.pre-commit-config.yaml` before
  task 6. Enforcement is wired only after the repo conforms — that ordering
  is what makes every intermediate commit legal without bypasses.
- repo-audit is the conformance meter, not the gate. Run it any time
  (`tools/bin/repo-audit` before task 1, `scripts/repo-audit` after) to see
  what remains. It is EXPECTED to report findings until task 6 completes.
- Any executable script you create or edit pins `requires-python = ">=3.14"`
  in its PEP 723 block (must equal the repo's `.python-version`).
- Autonomy: task cards state the goal and hard-won facts; the route is
  yours. Investigate before changing, fail loud on surprises, and record
  durable discoveries in Working notes for later iterations.

## Working notes

- Hook envs for task 6 are already installed and verified working:
  ruff-pre-commit v0.15.20 (ruff-check, ruff-format) and shellcheck-py
  v0.11.0.1.
- shellcheck pre-scout (task 6): exactly 3 findings across the 4 tracked
  .sh files — SC2148 in dotfiles/.bashrc.d/aliases.sh and
  dotfiles/.bashrc.d/worktree.sh (sourced files, no shebang: add a
  `# shellcheck shell=bash` directive line), SC2207 in worktree.sh:32
  (unquoted compgen split in COMPREPLY). sync-dotfiles.sh and
  standards/agentic-box/templates/greenfield-cli/box/gate.sh are clean.
- Task 1 landed: `tools/` is gone. Package is `src/dev_playbook/` (lib files
  flattened to the package root: md/pyast/gitrepo; judgments/, skipcache/,
  transcript_export/ as subpackages). 11 executables + README.md + index.md
  in `scripts/`; 26 files in `tests/`. One root `pyproject.toml` (project
  `dev-playbook`, package `dev_playbook`), root `Makefile`, root `uv.lock`.
  Scripts insert `parents[1] / "src"` on sys.path; sweep/repo-audit use
  `HOOK_REPO_ROOT = parents[1]`. `uv sync` builds the editable install.
- Post-move `scripts/repo-audit` = 14 findings; 12 map cleanly to later
  tasks — ci.yml bytes + .python-version (task 2); CLAUDE.md `## Build` +
  CONTEXT.md `## Example dialogue`/`## Flagged ambiguities` (task 4);
  Makefile deselect deviation (task 5); pre-commit canonical blocks x4 +
  self-audit "repo-audit missing from dogfood" (task 6). The `uv.lock`
  required-file finding is only because the new lockfile is untracked at
  audit time; it clears once committed.
- SURPRISE not in task 1's predicted list: `scripts/python-lint` and
  `scripts/ref-check` open with `#!/usr/bin/env python3` (both are
  pure-stdlib with no PEP 723 deps), so check_scripts' `script-shebang`
  rule flags them now that they live in `scripts/`. TASK 6 must resolve:
  either convert both to `#!/usr/bin/env -S uv run --script` + an empty
  PEP 723 block (they run dependency-free, so this is low-risk — note
  test_ref_check invokes ref-check via `python3` explicitly, which still
  works), or carve out a std-lib-script exception in the standard/audit.
  Do NOT change their shebangs before task 6.

## Tasks

- [x] 1. The move: consolidate `tools/` into the standard layout
- [ ] 2. Canonical ci.yml and .python-version
- [ ] 3. Rewrite scripts/README.md
- [ ] 4. CLAUDE.md `## Build`; CONTEXT.md missing sections
- [ ] 5. Judgments: declare two new judgments, fill the cache, full pytest green
- [ ] 6. Canonical .gitignore + .pre-commit-config.yaml; wire enforcement; repo-audit exit 0

---

### Task 1 — The move: consolidate `tools/` into the standard layout

**Goal.** `tools/` ceases to exist. Python lives at the root per the build
standard: one package `src/dev_playbook/`, executables in `scripts/`, tests
in `tests/`, one `pyproject.toml` at the root. Gate green at the end.

**Layout mapping** (use `git mv` so history is preserved — expect ~58
renames):

- `tools/lib/{md,pyast,gitrepo}.py` → `src/dev_playbook/` (plus `__init__.py`)
- `tools/src/judgments/` → `src/dev_playbook/judgments/`
- `tools/src/skipcache/` → `src/dev_playbook/skipcache/`
- `tools/transcript_export/` → `src/dev_playbook/transcript_export/`
- `tools/bin/*` (11 scripts) → `scripts/`
- `tools/tests/` → `tests/`
- `tools/README.md` → `scripts/README.md`
- Delete `tools/index.md`, `tools/Makefile`, `tools/pyproject.toml`,
  `tools/uv.lock`; remove the emptied `tools/` (only gitignored caches
  should remain in it).

**Import rewrites** across `src/`, `scripts/`, `tests/`:

- `from lib import X` → `from dev_playbook import X` (same for `from lib.X …`)
- bare `judgments`, `skipcache`, `transcript_export` imports →
  `dev_playbook.`-prefixed.
- Seds miss string-form refs: test_skipcache.py holds
  `"import skipcache.seen; …"` inside a subprocess program string, and there
  may be others like it. After rewriting, audit with bare-name greps for each
  of `lib`, `judgments`, `skipcache`, `transcript_export` over the three
  trees and judge every hit individually.

**Path shims** (`sys.path.insert` lines in scripts): after the move a
script's `parents[1]` is the repo root. Known adjustments — python-lint,
okf-lint, ref-check, repo-audit, transcript-export insert
`parents[1] / "src"`; judgments-run and judgments-lint already compute an
expression that lands on `parents[1] / "src"` post-move (imports only);
sweep and repo-audit change `HOOK_REPO_ROOT` from `parents[2]` to
`parents[1]`. Audit all 11 scripts (bootstrap-labels, griffe-outline,
internal-skill-audit included) rather than trusting this list blindly.

**Test path constants**: tests that locate scripts or the repo root move up
one level — `parents[1] / "bin" / x` → `parents[1] / "scripts" / x`,
`parents[2]` → `parents[1]`. Known files: test_repo_audit, test_sweep,
test_okf_lint, test_python_lint, test_ref_check, test_judgments_lint,
test_skipcache. Rename `TOOLS_DIR`/`tools_dir` variables to
`REPO_ROOT`/`repo_root`.

**Root pyproject.toml**: replace the current stub with the canonical
template (`standards/canonical/pyproject.toml`; project name `dev-playbook`,
package `dev_playbook`) — pinned settings must match the canonical file
exactly; additions are free. Carry these extras from `tools/pyproject.toml`:

- dependency `pyyaml>=6.0`
- `[project.scripts]`: `judgments-run = "dev_playbook.judgments.runner:run_cli"`,
  `judgments-lint = "dev_playbook.judgments.loader:lint_cli"`
- `[tool.judgments]` paths (already in the root stub — keep)
- pytest: `pythonpath = ["src", "tests"]` (`tests` is needed — two test
  files do a bare `import transcript_fakes`)
- mypy extras: `mypy_path = ["src", "tests"]`, `explicit_package_bases = true`
- ruff extra: `extend-exclude = ["dotfiles/.agents", "dotfiles/.dhub"]`
  (ruff-pre-commit passes `--force-exclude`, so this works under hooks; it
  replaces the per-hook excludes when task 6 swaps the config)
- dev group: ruff floor is the canonical `>=0.15.20`

Do NOT carry `[tool.uv.build-backend] module-name` — uv_build's default for
project name `dev-playbook` is exactly `src/dev_playbook`.

Then `uv lock` and `uv sync` at the root. Commit `uv.lock`.

**Root Makefile**: replace the transitional content with the canonical
Python form (`standards/canonical/Makefile.python`, `<code-roots>` =
`src tests` — `scripts/` holds no `.py` files and mypy exits 2 on a
directory without any) with ONE deviation: the `test` target keeps the two
`--deselect` flags from the Rules section. Task 5 removes them.

**.pre-commit-config.yaml**: update hook entries `tools/bin/X` →
`scripts/X` only. Do not restructure — the canonical swap is task 6.

**Docs the commit hooks force** (okf-lint and ref-check run at commit):

- new `scripts/index.md` (index style: heading + one bullet per entry; no
  frontmatter on index files)
- root `index.md`: the `tools/` bullet becomes `scripts/`
- `scripts/README.md`: fix frontmatter title/description to the new reality
  (honest minimum — the full body rewrite is task 3)
- ref-check breaks at exactly 4 known spots:
  `dotfiles/dot-claude/skills/orient-workspace-meta/SKILL.md` (link to
  tools/README.md), `standards/judgments/declarations.md` ×2
  (`/tools/src/judgments/*.py`), `workflow/workflow.md`
  (`/tools/bin/bootstrap-labels`)
- `judgments/doc-consistency.yaml`: reference paths
  `tools/src/judgments/…` → `src/dev_playbook/judgments/…` (judgments-lint
  validates the files exist)

**Done when:** `make check` green (with the two deselects); `tools/` gone;
the commit lands without bypasses. Run `scripts/repo-audit` and record the
remaining findings in Working notes — expect roughly: ci.yml bytes,
missing .python-version, Makefile deviation (the deselects), pre-commit
canonical blocks, and the doc-shape findings. If the list surprises you,
say so in Working notes.

### Task 2 — Canonical ci.yml and .python-version

**Goal.** Two byte-identical canonical artifacts land at the root.

- `.github/workflows/ci.yml` ← `standards/canonical/ci.yml`, byte-for-byte.
  This replaces the old CI workflow entirely; the canonical job runs the
  hook suite with `SKIP: ref-check` and never runs tests (by design — see
  standards/build/).
- `.python-version` ← `standards/canonical/.python-version`, byte-for-byte.

**Done when:** repo-audit no longer reports either file; `make check` green.

### Task 3 — Rewrite scripts/README.md

**Goal.** The README body still describes the old `tools/` era (bin/, lib/,
a co-located pyproject). Rewrite it to describe what `scripts/` now is:
the executable surface — published hook entry points plus local dev
scripts — with library code living in `src/dev_playbook/`. Follow the docs
standards in standards/docs/ (voice, OKF frontmatter; the frontmatter was
minimally fixed in task 1 — refine it if the rewrite changes the story).

**Done when:** okf-lint green; no stale `tools/`-era paths remain in the
file (grep it); prose matches the actual directory contents.

### Task 4 — CLAUDE.md `## Build`; CONTEXT.md missing sections

**Goal.** The two repo docs gain the sections the doc-shape standard
requires (see standards/build/ for what each section is for).

- `CLAUDE.md`: add a `## Build` section — how to work on this repo's code:
  make targets, uv basics, where code/tests live, how to run a single test.
  Write it for an agent landing in the repo cold. Keep the existing content
  intact.
- `CONTEXT.md`: the required shape is four sections — `## Language`,
  `## Relationships`, `## Example dialogue`, `## Flagged ambiguities`.
  Check which exist; write the missing ones from first principles for THIS
  repo (standards/docs/ defines the section semantics).

**Done when:** repo-audit reports zero doc-shape findings; `make check`
green.

### Task 5 — Judgments: declare two new judgments, fill the cache, full pytest green

**Goal.** The judgment layer catches drift the deterministic checks cannot.
Declare two new judgments, evaluate everything, and drop the pytest
deselects.

The two judgments to declare:

- **Docs promise exactly what ships**: the standards/build/ prose is
  consistent with the canonical artifacts in standards/canonical/ AND the
  published hook manifest (.pre-commit-hooks.yaml).
- **The tool enforces only what the docs state**: repo-audit's checks are
  a subset of the documented standard in standards/build/.

Declarations live in `judgments/*.yaml` (see `[tool.judgments]` in
pyproject.toml); follow the existing `doc-consistency.yaml` shape —
judgments-lint validates them. Choose clear ids in that file's style.

Then:

1. Invoke the `/run-judgments` skill to evaluate and fill the cache. That
   covers the two long-pending misses (`judgments-standard-matches-loader`,
   `run-judgments-skill-matches-tooling`) plus the new declarations.
2. Remove the two `--deselect` flags from the Makefile `test` target. The
   Makefile should now byte-match the canonical form.

**Done when:** full `uv run pytest` green with zero deselects; `make check`
green; repo-audit no longer reports a Makefile finding.

### Task 6 — Canonical .gitignore + .pre-commit-config.yaml; wire enforcement; repo-audit exit 0

**Goal.** The repo's enforcement config becomes canonical, repo-audit joins
the commit gate, and the audit exits 0. This is last on purpose: only a
conforming repo can afford to enforce conformance on itself.

- `.gitignore`: every canonical pattern present (patterns-only compare —
  existing extras stay). Likely already true; verify via repo-audit.
- `.pre-commit-config.yaml`: swap to the canonical shape —
  `default_install_hook_types: [pre-commit, pre-push]`; ruff-pre-commit at
  the canonical rev with ids `ruff-check`/`ruff-format` (no args, no
  excludes — pyproject's extend-exclude covers it); the shellcheck block;
  one `repo: local` block with the canonical make-check lines verbatim
  FIRST, then the dogfood hooks (repo-audit, python-lint, ref-check,
  okf-lint, internal-skill-audit, judgments-lint, validate-manifest), all
  entries `scripts/X`. dev-playbook is the hook repo itself, so the pinned
  dev-playbook block from the canonical template is replaced by the dogfood
  local block (repo-audit's self-mode expects exactly this).
- shellcheck runs for the FIRST TIME EVER on the repo's tracked shell
  files. Findings are in scope — fix them. The shellcheck and ruff hook
  environments are already installed (see Working notes).
- Run `scripts/repo-audit`: fix any stragglers until it exits 0.

**Done when:** repo-audit exits 0; `make check` green; the commit passes
the full hook suite including repo-audit — no bypasses, no skips.
