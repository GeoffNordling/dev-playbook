---
name: fill-issue-gaps
description: Audits a triaged but under-specified child issue of an epic — reading its scope files and its parent epic — then closes the gaps that would make an autonomous implementer improvise. It surfaces the intent decisions only the user can make and rewrites the issue body in place to fold in the resolutions. Use when a sub-issue of an epic needs a pre-implementation readiness pass before an AFK build/tdd node picks it up, when the user invokes /fill-issue-gaps on an issue number or URL, or when a batch of similarly-written child issues needs vetting before dispatch.
disable-model-invocation: false
model: fable
effort: xhigh
argument-hint: "[issue] [epic]"
---

# Fill Issue Gaps

A pre-implementation readiness pass for **one child issue of an epic**. The issue is already triaged — four-tuple labels, a brief — but written well-scoped and thin, so an AFK implementer would improvise the missing detail and risk building the wrong thing. This skill catches that intent-mismatch risk: it audits the issue against its scope files and its epic, surfaces the decisions only the user can make, and **rewrites the issue body in place** to close the gaps. It never touches the scoped code, and it does not re-triage — that was intake's job.

## Read first

Before doing anything else, read [issue conventions](~/workspace/dev-playbook/standards/tracking/issues.md) end-to-end — the brief format the rewritten body must conform to. Then report `READ: issue-conventions.md` and proceed.

## Process

### 1. Load the issue and its epic — issue: $0, epic: $1

- `gh issue view $0 --comments` — read the body, the four-tuple, the acceptance criteria, and the out-of-scope list.
- Identify the **parent epic** — passed as `$1`, else the sub-issue parent this issue was minted under (try `gh issue view` and its blocked-by chain). If neither resolves it, ask the user for the epic number. Read the epic's body: its decomposition rationale and the seams between slices tell you **what is deliberately deferred to sibling slices** — the single fact that separates a real gap from an intended deferral.
- No epic at all → say so and proceed standalone, noting the gap-vs-deferral call is now weaker.

### 2. Read the scope in full

Read every file the issue names as a key interface — in full, not excerpts. The gaps hide in the details a summary drops.

### 3. Chase the load-bearing cross-references

The issue makes claims about the repo — "the rule lives in X", "every Y cites Z", "verified by W", pointers between docs. Open each referenced file and confirm it actually says what the issue assumes; a pointer to a rule that isn't there is the highest-value catch. Grep the stated scope for any term the acceptance criteria say must appear, vanish, or change, to confirm the real blast radius. Check each out-of-scope deferral against the epic: a deferral with no sibling home is itself a gap.

### 4. Triage into three tiers

- **Decisions** — genuine intent ambiguities where a wrong guess is costly. These go to the user; you never resolve them yourself.
- **Gaps** — under-specification an implementer would silently improvise, each closable by a sentence *you draft*.
- **Mechanical notes** — things the implementer should know that need no decision (a grep gotcha, a false positive, a confirmation).

Use the epic (§1) to keep deferrals out of the gap list. Example: a stale name the issue leaves untouched is a **gap** when nothing explains it, a **note** when the epic assigns the rename to a later slice.

### 5. Resolve with the user — HITL gate

Present all three tiers in one tight message, recommendation-first on every decision. Get the user's call on each tier-1 **Decision**, asked in prose — `AskUserQuestion` is denied globally. Then show the concrete rewrite you intend (resolved decisions plus the drafted gap-sentences) and land only on their nod. This gate is the skill's whole point: never guess a decision, and never overwrite the body without the nod. If the audit surfaced nothing at tier 1 or tier 2, say so and make no edit.

### 6. Rewrite the body in place

Fold the resolved decisions and the drafted gap-sentences **directly into the brief** — sharpen the desired-behavior section, tighten the acceptance criteria, add the missing specifics inline. No "Update:" banner, no changelog, no amendment marker: the body must read as if it were authored complete. Preserve the brief format ([issue conventions](~/workspace/dev-playbook/standards/tracking/issues.md)) and the four-tuple untouched. Fold in a mechanical note only where it changes what gets built; drop the rest. Write with `gh issue edit $0 --body`.

### 7. Report

One line: `<repo>#<issue> · <n> decisions resolved, <m> gaps filled · body rewritten in place` — or `· already precise, no change` when nothing needed filling.

### 8. Stop — launch nothing else

The gaps pass is the whole job. When the report is out, **pause and hand back to the user**: do not dispatch the next node, do not launch any other agent or skill on the issue, do not advance the phase. This skill runs on the `fable` model; the user manually downgrades to Opus before the next node picks the issue up, so stand by after the report and wait for the user — the model switch is their step, not yours.
