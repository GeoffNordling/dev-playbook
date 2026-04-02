# Repo Documentation Standard

The key words "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in the [spec-driven-development standard](spec-driven-development.md).

## Purpose

Define a consistent file hierarchy and scope boundary for every repository in the workspace, so that any human or agent can open a repo cold and immediately orient — what it is, how to operate it, and what's next.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope (what goes in it), but depth varies by project. A CLI tool's README may be 10 lines. A simulation's may be 100. Both are conformant if the content stays within scope.

**Presence is the status signal.** There are no explicit status fields. The presence or absence of optional files tells you what stage the project is in. An empty or missing ROADMAP.md means nothing is planned. A populated specs/ directory means the project is complex enough to warrant formal requirements.

**No duplication across files.** Each piece of information has exactly one home. Files reference each other rather than repeating content.

## Required Files

Every repository SHALL have these files.

### README.md

**Audience:** Human
**Scope:** What is this and how do I use it.

- What the project does
- Prerequisites and setup
- How to run it

README.md SHALL NOT contain: agent instructions, roadmap items, business rationale, or architecture decisions.

### CLAUDE.md

**Audience:** Agent (Claude Code)
**Scope:** How to operate in this repo.

- Build, run, and test commands
- Rules and constraints (what not to do, what to always do)
- Pointers to other docs the agent should consult before specific tasks

CLAUDE.md SHALL NOT contain: what the project is, why it exists, what's planned, or developer profile information (global preferences belong in `~/.claude/` rules, not per-repo).

## Optional Files

These files have standardized names and locations. They exist when needed and are absent when not. Each layer builds on the previous — the further down the list, the more complex the project.

### ROADMAP.md

**Audience:** Human and agent
**Scope:** What's next.
**Location:** Repository root

- Planned work, ordered by priority
- No timelines, no assignees — just what and roughly why

**Presence signal:** Exists with items = forward work planned. Absent = nothing planned (stable or parked).

**What's next?** To find the next step in any repo: open ROADMAP.md. If it doesn't exist, check `gh issue list`. If neither has items, nothing is planned.

ROADMAP.md SHALL NOT contain: timelines, status tracking, or completed items. It is a forward-looking document.

### BUSINESS_CONTEXT.md

**Audience:** Human and agent
**Scope:** Why this exists in the real world.
**Location:** Repository root

- The domain problem, the stakeholders, the constraints
- What you'd explain to someone who asked "why are you building this?"

Only needed when the domain isn't obvious from README.md alone. A simple CLI tool doesn't need one. A simulation modeling a robotics assembly line does.

### specs/

**Audience:** Human and agent
**Scope:** What the system does and how it's built, formally.
**Location:** `/specs/` directory in repo root

- `functional_requirements.md` — behavior in EARS + RFC 2119
- `design.md` — components, interfaces, and data flow in RFC 2119

The [spec-driven-development standard](spec-driven-development.md) governs how specs are written, structured, and maintained. Refer to it for format, requirement IDs, splitting rules, and the relationship between functional requirements and system design.

### docs/adr/

**Audience:** Human and agent
**Scope:** Why we made each significant technical choice.
**Location:** `/docs/adr/` directory in repo root

- One file per decision, immutable once written
- Indexed by `docs/adr/README.md`

The [spec-driven-development standard](spec-driven-development.md) defines when ADRs are appropriate and how they relate to the design spec. Refer to it for format and usage guidance.

## The Implicit Status Ladder

No repo needs a status field. File presence tells you everything:

| What exists | What it tells you |
|---|---|
| README + CLAUDE.md only | Simple or stable. Nothing planned. |
| + ROADMAP.md | Forward work is planned. |
| + BUSINESS_CONTEXT.md | Domain is non-trivial. |
| + specs/ (functional only) | Complex enough for formal requirements. |
| + specs/design.md | Complex enough to need explicit system structure. |
| + docs/adr/ | Enough architectural decisions to warrant a log. |

## Tactical Work

Specific, actionable work items (bugs, tasks, features) SHALL be tracked in GitHub Issues, not in-repo files. There SHALL NOT be a TODO.md, TASKS.md, or similar file in the repository.

GitHub Issues is the single source of truth for "what specific thing should I do next." ROADMAP.md provides strategic direction; issues provide tactical actions.
