---
type: General-Sheet
title: Issue Shapes Rule Audit
description: The rule audit over the tracking/ family's Issue Shapes — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Issue Shapes Rule Audit

[Issue Shapes](/standards/tracking/issue-shapes.md) holds twenty-six
rules: five of them are conditions, the H2 species tests that the H3
rules sit under, and twenty-one are predicates. One reclassification is
proposed, `tracking.artifacts` from deterministic to stochastic, and
none in the other direction. Eleven rules break, two are weakly checked,
and two are low value. Every break sits in a closed issue, because the
population is "a GitHub issue in a governed repo" and that class holds
295 closed dev-playbook issues against 24 open ones across the roster —
so the Standard binds a decade of history that nobody will amend, while
`scripts/workspace-lint` reads open issues only. Narrowing the population
to an open issue turns eight of the eleven breaks into holds; it also
exposes how little the family bites today, since 23 of the 24 open issues
carry no `mode:*` and no `wayfinder:*` label and match none of the five
species. The three breaks that survive the narrowing are authoring rules
over bodies written in stages: `tracking.user-intent` and
`tracking.written-for-the-user` are false of a brief still at
`phase:design`, and `tracking.behavioural-not-procedural` is false of
every brief that carries the verbatim amendment text `tracking.artifacts`
asks for. One live form drift runs under the heading rules: five of the
eleven most recent post-intake build leaves carry no `Prohibited
surfaces` heading, and the most recent session leaf writes its six
sections as `##` headings rather than bold ones. Kind is judged here as
the rest of the family judges it — one value, no judgment call, from a
member read over `gh api` — since this population is not a file in the
repo and `tracking.valid-labels` and `tracking.squash-only-merges`
already carry `deterministic` on that basis.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tracking.written-for-the-user` | "An issue's body is readable unaided by a user who sees only the issue and never the author's context, and a reference to existing file content quotes verbatim the text it amends." | stochastic | stochastic | none | breaks | none | high | Readability for an unaided reader is a judgment. False of dev-playbook#444, whose `Desired behavior` states the requirement only as "Per" three other issues' resolutions. See Escalations. |
| `tracking.behavioural-not-procedural` | "The body of an issue that carries `mode:direct` or `mode:session` describes what the system does after the work, as interfaces and behavioural contracts, never the steps that get there." | stochastic | stochastic | none | breaks | none | high | Telling a contract from a step is a judgment. False of dev-playbook#400, whose `## Artifacts` is a numbered list of edits with before-and-after text. See Escalations. |
| `tracking.one-goal` | "An issue that carries `mode:direct` or `mode:session` serves one outcome, and every part that could slip indefinitely with the outcome still standing, and could ship later as its own issue without reopening this one, is named under the issue's `Out of scope` heading and carried by a separate issue that carries `phase:intake`." | stochastic | stochastic | none | breaks | none | high | The last clause compares one member against another, which `doc-type.decidable-predicates` forbids. False of dev-playbook#452, whose `Out of scope` parts were "ruled not worth tracking". See Escalations. |
| `tracking.user-intent` | "Where an issue's body carries a `User intent` heading, what stands under it is the user's own words for this issue, never an agent's paraphrase." | stochastic | stochastic | none | breaks | none | high | Whose words these are is not in the repo. Of 19 dev-playbook issues carrying the heading, #443 and #444 read "NA - to be discussed with user during /design". See Escalations. |
| `tracking.closed-fences` | "A leaf that carries `mode:session`, or a leaf that carries a `phase:*` label other than `phase:intake`, closes every code fence its body opens." | deterministic | deterministic | weak | holds | none | high | `md.lines_outside_fences` decides it. Unchecked where the leaf's `mode:*` label is missing, doubled, or off-scheme. All 319 dev-playbook bodies parse. See Escalations. |
| `tracking.build-leaf` | "The issue has no sub-issues and carries `mode:direct`." | deterministic | deterministic | none | holds | none | high | A condition, not a falsifiable predicate: `sub_issues_summary.total` and the label set decide it. `check_issues` routes on exactly this test but emits no id for it. |
| `tracking.build-labels` | "A build leaf that carries a `phase:*` label other than `phase:intake` carries exactly one label from each of `category`, `mode`, `tests`, and `phase`, and each of those labels is a value of the label scheme." | deterministic | deterministic | full | breaks | `tracking.spike-labels` | high | `_tuple_findings` tests one value per dimension against `values_by_dimension()`. False of 25 closed leaves with no `category:*` label, all numbered below #201, such as dev-playbook#200. See Escalations. |
| `tracking.build-headings` | "A build leaf that carries a `phase:*` label other than `phase:intake` carries every heading below in its body, each as a bold heading; a heading shown inside a code fence is quoted, not carried." | deterministic | deterministic | full | breaks | none | high | `_heading_findings` tests the eight headings outside fences. False of 61 of 66 closed post-intake build leaves; five of the most recent eleven miss only `Prohibited surfaces`. See Escalations. |
| `tracking.prohibited-surfaces` | "A build leaf's `Prohibited surfaces` names only the paths whose touching is a real hazard." | stochastic | stochastic | none | holds | none | low | Whether a path is a real hazard is a judgment. The sampled entries name real ones, such as dev-playbook#444's `dotfiles/dot-claude/skills/frozen-*`. Binds the taste of one optional list. |
| `tracking.artifacts` | "Where a build leaf's body carries an `Artifacts` section, each block under it sits in a code fence, four backticks when the block has fences of its own." | deterministic | stochastic | none | unknown | none | high | "Block" is undefined, so which prose under the heading must be fenced is a judgment: #452 fences its clause, #383 quotes with `>`. The four-backtick clause alone is deterministic. |
| `tracking.spike` | "The issue has no sub-issues and carries `mode:spike`." | deterministic | deterministic | none | holds | none | high | A condition, not a falsifiable predicate: `sub_issues_summary.total` and the label set decide it. `check_issues` routes on exactly this test but emits no id for it. |
| `tracking.spike-labels` | "A spike that carries a `phase:*` label other than `phase:intake` carries exactly one label from each of `category`, `mode`, `tests`, and `phase`, each of those labels is a value of the label scheme, and its `tests:*` label is `tests:no`." | deterministic | deterministic | full | holds | `tracking.build-labels` | high | `_tuple_findings` tests the four-tuple and the `tests:no` pairing. All 11 closed dev-playbook spikes hold. States build-labels' clause plus one over a disjoint subset; neither subsumes. |
| `tracking.spike-headings` | "A spike that carries a `phase:*` label other than `phase:intake` carries `Summary`, `Question`, and `Deliverable` in its body, each as a bold heading; a heading shown inside a code fence is quoted, not carried." | deterministic | deterministic | full | holds | none | high | `_heading_findings` tests the three headings outside fences. All 11 closed dev-playbook spikes, #258 through #270, carry all three as bold headings. |
| `tracking.session-leaf` | "The issue has no sub-issues and carries `mode:session`." | deterministic | deterministic | none | holds | none | high | A condition, not a falsifiable predicate: `sub_issues_summary.total` and the label set decide it. `check_issues` routes on exactly this test but emits no id for it. |
| `tracking.session-labels` | "A session leaf carries exactly one `category:*` label, a value of the label scheme, and carries no `mode:*` label other than `mode:session`, no `tests:*` label, and no `phase:*` label." | deterministic | deterministic | full | holds | none | high | `_session_findings` tests each clause. Both closed session leaves, dev-playbook#474 and #478, carry `category:extension` and `mode:session` and nothing else. |
| `tracking.session-headings` | "A session leaf carries `Summary`, `User intent`, `Current behavior`, `Desired behavior`, `Acceptance criteria`, and `Out of scope` in its body, each as a bold heading; a heading shown inside a code fence is quoted, not carried." | deterministic | deterministic | full | breaks | `tracking.build-headings` | high | `_heading_findings` tests the six headings outside fences. False of dev-playbook#478, which writes all six as `##` headings. Its six are build-headings' eight less two, over a disjoint subset. See Escalations. |
| `tracking.a-stable-body` | "A session leaf's body holds no worklist, no open question, and no running decision." | stochastic | stochastic | none | holds | none | high | Telling a criterion from a worklist is a judgment. Both closed session leaves hold: #474 and #478 state a summary, an intent, two behaviors, criteria, and scope, and no running record. |
| `tracking.epic` | "The issue has sub-issues and carries no `wayfinder:*` label." | deterministic | deterministic | none | holds | none | high | A condition, not a falsifiable predicate: `sub_issues_summary.total` and the label set decide it. `check_issues` routes on exactly this test but emits no id for it. |
| `tracking.category-only` | "An epic carries exactly one `category:*` label, a value of the label scheme, and carries no `phase:*`, `mode:*`, or `tests:*` label." | deterministic | deterministic | full | breaks | none | high | `_epic_findings` tests each clause. False of dev-playbook#142, an epic with 13 sub-issues and no label at all. The other nine closed epics hold. See Escalations. |
| `tracking.epic-headings` | "An epic carries `Outcome` and `Decomposition rationale` in its body, each as a bold heading." | deterministic | deterministic | none | breaks | none | high | The verifier row is null, though `_heading_findings` already tests exactly this shape for leaves. False of dev-playbook#293, which carries neither, and #341, which writes both as `##`. See Escalations. |
| `tracking.no-child-list` | "An epic's body does not list its sub-issues." | stochastic | stochastic | none | breaks | none | high | Sub-issue numbers are machine-readable, but a listing and a prose mention are not: #437 names #438 and #443 in prose. False of #293's `## Chunk index` table. See Escalations. |
| `tracking.standing-rulings` | "Where an epic's body carries a `Standing rulings` heading, the rulings under it are a numbered list." | deterministic | deterministic | none | holds | none | low | Test: the first block after the heading is an ordered list. Holds on #437, #256, and #378, the three epics that carry the heading. Binds the formatting of one optional section. |
| `tracking.wayfinder-map-or-ticket` | "The issue carries a `wayfinder:*` label: `wayfinder:map` makes it a **map**, and any other `wayfinder:*` value makes it a **decision ticket**." | deterministic | deterministic | none | holds | none | high | A condition, not a falsifiable predicate: the label set decides it. `check_issues` routes on exactly this test but emits no id for it. |
| `tracking.wayfinder-labels` | "A map carries `wayfinder:map` and no other `wayfinder:*` value; a decision ticket carries exactly one `wayfinder:*` value, a value of the label scheme; and neither carries a `category:*`, `mode:*`, `tests:*`, or `phase:*` label." | deterministic | deterministic | full | holds | none | high | `_map_findings` and `_ticket_findings` test each clause against `_factory_labels`. All four closed maps and all 52 closed tickets hold. |
| `tracking.wayfinder-body` | "A map's body carries a `Destination`, a `Notes`, a `Decisions so far`, a `Not yet specified`, and an `Out of scope` section, and a decision ticket's body carries a `Question` section, each as a markdown heading at any level." | deterministic | deterministic | weak | breaks | none | high | `_has_section` scans the raw body, so a section quoted in a fence counts. False of dev-playbook#374, a `wayfinder:research` ticket with no `Question`. See Escalations. |
| `tracking.ticket-parentage` | "A decision ticket is a sub-issue of a map." | deterministic | deterministic | none | holds | none | high | Test: the ticket's `parent_issue_url` resolves to an issue carrying `wayfinder:map`. All 52 closed dev-playbook tickets hold. The verifier row is null although the field is one read away. |

## Escalations

### `tracking.written-for-the-user` — An issue's body is readable unaided by a user who sees only the issue and never the author's context

The predicate asks that a body stand alone for a reader who never saw the
author's context. dev-playbook#444's `Desired behavior` states its whole
requirement by reference: "Per the [Factory manager resolution](#432), the
[Merge-boundary light pass resolution](#435) §7–8, and the [Fact-base
refresh resolution](#433) Part III (provenance)". A reader of #444 alone
learns the shape of the work from no sentence in #444. The same brief's
`Acceptance criteria` opens "Provisional — the design session
re-authors", which says the body is a draft rather than a brief.

**Proposal.** Rewrite the predicate so it binds the moment the body is
finished, which is what the repo does on purpose: a brief at
`phase:design` is a draft the design session re-authors, and #444 was
closed at `phase:design`. The new sentence: "The body of an issue that
carries a `phase:*` label past `phase:design`, or that carries
`mode:session`, is readable unaided by a user who sees only the issue and
never the author's context, and a reference to existing file content
quotes verbatim the text it amends."

### `tracking.behavioural-not-procedural` — The body of an issue that carries `mode:direct` or `mode:session` describes what the system does after the work

The predicate bans steps from the body. `tracking.artifacts`, four rules
below it, requires the opposite of one section: a build leaf whose
deliverable is prose carries that prose verbatim, and in practice it
carries the edit with it. dev-playbook#400's `## Artifacts` reads "### 1.
Two edits to `/software-factory/user-checkpoints.md`", then "**1a.**
Frontmatter `description` (line 4). Before: … After: …". dev-playbook#452
opens its artifact with "Appended as the fourth bullet of § Mechanics,
after 'Report state, not next steps'". Both are steps, both were merged,
and the Tracking Explanation endorses the form: "A brief whose
deliverables include prose carries it verbatim in an `Artifacts` section
… so the landed text is compared against the brief's".

**Proposal.** Rewrite the predicate to exempt the section the other rule
mandates. The new sentence: "Outside its `Artifacts` section, the body of
an issue that carries `mode:direct` or `mode:session` describes what the
system does after the work, as interfaces and behavioural contracts,
never the steps that get there." The repo change is not the way out here:
placement notes beside verbatim amendment text are the factory's working
form, not an oversight.

### `tracking.one-goal` — An issue that carries `mode:direct` or `mode:session` serves one outcome

The predicate's last clause asks that each part named under `Out of
scope` be "carried by a separate issue that carries `phase:intake`".
dev-playbook#452's `Out of scope` names five parts, and its first reads
"Every other finding deferred at PR #450's `## Deferred` section. Some
are owned by named epic slices; the rest were ruled not worth tracking."
Work ruled not worth tracking is carried by no issue. The clause also
asks a question about a second member, which
`doc-type.decidable-predicates` forbids: "Each rule's predicate is true
or false of one member of the population at one moment, with no
comparison to another member".

**Proposal.** Rewrite by dropping the last clause. The new sentence: "An
issue that carries `mode:direct` or `mode:session` serves one outcome,
and every part that could slip indefinitely with the outcome still
standing, and could ship later as its own issue without reopening this
one, is named under the issue's `Out of scope` heading." Dropping work is
a decision the repo makes on purpose, and the remaining clauses still
hold the brief to one outcome.

### `tracking.user-intent` — Where an issue's body carries a `User intent` heading, what stands under it is the user's own words

Nineteen dev-playbook issues carry the heading. Seventeen hold a
paragraph in the user's voice, such as #474's "Agents work in loops and
the user works on the loops." Two, #443 and #444, read in full: "NA - to
be discussed with user during /design". A placeholder is neither the
user's words nor an agent's paraphrase, so the predicate is false of
both. Both issues were closed at `phase:design`, before the design
session that fills the heading in.

**Proposal.** Rewrite so the predicate binds after the stage that
authors the words, matching the sequence intake and design already run.
The new sentence: "Where an issue's body carries a `User intent` heading
and the issue carries a `phase:*` label past `phase:design`, what stands
under it is the user's own words for this issue, never an agent's
paraphrase." A repo change is the wrong way out: the placeholder is the
design session's own marker, not a defect.

### `tracking.closed-fences` — A leaf that carries `mode:session`, or a leaf that carries a `phase:*` label other than `phase:intake`, closes every code fence its body opens

`CLOSED_FENCES` is emitted from one place, `_heading_findings` in
`src/dev_playbook/workspace_lint.py:1089`, which parses the body and
catches `md.UnclosedFence`. Its only caller is `_brief_findings`
(line 1072), which returns an empty list before parsing anything when the
leaf's `mode:*` labels do not number exactly one (line 1075) and again
when the one value is not `direct`, `spike`, or `session` (line 1087). A
post-intake leaf with no `mode:*` label, with two, or with an off-scheme
one therefore has its fences unchecked, although the predicate binds it:
the predicate conditions on the phase label alone. The mislabelling draws
its own finding under `tracking.build-labels`, so the leaf is reported —
but not for the fence, and the unparsed body is what hides the rest of
its shape.

### `tracking.build-labels` — A build leaf that carries a `phase:*` label other than `phase:intake` carries exactly one label from each of `category`, `mode`, `tests`, and `phase`

Twenty-five closed dev-playbook build leaves carry `mode:*`, `tests:*`,
and `phase:*` but no `category:*` label: #44, #59, #84, #133, #144
through #155, and #163 through #200. Every one is numbered below #201,
which dates them before the `category` dimension entered the scheme. The
predicate is false of each of them today, because a closed issue is still
a member of "a GitHub issue in a governed repo".

**Proposal.** Rewrite the Standard's population to "an open GitHub issue
in a governed repo". The repo change — relabelling 25 closed issues —
buys nothing, and the rewrite states what the repo does on purpose:
`fetch_issues` in `workspace_lint.py:584` reads `state=open` and has
since the audit was written, so the open cut is already the one the
family enforces. The same rewrite settles the breaks under
`tracking.category-only`, `tracking.epic-headings`,
`tracking.no-child-list`, `tracking.session-headings`, and
`tracking.wayfinder-body`.

### `tracking.build-headings` — A build leaf that carries a `phase:*` label other than `phase:intake` carries every heading below in its body

Sixty-one of the 66 closed post-intake dev-playbook build leaves are
missing at least one of the eight headings. Fifty-six of those predate
the current list and miss several; the live pattern is the other five.
#452, #448, #440, #439, and #382 carry seven of the eight headings and
miss only `Prohibited surfaces`. Five of the eleven most recent
post-intake build leaves are in that set, and every one of them merged.

**Proposal.** Rewrite the heading block so `Prohibited surfaces` is
carried only where the issue has one, the way `Artifacts` and `Standing
rulings` already are. What makes the drift deliberate rather than an
oversight: `tracking.prohibited-surfaces` already says the section "names
only the paths whose touching is a real hazard", so a build leaf with no
hazard has nothing to write, and five recent briefs wrote nothing.
Pairing the rewrite with the population narrowing above clears the 56
historical breaks.

### `tracking.session-headings` — A session leaf carries `Summary`, `User intent`, `Current behavior`, `Desired behavior`, `Acceptance criteria`, and `Out of scope` in its body

Two session leaves exist in dev-playbook. #474 writes its six sections as
`**Summary:**` and the rest, which the predicate asks for. #478, the more
recent, writes them as `## Summary`, `## User intent`, `## Current
behavior`, `## Desired behavior`, `## Acceptance criteria`, and `## Out
of scope`. All six sections are there; none is a bold heading, so the
predicate is false of #478 and `_has_heading` reports six findings.

**Proposal.** Rewrite "each as a bold heading" to "each as a bold heading
or a markdown heading at any level", the form `tracking.wayfinder-body`
already accepts for a map and a ticket. The user authored #478 by hand
with `##` sections, which is a form choice rather than an omission, and
one family should not hold two heading forms to be right for a ticket and
wrong for a session leaf.

### `tracking.category-only` — An epic carries exactly one `category:*` label, a value of the label scheme

dev-playbook#142 has 13 sub-issues and carries no label at all, so the
"exactly one `category:*` label" clause is false of it. The other nine
closed epics — #220, #221, #231, #255, #256, #293, #341, #378, and #437 —
each carry exactly one in-scheme `category:*` and nothing from the other
three dimensions.

**Proposal.** Rewrite the Standard's population to an open issue, as
under `tracking.build-labels`. #142 is a closed epic from the same era as
the unlabelled build leaves, and labelling it now records nothing anyone
will read.

### `tracking.epic-headings` — An epic carries `Outcome` and `Decomposition rationale` in its body, each as a bold heading

Eight of the ten closed dev-playbook epics carry both as bold headings.
#341 carries both as `## Outcome` and `## Decomposition rationale`, the
same form drift as #478's. #293 carries neither: its body opens with `##
Instructions for the implementation agent` and `## Chunk index`. The
verifier row is null, although `_heading_findings` in
`workspace_lint.py:1089` already decides this exact shape for every leaf
species and `_epic_findings` (line 912) is the epic branch that would
call it.

**Proposal.** Rewrite the heading form as under `tracking.session-headings`,
accepting a markdown heading at any level, and narrow the population to
an open issue to clear #293. Wiring the rule to `scripts/workspace-lint`
is then a small addition to `_epic_findings`, which the design pass
should weigh separately.

### `tracking.no-child-list` — An epic's body does not list its sub-issues

dev-playbook#293's body carries a `## Chunk index` table whose rows are
`| 1 | Cleanup & truth pass | #294 | done |` and eight more. Six of the
nine rows name its actual sub-issues — #294, #296, #298, #303, #305, and
#307 — and each row carries a `Status` column the tracker already holds.
The rule exists to stop exactly that second copy from going stale. The
other nine epics hold: #437 names #438 and #443 in prose, inside
amendment notes, which is a mention rather than a listing.

**Proposal.** Rewrite the Standard's population to an open issue, as
under `tracking.build-labels`. #293 is closed and its table is now a
record of what happened; editing it would destroy that record, and the
predicate is what the repo wants of every epic it opens from here.

### `tracking.wayfinder-body` — A map's body carries a `Destination`, a `Notes`, a `Decisions so far`, a `Not yet specified`, and an `Out of scope` section

Two findings against this rule. The state: all four closed dev-playbook
maps — #322, #363, #403, and #424 — carry all five sections, and 51 of
the 52 decision tickets carry a `Question` section. The exception is
#374, a `wayfinder:research` ticket titled "Harvest: founding
conversation record of the mechanisms map", whose sections are `### What
happened`, `### The user's original concerns, in order raised`, and three
more. It asks no question because it records one, so the predicate is
false of it.

The check: `_has_section` in `workspace_lint.py:784` scans the raw body
rather than the lines outside fences, so a `## Question` quoted inside a
code fence satisfies the rule. Its own docstring says so — "a `##`
section quoted inside a fence forges one the map lacks" — and tracks the
gap at GeoffNordling/dev-playbook#386. The brief-shape rules do not share
the weakness: `_heading_findings` strips fences first.

**Proposal.** Rewrite the Standard's population to an open issue, as
under `tracking.build-labels`. #374 is closed, and a harvest ticket that
records a conversation is a shape the `/wayfinder` skill produced on
purpose; if the design pass keeps closed issues in the population, the
narrower way out is to state that a ticket carries a `Question` section
unless its `wayfinder:*` value is `research`.

## Detectors

**`scripts/workspace-lint`** is a thin shim over
`src/dev_playbook/workspace_lint.py` and is the only address any rule of
this Standard names. Its `check_issues` (line 1122) makes one
`gh api repos/<slug>/issues?state=open` read per governed repo and sorts
each issue into a species from its label set and `sub_issues_summary`,
in the order map, ticket, epic, session leaf, then post-intake leaf. Each
branch emits its own ids: `_map_findings` and `_ticket_findings` for
`tracking.wayfinder-labels` and `tracking.wayfinder-body`,
`_epic_findings` for `tracking.category-only`, `_session_findings` for
`tracking.session-labels`, `_tuple_findings` for `tracking.build-labels`
and `tracking.spike-labels`, and `_brief_findings` through
`_heading_findings` for the three heading rules and
`tracking.closed-fences`.

Three properties of the detector bound what any of that is worth. It runs
at no gate: `standards/boundaries.yaml` lists it as `[on-demand]`, alone
among the first-party scripts. It reads open issues only
(`fetch_issues`, line 584), so the 295 closed dev-playbook issues that
are members of this population are never checked. And it cannot run at
all today: `workspace_repos` (line 332) raises when a repo on the
`GOVERNED` roster is absent under `~/workspace`, and `lunch` and
`date-tree` are both absent, so the run exits 2 before the first read.

**`src/dev_playbook/md.py`** supplies the fence mechanics the heading
rules stand on. `lines_outside_fences` (line 114) nests fences by length,
which is what lets a four-backtick block wrap three-backtick content —
the form `tracking.artifacts` asks for — and raises `UnclosedFence` on a
block nothing closes, which is the only source of
`tracking.closed-fences`.

**`src/dev_playbook/label_scheme.py`** supplies `values_by_dimension()`,
the scheme values every label rule tests against, read from
`src/dev_playbook/label_scheme.json`. It is the same data
`tracking.valid-labels` holds a repo's tracker to, so a label rule here
and the scheme cannot disagree.

**`tests/dev_playbook/test_workspace_lint.py`** covers every branch
above, from `test_valid_leaf_tuple_and_brief_pass` (line 1172) through
`test_body_with_an_unclosed_fence_is_a_finding` (line 1566), including
the fence-stripping cases that keep a quoted template from forging a
heading. The tests match the code; where the code is weaker than the
predicate, the tests are weaker in the same place.

## Acronyms

- **H2** — markdown heading level two.
- **H3** — markdown heading level three.
- **PR** — pull request.
