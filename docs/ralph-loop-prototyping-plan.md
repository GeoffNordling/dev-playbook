# Ralph-Loop Prototyping — Session State & Plan

**Status:** In progress. This is a stateful handoff document compressing what was
decided and learned in one working session. The plan is intentionally a *sketch*
— it is to be developed further in a future session. A fresh agent should be
able to resume from this file alone.

**Scope note:** This document is *only* about using the official **`ralph-loop`**
Claude Code plugin to run pseudo-autonomous prototyping. Anything else, including `workflow/workflow.md`, is explicitly out of scope here and has been dropped.**

---

## 1. Goal and purpose

Enable a class of "vibe-coded" projects that the user wants to exist but does not
have time to focus on. The user delegates an extreme amount of responsibility to
the agent, in an automated way, and stays at the level of a requirements-gatherer
who reviews output and gives feedback — not an implementer.

The operating loop is: **kick off → the agent does a lot of work (spends tokens)
→ it comes back with something → the user reviews and reacts.** The official Ralph
loop plugin is the chosen engine for the "does a lot of work" middle.

## 2. The user's intentions about prototyping

- **Claude owns most of the work.** The user puts in very little effort.
- **Pseudo-autonomous, not autonomous.** The user is *present* (attended-async):
  available, not watching every step. They would prefer the agent have full AFK autonomy, but Claude Code subscription billing forces interaction sessions.
- **Low confidence in the output by design.** Because the user did not invest
  effort, they will not trust the result. The output must stay **quarantined from
  production code until it is time** to integrate.
- **The user is the requirements-gatherer / product designer.** Focus on *what*
  and *how it should behave*, not *how it is built*; then review, test, and refine
  the requirements.

## 3. Requirements for how prototypes go (locked constraints)

- **Subscription billing only.** Authenticate via `CLAUDE_CODE_OAUTH_TOKEN`
  (minted by `claude setup-token`). **Headless / API billing is 100% off the
  table** — it costs too much versus the subscription. This is a hard constraint
  and rules out the classic headless bash-loop form of Ralph.
- **Interactive TUI sessions.** The viable subscription path. (Headless `claude -p`
  on a subscription burns quota too fast and is rejected.)
- **Bare-metal, broad scoped permissions.** Stay simple: run on the host with a
  broad `permissions.allow` list so the loop is not constantly blocked, **without**
  `--dangerously-skip-permissions`. No Docker sandbox. (A network-contained
  sandbox was considered and rejected for now in favor of simplicity. Revisit only
  if a prototype turns executable + networked and is left unattended.)
- **Worktree isolation via the Claude agents dashboard.** Each run is isolated in
  its own git worktree; the user monitors from the dashboard.
- **Prototypes live in their associated existing repos** — not in a separate
  prototypes repo, and not scattered ad hoc. Quarantine mechanism:
  - A **top-level `prototypes/<name>/` directory** on `main`, one self-contained
    sub-project per prototype (its own `src/`, `tests/`, `pyproject.toml`, or just
    a brief, as needed).
  - **Not** `src/prototypes/` — that would put it on the package import path,
    enabling the integration we are trying to prevent. Keep it a *sibling* of
    `src/`.
  - Prototype code **may merge to `main`** but is **not integrated into production
    code** until it is time. Production code does not import from `prototypes/`.
  - **Deferred:** a mechanical one-way import guard (a hook that fails if `src/`
    imports `prototypes/`) — "option 3." Acknowledged as possibly needed, but not
    worth building now.
- **`/goal` usage convention:** structural *completion-contract* conditions for
  conceptual work (a checker can verify an artifact's *shape*, never its *quality*),
  and mechanical conditions ("tests pass / it runs") for executable prototypes.
  *(How `/goal` relates to the plugin's own `<promise>` stop condition is an open
  question — see §8.)*

## 4. What the community discussion said (claims and reported flaws)

Captured without attribution — these are the statements and criticisms that were
raised, to be checked against the plugin's actual current behavior in §5.

**What Ralph is:**

- Ralph runs a CLI coding agent in a continuous loop so it keeps working instead
  of stopping too early. Simple but effective.
- It reframes the human as the requirements-gatherer: you specify *what* the end
  state should look like; the agent works the list down.
- A comprehensive, actionable task with clear success criteria is often completed
  in a single iteration; a vague one-liner spawns many iterations.

**The central criticism — plugin vs. bash loop:**

- The official Claude Code Ralph plugin "runs everything in a single context
  window" and "is triggered by a stop hook," and the stop hook "isn't even
  triggered at compaction." As tasks pile up, context bloats, hallucinations
  increase, and you may have to stop and manually compact mid-run.
- The original bash loop (Geoffrey Huntley) "starts a fresh context window each
  iteration." This is described as the fundamental difference and as better for
  long-running tasks — at the cost of being headless and harder to set up/observe.
- Blunt verdict offered: "if you're not gonna use the bash loop, don't use the
  plugin."
- Trying to modify the prompt or the Ralph skill to force a clean loop was
  described as "problematic."

**Recommended setup practices:**

- **Safety:** use a sandbox so you can grant broad permissions ("yolo mode")
  without risking the host. A worktree isolates *files* but not the *system*; a
  container also prevents nuking a DB or installing unwanted libraries.
- **Efficiency:** keep a `plan.md` and an `activity.md`/`progress.txt`; give the
  agent a clear task list it can follow and update; format inspired by Anthropic's
  "effective harnesses for long-running agents." Use git.
- **Cost:** set max iterations — the plugin defaults to unlimited; start at 10–20.
  Subscription usage is consumed fast; a Max plan can be exhausted before the week
  ends. (Huntley reportedly had free tokens.)
- **Feedback loop:** give the agent browser automation (Playwright headless, or
  Claude for Chrome) so it can verify its own work — screenshots, console logs,
  end-to-end checks.

**State-file pattern described in detail:**

- A `PRD.json` with a `passes: true/false` flag per user story — simultaneously a
  to-do list, a product-requirements document, and a verification contract.
- A `progress.txt` append-only free-text log of learnings = the agent's memory for
  the sprint; deleted at sprint end. **Append, not update** (update rewrites the
  whole file).
- Per-iteration prompt steps: find the highest-priority feature, work on **only**
  that one feature, update the PRD (mark `passes: true`), append progress, and
  **git commit** — each iteration produces a commit, so git history + progress
  file are the durable memory.
- Keep tasks **small**; one big task gets swallowed and the agent gets "dumber" as
  the context fills. A "promise complete" sentinel breaks the loop early when the
  PRD is done.
- Robust feedback loops are essential; type-check and tests must stay green each
  commit; small tasks preserve context budget for verification (browser automation
  is context-expensive). It was noted that the agent tends to mark features
  complete without proper testing unless explicitly told to verify end-to-end as a
  human user.

**Skepticism raised:**

- Mega-PRs from overnight runs are hard to review; a team would reject them.
- An early mistake can compound across the whole run.
- It removes the expert from the loop exactly where their guidance matters most.
- Seen as best for solo developers on vanilla apps; doubtful for complex or team
  codebases. It is "not fully automated" — more like managing a team of developers
  whose PRs you review (split work into non-conflicting PRs; write specs/tests;
  re-run with review comments).
- Some report the agent finishes their tasks in one shot, so they see little value
  over a good upfront plan/spec.
- An orchestrator + subagents can run the outer loop in *separate* context windows
  per task, sidestepping the single-window problem.
- The plugin is "too flexible," which invites misuse; enforcing a plan phase +
  implementation phase (as the original shell script does) was said to give more
  consistent results.

## 5. Criticisms vs. the official `ralph-loop` plugin (confirm / deny, current state)

Grounded in a primary-source read of the plugin (see §7 for where to verify).
"Confirmed" = read in the source; "Inferred" = follows from the architecture but
not stated in the plugin's docs.

**Plugin-specific claims:**

| Claim | Verdict | Basis |
|---|---|---|
| Runs in a single context window / one session | **TRUE (confirmed)** | One `Stop` hook re-injects the prompt into the *same* session via `decision:"block"`. It never spawns fresh sessions. |
| Driven by a stop hook | **TRUE (confirmed)** | `hooks/hooks.json` registers only a `Stop` hook → `hooks/stop-hook.sh`. |
| Stop hook is not triggered at compaction / no PostCompact → context bloats | **TRUE (confirmed mechanism; degradation inferred)** | Neither plugin registers `PreCompact` or `PostCompact`. The session grows every iteration; when auto-compaction fires there is no hook to re-ground the agent. **Nuance:** the *loop-control* state (iteration, prompt, promise) lives on disk and survives compaction, so the loop never loses its place — it is the agent's *in-conversation working memory* that erodes. So "the loop breaks" is false; "the agent's memory degrades over a long run" is true. |
| Defaults to unlimited iterations | **TRUE (confirmed)** | `max_iterations` defaults to `0` (= unlimited); the README says to always set `--max-iterations` as the primary safety mechanism. |
| Bash loop gets fresh context each iteration; the plugin does not | **TRUE (confirmed for the plugin)** | The plugin is single-session by design; `ralph-loop`'s `session_id` guard actively *prevents* continuing in a different session. Fresh-context behavior is only available in the (rejected) headless bash loop. |
| You must manually compact mid-run | **PARTIAL** | The underlying cause (no auto-reset, no PostCompact) is real. Manual `/compact` is *one* workaround, but it is **not required** if working memory is externalized to disk and re-read each iteration (see §6). |
| Forcing a clean loop via prompt/skill edits is problematic | **TRUE (effectively)** | No prompt can clear the context window; the plugin has no fresh-context option (a `--fresh-context` flag was reportedly proposed upstream but is not in the shipped behavior). So you cannot prompt your way to fresh context. |
| Single completion condition, exact-string match | **TRUE (confirmed)** | `--completion-promise` is matched literally against a `<promise>…</promise>` tag in the latest assistant message — one condition only. |

**Practice claims that are about *usage*, not plugin features** (the plugin does
not provide these; you must add them in your prompt/setup):

| Claim | Verdict | Basis |
|---|---|---|
| `PRD.json` + `progress.txt` conventions | **Not a plugin feature** | The plugin ships only a loop-control state file (`.claude/ralph-loop.local.md`), the `<promise>` sentinel, and `--max-iterations`. PRD/progress files are conventions *you* impose via the prompt. |
| Git commit per iteration | **Not a plugin feature (TRUE that it is absent)** | Not built in. Must be instructed in the prompt. |
| Browser-automation feedback loops (Playwright / Claude for Chrome) | **Not a plugin feature** | Orthogonal; you wire these up yourself. |
| Sandbox for safety | **Not provided; orthogonal** | The plugin has no sandbox. We have chosen bare-metal + scoped permissions and accept worktree (file-only) isolation. |

**General skepticism** (not facts about the plugin — caveats to weigh):

- Mega-PR review burden, compounding early mistakes, expert-out-of-loop, weak fit
  for complex/team codebases: these are **real risks of the *technique*** and are
  mitigated in our regime by (a) small tasks, (b) the quarantine in
  `prototypes/<name>/`, (c) the user reviewing output as the requirements-gatherer,
  and (d) low-stakes prototype subject matter. They are not reasons the plugin is
  broken.
- "Orchestrator + subagents in separate context windows" is a genuinely different
  architecture that *does* sidestep the single-window flaw; noted as a possible
  future direction, not the current plan.

**Two-plugin difference (answering "what is the difference"):**

- `ralph-wiggum` (in `anthropics/claude-code`, author Daisy Hollman) is the
  original demo. `ralph-loop` (in `anthropics/claude-plugins-official`, author
  Anthropic) is the productionized copy.
- The **only material code difference**: `ralph-loop` adds **`session_id`
  tracking** — it stamps the session ID into the state file and the hook refuses
  to act if the current session ID differs, so a stale state file cannot hijack an
  unrelated session. `ralph-loop`'s README also adds a "Prompt Writing Best
  Practices" section.
- Everything else is the same: `Stop`-only hook, `decision:"block"` + `exit 0`
  (neither uses `exit 2` or `stop_hook_active`), `<promise>` exact match,
  `--max-iterations` / `--completion-promise`, state file at
  `.claude/ralph-loop.local.md`.
- **Decision: use `ralph-loop`** — same mechanism, hardened with session isolation,
  which matters when running multiple prototype sessions.

## 6. How the plugin actually works (mechanism, for a self-contained read)

Each iteration: the agent works, then tries to end its turn → the `Stop` hook
(`stop-hook.sh`) fires and:

1. Reads `.claude/ralph-loop.local.md` (YAML frontmatter: `iteration`,
   `max_iterations`, `completion_promise`, and — in `ralph-loop` — `session_id`;
   the markdown body is the prompt to re-inject). **If the file is gone → `exit 0`,
   the loop ends.** (`/cancel-ralph` simply deletes the file.)
2. If `max_iterations` is reached, or the latest assistant message contains
   `<promise>EXACT TEXT</promise>` matching the configured promise → delete the
   state file and stop.
3. Otherwise → return `{"decision":"block","reason":<the prompt>,"systemMessage":
   <reminder>}`, increment the iteration on disk, and re-feed the prompt as a new
   turn **in the same session**.

**The two-memory model is the crux of the flaw and its fix:**

- **Loop-control memory** (iteration, prompt, promise) lives on disk and is
  re-read fresh every iteration → **immune to compaction.**
- **Agent working memory** (what was tried, what failed, decisions this run) lives
  only in the conversation → **eroded by compaction.**

Below the auto-compaction threshold, the flaw does not bite at all. Above it, the
mitigation is to **make disk the agent's memory too**: force every iteration to
re-read a progress/PRD file, do one small unit, write what it did + learned back,
and commit. Then the conversation is disposable scratch and compaction is
harmless. This recovers the bash-loop's anti-drift property without fresh context.

## 7. How to look up the raw details (sources a fresh agent can verify)

**Plugin source (primary, authoritative):**

- `anthropics/claude-code` → `plugins/ralph-wiggum/` — read:
  - `README.md`
  - `.claude-plugin/plugin.json`
  - `hooks/hooks.json`
  - `hooks/stop-hook.sh`  ← the loop logic
  - `commands/ralph-loop.md`, `commands/cancel-ralph.md`, `commands/help.md`
  - `scripts/setup-ralph-loop.sh`  ← writes the state file
- `anthropics/claude-code` → `.claude-plugin/marketplace.json` — marketplace
  `name` is `claude-code-plugins` (this is the install suffix for ralph-wiggum).
- `anthropics/claude-plugins-official` → `plugins/ralph-loop/` — same file set,
  plus `LICENSE`. This is the productionized version with `session_id` isolation.

**Fetch/verify methods:**

- Raw file, e.g.
  `https://raw.githubusercontent.com/anthropics/claude-code/main/plugins/ralph-wiggum/hooks/stop-hook.sh`
- `gh api` against the repos, or shallow `git clone` and read locally.
- Inspect the live loop state during a run at `.claude/ralph-loop.local.md`.

**Install:**

- ralph-wiggum: `/plugin marketplace add anthropics/claude-code` then
  `/plugin install ralph-wiggum@claude-code-plugins`.
- ralph-loop: `/plugin marketplace add anthropics/claude-plugins-official` then
  `/plugin install ralph-loop@claude-plugins-official`. *(The `@claude-plugins-official`
  suffix is inferred from the repo; confirm against that repo's `marketplace.json`
  `name` field.)*

**Official Claude Code documentation:**

- Plugins: the "discover plugins" / plugins documentation pages.
- Hooks guide: the `Stop` hook and the `decision:"block"` mechanism.
- `/goal` documentation, and `/loop` (scheduled-tasks) documentation, and the
  changelog entries introducing them.

**Background reading:**

- Anthropic engineering post: "Effective harnesses for long-running agents"
  (source of the PRD/progress-file pattern and the verify-as-a-human guidance).

**Caveat:** web-search summaries seen this session hallucinated several specifics
(the exact install suffix for ralph-wiggum, install counts, issue/PR numbers).
Trust the primary source files above over any summary.

## 8. Plan sketch (to be developed next session)

**Engine:** the official **`ralph-loop`** plugin, run in an interactive TUI
session on subscription auth. Headless bash-loop Ralph is rejected (cost). This
commits us to **single-session loops**; fresh-context Ralph is out of scope.

**The invariant that makes it work:** a disk-state convention that makes the
conversation disposable —

- a plan/PRD file (the to-do + behavior contract),
- an append-only progress log (the durable working memory),
- **git commit every iteration**,
- a per-iteration prompt that forces: re-read state from disk → do one small unit →
  write progress back → commit.

**Healthy-zone settings** (keep the run under the compaction threshold and robust
if it crosses):

- always pass `--max-iterations` (start 10–20; never unlimited),
- small, incremental tasks,
- a single exact `<promise>` completion sentinel, with an instruction never to emit
  it falsely to escape,
- externalize all state to disk + commit each pass.

**Quarantine:** prototypes in `prototypes/<name>/` (top-level, not under `src/`) in
their associated repos; not integrated into production until graduation; graduate
via a real repo/promotion when one earns it.

**Auth / permissions:** subscription `CLAUDE_CODE_OAUTH_TOKEN`; broad
`permissions.allow` list; no sandbox.

**Default mode:** pseudo-autonomous and attended — the user kicks runs and reviews
output, graduating individual prototypes to longer unattended runs as trust grows.

## 9. Decisions locked this session

- Pseudo-autonomous, attended-async — not full autonomy.
- Subscription billing only; headless/API rejected.
- Bare-metal + broad scoped permissions; no sandbox (simplicity).
- Worktree isolation via the Claude agents dashboard.
- Prototypes quarantined in top-level `prototypes/<name>/` (option 2); not under
  `src/`; not integrated into production until graduation.
- Import-membrane enforcement (option 3) deferred.
- Engine = official `ralph-loop` plugin (not `ralph-wiggum`, not the headless bash
  loop).
- Disk-state discipline is mandatory (it is the only mitigation for the single-
  session compaction flaw, given headless is rejected).
- `/goal` convention: structural-contract for conceptual, mechanical for
  executable.

## 10. Open questions for next session

- **`/goal` vs. the plugin's `<promise>` sentinel** — are both used, or is one
  canonical? The plugin already has a completion mechanism; `/goal` may be
  redundant or complementary. Resolve.
- **Re-orientation anchor** — a nested `prototypes/<name>/CLAUDE.md` is *lost* at
  compaction; only root `CLAUDE.md` (+ global rules + auto-memory) is re-injected.
  Leaning toward a thin pointer in the repo-root `CLAUDE.md` ("autonomous prototype
  sessions: re-read `prototypes/<name>/AGENT.md`") with the fat contract/state in
  the prototype dir — **proposed, not locked.**
- **Exact disk-state file layout** — PRD/plan format, progress-log format, and
  where the per-prototype contract lives.
- **The iteration-prompt template.**
- **The scoped-permissions allowlist contents** for unattended-enough runs.
- **Verification/feedback loop for conceptual (non-code) prototypes** — there is no
  "tests pass" for a design brief; what is the mechanical check?
- **Graduation** — when and how a prototype leaves `prototypes/` for a real repo.
- **Revisit option 3 (import membrane)** and the sandbox/network-egress question if
  a prototype turns executable + networked and is left unattended.
