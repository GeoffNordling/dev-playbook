# Agent View Adoption

Working document. Survey of Claude Code's [agent view](https://code.claude.com/docs/en/agent-view) (`claude agents`) as a candidate primary entry point for parallel multi-agent work in this workspace.

**Not authoritative.** Adoption decisions live in [`adr/`](adr/). This doc collects requirements, capabilities, open questions, and the experiments that will close the gap.

## Purpose

Establish a firm understanding of what agent view can and cannot do, sized to support a workflow-design decision. The doc is structured so requirements drive the experiment list and the experiment list drives the eventual policy.

## Design principles

- Prefer native agent view behavior where it covers a requirement.
- Add a custom layer only when a requirement is established and no native path satisfies it.
- Existing custom-workflow behaviors are means, not ends — validate each against the requirement it serves before keeping it.
- Ideal end state: fully native, no custom worktree or dispatch code. Reachability depends on the open questions below.

## Requirements (must have)

These constrain any workflow design.

| # | Requirement |
|---|---|
| R1 | Multiple sessions run in parallel, each in its own worktree (so edits don't collide). |
| R2 | Sessions commit on their own. Commit happens without a human keystroke per commit. |
| R3 | Commit branches have human-readable names tied to the issue (readable from `git branch` alone). |
| R4 | Each row in agent view has a human-readable title — issue, phase, and overall job legible at a glance. |
| R5 | 1h idle-reaping of non-pinned sessions is acceptable. Reaping is process-level only — transcript, worktree, branch, and commits all persist; reattach respawns the session from saved state. Active work, blocked-on-input, attached-terminal, and long-running background processes all prevent reaping without any action. Pinning (`Ctrl+T`) is the explicit override for finished-and-idle sessions; whether a skill can self-pin is U8. |
| R6 | The GitHub issue's `phase/*` label is the externally-visible state machine (`phase/requirements` → `phase/design` → `phase/build` → `phase/review`). Survives any session, supervisor, or agent-view crash; readable by humans and fresh agents in fresh terminals. |
| R7 | The issue body is the self-contained brief. Cold-start works because no session-local memory is required to resume. |
| R8 | Skills are the single point of behavior definition. Behavior changes propagate everywhere because there is one definition. |
| R9 | Pre-flight check that local `main` matches `origin/main` before branching for new work. (Couples to the YubiKey/PAT decision below — see Deferred.) |

## Nice-to-haves

| # | Desire | Notes |
|---|---|---|
| N1 | Sessions push and open pull requests on their own. | Per U9: PR creation/merging are already PAT-reachable; only `git push` still taps. Reversible workspace policy choice; see Deferred. |
| N2 | Skill-invocable entry into agent view (typing `/sdd 4` into the agent view input dispatches the skill). | Whether this works at all is an unknown — see U1. |
| N3 | Human review gate is configurable per skill or per invocation. Two modes: review-each-commit-diff vs review-only-the-PR. | Pure skill-design problem; agent view supports both natively (see "Design space"). |

## Scope notes

Things explicitly outside the requirement set:

- Worktree directory naming is unconstrained. Branch naming is constrained by R3; directory naming is not.
- Agent view is the primary entry point. Resumability from other shells is not a requirement.

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
- Cleanup interaction: `Ctrl+X` ×2 in agent view deletes Claude-*created* worktrees including uncommitted changes; user-*created* worktrees (via `git worktree add` in Bash) are left in place.

### Session lifetime

- Sessions persist across machine sleep, supervisor restart, and Claude Code auto-update.
- Reaping is process-level, not data-level. After ~1h of idle, the supervisor stops a non-pinned session's *process* to free resources. Transcript, worktree, branch, commits, and tool state all persist on disk. The next peek/reply/attach respawns the process from saved state; the only cost is a brief warmup latency.
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

### GitHub auth surface

Tap surface for the autonomous loop:

- `git pull` — taps (SSH-bound to `git@github.com:...`).
- `git push` — taps (same).
- `gh pr create` / `gh pr merge` — no tap (PAT over HTTPS).
- `gh api` / `gh issue *` / `gh label *` — no tap (PAT over HTTPS).

Most GitHub operations are PAT-reachable; the only thing standing between today's auth and N1 is `git push`.

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

**Run U1 and U3 first** — they unblock the most. U1 tells us whether the skill-dispatch model survives at all. U3 tells us whether branch naming can stay native (no `bgIsolation: "none"` needed) or whether we need a manual escape.

## Skill-design space vs product-constraint space

Agent view hosts whatever behavior the skills implement. Some workflow choices live in the skill layer; others are fixed by the product.

### Skill-design space (either path is supported)

- **Human review gate location.** A skill that calls `AskUserQuestion` at each commit → row shows "Needs input" → human peeks/replies. A skill that runs through to `gh pr create` → row shows green PR dot → human reviews on github.com. Both modes are first-class. Choice is per-skill, per-invocation, or per-parameter.
- **Cross-phase continuity.** One session per issue lives across all phases (reattach + re-invoke `/sdd <N>` to advance), or one session per phase (each phase dispatches fresh and lands on the same branch). Both work; the choice is ergonomic.

### Product constraints (fixed)

- 1h idle reaping for non-pinned sessions.
- Permission mode inheritance rules at session birth.
- One-time interactive acceptance for `bypassPermissions` / `auto`.
- Auto-isolation timing (before first edit) — only the *whether* is configurable via `bgIsolation`, not the *when*.
- No master agent in agent view; input always dispatches a new session.

## Deferred topics

Each deserves its own dedicated pass before final workflow design.

### Sandboxing and permissions

Sessions run mostly unsupervised. The permission surface needs explicit treatment at two layers:

- **Claude Code permission system.** Default permission mode for autonomous sessions: `bypassPermissions` (faster, less safe), `acceptEdits` (curated), or explicit allowlist. Per-skill overrides.
- **OS-level sandboxing.** Network access, filesystem reach, process spawning. Available primitives on Fedora (Firejail, systemd-run with restrictions, Bubblewrap). Whether Claude Code can be invoked under a sandbox wrapper.

### `git push` autonomy

The single tap that gates N1. Three options:

1. **Keep SSH-bound `git push`.** Agents block on push, surface as "Needs input," human taps. Realizes everything except the unattended push — agent prepares the PR step, human's tap unblocks it, agent continues. Lowest-friction safety preserve.
2. **Switch the remote to HTTPS** (`https://github.com/...`) and let `git push` go over PAT. Realizes N1 fully. Cost: any compromised agent can push without a hardware tap; the PAT is the entire credential.
3. **Per-remote split.** SSH (`origin`) for human-driven work, separate HTTPS remote (e.g., `origin-pat`) for agent-driven push. More machinery; finer-grained.

**Mitigations under options 2 or 3:**

- Branch protection on `main` requiring PR review + passing checks (prevents direct push to `main`).
- Required signed commits.
- Scoped PAT (only the repos in scope, only the permissions needed; no `admin`, no `delete_repo`).
- Agents push to feature branches only; merges go through PR review.

R9 (main currency check) is independent of this decision — local `main` refresh still needs `git pull`, which taps under option 1 and PATs under options 2 or 3.

## Open decisions

Each depends on a deferred topic or an open experiment. Listed with their gating items.

- **Cleanup policy.** Candidates: the `worktree-sweep` tool (gated on PR-merged + no local divergence), or trust `Ctrl+X` ×2. Under fully-native auto-isolation, worktrees are Claude-created and `Ctrl+X` deletes them with any uncommitted changes — that constraint shapes the choice.
- **Worktree-creation mechanism.** Native auto-isolation, or Bash-driven `git worktree add`. Hinges on U2 + U3.
- **`bgIsolation` setting location.** Hinges on U4.
- **Cross-phase continuity model.** Skill-design choice; resolves after first lived cycle.
- **Human review gate default.** Skill-design choice; likely a per-skill parameter.
- **Session-naming mechanism.** Hinges on U5.
- **`EnterWorktree` / `ExitWorktree` permission deny in `dotfiles/dot-claude/settings.json`.** Whether to retain. Becomes redundant under `bgIsolation: "none"` or full-native auto-isolation.

## Next actions

1. **Run experiments U1 and U3** in a throwaway repo. Append results to this file.
2. **Run U2, U4, U5** opportunistically.
3. **Sandboxing pass.** Dedicated investigation; output is its own doc or ADR.
4. **`git push` autonomy pass.** Dedicated investigation; output is its own doc or ADR.
5. **Design the workflow policy** once U1–U5 close and the sandboxing + `git push` decisions land: dispatch surface, skill surface, `settings.json` shape, cleanup mechanism.
6. **Apply the policy** to `standards/workflow.md`, the `sdd*` skills, and `dotfiles/dot-claude/settings.json`.
7. **ADR** capturing the decision and its rationale.
