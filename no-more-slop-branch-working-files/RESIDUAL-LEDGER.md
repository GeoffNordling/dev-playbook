---
type: General-Sheet
title: Residual Ledger
description: Per unit, what its full rewrite could not express in the edge-encoding map — each entry awaiting a verdict
---

# Residual Ledger

Per unit ported to the
[Edge Encoding](/no-more-slop-branch-working-files/EDGE-ENCODING.md) map:
what the full rewrite could not express in it. Each entry awaits a
verdict — valuable (amends the shared structure) or not (reworded away).

## log-friction

The rewrite converges: every sentence is a primitive, an accounted
internal, or one of these residuals.

1. **Behavior-mode block** — "Run to completion without asking the user
   anything … fire-and-forget …". The higher level already ledgers this
   category (orchestrate's whole body, diagnosing-bugs' secret-redaction
   rule) as remembered-not-primitive. It recurs; strongest candidate for
   a future primitive.
2. **Control flow** — "and stop" in the nothing-to-record bullet. Early
   exit has no primitive; it rides as uncoded payload words the agent
   obeys.
3. **Rationale prose** — "An imperfect entry is cheap: the log is
   append-only prose …". Not an instruction — why-text calibrating the
   agent's judgment. No primitive expresses justification.

Accounted: the three unbraced `If` bullets (the deliberate
uncoded-conditional tier); step 2's entry-writing and step 3's staging
detail (internal program below the CLOA); the working-tree edit itself
(subsumed by the git commit edge, exactly as the ledger's chain models
it).

## document-deslop

Partially rewritten: args and does→Agent are encoded; the Review
section waits on a conditional-report round. Candidates so far:

1. **Negated edge** — "This skill never commits." No primitive
   expresses the absence of an edge.
2. **Conditional report** — "Relay the problem to the user" versus
   "Say nothing and go on": the report to the caller depends on the
   subagent's reply, and one branch deliberately reports nothing.
   Likely resolvable without a new primitive: deslopper's Report back
   encodes the same shape as guard-contained `{Report …}` spans.

## grill-with-docs

The rewrite converges; one candidate:

1. **Override-scope prose** — "Everything else applies as written" and
   "Its `CONTEXT.md` format applies as written": statements of what is
   *not* overridden. Same family as document-deslop's negated edge —
   prose asserting an edge's absence.

## usage-report

The rewrite converges — the body is one span. One candidate:

1. **Script subtree** — the ledger's chain draws a reads edge under
   `report.sh` (`~/.cache/claude-code/usage.json`). A shell script has
   no frontmatter and no spans, so nothing in the map can generate a
   Script's sub-edges; the does edge ends at the file.

## deslopper

The rewrite converges — reads, guarded read, local-file write, and two
guarded reports all land in the map. Candidates:

1. **The enforce relationship** — Run 1's chain drew
   `does → [slop-tics] Standard — .enforce`. The map expresses the
   relationship as `{Read [slop-tics.md]}`: honest (the agent must read
   the tics) but flat — no expression says this unit is the *enforce
   arm* of a Standard.
2. **Agent inputs** — "The launching prompt names the working directory
   and the target document." A skill's args derive from frontmatter
   `arguments`; an agent has no such field, so its inputs ride as
   prose.
3. **Recurrences** — "you never commit" (negated edge, third sighting)
   and "Conformance to the standard is the goal …" (rationale prose,
   second sighting).

## ralph-setup

The first corpus-port unit; the rewrite converges — read, does, two
guarded local-file writes, one report. Candidates:

1. **Named reports** — the hand-drawn chain says
   `launch_command: str`; the map's Report payload renders the
   constant `outcome: str`, so the name rides only in the annotation
   ("the full launch command for the user to run"). Accepted for now —
   no naming syntax invented; candidate-promote's `issue_number: int`
   will re-raise this.
2. **Mid-run acknowledgment** — "Then say `READ: ralph-loop.md` and
   proceed" reads like a report but targets the conversation, not the
   invoker; left as plain prose, reworded from "report" to "say" so no
   shadow prose remains.
3. **Hard gates restated as guard** — sections 3–5 stop the run in
   prose ("nothing is written until the user approves"); the guard on
   the two Write spans restates those conditions at the write site.
   The duplication is deliberate: the prose stops the agent, the guard
   draws the dashes.
