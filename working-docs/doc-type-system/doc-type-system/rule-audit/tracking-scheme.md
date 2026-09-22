---
type: General-Sheet
title: Candidates, Label Scheme, and Repo Settings Rule Audit
description: The rule audit over the tracking/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Candidates, Label Scheme, and Repo Settings Rule Audit

Three of the four Standards in the `tracking/` family are audited here:
[Candidates](/standards/tracking/candidates.md),
[Label Scheme](/standards/tracking/label-scheme.md), and
[Repository Settings](/guides/repo-settings.md). They hold
seven rules between them. No reclassification is proposed in either
direction: every trailer already carries the kind its predicate earns.
Three rules break. All three breaks sit in repos other than the one that
declares the rule, which is the pattern of this family: its population is
the governed roster and its one detector, `scripts/workspace-lint`, is
ungated and cannot run at all today. `tracking.entry-shape` is false of
almost every entry in story-forge's `CANDIDATES.md` and of one entry in
dev-playbook's own; `tracking.structure` is false of sounds'
`CANDIDATES.md`, whose single entry sits under no `##` heading; and
`tracking.valid-labels` is false of lunch, which is missing `mode:session`
and carries seventeen labels whose descriptions predate the scheme data. No
rule is weakly checked: the four rules with a verifier row are each tested
in full, and the three Candidates rules are checked by nothing at all. No
rule is low value.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `tracking.one-home` | "A unit of work is a Candidate or an issue, never both." | stochastic | stochastic | none | holds | none | high | Deciding sameness of two work descriptions is a judgment, and the issue side is not a repo file. Checked by hand: 73 entries across four `CANDIDATES.md` files against 21 open issues in the same four repos; no pair names one unit of work. |
| `tracking.entry-shape` | "An entry is one list item: a bolded short name, an em dash, then one or two sentences of intent, with no fields, no acceptance criteria, and no checkboxes." | deterministic | deterministic | none | breaks | none | high | Test over `CANDIDATES.md`: each list item starts `**…**`, the next character run is `—`, the item holds at most two sentences and no `- [ ]`. The clauses "of intent" and "no acceptance criteria" judge meaning and need rewording. See Escalations. |
| `tracking.structure` | "Every entry sits under a `##` heading, directly or nested under a parent entry; a heading groups its entries and carries no other meaning, and a nested entry is work that achieves its parent's outcome." | stochastic | stochastic | none | breaks | none | high | The first clause is mechanical, but "achieves its parent's outcome" is a judgment, so the rule as written stays stochastic. The mechanical clause is false of `sounds/CANDIDATES.md:9`. See Escalations. |
| `tracking.valid-labels` | "A governed repo's GitHub labels are exactly the labels declared in the scheme data `src/dev_playbook/label_scheme.json`, each carrying the color and the description that data gives it." | deterministic | deterministic | full | breaks | none | high | `check_labels` compares name, color, and description both ways against `canonical_labels()`. The repo's labels are not a repo file, but `gh api repos/<slug>/labels` returns one value with no judgment. False of lunch. See Escalations. |
| `tracking.github-origin` | "A governed repo's `origin` remote is a repository on github.com." | deterministic | deterministic | full | holds | none | high | `origin_slug` reads `git remote get-url origin` and matches `REMOTE_SLUG_PATTERN`; `check_settings` emits the id when it returns None. All eight governed repos present under `~/workspace` carry a `https://github.com/GeoffNordling/<name>.git` origin. |
| `tracking.squash-only-merges` | "A governed repo's GitHub merge settings hold every row of this table:" | deterministic | deterministic | full | holds | none | high | `EXPECTED_SETTINGS` holds all five table rows as six GraphQL fields, the commit-message row splitting into `squashMergeCommitTitle` PR_TITLE and `squashMergeCommitMessage` PR_BODY. All ten governed repos answer every field as expected. |
| `tracking.default-branch-protection` | "A governed repo's default branch carries both destructive-operation rules in force: force pushes are blocked, and deletions are restricted." | deterministic | deterministic | full | holds | none | high | `check_protection` reads `defaultBranchRef.rules`, requires NON_FAST_FORWARD and DELETION, and judges each supplying ruleset for ACTIVE enforcement, an empty bypass list, and the name `protect-main`. All ten repos hold every clause. |

## Escalations

### `tracking.entry-shape` — An entry is one list item: a bolded short name, an em dash, then one or two sentences of intent, with no fields, no acceptance criteria, and no checkboxes

The predicate caps an entry at two sentences and requires an em dash after
the bolded name. The example block under it shows a two-line entry. The rule's own why
([Entry shape](/standards/tracking/candidates.md#entry-shape)) gives
the reason: brief furniture on a Candidate is the signal that the brief
could be written, so the work belongs in an issue and not in this file.

`story-forge/CANDIDATES.md` disobeys the predicate in three ways at once.

- **The separator is a hyphen, not an em dash.** Not one of the file's 38
  entries uses an em dash. 31 use ` - `, from
  `- **Problem-solver positioning** - position me not as a…` at line 11
  to `- **Pydantic drill** - the sheet exists…` at line 140. The repo bans
  the em dash repo-locally, and story-forge issue 14 records that it kept
  the ban against a workspace ruling to delete it.
- **Seven entries carry no separator at all.** Line 123,
  `- **Tell me your theory of agents** This is a question I would ask a
  candidate myself…`, and line 124,
  `- **Agentic Patterns and Anti-Patterns** Just like object-oriented
  programming in the 1990's…`, run the bolded name straight into prose.
  Five more, at lines 236, 250, 260, 290, and 309, put the period inside
  the bold and open a narrative section, as in
  `- **Autopsy, one agent per slice.** Three agents in parallel…`.
- **Entries run far past two sentences.** Line 14, "Pipeline status at a
  glance", holds five sentences. Line 123 holds six. Line 151, "Fit on
  paper versus readiness in the room", holds eleven and reads as a brief.
  Line 198, "Tapless factory epic 341 abandonment and restart", opens a
  narrative that runs to line 349, with nested sub-entries whose bodies
  are multi-paragraph and two closing paragraphs that belong to no entry
  at all.

dev-playbook's own file breaks the sentence cap once.
`CANDIDATES.md:52`, "The parser's trigger", holds three sentences: the
chain-parser sentence ending at line 55, the runbook-shadowing sentence
ending at line 58, and "Hierarchical imports across repositories are the
mechanism under both." at lines 58 to 59.

**Proposal.** Change the repos, not the predicate. The cap is the one
thing that keeps a Candidate from becoming an unreviewed brief, the
explanation argues for it at length, and dev-playbook's own file obeys it
in 30 of 31 entries, so story-forge's drift is an unpoliced oversight and
not a deliberate local rule. The files that change are
`story-forge/CANDIDATES.md`, whose over-long entries are trimmed to their
intent and whose `## Story seeds` section moves out of the file entirely,
since remembered material is not work and the explanation excludes it, and
`dev-playbook/CANDIDATES.md:52`, whose third sentence is cut or split off
as a second entry. The hyphen clause is the exception: it is already under
an open deviation in story-forge issue 14 and should be settled there
rather than by rewriting this predicate. Separately, the predicate's two
judgment clauses, "sentences of intent" and "no acceptance criteria",
block a detector and should be reworded as form, for example "no bolded
field label and no `- [ ]` checkbox".

### `tracking.structure` — Every entry sits under a `##` heading, directly or nested under a parent entry

The predicate's first clause puts every entry under a `##` heading.
`sounds/CANDIDATES.md` holds one entry, `- **Apex Legends sound
effects** — the rotation is drawn from a fixed set of game clips…` at
line 9, and the file carries no `##` heading anywhere: the entry sits
directly under the `# Candidates` title at line 7. The other three files
obey the clause. dev-playbook uses five headings, sysadmin-playbook one,
and story-forge four.

**Proposal.** Change the repo. The cost is one line in one file: add a
`## Sound effects` heading above line 9 of `sounds/CANDIDATES.md`. The
explanation says headings are navigational only and free to invent, so
naming one costs the author nothing and no meaning is asserted by it. The
alternative, relaxing the predicate so a file with one entry may skip the
heading, buys a special case into a rule whose value is that it has none.

### `tracking.valid-labels` — A governed repo's GitHub labels are exactly the labels declared in the scheme data `src/dev_playbook/label_scheme.json`, each carrying the color and the description that data gives it

The scheme data declares 18 labels across six dimensions. Nine of the ten
governed repos carry all 18 at full parity, name, color, and description.
The lunch repo does not.

- `mode:session` is absent. The scheme declares it with the description
  "Led by the user in a session: worked in a worktree, PR opened by hand,
  never dispatched."
- All 17 labels lunch does carry hold a placeholder description rather
  than the scheme's sentence. For example `category:maintenance` reads
  "Category: maintenance." where the scheme gives "Maintains shipped
  state: a fix, hygiene, or polish that adds no capability."

The detector would report each of these 18 findings, but it never runs.
`workspace_repos` in `src/dev_playbook/workspace_lint.py` raises
`ToolError` when a repo on the `GOVERNED` roster has no `.git` under the
workspace root, and `main` turns that into exit 2 and prints nothing
else. Neither `lunch` nor `date-tree` is checked out under
`~/workspace` on this machine, although both exist on github.com, so
`workspace-lint` refuses to start and has been reporting nothing about
any governed repo.

**Proposal.** Change the repo. The scheme is closed-world and
`scripts/bootstrap-labels` mints it, so the repair is one run of that
script against lunch; the drift is plainly an oversight, because lunch was
minted before the descriptions moved into
`src/dev_playbook/label_scheme.json` and every other governed repo is at
full parity. Rewriting the predicate to tolerate a placeholder description
would end the closed world, which is the only thing that lets
bootstrap-labels, workspace-lint, and labelgen read one authority. Cloning
lunch and date-tree under `~/workspace` is a separate matter, but until it
happens no repair is visible to the audit.

## Detectors

**`scripts/workspace-lint`** is a thin shim over
`src/dev_playbook/workspace_lint.py` and is the only detector any rule in
these three Standards names. It is registered `on-demand` in
`standards/boundaries.yaml`, so no gate runs it. For each repo on the
`GOVERNED` roster it reads the merge settings over one GraphQL query and
compares them field by field against `EXPECTED_SETTINGS`
(`tracking.squash-only-merges`), reads `defaultBranchRef.rules` over a
second query and requires NON_FAST_FORWARD and DELETION plus an active,
bypass-free, `protect-main`-named ruleset behind them
(`tracking.default-branch-protection`), emits a finding when
`git remote get-url origin` yields no github.com slug
(`tracking.github-origin`), and compares the repo's labels against
`canonical_labels()` at full parity in both directions
(`tracking.valid-labels`). It reads GitHub only; it never writes. Two
facts limit it today: it cannot start at all while a governed repo is
missing from `~/workspace`, and dev-playbook issues 469 and 470 record
further known drift between it, the standard, and how these settings are
really applied.

**`src/dev_playbook/label_scheme.py`** is the authority behind
`tracking.valid-labels` rather than a detector. It parses
`label_scheme.json` into dimensions, refuses any description longer than
GitHub's 100-character limit, and exposes `canonical_labels()`, the
`(name, color, description)` triple set that workspace-lint compares a
repo against and that `scripts/bootstrap-labels` mints.

**`scripts/labelgen`** renders the same data as the table between the
`labelgen:start` and `labelgen:end` markers in
`standards/tracking/label-scheme.md`, and `--check` exits 1 on drift. I
confirmed by hand that the table's 18 rows match the data. The script is
in no rule's verifier row and in no gate of `standards/boundaries.yaml`,
so nothing fails when that table and the data disagree: no rule in this
family states that the rendered table matches the scheme.

**No detector exists for `standards/tracking/candidates.md`.** All three
of its rule ids, `tracking.one-home`, `tracking.entry-shape`, and
`tracking.structure`, are null in `standards/verifiers.yaml`. Two of the
family's three breaks are in that unchecked Standard, and both are
mechanical enough for a lint over `CANDIDATES.md`.
