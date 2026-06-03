# Skill authoring

Conventions for writing the workflow node-skills — the `phase:*` skills in `dotfiles/dot-claude/skills/`. [workflow.md](~/workspace/dev-playbook/workflow/workflow.md) defines the graph, the dispatch model, and the Node-skill contract (`disallowed-tools`, `## Read first`, terminate/escalate by mode); this captures the authoring *style* behind them.

## Voice

The body is read by an agent running one node who does not know the workflow model.

- **Plain behavioral language.** No `FOTW`, `node`, `edge`, or "dashboard" in the body — that vocabulary lives here and in `workflow.md`, not in front of the executing agent. The exception is a skill whose subject *is* the workflow itself: it reads `workflow.md` up front and navigates by node, edge, and state, because that is its job.
- **Positive, not by negation.** Say what a mode or step does, not "the one that isn't X"; instruct toward the action to take, not away from the misstep to avoid. Negation earns its place only in an escalation trigger, where the misstep *is* the subject.
- **Recommendations carry their reason.** Where a skill has the agent recommend something to the human, require the recommendation *and why*.
- **Name the user's choices plainly, and few.** A skill body speaks to the person at the keyboard as the `user` — per the [terminology rule](~/workspace/dev-playbook/standards/doc-conventions.md) — so word a verdict as a plain command they already understand, not an insider term; collapse near-synonyms into one option.

## Content

- **Author against the whole contract, not a salient part.** The most visible piece — a pinned interface, a headline item — is the public surface, not the whole of what's owed.
- **Don't restate what the steps already enforce.** If the body did its job, a trailing "Output"/recap section is dead weight — omit it.
- **An instruction earns its words by changing what the agent does.** Give the action and any real condition or branch, and cut what the agent would do the same way without it. Four paddings recur: the *obvious* (restating what the action already implies — "enter the worktree, where the code lives"), the *downstream why* (how a step serves a later phase the agent can't see — "commit so the human's push has something to publish"), the *reassurance* (narrating a non-event — "you changed no source, so there's no commit"), and the *closed edge case* (guarding a scenario the design already settled — "a reboot won't lose the worktree"). Keep the conditions and escalations; drop the color.
- **Read only what's needed.** Skip what's auto-loaded (project `CLAUDE.md`); `## Read first` ends in a `READ:` line; conditional reads stay at their point of use.
- **Don't re-explain what `## Read first` taught.** Reference a concept from the standard; don't restate it — the agent has read it.
- **Keep useful interview aids even when they aren't required fields** — discussing what's out of scope sharpens what the thing *is*, though "out of scope" is no field you fill.
- **Name a location one way.** Use one consistent form for a fixed path — the directory form — and drop the "(or flat-file equivalent)" / "(or folder form)" hedges.
- **Order lists spec → test → code.** Everywhere this triad appears — reads, audit dimensions, context artifacts — keep that order: spec first, tests before code, behavior before style. When a list omits one of them, keep the surviving order.
- **Reference the source; don't copy it.** Don't bake a snapshot of something authoritatively defined elsewhere — a graph, a label set, a standard's rules — into a skill body; the copy goes stale when the source moves. Make the source mandatory `## Read first`, then act from what was read. Source the *what and when* — the routing and decisions the source already defines — and let the agent read them there rather than restating them; but supply the *how*, the commands an action draws on.
- **A reduced variant mirrors its fuller sibling.** When one skill is a leaner version of another, keep the shared skeleton and swap the contract — e.g. an issue brief's acceptance criteria standing in for a committed spec, with the heavier machinery dropped. Map each mechanism in the fuller skill to its analog in the leaner one rather than inventing a new shape.

## Robustness

- **Check, don't assume prior-phase state.** A node may be the first to run on a region — check for what you need and establish it if absent, rather than trusting an upstream node to have left it.
- **Stub or mark only what you won't later delete.** Deferring beats throwaway scaffolding — mark an unfinished region exempt rather than writing scaffolding you'd only delete later.
- **Decide only what's yours.** A node skill doesn't make calls that belong to a human or an upstream node — it takes them as input; handed a scope, it neither widens nor narrows it.
- **Make completion factual, not self-assessed.** Drive decisions off observable state and quantified thresholds, not the agent's sense of effort — a step retries a fixed number of times, not until "honest effort" runs out.
- **Guard against gaming the success signal.** When a check gates the work, forbid weakening the check to pass it — e.g. never edit a written test to make it go green; escalate instead.
- **Review nodes report, they don't fix.** A node that reviews another node's output stays read-only on it — it denies `Edit`/`Write` (and `MultiEdit`/`NotebookEdit`). Defects route back to the authoring node through the human's reject, not the reviewer's hand.
- **Separate the deliverable from the escalation.** When a node's whole job is to surface problems, say plainly that finding them is the output, not a reason to stop — otherwise the agent escalates on every defect. Escalation stays reserved for "can't produce the deliverable at all."
- **Don't audit what a deterministic gate already enforces.** An agent reviewer's value is the judgment a check can't automate — verifier honesty, scope, design — not re-confirming what the gate already proves (items discharged, the tree builds). Don't narrate those guarantees either; spend the review on what the machine can't see.

## Mechanics

- **A node loads its own context.** It runs after `/clear` with nothing carried over, so it reads what it needs from the issue and the worktree it sits in — never from the prior node.
- **Permissions are deny-only.** Auto mode self-approves safe calls, so a skill enumerates no allow-list — it copies its `disallowed-tools`, the few tools its role must never call, from the `workflow.md` skill table. Most skills deny nothing.
- **A FOTW skill escalates, it doesn't ask.** The skill table denies `AskUserQuestion` to every FOTW node, so a hands-off run can't pause for the human — when it needs a human call it prints `ESCALATE:` and yields. A HITL skill is the reverse: the human is engaged, so it interviews freely via `AskUserQuestion` or plain terminal prompts and gates on the answers.
- **Description names the launch trigger, not every situation.** Skills are human-dispatched, so the front-matter `description` ends at "Use when the agents dashboard launches the `<phase>` phase" — drop the "when X, when Y" restatements.
- **Close concretely:** advance the `phase:*` label → stop. A work node first leaves the tree green and commits; a read-only review node changed nothing on disk, so it skips both. HITL closes with a plain report; FOTW closes by printing a terminal line — `DONE:` on success or `ESCALATE:` when stuck.
- **FOTW skills don't gate on approval.** No mid-work "wait for the user" steps — the agent runs to its terminal line and escalates on exceptions; human review lives at the dedicated review nodes. HITL skills do gate — that's the line between the modes.
- **Escalation is a terminal state, not a pause.** Under `/goal` the session is re-driven after every turn until the condition holds, so a FOTW skill can't passively wait for the human — its only way to yield is to print a terminal line. Escalation gets its own, `ESCALATE:`, alongside `DONE:`, and the goal condition must stop on every terminal line the skill can print. A "stop and wait" with no terminal line is re-driven straight past the obstacle.
