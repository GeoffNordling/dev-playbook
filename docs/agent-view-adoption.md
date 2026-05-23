# Agent View Adoption

Working document. Captures the state of our investigation into Claude Code's [agent view](https://code.claude.com/docs/en/agent-view) (`claude agents`) as the primary entry point for parallel multi-agent work in this workspace.

**Not authoritative.** Adoption decisions live in [`adr/`](adr/). This doc collects requirements, knowns, unknowns, and the experiments that will close the gap.

Last updated: 2026-05-23.

## Purpose

Today the workspace runs multi-agent work through a custom Bash-driven worktree convention (`standards/workflow.md` and the `sdd*` skills in `dotfiles/dot-claude/skills/`). Agent view ships with its own native worktree and dispatch model. Before adopting it, we need a firm understanding of what the product can and cannot do, separate from any decision about how we'll use it.

## Stance

- We are **not** trying to make agent view fit the existing workflow.
- We are **not** treating the existing workflow's behaviors as requirements by default — many of them are means, not ends.
- The goal is to understand agent view's capabilities and constraints clearly enough that we can design a fresh workflow on top of it. Where native behavior covers a need, prefer native. Where it doesn't, decide consciously whether the need is real before adding custom layers.
- Ideal end state: fully native, no custom worktree/dispatch code. Whether that's reachable depends on the unknowns below.

## Requirements (must have)

Confirmed in discussion. These constrain any workflow design.

| # | Requirement |
|---|---|
| R1 | Multiple sessions run in parallel, each in its own worktree (so edits don't collide). |
| R2 | Sessions commit on their own. Commit happens without a human keystroke per commit. |
| R3 | Commit branches have human-readable names tied to the issue (readable from `git branch` alone). |
| R4 | Each row in agent view has a human-readable title — issue, phase, and overall job legible at a glance. |
| R5 | 1h idle-reaping of non-pinned sessions is acceptable. Reaping is process-level only — transcript, worktree, branch, and commits all persist; reattach respawns the session from saved state. Active work, blocked-on-input, attached-terminal, and long-running background processes all prevent reaping without any action. Pinning (`Ctrl+T`) is the explicit override for finished+idle sessions; whether a skill can self-pin is U8. |
| R6 | Phase label on the GitHub issue (`phase/requirements` → `phase/design` → `phase/build` → `phase/review`) remains the externally-visible state machine. Survives any session/supervisor/agent-view crash; readable by humans and fresh agents in fresh terminals. |
| R7 | The issue body remains the self-contained brief. Cold-start works because no session-local memory is required to resume. |
| R8 | Skills remain the single point of behavior definition. Behavior changes propagate everywhere because there is one definition. |
| R9 | Pre-flight check that local `main` matches `origin/main` before branching for new work. (Couples to the YubiKey/PAT decision below — see Deferred.) |

## Nice-to-haves

| # | Desire | Notes |
|---|---|---|
| N1 | Sessions push and open pull requests on their own. | Currently blocked by YubiKey gating of `git push` and possibly `gh pr create`. Reversible workspace policy choice; see Deferred. |
| N2 | Skill-invocable entry into agent view (typing `/sdd 4` into the agent view input dispatches the skill). | Whether this works at all is an unknown — see U1. |
| N3 | Human review gate is configurable per skill or per invocation. Two modes: review-each-commit-diff vs review-only-the-PR. | Pure skill-design problem; agent view supports both natively (see "Design space"). |

## Dropped or downgraded from prior workflow

Behaviors the current custom flow has but the discussion concluded are not requirements going forward.

- **Worktree directory name encodes the issue.** Worktrees may be opaquely named (e.g., agent-view's session-id-based dirs). Branch name still matters (R3); directory name doesn't.
- **Worktree resumable from a plain terminal** (`cd .claude/worktrees/<name>` from any shell). Agent view is the primary entry point.
- **`worktree-sweep` cleanup gating** (PR-merged + no divergence check). Open question whether this safety property must be preserved or whether `Ctrl+X` ×2 is enough — see "Decisions deferred until unknowns close."

## What we know about agent view

From the official docs (https://code.claude.com/docs/en/agent-view). Confidence: high unless flagged.

### Dispatch model

- No master agent. Every input typed into agent view's bottom prompt **launches a new background session**; there is no persistent master conversation.
- Three dispatch surfaces:
  - `claude --bg [--name "X"] "<prompt>"` from a plain shell — starts a fresh detached session in cwd.
  - Typing into agent view's input — same as `claude --bg` but from within agent view; row gets auto-named from the prompt.
  - `/bg [optional final instruction]` from inside an already-attached session — backgrounds the current conversation (same transcript continues, just detached).
- Session display name controllable via `--name` at dispatch, or `Ctrl+R` interactively in agent view. Auto-generated from prompt otherwise.
- Filters in agent view input: `a:<agent>`, `s:<state>` (including `s:blocked`), `#<PR-number>` or PR URL.

### Worktree mechanism

- Auto-isolation triggers **before first edit**, not at session start: Claude moves the session into a worktree under `.claude/worktrees/`.
- Auto-isolation **skipped** when any of:
  - Session is already inside a linked git worktree (Claude-created or user-created via `git worktree add`).
  - Working directory is not a git repository and no `WorktreeCreate` hook is configured.
  - The write target is outside the working directory.
- Disable knob: `worktree.bgIsolation: "none"` in `.claude/settings.json`. Documented as project-level; global applicability is an unknown (U4). Requires Claude Code v2.1.143+.
- Cleanup interaction: `Ctrl+X` ×2 in agent view deletes Claude-*created* worktrees including uncommitted changes; **user-created** worktrees (via `git worktree add` in Bash) are left in place.

### Session lifetime

- Sessions persist across machine sleep, supervisor restart, and Claude Code auto-update.
- **Reaping is process-level, not data-level.** After ~1h of idle, the supervisor stops a non-pinned session's *process* to free resources. Transcript, worktree, branch, commits, and tool state all persist on disk. The next peek/reply/attach respawns the process from saved state; the only cost is a brief warmup latency.
- A session is **not eligible for reaping** while any of these holds:
  - Actively working (running a tool, generating).
  - Waiting on input (Needs input state — `AskUserQuestion`, permission prompt, blocking question).
  - A terminal is attached.
  - A long-running background shell command, subagent, workflow, or monitor is running inside it (docs explicitly note "a dev server keeps the session alive").
  - Pinned with `Ctrl+T`.
- `Ctrl+T` is therefore the explicit override for the *finished + idle + nobody-attached* case where you specifically want the process to stay hot (e.g., to avoid the warmup latency on next attach).
- Machine shutdown stops running sessions (they show as failed on next view); reattaching restarts them from state.

### Permissions

- Background sessions read settings from the directory they run in (project `.claude/settings.json` applies normally).
- Permission mode at session birth:
  - Dispatched from agent view input or `claude --bg`: uses directory's `defaultMode`, or dispatched subagent's `permissionMode` frontmatter.
  - `/bg` from existing session: keeps current mode (a session you put in `acceptEdits` stays there).
- `bypassPermissions` and `auto` modes require **one-time interactive acceptance** (run `claude` with that mode at least once) before any background session can use them.
- Permission mode persists across supervisor-driven process restarts (a session launched with `--dangerously-skip-permissions` stays in `bypassPermissions` after a restart).
- `claude agents --permission-mode/--model/--effort/--settings/--add-dir/--plugin-dir/--mcp-config` flags pass through to every session dispatched from that agent view invocation. Requires v2.1.142+.

### State signaling

- "Needs input" is a first-class state. Triggered by `AskUserQuestion`, permission prompts, or any blocking question from the session. Rows surface in a dedicated group at the top of agent view.
- "Ready for review" group collects sessions that have opened a pull request.
- PR status dot per row: yellow (waiting on checks/review), green (passed), purple (merged), grey (draft/closed). Hyperlinked in supporting terminals.
- Terminal tab title updates: `2 awaiting input · claude agents` when sessions are blocked.

## What we don't know (experiments needed)

Run before any design or implementation decisions. Numbered for reference.

| # | Unknown | Why it matters | Experiment |
|---|---|---|---|
| U1 | Typing `/sdd 4` into agent view's input — does the launched session invoke the skill, or see the literal string `"/sdd 4"`? | Determines whether the entire skill-dispatch model (N2, R8) survives in agent view. Foundational. | In a throwaway repo, type `/sdd 4` into the input. Peek the new row to see whether the skill ran or the prompt was treated as text. |
| U2 | When agent view auto-isolates, what branch does the new worktree get? | Determines whether R3 (human-readable branch names) needs custom skill code or whether native naming is acceptable. | Dispatch a trivial session ("create foo.txt"), let auto-isolation fire, check `git -C .claude/worktrees/<dir> branch --show-current`. |
| U3 | If a skill runs `git switch -c <issue>-<slug>` *before* the first edit, does auto-isolation create the worktree on that branch, or invent its own? | Determines whether a skill can force the branch name R3 wants without disabling auto-isolation. | Dispatch a skill that explicitly creates and switches to a named branch, then touches a file. Inspect the worktree's branch. |
| U4 | Can `worktree.bgIsolation` live in user-global `~/.claude/settings.json`, or must it be per-project? | Determines whether the setting goes in dotfiles once or in every repo. | Put it in global only; dispatch a session in a fresh repo without project settings; observe whether auto-isolation fires. |
| U5 | Can a session rename itself programmatically (e.g., set display name to `<issue>-<slug>` after loading the issue), or is naming only `--name` at dispatch and `Ctrl+R` interactively? | Determines whether R4 (human-readable rows) requires user keystrokes or can be automatic. | Inside a dispatched session, look for a `claude` subcommand, MCP-style hook, or skill primitive that renames the current session. |
| U6 | What happens if you re-invoke `/sdd <N>` inside an already-attached session that's already in its worktree? | Cross-phase continuity may want this. The current dispatcher's `git worktree add` would fail (already exists); glob-resolution branch should succeed. Needs confirmation. | Dispatch `/sdd 4`, let it land in a worktree, attach, re-invoke `/sdd 4`. |
| U7 | Does `/bg` from an interactive session preserve the branch and worktree state, or create a new worktree on backgrounding? | Affects whether a manual terminal session can be promoted into agent view mid-work. | Start `claude` in a manually-created worktree, run `/bg`, inspect the resulting agent-view session's worktree and branch. |
| U8 | Can a session self-pin (`Ctrl+T` equivalent from inside a skill)? | If yes, long-running skills can keep themselves hot. If no, pinning is a manual user step. | Investigate `claude` CLI subcommands and any in-session primitives. |
| U9 | Does `gh pr create` require a YubiKey tap, independent of the underlying `git push`? | Directly informs N1 (sessions push and open PRs on their own) and the YubiKey/PAT deferred decision. `gh` uses HTTPS+PAT per `dotfiles/dot-claude/rules/bash-commands.md` — so `gh pr create` itself likely doesn't tap, but a PR can't be opened for an unpushed branch, and `git push` does tap. Need to confirm the split. | On an already-pushed test branch, run `gh pr create --draft --title test --body test` and observe whether a tap is prompted. Then in a clean workspace, attempt the full `git push` + `gh pr create` flow and confirm which step taps. |

**Run U1 and U3 first** — they unblock the most. U1 tells us whether the skill-dispatch model survives at all. U3 tells us whether branch naming can stay native (no `bgIsolation: "none"` needed) or whether we need a manual escape.

## Skill-design space vs product-constraint space

A clean distinction worth holding onto: agent view *hosts* whatever behavior the skills implement. Several questions that feel like they're about agent view are actually about how we author skills on top of it.

### Skill-design choices (agent view supports either)

- **Human review gate location.** Skill that calls `AskUserQuestion` at each commit → row shows "Needs input" → human peeks/replies. Skill that runs through to `gh pr create` → row shows green PR dot → human reviews on github.com. Both modes are first-class. The choice is per-skill, per-invocation, or per-parameter.
- **Cross-phase continuity.** One session per issue lives across all phases (reattach + re-invoke `/sdd <N>` to advance) vs one session per phase (each phase dispatches fresh and lands on the same branch). Both work; tradeoffs are ergonomic. Decision can wait until we've used agent view for a real cycle.

### Product constraints (cannot be skilled around)

- 1h idle reaping for non-pinned sessions.
- Permission mode inheritance rules at session birth.
- One-time interactive acceptance for `bypassPermissions`/`auto`.
- Auto-isolation timing (before first edit) — only the *whether* is configurable via `bgIsolation`, not the *when*.
- No master agent in agent view; input always dispatches a new session.

## Deferred topics

Surfaced in discussion, not investigated. Worth their own dedicated passes before final workflow design.

### Sandboxing and permissions deep dive

Sessions will run mostly unsupervised; the permission surface deserves explicit treatment at two layers:

- **Claude Code permission system.** Current `dotfiles/dot-claude/settings.json` allow/deny scheme. What should the default be for autonomous sessions? `bypassPermissions` (faster, less safe), `acceptEdits` (curated), or default with explicit allowlist (current)? Per-skill overrides?
- **OS-level sandboxing.** Network access, filesystem reach, process spawning. What sandboxing primitives are available on Fedora? Firejail? systemd-run with restrictions? Bubblewrap? Does Claude Code support invocation under a sandbox wrapper?

### YubiKey vs PAT for git operations

Current policy: `git pull`, `git push` require YubiKey tap (SSH-bound). Whether `gh pr create` itself taps is U9.

Tradeoff to evaluate:
- **Keep YubiKey**: agents block on pulls/pushes/PRs, surface as "Needs input." Human-in-the-loop for every network-affecting git op. Slows autonomous flow; preserves R9 by forcing the human to refresh `main`.
- **Add PAT for git over HTTPS**: agents pull/push/PR autonomously. Realizes N1. Cost: any compromised agent can push and open PRs in your name without a hardware tap.

Mitigations to consider if relaxing: scoped PAT, push-protection rules on the remote, branch protection requiring review on `main`, signed commits.

## Decisions deferred until unknowns close

These are real decisions; we're not making them yet.

- **Cleanup model.** `worktree-sweep` (PR-merged gating) vs `Ctrl+X` ×2 (trust the keystroke). If we go fully native and worktrees become Claude-created, sweep loses its safety property (Claude-created worktrees can be deleted with uncommitted changes via Ctrl+X).
- **Worktree-creation mechanism.** Native auto-isolation vs Bash-driven `git worktree add`. Hinges on U2 + U3.
- **`bgIsolation` setting location.** Hinges on U4.
- **Cross-phase continuity model.** Skill-design choice; defer until lived experience.
- **Human review gate default.** Skill-design choice; per-skill parameter likely.
- **Session-naming mechanism.** Hinges on U5.
- **Whether to keep `EnterWorktree`/`ExitWorktree` deny in `dotfiles/dot-claude/settings.json`.** Currently kept; becomes redundant if `bgIsolation: "none"` is used OR if we go fully native and embrace auto-isolation.

## Next actions

1. **Run experiments U1 and U3** in a throwaway repo. Document results in this file.
2. **Run U2, U4, U5** opportunistically.
3. **Sandboxing pass.** Dedicated investigation; output is its own doc or ADR.
4. **YubiKey/PAT cost-benefit pass.** Dedicated investigation; output is its own doc or ADR.
5. **Once U1–U5 are closed and sandboxing/YubiKey decisions made:** design the workflow policy (which dispatch surface, which skills survive, what `settings.json` looks like, whether `worktree-sweep` stays).
6. **Migrate `standards/workflow.md` and `sdd*` skills** per the chosen policy. Update `dotfiles/dot-claude/settings.json` to match.
7. **ADR** capturing the decision and its rationale.
