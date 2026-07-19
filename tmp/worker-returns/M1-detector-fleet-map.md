# M1 · opus · terrain map: detector fleet (issues 184, 183, 169) — verbatim return

Note on spelling: the repo uses British **judgements** everywhere (dir, scripts, console-scripts, `[tool.judgements]`), and the rule is `semantic-validation.refuted` — not `judgments.refuted`. The task's "judgments-*" are American approximations of `judgements-*`.

## Subsystem sketch (who calls whom)

- **standards-audit** (`scripts/standards-audit` → `src/dev_playbook/standards_audit.py:main`) is `always_run` in the local block only (`.pre-commit-config.yaml:91-96`); it is `LOCAL_ONLY` (`standards_audit.py:387`), never in the published manifest.
- `main` calls `audit(root, _list_rules_via_subprocess)` (`standards_audit.py:588`); `audit` (528) runs four checks. `check_rule_matrix(root, list_rules)` (303) is the fleet driver.
- **Detector discovery** = `_audit_citations` (282-295): for each flat card `standards/<name>.md`, it reads the `## Audit` cell and collects markdown-link targets that start `/scripts/`; third-party (ruff/shellcheck) and `/judgements/*.yaml` pointers are excluded by that scoping (test `test_standards_audit.py:344`).
- **`_list_rules_via_subprocess`** (538-562): runs `scripts/<name> --list-rules` with `cwd=root`, `timeout=10`. Absent script / OSError / timeout / `returncode!=0` → raises `CannotRun`. `returncode==0` → returns stripped non-blank stdout lines — **possibly empty**.
- Each script's shebang is `#!/usr/bin/env -S uv run --script` with PEP-723 inline deps, so every call is a cold `uv` env-resolve. The 11 distinct cited detectors subprocessed per commit: repo-audit, python-audit, testing-audit, ref-audit, okf-audit, decisions-audit, skill-audit, workspace-audit, standards-audit, **judgements-audit**, **judgements-run**. That is issue (b)'s "~10".
- **judgements-audit** (`scripts/judgements-audit` → `loader.lint_cli`, pyproject.toml:14) is a real pre-commit hook (`.pre-commit-hooks.yaml:72`, `always_run`); emits `semantic-validation.declaration` + `semantic-validation.evidence-path` (`loader.py:31-33`).
- **judgements-run** (`scripts/judgements-run` → `runner.run_cli`, pyproject.toml:13) is **not** a hook — only cited by the card; emits the single `semantic-validation.refuted` (`runner.py:35-36`). The card is `standards/semantic-validation.md` (Audit cell cites judgements-audit L19 and judgements-run L21); contract docs live under `standards/judgements/`. Card prefix `semantic-validation` ≠ script name `judgements` (already a deliberate split).

## What happens if a cited detector emits no rules

If `judgements-run --list-rules` prints nothing but exits 0, `_list_rules_via_subprocess` returns `[]` (no `CannotRun`). Then `prefixes_of["judgements-run"]={}`, and Direction 2 (`standards_audit.py:339-349`) emits at `standards/semantic-validation.md`: *"Audit cell cites scripts/judgements-run, but it emits no semantic-validation.\* rule."* (Distinct from the `CannotRun` path 325-335 → *"does not answer --list-rules"*.) So removing REFUTED **without** removing the card citation reds rule-matrix — it does not crash. `print_rules(())` prints nothing and returns 0 (`findings.py:32-34`), so `--list-rules` stays valid.

## Per-issue file inventory

**(a) Remove `semantic-validation.refuted` + `--refuted`** (issue 184)
- `src/dev_playbook/judgements/runner.py`: `REFUTED`/`RULES` (35-36), `RefutedFinding` (44-50), `refutations()` (92-101), `--refuted` arg (193-199) and its `record` branch + both-set guard (143-162), docstring (10-16).
- `standards/semantic-validation.md`: delete the judgements-run Audit bullet (21-23) — **must** land in the same change or rule-matrix reds.
- `tests/dev_playbook/judgements/test_runner.py`: `REFUTED` import (9) + refuted tests (147-197).
- `tests/test_rule_registry.py`: drop the `RefutedFinding` CARRIER row (47) and runner.py `RULES` REGISTRY row (61) — else `test_..._references_a_rule_constant` asserts "found no RefutedFinding constructions" (96).
- `scripts/judgements-run` docstring only. No consumer/README/hook-id ripple (judgements-run isn't a hook; scripts/README.md:127 lists it in the non-hook table already).

**(b) Cut cold-start latency of the 11 subprocesses** (issue 183)
- Only `src/dev_playbook/standards_audit.py:_list_rules_via_subprocess` (538-562). The `Callable` seam (`audit` 528, `check_rule_matrix` 303, injection at 588) already isolates it — swap impl without touching matrix logic. Tests inject `fake_list_rules` (`test_standards_audit.py:268`), so a perf refactor is invisible to them; the real per-detector `--list-rules` contract is pinned elsewhere (test_rule_registry.py `RULES` tuples + each detector's `test_list_rules_*`). Dev-playbook-local cost only (standards-audit is LOCAL_ONLY).

**(c) Purge "lint" vocabulary** (issue 169, pre-pivot inventory)
- Load-bearing identifiers (in-repo ripple only): `lint_cli` (`loader.py:335`) → also `pyproject.toml:14` target + `scripts/judgements-audit` import; `LintFinding` (`loader.py:53`, constructed 298/305/311/323) → pinned as a **string** in `tests/test_rule_registry.py:46`; `lint_findings` (`loader.py:279`, in-module).
- Prose only: loader.py docstrings (7,130,134,152,336,347), `bench.py:7`, `consuming.md:4,104`, `judgements/index.md:10`, test names in `tests/test_judgements_audit.py` (41,47,69,81,111), `test_loader.py` comments (194,220).
- Broader "lint" if in scope: the `type-lint` nickname (`standards/docs/bundle.md:32,37`, `claude-code/files.md:11`, `docs/indexes.md:55`, `docs/document-types.md:11`, `md.py:140`) and argparse `--help` "Lint …" in `decisions_audit.py:226` + `testing_audit.py:366`.
- **No** hook-id / console-script-key / rule-id contains "lint" → no consumer-pin ripple per distribution.md.

## Fragilities / surprises

1. **`--refuted` is orphaned.** Its only consumer, the run-judgements skill, records passes only (`SKILL.md:54`; refutations are fixed → content-key changes → re-planned, never `record --refuted`). So the rule exists purely to back the card's judgements-run citation through rule-matrix Direction 2 — issue (a)'s premise is confirmed by the code.
2. **Empty `--list-rules` is silent success, not `CannotRun`** — the failure mode is a rule-matrix finding, not an exit-2 crash.
3. **`test_rule_registry.py` hard-codes carrier class names and tuple names as strings** (46-47, 60-61); both (a) and (c) touch it, and the AST test fails loud if a listed class vanishes or is renamed without updating the list.
4. **hook-surfaces is orthogonal to (a):** it only checks hooks whose entry is `scripts/…` (`standards_audit.py:393-403`) and requires each *local hook* be card-cited (515-521); judgements-run is not a hook, so dropping its card citation does not trip hook-surfaces.
5. **okf-audit lockstep:** `judgements/index.md:10` description must equal `consuming.md:4` frontmatter description (`knowledge-organization.description`, `scripts/okf-audit:22,80`). If (c) rewrites "lint hook", change both or okf-audit reds.
6. **Naming split trap:** card/prefix/rules say `semantic-validation`; dir/scripts/config/console say British `judgements`. Issue (c) is "lint→audit" only — do not sweep the judgement/judgment spelling into it.

## Ordering constraints

- **(a) is atomic:** the runner rule-removal and the `semantic-validation.md` Audit-bullet removal must ship together, or the `always_run` standards-audit reds rule-matrix between the two edits.
- **(a) before (b):** after (a), judgements-run leaves the cited fleet, so (b) optimizes 10 subprocesses, not 11 — not a hard dependency, but cleaner; and any `--list-rules` cache (b) adds must not outlive (a)'s removal of judgements-run's rule.
- **(a) and (c) collide on files:** both edit `runner.py`/`loader.py`, `tests/test_rule_registry.py` (CARRIERS/REGISTRIES), `tests/dev_playbook/judgements/test_runner.py`, the `semantic-validation.md` card, and the `judgements/` docs — sequence them (suggest a → c) to avoid churn conflicts.
- **(c) internal:** the index↔frontmatter description lockstep above.
