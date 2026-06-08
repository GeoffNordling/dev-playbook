---
name: design
description: Explores the approach for a direct-path issue — solutions, prototypes, tradeoffs — through a structured interview, then writes the chosen approach into the issue and advances it to implementation. Use when the agents dashboard launches the design phase.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "<issue-number>"
---

# Design

Explore the approach for a direct-path issue — talk through solutions, prototype where it helps, weigh tradeoffs — then write the chosen approach into the issue body and hand it off to implementation. The interview is the value of this skill. Design does not permanently write to disk: the deliverable is the approach captured on the issue, and any prototyping is exploratory — the worktree is left clean for the implementation node.

## Read first

Before doing anything else, read end-to-end:

- [module design](~/workspace/dev-playbook/standards/module-design.md) — small interface, deep implementation; accept dependencies, return results; keep the surface small. The lens for weighing a solution's shape.

Then report: `READ: module-design.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

**Be in the issue's worktree.** If the session is already there (cwd `.claude/worktrees/issue-<issue>`, carried across `/clear`), proceed. If the worktree exists but the session isn't in it, re-enter it: `EnterWorktree(path=.claude/worktrees/issue-<issue>)`. If neither the worktree nor the branch `issue-<issue>` exists yet — this is the issue's first node — create it: confirm local `main` is current with origin (a check, not a pull: compare `git rev-parse origin/main` to `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`; if they differ, tell the user to pull `main` and stop), then `EnterWorktree(name=issue-<issue>)` and `git branch -m worktree-issue-<issue> issue-<issue>`. If the branch exists but the worktree is gone, the issue's work was lost — tell the user and stop.

- `gh issue view <issue>` — the brief is the contract; the approach you write extends it.
- **Brownfield reconnaissance.** Read the existing code the issue touches — the modules in play, their public surfaces, the seams a solution would use.

## 2. Area discovery interview

Ask the user which decisions the approach turns on. Common areas:

- **Solution shape.** The main way to build it, and the alternatives worth weighing.
- **Module placement.** Whether the work extends a module or introduces one; where new code sits.
- **Public surface.** The signatures or interfaces the work exposes.
- **Tradeoffs.** Where two reasonable approaches diverge, and what tips the choice.
- **Scope boundary.** What this issue does not cover.

Surface your read of which areas look load-bearing and why; ask the user to confirm, add, or drop.

## 3. Intent interview

Invoke /grill-with-docs to sharpen the approach against the codebase, capturing significant decisions as ADRs as they crystallize. Where an area has discrete options — solution shape, module placement, interface — surface them, each option carrying a recommendation and the reason it is recommended. Prototype in the worktree only to settle a question the reading can't, and treat it as scratch, not work product.

## 4. Approach synthesis

Present the approach for explicit approval, then wait:

- **Chosen solution.** How the work will be built, at the level of modules, surfaces, and data shapes — not line by line.
- **Alternatives weighed.** The options considered and why the chosen one wins.
- **Decisions made.** Naming, placement, interface, error strategy, as resolved by interview.
- **Decisions deferred.** Anything left to the implementation node.

## 5. Capture the approach

On approval, append an `## Approach` section to the issue body — preserving the existing brief, never overwriting it — per [issue conventions](~/workspace/dev-playbook/standards/issue-conventions.md). `gh issue edit --body` replaces the whole body, so write back the brief unchanged plus the new section. Keep the Approach to what the implementation node needs — the chosen solution, the decisions that constrain the build, and the tradeoffs behind them; it is the contract the implementation node reads.

```bash
gh issue edit <issue> --body "$(cat <<'EOF'
...the existing brief, unchanged...

## Approach

...chosen solution, constraining decisions, tradeoffs...
EOF
)"
```

## 6. Close the phase

When the user approves the approach:

1. **Leave the worktree clean.** Design commits nothing — discard any scratch prototyping (restore tracked files, remove untracked) so the tree matches `origin/main` and the implementation node starts from the written approach alone.
2. Advance the issue to its implementation phase — move its label by the issue's `tests:*` value:
   ```bash
   # tests:yes
   gh issue edit <issue> --remove-label "phase:design" --add-label "phase:tdd"
   # tests:no
   gh issue edit <issue> --remove-label "phase:design" --add-label "phase:build"
   ```
3. Report and stop:
   ```
   <repo>#<issue> · current phase: design · next phase: <tdd|build> · <one-line summary> · approach in issue
   ```
