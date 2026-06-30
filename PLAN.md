# PLAN.md — Adopt the Open Knowledge Format (OKF) for dev-playbook

**Status:** working plan. **Transient** — delete before the final PR. NOT an OKF
concept doc (no frontmatter; excluded from the bundle and the type-lint).

**Branch:** `worktree-adopt-okf` (worktree at `.claude/worktrees/adopt-okf/`).
No autonomous-commit authority — pause for human review/commit after each phase.

**Goal:** Convert dev-playbook's agent-navigated documentation into one OKF
bundle, so an agent can triage by frontmatter and navigate via generated indexes
with minimal context bloat. Scope is THIS repo only; other workspace repos adopt
later.

---

## Locked decisions (the contract)

### Bundle
- **One bundle = the whole repo.** Not split. (More bundles ⇒ more cross-bundle
  citations; not worth it.)
- **In scope** (docs an agent crawls/loads dynamically): `standards/`, `docs/`,
  `workflow/`, `protocols/`, `harness-recipes/`, `tools/` doc(s), every dir
  `README`, root `README`, `CONTEXT.md`.
- **Out of scope (harness-owned, NOT OKF):** `CLAUDE.md` (any), `SKILL.md` + skill
  `references/`, `rules/`, `settings*.json`, `.js` workflows, Python code under
  `tools/`. Phase F must state this boundary explicitly.

### Type registry — 8 concept types
Title Case, acronyms upper (matches OKF SPEC.md style, e.g. `BigQuery Table`,
`API Endpoint`).

- **`Standard`** — A normative conformance target: rules a repo, doc, or agent
  must follow, that a reviewer or linter could cite to reject work.
- **`README`** — The GitHub-rendered landing/orientation doc for a directory or
  the repo; prose, with any listing delegated to a sibling `index.md`.
  Role-based: filename `README.md` ⟺ `type: README`.
- **`ADR`** — An immutable, numbered record of one architectural decision and its
  rationale.
- **`Guide`** — A teaching or procedure doc you read to learn how to do or think
  about something, not to be measured against.
- **`Survey`** — An evaluative analysis of options or tradeoffs, gathered to
  inform a decision.
- **`Protocol`** — A formal algorithm for structured human–agent collaboration.
- **`Vocabulary`** — The canonical definitions of the workspace's domain terms
  (lives in `CONTEXT.md`).
- **`Recipe Description`** — A prose description of a reusable harness pattern;
  the recipe itself is the backing code/skill/workflow, this doc only describes it.

Reserved, **typeless** (no frontmatter): `index.md` (directory listing).
`log.md` is NOT used (see parked).

### Frontmatter field profile (per concept doc)
- `type` — REQUIRED; one of the 8 above.
- `title` — yes.
- `description` — yes (the one-liner that powers triage + generated indexes).
- `tags` — NO. `timestamp` — NO.
- `resource` — only on `Recipe Description`: the backing `.js` as a repo-root
  path (e.g. `/dotfiles/dot-claude/workflows/ralph-loop.js`). A companion skill,
  if any, is linked in the body — NOT in `resource`. Do not overload `resource`
  as a list.

### Links
- Intra-repo doc→doc links: **OKF `/`-from-repo-root** (e.g.
  `/standards/doc-conventions.md`).
- Cross-repo refs: stay `~/workspace/…` (treated as OKF citations).
- `ref-check` rewrite to understand both classes is **deferred to phase G**.

### Indexes
- `README.md` keeps its name + gets `type: README`; its **listing moves to a
  sibling typeless `index.md`**.
- `index.md` is **auto-generated from child frontmatter `description`s** (a
  producer script).
- Root `index.md` declares `okf_version`.

### Type-registry doc + lint
- Allowed types live in **`standards/document-types.md`** (`type: Standard`): the
  8 names + one-line definitions + the field profile.
- Lint (phase G): assert every concept's `type` ∈ the set declared there; wire
  into pre-commit. Subset/exact semantics TBD in G.

### Editorial rule
- **Stale content is deleted, not archived.** No decision-log narration in living
  docs; a one-line "since refactored / dropped" is the most.
  **Exception: ADRs are immutable** — never edited or scrubbed.

---

## File → type map (37 concepts + 7 generated `index.md`)

- **`Standard` (14):** `standards/`: adr-conventions, build-conventions,
  doc-conventions, issue-conventions, judgments, python-conventions,
  python-project-conventions, repo-documentation, repo-settings, skill-conventions,
  testing-conventions, **document-types (NEW)**; `workflow/`: skill-authoring,
  workflow.
- **`README` (8):** root, `standards/`, `docs/adr/`, `workflow/`, `protocols/`,
  `harness-recipes/`, `tools/`, `dotfiles/`.
- **`ADR` (7):** `docs/adr/0001…0007`.
- **`Guide` (2):** `standards/module-design`, `standards/skill-management`.
- **`Survey` (2):** `docs/third-party-survey`, `docs/sandboxing`.
- **`Protocol` (1):** `protocols/align-map-execute/formulation`.
- **`Vocabulary` (1):** `CONTEXT.md` (NEW — from `architecture-vocabulary`).
- **`Recipe Description` (2):** `harness-recipes/recipes/ralph-loop`,
  `harness-recipes/recipes/scatter-gather`.

**Generated `index.md` (7, typeless):** root, `standards/`, `docs/adr/`,
`workflow/`, `protocols/`, `harness-recipes/`, `tools/`. (`dotfiles/README` is
narrative, no listing → no index. `docs/` top-level has no README today → index
TBD, see parked.)

**Deleted:** `standards/dependency-taxonomy.md`; skill bundle
`dotfiles/dot-claude/skills/improve-codebase-architecture/` (3 files).

---

## Execution — phases (human review/commit checkpoint after each)

**A · Cleanup & migration** *(by hand)*
- Delete `standards/dependency-taxonomy.md`.
- Delete the `improve-codebase-architecture` skill bundle. Leave ADR mentions
  (immutable).
- Create `CONTEXT.md` (`type: Vocabulary`, keep existing CONTEXT format) from
  `architecture-vocabulary.md`; delete the original; repoint inbound links
  (`standards/README` row, `standards/module-design`).
- SAME pass: trim `docs/third-party-survey.md` (~line 19) to drop
  `dependency-taxonomy`, `architecture-vocabulary`, `improve-codebase-architecture`;
  ≤1-line "since refactored / dropped" note. (~line 15 describes Pocock's bundle —
  leave it.)

**B · Define the profile** *(by hand — BEFORE C)*
- Author `standards/document-types.md`: 8 type names + definitions + field profile.
- Write 1–2 exemplar frontmatter blocks to lock the `description` voice (also the
  spec if C ever falls back to agent fan-out).

**C · Frontmatter pass** *(by hand)*
- For each of the 37 concept docs: read it if not fresh, then add `type` + `title`
  + `description` in the locked voice.
- On the 2 `Recipe Description` docs: `resource` → backing `.js`; body links the
  companion skill where one exists (ralph-loop → ralph-setup; scatter-gather →
  none).

**D · Indexes** *(script)*
- For the 7 listing dirs: move the README's listing into a generated sibling
  `index.md` (built from child `description`s); README keeps narrative + frontmatter.
- Root `index.md` gets `okf_version`.

**E · Links** *(script + verify)*
- Convert intra-repo doc links to `/`-from-repo-root. Cross-repo stays
  `~/workspace/…`.

**F · Standards rewrite** *(by hand — after A–E, before G)*
- Rewrite `standards/repo-documentation.md` to define the OKF profile as the doc
  standard + the in/out-of-bundle boundary.
- Align `standards/doc-conventions`, `standards/adr-conventions`,
  `standards/skill-conventions` to the new structure + link form.

**G · Tooling** *(by hand / TDD — last)*
- Rewrite `tools/bin/ref-check` for the two link classes; update its tests.
- Implement the type-lint (concept `type` ∈ `document-types.md`); wire into
  pre-commit (`.pre-commit-hooks.yaml` / `.pre-commit-config.yaml`).

---

## Parked / open micro-items
- `log.md` — not adopted; revisit later.
- `docs/` top-level `index.md` — none today (no README); decide whether to add.
- Type-lint exact semantics (subset vs exact) — settle in G.
- Other workspace repos adopt OKF — later, separate effort.

---

## Progress
- [ ] A — cleanup & migration
- [ ] B — `document-types.md` + exemplars
- [ ] C — frontmatter on 37 docs
- [ ] D — generate `index.md`
- [ ] E — link conversion
- [ ] F — standards rewrite
- [ ] G — `ref-check` + type-lint + pre-commit
- [ ] Final — delete PLAN.md, open PR
