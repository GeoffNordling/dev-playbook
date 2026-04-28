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

## Why now

The user pivoted into this project after finishing a round of
spec-tools work (committed and merged to main on 2026-04-28). Several
forces motivate the cleanup:

- The user's authored sdd-* skills are old, written before recent
  changes to the SDD standards and before lessons from the spec-tools
  build. They need a fresh review and likely partial rewrites.
- Matt Pocock published a public skills repository
  (github.com/mattpocock/skills). It contains skills the user wants to
  evaluate, especially `tdd`, `grill-with-docs`, and `to-issues`.
  Matt is a known professional whose conventions are worth studying
  even where they conflict with ours.
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

### The user's standards (relevant excerpts)

- `standards/repo-documentation.md` — required and optional files in
  every repo (`CLAUDE.md`, `README.md`, optional `ROADMAP.md`,
  `BUSINESS_CONTEXT.md`, `specs/`, `docs/`, `docs/adr/`). Notably
  **no `CONTEXT.md`**.
- Cross-reference style is split by audience: Human and Human+Agent
  use inline links with full `~/workspace/...` paths; Agent-only uses
  full path as inline code, no link. Linted by
  `tools/bin/ref-check`.
- Tactical work (bugs, tasks) lives in GitHub Issues. No `TODO.md` or
  similar in-repo file.
- `standards/testing-conventions.md` — default pytest conventions:
  structure, test doubles, fixtures.
- `sdd-standards/` — spec-driven-development standards (separate from
  general standards).

### The user's authored skills

In `dotfiles/.claude/skills/`:

- agent-finished, code-quality-sweep, commit, em-dashes, orient,
  orient-workspace-meta, polish, prime-user-context,
  protocol-align-map-execute, **sdd-design**, **sdd-func-reqs**,
  **sdd-green**, **sdd-red**, **sdd-review**, skill-creator,
  standardize-markdown.

The bolded `sdd-*` ones are the targets of the refresh in task #25.

### Matt Pocock's skills (12 total)

`npx skills add mattpocock/skills --list` returned:

**Engineering** — `diagnose`, `grill-with-docs`,
`improve-codebase-architecture`, `setup-matt-pocock-skills`, `tdd`,
`to-issues`, `to-prd`, `triage`, `zoom-out`.

**Productivity** — `caveman`, `grill-me`, `write-a-skill`.

Several engineering skills (`to-issues`, `to-prd`, `triage`,
`improve-codebase-architecture`, `tdd`, `diagnose`, `zoom-out`)
depend on `setup-matt-pocock-skills` configuring a backlog backend,
ADR layout, and domain doc layout in the target repo.

Final picks (10 adopt, 2 reject — accounts for all 12):

- **Adopt:** `tdd`, `caveman`, `grill-me`, `grill-with-docs`,
  `improve-codebase-architecture`, `zoom-out`, `to-issues`, `to-prd`,
  `triage`, `setup-matt-pocock-skills`
- **Reject:** `diagnose` ("too much"), `write-a-skill` (rejected as a
  skill, but feeds the skill-creator comparison action in #25)

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

The Claude Code task tracker holds the live status. Each task points
back to a section in this file.

| # | Task | Status |
|---|------|--------|
| 8 | Survey Matt Pocock's skills | in progress |
| 15 | Plan adoption of Matt's repo conventions | pending |
| 16 | Compare Matt's md-linking convention | done — implementation folded into #25 |
| 23 | Install chosen Matt skills | pending |
| 24 | De-duplicate marimo-notebook | pending |
| 25 | Refresh authored skills | pending |
| 26 | Decide DHub ecosystem path | pending |
| 27 | Document external-skills workflow | pending |

#15 plans the adoption of Matt's standard in a way that preserves
our existing supersets. It gates the *use* of the convention-dependent
skills (`setup-matt-pocock-skills`, `to-issues`, `to-prd`, `triage`,
plus degraded reads in `tdd` / `grill-with-docs` /
`improve-codebase-architecture`). The unconditional 6 (`tdd`,
`caveman`, `grill-me`, `grill-with-docs`,
`improve-codebase-architecture`, `zoom-out`) can be installed (#23)
before #15 finishes since installation is just file placement; their
*degraded reads* improve once #15's outputs land. #16 (md-linking)
remains a separate styling decision. #25–#27 follow once external
skills are settled.

## Section per task

### Survey Matt Pocock's skills (#8)

User is reading the 12 skills returned by the CLI. Outcome: a
finalized adopt/reject list. Carry this list into #15 (the
conventions some skills depend on) before installing in #23.

### Plan adoption of Matt's repo conventions (#15)

**Decision (made 2026-04-28):** adopt Matt's standard. The user does
not want to run any of Matt's skills in degraded mode, so the
conventions those skills assume are coming with them.

This task is no longer about *whether*; it's about *how*. Plan the
adoption so:
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

- **Audience-split cross-reference style** — Human / Human+Agent use
  inline links; Agent-only uses inline code with full path.
  See `standards/repo-documentation.md`. Linted by
  `tools/bin/ref-check`.
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
- **`tools/bin/ref-check`** — link linter for our path-based
  cross-references.
- **GNU Stow + dotfiles workflow** — orthogonal to Matt's standard;
  unaffected.

#### Per-convention adoption decisions (TBD)

Need to walk the table above row by row and decide:
- **Adopt as-is** — copy Matt's prescription verbatim into our standard
- **Adopt with our superset preserved** — Matt's prescription plus our
  existing rule(s) on top (e.g. `CONTEXT.md` adopted, but
  cross-references still follow our audience-split style)
- **Adopt with adaptation** — Matt's prescription modified to fit our
  workspace (e.g. backlog backend always GitHub for our repos, drop
  the `.scratch/` option)

#### Outputs

- Amendments to `standards/repo-documentation.md` — `CONTEXT.md`,
  `docs/agents/`, `## Agent skills` block, etc.
- Possibly new files under `standards/` for triage labels and PRD
  format.
- Reconciliation pass on `standards/testing-conventions.md` against
  `/tdd` (replace? merge? keep both?).
- Retrofit plan for active repos. Order: dev-playbook itself first
  (eat our own dog food), then `sdd-tools`, `sdd-simulation`,
  `spec-tools`. For each: run `setup-matt-pocock-skills` (or fork it
  if we adapted), backfill `CONTEXT.md`, and verify
  `tools/bin/ref-check` still passes.
- Decision on whether to use `setup-matt-pocock-skills` as-is or fork
  it. If we adopt-with-adaptation on any of its scaffolded files, a
  fork is the safer path so future `skills update` doesn't overwrite
  our edits.

### Compare Matt's md-linking convention (#16)

#### Sample of Matt's cross-references

From SKILL.md bodies in `improve-codebase-architecture`, `tdd`,
`grill-with-docs`, `triage`, `setup-matt-pocock-skills`:

**Inline links to sibling files in the same skill:**
- `[LANGUAGE.md](LANGUAGE.md)` (bare filename)
- `[INTERFACE-DESIGN.md](INTERFACE-DESIGN.md)`
- `[tests.md](tests.md)`, `[mocking.md](mocking.md)`,
  `[deep-modules.md](deep-modules.md)`,
  `[interface-design.md](interface-design.md)`,
  `[refactoring.md](refactoring.md)`
- `[CONTEXT-FORMAT.md](./CONTEXT-FORMAT.md)` (`./` prefix variant)
- `[ADR-FORMAT.md](./ADR-FORMAT.md)`
- `[AGENT-BRIEF.md](AGENT-BRIEF.md)`
- `[backlog-github.md](./backlog-github.md)`

**Inline links to files in another skill (`../`):**
- `[CONTEXT-FORMAT.md](../grill-with-docs/CONTEXT-FORMAT.md)`
- `[ADR-FORMAT.md](../grill-with-docs/ADR-FORMAT.md)`

**Descriptive link text instead of bare filename:**
- `look for [refactor candidates](refactoring.md)`
- `[deep modules](deep-modules.md)`
- `[testability](interface-design.md)`

**Inline code (backticks) for files mentioned by name without
linking:**
- `` `CONTEXT.md` ``, `` `LANGUAGE.md` `` (in prose, even though
  `LANGUAGE.md` is also linked elsewhere)
- `` `docs/adr/` ``, `` `AGENTS.md` ``, `` `CLAUDE.md` ``
- `` `CONTEXT-MAP.md` ``, `` `.out-of-scope/` ``

**Slash-skill invocations:**
- `/grill-with-docs`, `/setup-matt-pocock-skills`, `/triage`
- All bare slash references, no backticks, no links.

#### Inferred rule

Matt does not split by audience. He splits by **what the reference is
for**:

- **Inline link** when the target is a specific file at a knowable
  relative path that the reader should *open*. Path is relative
  (bare, `./`, or `../`).
- **Inline code** when mentioning a file *conceptually* — naming a
  file kind that exists in the user's repo whose location varies, or
  pointing at a directory.
- The semantics differ: link = "go read this", backtick = "this
  exists, don't look at me".

#### Comparison to our `standards/repo-documentation.md`

Our standard governs cross-references *in repo documentation* across
the workspace:

| Audience | Style |
|---|---|
| Human | Inline link with absolute path: `[Spec standard](~/workspace/dev-playbook/sdd-standards/spec-standard.md)` |
| Human + Agent | Same as Human |
| Agent (only) | Inline code with absolute path; no link. Rationale: links add markup an agent has to parse without adding information |

Linted by `tools/bin/ref-check`, which validates `~/workspace/...`
paths.

| Dimension | Matt | Our repo-documentation.md |
|---|---|---|
| Path style | Relative (bare / `./` / `../`) | Absolute (`~/workspace/...`) |
| Audience differentiation | None — one style for all readers | Split: human / human+agent vs. agent-only |
| Link-vs-backtick decision | By **target semantics**: open this vs. mention this | By **audience**: humans read it vs. agents only |
| Linting | None visible | `ref-check` on `~/workspace/...` paths |

#### Internal inconsistency in our standards

Our `standards/skill-authoring.md` already shows this example for
skill cross-references:

> See [UI.md](references/UI.md) for UI element details.

That's Matt's pattern: relative path, inline markdown link, in a
context (skill bodies) that is overwhelmingly agent-read. So the
audience-split rule we apply to *repo docs* does **not** apply to our
own *skill bodies* — we already use Matt's style there.

The split is therefore not a consistent stance about agent-readable
links; it's specific to the repo-documentation scope.

#### Decision (2026-04-28)

Scope: **skills only**. Repo documentation convention is unchanged.

- **Repo docs (`standards/repo-documentation.md`)** — keep audience-split
  rule, keep absolute `~/workspace/...` paths, keep `ref-check`.
  Reason: switching repo-doc paths to relative would either break
  `ref-check` or require reworking it, which the user does not want
  to do now.
- **Skills (`standards/skill-authoring.md`)** — adopt Matt's style.
  Reason: the inconsistency between agent-only repo files (backticked
  paths, no link) and our skill bodies (already using inline relative
  links per the existing example) was real. Resolving it in the
  direction of Matt is cleaner than rewriting our skills to use
  backticks-only.

#### Implementation

Folded into task #25 (Refresh authored skills):
- Update `standards/skill-authoring.md` to explicitly document
  Matt's cross-reference style (link with relative path = "go read
  this"; backticks = "this exists conceptually").
- Sweep `dotfiles/.claude/skills/` to apply the style consistently.

Matt's installed skills (`dotfiles/.agents/skills/`) already follow
this style by construction; no work needed there.

### Install chosen Matt skills (#23)

For each picked skill: `npx skills add mattpocock/skills --skill <name>`.

The CLI writes to `~/.agents/skills/<name>/`, which Stow-folds into
`dotfiles/.agents/skills/`. The lock file at
`dotfiles/.agents/.skill-lock.json` updates in place. Review the diff,
then commit.

If #15 decided we fork any skill (e.g. to swap Matt's testing
conventions for ours, or to remap CONTEXT.md reads), do that
post-install in the dotfiles working tree and document the divergence
so future `skills update` runs don't silently overwrite our edits.

### De-duplicate marimo-notebook (#24)

`marimo-notebook` exists in both:
- `dotfiles/.agents/skills/marimo-notebook/` (Vercel-managed)
- `dotfiles/.dhub/skills/marimo-team/marimo-notebook/` (older DHub)

Likely keep the Vercel copy (newer, lock-file-pinned, multi-agent).
Remove the DHub duplicate. Update
`dotfiles/.claude/rules/marimo.md` if the canonical path changes.

### Refresh authored skills (#25)

Audit user-authored skills in `dotfiles/.claude/skills/` against
current practice and external inputs.

**sdd-\* skills** —
`sdd-{design,red,green,review,func-reqs}`. Inputs:
- `~/workspace/dev-playbook/sdd-standards/` — current standards
- `~/workspace/dev-playbook/sdd-standards/lessons.md` — lessons logged
  during the spec-tools work
- Recent spec-tools build at `~/workspace/dev-playbook/spec-tools/` —
  shows current SDD practice in action
- Matt's `/tdd` skill (post-install) — reconcile any testing-convention
  conflicts identified in #15

Identify what's stale vs. still load-bearing. Rewrite as needed.

**skill-creator** —
`dotfiles/.claude/skills/skill-creator/`. Compare against Matt's
`write-a-skill` (rejected for direct adoption but worth studying).
Pull ideas about structure, progressive disclosure, bundled
resources, and any other patterns Matt uses that our skill doesn't.
Update skill-creator with what fits.

**Cross-reference style sweep (from #16 decision)** —
- Update `~/workspace/dev-playbook/standards/skill-authoring.md` to
  document the cross-reference style explicitly:
  - **Inline link with relative path** — when the target is a
    specific file the reader should open. Forms: bare filename,
    `./file.md`, `../other-skill/file.md`. Example:
    `[UI.md](references/UI.md)`.
  - **Inline code (backticks)** — when naming a file conceptually
    without pointing the reader to read it now. Example:
    `` `CONTEXT.md` ``, `` `docs/adr/` ``.
  - **Slash-skill invocations** — bare, no backticks, no link.
    Example: `/commit`, `/orient`.
- Sweep all authored skills in `dotfiles/.claude/skills/` to apply
  the style consistently.

### Decide DHub ecosystem path (#26)

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

### Document external-skills workflow (#27)

The deliverable that closes this project. Short doc in dev-playbook
explaining:

- Where authored skills live (`dotfiles/.claude/skills/`)
- Where external skills live (`dotfiles/.agents/skills/`,
  `dotfiles/.dhub/skills/` if retained)
- How the Vercel CLI installs and pins skills (lock file is the
  source of truth)
- Stow tree-folding integration (CLI writes land directly in
  git-tracked dotfiles)
- How to update / remove a skill
- Rationale for any DHub-vs-Vercel split decided in #26
- The fork-and-document pattern for skills we modify after install

When committed, delete this working-notes file.

## Conventions for working in this file

- Update the per-task sections as decisions land. The task tracker
  carries status; the file carries the reasoning.
- When a sub-instance of an existing theme surfaces (e.g. another
  Matt convention to evaluate), add it to the relevant section's
  table or list. Don't spawn a new top-level task for every example.
- Keep the cold-start brief at the top truthful as the project
  evolves. A new agent should be able to read top-to-bottom and pick
  up where things left off.
