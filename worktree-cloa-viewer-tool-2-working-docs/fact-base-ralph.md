---
type: General-Sheet
title: Ralph Fact Base
description: The definitions behind the simulated fact base for the Ralph loop subsystem — its terms, the extractors that yield each fact, the views selected from it, and the facts no extractor reaches
---

# Ralph Fact Base

The definitions behind
[fact-base-ralph.json](/worktree-cloa-viewer-tool-2-working-docs/fact-base-ralph.json),
a data file written by hand on 2026-09-10 to simulate what deterministic
code would produce for one subsystem: the Ralph loop. The concept it
simulates is
[Fact Base](/worktree-cloa-viewer-tool-2-working-docs/fact-base.md). This page holds
what a person needs to read the data. The data file holds only data:
every row in it is a fact a stated extractor finds in a real file at a real
line, and nothing is inferred. The pair answers one question, "what makes
up a Ralph loop run, and in what order do the parts act?", and records
where the extractors run out.

## Terms

- **fact base** — the one object underneath every view: a set of nodes
  and a set of edges.
- **node** — one thing with an identity, a node type, a provenance, and
  attributes. An identity is a repo-relative path, per the
  [Contract](/worktree-cloa-viewer-tool-2-working-docs/contract.md#identities);
  an imported node has a name instead, and a bucket is named
  `bucket:<name>`.
- **edge** — one relation from a source node to a target node, with a
  relation type, and, where the source declares them, an order, a
  condition, and a detail quoted from the source.
- **extractor** — a deterministic function from one artifact to rows.
  A bedrock extractor parses; a doc-type extractor reads a contract
  shape. Every row in the data file names its extractor.
- **view** — a selection of nodes and edges from the fact base, plus a
  renderer. A view drops; it never adds or converts.

## The data file

The data file obeys the
[envelope](/worktree-cloa-viewer-tool-2-working-docs/contract.md#the-envelope)
with kind `fact-base`, version `0`, and a null subject, since a real
generator would emit the whole checkout. The title names the slice this
simulation took: paths matching `*ralph*` and the nodes their edges
touch. The payload is two arrays.

A node row: `id`, `type`, `provenance`, `extractor`, `line`, `attrs`.

An edge row: `source`, `relation`, `target`, `order`, `condition`,
`detail`, `extractor`, `line`. Order and condition are null unless the
chain extractor set them.

## The extractors

| Extractor | Procedure | Exists today |
| --------- | --------- | ------------ |
| fs | Walk the checkout. Every tracked file is a node of type File; every directory contains its entries. | yes, git |
| frontmatter | Parse YAML frontmatter. `name`, `description`, `type`, `arguments`, `model`, `effort` become attributes; `resource` becomes a resource edge. | yes, md.py |
| location | `skills/<name>/SKILL.md` is a Skill; `agents/<name>.md` is an Agent. | yes, the runbook shape's `location` predicate |
| mdlink | Every markdown link `[text](target)` is a links-to edge to the resolved path. `~/.claude/` resolves to `dotfiles/dot-claude/`; `~/workspace/dev-playbook/` resolves to the checkout root. | yes, ref-lint |
| chain | The runbook encoding's spans, `{Read …}`, `{Run …}`, `{Launch …}`, `{Write …}`, `{Never …}`, `{Report …}`, plus frontmatter `arguments`, yield chain edges with operation, target, and condition, in document order. | yes, chaingen |
| js-meta | For a `.js` under `workflows/`, parse the `export const meta` literal and the `ARG_TYPES` literal. Name, description, and args become attributes. | no |
| launch-literal | A fenced code block containing `Workflow({ name: "<x>"` yields a launches edge to `workflows/<x>.js`. | no, and it is fragile |

Node types Skill and Agent are the runbook's own. Directory, File,
Workflow, and Recipe-Description are types the fact base needs that the
runbook's closed vocabulary does not hold.

## Views selected from it

### Dependency graph

Selection: every node except directories and buckets; relations
links-to, resource, does, reads with a file target, launches. Order and
condition dropped.

```
[ralph-setup] Skill
  ├─reads────► ralph-loop.md Recipe ─resource─► ralph-loop.js Workflow
  ├─launches─► ralph-loop.js Workflow                 (proposed extractor)
  ├─does─────► [grilling] Skill
  ├─does─────► [domain-modeling] Skill
  ├─links-to─► references/plan-skeleton.md
  ├─links-to─► references/progress-skeleton.md
  └─links-to─► [ralph-checkpoint] Skill
                 └─does─────► [ralph-checkpointer] Agent

no chain edge reaches ralph-loop.js                   (gap 1)
no edge leaves ralph-loop.js                          (gap 3)
```

### Control flow

Selection: chain edges only, with order and condition kept. One box per
runbook. The workflow is one opaque box. USER is not a node; it is
drawn from prose, not from an extractor, and is marked as such.

```
USER runs [ralph-setup]                                    ← prose
  1 args goal
  2 reads ralph-loop.md
  3 does [grilling]
  4 does [domain-modeling]           active throughout
  5 writes local file: plan file     ╌ if approved and gate green
  6 writes local file: progress file ╌ same
  7 reports outcome: str             the launch command
USER runs ralph-loop.js                                    ← prose
  ▓ opaque: its behavior is a prompt string              (gap 3)
  returns {iterations, blocker}
USER runs [ralph-checkpoint]                               ← prose
  1 args run-hint
  ? reads the workflow's return      no span, no edge    (gap 2)
  2 does [ralph-checkpointer]        as a fork
      1 reads launch prompt
      2 reads PLAN.md
      3 reads PROGRESS.md
      4–8 writes local file ×5
      9–10 never writes ×2
      11 writes local file: Decisions
      12 writes local file: marker
      13 writes git(add, commit)
      14 reports outcome: str        ≤ ten lines
  3 reports outcome: str
  ⟲ USER repeats from ralph-loop.js while tasks remain     ← prose
```

### The other five, in one line each

- **Containment tree** — contains edges only. Shows the six parts under
  four directories; no contains edge gathers the subsystem.
- **Catalog** — nodes only, columns id, type, description. Seven
  declared rows.
- **Cross-reference matrix** — rows Skill and Agent nodes, columns the
  same, cell marks a does edge. Three marks.
- **Data flow** — reads and writes edges with a file target. `PLAN.md`
  and `PROGRESS.md` are the artifacts; ralph-setup writes, the
  checkpointer reads and writes, the iteration agent is missing (gap 3).
- **Interface card** — one node's attributes plus its edges.
  ralph-checkpoint: args run-hint, does ralph-checkpointer, reports
  outcome.

## What no extractor reaches

Facts the question needs that the fact base cannot hold.

1. **Who launches the workflow.** ralph-setup ends at a report whose
   text is a launch command; the user runs it. No chain edge touches
   `ralph-loop.js`. The runbook's closed vocabulary has no operation for
   "hands a command to the user".
2. **ralph-checkpoint reads the workflow's return.** Lines 23–30 say so
   in prose with no span. One `{Read …}` span would fix it; the fact
   base makes the missing declaration visible.
3. **The iteration agent.** Its behavior is a prompt string inside
   `ralph-loop.js`, lines 80–105: it reads the plan and progress files,
   commits by invoking `/commit`, and reports a count. No doc-type extractor
   reaches inside a string in code. The move that closes it is named
   under code carries no prose in
   [Fact Base](/worktree-cloa-viewer-tool-2-working-docs/fact-base.md#code-carries-no-prose):
   the string becomes an Agent runbook the workflow refers to by path.
4. **The user as the connector.** Every handoff between the three
   runbooks and the workflow passes through the user. The recipe's own
   drawing at `harness-recipes/recipes/ralph-loop.md` line 60 puts USER
   at the top; no extractor produces that node.
5. **The subsystem itself.** Nothing declares that these six files are
   one thing. The name "Ralph" appears in each filename, and that is the
   only fact that gathers them.

## Acronyms

- **CLOA** — Correct Level of Abstraction.
- **JSON** — JavaScript Object Notation.
- **YAML** — YAML Ain't Markup Language.
