# Remove Pocock Direct Dependency, Absorb Conventions, Lift Engineering Skills

## Context

[ADR-0001](0001-adopt-matt-pocock-conventions.md) adopted Matt Pocock's
conventions and skills wholesale on the principle that running the engineering
skills (`/tdd`, `/triage`, `/to-issues`, `/grill-with-docs`,
`/improve-codebase-architecture`) without their per-repo configuration produces
degraded output — so adopt the conventions the skills assume, not just the
skills themselves. The rationale held when the workspace's own conventions were
thin and Pocock's filled gaps cleanly.

[ADR-0003](0003-decline-superpowers.md) generalized that rationale into an
explicit workspace principle:

> **Adopt third-party skills only when their conventions integrate cleanly
> with existing canon. Otherwise harvest techniques into authored skills,
> not foreign skills into the toolbox.**

ADR-0003 noted that the rule was *implicitly* applied in ADR-0001 because
Pocock's per-repo configuration complemented existing standards at the time.

The landscape has changed since ADR-0001:

- **`spec-tools` moved to its own repo** (`~/workspace/spec-tools/`) and grew
  per-repo conventions of its own — `sdd-standards/` covering specs, design,
  and test-coverage rules; `pytest-sdd` for collection-time validation. The
  workspace canon is no longer thin.
- **Pocock's conventions began overlapping the new canon** in places where
  they had previously filled empty space — the architecture vocabulary
  (`improve-codebase-architecture/LANGUAGE.md`) overlaps `sdd-design`'s
  module-shaping discipline; the triage / agent-brief / vertical-slice content
  overlaps the issue-implementation workflow; the `docs/agents/` per-repo
  config layer is a parallel mechanism for things now better served from
  workspace standards.

The "complements existing canon" condition from ADR-0003 no longer holds for
the load-bearing skills. The principle ADR-0003 articulated, applied honestly
to the changed landscape, points to cutting the direct dependency.

## Decision

**Cut the Pocock direct dependency.** Absorb the load-bearing ideas into
authored standards. Lift the load-bearing engineering skills into authored
skill bundles in `dotfiles/.claude/skills/`. Drop the bootstrapper and
redundant-runtime skills entirely. Keep two tiny utility skills as direct
Vercel dependencies because their lift cost ≈ drop cost.

### Drop (no replacement)

- `/setup-matt-pocock-skills` — its job (scaffolding `docs/agents/` and the
  `## Agent skills` block) is gone.
- `/tdd` — covered by `/sdd-implementation` for spec-bound work; exploratory
  TDD outside SDD is encoded in `standards/testing-conventions.md`. Author
  later if a real gap surfaces.
- `/grill-me` — redundant with `/grill-with-docs`.

### Lift (authored skill bundles)

Body prose preserved verbatim from the originals; references rewired to
absorbed standards; `model: opus`, `effort: xhigh`, explicit
`disable-model-invocation`, `# H1` titles per `standards/skill-conventions.md`.

- `/grill-with-docs` → `dotfiles/.claude/skills/grill-with-docs/`. References
  absorbed into `standards/repo-documentation.md` (CONTEXT.md format) and
  `standards/adr-conventions.md` (template, offer-gate).
- `/triage` → `dotfiles/.claude/skills/triage/`. References absorbed into
  `standards/issue-management.md` (triage roles, agent briefs).
  `OUT-OF-SCOPE.md` and the `.out-of-scope/` knowledge-base content dropped.
- `/to-issues` → `dotfiles/.claude/skills/to-issues/`. References absorbed
  into `standards/issue-management.md` (vertical-slice rules, issue body
  template).
- `/improve-codebase-architecture` →
  `dotfiles/.claude/skills/improve-codebase-architecture/`. References
  absorbed into `standards/architecture-vocabulary.md`,
  `standards/module-design.md`, `standards/dependency-taxonomy.md`. Two
  workflow refs kept in `references/`: `DEEPENING-WORKFLOW.md` (testing
  strategy: replace, don't layer) and `DESIGN-IT-TWICE.md` (parallel-design
  sub-agent pattern). Both are skill workflow, not standards.

### Keep as direct Vercel dependency

`/zoom-out` and `/caveman` — tiny one-paragraph utility skills, non-load-
bearing, low semantic-drift risk. Lift cost ≈ drop cost; chosen as direct
deps for low overhead. They remain installed via `npx skills@latest` and
mirrored into `dotfiles/.claude/skills/` by `dotfiles/bin/sync-dotfiles.sh`.

### Authored standards created or rewritten

- New: `standards/architecture-vocabulary.md` (Module / Interface /
  Implementation / Depth / Seam / Adapter / Leverage / Locality, verbatim
  from `improve-codebase-architecture/LANGUAGE.md`).
- New: `standards/module-design.md` (deep-module principle and
  designing-for-testability rules).
- New: `standards/dependency-taxonomy.md` (four dependency categories +
  seam discipline).
- New: `standards/adr-conventions.md` (offer-gate, template, optional
  sections, 4-digit numbering).
- Rewritten: `standards/issue-management.md` from pointer-file to authored
  content (5-role vocabulary, agent-brief template, vertical-slice rules,
  issue body template, GitHub-only conventions).
- Updated: `standards/repo-documentation.md` (absorb CONTEXT.md format;
  pointer to `adr-conventions.md`; drop `docs/agents/` row; drop multi-context
  `CONTEXT-MAP.md` framing).
- Updated: `standards/testing-conventions.md` (drop `/tdd` runtime-companion
  pointer).
- Updated: `standards/skill-management.md` (drop the Pocock-vs-Superpowers
  anecdote paragraph; rule and failure-modes paragraph kept).

### Authored skills rewired

- `/sdd-design` — `tdd/{deep-modules,interface-design}.md` references →
  `standards/module-design.md`. `/grill-me` invocation line dropped.
- `/sdd-implementation` — `tdd/{tests,mocking}.md` references →
  `standards/testing-conventions.md`. `tdd/refactoring.md` reference replaced
  with the inline 6-bullet refactor catalogue (lifted verbatim, since the
  catalogue is post-green workflow rather than a convention that fits any
  standard).
- `/sdd-requirements` — `/grill-me` invocation line dropped.

### Per-repo Pocock content removed from this repo

- `docs/agents/{issue-tracker,triage-labels,domain}.md` — deleted.
- `## Agent skills` block in root `CLAUDE.md` — deleted.

The single-context `CONTEXT.md` + `docs/adr/` pattern at the repo root
remains, codified in `standards/repo-documentation.md`. The multi-context
`CONTEXT-MAP.md` variant is dropped — single-context is the only supported
shape going forward.

## Alternatives considered

| Alternative | Why rejected |
|---|---|
| Keep the wholesale Pocock dependency from ADR-0001 | Honest application of the [ADR-0003](0003-decline-superpowers.md) rule says the "complements existing canon" condition no longer holds; the dependency is now competing rather than complementing. |
| Lift only some skills, keep others as direct dependencies | All four load-bearing skills overlap with workspace standards in the same way; halfway state would carry the worst of both — partial dependency for skills that no longer complement, no clean ownership of the conventions they rely on. |
| Keep `/zoom-out` and `/caveman` as authored bundles too | These are tiny utility skills with negligible semantic-drift risk. Authoring them adds maintenance for no real benefit; the Vercel install path handles them adequately. |
| Lift the supplementary reference files (`AGENT-BRIEF.md`, `OUT-OF-SCOPE.md`, `CONTEXT-FORMAT.md`, `ADR-FORMAT.md`) into the lifted skill bundles | Standards are the single source of truth. Duplicating reference material into skill bundles invites drift between the standard and the bundle copy. The lifted skills point at the standards directly. |
| Keep `.out-of-scope/` knowledge-base mechanism | No real-use evidence the mechanism earns its complexity; closing a `wontfix` enhancement with a comment captures the same information without the parallel filesystem. Drop it; revisit if the lack becomes painful. |
| Keep multi-context `CONTEXT-MAP.md` framing as an option | No workspace repo has used it. Single-context covers every actual use case. Carrying the multi-context option adds prose without earning its keep. |
| Fork Pocock's repo and maintain a workspace branch | More overhead than authoring, less control than authoring. Authoring captures only what's load-bearing in the workspace's own voice. |

## Consequences

- `dotfiles/.agents/.skill-lock.json` shrinks: `setup-matt-pocock-skills`,
  `tdd`, `grill-me`, `grill-with-docs`, `triage`, `to-issues`,
  `improve-codebase-architecture` removed via
  `npx skills@latest remove <name> -g`. `zoom-out` and `caveman` retained.
- Four authored skill bundles land in `dotfiles/.claude/skills/`, with body
  prose preserved verbatim from the upstream originals (load-bearing for
  `/sdd-design` and `/sdd-implementation` via the rewired references).
- Six standards files are added or rewritten; three existing standards
  updated; one repo file (`CLAUDE.md`) and one repo directory
  (`docs/agents/`) removed.
- ADR-0001's `Status` is updated to `Superseded by ADR-0004 in part` —
  conventions like 4-digit ADR numbering remain. The body of ADR-0001 is
  unchanged (historical record).
- ADR-0003's Consequences are extended with a pointer back to this ADR,
  noting the rule's re-application to Pocock himself.
- Future luminary-driven framework pulls route through the same rule
  ([ADR-0003](0003-decline-superpowers.md)). Pocock is now the worked
  example of the rule's *re*-application: a dependency that was once
  complementary can become competing as the workspace's own canon grows.
- The soft cost of carrying a foreign voice inside the authored skill
  bundles (the body prose is Pocock's, in his register) is accepted in
  exchange for not having to author the four bundles from scratch.
  Revisit if the voice mismatch becomes load-bearing in real use.

## Addendum — 2026-05-18

The "Per-repo Pocock content removed from this repo" cleanup above scoped
to dev-playbook. When `spec-tools` was scaffolded under the same era's
conventions it carried its own `docs/agents/{issue-tracker,domain}.md`
(no `triage-labels.md`), which persisted unnoticed until surfaced by
issue #35.

Audit and disposition:

- **`issue-tracker.md`** — Pocock's tracker-abstraction layer ("when a
  skill says 'publish to the issue tracker', create a GitHub issue").
  Obsolete; the workspace declares GitHub Issues as the sole tracker in
  [workflow.md](~/workspace/dev-playbook/standards/workflow.md). Deleted
  with no migration.
- **`domain.md`** — five agent-discipline rules (read `CONTEXT.md` and
  relevant ADRs before exploring; proceed silently on missing optional
  docs; use glossary vocabulary in outputs; explicit disposition for
  off-glossary concepts; flag ADR conflicts with template). All five
  were absent from the workspace canon at the time of this ADR. Absorbed
  into the CLAUDE.md Baseline as a new `## Domain awareness` section in
  [repo-documentation.md](~/workspace/dev-playbook/standards/repo-documentation.md),
  then inlined into dev-playbook's and spec-tools' root `CLAUDE.md`. File
  deleted from spec-tools.

`docs/agents/` is now empty across the workspace. The standard remains
silent on the directory — it was never listed in the Files table; the
silence is the answer.
