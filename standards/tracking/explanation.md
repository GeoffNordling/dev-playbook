---
type: Explanation
title: Tracking Explanation
description: The thinking behind the tracking rules — what a Candidate is and how it becomes an issue, the roles and relationships an issue has, the five species, what the labels mean, and why the repository settings are what they are
---

# Tracking Explanation

The reasoning behind the tracking rulesets,
[Candidates](/standards/tracking/candidates.md),
[Issue Shapes](/standards/tracking/issue-shapes.md),
[Label Scheme](/standards/tracking/label-scheme.md), and
[Repository Settings](/standards/tracking/repo-settings.md): the
vocabulary, the reasons, and the examples, and the GitHub settings a
repo's administrator sets by hand.

## Candidates

A Candidate is work described but not yet decided
([Candidates](/standards/tracking/candidates.md)). Commitment is a
decision, not a capability: an entry may be perfectly specifiable and
stay a Candidate for as long as nobody has chosen to build it, and
deciding to write its brief is what ends that. The author makes this
call; no detector checks it. A Candidate is serious and repo-scoped: not
the unfiltered, cross-repo ideas that belong in mission-control's
capture path, and never material that is not work at all. Once
committed, the work belongs in an issue at whatever size fits, an epic,
an ordinary issue, or a one-line bug.

The bolded name is the entry's handle: what promotion is pointed at, and
what gets deleted when it lands. The prose says what the work is, never
how to do it, since an approach decided this early goes stale before the
work starts. Brief furniture on a Candidate is the signal that the brief
could be written, and therefore that the work belongs in an issue
([Entry shape](/standards/tracking/candidates.md#entry-shape)).

Headings are navigational only, free to invent, and order carries no
meaning in either dimension, so every merge conflict in this file
resolves by keeping both sides
([Structure](/standards/tracking/candidates.md#structure)).

Promotion is the change that authors an issue from an entry and
deletes the entry, so the work never sits in both homes
([One home](/standards/tracking/candidates.md#one-home)); a parent
promotes with its whole subtree as one issue, never as an issue per
child, since intake does not slice. Deleting an entry without promoting
it is ordinary editing: a Candidate that no longer appeals is removed,
and nothing records that it was once considered.

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
[Linking Issues](/guides/linking-issues.md) holds the
`gh api` calls.

## The five species

An issue is one of five species, told from its labels and its sub-issues.

- **Build leaf.** A leaf carrying `mode:direct`: the software factory's
  path, an issue that ends in merged code
  ([Build leaf](/standards/tracking/issue-shapes.md#build-leaf)). Its
  `User intent` heading holds the user's words and never an agent's
  paraphrase; one epic-level block copied into every child is the defect.
  A brief whose deliverables include prose carries it verbatim in an
  `Artifacts` section
  ([Artifacts](/standards/tracking/issue-shapes.md#artifacts)), so the
  landed text is compared against the brief's.
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
are the software factory's states, the factory being isolated under
`working-docs/software-factory/`; the `wayfinder:*` values are the `/wayfinder` skill's ticket types. No label
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
proposed as a Decision Record in the pull request body.

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
ruleset**, with the fields the rule's table names.

Nothing is added to the bypass list — a bypass actor would return the
destructive operations to whoever holds it, which is the one thing this
ruleset exists to deny. Extra rules and extra rulesets are fine; the two
destructive-operation rules are a floor. The audit reads the rules in
force on the default branch, so a ruleset that is inactive or aimed
elsewhere supplies no rule and fails the check by its absence.

This is deliberately not branch protection with required status
checks: nothing here makes CI a merge precondition.
