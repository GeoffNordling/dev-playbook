---
name: sdd-design
description: Authors the project's design layer — `dsn` items that pin `Interface:` lines and design commitments — from approved functional requirements, then leaves the tree green and hands the issue off to spec review. Use when advancing a `phase:sdd-design` issue, when an SDD issue needs its design items written or revised, or when the agents dashboard launches the design phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Edit Write Skill(grill-with-docs) Skill(commit)
argument-hint: "<issue-number>"
---

# SDD Design

Author the project's design layer — `dsn` items pinning `Interface:` lines and design commitments — from approved functional requirements, then leave the tree green and hand the issue off to spec review. The interview is the value of this skill.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — the full `dsn` grammar, `Interface:` annotation idiom, coverage chain.
- [design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — what a `dsn` pins, and why design happens up front.
- [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

Then report: `READ: spec-standard.md, design-layer.md, lessons.md`. Proceed only after.

## 1. Load context

Issue number arrives as `$ARGUMENTS`. Work happens on the issue's branch.

- `gh issue view $ARGUMENTS` — the body is the contract.
- Approved requirements: `specs/functional_requirements.md` (or folder form). Without them, designing is premature — stop and surface that.
- Existing design: `specs/design.md` (or folder form).
- `docs/adr/README.md` — the ADR index; from its descriptions, read only the ADRs relevant to the area being designed.
- **Brownfield reconnaissance.** Read the existing code the area touches. For each new capability, work out whether it extends a module or introduces one, and what public surface each requirement implies.

## 2. Area discovery interview

Ask the user which design areas matter. Common areas:

- **Data shapes.** Fields and types on each proposed dataclass / exception.
- **API shape.** Public signatures, module structure.
- **Exception strategy.** Plain `ValueError` vs. structured types; raise-vs-return-as-data.
- **Naming.** Type and symbol names — each name's semantic load should read clearly.
- **CLI shape.** Subcommand dispatcher vs. independent scripts; flag conventions.
- **Cross-cutting infrastructure.** Loaders, central types, dispatchers.
- **Module decomposition.** One module per `feat` vs. grouping; where new modules sit.

Surface your read of which areas look load-bearing and why; ask the user to confirm, add, or drop.

## 3. Intent interview

Invoke /grill-with-docs to sharpen design intent and public-boundary terminology against the codebase, capturing significant decisions as ADRs as they crystallize. Where an area has discrete choices — interface shape, exception strategy, naming — surface them with AskUserQuestion, each option carrying a recommendation and the reason it is recommended.

## 4. Plan synthesis

Present a plan for explicit approval, then wait:

- **Scope.** Which requirements this pass covers, and which `dsn` satisfies each.
- **Skeletons.** Per planned `dsn`: id + heading + role + proposed `Interface:` line(s) + `Covers:` + `Needs:` + `Depends:`. No prose yet.
- **Decisions made.** Type names, exception strategy, CLI shape, as resolved by interview.
- **Decisions deferred.** Anything still open.

## 5. Drafting

The skeleton holds — `Interface:`, `Covers:`, `Needs:`, `Depends:` from the plan are locked; add prose now.

- When shaping public surfaces, first read [module design](~/workspace/dev-playbook/standards/module-design.md) — small interface, deep implementation; accept dependencies, return results; keep the surface small.
- **Minimum viable shape.** Don't add a field, method, or type unless you can name its caller. Prefer two fields over four.
- **Don't pin implementation.** Output format, packaging, internal walk shape, file paths — leave to the build phase unless a `req` constrains them.
- Write each `dsn` per the spec standard; `Interface:` lines fully qualify symbol paths and follow its annotation idiom.
- **Non-mandatory inclusion is a commitment.** A `SHOULD` / `MAY` you design in is one you intend to deliver.
- Keep `Rationale:` and `Comment:` non-prescriptive per the spec standard; a claim that wants to prescribe belongs in `Description:`.
- Reference relevant ADRs rather than re-explaining them.
- **Keep the region work-in-progress.** Your `dsn`s reach no verifiers yet, so their region must carry `WIP: true` (§2.10) or completeness fails. Check the `feat` they cover: if it already bears the marker (requirements left it), leave it; if it does not — design may be the first phase to run on this region — mark the `feat` `WIP: true` yourself. The marker exempts the `feat` and everything beneath it; build removes it once verifiers land.

## 6. Review pass

Re-read each new `dsn` and iterate until clean:

- [ ] Chains up to a `req` via `Covers:` (or is a root); `Needs:` declares verification.
- [ ] `Interface:` annotations and obligation prose conform to the spec standard.
- [ ] `Rationale:` / `Comment:` stay non-prescriptive.
- [ ] Honors the section 5 principles.

## 7. Close the phase

When the user approves and the rubric passes:

1. **Final check sweep — leave the tree green.** Run the project's tests, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). If a command is undefined, note the absence and continue; if a defined command fails, stop and surface it.
2. Run /commit.
3. Advance the issue to the spec-review phase — move its label from this node to the next:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase:sdd-design" --add-label "phase:sdd-agent-spec-review"
   ```
4. Stop. Report that design is complete and the issue now sits at `phase:sdd-agent-spec-review`. Do not begin the review — the human launches /sdd-agent-spec-review from the dashboard when ready.
