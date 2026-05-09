# ADR-0008: Decline Superpowers, Catalog Techniques

**Date:** 2026-05-08
**Status:** Accepted

## Context

Superpowers (https://github.com/obra/superpowers) is an agentic skills
framework by Jesse Vincent, distributed as plugins for seven coding-
agent harnesses (Claude Code, Codex CLI/App, Cursor, Gemini CLI,
OpenCode, Factory Droid, GitHub Copilot CLI). Several internet
luminaries in agentic-AI and data-science have publicly endorsed it,
which prompted this audit. Working audit notes are in
[docs/third-party-survey.md](~/workspace/dev-playbook/docs/third-party-survey.md).

**Superpowers has a ton of great stuff in it.** Roughly 10k lines of
markdown across 13 skills, plus a SessionStart bootstrap hook that
injects priming on every session. The audit found legitimate strengths:

- A SessionStart hook that injects priming on every session — a clever,
  harness-portable mechanism for forcing skill consultation.
- Skills written using research-backed persuasion techniques: Cialdini's
  seven principles plus Meincke et al. (2025), an N=28k experiment showing
  compliance jumps 33% → 72% with authority/commitment/scarcity framing.
- Adversarial pressure-testing methodology for skill prose, treating
  skills as code to be eval'd rather than docs to be written.
- A subagent-isolation-per-task pattern for context pollution prevention.
- Two-stage review (spec compliance, then code quality) for execution
  loops.
- Self-dogfooded — `docs/superpowers/specs/*` and `docs/superpowers/plans/*`
  show the maintainer building the framework with the framework.
- Cross-harness portability through per-harness plugin manifests.

The framework is well-engineered, opinionated, and clearly designed for
wholesale adoption. The audit's question is whether this workspace
should adopt it.

## Decision

**Decline Superpowers wholesale. Adopt nothing. Catalog techniques worth
remembering for future authored skills.**

### Why not wholesale

This workspace is already committing to and exploring two coherent
investments that Superpowers conflicts with:

- **spec-tools** (`~/workspace/spec-tools/`) — the workspace's
  EARS+OFT-grounded SDD layer with machine-validated traceability, the
  `Interface:` keyword for structural commitments, and `pytest-sdd` for
  collection-time validation. Superpowers' `brainstorming` and
  `writing-plans` produce prose specs and plans without traceability or
  machine validation. This is the same prose-spec category
  [ADR-0006](0006-adopt-matt-pocock-conventions.md) rejected for Matt
  Pocock's `/to-prd`. The reasoning applies identically.
- **Matt Pocock's conventions** (adopted in
  [ADR-0006](0006-adopt-matt-pocock-conventions.md)) — `/tdd`,
  `/to-issues`, `/triage`, the issue-tracker per-repo configuration, and
  the vertical-slice breakdown rules. Superpowers' `test-driven-development`
  competes directly with `/tdd` (canonicalized in ADR-0006), and
  Superpowers has no issue-tracker layer.

Superpowers asks for retiring both. The case for that exchange is not
made by anything in Superpowers.

### Why not piecemeal

Several Superpowers skills are real gap-fillers. The audit
seriously considered installing these as third-party dependencies via
the Vercel `skills` CLI (the same mechanism that handles the Pocock
skills). We declined.

**Piecemeal adoption opens a can of SpaghettiOs.**

- **Voice fragmentation.** Superpowers writes in a distinctive register —
  "your human partner," "Iron Law," "EXTREMELY-IMPORTANT" XML tags,
  Red Flags tables. Pocock's voice differs. The workspace's own SDD
  skills differ again. Mixing three voices in one toolbox makes agent
  behavior less predictable and harder to mentally model.
- **Cross-reference fragility.** Each Superpowers skill assumes the
  others are present (`systematic-debugging` references
  `superpowers:test-driven-development` and
  `superpowers:verification-before-completion`). Cherry-picking creates
  dead references that either mislead the agent or require fork-and-edit,
  which negates the dependency benefit.
- **Semantic drift on update.** `npx skills@latest update` advances the
  SHA pin, but the *meaning* of the skill is still authored by Jesse
  Vincent. A tightened phrase, a new Red Flag, a workflow restructure,
  and the agent's behavior shifts without the workspace authoring the
  change. SHA-pinning is a byte-level dependency mechanism; the concern
  is semantic-level drift, which it does not address.
- **No clean convention boundary.** Pocock's skills were adopted with
  their per-repo conventions (`docs/agents/issue-tracker.md`,
  `docs/agents/triage-labels.md`, `## Agent skills` block) — skills and
  conventions form one coherent integratable unit. Superpowers' skills
  do not decouple that way; the methodology *is* the convention.
  Importing parts means importing a worldview piecemeal.

### Generalizable rule

This is the second luminary pull this workspace has audited (Pocock,
now Superpowers). The pattern will recur. Promote the implicit rule
from ADR-0006 into an explicit workspace principle:

> **Adopt third-party skills only when their conventions integrate
> cleanly with existing canon. Otherwise harvest techniques into
> authored skills, not foreign skills into the toolbox.**

ADR-0006 implicitly applied this rule — Pocock's skills came with
per-repo configuration that complemented existing standards.
Superpowers' skills come with a methodology that competes with existing
canon. That asymmetry is the rule, generalized.

## Catalog of techniques worth remembering

Recorded here so the workspace does not lose track of these ideas, with
source pointers for re-reading. None of these are adopted as foreign
skills. If a specific gap becomes painful enough in real use, author a
workspace-native skill that incorporates the technique in the
workspace's voice.

| Technique | Source | What's worth keeping |
|---|---|---|
| Cialdini-grounded persuasion principles for skill prose | [`writing-skills/persuasion-principles.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/persuasion-principles.md) | Authority + Commitment + Social Proof for discipline-enforcing skills; Liking and Reciprocity avoided. Citations: Cialdini (2021); Meincke et al. (2025). |
| "Red Flags" rationalization tables | Multiple Superpowers skills (e.g. `using-superpowers/SKILL.md`, `test-driven-development/SKILL.md`) | Two-column table naming the rationalization the agent would use to skip discipline, paired with the rule it violates. |
| Iron Law / Gate Function pattern | `verification-before-completion/SKILL.md`, `test-driven-development/SKILL.md` | Bright-line absolute rule with explicit anti-rationalization clauses ("violating the letter is violating the spirit"). |
| Adversarial pressure-testing methodology for skill evals | [`writing-skills/testing-skills-with-subagents.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/testing-skills-with-subagents.md), [`writing-skills/examples/CLAUDE_MD_TESTING.md`](https://github.com/obra/superpowers/blob/main/skills/writing-skills/examples/CLAUDE_MD_TESTING.md) | RED-GREEN-REFACTOR for skill prose itself. Run scenarios without the skill (watch agent fail), write the skill (watch agent comply), close loopholes. |
| SessionStart hook for cross-cutting priming | `hooks/session-start`, `hooks/hooks.json` | Inject prose into `additionalContext` at session start. Harness-portable across Claude Code, Cursor, Copilot CLI. |
| Subagent-isolation-per-task pattern | `subagent-driven-development/SKILL.md`, `subagent-driven-development/implementer-prompt.md` | Fresh subagent per task with curated context; controller never pollutes its context with implementation details. |
| Two-stage review (spec compliance → code quality) | `subagent-driven-development/spec-reviewer-prompt.md`, `subagent-driven-development/code-quality-reviewer-prompt.md` | Spec-compliance review (did you build the right thing?) before code-quality review (did you build it well?). Order matters; running quality first lets shippable-but-out-of-spec work pass. |

If any of these techniques would meaningfully improve the workspace's
existing SDD or Pocock-derived skills, the route is to author a
workspace-native skill in `dotfiles/.claude/skills/<name>/`, not to
install Superpowers content as a foreign skill.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Adopt Superpowers wholesale | Retires the spec-tools SDD layer and the Pocock `/tdd` canonicalization from ADR-0006. The case for that exchange is not made by anything in Superpowers. |
| Adopt three gap-filler skills as third-party dependencies (`requesting-code-review`, `verification-before-completion`, `systematic-debugging`) | Voice fragmentation, cross-reference fragility, semantic drift on update, no clean convention boundary. Piecemeal adoption opens a can of SpaghettiOs. |
| Copy skill prose into authored skills, citing the source | One-time copy that drifts from upstream as Superpowers updates. Worst of both worlds — neither tracked dependency nor independent authorship. |
| Install only `superpowers:writing-skills` for `persuasion-principles.md` | Importing an opinionated meta-bundle imports its worldview about how skills should be authored. The principles can be cited from the upstream URL without installation. |
| Adopt the SessionStart hook *technique* (not Superpowers content) for workspace-wide priming | Catalogued as a deferred follow-up. No concrete priming need has surfaced; if one does, that should be its own ADR. |
| Adopt the subagent-isolation pattern as an enhancement to `/sdd-implementation`'s chunk loop | Catalogued as a deferred follow-up. Requires real-use evidence that `/sdd-implementation` suffers from context pollution before reorganizing it. |

## Consequences

- No changes to `dotfiles/.agents/.skill-lock.json`. No new third-party
  skills installed.
- ADR-0008 stands as the workspace's documented position on Superpowers;
  future questions about it route here.
- New workspace principle ("Adopt third-party skills only when their
  conventions integrate cleanly with existing canon. Otherwise harvest
  techniques into authored skills, not foreign skills into the toolbox.")
  applies to future luminary-driven framework pulls. The same rule was
  re-applied to Pocock himself once spec-tools' growth changed the
  convention landscape; see
  [ADR-0009](0009-remove-pocock-direct-dependency.md).
- Open follow-ups (deliberately deferred):
  - SessionStart hook as a workspace-wide priming mechanism, if a
    concrete priming need surfaces.
  - Subagent-isolation pattern as a possible enhancement to
    `/sdd-implementation`, if real-use evidence shows context pollution
    in the existing chunk loop.
  - Citation of Cialdini and Meincke et al. in
    `standards/skill-conventions.md`, if persuasion-principle guidance
    becomes useful for future authored skills.
- The SDD-extension bet (from
  [ADR-0005](0005-workspace-sdd-standard.md), reaffirmed in
  [ADR-0006](0006-adopt-matt-pocock-conventions.md)) remains testable.
  If conventional prose-spec workflows like Superpowers' `brainstorming` +
  `writing-plans` outperform spec-tools' SDD layer in practice with
  current-state coding agents, this ADR's wholesale rejection should be
  revisited.
