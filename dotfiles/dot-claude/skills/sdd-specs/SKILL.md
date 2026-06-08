---
name: sdd-specs
description: Authors a project's spec — its `feat`, `req`, and `dsn` items — as one hierarchy through a structured interview, then leaves the tree green and advances the issue to spec review. Use when the agents dashboard launches the spec phase.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# SDD Specs

Author a project's spec as one interdependent hierarchy — `feat` (high-level capability), `req` (functional requirement), and `dsn` (design item pinning `Interface:` lines and design commitments) — through a structured interview, then leave the tree green and hand the issue off to spec review. The interview is the value of this skill.

The three levels are one graph, not two passes. A `req` and the `dsn` that designs it are decided together; a sharper name or shape at one level is free to cascade to its neighbours — rename a `req` and update the `dsn` that covers it in the same breath, with the user's agreement. Move between levels as the conversation demands: establish a capability before pinning its interface, but revisit either when the other sharpens it. What stays distinct is the *altitude* — a `req` says what holds, a `dsn` says how — not the moment you think about each.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — the full `feat`/`req`/`dsn` grammar, EARS templates, `Interface:` annotation idiom, obligation vocabulary, coverage chain.
- [design layer](~/workspace/spec-tools/sdd-standards/design-layer.md) — what a `dsn` pins, and why design happens up front.
- [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

Then report: `READ: spec-standard.md, design-layer.md, lessons.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** If the session is already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`), proceed. If the worktree exists but the session isn't in it, re-enter it: `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If neither the worktree nor the branch `issue-<issue>` exists yet — this is the issue's first node — create it: confirm local `main` is current with origin (a check, not a pull: compare `git rev-parse origin/main` to `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`; if they differ, tell the user to pull `main` and stop), then `EnterWorktree(name=issue-<issue>)` and `git branch -m worktree-issue-<issue> issue-<issue>`. If the branch exists but the worktree is gone, the issue's work was lost — tell the user and stop.

- `gh issue view <issue>` — the body is the contract.
- Existing specs: `specs/functional_requirements/` and `specs/design/`.
- `CONTEXT.md` for domain vocabulary, if present.
- `docs/adr/README.md` — the ADR index; from its descriptions, read only the ADRs relevant to the area.
- **Brownfield reconnaissance.** Read the existing code the area touches. For each new capability, work out whether it extends a module or introduces one, and what public surface each requirement implies.

## 2. Area discovery interview

Ask the user which areas matter — behavior and design both. Start small:

- **Success path.** The headline behavior the `feat` exists for.
- **Edge / error behavior.** What counts as malformed; raise vs. return-as-data; what is silently accepted.
- **Scope boundary.** What is explicitly out of scope for this `feat`.
- **Data + API shape.** Fields and types on each proposed dataclass / exception; public signatures and module structure.
- **Naming.** Type and symbol names — each name's semantic load should read clearly.
- **Cross-cutting infrastructure.** Loaders, central types, dispatchers, CLI shape.
- **Module decomposition.** One module per `feat` vs. grouping; where new modules sit.

Add areas as they surface. Surface your read of which areas look load-bearing and why; ask the user to confirm, add, or drop.

## 3. Intent interview

Invoke /grill-with-docs to reach shared understanding of the flagged areas — behavioral intent and public-boundary terminology both — challenging fuzzy terms against `CONTEXT.md`, cross-referencing the code, and recording resolved domain terms and decisions in `CONTEXT.md` / ADRs as they crystallize.

Where an area has discrete options — a requirement's edge-case treatment, an interface shape, an exception strategy, a name — present them as **compact, self-contained handles** the user can weigh at a glance: each candidate item shown by id + heading + a one-line gist, never its full prose, and grouped into the `feat → req → dsn` hierarchy they form (indented along `Covers:`) so their mutual support is visible. Each option carries a recommendation and the reason it is recommended.

## 4. Plan synthesis

Present a plan for explicit approval, then wait:

- **Scope.** Which behaviors and design commitments this pass captures, and which `req` / `dsn` covers each.
- **Skeletons.** The planned items as a hierarchy — each `feat` / `req` / `dsn` a compact handle (id + heading + role + `Covers:` + `Needs:`; a `dsn` adds its `Interface:` line(s) + `Depends:`), indented along `Covers:` so the support structure reads at a glance. No `Description:` prose yet.
- **Decisions made.** Obligation level, granularity, edge-case treatment, type names, exception strategy, CLI shape, as resolved by interview.
- **Decisions deferred.** Anything still open.

## 5. Drafting

The skeleton holds — `Covers:`, `Needs:`, `Depends:`, and `Interface:` from the plan are locked; add prose now.

- **Minimum viable shape.** Each `req` commits to one checkable behavior; a clause earns its place only by adding a check. Don't add a field, method, or type unless you can name its caller — prefer two fields over four.
- **Hold the altitude.** A `req` describes what holds; a `dsn` pins how — interface, type, structure. Keep each claim at its level.
- **One obligation level per item.** If `SHALL` and `SHOULD` content mixes, split the item.
- **Leave implementation to build.** Output format, packaging, internal walk shape, file paths stay open unless a `req` constrains them.
- When shaping public surfaces, first read [module design](~/workspace/dev-playbook/standards/module-design.md) — small interface, deep implementation; accept dependencies, return results; keep the surface small. `Interface:` lines fully qualify symbol paths and follow the standard's annotation idiom.
- **Non-mandatory inclusion is a commitment.** A `SHOULD` / `MAY` you include is one you intend to deliver.
- Keep `Rationale:` and `Comment:` non-prescriptive per the spec standard; a claim that wants to prescribe belongs in `Description:`. Reference relevant ADRs rather than re-explaining them.
- **Mark the region work-in-progress.** Set `WIP: true` (§2.10) on each `feat` you author or reopen. Its cone reaches no verifiers yet, so completeness would otherwise fail; the marker exempts the `feat` and everything beneath it until build lands the verifiers and removes it. Consistency still holds.
- **Reconcile a revision bump.** When an edit bumps an existing item's revision (§2.2.3), every committed adjacent reference now names the prior revision — a **stale reference** (target `(type, name)` present at another revision; reported by `SpecGraph.stale_references()`, not raised), distinct from a **dangling reference** (target `(type, name)` absent entirely, still a raised consistency breach). Reconcile the bump's adjacent references:
  - **Spec-side bullets** — `Covers:` / `Depends:` in other spec items: re-point them to the new revision in-phase (the phase owns these files), re-evaluating that each adjacent item still fits the bumped item's new meaning.
  - **Verifier markers** — each `@pytest.mark.covers` on the bumped node: decide with the user. If the test still validates the new meaning, re-point the marker now — the covers-string only, never test logic. If it needs rework, leave it stale and set `WIP: true` (§2.10) on the bumped node (or its `feat`) so the now-uncovered completeness gap is exempt and the gate stays green.

  A deferred stale reference stays visible to `sdd-tdd` via `stale_references()`, which reconciles it when it reworks the test.

## 6. Review pass

Re-read each new `feat` / `req` / `dsn` and iterate until clean:

- [ ] Chains up via `Covers:` (or is a root); `Needs:` declares verification.
- [ ] `Description:` conforms to the spec standard (EARS template, single obligation level); a `dsn`'s `Interface:` annotations follow its idiom.
- [ ] `Rationale:` / `Comment:` stay non-prescriptive.
- [ ] Honors the section 5 principles.

## 7. Close the phase

When the user approves and the rubric passes:

1. **Leave the tree green.** Run the gate — `make check`; it builds and validates the spec graph. The region is `WIP:` (§5), so completeness is exempt and only **consistency** is enforced (§2.10) — a red build means the spec you just authored is malformed. Don't commit a red tree.
2. Run /commit.
3. Advance the issue to spec review — move its label from this node to the next:
   ```bash
   gh issue edit <issue> --remove-label "phase:sdd-specs" --add-label "phase:sdd-agent-spec-review"
   ```
4. Stop. Report that the spec is complete and the issue now sits at `phase:sdd-agent-spec-review`. Do not begin the review — the user dispatches the next node when ready.
