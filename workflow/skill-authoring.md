# Skill authoring

Conventions for writing the workflow node-skills — the `phase:*` skills in `dotfiles/dot-claude/skills/`. [workflow.md](~/workspace/dev-playbook/workflow/workflow.md) defines the graph, the dispatch model, and the Node-skill contract (allowed-tools, `## Read first`, terminate/escalate by mode); this captures the authoring *style* behind them. Each line names a skill that shows it.

## Voice

The body is read by an agent running one node who does not know the workflow model.

- **Plain behavioral language.** No `FOTW`, `node`, `edge`, or "dashboard" in the body — that vocabulary lives here and in `workflow.md`, not in front of the executing agent. (`sdd-tdd`)
- **Positive, not by negation.** Say what a mode or step does, not "the one that isn't X."
- **Recommendations carry their reason.** Where a skill has the agent recommend something to the human, require the recommendation *and why*. (`sdd-requirements` §3, `sdd-design` §3)

## Content

- **Author against the whole spec**, not a salient part — `Interface:` is the pinned public surface, not the contract. (`sdd-tdd`)
- **Don't restate what the steps already enforce.** If the body did its job, a trailing "Output"/recap section is dead weight — omit it.
- **Read only what's needed.** Skip what's auto-loaded (project `CLAUDE.md`); `## Read first` ends in a `READ:` line; conditional reads stay at their point of use. (`sdd-requirements`, `sdd-tdd`)
- **Don't re-explain what `## Read first` taught.** Reference a spec concept; don't restate it — the agent has read the standard. (`sdd-tdd` §1 just locates the specs.)
- **Keep useful interview aids even when they aren't spec fields** — a `feat`'s out-of-scope discussion sharpens what the feature *is*. (`sdd-requirements`)
- **Name the spec location one way.** Always "The specs under `specs/functional_requirements/` and `specs/design/`" — the directory form, no "(or flat-file equivalents)" / "(or folder form)" hedge. (`sdd-agent-spec-review` §1)
- **Order lists spec → test → code.** Everywhere this triad appears — reads, audit dimensions, context artifacts — keep that order: spec first, tests before code, behavior before style. Reads go spec-standard → testing-conventions → python-conventions; context goes specs → tests → code. Where python is absent (the build skills dropped it), it's just spec → test. (`sdd-agent-code-review`, `sdd-tdd`)

## Robustness

- **Check, don't assume prior-phase state.** A node may be the first to run on a region — check for what you need and establish it if absent. (`sdd-design` checks for the `WIP:` marker rather than trusting requirements to have left it.)
- **Stub or mark only what you won't later delete.** Deferring beats throwaway scaffolding — the `WIP:` marker exempts an unfinished cone instead of writing verifiers you'd delete. (`sdd-requirements`, `sdd-design`; spec-standard §2.10)
- **Decide only what's yours.** A node skill doesn't make calls that belong to a human or an upstream node — it takes them as input. (`sdd-tdd` is handed its scope; it never judges whether an issue is too big to build.)
- **Make completion factual, not self-assessed.** Drive decisions off observable state and quantified thresholds, not the agent's sense of effort. (`sdd-tdd` reads `WIP:` markers to know the issue is done; a stuck test escalates after *two* attempts, not after "honest effort.")
- **Guard against gaming the success signal.** When a check gates the work, forbid weakening the check to pass it. (`sdd-tdd`: never modify a written test — escalate instead.)
- **Review nodes report, they don't fix.** A node that reviews another node's output stays read-only on it — no `Edit`/`Write` grant. Defects route back to the authoring node through the human's reject, not the reviewer's hand. (`sdd-agent-spec-review` attaches findings; it never edits the spec.)
- **Separate the deliverable from the escalation.** When a node's whole job is to surface problems, say plainly that finding them is the output, not a reason to stop — otherwise the agent escalates on every defect. Escalation stays reserved for "can't produce the deliverable at all." (`sdd-agent-spec-review`: findings ride to the human in a comment; only a red consistency gate escalates.)
- **Don't audit what a deterministic gate already enforces.** An agent reviewer's value is the judgment a check can't automate — verifier honesty, scope, design — not re-confirming green-gate invariants (`covers` markers present, spec items discharged, the tree builds). Don't narrate those guarantees either; spend the review on what the machine can't see. (`sdd-agent-code-review` §3 checks that verifiers are honest, not that they exist.)

## Mechanics

- **Permissions are per-skill, verified empirically.** Under `dontAsk`, `Edit`/`Write` are denied without a grant; copy `allowed-tools` verbatim from the `workflow.md` skill table.
- **Description names the launch trigger, not every situation.** Skills are human-dispatched, so the front-matter `description` ends at "Use when the agents dashboard launches the `<phase>` phase" — drop the "when X, when Y" restatements. (`sdd-agent-spec-review`)
- **Close concretely:** advance the `phase:*` label → stop. A work node first leaves the tree green and commits; a read-only review node changed nothing on disk, so it skips both. HITL closes with a plain report; FOTW closes with the `DONE:` line.
- **FOTW skills don't gate on approval.** No mid-work "wait for the user" steps — the agent runs to its terminal line and escalates on exceptions; human review lives at the dedicated review nodes. HITL skills do gate — that's the line between the modes.
