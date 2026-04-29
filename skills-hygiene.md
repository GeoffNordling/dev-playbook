# Skills hygiene — working notes

A cold-start brief for any agent picking up the in-flight skills-hygiene
cleanup. Read top-to-bottom and you should know the mission, current
state, what's next in what order, why, and the background needed to act.

## Mission

Get the agent-skills ecosystem on this machine into a clean, documented
state — authored skills refreshed, external skills installed via a
single dependency manager, conventions reconciled with Matt Pocock's
standard, and a written workflow that stays good going forward.

## Where we are now

- **Single skill registry.** The Vercel `skills` CLI is the only
  installer. DHub has been decommissioned: `dhub-cli` PyPI tool
  uninstalled, `dotfiles/.dhub/` removed, `.dhub` dropped from
  `sync-dotfiles.sh` MANAGED_DIRS. Rationale: org-gated auth at
  `pymc-labs--api.modal.run` (the prod registry restricts `dhub login`
  to allowed GitHub orgs), single-vendor Modal infra risk, and every
  DHub-published skill is also on GitHub and installable via Vercel.
- **Skill management standard committed** in `58b25ae`:
  [Skill management standard](~/workspace/dev-playbook/standards/skill-management.md)
  covers locations, install/update/remove commands, and the
  don't-edit-installed rule. Indexed in
  [standards/README.md](~/workspace/dev-playbook/standards/README.md).
- **External skills currently installed via Vercel**: `marimo-batch`,
  `marimo-notebook`, `pymc-modeling`. Lock file at
  `dotfiles/.agents/.skill-lock.json`.
- **Cross-reference convention shipped earlier** (commit `52f925b`,
  authored skills swept in `b3cc9bd`). Repo docs use uniform inline
  links with absolute `~/workspace/...` paths; skill bundles use the
  target-based rule (link = "go open this", inline code = "this exists
  conceptually"). Rules in
  [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
  and
  [Skill authoring standard](~/workspace/dev-playbook/standards/skill-authoring.md).
- **Matt Pocock's skills surveyed.** 9 picked for adoption, 3 rejected
  (originally 10/2; `to-prd` moved to reject when its overlap with our
  SDD spec layer surfaced — see #15 and the planned ADR-0006). Picks
  listed in Background.
- **Per-convention decisions logged.** See the #15 decisions table.
- **Standards rewrite landed (#15 steps 1-4).** New
  [Issue management standard](~/workspace/dev-playbook/standards/issue-management.md);
  [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md)
  updated; `/tdd` cross-ref added in
  [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md).
  Steps 5-10 pending.
- **`ref-check` has one known-broken link** — `repo-documentation.md`
  points at `grill-with-docs`'s `ADR-FORMAT.md`, which resolves once #23
  installs that skill.

## What's next, in order

1. **#15 dev-playbook implementation** — Rename existing ADRs to
   4-digit; install and run `setup-matt-pocock-skills` against
   dev-playbook; edit the generated `issue-tracker.md`; defer
   `CONTEXT.md` creation; run `ref-check --all`. Steps 5-9 of the #15
   checklist.
2. **#15 ADR tie-off** — Interview the user for reasons, then write
   `docs/adr/0006-adopt-matt-pocock-conventions.md` retrospectively,
   covering both the broad adoption and the PRD rejection. Step 10.
3. **#23 install remaining Matt skills, #28 update cookiecutter** —
   Install the other 8 adopted skills (skip `to-prd`); propagate the
   conventions into `project-template/`.
4. **#25 refresh authored skills** — sdd-* content audit and
   `skill-creator` vs `write-a-skill` comparison. Last so any
   conventions that shake out during the earlier phases inform the
   audit.

Closed tasks: #8 (survey Matt's skills, results in Background), #16
(cross-reference convention), #24 (de-duplicate `marimo-notebook` —
content confirmed identical between Vercel and DHub before DHub was
decommissioned), #26 (DHub ecosystem path — decommissioned), #27
(external-skills workflow doc — committed as
`standards/skill-management.md`).

## Why now

The user pivoted into this project after finishing a round of spec-tools
work. Two motivators remain:

- The user's authored sdd-* skills are old, written before recent
  changes to the SDD standards and before lessons from the spec-tools
  build. They need a fresh review and likely partial rewrites.
- Matt Pocock published a public skills repository
  (github.com/mattpocock/skills). Several skills there are useful, and
  Matt's conventions are worth aligning with where we adopt his work.

## Background a fresh agent needs

### Skill ecosystem on this machine

Two kinds of skills coexist in `dotfiles/`:

| Path under `dotfiles/` | Loaded by | Origin |
|---|---|---|
| `.claude/skills/` | Claude Code only | Authored by the user, hand-edited |
| `.agents/skills/` | ~50 agents (claude-code, codex, cursor, amp, gemini-cli, etc.) | Vercel `skills` CLI, pulled from GitHub |

Stow tree-folding maps `~/.agents/` and `~/.claude/skills/` into the
dotfiles repo. Edit the source in `dotfiles/`, never the symlink
target. The
[Skill management standard](~/workspace/dev-playbook/standards/skill-management.md)
owns the install/update workflow.

### The user's standards

General standards live in
[`~/workspace/dev-playbook/standards/`](~/workspace/dev-playbook/standards/)
(repo documentation, testing conventions, skill authoring, skill
management, Python conventions). Spec-driven-development standards live
separately in
[`~/workspace/dev-playbook/sdd-standards/`](~/workspace/dev-playbook/sdd-standards/).
Cross-references are linted by `tools/bin/ref-check --all`. Read those
for the current rules; #15 will amend them.

### The user's authored skills

Authored skills live in `dotfiles/.claude/skills/`. Two are
specifically called out by later tasks: the **sdd-\*** family
(`sdd-design`, `sdd-func-reqs`, `sdd-green`, `sdd-red`, `sdd-review`)
are content-audit targets in #25, and `skill-creator` gets compared
against Matt's `write-a-skill` in #25.

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

Final picks (9 adopt, 3 reject — accounts for all 12):

- **Adopt:** `tdd`, `caveman`, `grill-me`, `grill-with-docs`,
  `improve-codebase-architecture`, `zoom-out`, `to-issues`, `triage`,
  `setup-matt-pocock-skills`.
- **Reject:** `diagnose` ("too much"), `write-a-skill` (rejected as a
  skill, but feeds the skill-creator comparison in #25), `to-prd`
  (overlaps and conflicts with our SDD spec layer; see #15 and
  ADR-0006 once written).

Notes on classification:
- `setup-matt-pocock-skills` is a one-time per-repo bootstrap, not a
  runtime skill. Frontmatter has `disable-model-invocation: true`. It
  scaffolds the per-repo files Matt's engineering skills read from.
- The decision to adopt the engineering picks was made in advance:
  `tdd`, `grill-with-docs`, `improve-codebase-architecture`,
  `to-issues`, and `triage` all read from Matt's domain docs / backlog
  conventions, and the user does not want to run them in degraded mode
  without those conventions in place. So adopting them implies
  adopting the conventions — see #15.

## Tasks

Live status lives in the Claude Code task tracker. The detail below
carries the reasoning. Sections are in the recommended execution order.

### #15 Adopt Matt's repo conventions

**Status:** decisions logged; standards rewrite (steps 1-4) done; steps 5-10 pending.

**Top-level decision:** adopt Matt's standard, with one rejection
(PRD) and one adaptation (GitHub-only issue tracker). The user does
not want to run Matt's skills in degraded mode, so the conventions
those skills assume are coming with them — except where they conflict
with workspace conventions we've committed to (notably SDD).

#### Per-convention decisions

| Convention | Decision | Notes |
|---|---|---|
| `CONTEXT.md` (domain glossary at repo root) | Adopt | Lazy creation by `/grill-with-docs`; don't backfill upfront |
| `CONTEXT-MAP.md` (multi-context monorepos) | Adopt as optional | dev-playbook stays single-context for now |
| `docs/adr/` directory | Adopt | Plus our existing `docs/adr/README.md` index requirement |
| ADR file naming | Adapt — rename | Existing `001-005` → `0001-0005` to match Matt's 4-digit convention |
| ADR template | Adopt | 1-3 sentences; optional Status / Considered Options / Consequences |
| ADR offer-criteria gate | Adopt | All three of: hard-to-reverse + surprising + real trade-off |
| `docs/agents/` directory | Adopt | Per-repo agent config (issue-tracker, triage-labels, domain); distinct from workspace `standards/` |
| `## Agent skills` block in `CLAUDE.md` | Adopt | Required when Matt's skills are configured for the repo |
| Issue tracker backend | Adapt — GitHub-only | Drop `.scratch/` and "other" options; `setup-matt-pocock-skills` supports this as a built-in choice |
| Triage label vocabulary (5 state + 2 category) | Adopt | Lives in new file `standards/issue-management.md` (vocabulary section) |
| PRD format and `/to-prd` workflow | **Reject** | Overlaps with SDD spec; uninstall `/to-prd`; documented retrospectively in ADR-0006 alongside the broader Matt-conventions adoption |
| Vertical-slice issue breakdown (tracer bullets, HITL/AFK, blocked-by) | Adopt | Lives in `standards/issue-management.md` (slice section); single-file consolidation with triage labels and state machine |
| `/tdd` testing conventions | Keep ours authoritative | Don't fork `/tdd`; one-line cross-reference in our standard |
| Architecture vocabulary (Module/Interface/Depth/Seam/Adapter/Leverage/Locality) | Adopt implicitly | No standards change — vocabulary used in `improve-codebase-architecture` output |

#### Forking decision

Do not fork any of Matt's skills. The only adaptation (GitHub-only)
is supported by `setup-matt-pocock-skills` as a built-in choice.
Revisit forking only if specific friction surfaces post-install.

#### Existing supersets preserved

- **`BUSINESS_CONTEXT.md`** — distinct scope from `CONTEXT.md`. Both
  can coexist.
- **`ROADMAP.md`** — strategic goals; no Matt equivalent.
- **`specs/` and `sdd-standards/`** — formal SDD requirements layer.
  Matt rejects SDD; we keep it. The PRD rejection follows from this.
- **`standards/testing-conventions.md`** — superset of `/tdd`; stays
  authoritative.
- **`tools/bin/ref-check`** — link linter for `~/workspace/...`
  cross-references.
- **GNU Stow + dotfiles workflow** — orthogonal; unaffected.

#### Execution checklist

1. ✅ Amend
   [Repo documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md).
2. ✅ Create
   [Issue management standard](~/workspace/dev-playbook/standards/issue-management.md).
3. ✅ Cross-reference
   [Testing conventions](~/workspace/dev-playbook/standards/testing-conventions.md)
   → `/tdd`.
4. ✅ Update
   [standards index](~/workspace/dev-playbook/standards/README.md).
5. Rename `docs/adr/00N-*.md` → `docs/adr/000N-*.md` for the existing
   five ADRs; update the index in `docs/adr/README.md`.
6. Install `setup-matt-pocock-skills`
   (`npx skills@latest add mattpocock/skills --skill setup-matt-pocock-skills -g -y`)
   and run it against `~/workspace/dev-playbook/` itself:
   single-context, GitHub backend, default labels. Scaffolds
   `docs/agents/{issue-tracker,triage-labels,domain}.md` and the
   `## Agent skills` block in `CLAUDE.md`. The remaining 8 skills are
   installed later in #23.
7. Edit the generated `docs/agents/issue-tracker.md` to drop the
   "and PRDs" clause from Matt's seed (we don't use PRDs).
8. Defer `CONTEXT.md` creation — let `/grill-with-docs` create it
   lazily on first ambiguity.
9. Run `tools/bin/ref-check --all`. The `grill-with-docs/ADR-FORMAT.md`
   link in `repo-documentation.md` will still be broken at this point;
   it resolves once #23 installs the skill.
10. Write `docs/adr/0006-adopt-matt-pocock-conventions.md`
    retrospectively, capturing both (a) the broad decision to adopt
    Matt's conventions and (b) the rejection of the PRD workflow.
    Interview the user for reasons before drafting — do not pre-fill
    the rationale. Split into two ADRs only if the reasoning diverges
    enough to warrant it.

### #23 Install chosen Matt skills

**Status:** pending — depends on #15 landing.

`setup-matt-pocock-skills` is already installed during #15 step 6.
This task installs the remaining 8 adopted skills: `tdd`, `caveman`,
`grill-me`, `grill-with-docs`, `improve-codebase-architecture`,
`zoom-out`, `to-issues`, `triage`. One invocation per skill:
`npx skills@latest add mattpocock/skills --skill <name> -g -y`.
Skip `to-prd` (rejected — see ADR-0006). The CLI writes to
`~/.agents/skills/<name>/`, which Stow-folds into
`dotfiles/.agents/skills/`. The lock file at
`dotfiles/.agents/.skill-lock.json` updates in place. Review the diff,
then commit.

No forking required (decided in #15). If post-install friction
surfaces and we later fork a skill, do it in the dotfiles working
tree and document the divergence so future `skills update` runs don't
silently overwrite our edits.

### #25 Refresh authored skills

**Status:** partially done — cross-reference sweep complete; content
audit pending.

Audit user-authored skills in `dotfiles/.claude/skills/` against
current practice and external inputs.

**sdd-\* skills.** `sdd-{design,red,green,review,func-reqs}`. Inputs:

- [SDD standards index](~/workspace/dev-playbook/sdd-standards/README.md)
  — current standards.
- `~/workspace/dev-playbook/sdd-standards/lessons.md` — lessons logged
  during the spec-tools work.
- Recent spec-tools build at `~/workspace/dev-playbook/spec-tools/` —
  shows current SDD practice in action.
- Matt's `/tdd` skill (post-install) — reconcile any testing-convention
  conflicts identified in #15.

Identify what's stale vs. still load-bearing. Rewrite as needed.

**`skill-creator`.** `dotfiles/.claude/skills/skill-creator/`. Compare
against Matt's `write-a-skill` (rejected for direct adoption but worth
studying). Pull ideas about structure, progressive disclosure, bundled
resources, and any other patterns Matt uses that our skill doesn't.
Update `skill-creator` with what fits.

### #28 Update cookiecutter project template

**Status:** pending — depends on #15 landing.

The cookiecutter at
[`project-template/`](~/workspace/dev-playbook/project-template/)
generates new repos. Once #15 finalises the conventions, the template
must propagate them so newly-generated repos start in compliance.

Concrete updates to
`project-template/{{ cookiecutter.project_slug }}/`:

- `CLAUDE.md` — add the `## Agent skills` block pointing at
  `docs/agents/*.md`.
- `docs/agents/` seed directory — bundle `issue-tracker.md` (GitHub
  variant, with the "and PRDs" clause dropped), `triage-labels.md`
  (default 5+2 vocabulary), and `domain.md` (single-context default,
  copied from Matt's seed).
- `docs/adr/` seed directory — empty except for `README.md` indexing
  no ADRs yet.
- Don't seed `CONTEXT.md` — keep lazy-creation discipline.
- Verify `cookiecutter` still generates a valid repo end-to-end after
  the changes.

Cross-check the source files used to seed: they should ultimately
match the canonical seeds bundled inside
`dotfiles/.agents/skills/setup-matt-pocock-skills/` (post-#23) so the
template doesn't drift from what `setup-matt-pocock-skills` would
write into a fresh repo.

## Working with this file

- Update the per-task sections as decisions land. The task tracker
  carries status; the file carries the reasoning.
- When a sub-instance of an existing theme surfaces (e.g. another
  Matt convention to evaluate), add it to the relevant section's
  table or list. Don't spawn a new top-level task for every example.
- Keep the cold-start summary at the top truthful as the project
  evolves. A new agent should be able to read top-to-bottom and pick
  up where things left off.
- Delete this file once #15, #23, #25, and #28 are all complete.
