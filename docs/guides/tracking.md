---
type: Guide
title: Tracking Guide
description: The thinking behind the tracking rules — what a Candidate is and how it becomes an issue, the roles and relationships an issue has, the five species, what the labels mean, and why the repository settings are what they are, with the hand-set ruleset spelled out
---

# Tracking Guide

The guide behind the three tracking Standards,
[Issue Shapes](/standards/tracking/issue-shapes.md),
[Label Scheme](/standards/tracking/label-scheme.md), and
[Repository Settings](/standards/tracking/repo-settings.md). Each states
its rules as predicates a reviewer or a script can decide; this guide
carries the vocabulary, the reasoning, and the examples that make the
rules intelligible, and it documents the one GitHub setting a repo's
administrator sets by hand. Nothing here is enforced; every rule is in
its Standard.

## Candidates

A repo's `CANDIDATES.md` is the register of the future work it has not
committed to. Committed work lives in GitHub issues; a **Candidate** is
work described but not yet decided, and a unit of work has one home,
never both. The file is optional, one per repo, at the root
([Root-only files](/standards/build/skeleton.md#root-only-files)); its
absence means nothing has been recorded yet. It carries `Candidate-List`
frontmatter and an index entry like any concept document
([Document Types](/standards/knowledge-organization/document-types.md)).
No `ROADMAP.md`, `TODO.md`, `BACKLOG.md`, or `IDEAS.md` exists anywhere
in the tree
([No other future-work file](/standards/build/skeleton.md#no-other-future-work-file)).

Every entry is work the repo would implement once the decision is made,
and that decision has not been made. Commitment is a decision, not a
capability: an entry may be perfectly specifiable and stay a Candidate
for as long as nobody has chosen to build it, and deciding to write its
brief is what ends that. The author makes this call; no detector checks
it. A Candidate is serious and repo-scoped: not the unfiltered,
cross-repo ideas that belong in mission-control's capture path, and never
material that is not work at all. Once committed, the work belongs in an
issue at whatever size fits — an epic, an ordinary issue, or a one-line
bug.

### Entry shape

An entry is one list item — a bolded short name, an em dash, then one or
two sentences of intent — and carries no fields, no acceptance criteria,
and no checkboxes.

```markdown
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.
```

The bolded name is the entry's handle: what promotion is pointed at, and
what gets deleted when it lands. The prose says what the work is, never
how to do it, since an approach decided this early goes stale before the
work starts. Brief furniture on a Candidate is the signal that the brief
could be written, and therefore that the work belongs in an issue.

### Structure

A `##` heading groups entries and carries no other meaning; nesting
decomposes, a parent being an outcome and its children the work that
achieves it, to any depth; and order carries no meaning in either
dimension. Headings are navigational only, free to invent. Since order is
meaningless, every merge conflict in this file resolves by keeping both
sides. A register in full:

```markdown
---
type: Candidate-List
title: Candidates
description: Uncommitted future work — described, not yet promoted to issues
---

# Candidates

## Export

- **Scheduled exports** — a user picks a cadence and the report reaches their
  inbox without them opening the app.
  - **Cadence picker** — daily, weekly, or monthly, with the timezone taken
    from the user's profile.
  - **Delivery retry** — a bounced send is retried before the run is marked
    failed.
- **Column selection** — the export is all-or-nothing today; users want to
  choose which columns ship.

## Search

- **Fuzzy matching** — matching is exact-prefix only, so a typo returns
  nothing.
```

### Promotion

An entry whose issue has been authored is deleted in the same change, so
the work never sits in both homes; a parent promotes with its whole
subtree as one issue, never as an issue per child. Intake does not slice,
so the subtree's decomposition is deferred to the `design` node like any
other multi-issue plan. Deleting an entry without promoting it is
ordinary editing: a Candidate that no longer appeals is removed, and
nothing records that it was once considered.

## Roles

Every issue is a **leaf**, an issue with no sub-issues, or an **epic**,
an issue with sub-issues; the role is read from the tracker and is never
a label. An epic is never built directly: its children carry the work.

## Relationships

Hierarchy and dependency are native GitHub relationships, never body
fields and never labels: a **sub-issue** is part of its parent, and an
issue **blocked-by** another waits for it to close. The two are
independent, so a parent says nothing about order and a blocker nothing
about parentage, and *blocked* is derived from open blockers, never a
label. Neither relationship has a `gh` subcommand;
[Linking Issues](/standards/tracking/linking-issues.md) holds the
`gh api` calls.

## The five species

An issue is one of five species, told from its labels and its sub-issues.

- **Build leaf.** A leaf carrying `mode:direct`: the software factory's
  path, an issue that ends in merged code
  ([Build leaf](/standards/tracking/issue-shapes.md#build-leaf)). Its
  `User intent` heading holds the user's words and never an agent's
  paraphrase; one epic-level block copied into every child is the defect.
  `Prohibited surfaces` names only the paths whose touching is a real
  hazard. A brief whose deliverables include prose may carry it verbatim
  in a `## Artifacts` section, each block in a code fence, four backticks
  when the content has fences of its own; the section binds when present
  and is never required.
- **Spike.** A leaf carrying `mode:spike`: a question whose deliverable
  is an answer in the issue's closing comment; no PR opens
  ([Spike](/standards/tracking/issue-shapes.md#spike)).
- **Session leaf.** A leaf carrying `mode:session`: work the user leads
  in a session, in a worktree, with a pull request opened by hand;
  nothing dispatches it
  ([Session leaf](/standards/tracking/issue-shapes.md#session-leaf)). Its
  body is written once and stays the brief: the plan, the open questions,
  and the decisions of the work live in a
  [working documentation set](/standards/knowledge-organization/documentation-sets/working-documentation-sets.md)
  on the branch. `Out of scope` may read "Unknown; dealt with when
  found."
- **Epic.** An issue with sub-issues and no `wayfinder:*` label
  ([Epic](/standards/tracking/issue-shapes.md#epic)). `Out of scope` and
  `Standing rulings` are added only when the epic accrues one, and
  `Standing rulings` is appended to, never renumbered.
- **Wayfinder map or ticket.** An issue carrying a `wayfinder:*` label: a
  **map**, the planning epic the `/wayfinder` skill drives, or a
  **decision ticket**, one of its children
  ([Wayfinder map or ticket](/standards/tracking/issue-shapes.md#wayfinder-map-or-ticket)).
  The skill owns the body shapes; the Standard and workspace-lint mirror
  them.

## What the labels mean

The scheme is closed-world: which labels exist is fixed as data in
`src/dev_playbook/label_scheme.json`,
[bootstrap-labels](/scripts/bootstrap-labels) mints that data into a
repo, and [labelgen](/scripts/labelgen) renders it as the table in
[Label Scheme](/standards/tracking/label-scheme.md). The `phase:*` values
are the software factory's states
([the graph](/software-factory/software-factory.md#the-graph)); the
`wayfinder:*` values are the `/wayfinder` skill's ticket types. No label
names a blocked state, because blocked is derived from an issue's open
blockers ([Relationships](#relationships)) and a minted label would drift
from the truth the tracker already holds.

## Why the repository settings are what they are

The merge settings and the rulesets both sit behind GitHub's
all-or-nothing **Administration** permission, too broad to grant for a
one-time toggle, so they are set by hand and only audited: workspace-lint
reads them over `gh api` and reports drift, and no repair tool exists. No
agent changes them.

### Squash-only merges

One pull request lands as one commit on `main`, its message from the PR
title and body, and the merged branch is deleted
([Squash-only merges](/standards/tracking/repo-settings.md#squash-only-merges)).
The settings live in **Settings → General → Pull Requests**. The
branch's own commits do not survive the squash, so what the branch
settled survives only in the tree it merges or in its message; a decision
that is expensive to reverse and that the merged tree does not explain is
proposed as a Decision Record in the pull request body
([Pull requests](/software-factory/factory-operations.md#pull-requests)).

### Default branch protection

The default branch carries two destructive-operation rules, force pushes
blocked and deletions restricted, from a ruleset named `protect-main`
with enforcement Active and an empty bypass list
([Default branch protection](/standards/tracking/repo-settings.md#default-branch-protection)).

| Rule | Denies |
|---|---|
| Block force pushes | rewriting history under the branch |
| Restrict deletions | removing the branch |

Together these make the branch's history append-only: every commit that
reaches `main` stays reachable, so a mistaken push cannot erase reviewed
work and no recovery depends on someone's local reflog.

Create it at **Settings → Rules → Rulesets → New ruleset → New branch
ruleset**. Every field:

| Field | Value |
|---|---|
| Ruleset Name | `protect-main` |
| Enforcement status | Active |
| Bypass list | empty |
| Target branches | Include default branch |
| Restrict deletions | checked |
| Block force pushes | checked |

Nothing is added to the bypass list — a bypass actor would return the
destructive operations to whoever holds it, which is the one thing this
ruleset exists to deny. Extra rules and extra rulesets are fine; the two
destructive-operation rules are a floor. The audit reads the rules in
force on the default branch, so a ruleset that is inactive or aimed
elsewhere supplies no rule and fails the check by its absence.

This is deliberately not branch protection with required status
checks: nothing here makes CI a merge precondition.
