# Phase 4 — ALTERNATIVE plan: per-namespace moves (Plan B)

The fallback to PLAN.md (Plan A). Same destination — dev-playbook fully
conformant to its own build standard — but the big consolidation is split
into per-namespace steps, each leaving the repo green. Use this only if
Plan A's single move iteration proves unmanageable: every intermediate
state here is NOVEL (never executed by the prototype), so what this plan
buys in smaller commits it pays for in unproven transitional
configurations.

> A note on "namespace": `tools/` holds four separately-importable Python
> roots — `tools/lib/` (`from lib import md`), `tools/src/judgments/` and
> `tools/src/skipcache/` (`import judgments`, `import skipcache`), and
> `tools/transcript_export/`. Each task below relocates one of them and
> rewrites only its imports, so the suite stays green between tasks.

## Done when

Identical to Plan A's `## Done when` (this plan reaches the same
destination): repo-audit exit 0; `make check` and full pytest green with
zero deselects; `tools/` gone with one root pyproject and the single
`src/dev_playbook/` package; canonical ci.yml/.python-version bytes and
canonical Makefile/pre-commit blocks; final commit passes the full hook
suite with repo-audit wired, no bypasses.

## Rules for every iteration

Identical to Plan A's rules (one task per iteration; never read `tmp/`;
never `--no-verify`; gate is `make check` with the two judgment-cache
`--deselect`s intact until the judgments task; no repo-audit/shellcheck in
the commit config until the final task; new/edited scripts pin
`requires-python = ">=3.14"`; prototype reference `git show 95fd487:<path>`,
this plan wins conflicts; record durable discoveries in Working notes).

One addition: **transitional constructs are marked ⏳ and each names the
task that deletes it.** If you finish a task and a ⏳ you were supposed to
remove still exists, that is a finding, not a style choice.

## Tasks

- [ ] 1. Scaffold: root pyproject + empty package + lockfile
- [ ] 2. Move `lib/` → `src/dev_playbook/`
- [ ] 3. Move `judgments/` + `skipcache/`; console scripts to root
- [ ] 4. Move `transcript_export/`
- [ ] 5. Move `bin/` → `scripts/`
- [ ] 6. Move `tests/` to root; pytest/mypy config migrates
- [ ] 7. Retire `tools/`; Makefile canonical
- [ ] 8. Canonical ci.yml and .python-version
- [ ] 9. Rewrite scripts/README.md; CLAUDE.md `## Build`; CONTEXT.md sections
- [ ] 10. Judgments: declare two new judgments, fill the cache, full pytest green
- [ ] 11. Canonical .gitignore + .pre-commit-config.yaml; wire enforcement; repo-audit exit 0

---

### Task 1 — Scaffold: root pyproject + empty package + lockfile

Create the root project without moving anything:

- Root `pyproject.toml`: canonical template (`standards/canonical/
  pyproject.toml`, name `dev-playbook`) + carried extras from
  `tools/pyproject.toml` that are location-independent: `pyyaml>=6.0`
  dependency, `[tool.judgments]` (already in the root stub), dev-group with
  the canonical ruff floor. Console scripts and pytest/mypy config do NOT
  move yet (tasks 3 and 6).
- `src/dev_playbook/__init__.py` (empty package so uv_build has something
  to build; no module-name override — the default for `dev-playbook` is
  `src/dev_playbook`).
- `uv lock` + `uv sync` at the root (warm cache; offline OK).
- ⏳ `tools/pyproject.toml` gains `"../src"` in `[tool.pytest.ini_options]
  pythonpath` and `[tool.mypy] mypy_path`, so tools-rooted tests can import
  `dev_playbook.*` as modules migrate. Deleted by task 7.

Done when: `make check` green; both projects lock/sync cleanly.

### Task 2 — Move `lib/` → `src/dev_playbook/`

- `git mv` `tools/lib/{md,pyast,gitrepo}.py` → `src/dev_playbook/`.
- Rewrite `from lib import X` / `from lib.X …` →
  `from dev_playbook import X` across `tools/bin`, `tools/tests`,
  `tools/src`, `tools/transcript_export`.
- ⏳ Shims in `tools/bin/*` that inserted `tools/lib` now ALSO insert the
  root `src/` (`parents[2] / "src"` from `tools/bin`). Dual-path shims are
  transitional; task 5 collapses them to a single `parents[1] / "src"`.
- Bare-name grep for `lib` afterwards; judge every hit (string-form refs
  escape seds — a prototype lesson).

Done when: `make check` green.

### Task 3 — Move `judgments/` + `skipcache/`; console scripts to root

- `git mv` `tools/src/judgments` and `tools/src/skipcache` →
  `src/dev_playbook/`.
- Rewrite bare `judgments` / `skipcache` imports to `dev_playbook.`-
  prefixed. Known trap: `tests/test_skipcache.py` holds
  `"import skipcache.seen; …"` INSIDE a subprocess program string — the
  bare-name grep finds it; a sed anchored on line starts does not.
- Move `[project.scripts]` to the root pyproject, retargeted:
  `judgments-run = "dev_playbook.judgments.runner:run_cli"`,
  `judgments-lint = "dev_playbook.judgments.loader:lint_cli"`. Remove them
  and the `[tool.uv.build-backend] module-name` override from
  `tools/pyproject.toml` (nothing ships from tools/ anymore); re-lock both
  projects.

Done when: `make check` green; bare-name greps clean.

### Task 4 — Move `transcript_export/`

- `git mv` `tools/transcript_export` → `src/dev_playbook/transcript_export`.
- Rewrite its imports (`transcript_export` → `dev_playbook.transcript_export`)
  in `tools/bin/transcript-export`, `tools/tests/test_transcript_export*`,
  `tools/tests/transcript_fakes.py`, and intra-package relative imports if
  any are absolute.
- Bare-name grep for `transcript_export`; judge every hit.

Done when: `make check` green.

### Task 5 — Move `bin/` → `scripts/`

- `git mv tools/bin scripts` (11 scripts).
- Collapse each shim to `sys.path.insert(0, str(...parents[1] / "src"))`
  (parents[1] is now the repo root). judgments-run/judgments-lint's
  existing expression already lands there — imports only. sweep and
  repo-audit: `HOOK_REPO_ROOT` `parents[2]` → `parents[1]`. Audit all 11
  scripts, including bootstrap-labels, griffe-outline,
  internal-skill-audit.
- `.pre-commit-config.yaml`: hook entries `tools/bin/X` → `scripts/X`
  (paths only — the canonical restructure is task 11).
- ⏳ Test path constants: `parents[1] / "bin"` → `parents[2] / "scripts"`
  (tests still live under tools/). Reworked again by task 6 — mark them.
- Docs forced by commit hooks: new `scripts/index.md`; root `index.md`
  bullet; `scripts/`… (README still at tools/README.md until task 7 — fix
  the `workflow/workflow.md` link to `/tools/bin/bootstrap-labels` now, it
  breaks here).

Done when: `make check` green; every script runs from its new home
(spot-run repo-audit, python-lint).

### Task 6 — Move `tests/` to root; pytest/mypy config migrates

- `git mv tools/tests tests`.
- Path constants round 2: `parents[2] / "scripts"` → `parents[1] /
  "scripts"`; repo-root refs `parents[2]` → `parents[1]`; rename
  `TOOLS_DIR`/`tools_dir` → `REPO_ROOT`/`repo_root`. Known files:
  test_repo_audit, test_sweep, test_okf_lint, test_python_lint,
  test_ref_check, test_judgments_lint, test_skipcache.
- Root pyproject gains the pytest/mypy config: `pythonpath = ["src",
  "tests"]` (bare `import transcript_fakes` in two files needs `tests`),
  canonical `testpaths`, `mypy_path = ["src", "tests"]`,
  `explicit_package_bases = true`.
- Root Makefile's transitional check now runs pytest at the ROOT (keep the
  two `--deselect`s); tools/Makefile loses its test target.
- Remove the ⏳ `"../src"` entries from `tools/pyproject.toml` (dead — no
  tests left under tools/).

Done when: `make check` green from the root; `uv run pytest` collects the
full suite (~400 tests) from the root.

### Task 7 — Retire `tools/`; Makefile canonical

- Delete `tools/pyproject.toml`, `tools/uv.lock`, `tools/Makefile`,
  `tools/index.md`; `git mv tools/README.md scripts/README.md` (fix its
  frontmatter minimally); remove the emptied `tools/`.
- Root Makefile becomes the canonical Python form (`<code-roots>` =
  `src tests`) with the ONE `--deselect` deviation (removed by task 10).
- Root `index.md` and ref-check casualties: the remaining known breaks —
  `dotfiles/dot-claude/skills/orient-workspace-meta/SKILL.md`
  (tools/README.md link), `standards/judgments/declarations.md` ×2
  (`/tools/src/judgments/*.py`) — fix them; grep for any other `/tools/`
  refs. `judgments/doc-consistency.yaml` reference paths →
  `src/dev_playbook/judgments/…`.
- Confirm no ⏳ construct survives (dual-path shims, `../src` entries).

Done when: `make check` green; `tools/` gone; only one pyproject in the
repo.

### Tasks 8–11 — identical to Plan A's tasks 2, 3+4 (merged), 5, 6

Use the corresponding Plan A task cards verbatim (they are
layout-independent): canonical ci.yml/.python-version; the doc rewrites;
the judgments declarations + cache fill + deselect removal; the canonical
config swap + enforcement wiring + repo-audit exit 0.

---

## Working notes

- Prototype diff: `git show 95fd487:<path>` / ref `refs/archive/prototype-phase4`.
- uv cache is warm — `uv lock`/`uv sync` work offline in the sandbox.
- The sandbox has no network. Anything needing a download is a blocker to
  report, not to work around.
