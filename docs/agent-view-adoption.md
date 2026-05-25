# Agent View Adoption

We have committed to adopting Claude Code's [`claude agents`](https://code.claude.com/docs/en/agent-view) view as this workspace's parallel-session entry point. Today's workflow — `workflow.md` and the skills that implement it (especially the `/sdd-*` family) — pre-dates the feature and will be redesigned around it. This document is the survey that has to land first: agent view's abilities, limitations, and constraints in enough detail to design against.

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
| R3 | Given an issue reference, the user can locate the worktree and reattach to its session. The mechanism is open (branch name, display name, state.json grep, filter, custom tool); the capability is required. |
| R4 | Each row in agent view has a human-readable title — issue, phase, and overall job legible at a glance. |
| R9 | Pre-flight check that local `main` matches `origin/main` before branching for new work. (Couples to the YubiKey/PAT decision below — see Deferred.) |

## Nice-to-haves

| # | Desire | Notes |
|---|---|---|
| N1a | Sessions push branches to `origin` on their own. | Not possible today: `git push` to `git@github.com:...` taps the YubiKey. Requires the `git push` autonomy decision — see Deferred. |
| N1b | Sessions create, update, and merge pull requests on their own. | Works today. `gh pr create`, `gh pr edit`, `gh pr review`, `gh pr merge --auto` all go over HTTPS via the PAT — no tap. |
| N2 | Skill-invocable entry into agent view (typing `/sdd 4` into the agent view input dispatches the skill). | Works: the launched session model-invokes the skill. Skill must have `disable-model-invocation: false`. |
| N3 | Human review gate is configurable per skill or per invocation. Two modes: review-each-commit-diff vs review-only-the-PR. | Pure skill-design problem; agent view supports both natively (see "Design space"). |

**N1a × N1b interaction.** End-to-end autonomy (dispatch → commit → push → PR → merge) is gated only by N1a. An autonomous-mode agent runs to the point of `git push`, stops, and surfaces a "Needs input" row in agent view; after the user's YubiKey tap completes the push, downstream `gh pr create` / `gh pr merge --auto` proceeds without further intervention. The `git push` autonomy decision (Deferred) is what would close that one remaining gap.

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
- The prompt is delivered as the launched session's first user message; agent view itself does not parse slash commands.
- A prompt starting with `/<skill>` causes the launched session to model-invoke that skill as its first action, subject to the skill's `disable-model-invocation` frontmatter. Skills with `disable-model-invocation: true` cannot be entered this way (the autocomplete picker also hides them).
- Session display name controllable via `--name` at dispatch, or `Ctrl+R` interactively in agent view. Auto-generated from prompt otherwise — by a Haiku-class model, so not deterministic across repeated runs of the same prompt. `nameSource: "auto"` vs `"manual"` is recorded in `state.json`.
- Filters in agent view input: `a:<agent>`, `s:<state>` (including `s:blocked`), `#<PR-number>` or PR URL.

### Worktree mechanism

- Auto-isolation triggers **before first edit**, not at session start: Claude moves the session into a worktree under `.claude/worktrees/`.
- Native naming scheme (observed in v2.1.150): the directory gets a 3-word adjective-adjective-noun slug (e.g., `quiet-exploring-waterfall`); the branch is that slug prefixed with `worktree-` (e.g., `worktree-quiet-exploring-waterfall`). Branched from current HEAD. No tie to the prompt, intent, session name, or any issue — does not satisfy R3.
- Auto-isolation **skipped** when any of:
  - Session is already inside a linked git worktree (Claude-created or user-created via `git worktree add`).
  - Working directory is not a git repository and no `WorktreeCreate` hook is configured.
  - The write target is outside the working directory.
- Disable knob: `worktree.bgIsolation: "none"` in `.claude/settings.json`. Documented as project-level; global applicability is an unknown (U4). Requires Claude Code v2.1.143+.
- Override knob: the `WorktreeCreate` hook. Per the hooks reference it "replaces default git behavior"; a registered command receives the session context on stdin and prints the chosen worktree path to stdout. Whether the hook fires inside a git repo (not only outside git), what payload it gets, and whether a hook-created branch name is preserved are still unknowns — see U3.
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

### Session state on disk

- `~/.claude/jobs/<short-id>/state.json` holds per-session metadata. Observed fields (v2.1.150):
  - `intent` — raw text of the session's first prompt (e.g., `/caveman`, `/sdd 7`). Most direct lookup key for "which session is working on X."
  - `name`, `nameSource` — display name shown in agent view rows. `auto` when generated from the prompt by the Haiku-class namer; `manual` after `--name` or `Ctrl+R`.
  - `daemonShort` — 8-char short ID used by `claude attach`, `claude logs`, `claude stop`, `claude rm`; matches the directory name under `~/.claude/jobs/`.
  - `sessionId`, `resumeSessionId` — full UUIDs; the transcript jsonl lives at `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl`.
  - `originCwd`, `cwd` — original dispatch directory vs current working directory; `cwd` updates when auto-isolation moves the session into a worktree.
  - `state`, `detail`, `tempo`, `inFlight`, `output.result` — runtime status fields driving agent view rows and the peek panel.
  - `template`, `respawnFlags`, `backend`, `cliVersion`, `createdAt`, `updatedAt`, `firstTerminalAt` — infrastructural.
- `~/.claude/jobs/<short-id>/timeline.jsonl` — append-only event log per session.
- `~/.claude/jobs/pins.json` — the pin set.
- `~/.claude/daemon.log`, `~/.claude/daemon/roster.json` — supervisor-level state.
- Implication for R3 (lookup): grepping `intent` and `originCwd` across `~/.claude/jobs/*/state.json` is the most direct mechanism today. `claude agents --json` is the supported programmatic surface for the same data.

### Permissions

- Background sessions read settings from the directory they run in (project `.claude/settings.json` applies normally).
- Denying a built-in tool in `settings.json` (e.g., `deny: ["EnterWorktree"]`) removes that tool from the session's tool surface entirely — the model doesn't have it available to call, not just refused at call site. A session that needed `EnterWorktree` for auto-isolation under the deny improvised by writing to its job dir (`~/.claude/jobs/<id>/`), which sits outside the working directory and is exempt from the "write outside cwd" auto-isolation trigger.
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

Most GitHub operations are PAT-reachable; the only thing standing between today's auth and N1a is `git push`.

## What we don't know (experiments needed)

This list was drafted across earlier sessions and may not all hold up under fresh eyes. Treat each row as provisional — reassess whether the question is still right, whether the experiment is still worth running, and what new experiments belong here as understanding deepens.

Run before any design or implementation decisions. Numbered for reference.

| # | Unknown | Why it matters | Experiment |
|---|---|---|---|
| U3 | What lookup affordances does agent view ship with, and what session-state files exist to support them? Sub-questions: (a) agent view input filters documented are `a:<agent>`, `s:<state>`, `#<PR>`, `@<repo>` — does anything else work (display-name substring, cwd, intent)? (b) What fields appear in `~/.claude/jobs/<id>/state.json` across session origins (agent view dispatch, `/bg` from interactive, `claude --bg`)? (c) What does `claude agents --json` output look like across the same set? | R3 is satisfiable by lookup, not naming. We need to see which native lookup paths exist before deciding whether anything custom is needed. | Dispatch 2–3 sessions with realistic-shaped prompts. Observe: row titles, state.json contents, `claude agents --json` output, and which filter strings narrow the list. |
| U4 | Can `worktree.bgIsolation` live in user-global `~/.claude/settings.json`, or must it be per-project? | Determines whether the setting goes in dotfiles once or in every repo. | Put it in global only; dispatch a session in a fresh repo without project settings; observe whether auto-isolation fires. |
| U5 | Can a session rename itself programmatically (e.g., set display name to `<issue>-<slug>` after loading the issue), or is naming only `--name` at dispatch and `Ctrl+R` interactively? | Determines whether R4 (human-readable rows) requires user keystrokes or can be automatic. | Inside a dispatched session, look for a `claude` subcommand, MCP-style hook, or skill primitive that renames the current session. |
| U6 | What happens if you re-invoke `/sdd <N>` inside an already-attached session that's already in its worktree? | Cross-phase continuity may want this. The current dispatcher's `git worktree add` would fail (already exists); glob-resolution branch should succeed. Needs confirmation. | Dispatch `/sdd 4`, let it land in a worktree, attach, re-invoke `/sdd 4`. |
| U7 | Does `/bg` from an interactive session preserve the branch and worktree state, or create a new worktree on backgrounding? | Affects whether a manual terminal session can be promoted into agent view mid-work. | Start `claude` in a manually-created worktree, run `/bg`, inspect the resulting agent-view session's worktree and branch. |
| U8 | Can a session self-pin (`Ctrl+T` equivalent from inside a skill)? | If yes, long-running skills can keep themselves hot. If no, pinning is a manual user step. | Investigate `claude` CLI subcommands and any in-session primitives. |

**Run U3 next** — it characterizes the lookup surface that R3 actually depends on.

## Deferred topics

Each deserves its own dedicated pass before final workflow design.

### Sandboxing and permissions

Sessions run mostly unsupervised. We need to understand the options at two different layers:

- **Claude Code permission system.** Default permission mode for autonomous sessions: `bypassPermissions` (faster, less safe), `acceptEdits` (curated), or explicit allowlist. Per-skill overrides.
- **OS-level sandboxing.** Network access, filesystem reach, process spawning. Available primitives on Fedora (Firejail, systemd-run with restrictions, Bubblewrap). Whether Claude Code can be invoked under a sandbox wrapper.

### `git push` autonomy

The single tap that gates N1a. We prefer to leave git push as requiring human yubikey tap, but want to understand the impact of this decision on our ability to run semi-autonomous agents in the agents view UI. We are open to re-evaluating this yubikey tap constraint based on cost benefit analysis.

R9 (main currency check) is independent of this decision — local `main` refresh still needs `git pull`, which taps under option 1 and PATs under options 2 or 3.

## Side Notes
**`EnterWorktree` / `ExitWorktree` permission deny in `dotfiles/dot-claude/settings.json`.** Currently lifted (the `deny` array and the accompanying `_denyNotes` field were removed from the `permissions` object) so sessions can call `EnterWorktree` and native auto-isolation works. Permanent removal vs restoration depends on (a) what directory and branch names auto-isolation picks, (b) how the SDD dispatcher's manual `git worktree add` interacts with auto-isolation enabled (two paths competing for the same outcome), (c) how cleanup behaves under Claude-created vs user-created worktrees (`Ctrl+X` ×2 deletes Claude-created including uncommitted changes).
  - **To restore:** in `dotfiles/dot-claude/settings.json`, add the following two fields back into the `permissions` object (alongside the existing `allow` array):
    ```json
    "deny": [
      "EnterWorktree",
      "ExitWorktree"
    ],
    "_denyNotes": "EnterWorktree/ExitWorktree denied so every session uses the manual worktree-per-issue flow in standards/workflow.md (git worktree add .claude/worktrees/<name> + cd) — uniform across agents, humans, and fresh terminals."
    ```