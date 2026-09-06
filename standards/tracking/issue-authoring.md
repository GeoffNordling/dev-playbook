---
type: Standard
title: Issue Authoring
description: How a GitHub issue is authored — the derived roles, a leaf's four-tuple, readiness, and slicing, the build-leaf brief, the spike brief, the epic body, the wayfinder shapes, native relationships, and the rules every brief obeys
population: "a GitHub issue in a governed repo"
---

# Issue Authoring

A GitHub issue in a governed repo. An issue plays one of two derived
**roles**, leaf or epic; a leaf moves through a **readiness** lifecycle;
and its body is the agent **brief**, in the format its role and mode fix.
The rules bind wherever an issue is authored — at intake, when an idea or
a rushed stub becomes a tracked issue, and at the `design` node, when one
issue becomes an epic and its children. The commands that create, link,
label, and close an issue are
[Tracker Operations](/standards/tracking/tracker-operations.md); the
labels the tracker mints are
[Label Scheme](/standards/tracking/label-scheme.md).

An issue is **committed work**, at any size — an epic, an ordinary issue,
or a one-line bug. Work not yet decided on is a Candidate in
`CANDIDATES.md` ([Candidates](/standards/tracking/candidates.md)), and
the two are exclusive: a unit of work sits in one home, never both.
Deciding to write the brief is the act of committing, so a specifiable
idea nobody has chosen to build stays a Candidate, and promoting it
deletes its entry as the issue is authored.

## Roles

Every issue is exactly one of two roles, derived from the tracker and
never a label: an **epic**, an issue with sub-issues, or a **leaf**, an
issue without. There is no `epic` label to mint — the same principle as
*blocked*, a derived dependency state never minted as a label.

- **Leaf** — the unit of work. A factory leaf is dispatched through the
  [software factory graph](/software-factory/software-factory.md#the-graph),
  carries [the four-tuple](#the-four-tuple), and its body is a build-leaf
  brief or a spike brief. A decision ticket is a leaf outside the factory
  ([Wayfinder map or ticket](#wayfinder-map-or-ticket)).
- **Epic** — an issue decomposed into sub-issues. An epic is **never built
  directly**: no branch, no PR, no dispatch; its children carry the work.
  A build epic's children are build leaves, each a vertical slice of the
  outcome, and its body is [the epic body](#the-epic-body). A wayfinder
  map is the other species: a planning epic whose children are decision
  tickets.

## Relationships

Hierarchy and dependency are **native GitHub relationships** — never body
fields, never labels — wired when the work is decomposed, at the `design`
node, and orthogonal: a parent says nothing about order, and a blocker
says nothing about parentage.

- **Dependency — blocked-by.** The "must finish first" relationship, and
  the workhorse for sequencing slices. An issue is *blocked* while any
  issue it is blocked-by is still open, and *ready* once they all close.
  Blocked is a derived state, never a label.
- **Hierarchy — sub-issues.** The "part of" relationship: a parent issue
  and its children. It groups the slices of a large feature under a
  tracking **epic** — which is exactly what derives the epic role
  ([Roles](#roles)). Decomposition only — it implies no ordering, and a
  sub-issue is not blocked by its siblings unless a blocked-by edge says
  so.

Example — epic "User CSV export" (#10) sliced into schema (#11), API
(#12), UI (#13), docs (#14):

- Hierarchy: #11–#14 are sub-issues of #10.
- Dependency: #12 blocked-by #11; #13 blocked-by #12; #11 and #14 blocked
  by nothing.

The two graphs need not align: #14 is a sibling of #12 with no dependency
between them, and a blocker can cross epics (#12 could be blocked-by an
issue under a different parent).

## Leaf

An issue with no sub-issues that carries no `wayfinder:*` label: a
factory leaf, whether or not intake has triaged it yet.

### The four-tuple

A triaged leaf carries the four-tuple `(category:*, mode:*, tests:*,
phase:*)` — one label per dimension, each a scheme value, `phase:*`
naming its current node, and `mode:spike` paired with `tests:no`; an
untriaged leaf carries `phase:intake` or no labels at all, `phase:intake`
being the implied default. workspace-lint reports a post-intake leaf
whose tuple is incomplete, doubled, or off-scheme
(`tracking.tuple-valid`).

Intake assigns the triple `category:*`, `mode:*`, `tests:*` and the
phase, so triage *is* the four-tuple. Hierarchy and blocked-by are
tracked outside it ([Relationships](#relationships)).

### Readiness

A leaf at `phase:build` or beyond is ready — the industry's *Definition of
Ready*: every issue it is blocked-by is closed, its body is
brief-complete under [Build leaf](#build-leaf) or [Spike](#spike), and an
issue-review verdict released it, `phase:build` being that verdict's
consequence and its only evidence; a spike, whose deliverable is an
answer, is ready on the first two alone.

- **Unblocked** — every issue it is blocked-by is closed
  ([Relationships](#relationships)).
- **A brief-complete body** — an under-specified leaf is not yet ready.
- **Released at an issue-review verdict** — the definition session
  dispatched the two review lenses, edited the brief from what they
  returned, and the user approved the finished issue
  ([user-checkpoints.md](/software-factory/user-checkpoints.md#the-issue-review-verdict)).
  The user may always skip or override the beat; the release is theirs
  either way.

The bar governs the **one crossing out of definition**. An issue the
review stop sends back to `build` is already inside the factory and does
not re-cross: the rework lap carries the original release, and no fresh
issue review is owed. A leaf's role never changes as it readies; only its
body and phase advance.

### Vertical slices

A leaf minted by decomposition is a **tracer bullet** — a thin vertical
slice cutting through every integration layer end-to-end, never a
horizontal slice of one layer — sized so that building it keeps the agent
well under ~30% of its context window, and blocked-by the slice it must
follow.

- Each slice delivers a narrow but COMPLETE path through every layer
  (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Many thin slices beat few thick ones; anything bigger than the context
  budget is split.
- **A wide migration is sliced expand–contract.** A mechanical change
  whose blast radius hits every call site at once — renaming a shared
  symbol, retyping a column — has no vertical slice that lands green. It
  is sequenced instead: **expand**, adding the new form beside the old;
  then the callers migrated in batches sized by blast radius, one issue
  per batch, each blocked-by the expand; then **contract**, deleting the
  old form once no caller remains, blocked-by every batch. Every issue in
  the sequence leaves the system working.

Slices are created in dependency order and wired blocked-by their
predecessors ([Relationships](#relationships)): creating in order means
the blocker exists before the dependent links to it.

## Build leaf

A leaf carrying `mode:direct`: the ordinary path, an issue that ends in
merged code. Its body is the build-leaf brief.

### Required headings

The body carries **every heading in the template below** — none optional,
`Key interfaces` and `Prohibited surfaces` stating "none" when there are
none rather than being omitted. The list is exactly what workspace-lint
checks on live leaves (`tracking.issue-brief-shape`), so this document
and the rule cannot disagree.

```markdown
**Summary:** one-line description

**User intent:**
Why this issue exists — the goal the acceptance criteria are a proxy for —
and what wins when goods collide. Free prose in the user's words, five lines
at most; two or three sentences is typical.

**Current behavior:**
What happens now (or status quo for an enhancement).

**Desired behavior:**
What should happen after the work is complete. Be specific about edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns vs what it should return
- Config shape — any new options needed

**Acceptance criteria:**
- [ ] Specific, testable criterion 1
- [ ] Specific, testable criterion 2

**Prohibited surfaces:**
- `path/or/module` — why this issue must not touch it

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate
```

A brief reporting broken behavior may add a `Steps to reproduce` heading;
it is optional, unenforced, and changes none of the required headings.
`Out of scope` is explicit about what the issue will not change — the
adjacent features that are separate, the gold-plating deferred to a
sibling — and is what prevents it.

### Acceptance criteria

Each acceptance criterion is independently verifiable.

### Prohibited surfaces

`Prohibited surfaces` names only the paths, modules, or interfaces that
touching would be a real hazard, or "none"; it never strains to fill the
heading with a laundry list.

It constrains codebase territory the way `Out of scope` constrains idea
space, and it is what makes the codebase half of the second
[deviation limiter](/software-factory/deviation-contract.md#the-three-deviation-limiters)
mechanical: the implementing agent compares the file it is about to edit
against a list rather than weighing intent. "none" is the expected value.

### User intent

`User intent` is the user's own words, written fresh for the leaf — why
the issue exists and which way to lean when goods collide, the priority
ordering and which error direction is cheap — reconciled through the
User Intent Mini-Interview (`/user-intent-mini-interview`), repaired for
grammar and never enriched; one epic-level block copied into every child
is the defect this rule bans.

It is the one heading an agent does not compose: the user says their
intent cold, the agent surfaces where it collides with the drafted brief,
and the reconciled paragraph lands. Slices of one epic need different
orderings, which is why the copy-paste is the defect. The implementing
agent consults it for micro-decisions and for choosing among permitted
fixes; it is never grounds for whether a deviation is permitted. Spike
briefs and epic bodies never carry it.

### The Artifacts section

A brief whose deliverables include prose files or substantial new prose
sections — a skill, a standard's section — carries them verbatim in an
optional `## Artifacts` section, one `###` subsection per installed block
naming what it changes and where it lands with the approved content in a
code fence, and the section **binds when present**: the approved words
are part of the contract, and a review may cite them for a Blocking
finding exactly as it cites a required section
([the citeability rule](/software-factory/review-contract.md#the-two-severities)).

Several blocks commonly share one destination file; the destination may
be named in the subsection heading, or fixed once for the section where
every block shares it. Content that itself contains triple-backtick
fences uses a four-backtick outer fence. The acceptance criteria cite the
section ("install the artifacts as their subsections state"). The
approved words are not the builder's to edit — but everything about
fitting them in is: placement, heading levels, stitching into surrounding
text are ordinary build judgment under the brief's intent. Trouble with
the words themselves is a deviation. Approval of the text is part of the
issue-review verdict. If artifacts push the body toward GitHub's size
limit, they overflow to issue comments — stated loudly in the section,
never silently. Mechanical edits need no artifact. The heading is
optional and the lint never demands it, so a brief without one is
well-shaped.

## Spike

A leaf carrying `mode:spike`: a **question** whose deliverable is an
**answer**, not merged code. The findings land in the issue's closing
comment, and no PR opens
([the spike state](/software-factory/software-factory.md#the-definition-region)).

### Spike headings

The body carries `Summary`, `Question`, and `Deliverable`
(`tracking.issue-brief-shape`):

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question the spike answers — narrow enough to resolve in one focused investigation.

**Deliverable:**
What a good answer looks like. The answer itself lands in the closing comment
(plus a Decision Record if a one-way door was crossed).
```

## Epic

An issue with sub-issues that carries no `wayfinder:*` label: a build
epic.

### Category only

An epic carries exactly one `category:*` label, a scheme value, and no
`phase:*`, `mode:*`, or `tests:*` label; workspace-lint reports the rest
(`tracking.epic-shape`).

Nothing dispatches on an epic, so nothing routes it.

### The epic body

The body states the **outcome** and the **decomposition rationale**,
under the two headings below, and never duplicates the native sub-issue
list.

```markdown
**Outcome:**
The end state once every child has merged.

**Decomposition rationale:**
Why the work was sliced this way — the ordering constraints and shared surfaces
that shaped the slices.
```

### Optional sections

`Out of scope` and `Standing rulings` are added when — and only when —
the epic accrues one, a boundary that keeps getting re-asked or a ruling
made after the decomposition that binds more than one child; and
`Standing rulings` is numbered, appended to, never renumbered.

A fresh epic carries neither, and most never grow them; an empty heading
is boilerplate, not structure.

```markdown
**Out of scope:**
- What this epic will not do, and why. Link the child, where one was closed as mis-scoped.

**Standing rulings:**
1. The ruling in one line, stated as the constraint it puts on children.
```

**Out of scope** rules work outside the outcome: it will never become a
child. A boundary earns a line when a reader could reasonably have
assumed the opposite. Work inside the outcome but not yet sliced is a
child not created yet — the decomposition rationale's business. A leaf's
`Out of scope` defers gold-plating to a sibling; an epic's rules out work
no sibling will pick up.

**Standing rulings** holds decisions taken after the epic was written
that constrain children not yet built. Governing unbuilt work is what
earns a ruling its place — this is not an index of closed children, nor a
changelog. The number is how a child cites a ruling. A decision binding
one child belongs in that child's brief; one meeting the Decision Record
bar gets a record under `docs/decisions/`
([records.md](/standards/decisions/records.md)).

## Wayfinder map or ticket

An issue carrying a `wayfinder:*` label: a **wayfinder map**, a planning
epic whose children are decision tickets — research, prototype, grilling,
and task tickets that close by producing an answer rather than shipping a
slice — or a **decision ticket**, one of those children. The `/wayfinder`
skill drives a map and owns its body shape, its ticket's question, and
its working loop; the skill is the definition, workspace-lint mirrors the
skill's own statement of the body shape, and this Standard restates none
of it. The tracker moves a map runs on are in
[Tracker Operations](/standards/tracking/tracker-operations.md#wayfinding-operations).

### No factory label

A map and a ticket carry no `category:*`, `mode:*`, `tests:*`, or
`phase:*` label: neither enters the factory graph, and a ticket is not a
factory leaf — no four-tuple, no dispatch, no build-leaf or spike brief.
workspace-lint reports one that does (`tracking.wayfinder-shape`).

### Wayfinder labels

A map carries `wayfinder:map` and no ticket type; a ticket carries
exactly one `wayfinder:<type>`, a scheme value, and is a native sub-issue
of its map; a ticket that must wait for another is blocked-by it
(`tracking.wayfinder-shape`).

## One goal

A brief serves one master, at leaf and at epic altitude: any part that
could slip indefinitely with the outcome still standing, and could ship
later as its own issue without reopening this one, is deferred — a
tracker stub minted at `phase:intake`, never a Candidate, and named in
`Out of scope`.

The deferred part is committed work already, by sitting inside an
approved outcome, which is why it becomes a stub and not a Candidate. The
test is applied when slicing and backstopped at issue review.

## Behavioural, not procedural

A brief describes what the system should do — interfaces, types, and
behavioural contracts — never how to implement it, and names no file path
or line number: the issue may sit for days or weeks, and those go stale
while a contract holds.

The agent will explore and decide.

## Written for the user

A brief is readable unaided by the user, who sees only the issue and
never the author's context: any reference to existing file content, an
artifact placement note above all, quotes the text it amends verbatim,
before/after style. A brief the user cannot follow is defective even when
the implementer could follow it.

## Prototype claims

A brief cites a prototype as proof only for what the prototype executed
for real — real transport, real hook, real filesystem — as the code stood
when it ran; the claim cites branch + path and names the stubs bearing
on it, and a prototype claim with no citable committed artifact is
demoted to assumed.

Everything the prototype faked is a stub, and a stubbed thing can never
be cited as proven: honesty about fidelity is required, fidelity is not.
The brief may carry a verbatim snippet the prototype produced. Capture is
the `/prototype` skill's: the code on a throwaway branch off main, the
answer — the verdict and the question it settled — in the issue or a
commit. The branch is pushed: remotes are never pruned, so a pushed
throwaway branch is disposable and permanently citable at once.

## Claim provenance

Every empirical claim a brief makes about existing reality carries one
of two grades, **measured** — the probe was run, and its observed output
is cited — or **assumed**; a measured claim without checkable evidence is
demoted to assumed at issue review.

Evidence lives in a probe-record comment on the issue (the probe command
and its observed output); a one-line output may sit inline instead.
Grades are authored where the claim is authored.

## The brief freeze

A brief is frozen when its issue launches into the factory: the body is
never amended after launch — not by agents, not by user rulings.

Rulings live as comments on the issue or PR; the launch baseline, the
[deviation ledger](/software-factory/deviation-contract.md#the-deviation-ledger),
and the rulings together make the issue's full drift visible.
