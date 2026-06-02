---
name: sdd-requirements
description: Authors a project's functional requirements — `feat` and `req` spec items — through a structured interview, then leaves the tree green and advances the issue to design. Use when the agents dashboard launches the requirements phase.
disable-model-invocation: false
model: opus
effort: xhigh
allowed-tools: Bash(gh issue *) Bash(gh api *) Bash(git *) EnterWorktree ExitWorktree Edit Write Skill(grill-with-docs) Skill(commit)
argument-hint: "<issue-number>"
---

# SDD Requirements

Author a project's functional requirements — `feat` (high-level capability) and `req` (functional requirement) items — through a structured interview, then leave the tree green and hand the issue off to the design phase. The interview is the value of this skill.

## Read first

Before doing anything else, read end-to-end:

- [spec standard](~/workspace/spec-tools/sdd-standards/spec-standard.md) — the full `feat`/`req` grammar, EARS templates, obligation vocabulary, coverage chain.
- [lessons](~/workspace/spec-tools/sdd-standards/lessons.md) — accumulated observations about the standard from prior use.

Then report: `READ: spec-standard.md, lessons.md`. Proceed only after.

## 1. Load context

Issue number arrives as `$ARGUMENTS`.

**Create the issue's worktree.** First confirm local `main` is current with origin — a check, not a pull: compare `git rev-parse origin/main` to `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`. If they differ, tell the human to pull `main` and stop. Otherwise create it: `EnterWorktree(name=issue-$ARGUMENTS)`, then `git branch -m worktree-issue-$ARGUMENTS issue-$ARGUMENTS`.

- `gh issue view $ARGUMENTS` — the body is the contract.
- Existing specs: `specs/functional_requirements/`.
- `CONTEXT.md` for domain vocabulary, if present.

## 2. Area discovery interview

Ask the user which behavior areas matter. Start small:

- **Success path.** The headline behavior the `feat` exists for.
- **Edge / error behavior.** What counts as malformed; raise vs. return-as-data; what is silently accepted.
- **Scope boundary.** What is explicitly out of scope for this `feat`.

Add areas as they surface. Surface your read of which areas look load-bearing and why; ask the user to confirm, add, or drop.

## 3. Intent interview

Invoke /grill-with-docs to reach shared understanding of the flagged areas. It interviews the user one question at a time, challenges fuzzy terms against `CONTEXT.md`, cross-references the code, and records resolved domain terms and decisions in `CONTEXT.md` / ADRs as they crystallize. Where an area has discrete options, surface them with AskUserQuestion — each option carrying a recommendation and the reason it is recommended.

## 4. Plan synthesis

Present a plan for explicit approval, then wait:

- **Scope.** Which behaviors this pass captures, and which `req` covers each.
- **Skeletons.** Per planned `feat` / `req`: id + heading + role + `Covers:` + `Needs:`. No `Description:` prose yet.
- **Decisions made.** Obligation level, granularity, edge-case treatment, as resolved by interview.
- **Decisions deferred.** Anything still open.

## 5. Drafting

The skeleton holds — `Covers:` and `Needs:` from the plan are locked; add prose now.

- **Minimum viable shape.** Each `req` commits to one checkable behavior. A clause earns its place only by adding a check.
- **Behavior, not method.** Describe what holds; implementation choices belong to design.
- **One obligation level per item.** If `SHALL` and `SHOULD` content mixes, split the item.
- **Non-mandatory inclusion is a commitment.** A `SHOULD` / `MAY` you include is one you intend to deliver.
- Keep `Rationale:` and `Comment:` non-prescriptive per the spec standard; a claim that wants to prescribe belongs in `Description:`.
- **Mark the region work-in-progress.** Set `WIP: true` (§2.10) on each `feat` you author or reopen. Its cone reaches no verifiers yet, so the completeness rules would otherwise fail; the marker exempts the `feat` and everything beneath it until build lands the verifiers and removes it. Consistency still holds.

## 6. Review pass

Re-read each new `feat` / `req` and iterate until clean:

- [ ] Chains up to a `feat` via `Covers:` (or is a root); `Needs:` declares verification.
- [ ] `Description:` conforms to the spec standard (EARS template, single obligation level).
- [ ] `Rationale:` / `Comment:` stay non-prescriptive.
- [ ] Honors the section 5 principles.

## 7. Close the phase

When the user approves and the rubric passes:

1. **Final check sweep — leave the tree green.** Run the project's tests, lint, format, and typecheck (per `CLAUDE.md` / `Makefile`). If a command is undefined, note the absence and continue; if a defined command fails, stop and surface it.
2. Run /commit.
3. **Release the worktree.** `ExitWorktree(keep)`.
4. Advance the issue to the design phase — move its label from this node to the next:
   ```bash
   gh issue edit $ARGUMENTS --remove-label "phase:sdd-requirements" --add-label "phase:sdd-design"
   ```
5. Stop. Report that requirements is complete and the issue now sits at `phase:sdd-design`. Do not begin design work — the human launches /sdd-design from the dashboard when ready.