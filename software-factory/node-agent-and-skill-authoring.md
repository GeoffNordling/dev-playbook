---
type: Guide
title: Node-Agent and Skill Authoring
description: Voice, content rules, and mechanics for authoring the software factory's node agent definitions and node skills
---

# Node-Agent and Skill Authoring

Conventions for writing what runs the software factory's nodes: the typed agent definitions in `dotfiles/dot-claude/agents/` and the `phase:*` skills in `dotfiles/dot-claude/skills/`. One authoring style governs both — a definition and a skill differ in how they are launched and how they report, not in how they are written — and every rule below applies to both unless it names one. What a node *does* is bound elsewhere, and this one restates none of it: [software-factory.md](/software-factory/software-factory.md) defines the graph and the states; [factory-operations.md](/software-factory/factory-operations.md) defines the dispatch model and the [node-skill contract](/software-factory/factory-operations.md#the-node-skill-contract) — `## Read first`, the worktree, the gate, the terminal report contract and its report line; [review-contract.md](/software-factory/review-contract.md) defines everything a review does once dispatched, from its stance to the threads it leaves behind. Clauses of that node-skill contract bind a skill only: a definition never enters a worktree — its launcher sets the cwd — and it ends on the report envelope rather than a report line. What follows is the authoring *style* behind them.

Its base is the general runbook machinery, equally unrestated: [runbook-conventions.md](/standards/harness/runbook-conventions.md) binds the format a skill or agent definition takes, the installed [`/writing-for-agents`](/dotfiles/.agents/skills/writing-for-agents/SKILL.md) skill carries the craft both answer to, and the `runbook-creator` skill is the workflow over both. What follows is what a node needs on top of them.

## Voice

The body is read by an agent running one node who does not know the software factory model.

- **Plain behavioral language.** No `AFK`, `node`, `edge`, "overwatch", or "Agent view" in the body — that vocabulary lives here and in the software factory documents. The exception is a body whose subject *is* the software factory itself: it reads them up front and navigates by node, edge, and state.

## Content

- **Source the *what and when* from the read itself.** A node's `## Read first` hands the agent the routing and the decisions; the body supplies only the *how* — the commands an action draws on — and cites the rest.
- **Paddings a node body invites.** The [no-op test](/dotfiles/.agents/skills/writing-for-agents/SKILL.md#pruning) cuts what the agent would do anyway. Node-shaped instances: explaining how a step serves a later phase the agent can't see ("commit so the later PR has content to carry"), and guarding a scenario the factory design settled ("a reboot won't lose the worktree"). Keep the conditions and escalations; drop the color.
- **Order lists spec → test → code.** Everywhere this triad appears — reads, audit dimensions, context artifacts — keep that order: spec first, tests before code, behavior before style. When a list omits one of them, keep the surviving order.

## Robustness

- **Check, don't assume prior-phase state.** A node may be the first to run on a region — check for what you need and establish it if absent.
- **Defer rather than scaffold.** An unfinished region is left undone and reported as deferred.
- **Decide only what's yours.** A node doesn't make calls that belong to the user or an upstream node — it takes them as input; handed a scope, it neither widens nor narrows it.

## Mechanics

- **A body does not enumerate its permissions.** They are the session's: auto mode judges each call, and subagent permissions are consciously wide ([factory-operations.md § Permissions](/software-factory/factory-operations.md#permissions)). The exception is a role boundary the harness must enforce rather than merely be asked for — a reviewer's read-only stance is stated in the body's prose *and* nailed down in frontmatter, by the form's own mechanism: a definition pins the `tools` roster it needs and the file-writing tools are simply absent from it, while a skill denies them outright with `disallowed-tools` ([runbook-conventions.md — Front matter](/standards/harness/runbook-conventions.md#front-matter)).
- **A hands-off node escalates, it never waits.** It runs with no user attached, so a mid-work "wait for the user" step waits forever — the run yields only by ending. When it needs a call from the user it says so on its terminal report and ends: an agent definition on the report envelope — required top-level `outcome` `"escalated"`, the reason in `gist` — and a skill on its `ESCALATE:` line. Review by the user lives at the dedicated review nodes rather than mid-body. An interview skill is the reverse: the user is at the terminal, so it interviews freely in prose and gates on the answers.
- **Report state, not next steps.** A node reports its own state and stops; what runs next — the next node, a label move — belongs to whatever sequences the graph, and is decided outside the body. State a pending hand-off as a flag (`awaiting verdict`), never as an instruction to run.
- **A node stages scratch outside the repository.** Intermediate text — a comment body, a PR description — goes to `/tmp/<kind>-<issue>.md`, then passes to `gh` with `--body-file`. The worktree holds the deliverable and nothing else. The rule fixes where scratch lands, not what writes it: a node whose roster carries `Write` uses it, and a reviewer, whose roster is read-only against the repository, writes the file from `Bash`.
