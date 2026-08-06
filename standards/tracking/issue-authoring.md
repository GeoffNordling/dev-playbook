---
type: Standard
title: Issue Authoring
description: How a GitHub issue is authored — epic and leaf roles, readiness, the three brief formats and the optional Artifacts section, the brief principles governing claim provenance and prototype claims, vertical slices, and native relationships
---

# Issue Authoring

How GitHub Issues are authored in workspace repos. An issue plays one of two
**roles** and, as a leaf, moves through a **readiness** lifecycle; its body is
the agent **brief**, in one of three formats. Applies wherever issues are
authored — at intake, when an idea or a rushed stub becomes a tracked issue, and
at the `design` node, when one issue becomes an epic and its children. Driving
the tracker itself — the commands that create, link, and close issues — is
[tracker-operations.md](/standards/tracking/tracker-operations.md).

An issue is **committed work**, at any size — an epic, an ordinary issue, or a
one-line bug. Work not yet decided on is a Candidate in `CANDIDATES.md`
([candidates.md](/standards/tracking/candidates.md)), and the two are
exclusive: a unit of work sits in one home, never both. Deciding to write the
brief below is the act of committing, so a specifiable idea nobody has chosen
to build stays a Candidate — and promoting it deletes its entry as the issue is
authored.

## Roles: epic and leaf

Every issue carrying build work through the software factory is exactly one of
two roles. The role is **derived**, never a label — the same principle as
*blocked* (a derived dependency state, never minted as a label).

- **Leaf** — the unit of work. A leaf is dispatched through the
  [software factory graph](/software-factory/software-factory.md#the-graph) and carries the full four-tuple
  `(category:*, mode:*, tests:*, phase:*)`. Its body is a build-leaf brief or a
  spike brief (below).
- **Epic** — an issue decomposed into sub-issues. An epic is **never built
  directly**: no branch, no PR, no dispatch. It carries a **category label
  only** — no phase, mode, or tests label — and its epic role is derived purely
  from having sub-issues, so there is no `epic` label to mint. Its body is the
  epic body (below): the outcome and the decomposition rationale, never a
  restatement of the native sub-issue list GitHub already shows.

**A design session produces an epic.** The common way an epic is born is the
`design` node concluding the work is too big for one leaf: the session
decomposes it in place, turning the issue into an epic and minting its children
as ready leaves (see [the decompose exit](/software-factory/software-factory.md#the-definition-region)).

### Two species of epic

The two roles are the whole model for factory-tracked build work, but an epic
comes in two species, told apart by what its children are *for*:

- **Wayfinder map** — a **planning** epic whose children are decision tickets:
  research, prototype, grilling, and task tickets that close by producing an
  answer rather than shipping a slice. A map is driven by the `/wayfinder`
  skill, which owns its body shape, its labels, and its working loop; the skill
  is the definition, and this standard restates none of it. The tracker moves a
  map runs on are in
  [tracker-operations.md](/standards/tracking/tracker-operations.md).
- **Build epic** — children are build leaves, each a vertical slice of the
  outcome. This is the default species, and the one the epic body below
  describes.

A decision ticket is **not a factory leaf** and carries none of a leaf's
obligations: no four-tuple, no dispatch through the software factory graph, no
build-leaf or spike brief. What a ticket does carry is the `/wayfinder` skill's
to define.

**Neither species carries a factory label.** A map and a ticket both stay outside
the factory graph; they do not carry `category:*`, `mode:*`, `tests:*`, or
`phase:*` labels. That much is this standard's rule, and workspace-lint reports
it. The rest of their shape — the map's body sections, the ticket's question, the
`wayfinder:<type>` vocabulary — stays the skill's, and the lint mirrors the
skill's own statement of it rather than a restatement here.

## Readiness

Readiness is a **lifecycle position, not a kind of issue** — the industry's
*Definition of Ready*. Three things make an issue ready, and work is dispatched
only when all three hold:

- **A leaf** — an epic is decomposed, never built
  ([Roles](#roles-epic-and-leaf)).
- **Unblocked** — every issue it is blocked-by is closed
  ([Relationships](#relationships)).
- **A brief-complete body**, meeting the brief standard below; an
  under-specified leaf is not yet ready.

The refinement interview — intake, or the `design` node — is the **refinement
step** that carries a leaf to ready by authoring its brief. A leaf's role never
changes as it readies; only its body and phase advance.
(**Promotion** is a different move, reserved for Candidate → issue.)

## The body is the brief

The issue body IS the agent brief. There are **three brief formats**, one per
role-and-mode. Each format's required headings are stated explicitly below, and
are exactly the lists the [`tracking.issue-brief-shape` audit](/scripts/workspace-lint)
checks on live leaves — so this document and the rule cannot disagree.

Dependencies and hierarchy are **not** body fields — they are native GitHub
relationships; see [Relationships](#relationships).

### The build-leaf brief (`mode:direct`)

A build leaf carries **all seven** headings — none optional. `Key interfaces`
states "none" when there are none, rather than being omitted.

`User intent` answers why this issue exists and which way to lean when goods
collide — the priority ordering, and which error direction is cheap. Its
decisions come from above — the epic, or the design work behind it — already
made and not re-asked: writing this section is distillation, not a new
interview. But the *text* is written fresh for each leaf, because slices of
one epic need different orderings; copy-pasting one epic-level block into
every child is the defect this rule bans. The implementing agent consults it
for micro-decisions and for choosing among permitted fixes; it is never
grounds for whether a deviation is permitted. Build-leaf briefs only — spike
briefs and epic bodies never carry it.

```markdown
**Summary:** one-line description

**User intent:**
Why this issue exists — the goal the acceptance criteria are a proxy for —
and what wins when goods collide. Free prose, five lines at most.

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

**Out of scope:**
- Things that should NOT be changed
- Adjacent features that are separate
```

A brief reporting broken behavior may add a `Steps to reproduce` heading; it is
optional, unenforced, and changes none of the required headings.

#### The Artifacts section

A brief whose deliverables include prose files or substantial new prose
sections — a skill, a standard's section — carries them verbatim in an
optional `## Artifacts` section: one `###` subsection per installed block,
each naming what it changes and where it lands, the approved content in a
code fence. Several blocks commonly share one destination file; the
destination may be named in the subsection heading, or fixed once for the
section where every block shares it. Content that itself contains
triple-backtick fences uses a four-backtick outer fence. The acceptance
criteria cite the section ("install the artifacts as their subsections
state").
The approved words are not the builder's to edit — but everything about
fitting them in is: placement, heading levels, stitching into surrounding
text are ordinary build judgment under the brief's intent, and a placement
note is guidance, not a script. Trouble with the words themselves is a
deviation. Approval of the text is part of the issue-review verdict. If
artifacts push the body toward GitHub's size limit, they overflow to issue
comments — stated loudly in the section, never silently. Mechanical edits
need no artifact.

### The spike brief (`mode:spike`)

A spike is a **question** whose deliverable is an **answer**, not
merged code — the findings land in the issue's closing comment, and no PR opens
(see [the spike state](/software-factory/software-factory.md#the-definition-region)). The spike brief carries
these headings:

```markdown
**Summary:** one-line framing of the question

**Question:**
The specific question the spike answers — narrow enough to resolve in one focused investigation.

**Deliverable:**
What a good answer looks like. The answer itself lands in the closing comment
(plus a Decision Record if a one-way door was crossed).
```

### The epic body

An epic's body is not a brief for work — nothing dispatches on it. It states the
**outcome** and the **decomposition rationale**, and never duplicates the native
sub-issue list.

```markdown
**Outcome:**
The end state once every child has merged.

**Decomposition rationale:**
Why the work was sliced this way — the ordering constraints and shared surfaces
that shaped the slices.
```

#### Optional sections

A long-running epic accumulates two things the required sections have no home
for: a boundary that keeps getting re-asked, and a ruling made after the
decomposition that binds more than one child. Each gets an **optional** section,
added when — and only when — the epic actually accrues one. A fresh epic carries
neither, and most never grow them; an empty heading is boilerplate, not
structure.

```markdown
**Out of scope:**
- What this epic will not do, and why. Link the child, where one was closed as mis-scoped.

**Standing rulings:**
1. The ruling in one line, stated as the constraint it puts on children.
```

**Out of scope** rules work outside the outcome: it will never become a child. A
boundary earns a line when a reader could reasonably have assumed the opposite.
Work inside the outcome but not yet sliced is a child not created yet — the
decomposition rationale's business. A leaf's `Out of scope` defers gold-plating
to a sibling; an epic's rules out work no sibling will pick up.

**Standing rulings** holds decisions taken after the epic was written that
constrain children not yet built. Governing unbuilt work is what earns a ruling
its place — this is not an index of closed children, nor a changelog. Numbered,
appended to, never renumbered: the number is how a child cites a ruling. A
decision binding one child belongs in that child's brief; one meeting the
Decision Record bar gets a record under `docs/decisions/`
([records.md](/standards/decisions/records.md)).

## Brief principles

- **Durability over precision.** The issue may sit for days or weeks. Describe interfaces, types, and behavioural contracts. File paths and line numbers go stale.
- **Behavioural, not procedural.** Describe what the system should do, not how to implement it. The agent will explore and decide.
- **Testable acceptance criteria.** Each criterion is independently verifiable.
- **Explicit out-of-scope.** Prevents gold-plating.
- **One goal.** A brief serves one master. Test any doubtful part with two
  questions: would the outcome still stand if this part slipped
  indefinitely, and could it ship later as its own issue without reopening
  this one? Both yes — it must be deferred: mint a real tracker stub at
  `phase:intake` (never a Candidate — the deferred part is committed work
  already, by sitting inside an approved outcome) and name it in
  `Out of scope`. This binds at leaf and at epic altitude, applied when
  slicing and backstopped at issue review.
- **Written for the human reader.** The human sees only the issue — never
  the author's context. Any reference to existing file content, especially
  an artifact placement note, quotes the text it amends verbatim,
  before/after style. A brief the human cannot follow unaided is defective
  even when the implementer could follow it.

**Prototype claims.** A brief may cite a prototype as proof, and may carry a
verbatim snippet a prototype produced. "Proven" means the prototype executed
that specific thing against the real substrate — real transport, real hook,
real filesystem — with the run's observed output in the committed record.
Everything the prototype faked is a declared stub, and a stubbed thing can
never be cited as proven: honesty about fidelity is required, fidelity is
not. Prototypes commit to a `worktree-design-<issue>` branch carrying the
code, the stub list, and the run outputs; the brief cites branch + path, and a
prototype claim with no citable committed artifact is demoted to assumed. The
branch survives until everything citing it has merged.

### Claim provenance

Every empirical claim a brief makes about existing reality carries one of two
grades: measured — the probe was run, and its observed output is cited — or
assumed. Evidence lives in a probe-record comment on the issue (the probe
command and its observed output); a one-line output may sit inline instead. A
measured claim without checkable evidence is demoted to assumed at issue
review. Grades are authored where the claim is authored; the authoring
session surfaces the claims it believes load-bearing and the human picks
which to probe.

### The brief freeze

A brief is frozen when its issue launches into the factory: the body is
never amended after launch — not by agents, not by human rulings. Rulings
live as comments on the issue or PR; the launch baseline, the
[deviation ledger](/software-factory/deviation-contract.md#the-deviation-ledger),
and the rulings together make the issue's full drift visible.

## Vertical-slice rules

When one idea becomes many issues, break the plan into **tracer bullet** issues. Each issue is a thin vertical slice cutting through ALL integration layers end-to-end, not a horizontal slice of one layer.

- Each slice delivers a narrow but COMPLETE path through every layer (schema, API, UI, tests).
- A completed slice is demoable or verifiable on its own.
- Prefer many thin slices over few thick ones.
- **Size to the context budget.** Slice thin enough that building one issue keeps the agent well under ~30% of its context window. Split anything bigger.
- **Slice a wide migration expand–contract.** A mechanical change whose blast radius hits every call site at once — renaming a shared symbol, retyping a column — has no vertical slice that lands green. Sequence it instead: **expand**, adding the new form beside the old; then migrate the callers in batches sized by blast radius, one issue per batch, each blocked-by the expand; then **contract**, deleting the old form once no caller remains, blocked-by every batch. Every issue in the sequence leaves the system working.

Create slices in dependency order, then wire the native relationships (see [Relationships](#relationships)): mark each ordered slice **blocked-by** its predecessor. Creating in order means the blocker exists before the dependent links to it.

## Relationships

Two independent relationships connect issues. Both are **native GitHub relationships** — not body fields, not labels — wired when the work is decomposed, at the `design` node. They are orthogonal: a parent says nothing about order, and a blocker says nothing about parentage.

- **Dependency — blocked-by.** The "must finish first" relationship, and the workhorse for sequencing slices. An issue is *blocked* while any issue it is blocked-by is still open, and *ready* once they all close. Blocked is a derived state, never a label — don't mint one.
- **Hierarchy — sub-issues.** The "part of" relationship: a parent issue and its children. Use it to group the slices of a large feature under a tracking **epic** — which is exactly what derives the epic role (see [Roles](#roles-epic-and-leaf)). Decomposition only — it implies no ordering, and a sub-issue is not blocked by its siblings unless a blocked-by edge says so.

Example — epic "User CSV export" (#10) sliced into schema (#11), API (#12), UI (#13), docs (#14):

- Hierarchy: #11–#14 are sub-issues of #10.
- Dependency: #12 blocked-by #11; #13 blocked-by #12; #11 and #14 blocked by nothing.

The two graphs need not align: #14 is a sibling of #12 with no dependency between them, and a blocker can cross epics (#12 could be blocked-by an issue under a different parent).
