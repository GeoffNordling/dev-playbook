# Workflow

Standard workflow for how ideas become merged PRs in a workspace repo.

## State machine

Every issue is tagged with a four-tuple of labels: `(category:*, mode:*, tests:*, phase:*)`. All four are always present. The state of an issue is the `(mode, tests, phase)` sub-triple — each node below is one reachable combination. Category is required metadata but does not affect routing.

- `category:*` — `category:bug` (broken or incorrect) or `category:enhancement` (new behavior or improvement; covers everything that isn't a bug, including docs, config, refactors, and chores). Picked at intake.
- `mode:*` — `mode:sdd` or `mode:direct`. Picked at intake.
- `tests:*` — `tests:yes` or `tests:no`. Picked at intake. `mode:sdd` always carries `tests:yes`; `mode:direct` is split — testable work goes `tests:yes` (routed to `tdd`), doc/config/work not touching tests goes `tests:no` (routed to `build`).
- `phase:*` — the current node in the graph below. The graph is the inventory; see [Naming](#naming).

### Valid labels

[bootstrap-labels](~/workspace/dev-playbook/tools/bin/bootstrap-labels) mints exactly these. Six fixed-value labels enumerated below, plus all `phase:*` labels derived from graph nodes per [Naming](#naming).

| Dimension | Label | Meaning |
|---|---|---|
| Category | `category:bug` | Something is broken or incorrect. |
| Category | `category:enhancement` | New behavior or improvement; covers everything that isn't a bug. |
| Mode | `mode:sdd` | SDD path: spec → design → TDD ceremony. |
| Mode | `mode:direct` | Direct path: no spec/design ceremony. |
| Tests | `tests:yes` | Issue involves writing or modifying tests. |
| Tests | `tests:no` | Issue does not touch tests. |

### Graph-based flow

Each node also has two attributes: `(actor ∈ {agent, human}, role ∈ {work, review})`. Four kinds:

- `(agent, work)` — agent produces output (e.g., `sdd_tdd`, `tdd`, `build`)
- `(agent, review)` — agent reviews work, attaches findings (e.g., `sdd_agent_spec_review`, `agent_code_review`)
- `(human, work)` — human produces output (e.g., `intake`, `sdd_requirements`, `sdd_design`)
- `(human, review)` — human reads and decides (e.g., `sdd_human_spec_review`, `human_code_review`)

```mermaid
%%{init: {'flowchart': {'defaultRenderer': 'elk'}}}%%
flowchart LR
    start([ ]) --> intake[intake]
    intake -->|mode:sdd| sdd_requirements[sdd_requirements]
    intake -->|mode:direct, tests:yes| tdd[tdd]
    intake -->|mode:direct, tests:no| build[build]

    subgraph sdd[SDD path]
        sdd_requirements -->|design| sdd_design[sdd_design]
        sdd_design -->|draft| sdd_agent_spec_review[sdd_agent_spec_review]
        sdd_agent_spec_review -->|attach review| sdd_human_spec_review{sdd_human_spec_review}
        sdd_human_spec_review -->|reject: review again| sdd_agent_spec_review
        sdd_human_spec_review -->|reject: rework| sdd_design
        sdd_human_spec_review -->|approve| sdd_tdd[sdd_tdd]
        sdd_tdd -->|open PR| sdd_agent_code_review[sdd_agent_code_review]
        sdd_agent_code_review -->|attach review| sdd_human_code_review{sdd_human_code_review}
        sdd_human_code_review -->|reject: review again| sdd_agent_code_review
        sdd_human_code_review -->|reject: rework| sdd_tdd
    end

    subgraph direct[Direct path]
        tdd -->|open PR| agent_code_review[agent_code_review]
        build -->|open PR| agent_code_review
        agent_code_review -->|attach review| human_code_review{human_code_review}
        human_code_review -->|reject: review again| agent_code_review
        human_code_review -->|reject: rework| tdd
        human_code_review -->|reject: rework| build
    end

    sdd_human_code_review -->|approve: merge| done([merged])
    human_code_review -->|approve: merge| done
```

### Naming

Phase labels and slash-commands derive from graph node ids by `_`→`-`. Example: node `sdd_agent_spec_review` → label `phase:sdd-agent-spec-review`, command `/sdd-agent-spec-review`. The set of graph nodes IS the phase-label inventory.

Each work or agent-review node's skill updates the issue's `phase:*` label to the next node when it finishes. The three human-review nodes share one skill, `/human-review`: it reads the `phase:*` label to place itself, lays out the prior agent review and the artifact, and executes the human's verdict — advancing on approve (merging the PR at a code node), or routing the label back to an earlier node on `reject` (`review again`, `rework`). This is the one command whose name does not derive from a node id: it serves `sdd_human_spec_review`, `sdd_human_code_review`, and `human_code_review` at once. The human launches every node (per [Dispatch](#dispatch)) — nothing launches itself.

One long-lived branch and PR per issue. The branch is built up across phases in the issue's worktree (see [Worktrees](#worktrees-and-branches)); the PR opens on the `open PR` edge — after the human pushes the branch — and is merged on `approve: merge` via `gh pr merge`.

## Worktrees and branches

An issue's phases run as separate sessions, but they build one continuous line of work. Continuity and isolation both come from giving each issue its own **git worktree** — a second working directory with its own branch checked out, sharing the repo's object store.

### The per-issue worktree

- **One worktree, one branch, one PR per issue,** at `<repo>/.claude/worktrees/issue-<N>` on branch `issue-<N>` (`N` is the issue number).
- **It persists across the issue's phases:** the first phase creates it, and every later phase re-enters the same worktree and inherits all prior commits.

### The contract every file-touching phase follows

- **Create** — the first phase opens the worktree, gated on a tap-free check that local `main` matches origin (`git rev-parse origin/main` against `gh api …/branches/main`); a stale base escalates, since pulling is the human's. It creates with `EnterWorktree(name=issue-<N>)` and renames the branch to the bare `issue-<N>` — the `worktree-` prefix appears to be what agent view's cleanup keys on, so dropping it lets the worktree outlive a torn-down session.
- **Adopt** — every later phase re-enters the same worktree by path (`EnterWorktree(path=.claude/worktrees/issue-<N>)`) and inherits all prior commits. A missing worktree escalates: the issue's work is gone.
- **Release** — every phase closes with `ExitWorktree(keep)`, which leaves the worktree and branch for the next phase. The merge node removes them when the issue lands.

### The two-tap boundary

Only two operations touch the GitHub SSH remote and so need the human's YubiKey; both are the human's, in their own terminal. Everything else is tap-free and lives in a skill.

| | Tap | Owner |
|---|---|---|
| `git push` (publish the branch at `open PR`) | **yes** | human |
| `git pull` (keep local `main` current) | **yes** | human |
| `gh pr create` / `gh pr merge` / `gh api` / `gh issue` / `gh pr diff` | no | skills |
| commit, `EnterWorktree`/`ExitWorktree`, `git branch -m`, `git worktree remove` | no | skills |

Consequences that shape the skills:

- **The implementation phase never opens the PR.** It cannot push, and a finger-on-the-wheel skill cannot pause mid-run to wait for a tap. So it commits, releases the worktree, advances its label, and ends `DONE` with a reminder to push. The PR is created downstream, after the push.
- **The push is the human's transition ritual.** Seeing implementation `DONE`, the human runs `git push -u origin issue-<N>` (one tap) and then launches the code-review phase.
- **The PR is born at code review.** `/open-pr` (first link of the code-review goal) creates it with `gh pr create` once the branch is on origin — tap-free, in a skill. If the branch isn't pushed yet, `/open-pr` escalates rather than guessing.
- **Cleanup is the merge node's job.** On `approve: merge`, `/human-review` runs `gh pr merge --squash --delete-branch` (drops the origin branch), then removes the local worktree and branch: `git worktree remove .claude/worktrees/issue-<N>` and `git branch -D issue-<N>`.

## Dispatch

The human dispatcher operates from Claude Code's "claude agents" dashboard. Every input typed into the dashboard launches a new background session; the prompt is delivered as that session's first user message, and a prompt beginning `/<skill>` model-invokes the skill. There is no master agent. The dashboard spans repos, so each session's row should read `repo#N · phase` to stay legible across parallel issues. Anthropic subscription billing requires interactive sessions, so every node entry is human-launched.

**One session, one node — nodes do not auto-advance.** A node skill enters the issue's worktree, does its work, commits, releases the worktree, and updates the issue's `phase:*` label to the next node's label, then stops and returns control to the dashboard. It never launches the next node. The human reads the issue's new phase and launches the matching skill. Every transition stays human-gated and visible on the live dashboard. Parallel issues run as independent sets of sessions, each in its own worktree; git keeps them from colliding.

The two modes invoke differently. **FOTW skills run hands-off under `/goal`**, which pairs the action with proof and a stop-clause. A FOTW skill yields control only by printing a **terminal line** — `DONE:` (work complete) or `ESCALATE:` (blocked, needs a human call) — and the goal condition stops on either:

```
/goal Run /<skill> <args> until it prints a terminal line — DONE: or ESCALATE: — or stop after N turns.
```

`/goal` is a user-only UI command; an agent cannot invoke it. It re-drives the session after every turn until its condition holds, so *every* exit must be a recognized terminal line — a skill that merely paused to ask a question would be re-driven past it. Its evaluator is text-only (it judges the transcript, calls no tools), which is why a condition must name both the proof shape (the literal `DONE:`/`ESCALATE:` line) and a turn cap. The evaluator matches the literal prefix, clears the goal, and the session idles, visible to the human at the dashboard. **HITL skills are launched directly as `/<skill> <args>`** with the human engaged throughout; they close with a plain report and need no `/goal` wrapper or terminal line.

## Permissions

Tool access is governed by a tiered settings hierarchy. Rules at every level merge into one effective ruleset; **deny wins anywhere** — a deny at any level blocks the call regardless of allows elsewhere.

| Level (highest precedence first) | File / Source | Our use |
|---|---|---|
| Managed | `/etc/claude-code/managed-settings.json` | Not used (not enterprise). |
| CLI args | `claude agents --permission-mode dontAsk …` | **Sets FOTW mode for dispatched sessions only**, leaving personal `claude` sessions in their normal mode. |
| Local | `<repo>/.claude/settings.local.json` | Rare; gitignored personal exceptions. |
| Project | `<repo>/.claude/settings.json` | Repo-specific allow rules. |
| User | `~/.claude/settings.json` | `Skill()` gates for the skills `/goal` launches, plus narrow backstop for built-in skills. Stow-linked from `dotfiles/dot-claude/`. Benign for personal sessions — never sets mode. |

**Mode: `dontAsk`, set at agent-view startup** via `claude agents --permission-mode dontAsk`. Auto-deny anything not pre-approved; never prompt. Applies to every dispatched session (HITL and FOTW); personal `claude` sessions are unaffected. Trades upfront allow-list enumeration for runtime determinism.

Allow rules live at two levels, split by one question — **who invokes the skill or tool:**

- **Per-skill `allowed-tools` front-matter is self-sufficient under `dontAsk`.** A skill's own grants — bash, edits, the worktree tools (`EnterWorktree`, `ExitWorktree`), and sub-skills (`Skill(child)`) — run for the skill's lifetime with no settings.json duplicate, even for a tool that appears in settings.json nowhere. This is the **per-skill permission set** in the [skill table](#skills). Additive, scoped to the skill's lifetime; cannot override a deny.
- **User-level allow holds only the `Skill(name)` gates front-matter can't carry** — the skills `/goal` launches or chains. `/goal` drives a session with no front-matter of its own, so its `Skill(…)` call is gated by `dontAsk`, and a settings.json gate is the only place to allow it. A skill the human launches by typing `/<skill>` is never gated, and a sub-skill rides on its parent's front-matter — so neither needs an entry here. A narrow bash backstop for built-in skills (e.g., `/code-review`'s `Bash(gh pr diff *)`) lives here too.

**Bash baseline.**

- *Auto-allowed in every mode, no rule needed:* `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` forms.
- *User-level allow for universally-trusted mutators:* `Bash(mkdir *)`, `Bash(touch *)`, `Bash(mv *)`, `Bash(cp *)`.
- *`rm` is not yet user-allowed.* Each session works inside the issue's worktree (`.claude/worktrees/issue-<N>`), which cwd-bounds it — sufficient practical confinement (a soft boundary, not an OS jail). Code-writing skills will likely need `rm`; not yet committed.

A transition a skill performs — the `phase:*` label update, plus any commit, worktree, or PR action — is covered by that skill's `allowed-tools`. Transitions the human performs (the two taps — `git push`, `git pull` — and the merge verdict) need no encoding.

Canonical rule syntax and edge cases: [permissions docs](https://code.claude.com/docs/en/permissions).

## Skills

Three modes of human engagement exist in theory; only two are available under the [Dispatch](#dispatch) model:

- **Human in the loop (HITL)** — human is actively engaged throughout, spending real time and focus. Use this for stages that focus on extracting human intent. Examples: initial issue creation and writing specs.
- **Finger on the wheel (FOTW)** — skill is designed to run hands-off; human is present only because billing requires it. Agent does the work; human invokes the skill and responds to escalations. Examples: implementing code, performing agent reviews.
- **Hands off the wheel (AFK)** — agent runs autonomously, no human involvement. *Not available* — see [Dispatch](#dispatch). We would use this if we could.

Direct-path work splits by `tests:*`. `/tdd` mirrors `/sdd-tdd` for testable Direct work; `/build` handles non-test work — docs, config, chores. Both feed shared `agent_code_review` and `human_code_review`.

### Node-skill contract

Across modes, a node skill copies its `allowed-tools` verbatim from the [table](#skills) below. When it has required reading, it front-loads a `## Read first` section ending in a `READ: <files>` confirmation; when it has none, it omits the section entirely. Mode fixes the rest — see [Dispatch](#dispatch) for the launch and termination mechanics. This contract fixes structure; the authoring *style* behind the skills — voice, content, robustness, mechanics — lives in [skill-authoring.md](~/workspace/dev-playbook/workflow/skill-authoring.md).

- **Worktree.** Every file-touching node enters the issue's worktree before doing anything else and releases it with `ExitWorktree(keep)` at close, per [Worktrees](#worktrees-and-branches). First phases (`sdd_requirements`, `tdd`, `build`) create-and-rename; later phases adopt by path. `intake` touches no files and has no worktree.
- **HITL** — the human is engaged throughout, so the body may gate on interviews and approvals, and the skill terminates with a plain report. Escalation is `—`: the human is already present.
- **FOTW** — the skill runs hands-off, so it terminates by printing a deterministic terminal line and declares its escalation triggers in the table. The line is `DONE:` on success or `ESCALATE:` when blocked. Escalation is a terminal line, not an in-place wait: under `/goal` the session is re-driven each turn until a terminal line appears, so to escalate is to print `ESCALATE:` and yield.

| Skill | Mode | Permissions set (`allowed-tools`) | Escalation triggers |
|-------|------|-----------------------------------|---------------------|
| `/intake` | HITL | `Bash(gh issue *)` `Bash(gh label *)` `Skill(grill-with-docs)` | — |
| `/sdd-requirements` | HITL | `Bash(gh issue *)` `Bash(gh api *)` `Bash(git *)` `EnterWorktree` `ExitWorktree` `Edit` `Write` `Skill(grill-with-docs)` `Skill(commit)` | main behind origin (stale base) |
| `/sdd-design` | HITL | `Bash(gh issue *)` `EnterWorktree` `ExitWorktree` `Edit` `Write` `Skill(grill-with-docs)` `Skill(commit)` | issue worktree missing |
| `/sdd-tdd` | FOTW | `Bash(gh issue *)` `Bash(git *)` `EnterWorktree` `ExitWorktree` `Edit` `Write` `Skill(commit)` | Interface amendment / spec gap; blocking ambiguity; issue too big for one session; test red after 2 attempts; issue worktree missing |
| `/tdd` | FOTW | `Bash(gh issue *)` `Bash(gh api *)` `Bash(git *)` `EnterWorktree` `ExitWorktree` `Edit` `Write` `Skill(commit)` | Brief wrong or underdetermined; issue too big for one session; test red after 2 attempts; main behind origin (stale base) |
| `/build` | FOTW | `Bash(gh issue *)` `Bash(gh api *)` `Bash(git *)` `EnterWorktree` `ExitWorktree` `Edit` `Write` `Skill(commit)` | Brief wrong or underdetermined; issue too big for one session; work needs tests (mis-triaged); main behind origin (stale base) |
| `/open-pr` | FOTW | `Bash(gh pr *)` `Bash(gh issue view *)` `Bash(gh api *)` `Bash(git *)` | branch not pushed to origin |
| `/sdd-agent-spec-review` | FOTW | `Bash(gh issue view *)` `Bash(gh issue comment *)` `Bash(gh issue edit *)` `Bash(make *)` `EnterWorktree` `ExitWorktree` | Consistency gate red (malformed spec); specs absent/unreadable; issue worktree missing |
| `/sdd-agent-code-review` | FOTW | `Bash(gh issue view *)` `Bash(gh issue edit *)` `Bash(gh pr view *)` `Bash(gh pr diff *)` `Bash(gh pr comment *)` `Bash(make *)` `EnterWorktree` `ExitWorktree` | Green gate red (PR over red tree); PR/diff missing; issue worktree missing |
| `/agent-code-review` | FOTW | same as `/sdd-agent-code-review` | Green gate red (PR over red tree); PR/diff missing; issue worktree missing |
| `/human-review` | HITL | `Bash(gh issue view *)` `Bash(gh issue edit *)` `Bash(gh issue comment *)` `Bash(gh pr view *)` `Bash(gh pr diff *)` `Bash(gh pr merge *)` `Bash(git worktree *)` `Bash(git branch *)` | — |

**Compound dispatch — the code-review nodes.** `sdd_agent_code_review` and `agent_code_review` each run three steps in one FOTW goal: `/open-pr` creates the PR from the just-pushed branch (tap-free), the native `/code-review` posts its automated bug/regression findings as a PR comment, then our skill adds the spec-fidelity and convention findings the native pass does not cover (also a PR comment). Ours runs last so its label advance means all three are done, and so it can read the native comment and skip re-flagging. The goal chains them:

```
/goal Run /load-issue <issue>, then /open-pr <issue>, then /code-review <pr>, then /sdd-agent-code-review <issue> — stop when /sdd-agent-code-review prints a terminal line (DONE: or ESCALATE:), or after N turns.
```
