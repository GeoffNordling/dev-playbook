# Repo Documentation Standard

The key words "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in
[sdd-standards/rfc2119.md](~/workspace/dev-playbook/sdd-standards/rfc2119.md),
including the workspace subset and formatting rules in its
[Extensions](~/workspace/dev-playbook/sdd-standards/rfc2119.md#extensions)
section.

## Purpose

Define a consistent file hierarchy and scope boundary for every repository in the workspace, so that any human or agent can open a repo cold and immediately orient — what it is, how to operate it, and what's next.

## Principles

**Scope is standardized; depth is not.** Every file has a defined scope (what goes in it), but depth varies by project. A CLI tool's README may be 10 lines. A simulation's may be 100. Both are conformant if the content stays within scope.

**Presence is the status signal.** There are no explicit status fields. The presence or absence of optional files tells you what stage the project is in. An empty or missing ROADMAP.md means nothing is planned. A populated specs/ directory means the project is complex enough to warrant formal requirements.

**No duplication across files.** Each piece of information has exactly one home. Files reference each other rather than repeating content.

## Audience and Presence

Every file in the documentation hierarchy has two properties.

### Audience

Who is expected to read the file. These are intended audiences, not access
restrictions — a human may read CLAUDE.md; an agent may read a human-audience
file. The distinction governs formatting conventions and cross-reference style.

All cross-references `SHALL` use the full path starting with `~/workspace/` — e.g., `~/workspace/dev-playbook/sdd-standards/spec-format.md`. The `ref-check` tool (`~/workspace/dev-playbook/tools/bin/ref-check`) lints every reference in this form and reports broken links; anything else — e.g. backticked filenames like `conftest.py` or repo-relative paths — is treated as prose and ignored. The audience determines the wrapper:

| Audience | Cross-reference style |
|---|---|
| Human | Inline link with full path as target — e.g., `[spec format walkthrough](~/workspace/dev-playbook/sdd-standards/spec-format.md)`. |
| Human + Agent | Same as Human. |
| Agent | Full path as inline code — e.g., `` `~/workspace/dev-playbook/sdd-standards/spec-format.md` ``. No inline links; they add syntax noise without adding information for an agent. |

### Fenced code blocks

Fenced code blocks delimited by triple backticks or `~~~` may contain `~/workspace/` paths in shell examples or sample output; `ref-check` skips them. For example:

```bash
# Run ref-check from any workspace repo:
python3 ~/workspace/dev-playbook/tools/bin/ref-check .
```

### Presence

Whether the file is required or optional.

| Presence | Meaning |
|---|---|
| Required | Every repository `SHALL` have this file. |
| Optional | A repository `MAY` have this file. Exists when needed, absent when not. |

## Files

| File | Audience | Presence | Scope |
|---|---|---|---|
| `CLAUDE.md` | Agent | Required | How to operate in this repo: build/run/test commands, rules, pointers to other docs. `SHALL NOT` contain what the project is, why it exists, or developer profile information. |
| `README.md` | Human + Agent | Required | What the project does, prerequisites, how to run it. `SHALL NOT` contain agent instructions, roadmap items, or architecture decisions. |
| `ROADMAP.md` | Human + Agent | Optional | Strategy: broad goals and aspirations for the project. No priority ordering, timelines, or assignees. `SHALL NOT` contain actionable work items — those belong in GitHub Issues. |
| `BUSINESS_CONTEXT.md` | Human + Agent | Optional | Domain context for corporate/business projects: the business problem, stakeholders, and why the project exists. Not applicable to non-corporate projects. |
| `specs/` | Human + Agent | Optional | Functional requirements and optionally system design, as flat files or hierarchical folders. See the [spec format walkthrough](~/workspace/dev-playbook/sdd-standards/spec-format.md) for content conventions and [oft-format.md — File organization](~/workspace/dev-playbook/sdd-standards/oft-format.md#file-organization--extension) for file layout and splitting rules. |
| `docs/` | Human + Agent | Optional | Supplementary documentation that does not belong in README, specs, or CLAUDE.md. |
| `docs/adr/` | Human + Agent | Optional | Architectural decision records. One per file, immutable once written, indexed by `docs/adr/README.md`. |

## Tactical Work

Specific, actionable work items (bugs, tasks, features) `SHALL` be tracked in GitHub Issues, not in-repo files. There `SHALL NOT` be a TODO.md, TASKS.md, or similar file in the repository.

GitHub Issues is the single source of truth for "what specific thing should I do next."
