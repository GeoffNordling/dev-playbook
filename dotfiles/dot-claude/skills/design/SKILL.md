---
name: design
description: Works out how a direct-mode issue should be built, then leaves it factory-ready. Use when an issue's approach needs thought before it can be built, when intake parks work for design, or when an issue looks too big for one build and needs slicing.
disable-model-invocation: false
model: inherit
effort: xhigh
argument-hint: "<issue-number>"
---

# Design

Work out how the issue should be built, then leave it factory-ready. Design is the definition region's research state ([software-factory.md](~/workspace/dev-playbook/software-factory/software-factory.md#the-definition-region)): it explores the approach, and where the work turns out to be bigger than one build, it decomposes.

**Nothing merges out of design.** The deliverable is on the issue — a re-authored brief, or an epic and its children (§7). Any code written here survives only on a never-merging branch as context (§5, §8); its tree is deleted at exit.

## Read first

Before doing anything else:

- Invoke /codebase-design — small interface, deep implementation; accept dependencies, return results; keep the surface small. The lens for weighing a solution's shape.
- Read [issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md) end-to-end — the brief formats and the readiness bar, plus the vertical-slice rules and native relationships the decompose exit runs on.

Then report: `READ: codebase-design, issue-authoring.md`. Proceed only after.

## 1. Load context

`$ARGUMENTS` is the issue number; below, `<issue>` is that number.

- `gh issue view <issue> --json title,body,comments` — the brief is what you re-author or decompose. Comments may carry context the body doesn't.
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

## 3. General Interview

Invoke /grill-with-docs to sharpen the approach against the codebase, capturing significant decisions as Decision Records as they crystallize. Where an area has discrete options — solution shape, module placement, interface — surface them, each option carrying a recommendation and the reason it is recommended.

Claims about existing reality accumulate through this interview — what a module does today, what a config holds, what a rule enforces. Collect the ones the approach stands on into a **proposed-probe list** and put it to the user; they pick which are worth measuring ([Claim provenance](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#claim-provenance)). Run the picked probes immediately, in-context, as ordinary tool calls, and post the **probe-record comment** on the issue — each probe's command and its observed output, appended to on later runs. The §7 brief's `measured` claims cite it; peripheral claims ride as `assumed` freely.

## 4. Design it twice — only for a load-bearing surface

When §2 settled that the public surface is load-bearing, read [design-it-twice.md](references/design-it-twice.md) and work through it: three or four subagents in parallel proposing the surface along different axes, compared on depth, locality, and seam placement.

An ordinary surface — internal, one caller, cheap to change — skips it, and skips that file.

## 5. Prototype — only where reading can't settle it

When a question survives the interview and the code can't answer it, invoke /prototype. Everything it says applies, with one thing fixed here: the prototype lives in its own disposable tree, because nothing merges out of definition.

Open it with `EnterWorktree(name=design-<issue>)`, then rename the branch the tool minted — `git branch -m worktree-design-<issue> prototype/<issue>` — because automated worktree cleanup keys on the `worktree-` prefix, and this branch must outlive the session. `prototype/<issue>` is this node's prototype branch name, suffixed when one issue carries several (`prototype/<issue>-<slug>`). If the tool refuses because this session already holds a worktree, make the tree by hand — `git worktree add .claude/worktrees/design-<issue> -b prototype/<issue>` — and enter it with `EnterWorktree(path: …)`; no rename needed, and §8's exit is the same either way. Commit on that branch whatever the outcome, and commit everything the standard's prototype paragraph requires, so review can audit the artifact without re-running it. The answer comes back on the issue; the tree goes at §8; the branch survives as the prototype's primary source, and the re-authored brief cites branch + path.

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

Re-author the issue's brief in place across the build-leaf headings ([issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#the-build-leaf-brief-modedirect)), which is where the required set is fixed. A child a decomposition minted takes this exit too — its starting brief is what gets re-authored, and this is where that child's brief becomes complete. The approach lands *inside* those headings — the chosen solution shapes `Desired behavior` and `Key interfaces`, the constraining decisions become acceptance criteria, the boundary becomes `Out of scope`. There is no separate approach section: `build` reads one brief, not a brief plus a commentary on it.

Draft every heading except `User intent`, then invoke /user-intent-mini-interview for that one: the user says their intent cold, the beat surfaces where it collides with the draft, and the reconciled paragraph lands in their own words. Run it on every single-leaf write, rework laps included — an umbrella dictated over an earlier draft may no longer fit a re-authored brief. It runs before the write, so a collision that exposes a mistaken acceptance criterion is still free to fix.

`gh issue edit --body` replaces the whole body
([tracker operations](~/workspace/dev-playbook/standards/tracking/tracker-operations.md#the-issue-surface)),
so write the complete brief back — every required heading, re-authored.

### Decompose

When the work is bigger than one build, the issue becomes an **epic** and never builds itself, and its children are minted here rather than round-tripping through `intake` — each carrying a starting brief only, never a finished one. A child is completed and released later, in its own design session. Read [decompose.md](references/decompose.md) and work through it — the epic rewrite, the slicing, the children, and the relationship wiring.

## 8. Close the phase

Only once the user has explicitly agreed design is done. No label moves in this region on the agent's own authority.

1. **Run the issue-review beat** — for the leaf this session designed, fresh or decomposition-minted. The two lenses are **your tools, not the user's** — latent instruments that sharpen your brief. Dispatch both in one message, as fresh-context subagents: one invokes `/issue-review-claims <issue>`, the other `/issue-review-simulation <issue>`, each pinned to the model its skill file names, reading only the issue and the repo. Merge and deduplicate their findings, then apply or demote each on your judgment, rewriting until it is a brief you would hand an autonomous builder. Never stop to have the user rule, and record nothing on the issue. Then present the finished issue: the URL, what you changed, and anything unresolved ([the issue-review verdict](~/workspace/dev-playbook/software-factory/user-checkpoints.md#the-issue-review-verdict)). They may always skip or cut short the beat.
2. **Move the phase** — single leaf only, on their approval alone: `gh issue edit <issue> --remove-label "phase:design" --add-label "phase:build"`. Asked for changes, apply and re-present. Judged not ready, it stays at `phase:design` for a session that re-authors it; only this move is skipped — the rest run either way. A decomposed issue shed its phase at §7 and stays an epic; each child crosses on its own approval.
3. **Keep the branch, drop the tree**, if §5 opened one. The prototype is already committed on `prototype/<issue>` (§5). Exit with `ExitWorktree(action: "keep")` — never `"remove"`, which deletes the branch too — then `git worktree remove .claude/worktrees/design-<issue>`, and leave the pointer /prototype asks for: `gh issue comment <issue> --body "Prototype preserved on branch prototype/<issue> at <dir>."`, where `<dir>` is the prototype's directory **inside that branch** — not the tree the previous command just deleted. Then push the branch — `git push -u origin prototype/<issue>` — so the citable artifact is on origin. It survives there until everything citing it has merged; after that it is deletable garbage with no purge duty.
4. Report and stop:
   ```
   <repo>#<issue> · phase: design · <released to build | epic + N children, M released | awaiting verdict> · brief in issue
   ```
   Where §5 opened a tree, append ` · prototype/<issue> on origin`.
