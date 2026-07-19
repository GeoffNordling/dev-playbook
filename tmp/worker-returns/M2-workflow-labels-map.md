# M2 · opus · terrain map: workflow/labels (issues 208, 207) — verbatim return

## Subsystem sketch

`workflow/workflow.md` is the semantic authority for a four-tuple label scheme `(category, mode, tests, phase)`. `src/dev_playbook/label_scheme.json` is the operational data (dimensions → color, description recipe, values); `label_scheme.py` parses it into `canonical_labels()` and `values_by_dimension()`. Two consumers read the module: `scripts/bootstrap-labels` (mints the closed-world set into a repo over `gh`) and `src/dev_playbook/workspace_audit.py` (checks live repos at full parity + four-tuple validity). The doc↔scheme agreement is **already** covered by an LLM judgement (`scheme-vs-graph`), cache-gated in pytest at pre-push.

## Issue (a) rename — file inventory & parseability of workflow.md

`workflow/workflow.md` structure (single file, 221 lines):
- **§ Valid labels table** (L26–34): clean GFM table `Dimension | Label | Meaning`, 7 fixed rows only (category/mode/tests), labels backtick-wrapped. Trivially parseable — but it deliberately omits `phase:*`.
- **§ Graph-based flow** (L45–76): one mermaid flowchart. `phase:*` labels are **derived, not listed** — §Naming (L84–88) states the rule in prose: work nodes = rectangles `id[..]` + diamonds `id{..}`; terminal markers `id([..])` and `subgraph name[..]` mint nothing; map node-id `_`→`-`, prefix `phase:`.
- **Parseability verdict:** table = easy. Graph = feasible but fragile — a checker must be mermaid-shape-aware (distinguish `[..]`/`{..}`/`([..])`), skip `subgraph`/`%%{init}` lines, dedupe ids appearing on both edge ends, and hard-code the "work-nodes-only" rule that lives only in prose. The two-source split (table for 7 fixed + graph for phase) is the real complexity, and §Naming's rule is the load-bearing, un-encoded part.

## Issue (b) scheme↔doc cross-check — what already exists

- `src/dev_playbook/label_scheme.py:9-12` — the docstring "left to a judgement, never parsed here." That judgement is real: **`judgements/code-matches-docs.yaml:69-82` id `scheme-vs-graph`**, evidence `label_scheme.json`, reference `workflow/workflow.md`, claim states the exact bidirectional-equality property issue 207 wants.
- It is enforced, not decorative: `tests/test_judgements_gate.py:39-41` auto-discovers **every** declared judgement (`load(resolve_root())`) and parametrizes `assert_judgement_cached(jid)`; `make check-judgements` (Makefile:16-17, `SKIP_JUDGEMENTS=0`) is the pre-push hook (`.pre-commit-config.yaml:26-27`). So a stale `scheme-vs-graph` cache blocks the push.
- **Critical reframing:** issue 207's premise "nothing verifies they agree" is inaccurate — an LLM judgement already does. 207 is really "replace/supplement the *semantic LLM* check with a *deterministic parse-based* one." Whoever builds it should decide whether the new deterministic check retires the `scheme-vs-graph` judgement or sits beside it.
- Other coupled tests hard-code label text: `tests/dev_playbook/test_label_scheme.py:20-36` pins all 17 label descriptions incl. the literal `"See workflow.md."`; `test_workspace_audit.py:66-70` builds fixtures from `canonical_labels()`.

## Three-bucket "workflow" occurrence summary (~599 hits / 68 files, `.venv`+`uv.lock` excluded)

**Bucket 1 — OUR "Workflow" concept (rename targets).** Notable sites:
- Directory `workflow/` + its 4 docs (`workflow.md`, `skill-authoring.md`, `index.md`, `README.md` — titles/frontmatter "Workflow").
- Standard card `standards/workflow.md` (title/frontmatter/body) + index line `standards/index.md:25` + root index line `index.md:19`.
- Path cross-refs to `/workflow/workflow.md` (a rename breaks these): `standards/tracking.md:10`, `standards/tracking/issues.md:21,34,87`, `standards/build/enforcement.md:39`, `standards/claude-code/skill-conventions.md:51`, `workflow/skill-authoring.md:9,41,50,54`.
- Skill bodies (dotfiles) pinning `~/workspace/dev-playbook/workflow/workflow.md`: `issue-overwatch:20,83`, `agent-view-overwatch:20`, `intake:20`, `open-pr:21`, `doc-pr-review:27`.
- Code/data: `label_scheme.py:9` docstring; `label_scheme.json:6,12,18,24` label descriptions "See workflow.md." (these mint onto GitHub); `scripts/bootstrap-labels:8` docstring path.
- Judgements referencing the concept files: `code-matches-docs.yaml:79`, `standard-cards.yaml:177,182,185-186`.
- Machine identifier: `workspace_audit.py:56` rule id `workflow.tuple-valid` (namespace `workflow.`), surfaced in the card's Audit cell.
- `dotfiles/dot-claude/settings.json:144` — our concept ("The workflow's hands-off nodes…") embedded in an autoMode.allow prose entry.

**Bucket 2 — Claude Code harness 'workflow' feature (MUST NOT rename).**
- `dotfiles/dot-claude/workflows/` (`ralph-loop.js`, `scatter-gather.js`); `.claude/workflows` harness dir.
- `dotfiles/dot-claude/settings.json:85` `workflowKeywordTriggerEnabled`.
- `harness-recipes/recipes/scatter-gather.md:5,13,54,56,63` + `ralph-loop.md` — "Workflow runtime", `Workflow({name:...})`, `resource: /dotfiles/dot-claude/workflows/…`.
- `judgements/docs-match-code.yaml` ids `scatter-gather-recipe-matches-workflow`, `run-judgements-skill-matches-tooling`; `run-judgements`/`ralph-setup` SKILLs.

**Bucket 3 — generic / third-party "workflow" (do not touch).**
- GitHub Actions: `scripts/repo-audit:121,418` and `.github/workflows/ci.yml` references — platform term.
- Generic English: `README.md`/`index.md` "workflow definitions", "multi-agent workflows" (harness-recipes), `standards/semantic-validation.md:22` "semantic-detection workflow", historical Decision Records (`docs/decisions/0001,0004,0005,0007` — 0005 is literally titled "issue-workflow-reorganization"; leave history as-is).

## Fragilities & surprises

1. **The rename reaches GitHub state across all repos.** `label_scheme.json`'s descriptions carry "See workflow.md." Renaming the doc changes every minted label's description → `bootstrap-labels` re-mints and `workspace-audit`'s label-scheme parity check flags drift in every workspace repo until re-bootstrapped. Decide whether the label recipe even needs the filename. [HUMAN DECIDED at checkpoint 1: drop file references from label descriptions entirely.]
2. **17 hard-coded description strings** in `test_label_scheme.py:20-36` embed "See workflow.md." — an automated rename must hit the test fixture too, or the suite reds.
3. **OKF index-description coupling.** `scripts/okf-audit` enforces each index bullet's description == the child's frontmatter description (rule `knowledge-organization.description`, okf-audit L22,80-84). Renaming titles/descriptions in `workflow/README.md`, `standards/workflow.md`, etc. must update `index.md:19`, `workflow/index.md:3-5`, `standards/index.md:25` in lockstep or okf-audit reds.
4. **Consumer-pinned identifiers are safe.** No hook id in `.pre-commit-hooks.yaml` and no script filename contains "workflow", so nothing consumer repos pin (per distribution.md) breaks. The only machine identifier in play is the *internal* audit rule `workflow.tuple-valid`; renaming it is optional and self-contained (it also feeds the rule-prefix→standard mapping behind the subset judgements).
5. **A rename that touches a live cache.** Because `scheme-vs-graph` and `standard-card-workflow` hard-code `workflow/workflow.md`, editing that file changes their prepared content keys → both judgement caches invalidate → `make check-judgements` reds at pre-push until re-run. Expected, but the rename PR will need a judgements re-run.

## Ordering constraint (rename 208 ↔ cross-check 207)

Not independent — both center on (`workflow/workflow.md`, `label_scheme.json`). The existing `scheme-vs-graph` judgement hard-codes `reference: [workflow/workflow.md]` (`code-matches-docs.yaml:79`); any new deterministic checker in 207 would hard-code that path too. **Recommended order: land the rename (208) first, then point any cross-check work at the settled path.** [MOOT if 207 closes, as human ratified at checkpoint 1.]
