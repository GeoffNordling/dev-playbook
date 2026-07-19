# Wave-1 Sonnet probes P1–P6 — verbatim returns (P3, P5 lightly condensed where superseded)

## P1 · judgments.refuted reality (issue 184)

**H-a — SURVIVED.** The rule id and `--refuted` flag both exist and are wired together, live.
- `scripts/judgements-run` (shim) → `src/dev_playbook/judgements/runner.py:run_cli` → `main`, registered as the `judgements-run` console script in `pyproject.toml:13`.
- Rule id constant: `runner.py:35` `REFUTED = "semantic-validation.refuted"` (the actual rule id is `semantic-validation.refuted`, not literally `judgments.refuted` — that compound string appears nowhere in code).
- `--refuted` flag: defined `runner.py:193-199` on the `record` subparser; consumed at `runner.py:143,149,158` (mutual-exclusion check against passing `ids`, then fed to `refutations()` which builds `RefutedFinding` per id, `runner.py:92-101`).
- Drift-guard coverage: `tests/test_rule_registry.py:47,61` ties `runner.py`'s `RefutedFinding`/`RULES` into the repo-wide `--list-rules` ground-truth check.
- Behavior tests: `tests/dev_playbook/judgements/test_runner.py:147-198` (`--list-rules` prints `REFUTED`; `record --refuted` emits a finding and caches nothing; mixing an id as both passed and refuted is rejected).

**H-b — SURVIVED.** Whole-repo grep for `refuted`: only (1) runner.py the canonical emitter, (2) its tests, (3) run-judgements SKILL.md prose describing the fix-loop, (4) tmp/ meta-docs about this probe. No hits in `standards/`, `judgements/*.yaml`, `src/dev_playbook/findings.py`, `standards/semantic-validation.md`, or `tests/test_rule_registry.py` for the literal string `refuted`. Second pass for `judg[e]*ments\.refuted` and `semantic-validation` aliases: none found.

**H-c — SURVIVED.** `dotfiles/dot-claude/skills/run-judgements/SKILL.md` step 4: `judgements-run record <pass-id> [<pass-id> …]` — "**Only passes are ever recorded.** If nothing passed, skip the call." (line 54). Step 5 handles a refuted verdict entirely through fixing the artifact/claim and re-running the judge (line 58) — never `--refuted`.

## P2 · standards-audit latency (issue 183)

**H-a — SURVIVED.** `.pre-commit-config.yaml:91-96` (the local block this repo actually runs): `id: standards-audit`, `entry: scripts/standards-audit`, `language: script`, `pass_filenames: false`, `always_run: true`. The published `.pre-commit-hooks.yaml` deliberately omits standards-audit (comment at lines 88-90: dev-playbook-local, `standards/` doesn't exist in consumer repos).

**H-b — SURVIVED.** `standards_audit.py:538-562` `_list_rules_via_subprocess` runs `scripts/<name> --list-rules` per cited detector; each script's shebang `#!/usr/bin/env -S uv run --script`. Cited today: **11 detectors** — decisions-audit, judgements-audit, judgements-run, okf-audit, python-audit, ref-audit, repo-audit, skill-audit, standards-audit, testing-audit, workspace-audit. (bootstrap-labels, file-graph, griffe-outline, transcript-export exist but uncited.)

**H-c — REFUTED.** Three consecutive warm runs of `scripts/standards-audit` (exit 0, "standards-audit: clean"): 0.614 s / 0.612 s / 0.623 s. Single-detector `--list-rules` (repo-audit, 3 runs): 0.064 / 0.062 / 0.067 s. Consistently ~0.61-0.62 s — well under the claimed 1-2 s. [Orchestrator re-verified: 0.636 s.]

## P3 · lint inventory vs issue list (issue 169; superseded in detail by W2-A, kept for the deltas)

**H-a — REFUTED.** 7 of the issue's 8 paths are stale — PR #205 ("Name standard cards by their question, and Britishise 'judgement'") moved `standards/judgments/*` → `standards/docs/*`, `standards/claude-code/*`, `instruments/*`, `standards/judgements/*`. Only `standards/docs/cross-references.md` unchanged. `pyproject.toml:14` now `judgements-audit = "dev_playbook.judgements.loader:lint_cli"` (script name renamed by #166; only the target still says lint). **No bare `lint()` function exists anywhere** (`git grep -n "def lint("` → 0 hits); nearest: `lint_findings()` (loader.py:279), `class LintFinding` (loader.py:53).

**H-b — REFUTED.** 242 hits / 48 files vs ~13 inventoried. Key misses beyond the issue's list: `Makefile:1,8,14` + canonical template `lint` target; `scripts/judgements-audit:8,22,25`; `scripts/okf-audit` own docstrings; `scripts/python-audit`; `decisions_audit.py:226` + `testing_audit.py:366` argparse; loader.py ~15 hits; `md.py:140` (6th type-lint file); whole test surfaces (`test_judgements_audit.py` ~13 hits, `test_okf_audit.py`, `test_rule_registry.py:46`); **`readings/datasheet/lint-suite.html`** (whole tracked generated file named "lint-suite", cites pre-#166 script names that no longer exist); `readings/datasheet/judgements.html`, `tools.html`, `readings/file-graph/*` (even older names). Decision Records `docs/decisions/0001,0002,0008,0009` (~18 hits) immutable per `standards/decisions/records.md` §Immutability — an audit rule must exempt `docs/decisions/**` wholesale.

## P4 · fan-out guardrails inventory (issue 199)

**H-a — SURVIVED.** The literal string `fork` appears nowhere in `dotfiles/dot-claude`. Fan-out surfaces lacking guardrails:
| File | Fan-out instruction | Guardrail? |
|---|---|---|
| `skills/issue-overwatch/SKILL.md` | §3 "Spawn a subagent whose prompt is the launch line, nothing more" (:46); review stops dispatch audits in parallel (:38) | No leaf clause; partial mitigations: fixed AFK skill list (:58), native /code-review pinned medium (:62) |
| `skills/run-judgements/SKILL.md` | "one judge agent per miss, in parallel" via scatter-gather (:44) | No |
| `workflows/ralph-loop.js` | one fresh agent() per iteration (:88) | No |
| `workflows/scatter-gather.js` | parallel(JOBS.map(... agent(...))) (:63-76) | Only MAX_JOBS = 1000 (:21) |
The leaf-clause pattern exists elsewhere: `skills/fill-issue-gaps/SKILL.md:56` — "do not dispatch the next node, do not launch any other agent or skill on the issue, do not advance the phase".

**H-b — SURVIVED.** `rules/` contains exactly `bash-commands.md` + `edit-in-dev-playbook.md`; zero fork/subagent/agent matches there or in `dotfiles/dot-claude/CLAUDE.md`.

**H-c — SURVIVED.** No `code-review` dir under `dotfiles/dot-claude/skills/` (only code-pr-review, sdd-code-pr-review, doc-pr-review). `issue-overwatch/SKILL.md:60`: "The native /code-review breaks the launch template. It is a harness built-in, not one of our skills". Workspace fix surface: its own skills, workflows/*.js, rules/, CLAUDE.md.

## P5 · rename blast radius (issue 208; corroborates M2 independently)

**SURVIVED with caveats.** 354 hits / 74 files (git-tracked), every hit bucketed. None of the consumer-facing identifier classes contain "workflow": hook ids (all 8: repo-audit … judgements-audit), scripts/ filenames, `[project.scripts]` (judgements-run, judgements-audit), label VALUES in label_scheme.json (only descriptions reference workflow.md); consumer repos pin a git `rev`, not paths (distribution.md).

Riskiest items:
1. `skills/run-judgements/SKILL.md` uses "workflow" 6× — ALL bucket-2 (Workflow tool calls / generic), zero our-concept, despite living in bucket-1 territory. `workflows/ralph-loop.js:16` explicitly references "the Workflow runtime's own docs" (Anthropic's SDK feature).
2. `standards/build/ci.md:9` / `standards/build/index.md:15` — "the byte-identical workflow that runs exactly the hook suite" = GitHub Actions vocabulary inside standards prose — textually indistinguishable from bucket-1 without reading for meaning.
3. Decision Records 0001/0004/0005/0007 frozen (records.md:63 "the body is never rewritten"); contain live-looking bucket-1 hits incl. a same-repo `~/workspace/dev-playbook/standards/workflow.md` citation — must be left untouched; ref-audit already exempts DR bodies as link-check sources.
4. `workspace_audit.py:56`: `TUPLE_VALID = "workflow.tuple-valid"` — internal finding-id, asserted verbatim at 9 sites in `tests/dev_playbook/test_workspace_audit.py`, tabulated in `standards/build/enforcement.md`. Coordinated multi-site rename, internal-only.
5. Label description propagation: fixing the source string doesn't retroactively fix bootstrapped repos — each needs a `bootstrap-labels` re-run; `workspace-audit` parity check already detects the drift class.
Excluded: `readings/file-graph/dev-playbook.{json,html}` — stale snapshot with dangling paths (`docs/adr/0005-...`, phantom `skills/workflow-overwatch/SKILL.md`) — regenerate, don't hand-edit.

## P6 · existing cross-check (issue 207)

**H-a — REFUTED.** `judgements/code-matches-docs.yaml:69-81`, judgement id `scheme-vs-graph`: claim = label_scheme.json mints exactly the labels workflow.md states (7 fixed via Valid-labels table + phase via graph-derived inventory, `_`→`-`, bidirectional). evidence: [src/dev_playbook/label_scheme.json], reference: [workflow/workflow.md], model claude-sonnet-5, effort high. Enforced: `tests/test_judgements_gate.py:39-41` parametrizes every declared judgement; `make check-judgements` (Makefile:16-17, SKIP_JUDGEMENTS=0) runs at pre-push (.pre-commit-config.yaml). Probe ran the gate live for scheme-vs-graph: 1 passed (cached green). Deterministic paths genuinely do NOT cross-check workflow.md — `workspace_audit.py:52` `tracking.label-scheme` compares live GitHub labels vs JSON only; `test_label_scheme.py` pins a hand-copied EXPECTED_LABELS snapshot vs the JSON.

**H-b — SURVIVED.** `label_scheme.py:10-12`: "The scheme-vs-graph consistency between the two is left to a judgement, never parsed here." — exact match.

**H-c — SURVIVED.** Live extraction and comparison: category {maintenance, extension}, mode {sdd, direct, spike}, tests {yes, no} all match; phase: mermaid work-nodes {intake, sdd-specs, sdd-spec-review, sdd-tdd, sdd-pr-review, design, tdd, build, pr-review, spike} (10, graph order) == JSON phase.values (same 10, same order). 17 labels both sides, zero drift.
