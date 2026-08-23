---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent. Extensible: terms are added here as they're pinned down.

## Language

### Architecture

The architecture vocabulary — Module, Interface, Implementation, Depth, Seam,
Adapter, Leverage, Locality — is defined by the installed `/codebase-design`
skill, along with the aliases it retires and the relationships among the
terms. Invoke it before making a module suggestion and use its terms exactly;
[Module Design](/standards/modules.md) is the card that governs the concern.

### Definition region

The interview beats that author an issue's brief before it crosses into the
factory. Both run in `intake` and `design`; this fixes which is which.

**General Interview**
The ordinary interviewing that authors a brief — the areas in play, the approach, the tradeoffs, the probes. The agent asks, the user answers, and the agent writes the result in its own words. It authors every heading but `User intent`.
_Avoid_: intent interview (retired).

**User Intent Mini-Interview**
The short beat that authors the `User intent` heading alone, run once the rest of the brief is drafted and before it lands. The user says their intent cold, the agent surfaces where it collides with the draft, and the reconciled text lands in the user's own words. Authored by the `/user-intent-mini-interview` skill.

### Engagement

Whether the user is at the terminal for a piece of work. Exactly two values;
which one each factory node takes is set by the dispatch table in
[factory-operations.md](/software-factory/factory-operations.md), and this fixes
the words.

**AFK**
Work the user is not intended to be involved in. No user is attached, so it runs to completion or escalates — it never waits. Independent of substrate: a delegated subagent and a headless `claude -p` process are both AFK.
_Avoid_: unattended, hands-off, autonomous.

**Inline**
Work run with the user present in the terminal, free to interview, gate on the answers, and hand back mid-task.
_Avoid_: interactive — overloaded, since it also names the Claude Code TUI as opposed to `claude -p`. Say **Inline** when engagement is the point.

### Governance

How a standard is checked against the repository and where nonconformance is
blocked. The gate rungs are defined once in
[enforcement.md](/standards/build/enforcement.md); this fixes the words.

**Audit**
The umbrella term for the Standard's read-only checking process: a run of one or more detectors; read-only — it never mutates the repository and never blocks by itself. A Detector is a **lint** if it is deterministic code, an **audit** in the narrow sense if it is an LLM judge.
_Avoid_: check (too broad — a check may block; an audit never does).

**Lint**
A Detector implemented as deterministic code — the `*-lint` scripts under `scripts/`. Every lint is part of the audit process (lint ⊂ audit), never the reverse — an audit in the narrow sense (an LLM judge) is not a lint.
_Avoid_: audit, for a deterministic detector — that detector is a lint.

**Detector**
The read-only check that inspects the repository against one or more standards and emits findings; it never mutates the repository. A Detector is a **lint** if it is deterministic code and an **audit** in the narrow sense if it is an LLM judge. Cards are organized by question and detectors by mechanism, so a card may have more than one detector; the one-to-one is at the rule — every `card.rule` id belongs to exactly one card.

**Gate**
An automatic, unmanned blocking point on the path to main. There are exactly three, with fixed rung names: **commit gate** (the pre-commit suite), **push gate** (`make check-judgments-cache`, via the pre-push stage), **CI gate** (thin CI).
_Avoid_: venue (retired — say **gate**, or a rung name).

**Enforcement**
An audit stationed at a gate — the audit's findings block the path to main there. Enforcement is automatic and continuously in effect.

**Finding**
One output line from a detector, in GNU format: `file:line: card.rule message` — a colon after the location, single spaces, a repo-relative path. The `:line` is omitted for a file-level finding (e.g. `README.md: knowledge-organization.doc-shape missing an H1 title`). The rule id is namespaced by the card whose question it answers.

**Consumer**
A repository that consumes what dev-playbook defines — standards, published hooks, judgments machinery, methods. Every other workspace repo is a consumer.

**Scope**
The population a standard governs. **Workspace-scoped**: declared in dev-playbook, governing every repo in `~/workspace`. **Repo-scoped**: declared in one consumer, governing that repo alone. Exactly two values.

### Machines

The hosts the workspace runs on. The inventory — which machines exist and what
differs between them — is in [machines.md](/docs/machines.md); this fixes the
words.

**Primary machine**
The Fedora host, where development happens and every workspace repo is cloned. Exactly one exists. Every check runs here.
_Avoid_: dev box, main machine.

**Secondary machine**
A Windows/WSL host. Carries only some of the workspace's repos and runs a reduced set of checks. Several exist, kept identical and sharing one configuration, so they are addressed collectively by the machine key `wsl`.
_Avoid_: WSL box (say **secondary machine** when the distinction from the primary is the point).

**Machine-local state**
Input a detector needs that lives on the host rather than in the repository — a sibling repo's clone, a populated cache. A detector whose machine-local state is absent reports the environment, not the code, which is why such a detector is skipped rather than allowed to fail.

### Software factory

The software factory's managing roles. The factory itself — regions, states,
labels — is defined in
[software-factory.md](/software-factory/software-factory.md); this fixes the
words for who runs it.

**Issue Manager**
The top-level session that owns one issue's whole traverse through the factory — one per issue, launched by the user in Agent view, locked into the issue's worktree for the issue's life. It spawns the node subagents, writes every label, and stops only to escalate or to hand over the finished PR at the merge boundary.
_Avoid_: issue overwatch, overwatch (retired).

**Agent-View Manager**
The user's fleet assistant in Agent view: reads the board across issues, recommends what to launch next, and hands the user paste-ready Issue Manager launch lines. It executes no node, owns no issue, and holds no git duties.
_Avoid_: agent-view overwatch (retired).

### Tracking

Where future work is recorded. A unit of work has exactly one home, decided by
whether it is committed; the tracking standard defines both homes, and this
fixes the words.

**Candidate**
A described but uncommitted unit of future work, recorded in a repo's `CANDIDATES.md`. Serious and repo-scoped — work the repo would genuinely implement if the decision were made — but not yet decided, so it carries no brief. Becomes committed work via **Promotion**.
_Avoid_: backlog item, todo, roadmap item.

**Promotion**
The step that turns a **Candidate** into committed work: an issue is authored from the entry, and the entry is deleted in the same change. Deciding to write the brief is the act of committing — a Candidate may already be specifiable and stay a Candidate until that decision is made.
