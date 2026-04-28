# Skills hygiene — working notes

Working notes for an in-flight project to clean up the user's
Claude Code / agent-skills setup. This file is the cold-start brief
for any agent picking the work up later. Delete the file once task
#27 (the external-skills workflow doc) is committed.

## Mission

Get the agent-skills ecosystem on this machine into a clean, documented
state — authored skills refreshed, external skills installed via a
proper dependency manager, duplicates removed, conventions reconciled,
and a written workflow that stays good going forward.

## Where we are now (as of 2026-04-28)

- All 12 of Matt's skills surveyed; 10 picked for adoption, 2 rejected.
- Cross-reference convention question (#16) decided and implemented:
  - Repo docs use uniform inline links with absolute `~/workspace/...`
    paths (audience-split rule removed).
  - Skill bundles use Matt's target-based rule.
  - `standards/repo-documentation.md` and `standards/skill-authoring.md`
    updated and committed (`52f925b`).
  - Authored skills swept for the new convention (5 files, 11 edits).
    **Sweep is uncommitted** — pending user push.
- Working notes have been rewritten as a cold-start brief because the
  user is about to reset context.

**Recommended next-step order:**
1. **#23 Install Matt's skills** — cheap, file-placement only. The 6
   that don't depend on his repo conventions (`tdd`, `caveman`,
   `grill-me`, `grill-with-docs`, `improve-codebase-architecture`,
   `zoom-out`) are immediately usable. The 4 convention-dependent ones
   (`to-issues`, `to-prd`, `triage`, `setup-matt-pocock-skills`) can
   install but wait on #15 for full utility.
2. **#24 De-duplicate marimo-notebook** — quick housekeeping; no
   dependency on other tasks.
3. **#15 Plan adoption of Matt's repo conventions** — the biggest
   piece. Walk Matt's prescribed conventions row-by-row, decide
   adopt-as-is / adapt / preserve-superset for each, plan retrofit of
   active repos starting with dev-playbook itself.
4. **#25 Refresh authored skills** (sdd-* content audit + skill-creator
   vs write-a-skill comparison; cross-reference sweep portion already
   done).
5. **#26 Decide DHub ecosystem path**.
6. **#27 Document external-skills workflow** — closes the project.

## Why now

The user pivoted into this project after finishing a round of
spec-tools work (committed and merged to main on 2026-04-28). Several
forces motivate the cleanup:

- The user's authored sdd-* skills are old, written before recent
  changes to the SDD standards and before lessons from the spec-tools
  build. They need a fresh review and likely partial rewrites.
- Matt Pocock published a public skills repository
  (github.com/mattpocock/skills). Several skills there are useful, and
  Matt's conventions are worth aligning with where we adopt his work.
- An older parallel skills system (`.dhub/`, from PyMC Labs) has stale
  content. At least one duplicate exists with the newer Vercel-managed
  skills (`marimo-notebook` is in both `.agents/` and
  `.dhub/marimo-team/`).
- There is no written workflow for installing, updating, pinning, or
  removing external skills. The decision-making and documentation gap
  is itself one of the motivators.

## Background a fresh agent needs

### The user's three skill ecosystems

The user has GNU Stow managing `dotfiles/` symlinks into `$HOME`.
There are three separate skill-loading conventions in play:

| Path under `dotfiles/` | Loaded by | Origin / management |
|---|---|---|
| `.claude/skills/` | Claude Code (only) | Authored by the user, hand-edited in dotfiles |
| `.agents/skills/` | Multiple agents (claude-code, codex, cursor, amp, cline, gemini-cli, etc.) | Managed by Vercel-Labs `skills` CLI |
| `.dhub/skills/` | DHub clients (PyMC Labs ecosystem) | Older bespoke version-cache system |

Stow tree-folding means `~/.claude/skills`, `~/.agents`, and `~/.dhub`
are symlinks pointing into the user's `dotfiles/` git working tree.
When a tool (or the user) writes to one of those paths, the file lands
inside `dotfiles/` and is automatically git-tracked. **Edit the source
in `dotfiles/`, never the symlink target.**

### Vercel-Labs `skills` CLI

`npm install -g skills` (currently at 1.5.2; we use it via
`npx skills@latest …`). Marketed as "the open agent skills ecosystem",
maintained by Vercel folks (`rauchg` and `quuu`). Supports 50+ AI
agents.

What it does for us:
- `skills add <owner>/<repo> --list` — list skills in a remote repo
  without installing.
- `skills add <owner>/<repo> --skill <name>` — install one skill.
- Default install is symlink mode: writes the canonical copy under
  `~/.agents/skills/<name>/` (which Stow folds into
  `dotfiles/.agents/skills/<name>/`), and adds per-agent symlinks
  elsewhere as needed.
- Maintains a lock file at `~/.agents/.skill-lock.json` (Stow-folded
  to `dotfiles/.agents/.skill-lock.json`). Lock-file v3 records
  source URL, ref, GitHub tree SHA (`skillFolderHash`), and install
  timestamps. The lock file is the source of truth for what's
  installed and pinned.

The user is already using the CLI: marimo-team's `marimo-notebook` and
`marimo-batch` were installed via this CLI on 2026-03-13.

### The user's standards (relevant)

- [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
  — required and optional files in every repo (`CLAUDE.md`,
  `README.md`, optional `ROADMAP.md`, `BUSINESS_CONTEXT.md`, `specs/`,
  `docs/`, `docs/adr/`). Notably **no `CONTEXT.md`**.
- Cross-reference convention: repo docs use uniform inline links with
  absolute `~/workspace/...` paths (no audience split). Skill bundles
  use a target-based rule (link = "go open this", inline code =
  "this exists conceptually") borrowed from Matt's pattern. Linted by
  `tools/bin/ref-check`.
- Tactical work (bugs, tasks) lives in GitHub Issues. No `TODO.md` or
  similar in-repo file.
- [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md)
  — default pytest conventions: structure, test doubles, fixtures.
- [Skill authoring standard](~/workspace/dev-playbook/standards/skill-authoring.md)
  — frontmatter, file structure, body conventions. Defers to
  `repo-documentation.md` for cross-reference style.
- `sdd-standards/` — spec-driven-development standards (separate from
  general standards).

### The user's authored skills

In `dotfiles/.claude/skills/`:

- `agent-finished`, `code-quality-sweep`, `commit`, `doc-format`,
  `doc-rewrite`, `em-dashes`, `orient`, `orient-workspace-meta`,
  `prime-user-context`, `protocol-align-map-execute`, **`sdd-design`**,
  **`sdd-func-reqs`**, **`sdd-green`**, **`sdd-red`**,
  **`sdd-review`**, `skill-creator`.

The bolded `sdd-*` ones are content-audit targets in #25. `skill-creator`
gets compared to Matt's `write-a-skill` in #25.

### Matt Pocock's skills (12 total)

`npx skills add mattpocock/skills --list` returned:

**Engineering** — `diagnose`, `grill-with-docs`,
`improve-codebase-architecture`, `setup-matt-pocock-skills`, `tdd`,
`to-issues`, `to-prd`, `triage`, `zoom-out`.

**Productivity** — `caveman`, `grill-me`, `write-a-skill`.

Several engineering skills (`to-issues`, `to-prd`, `triage`,
`improve-codebase-architecture`, `tdd`, `zoom-out`) depend on
`setup-matt-pocock-skills` configuring a backlog backend, ADR layout,
and domain doc layout in the target repo. Adoption decisions therefore
came in two flavors: the unconditional 6 (no per-repo prerequisites)
and the convention-dependent 4 (require `setup-matt-pocock-skills` to
have been run in the target repo).

Final picks (10 adopt, 2 reject — accounts for all 12):

- **Adopt:** `tdd`, `caveman`, `grill-me`, `grill-with-docs`,
  `improve-codebase-architecture`, `zoom-out`, `to-issues`, `to-prd`,
  `triage`, `setup-matt-pocock-skills`
- **Reject:** `diagnose` ("too much"), `write-a-skill` (rejected as a
  skill, but feeds the skill-creator comparison in #25)

Notes on classification:
- `setup-matt-pocock-skills` is a one-time per-repo bootstrap, not a
  runtime skill. Frontmatter has `disable-model-invocation: true`. It
  scaffolds the per-repo files Matt's engineering skills read from.
- The decision to adopt all 10 was made in advance: `tdd`,
  `grill-with-docs`, `improve-codebase-architecture`, `to-issues`,
  `to-prd`, and `triage` all read from Matt's domain docs / backlog
  conventions, and the user does not want to run them in degraded
  mode without those conventions in place. So adopting them implies
  adopting the conventions — see #15.

## Plan — task list

Live status lives in the Claude Code task tracker. This file carries
the reasoning. Each task points back to a section below.

| # | Task | Status |
|---|------|--------|
| 8 | Survey Matt Pocock's skills | completed |
| 16 | Compare Matt's md-linking convention | completed (standards updated, sweep done — uncommitted) |
| 15 | Plan adoption of Matt's repo conventions | pending — biggest remaining piece |
| 23 | Install chosen Matt skills | pending |
| 24 | De-duplicate marimo-notebook | pending |
| 25 | Refresh authored skills | partially done (cross-reference sweep complete; content audit pending) |
| 26 | Decide DHub ecosystem path | pending |
| 27 | Document external-skills workflow | pending — closes the project |

## Section per task

### Survey Matt Pocock's skills (#8) — completed

12 skills surveyed; 10 to adopt, 2 to reject. See "Matt Pocock's
skills" in Background.

### Plan adoption of Matt's repo conventions (#15) — pending

**Decision (made 2026-04-28):** adopt Matt's standard. The user does
not want to run any of Matt's skills in degraded mode, so the
conventions those skills assume are coming with them.

This task is about *how*, not *whether*. Plan the adoption so:
- Documentation and scaffolding stay accurate end-to-end.
- Any superset we already have (functionality Matt's standard
  doesn't cover) is preserved.
- Active repos are retrofitted to the new convention with no broken
  cross-references or stale standards left behind.

#### Conventions Matt prescribes

Built from `setup-matt-pocock-skills/SKILL.md` and the engineering
skills' reads. Extend as more surface.

| Convention | Source | Maps to in our standard |
|---|---|---|
| `CONTEXT.md` at repo root (domain language / lexicon) | engineering skills | New file kind. Closest neighbor: `BUSINESS_CONTEXT.md` (different scope) and `specs/` (formal SDD) |
| `CONTEXT-MAP.md` for monorepos pointing at per-context `CONTEXT.md` files | setup-matt-pocock-skills | New file kind |
| `docs/adr/` for ADRs | setup-matt-pocock-skills | **Already in our standard** (optional, indexed by `docs/adr/README.md`) |
| `docs/agents/` directory holding `backlog.md`, `triage-labels.md`, `domain.md` | setup-matt-pocock-skills | New directory and file kinds |
| `## Agent skills` block in `CLAUDE.md` (or `AGENTS.md`) pointing at `docs/agents/*.md` | setup-matt-pocock-skills | New required block in `CLAUDE.md` |
| Backlog backend: GitHub Issues, local markdown under `.scratch/<feature>/`, or "other" with freeform description | setup-matt-pocock-skills | We mandate GitHub Issues; need to either match or codify multi-backend support |
| Triage label vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix` | setup-matt-pocock-skills, triage | New: we have no codified label vocabulary |
| PRD format | to-prd, to-issues | New: user has never written a PRD |
| Vertical-slice issue breakdown | to-issues | New: not codified |
| Testing conventions inside `/tdd` skill body | tdd | Overlaps `standards/testing-conventions.md` |

#### Our existing supersets (preserve)

Things we have that Matt's standard doesn't, and that we want to keep
through the adoption.

- **`BUSINESS_CONTEXT.md`** — distinct scope from `CONTEXT.md`
  (business problem & stakeholders, not domain lexicon). Both can
  coexist.
- **`ROADMAP.md`** — strategic goals; Matt's standard has no
  equivalent.
- **`specs/` layer** — formal SDD requirements & design (see
  `sdd-standards/`). Matt's standard has nothing comparable; this is
  a workspace-specific superset.
- **`standards/testing-conventions.md`** — separate, more prescriptive
  than `/tdd`'s embedded conventions. Reconcile vs. replace TBD.
- **`tools/bin/ref-check`** — link linter for our `~/workspace/...`
  cross-references.
- **GNU Stow + dotfiles workflow** — orthogonal to Matt's standard;
  unaffected.

#### Per-convention adoption decisions (TBD)

Walk the table above row by row and decide:
- **Adopt as-is** — copy Matt's prescription verbatim into our standard.
- **Adopt with our superset preserved** — Matt's prescription plus our
  existing rule(s) on top.
- **Adopt with adaptation** — Matt's prescription modified to fit our
  workspace (e.g. backlog backend always GitHub for our repos, drop
  the `.scratch/` option).

#### Outputs

- Amendments to
  [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
  — `CONTEXT.md`, `docs/agents/`, `## Agent skills` block, etc.
- Possibly new files under `standards/` for triage labels and PRD
  format.
- Reconciliation pass on
  [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md)
  against `/tdd` (replace? merge? keep both?).
- Retrofit plan for active repos. Order: dev-playbook itself first
  (eat our own dog food), then `sdd-tools`, `sdd-simulation`,
  `spec-tools`. For each: run `setup-matt-pocock-skills` (or fork it
  if we adapted), backfill `CONTEXT.md`, and verify
  `tools/bin/ref-check` still passes.
- Decision on whether to use `setup-matt-pocock-skills` as-is or fork
  it. If we adopt-with-adaptation on any of its scaffolded files, a
  fork is the safer path so future `skills update` doesn't overwrite
  our edits.

### Compare Matt's md-linking convention (#16) — completed

**Decision (2026-04-28):**
- **Repo docs** — use uniform inline links with absolute
  `~/workspace/...` paths. The previous audience-split rule (Human
  links / Agent backticks) was removed; it added complexity for token
  savings the user judged not worth it.
- **Skill bundles** — adopt Matt's target-based rule:
  - Inline link with relative path → file inside the same skill bundle.
  - Inline link with absolute `~/workspace/...` path → file at a
    stable workspace location.
  - Inline code → file in user's repo with varying location, or any
    directory.
  - Bare (no markup) → slash-skill invocations.
- **Path style stays absolute** for ref-check compatibility. ref-check
  is unchanged.

**Implementation (committed in `52f925b`):**
- Updated
  [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md):
  removed "Audience" → cross-reference-style coupling; replaced the
  audience-based table with a single inline-link rule for repo docs;
  added an "In skill bundles" subsection with the target-based table
  and rationale (matches Matt for ecosystem consistency).
- Updated
  [Skill authoring standard](~/workspace/dev-playbook/standards/skill-authoring.md):
  added a Cross-References section that defers to the primary source.

**Implementation — sweep (uncommitted, ready to commit):**
- `orient/SKILL.md` — 1× backticked path → inline link.
- `orient-workspace-meta/SKILL.md` — 2× backticked path → inline link.
- `code-quality-sweep/SKILL.md` — 2× backticked path → inline link.
- `sdd-red/SKILL.md` — 2× `` `/sdd-green` `` + 1× `` `/sdd-design` ``
  → bare.
- `sdd-green/SKILL.md` — 3× `` `/sdd-red` `` → bare.

`ref-check` passes (38 references, all ok). `sync-dotfiles.sh` in
`skill-creator/SKILL.md` stays backticked (script invocation, not a
"go open this" reference).

Matt's installed skills (`dotfiles/.agents/skills/`) already follow
the new style by construction; no work needed there.

### Install chosen Matt skills (#23) — pending

For each picked skill: `npx skills add mattpocock/skills --skill <name>`.

The CLI writes to `~/.agents/skills/<name>/`, which Stow-folds into
`dotfiles/.agents/skills/`. The lock file at
`dotfiles/.agents/.skill-lock.json` updates in place. Review the diff,
then commit.

If #15 decided we fork any skill (e.g. to swap Matt's testing
conventions for ours, or to remap `CONTEXT.md` reads), do that
post-install in the dotfiles working tree and document the divergence
so future `skills update` runs don't silently overwrite our edits.

### De-duplicate marimo-notebook (#24) — pending

`marimo-notebook` exists in both:
- `dotfiles/.agents/skills/marimo-notebook/` (Vercel-managed)
- `dotfiles/.dhub/skills/marimo-team/marimo-notebook/` (older DHub)

Likely keep the Vercel copy (newer, lock-file-pinned, multi-agent).
Remove the DHub duplicate. Update
`dotfiles/.claude/rules/marimo.md` if the canonical path changes.

### Refresh authored skills (#25) — partially done

Audit user-authored skills in `dotfiles/.claude/skills/` against
current practice and external inputs.

**Cross-reference style sweep — done** (see #16 for details).

**sdd-\* skills — pending.**
`sdd-{design,red,green,review,func-reqs}`. Inputs:
- [SDD standards index](~/workspace/dev-playbook/sdd-standards/README.md)
  — current standards.
- `~/workspace/dev-playbook/sdd-standards/lessons.md` — lessons logged
  during the spec-tools work.
- Recent spec-tools build at `~/workspace/dev-playbook/spec-tools/` —
  shows current SDD practice in action.
- Matt's `/tdd` skill (post-install) — reconcile any testing-convention
  conflicts identified in #15.

Identify what's stale vs. still load-bearing. Rewrite as needed.

**`skill-creator` — pending.**
`dotfiles/.claude/skills/skill-creator/`. Compare against Matt's
`write-a-skill` (rejected for direct adoption but worth studying).
Pull ideas about structure, progressive disclosure, bundled
resources, and any other patterns Matt uses that our skill doesn't.
Update `skill-creator` with what fits.

### Decide DHub ecosystem path (#26) — pending

`dotfiles/.dhub/` is an older parallel skills system using
`.version_cache.json` to track:
- `pymc-labs/dhub-cli`
- `pymc-labs/pymc-modeling`
- `marimo-team/marimo-notebook` (duplicate, see #24)

Decide:
- Consolidate remaining DHub skills into the Vercel CLI flow (only
  feasible if upstream sources are CLI-installable), **or**
- Keep DHub as a separate documented track and refresh content in
  place.

### Document external-skills workflow (#27) — pending

The deliverable that closes this project. Short doc in dev-playbook
explaining:

- Where authored skills live (`dotfiles/.claude/skills/`).
- Where external skills live (`dotfiles/.agents/skills/`,
  `dotfiles/.dhub/skills/` if retained).
- How the Vercel CLI installs and pins skills (lock file is the
  source of truth).
- Stow tree-folding integration (CLI writes land directly in
  git-tracked dotfiles).
- How to update / remove a skill.
- Rationale for any DHub-vs-Vercel split decided in #26.
- The fork-and-document pattern for skills we modify after install.

When committed, delete this working-notes file.

## Conventions for working in this file

- Update the per-task sections as decisions land. The task tracker
  carries status; the file carries the reasoning.
- When a sub-instance of an existing theme surfaces (e.g. another
  Matt convention to evaluate), add it to the relevant section's
  table or list. Don't spawn a new top-level task for every example.
- Keep the cold-start brief and "Where we are now" sections truthful
  as the project evolves. A new agent should be able to read
  top-to-bottom and pick up where things left off.
