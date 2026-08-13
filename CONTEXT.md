---
type: Vocabulary
title: Vocabulary
description: The workspace's established vocabulary — the canonical terms to use exactly
---

# Vocabulary

The workspace's established vocabulary — the canonical terms every doc uses exactly, so shared language stays consistent instead of each doc reinventing it. Extensible: terms are added here as they're pinned down. Consistent language is the whole point.

## Language

### Architecture

The architecture vocabulary — Module, Interface, Implementation, Depth, Seam,
Adapter, Leverage, Locality — is defined by the installed `/codebase-design`
skill, along with the aliases it retires and the relationships among the
terms. Invoke it before making a module suggestion and use its terms exactly;
[Module Design](/standards/modules.md) is the card that governs the concern.

### Governance

How a standard is checked against the repository and where nonconformance is
blocked. The gate rungs are defined once in
[enforcement.md](/standards/build/enforcement.md); this fixes the words.

**Audit**
The umbrella term for the Standard's read-only checking process: a run of one or more detectors; read-only — it never mutates the repository and never blocks by itself. A Detector is a **lint** if it is deterministic code, an **audit** in the narrow sense if it is an LLM judge — two kinds of the one read-only process.
_Avoid_: check (too broad — a check may block; an audit never does).

**Lint**
A Detector implemented as deterministic code — the `*-lint` scripts under `scripts/`. Every lint is part of the audit process (lint ⊂ audit), never the reverse: a lint is one kind of audit, but an audit in the narrow sense (an LLM judge) is not a lint.
_Avoid_: audit, for a deterministic detector — that detector is a lint.

**Detector**
The read-only check that inspects the repository against one or more standards and emits findings; it never mutates the repository. A Detector is a **lint** if it is deterministic code and an **audit** in the narrow sense if it is an LLM judge. Cards are organized by question and detectors by mechanism, so a card may have more than one detector; the one-to-one is at the rule — every `card.rule` id belongs to exactly one card.

**Gate**
An automatic, unmanned blocking point on the path to main. There are exactly three, with fixed rung names: **commit gate** (the pre-commit suite), **push gate** (`make check-judgments-cache`, via the pre-push stage), **CI gate** (thin CI).
_Avoid_: venue (retired — say **gate**, or a rung name).

**Enforcement**
An audit stationed at a gate — the audit's findings block the path to main there. Enforcement is automatic and continuously in effect; a one-time code review by the user is not enforcement.

**Finding**
One output line from a detector, in GNU format: `file:line: card.rule message` — a colon after the location, single spaces, a repo-relative path. The `:line` is omitted for a file-level finding (e.g. `README.md: knowledge-organization.doc-shape missing an H1 title`). The rule id is namespaced by the card whose question it answers.

**Consumer**
A repository that consumes what dev-playbook defines — standards, published hooks, judgments machinery, methods. Consuming dev-playbook is the point of dev-playbook: every other workspace repo is a consumer.

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

## Relationships

- A **Detector** inspects the repository against one or more standards and emits **Findings**; an **Audit** is a run of one or more **Detectors**; stationed at a **Gate**, that audit becomes **Enforcement**.
- A **Detector** is a **Lint** (deterministic code) or an **Audit** in the narrow sense (an LLM judge); **Lint** ⊂ **Audit** — every lint is part of the audit process, never the reverse.
- There are exactly three **Gates** on the path to main: commit gate, push gate, CI gate.
- A standard has exactly one **Scope**: workspace-scoped (declared in dev-playbook, governing every repo) or repo-scoped (declared in one **Consumer**, governing that repo alone).
- There is exactly one **Primary machine**; every other host is a **Secondary machine**.
- A **Detector** is skipped on a machine iff the **Machine-local state** it needs is absent there; the **Primary machine** lacks none, so every detector runs there.
- Exactly one **Issue Manager** per issue owns that issue's traverse; the **Agent-View Manager** watches the whole fleet and executes nothing.
- A unit of future work has exactly one home: a **Candidate** in `CANDIDATES.md` while uncommitted, or a GitHub issue once committed — never both.
- **Promotion** moves a unit of work from **Candidate** to issue, deleting the **Candidate** entry in the same change.
- A **Candidate** carries no brief: choosing to write the brief is what makes work committed, and therefore an issue.

## Example dialogue

> **Dev:** "repo-lint reported a **Finding**. Does that block my commit?"
> **Reviewer:** "Only because it runs at the **commit gate**. The audit itself is read-only — it just emits **Findings**. It's the **Gate** it's stationed at that blocks; run by hand, it isn't **Enforcement** at all."

## Flagged ambiguities

- "venue" was used informally for a blocking point — resolved: say **Gate**, or one of the three rung names (commit gate, push gate, CI gate). "venue" is retired.
- "check" and "audit" were blurred — resolved: an **Audit** is read-only and never blocks; a **Gate** is what blocks. A check that blocks is a gate; a check that only reports is an audit.
- "audit" and "detector" were blurred — the same read-only, gate-stationed role was defined with near-identical language in two files — resolved: a **Detector** is the check; an **Audit** is a run of one or more detectors.
- "lint" and "audit" were blurred — "lint" survived in internals and prose with no defined status while every read-only detector was named an "audit" — resolved: a **Lint** is a Detector implemented as deterministic code, an **Audit** in the narrow sense is a Detector that is an LLM judge, and **Lint** ⊂ **Audit** (the umbrella read-only process). Deterministic scripts are `*-lint`; LLM judges keep "audit."
- "backlog" floated with no definition as a name for both the register of uncommitted ideas and the queue of open issues — resolved: say **Candidate** for an uncommitted entry in `CANDIDATES.md`, and **issue** for committed work. "backlog" is retired.
- "overwatch" named the managing role at both scopes — resolved: **Issue Manager** (one issue's traverse) and **Agent-View Manager** (the fleet). "overwatch" is retired.
- "promotion" was used for two different moves — carrying an under-specified leaf to ready, and turning a Candidate into an issue — resolved: **Promotion** means Candidate → issue. The readiness interview is the **refinement step**.
