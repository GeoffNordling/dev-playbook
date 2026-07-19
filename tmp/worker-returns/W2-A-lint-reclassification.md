# W2-A · sonnet · reclassify lint hits under the pivot rule (issue 169) — verbatim return

## Verdict on H-a: REFUTED

Re-running `git grep -ni "lint"` now finds **249 hits across 48 files** (prior sweep: 242/48 — the delta is mostly tmp/LEDGER.md's ledger prose accumulating since). After excluding the two blanket-UNTOUCHABLE buckets (121 hits in `readings/**` generated artifacts, 15 hits in frozen `docs/decisions/**`), **113 hits required a per-line call**. Of those:

- **27 are VIOLATION** — more than the ~15 the hypothesis allows, and they aren't a single fix: they span at least 4 independent naming decisions (`type-lint`, `ref-audit`-called-"linter", each audit script's own docstring/argparse text, `judgements`'s "lint hook"/"Lint the declarations").
- **41 more are BORDERLINE**, clustered in one genuinely undecided question (the judgements-audit internals) — if humans rule that "code implementing a standard's audit" counts as "in the context of a standard," the violation count roughly doubles to ~68.

Coverage: 249/249 hits classified (121 UNTOUCHABLE-readings, 15 UNTOUCHABLE-decisions, 27 VIOLATION, 41 BORDERLINE, 35 LEGAL-FALLBACK, 10 process-ledger LEGAL-FALLBACK).

## 1. VIOLATION (27) — file:line, current text → suggested fix

**`type-lint` naming (9 sites)** — an OKF standard rule nickname, inconsistent with the fleet's `*-audit` convention:
- `scripts/okf-audit:8` — `**Type-lint**` → `**Type-audit**`
- `scripts/okf-audit:209` — `consumed by the type-lint)` → `consumed by the type-audit)`
- `instruments/file-graph.md:49` — `the type-lint set` → `the type-audit set`
- `src/dev_playbook/md.py:140` — `is subject to the type-lint.` → `is subject to the type-audit.`
- `standards/claude-code/files.md:11` — `exempt from the type-lint.` → `exempt from the type-audit.`
- `standards/docs/bundle.md:32` — `is subject to the type-lint.` → `is subject to the type-audit.`
- `standards/docs/bundle.md:37` — `are not type-linted.` → `are not type-audited.`
- `standards/docs/document-types.md:11` — `type-lint (a pre-commit hook) asserts` → `type-audit (a pre-commit hook) asserts`
- `standards/docs/indexes.md:55` — `type-lint) fails the commit` → `type-audit) fails the commit`

**`ref-audit` called "linter" (2 sites, standards prose)**:
- `standards/docs/cross-references.md:66` — `` `ref-audit` linter (`/scripts/ref-audit`) validates`` → drop "linter": `` `ref-audit` (`/scripts/ref-audit`) validates``
- `standards/docs/cross-references.md:81` — `what the linter has enforced at commit time` → `what ref-audit has enforced at commit time`
- (frozen origin of this phrasing at `docs/decisions/0009-same-repo-resolution.md:23,26,70` — UNTOUCHABLE, context only)

**Detectors' own docstring/argparse saying "Lint…" while they audit a standard (7 sites)**:
- `scripts/okf-audit:2` — `"""Lint the repo's Open Knowledge Format (OKF) bundle.` → `"""Audit the repo's...`
- `scripts/okf-audit:253` — `leaves every other file unlinted.` → `leaves every other file unaudited.`
- `scripts/okf-audit:551` — `description="Lint the repo's OKF bundle: ..."` → `description="Audit the repo's OKF bundle: ..."`
- `scripts/python-audit:2` — `"""Lint Python sources against the workspace conventions.` → `"""Audit Python sources...`
- `scripts/python-audit:143` — `description="Lint Python sources: ..."` → `description="Audit Python sources: ..."`
- `src/dev_playbook/decisions_audit.py:226` — `description="Lint Decision Records: ..."` → `description="Audit Decision Records: ..."` (note: `prog="decisions-audit"` two lines above already says "audit" — internal inconsistency, not just style)
- `src/dev_playbook/testing_audit.py:366` — `description="Lint Python tests: ..."` → `description="Audit Python tests: ..."` (same `prog="testing-audit"` inconsistency)

**`judgements` standard naming its own hook "lint" (3 sites)** — inconsistent with the hook's registered name, `judgements-audit`:
- `standards/judgements/consuming.md:4` — frontmatter `...pytest gate, lint hook, cache fill` → `...pytest gate, audit hook, cache fill`
- `standards/judgements/consuming.md:104` — `## 4. Lint the declarations on commit` → `## 4. Audit the declarations on commit`
- `standards/judgements/index.md:10` — same blurb → `...pytest gate, audit hook, cache fill`
- (index↔frontmatter lockstep: okf-audit's knowledge-organization.description rule — change both together)

**Other standards prose (1 site)**:
- `dotfiles/dot-claude/skills/doc-pr-review/SKILL.md:43` — `The deterministic linters already prove references resolve and indexes match frontmatter` → `The deterministic audits already prove...`

**Downstream test prose for the OKF/ref-audit standards (5 sites)**:
- `tests/test_okf_audit.py:207` — `def test_malformed_frontmatter_is_flagged_and_siblings_still_lint(` → `..._still_audit(`
- `tests/test_okf_audit.py:211` — `no silent mass un-linting.` → `no silent mass un-auditing.`
- `tests/test_okf_audit.py:328` — `is still linted` → `is still audited`
- `tests/test_ref_audit.py:407` — `expected staleness, not lint errors.` → `expected staleness, not audit findings.`
- `tests/test_ref_audit.py:144` — fixture string `"the linter lives at \`/tools/bin/ref-audit\`\n"` → cosmetic only; weakest item on the list

## 2. BORDERLINE (41) — one bundled question

All 41 sites are one coupled decision: **does code that *implements* a standard's own audit machinery count as "in the context of a standard"?** Same identifier chain throughout:

- **The identifiers** (`src/dev_playbook/judgements/loader.py`): `class LintFinding` (:53), `def lint_findings` (:279) and its call/construct sites (:292,298,305,311,323,358), `def lint_cli` (:335) — plus docstrings narrating them (:7,130,134,136,152,336,338) and argparse `description="Lint a repo's judgement declarations..."` (:347).
- **Console-script contract**: `pyproject.toml:14` — `judgements-audit = "dev_playbook.judgements.loader:lint_cli"` (script already `-audit`; only the Python target is `lint_cli`).
- **The shim**: `scripts/judgements-audit:8,22,25`.
- **Cross-file reference**: `src/dev_playbook/judgements/bench.py:7`.
- **Test mirrors**: `tests/test_judgements_audit.py` — docstring (:1), import (:9), `LINT_HOOK` (:13, used :149), 6 test names (`test_lint_*`), `lint_findings(...)` calls (:44,48,61,76,91,103,121,140) — 17 hits in that one file.
- **Second test file**: `tests/dev_playbook/judgements/test_loader.py:194,220` — comments.
- **Registry pin**: `tests/test_rule_registry.py:46` — pins the string `"LintFinding"` in `CARRIERS`.

**Fleet evidence**: `test_rule_registry.py`'s `CARRIERS` table shows every other audit script's finding type is `Finding` (okf-audit, python-audit, repo-audit, skill-audit, standards_audit.py, testing_audit.py, decisions_audit.py) or `Line`/`RefutedFinding`. `LintFinding` is the one outlier in the fleet's own naming convention.

## 3. LEGAL-FALLBACK (35 + 10 process-ledger) — grouped

- **`make lint` wrapping ruff** (6): `Makefile:1,8,14` + `standards/build/canonical/Makefile.python:1,8,14`.
- **`[tool.ruff.lint*]` TOML and readers** (17): `pyproject.toml:51,57,60,68`; canonical `pyproject.toml:25,31,34,40`; `scripts/repo-audit:487-493`; `standards/build/python.md:61,69`; `tests/test_repo_audit.py:534,544,560`.
- **Third-party lint, explicit phrasing** (4): `standards/python.md:20`, `standards/shell.md:18`, `tests/dev_playbook/test_standards_audit.py:355`, `standards/build/enforcement.md:58`.
- **`make.md` target table** (2): `standards/build/make.md:25,31`.
- **Generic English** (1): `standards/docs/document-types.md:40` — "a reviewer or linter".
- **Vendored skill** (1): `dotfiles/.agents/skills/marimo-notebook/SKILL.md:235`.
- **PR-review skills' generic "don't run lint tools yourself"** (3): `code-pr-review/SKILL.md:33`, `doc-pr-review/SKILL.md:31`, `sdd-code-pr-review/SKILL.md:47`.
- **`tmp/LEDGER.md` (10)** — self-referential process scratch, won't survive to main.

## 4. UNTOUCHABLE (136)

- **`readings/**` generated artifacts (121)**: `readings/file-graph/dev-playbook.json` (69), `readings/datasheet/tools.html` (22), `readings/datasheet/lint-suite.html` (19), `readings/datasheet/judgements.html` (9), `readings/file-graph/dev-playbook.html` (2). Fix is regeneration — already known-stale independent of vocabulary.
- **Frozen Decision Records (15)**: `docs/decisions/0001:29`, `0002:4,19,27,60,90,133,137`, `0008:19,21`, `0009:23,26,70,73`, and `docs/decisions/index.md:7` (pinned verbatim echo of 0002's frozen frontmatter).
