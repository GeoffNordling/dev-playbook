---
name: design
description: Works out how a direct-mode issue should be built — research, prototypes, tradeoffs — then leaves it factory-ready as one re-authored leaf or as an epic with ready children. Use when the user invokes /design on an issue, when intake parks work whose approach needs thought first, or when an issue looks too big for one build and needs slicing.
disable-model-invocation: false
model: inherit
effort: xhigh
argument-hint: "<issue-number>"
---

# Design

Work out how the issue should be built, then leave it factory-ready. Design is the definition region's research state ([software-factory.md](~/workspace/dev-playbook/software-factory/software-factory.md#the-definition-region)): it explores the approach, and where the work turns out to be bigger than one build, it decomposes.

**Nothing merges out of design.** The deliverable is on the issue — a re-authored brief, or an epic and its children (§7). Any code written here is scratch, and the tree it was written in is deleted at exit.

## Read first

Before doing anything else, read end-to-end:

- [module design](~/workspace/dev-playbook/standards/modules/design.md) — small interface, deep implementation; accept dependencies, return results; keep the surface small. The lens for weighing a solution's shape.
- [issue conventions](~/workspace/dev-playbook/standards/tracking/issues.md) — the brief formats and the readiness bar, plus the vertical-slice rules and native relationships the decompose exit runs on.

Then report: `READ: module-design.md, issue-conventions.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

- `gh issue view <issue> --comments` — the brief is what you re-author or decompose. Comments may carry context the body doesn't.
- **Brownfield reconnaissance.** Read the existing code the issue touches — the modules in play, their public surfaces, the seams a solution would use.

Reading needs no worktree; work in the checkout the session is already in. A tree is opened only if §5 prototypes, and it is a throwaway — never the issue's factory worktree, which design has no business creating.

## 2. Area discovery interview

Ask the user which decisions the approach turns on. Common areas:

- **Solution shape.** The main way to build it, and the alternatives worth weighing.
- **Module placement.** Whether the work extends a module or introduces one; where new code sits.
- **Public surface.** The signatures or interfaces the work exposes. Settle whether this one is **load-bearing** — written against by code you don't control, or costly to change once shipped. That answer decides §4.
- **Tradeoffs.** Where two reasonable approaches diverge, and what tips the choice.
- **Scope boundary.** What this issue does not cover.
- **Size.** Whether this is one build or several. "Several" is the §7 decompose exit; raise it here rather than discovering it at the end.

Surface your read of which areas look load-bearing and why; ask the user to confirm, add, or drop.

## 3. Intent interview

Invoke /grill-with-docs to sharpen the approach against the codebase, capturing significant decisions as Decision Records as they crystallize. Where an area has discrete options — solution shape, module placement, interface — surface them, each option carrying a recommendation and the reason it is recommended.

## 4. Design it twice — only for a load-bearing surface

When §2 settled that the public surface is load-bearing, read [design-it-twice.md](references/design-it-twice.md) and work through it: three or four subagents in parallel proposing the surface along different axes, compared on depth, locality, and seam placement.

Not an always-on step. An ordinary surface — internal, one caller, cheap to change — skips it, and skips that file.

## 5. Prototype — only where reading can't settle it

When a question survives the interview and the code can't answer it, invoke /prototype. Everything it says applies, with one thing fixed here: the code is throwaway and lives in a disposable tree, because nothing merges out of definition.

Open it with `EnterWorktree(name=design-<issue>)` and **keep** the `worktree-` prefix the tool puts on the branch — that prefix is what marks the tree disposable. Delete it at §8 whatever the outcome: the answer comes back on the issue, the code does not come back at all.

## 6. Synthesis and approval

Present the approach and the exit you propose, then wait for explicit approval:

- **Chosen solution.** How the work will be built, at the level of modules, surfaces, and data shapes — not line by line.
- **The seams, sketched.** The interfaces the work introduces or moves, what sits on each side, and what each hides. Sketch them *before* anything is written — always, whether or not §4 ran. The sketch is what `Key interfaces` is written from on the single-leaf exit, and what the slices cut along on the decompose exit.
- **Alternatives weighed.** The options considered and why the chosen one wins.
- **Decisions made.** Naming, placement, interface, error strategy, as resolved by interview.
- **Decisions deferred.** Anything left to `build`.
- **The exit** — one leaf, or decomposed, and why.

Nothing below this line is written to GitHub before the user approves.

## 7. Land the exit

### Single leaf

Re-author the issue's brief in place across the six build-leaf headings ([issue conventions](~/workspace/dev-playbook/standards/tracking/issues.md)). The approach lands *inside* those headings — the chosen solution shapes `Desired behavior` and `Key interfaces`, the constraining decisions become acceptance criteria, the boundary becomes `Out of scope`. There is no separate approach section: `build` reads one brief, not a brief plus a commentary on it.

`gh issue edit --body` replaces the whole body, so write the complete brief back:

```bash
gh issue edit <issue> --body "$(cat <<'EOF'
...the six headings, re-authored...
EOF
)"
```

### Decompose

When the work is bigger than one build, the issue becomes an **epic** and never builds itself, and its children are minted ready here rather than round-tripping through `intake`. Read [decompose.md](references/decompose.md) and work through it — the epic rewrite, the slicing, the children, and the relationship wiring.

## 8. Close the phase

Only once the user has explicitly agreed design is done. No label moves in this region on the agent's own authority.

1. **Move the phase** — single leaf only: `gh issue edit <issue> --remove-label "phase:design" --add-label "phase:build"`, and the issue crosses into the factory. A decomposed issue shed its phase at §7 and stays an epic; its children carry the work.
2. **Delete the prototype tree**, if §5 opened one: `ExitWorktree(action: "remove", discard_changes: true)` — the uncommitted scratch is exactly what that flag is for, and the answer already reached the issue at §7. If the tool reports no worktree session (this session re-entered the tree by path after a `/clear`, so it doesn't own it), use `ExitWorktree(action: "keep")` and then `git worktree remove --force .claude/worktrees/design-<issue>` and `git branch -D worktree-design-<issue>`.
3. Report and stop:
   ```
   <repo>#<issue> · phase: design · <released to build | epic + N ready children> · brief in issue
   ```
