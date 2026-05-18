# Issue Workflow Reorganization

## Context

The workflow taking an idea from conception to merged PR currently spans:

- Two standards: `issue-management.md` (triage roles, agent briefs, vertical-slice rules) and `issue-implementation.md` (branch / worktree / PR mechanics).
- Five skills: `/triage`, `/to-issues`, `/sdd-requirements`, `/sdd-design`, `/sdd-implementation`.
- A 5-state-role label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) plus 2 category roles (`bug`, `enhancement`).

Two frictions surfaced from real use:

**Phase invisibility.** A `ready-for-agent` issue gives no signal of which SDD phase it is currently in. An agent picking up issue #N with partial work has to infer state from the filesystem (which spec files exist, what is in `tests/`) or by reading free-form session-handoff comments. Phase belongs on the issue, visible at a glance.

**Solo-developer ceremony.** The 5-state vocabulary was authored when the workflow modelled multi-person collaboration (maintainer + reporter + AFK agent). For a solo developer who is both creator and triager, `needs-info` / `ready-for-agent` / `ready-for-human` collapse to a single decision made at issue creation. The separate `/triage` step is a pass-through.

## Decision

Reorganize around a phase-on-issue label scheme, collapse triage and creation into a single skill, and consolidate the workflow standards.

### Label scheme

Three orthogonal label tracks, plus `wontfix` for declined issues:

| Track | Values | Meaning |
|---|---|---|
| Category | `bug`, `enhancement` | What kind of work it is |
| Mode | `sdd` (presence) | Whether SDD ceremony applies |
| Phase | `phase/requirements`, `phase/design`, `phase/build`, `phase/review` | Where in the journey |

Issues are born with all three tracks set. The phase advances as work progresses; the dispatcher reads the phase label to decide which skill to run.

### Skills — adds, renames, deletions

**Add.**

- `/intake` — single entry point for idea-to-issue(s). Decides category / sdd / phase, writes the brief into the issue body, invokes `/grill-with-docs` when the idea is fuzzy. Auto-bootstraps repo labels via `tools/bin/bootstrap-labels`.
- `/sdd <issue>` — dispatcher. Refuses if the `sdd` label is absent. Reads the `phase/*` label, invokes the matching phase skill, bumps the label on success.

**Rename.**

- `sdd-implementation` → `sdd-tdd`

`sdd-requirements` keeps its name — parallel to `sdd-design`, and matches the directory it writes to (`specs/functional_requirements/`).

**Delete.**

- `/triage` — absorbed into `/intake`.
- `/to-issues` — absorbed into `/intake` (one skill handles both 1-issue and N-issue creation).

### Standards consolidation

- New: `standards/workflow.md` — single consolidated standard covering label scheme, `/intake` flow, `/sdd` dispatcher, branch / worktree convention, PR mechanics, cleanup.
- Delete: `standards/issue-management.md` and `standards/issue-implementation.md` — content moved into `workflow.md`.
- Each SDD skill drops its duplicated First-steps prelude and links to `workflow.md`.

### Closing review pass

`sdd-requirements` and `sdd-design` add a closing review pass — a fixed rubric the agent runs before declaring the phase done. Absorbs `lessons.md §7` (which is removed in `spec-tools`).

### AgentReview as final check

`/sdd-agentreviews` is reframed from a periodic project-wide audit into the final-check step of `sdd-tdd`. `sdd-tdd` computes the in-scope item IDs from the branch diff (`git diff main...HEAD -- specs/` filtered to items carrying `AgentReview:`) and passes them as an explicit list to the skill. The skill itself remains callable directly when the user wants a different scope. The `Maintenance routines` section in the workflow standard is dropped — the only entry was `/sdd-agentreviews` and it is no longer periodic.

### Tooling

- New: `tools/bin/bootstrap-labels` — idempotent script that creates the workflow's label scheme in a repo. Auto-invoked by `/intake`.
- `dotfiles/bin/gh-show` — documented in `tools/README.md` (was previously undocumented).

### Brief is the body

The agent brief is no longer a separate `## Agent Brief` comment posted at a state transition. The issue body itself IS the brief. One contract, no precedence ambiguity between body and comment.

### Worktree resolution

The dispatcher resolves the worktree by glob `.claude/worktrees/<N>-*` from the issue number. Exactly one match → enter. Zero → create. Multiple → error. No metadata about the worktree lives on the issue; the issue number is the unique key, the filesystem holds the rest.

### Open question

Where `/improve-codebase-architecture` fits in the SDD workflow beyond `sdd-design`'s explicit escape hatch is left to discover with use. It is not invoked from `sdd-tdd` — refactor pressure that crosses a committed `Interface:` routes through spec amendment back to `sdd-design`.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Keep `/triage` as a separate skill | Solo creator + solo triager makes the boundary artificial. The skill content is purely classification, which `/intake` does in one step. |
| Single `/intake-then-build` skill that runs every phase sequentially | Each phase is a distinct interaction mode (interview-heavy / reconnaissance-heavy / TDD-loop) and benefits from a fresh agent context. Merging blurs that. The dispatcher pattern keeps skills focused while presenting a single user-facing command. |
| Phase as issue body section (e.g. `## Phase: design`) instead of label | Labels are filterable (`gh issue list --label phase/requirements`); body sections are not. Labels are 1-line edits; body edits are diff-prone. |
| Phase as comment marker | Comments accumulate; the latest phase marker has to be searched for. Labels are a single source of truth. |
| Carry the AFK / HITL distinction forward | Solo developer is currently always HITL. The distinction can be re-introduced when AFK agents land — re-add the label, re-add a `/triage` step if needed. Not pre-specifying. |
| Inline `gh label create …` in `workflow.md` instead of a script | Lives in agent context every time `workflow.md` loads. A script lives outside context, runs idempotently, and lets `/intake` auto-bootstrap missing labels. |
| Rename phase label `phase/build` → `phase/tdd` to match the skill | Phase describes the journey state (we are building); the skill describes the method (TDD). The mismatch is intentional and one-line documented. |

## Consequences

- Two standards files removed (`issue-management.md`, `issue-implementation.md`); one added (`workflow.md`).
- Two skills removed (`triage`, `to-issues`); two added (`intake`, `sdd` dispatcher); one renamed (`sdd-implementation` → `sdd-tdd`).
- Three skills edited (`sdd-requirements`, `sdd-design`, `sdd-tdd`) to drop duplicated preludes, link to `workflow.md`, and (for requirements/design) add a closing review pass.
- `lessons.md §7` removed in `spec-tools` (separate commit) — content absorbed into `sdd-requirements` and `sdd-design`.
- New label vocabulary in target repos: `bug`, `enhancement`, `sdd`, `phase/{requirements,design,build,review}`, `wontfix`. Bootstrap is automatic on first `/intake` invocation per repo.
- Skill name `sdd-tdd` describes the methodology; phase label `phase/build` describes the journey state. The naming mismatch is accepted.
- Where `/improve-codebase-architecture` fits in the SDD workflow remains an open question, to be discovered with use rather than pre-specified.
