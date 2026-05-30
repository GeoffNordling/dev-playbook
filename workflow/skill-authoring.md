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

## Robustness

- **Check, don't assume prior-phase state.** A node may be the first to run on a region — check for what you need and establish it if absent. (`sdd-design` checks for the `WIP:` marker rather than trusting requirements to have left it.)
- **Stub or mark only what you won't later delete.** Deferring beats throwaway scaffolding — the `WIP:` marker exempts an unfinished cone instead of writing verifiers you'd delete. (`sdd-requirements`, `sdd-design`; spec-standard §2.10)

## Mechanics

- **Permissions are per-skill, verified empirically.** Under `dontAsk`, `Edit`/`Write` are denied without a grant; copy `allowed-tools` verbatim from the `workflow.md` skill table.
- **Close concretely:** leave the tree green → commit → advance the `phase:*` label → stop. HITL closes with a plain report; FOTW closes with the `DONE:` line. (all node skills)
