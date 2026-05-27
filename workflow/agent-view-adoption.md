# Claude Agents View Adoption

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
- Session display name controllable via `--name` at dispatch, or `Ctrl+R` interactively in agent view. Auto-generated from prompt otherwise — by a Haiku-class model, so not deterministic across repeated runs of the same prompt. `nameSource: "auto"` vs `"manual"` is recorded in `state.json`. **U5 confirmed these are the only paths:** no `claude` subcommand renames a running session (`attach`/`stop`/`logs`/`rm` don't, no other subcommand mentions naming); no in-session tool primitive renames the current session; editing the `name` field directly in `state.json` is ignored by the daemon (UI and `claude agents --json` continue to report the original name, `updatedAt` does not advance). State.json is a daemon-write-only checkpoint, not a config source.
- Filters in agent view input: `a:<agent>`, `s:<state>` (including `s:blocked`), `#<PR-number>` or PR URL.

### Goal-driven sessions

- `/goal <condition>` is a Claude Code UI command (v2.1.139+). It sets a session-scoped completion condition; after each turn, a small fast model (default Haiku) judges the condition against the conversation transcript and either ends the session or starts another turn.
- **User-only — cannot be invoked by an agent.** Confirmed via Skill-tool attempt: returns *"goal is a UI command, not a skill. Ask the user to run /goal themselves — it cannot be invoked via the Skill tool."* The runtime processes `/goal`, not the Skill surface.
- **Dispatcher-position invocation.** Type `/goal <condition>` into agent view's input to dispatch a new background session with the goal pre-loaded. The condition itself becomes the first-turn directive — no separate prompt needed.
- **Skill chaining works under a goal.** A single goal-driven session can invoke multiple skills sequentially. Verified in this workspace: a `/goal` session was instructed to invoke `/sdd-tdd` then `/sdd-design` and report contents; both `Skill(...)` calls succeeded in the same turn before the goal evaluator confirmed completion.
- **Evaluator is text-only.** Judges only what the agent has surfaced in the transcript; does not call tools. Conditions must therefore name both the proof shape (e.g., a literal `DONE:` line the skill prints) and a stop-clause (e.g., "or stop after 30 turns") to bound runaway loops.
- Survives `--resume`/`--continue` (with reset turn counter and timer); cleared by `/clear`. Disabled when `disableAllHooks` is set or the workspace is untrusted.

### Worktree mechanism

- Auto-isolation triggers **before first edit**, not at session start: Claude moves the session into a worktree under `.claude/worktrees/`.
- Native naming scheme (observed in v2.1.150): the directory gets a 3-word adjective-adjective-noun slug (e.g., `quiet-exploring-waterfall`); the branch is that slug prefixed with `worktree-` (e.g., `worktree-quiet-exploring-waterfall`). Branched from current HEAD. No tie to the prompt, intent, session name, or any issue — does not satisfy R3.
- Auto-isolation **skipped** when any of:
  - Session is already inside a linked git worktree (Claude-created or user-created via `git worktree add`).
  - Working directory is not a git repository and no `WorktreeCreate` hook is configured.
  - The write target is outside the working directory.
- Disable knob: `worktree.bgIsolation: "none"` in `.claude/settings.json`. **U4 confirmed global scope works:** setting `"worktree": {"bgIsolation": "none"}` in `~/.claude/settings.json` (with no project-level override in the test repo) suppressed auto-isolation for a background session dispatched from agent view typed input — the session wrote its probe file directly to the repo root, `cwd` stayed equal to `originCwd`, and `.claude/worktrees/` remained empty. The setting can live in dotfiles once. Requires Claude Code v2.1.143+.
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

- `~/.claude/jobs/<short-id>/state.json` holds per-session metadata. **Only background sessions get a folder;** interactive sessions appear in `claude agents --json` but have no `state.json`. Observed fields (v2.1.150; U3 confirmations marked):
  - `intent` — verbatim copy of the text typed into agent view's input box. U3 confirmed for both `/orient` and a long free-text prompt; both stored unchanged.
  - `name`, `nameSource` — display name shown in agent view rows; `auto` when generated by the Haiku-class namer, `manual` after `--name` or `Ctrl+R`. U3 observed: `auto` names are semantic paraphrase, not literal substring of `intent` — `/orient` → "dev-playbook orientation"; "U3 experiment: list the top-level entries…" → "repo structure overview." The literal "U3" did not reach `name`.
  - `daemonShort` — 8-char short ID used by `claude attach`, `claude logs`, `claude stop`, `claude rm`; matches the directory name under `~/.claude/jobs/`.
  - `sessionId`, `resumeSessionId` — full UUIDs; the transcript jsonl lives at `~/.claude/projects/<encoded-cwd>/<sessionId>.jsonl`.
  - `originCwd`, `cwd` — original dispatch directory vs current working directory. U3 confirmed equal when no auto-isolation fires (no-edit prompts); divergence under auto-isolation is documented but not exercised in U3.
  - `state`, `detail`, `tempo`, `inFlight`, `output.result` — runtime status fields driving agent view rows and the peek panel.
  - `template`, `respawnFlags`, `backend`, `cliVersion`, `createdAt`, `updatedAt`, `firstTerminalAt` — infrastructural.
  - `children` (null in both U3 rows), `linkScanOffset`, `linkScanPath` — present in U3 outputs but not previously enumerated; purpose not investigated.
- `~/.claude/jobs/<short-id>/timeline.jsonl` — append-only event log per session.
- `~/.claude/jobs/pins.json` — the pin set.
- `~/.claude/daemon.log`, `~/.claude/daemon/roster.json` — supervisor-level state.

`claude agents --json` returns a thinner projection than `state.json`. U3-confirmed fields per entry: `pid`, `cwd`, `kind` (`interactive`/`background`), `startedAt`, `sessionId`, `name`, `status` (observed values: `busy`, `idle`). Absent from `--json` but present in `state.json`: `intent`, `originCwd`, `daemonShort`, `nameSource`, `state`/`detail`/`tempo`. A consumer needing `intent` (the verbatim typed prompt) must read `state.json` files directly.

**Agent view input filters.** Documented: `a:<agent>`, `s:<state>` (incl. `s:blocked`), `#<PR-number>` or PR URL, `@<repo>`. U3 spot-checks (not exhaustive):

- `s:idle` returned "no sessions match" despite both rows being idle elsewhere (`status: "idle"` in `--json`, `tempo: "idle"` in state.json). `idle` is not the accepted value for `s:` here; the working vocabulary is not yet enumerated.
- `s:done` left both rows visible. Indistinguishable from "ignored" vs "matches both rows' `state: "done"`" from this single test.
- `intent:U` and `intent:U324kl4532jlkljk24lkjr` both showed all rows. Either `intent:` is not a recognized prefix, or it is recognized but does not substring-search. Either way, intent-based lookup is not reachable from the input box.

**Implication for R3.** The filter box is not on the access path for issue→session lookup, and the row counts this workflow targets are small enough that filtering is not a design requirement — visual scan of agent view's rows is the intended access pattern. That couples R3 to R4: row titles must be legible per-issue, and today's Haiku-paraphrase `name` does not guarantee the issue number appears. **U5 closed the post-dispatch fix:** a running session cannot rename itself. R4 from agent view typed input therefore narrows to three paths — accept Haiku names, `Ctrl+R` after dispatch (manual, one-time per row), or dispatch from a shell wrapper that passes `--name` (trades the primary-entry-point principle for an automatic title). A programmatic fallback against `state.json` exists if visual scan proves insufficient: `jq 'select(.intent | contains("17"))' ~/.claude/jobs/*/state.json`.

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