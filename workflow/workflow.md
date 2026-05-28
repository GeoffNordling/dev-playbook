# Workflow

Standard workflow for how ideas become merged PRs in a workspace repo.

# Main Concepts That We Need to Flesh Out in Documentation Somewhere in ~/workflow/ Directory:
All pre-existing documentation, workflow standards, skills, tooling, etc. is open for modification, deletion, and addition. We are re-writing the workflow and are not bound by prior convention.

GH Issue labels are defined in a central location and relayed to GH via [bootstrap-labels](~/workspace/dev-playbook/tools/bin/bootstrap-labels). The label set must be refreshed for the new `(category:*, mode:*, tests:*, phase:*)` scheme.

Human and agents collaborate to move issues along the graph from beginning to end, with a spectrum of permissions and authority to take actions and transitions. This is supported by well-organized and factored /skills and /tools scripts. Many /skills and /tools will need modification to fit the new workflow.

Since Claude Code "claude agents" view relies on worktrees, we need to understand how worktrees are created, entered, exited, and deleted. Our old workflow relied on manual worktree creation and cleanup; we now expect to use to "claude agents" native worktree tooling. Make sure to have agents check that local Git is up-to-date with remote Git before launching new adventures.

Current system security constraints require user yubikey tap for both `git pull` and `git push`. We are open to relaxing this requirement but will keep it in place tentatively while we develop the workflow.

All state transitions, actions, metadata, for each issue, is tracked in a local SQLite DB so we can understand how our system performs.

Interested in a lightweight web browser view of the system. Something visually appealing and parsimonious I can view in my browser. For example, a colorful view of the graph that indicates where all my open issues are across entire GH account, and the states they are in. This would be a "live" view the same way Claude Code's "claude agents" view is live.

Will need a closed feedback loop to improve the workflow and skills over time. One idea: a skill to run at the of a workflow that looks back on the context, summarizes what went well, what went wrong, unexpected surprises, and lessons learned, then compresses and writes them to a database, with all associated metadata for the session. Another agent or workflow can watch at that higher level and guide workflow improvements over time.

The `/improve-codebase-architecture` skill seems very useful but was not integrated in the old workflow. Look for opportunities to integrate into new workflow.

Plan a pass over all skills to align with this workflow: update existing skills, author the ones referenced here but not yet on disk (`/tdd`, `/build`, `/sdd-agent-spec-review`, `/sdd-agent-code-review`, `/agent-code-review`), retire obsolete ones (`/sdd` dispatcher).

# Graph-based Flow

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

### Node attributes

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
        sdd_human_spec_review -->|reject: iterate| sdd_agent_spec_review
        sdd_human_spec_review -->|reject: redesign| sdd_design
        sdd_human_spec_review -->|approve| sdd_tdd[sdd_tdd]
        sdd_tdd -->|open PR| sdd_agent_code_review[sdd_agent_code_review]
        sdd_agent_code_review -->|attach review| sdd_human_code_review{sdd_human_code_review}
        sdd_human_code_review -->|reject: iterate| sdd_agent_code_review
        sdd_human_code_review -->|reject: rework| sdd_tdd
    end

    subgraph direct[Direct path]
        tdd -->|open PR| agent_code_review[agent_code_review]
        build -->|open PR| agent_code_review
        agent_code_review -->|attach review| human_code_review{human_code_review}
        human_code_review -->|reject: iterate| agent_code_review
        human_code_review -->|reject: rework| tdd
        human_code_review -->|reject: rework| build
    end

    sdd_human_code_review -->|approve: merge| done([merged])
    human_code_review -->|approve: merge| done
```

### Naming

Phase labels and slash-commands derive from graph node ids by `_`→`-`. Example: node `sdd_agent_spec_review` → label `phase:sdd-agent-spec-review`, command `/sdd-agent-spec-review`. The set of graph nodes IS the phase-label inventory.

Forward edges through work and review nodes are fired by those nodes' skills. Self-loops (`iterate`, `redesign`, `rework`) re-launch the relevant skill. Only `approve: merge` is fired outside any skill — the dispatcher merges via GitHub.

One long-lived PR per issue, opened by the implementing skill on the `open PR` edge and merged on `approve: merge` via `gh pr merge`.

## Dispatch

The human dispatcher operates from Claude Code's "claude agents" dashboard (see [agent-view-adoption.md](~/workspace/dev-playbook/workflow/agent-view-adoption.md) for the view's capabilities and limits). Anthropic subscription billing requires interactive sessions, so every node entry is human-launched.

All FOTW skills are launched under `/goal`; HITL skills never are. FOTW skills declare a terminal `DONE: …` line so the (text-only) evaluator can match deterministically. Pair action with proof and a stop-clause: `/goal Run /<skill> <args> until <DONE: line appears>, or stop after N turns.`

## Permissions

Tool access is governed by a tiered settings hierarchy. Rules at every level merge into one effective ruleset; **deny wins anywhere** — a deny at any level blocks the call regardless of allows elsewhere.

| Level (highest precedence first) | File / Source | Our use |
|---|---|---|
| Managed | `/etc/claude-code/managed-settings.json` | Not used (not enterprise). |
| CLI args | `claude agents --permission-mode dontAsk …` | **Sets FOTW mode for dispatched sessions only**, leaving personal `claude` sessions in their normal mode. |
| Local | `<repo>/.claude/settings.local.json` | Rare; gitignored personal exceptions. |
| Project | `<repo>/.claude/settings.json` | Repo-specific allow rules. |
| User | `~/.claude/settings.json` | `Skill()` gates for FOTW-entry skills, plus narrow backstop for built-in skills. Stow-linked from `dotfiles/dot-claude/`. Benign for personal sessions — never sets mode. |

**Mode: `dontAsk`, set at agent-view startup** via `claude agents --permission-mode dontAsk`. Auto-deny anything not pre-approved; never prompt. Applies to every dispatched session (HITL and FOTW); personal `claude` sessions are unaffected. Trades upfront allow-list enumeration for runtime determinism.

Allow rules are encoded at two levels:

- **User-level allow** holds only `Skill(name)` gates for dispatcher-launched skills, plus a narrow bash backstop for built-in skills (e.g., `/code-review`'s `Bash(gh pr diff *)`).
- **Per-skill `allowed-tools` front-matter** holds everything else: bash, edits, sub-skills (`Skill(child)`). This is the **per-skill permission set** in the [skill table](#skills). Additive, scoped to the skill's lifetime; cannot override a deny.

**Bash baseline.**

- *Auto-allowed in every mode, no rule needed:* `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, read-only `git` forms.
- *User-level allow for universally-trusted mutators:* `Bash(mkdir *)`, `Bash(touch *)`, `Bash(mv *)`, `Bash(cp *)`.
- *`rm` is not yet user-allowed.* Worktree auto-isolation cwd-bounds each session — sufficient practical confinement (soft boundary, not an OS jail). Code-writing skills will likely need `rm`; not yet committed.

Edges fired by skills are covered by the firing skill's `allowed-tools`. Edges fired by the human (label changes, manual merge) need no encoding.

Canonical rule syntax and edge cases: [permissions docs](https://code.claude.com/docs/en/permissions).

## Skills

Three modes of human engagement exist in theory; only two are available under the [Dispatch](#dispatch) model:

- **Human in the loop (HITL)** — human is actively engaged throughout, spending real time and focus. Use this for stages that focus on extracting human intent. Examples: initial issue creation and writing specs.
- **Finger on the wheel (FOTW)** — skill is designed to run hands-off; human is present only because billing requires it. Agent does the work; human invokes the skill and responds to escalations. Examples: implementing code, performing agent reviews.
- **Hands off the wheel (AFK)** — agent runs autonomously, no human involvement. *Not available* — see [Dispatch](#dispatch). We would use this if we could.

FOTW agents can escalate to the human at any time — typically when they encounter something unexpected or want to deviate from their initial plan.

Direct-path work splits by `tests:*`. `/tdd` mirrors `/sdd-tdd` for testable Direct work; `/build` handles non-test work — docs, config, chores. Both feed shared `agent_code_review` and `human_code_review`.

| Skill | Mode | Permissions set (`allowed-tools`) | Escalation triggers |
|-------|------|-----------------------------------|---------------------|
| `/intake` | HITL | `Bash(gh issue *)` `Bash(gh label *)` `Skill(grill-with-docs)` | TBD |
| `/sdd-requirements` | HITL | `Bash(gh issue *)` `Skill(grill-with-docs)` | TBD |
| `/sdd-design` | HITL | `Bash(gh issue *)` `Skill(grill-with-docs)` `Skill(improve-codebase-architecture)` | TBD |
| `/sdd-tdd` | FOTW | `Bash(gh issue view *)` `Bash(gh pr *)` `Bash(git *)` `Edit` `Write` | TBD |
| `/tdd` | FOTW | same as `/sdd-tdd` | TBD |
| `/build` | FOTW | same as `/sdd-tdd` | TBD |
| `/sdd-agent-spec-review` | FOTW | `Bash(gh issue view *)` `Bash(gh issue comment *)` `Bash(gh api *)` | TBD |
| `/sdd-agent-code-review` | FOTW | `Skill(load-issue)` `Skill(code-review)` | TBD |
| `/agent-code-review` | FOTW | `Skill(load-issue)` `Skill(code-review)` | TBD |

# Old, Pre-existing Sections That Need New consideration. We May Delete or Modify These Based on How They Fit Into the New standard.

## Issue body format (the brief is the body)

The issue body IS the agent brief. Use this format:

```markdown
**Summary:** one-line description

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate

**Blocked by:** #<issue-number> (or "None")
```

Brief principles, applied when writing or revising:

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. Do not reference file paths or line numbers — they go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.

## Vertical-slice rules (when one idea becomes many issues)

Break a plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, NOT a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.

Publish issues in dependency order so the `Blocked by` field can reference real issue numbers.