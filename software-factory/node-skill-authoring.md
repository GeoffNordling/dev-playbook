---
type: Standard
title: Node-Skill Authoring
description: Voice, content rules, and mechanics for authoring the software factory's node skills
---

# Node-Skill Authoring

Conventions for writing the software factory's node skills — the `phase:*` skills in `dotfiles/dot-claude/skills/`. Three documents bind what those skills *do*, and this one restates none of them: [software-factory.md](/software-factory/software-factory.md) defines the graph and the states; [factory-operations.md](/software-factory/factory-operations.md) defines the dispatch model and the [node-skill contract](/software-factory/factory-operations.md#the-node-skill-contract) — `## Read first`, the worktree, the gate, the terminal report contract and its report line; [review-contract.md](/software-factory/review-contract.md) defines everything a review does once dispatched, from its stance to its findings comment. What follows is the authoring *style* behind them.

Its base is the general skill machinery, equally unrestated: [skill-conventions.md](/standards/claude-code/skill-conventions.md) binds the bundle format, [skill-writing.md](/standards/claude-code/skill-writing.md) carries the craft — the two loads, the information hierarchy, steering, pruning, and the failure modes — and the `skill-creator` skill is the workflow over both. What follows is what a node skill needs on top of them.

## Voice

The body is read by an agent running one node who does not know the software factory model.

- **Plain behavioral language.** No `AFK`, `node`, `edge`, "overwatch", or "Agent view" in the body — that vocabulary lives here and in the software factory documents, not in front of the executing agent. The exception is a skill whose subject *is* the software factory itself: it reads them up front and navigates by node, edge, and state, because that is its job.

## Content

- **Source the *what and when* from the read itself.** A node skill's `## Read first` hands the agent the routing and the decisions; the skill supplies only the *how* — the commands an action draws on — and cites the rest.
- **Two paddings a node skill invites.** The [no-op test](/standards/claude-code/skill-writing.md#pruning) cuts what the agent would do anyway, and two of its instances are node-shaped: the *downstream why*, explaining how a step serves a later phase the agent can't see ("commit so the later PR has content to carry"), and the *closed edge case*, guarding a scenario the factory design already settled ("a reboot won't lose the worktree"). Keep the conditions and escalations; drop the color.
- **Order lists spec → test → code.** Everywhere this triad appears — reads, audit dimensions, context artifacts — keep that order: spec first, tests before code, behavior before style. When a list omits one of them, keep the surviving order.

## Robustness

- **Check, don't assume prior-phase state.** A node may be the first to run on a region — check for what you need and establish it if absent, rather than trusting an upstream node to have left it.
- **Defer rather than scaffold.** An unfinished region is left undone and reported as deferred, not filled with placeholder content a later node would only delete.
- **Decide only what's yours.** A node skill doesn't make calls that belong to the user or an upstream node — it takes them as input; handed a scope, it neither widens nor narrows it.

## Mechanics

- **A skill does not enumerate its permissions.** They are the session's: auto mode judges each call, and subagent permissions are consciously wide ([factory-operations.md § Permissions](/software-factory/factory-operations.md#permissions)). The exception is a role boundary the harness must enforce rather than merely be asked for — a reviewer's read-only stance is stated in the skill's prose *and* nailed down by `disallowed-tools` ([skill-conventions.md — Optional fields](/standards/claude-code/skill-conventions.md#optional-fields)).
- **An AFK skill escalates, it never waits.** It runs in a subagent with no user attached, so a mid-work "wait for the user" step waits forever — a subagent yields only by ending its run. When it needs a call from the user it ends with `ESCALATE:`, and review by the user lives at the dedicated review nodes rather than mid-skill. An interview skill is the reverse: the user is at the terminal, so it interviews freely in prose and gates on the answers.
- **Report state, not next steps.** A node reports its own state and stops; what runs next — the next node, a label move — is the issue overwatch's concern, surfaced outside the skill. State a pending hand-off as a flag (`awaiting verdict`), never as an instruction to run.
