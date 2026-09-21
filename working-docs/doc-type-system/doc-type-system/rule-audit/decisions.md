---
type: General-Sheet
title: Decisions Family Rule Audit
description: The rule audit over the decisions/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Decisions Family Rule Audit

The family holds fourteen rules, all in
[Decision Record Conventions](/standards/decisions/records.md). One
reclassification is proposed, `decisions.date` from deterministic to
stochastic, and none in the other direction. Six rules break:
`decisions.template`, `decisions.context-decision-and-reason`,
`decisions.immutable-after-merge`, `decisions.optional-sections`,
`decisions.external-convention-evaluation`, and
`decisions.what-was-examined`. No rule is weakly checked, because almost
nothing is checked at all: `scripts/decisions-lint` decides two rules in
full, `decisions.sequential-numbering` and `decisions.status-vocabulary`,
and the other twelve carry a null verifier row. Three rules are low
value: `decisions.slug-case`, which forbids a fault none of the
twenty-nine records commits; `decisions.template`, whose frontmatter
clause restates three knowledge-organization rules and whose own clause
is what breaks; and `decisions.optional-sections`, which twenty of the
twenty-nine records disobey and which
`decisions.immutable-after-merge` forbids anyone to repair.

| id | rule | kind | proposed | check | state | overlap | value | note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `decisions.the-bar` | "A Decision Record records a decision that is hard to reverse, surprising without its context, and the outcome of a real trade-off, all three at once: changing course later carries meaningful cost, a future reader looking at the code would wonder why it was done this way, and there were genuine alternatives with a specific reason for the choice." | stochastic | stochastic | none | holds | none | high | Each of the twenty-nine records carries a reversal cost and names alternatives. Nothing else states the bar that decides whether to open a record. |
| `decisions.scope` | "A Decision Record sits in the `docs/decisions/` of the repo it governs, and a decision that governs several repos sits in the repo that governs them." | stochastic | stochastic | none | holds | none | high | Every record here rules on dev-playbook or the whole workspace, which dev-playbook governs. Other repos' records are not visible from this repo. |
| `decisions.the-directory` | "The `docs/decisions/` directory holding a Decision Record holds numbered records, one `index.md`, and one `README.md`, and nothing else." | deterministic | deterministic | none | holds | `knowledge-organization.an-index-in-every-directory` | high | Test: list `docs/decisions/`, assert every name is `NNNN-slug.md`, `index.md`, or `README.md`. The directory holds 0001-0029 plus those two files. |
| `decisions.sequential-numbering` | "A Decision Record's filename is `NNNN-slug.md`, where `NNNN` is the record's number zero-padded to four digits." | deterministic | deterministic | full | holds | `decisions.slug-case` | high | `check_sequential_numbering` flags a number below 1, a prefix whose length is not 4, a duplicate, and each gap run (`src/dev_playbook/decisions_lint.py:108-164`). 0001-0029 are contiguous. |
| `decisions.slug-case` | "A Decision Record's slug, the part of its filename after `NNNN-` and before `.md`, is kebab-case." | deterministic | deterministic | none | holds | `decisions.sequential-numbering` | low | Test: match `^\d{4}-[a-z0-9]+(-[a-z0-9]+)*\.md$`. All twenty-nine slugs pass. Sequential-numbering already states the filename shape but not the slug's case. |
| `decisions.template` | "A Decision Record's frontmatter holds `type: Decision-Record`, a `title`, a `description`, and a `date`; its body opens with an H1 repeating the `title`, followed by one to three sentences:" | deterministic | deterministic | none | breaks | `knowledge-organization.types` | low | Twenty-one records miss the one-to-three-sentence opener: twelve open straight on `## Context`, nine run four to eleven sentences. See the escalation. |
| `decisions.context-decision-and-reason` | "A Decision Record's opening sentences give the context the decision was made in, the decision itself, and the reason for it." | stochastic | stochastic | none | breaks | `decisions.template` | high | Twelve records have no opening sentences at all: the H1 is followed straight by `## Context`. See the escalation. |
| `decisions.date` | "A Decision Record's `date` frontmatter key holds the day the decision was made, written `YYYY-MM-DD`, or holds `null` where that day is unrecoverable." | deterministic | stochastic | none | holds | `decisions.template` | high | No file states the day a decision was made, so a script cannot decide the predicate. All twenty-nine carry a `date`; three hold `null` (0002, 0005, 0006). |
| `decisions.immutable-after-merge` | "A Decision Record that `main` carries has its body, and every frontmatter key other than `status`, byte-identical to the first commit on `main` that carries the file." | deterministic | deterministic | none | breaks | none | high | Sixteen of twenty-nine differ from their first commit at their current path: 0001-0014, 0016, 0021. See the escalation. |
| `decisions.status-vocabulary` | "A Decision Record either carries no `status` frontmatter key or carries one holding exactly one of `proposed`, `accepted`, `deprecated`, or `superseded by NNNN`, where `NNNN` is four digits." | deterministic | deterministic | full | holds | none | high | `check_status_vocabulary` skips an absent key and matches the three words or `^superseded by \d{4}$` (`src/dev_playbook/decisions_lint.py:185-216`). Seven records carry `accepted`; the rest carry no key. |
| `decisions.supersession-target` | "A Decision Record whose `status` is `superseded by NNNN` sits in a directory that holds a record numbered `NNNN`." | deterministic | deterministic | none | holds | `decisions.status-vocabulary` | high | Holds vacuously: no record carries a supersession status. Test: for each such status, assert a `NNNN-*.md` sibling exists. decisions-lint already parses the key. |
| `decisions.optional-sections` | "A Decision Record's body carries no section beyond the H1 except `Considered Options` and `Consequences`, and neither of those sections is empty." | deterministic | deterministic | none | breaks | `decisions.template` | low | Twenty of twenty-nine carry other H2s — `Context`, `Decision`, `Why`, `Alternatives considered`, `Recovery`, `Addendum`. See the escalation. |
| `decisions.external-convention-evaluation` | "A Decision Record's decision is a verdict on something outside the workspace: a skill, a skill collection, a framework, or a technique." | stochastic | stochastic | none | breaks | none | high | This H2 carries an H3, so the encoding reads it as a condition, not a rule. Read as a rule it fails on the twenty-one records that rule on the workspace's own material. See the escalation. |
| `decisions.what-was-examined` | "The Decision Record names the source and pins the exact state examined: the repository SHA, the release or version, and the date it was read." | stochastic | stochastic | none | breaks | none | high | Four of the eight external evaluations pin nothing: 0001, 0003, 0004, 0006. 0016 pins `2ab9580`, 0020 pins `v1.2.3`. See the escalation. |

## Escalations

### `decisions.template` — "A Decision Record's frontmatter holds `type: Decision-Record`, a `title`, a `description`, and a `date`; its body opens with an H1 repeating the `title`, followed by one to three sentences:"

The rule sits at
[records.md:66-85](/standards/decisions/records.md#template) and carries
a fenced `md` block whose body line reads
`{1-3 sentences: what's the context, what did we decide, and why.}`.

The frontmatter clause holds everywhere: all twenty-nine records carry
`type: Decision-Record`, a `title`, a `description`, and a `date`, and
every H1 repeats its `title` exactly.

The body clause breaks twice over. Twelve records put no sentence
between the H1 and the first H2: 0003, 0004, 0005, 0006, 0007, 0009,
0017, 0018, 0019, 0021, 0022, and 0025. In
`docs/decisions/0003-decline-superpowers.md` line 8 is the H1 and line
10 is `## Context`. Nine more run past three sentences: 0010 four, 0011
six, 0013 four, 0014 seven, 0016 six, 0020 seven, 0026 eleven, 0027
eight, 0029 four. `docs/decisions/0026-retire-verbatim-skill-adoption.md`
carries 2,721 characters of unsectioned prose after its H1 and no H2 at
all. Eight records obey: 0001, 0002, 0008, 0012, 0015, 0023, 0024, 0028.

The frontmatter clause also restates rules the family does not own.
`knowledge-organization.frontmatter-block`,
`knowledge-organization.types`, `knowledge-organization.title`, and
`knowledge-organization.description` already bind every concept
document, and `okf-lint` decides all four. `decisions.date` states the
`date` key a second time. What is left to this rule alone is two
things: the `type` value is exactly `Decision-Record`, and the H1
repeats the `title`.

Proposal: rewrite. The new sentence is "A Decision Record's frontmatter
holds `type: Decision-Record`, and its body opens with an H1 repeating
the `title`." That keeps the two clauses nothing else states, drops the
`title`, `description`, and `date` restatements, and drops the sentence
count the repo has disobeyed twenty-one times out of twenty-nine. The
template block moves to the explanation or a guide, where a writer's
starting shape belongs. Delete is the other honest option, but it would
lose the tie between the path and the type.

### `decisions.context-decision-and-reason` — "A Decision Record's opening sentences give the context the decision was made in, the decision itself, and the reason for it."

The rule sits at
[records.md:87-92](/standards/decisions/records.md#context-decision-and-reason).
"Opening sentences" names the one-to-three-sentence opener that
`decisions.template` prescribes, so the two rules fail together.

Twelve records have no opening sentences. `0005-issue-workflow-reorganization.md`
line 8 is `# Issue Workflow Reorganization` and line 10 is `## Context`;
the context, the decision, and the reason are each in their own H2
section below. The same shape holds in 0003, 0004, 0006, 0007, 0009,
0017, 0018, 0019, 0021, 0022, and 0025.

Where an opener exists it does carry all three parts.
`0024-disable-native-sandbox.md` gives the cost in its first sentence,
the decision in bold in its second, and the reason in the same sentence.
`0023-headless-on-subscription.md` does the same in three sentences.

Proposal: rewrite. The new sentence is "A Decision Record's body gives
the context the decision was made in, the decision itself, and the
reason for it." Dropping the word "opening" states what the repo does on
purpose: half the records front-load the three parts and half section
them, and both carry all three. The rule's value is in demanding the
three parts, not in fixing where they sit.

### `decisions.immutable-after-merge` — "A Decision Record that `main` carries has its body, and every frontmatter key other than `status`, byte-identical to the first commit on `main` that carries the file."

The rule sits at
[records.md:102-108](/standards/decisions/records.md#immutable-after-merge).
Sixteen of the twenty-nine records on `main` differ from the first
commit that carried them at their current path.

Three edit campaigns did it, and each was deliberate.

Records 0001-0009 were all added at `docs/decisions/` by commit
`d56e6712` and each differs from it. The largest change is the
frontmatter itself: at the repo's initial commit `3bdcc89d` these files
sat at `docs/adr/` with no frontmatter block at all, and the block was
added later. `0003-decline-superpowers.md` also had its body rewritten:
the line `[ADR-0001](0001-adopt-matt-pocock-conventions.md) rejected for
Matt` became `[Decision Record 0001](0001-adopt-matt-pocock-conventions.md)
rejected for Matt`, and a dead citation to `docs/third-party-survey.md`
was replaced with a note that the file retired on 2026-08-01.

Records 0011, 0012, 0013, and 0014 each differ by exactly one added
frontmatter line. `0011-one-registry-for-non-authored-content.md` gained
`date: 2026-07-20` after merge; `date` is not `status`, so the rule
forbids it.

Records 0016 and 0021 had their bodies edited under later decisions.
`0016-pocock-skills-sweep-2026-07.md` line 17 replaced the banned actor
noun with `user` in the phrase `no user ruling exists`, which is
[0019](/docs/decisions/0019-one-word-for-the-person.md) applied to the
record; 0019 states at its own line 72 that "Decision Records were
swapped under an explicit waiver".
`0021-scope-directories-and-spec-item-return.md` line 28 repointed
`/standards/judgments/cache-gate.md` to
`/standards/semantic-validation/cache-gate.md`.

Proposal: rewrite. The new sentence is "A Decision Record that `main`
carries has the substance of its decision unchanged from the first
commit on `main` that carries the file; only its `status`, its
frontmatter, and mechanical citation repairs change thereafter." The
repo has freely added frontmatter keys, renamed the type vocabulary, and
repaired dead paths in merged records, and did so under recorded
waivers, so the byte-identity test states something the repo has decided
twice not to do. Changing the repo is not available here: the edits are
merged and the rule cannot be obeyed backwards.

### `decisions.optional-sections` — "A Decision Record's body carries no section beyond the H1 except `Considered Options` and `Consequences`, and neither of those sections is empty."

The rule sits at
[records.md:125-131](/standards/decisions/records.md#optional-sections).
Twenty of the twenty-nine records carry a section it forbids.

The forbidden headings are the ordinary ones.
`0001-adopt-matt-pocock-conventions.md` carries `## Context` at line 12,
`## Decision` at line 35, `## Why adopt` at line 100,
`## Alternatives considered` at line 114, and
`## Addendum — 2026-05-19` at line 152.
`0017-remove-sdd-support.md` carries `## Scope` at line 62 and
`## Recovery` at line 69. `0015-tooling-verdicts-2026-05-audit.md`
carries one H2 per tool examined. Nine records obey: 0010, 0011, 0013,
0014, 0023, 0024, 0026, 0027, and 0029.

The rule and `decisions.immutable-after-merge` also contradict each
other. Twenty merged records break this rule, and immutability forbids
editing them into compliance, so the two rules together state a target
no repo can reach.

Proposal: delete. The rule's intent, that a record stays short and does
not become a form, is already carried by `decisions.template`'s opener
and by the prose standard's brevity rules, and the explanation at
[explanation.md](/standards/decisions/explanation.md#a-record-can-be-one-paragraph)
says it in plain words: "The value is in recording that a decision was
made and why, not in filling out sections." Nothing a reviewer needs is
lost, and the section roster returns to the explanation, where a
writer's heuristic belongs.

### `decisions.external-convention-evaluation` — "A Decision Record's decision is a verdict on something outside the workspace: a skill, a skill collection, a framework, or a technique."

The rule sits at
[records.md:133-138](/standards/decisions/records.md#external-convention-evaluation)
and carries one H3 beneath it, `### What was examined` at line 140.

[Population and Rules Encoding](/doc-types/standard/encoding.md) states
the mark plainly: "An H2 with no H3 beneath it is a rule that binds
every member. An H2 with H3s beneath it is a condition, and its H3s are
the rules." By that mark this H2 is a condition, and its first paragraph
is a membership test, not a predicate. It nonetheless carries a trailer
and holds a row in `standards/verifiers.yaml` line 33, so the verifier
table counts it as a rule.

Read as a rule it fails on most of the population. Twenty-one of the
twenty-nine records decide something inside the workspace:
`0009-same-repo-resolution.md` sets a path-resolution rule,
`0022-prose-lint-exempt-file.md` adds a per-repo exemption file,
`0028-delete-the-judgments-subsystem.md` deletes a subsystem. None is a
verdict on an outside skill, framework, or technique. Eight are: 0001,
0003, 0004, 0006, 0015, 0016, 0020, and 0026.

Proposal: rewrite, so the words say what the heading level already
means. The new sentence is "A Decision Record whose decision is a
verdict on something outside the workspace — a skill, a skill
collection, a framework, or a technique — is bound by the rules below."
Deleting it would orphan `decisions.what-was-examined`, which needs this
subset to bind. The larger question, whether a condition should carry a
trailer and a verifier row at all, is a design question for the whole
tree, not this family: `standards/standard/detectors.md` marks its
conditions the same way.

### `decisions.what-was-examined` — "The Decision Record names the source and pins the exact state examined: the repository SHA, the release or version, and the date it was read."

The rule sits at
[records.md:140-145](/standards/decisions/records.md#what-was-examined),
under the external-convention-evaluation condition. Eight records fall
under that condition; four of them pin nothing.

`0016-pocock-skills-sweep-2026-07.md` obeys: its title names the pin and
its body names the commit `2ab9580`.
`0020-pocock-skills-sweep-2026-08.md` pins the release `v1.2.3`.
`0015-tooling-verdicts-2026-05-audit.md` pins the audit date
2026-05-08. `0026-retire-verbatim-skill-adoption.md` rules on the
workspace's own adoption mechanism, and pins the lock file it retires.

Four pin nothing. `0003-decline-superpowers.md` names the source as a
bare repository URL in its first paragraph and gives no SHA, no release,
and no read date; a grep for `pin`, `pinned`, `SHA`, `version`, `read
on`, and `as of` over 0001, 0003, 0004, and 0006 returns only 0003's two
lines about SHA-pinning as a dependency mechanism, not about the state
examined. `0001-adopt-matt-pocock-conventions.md`,
`0004-remove-pocock-direct-dependency.md`, and
`0006-harvest-pocock-prototype-and-handoff.md` name Matt Pocock's
repository and pin no state of it.

Proposal: rewrite. The new sentence is "The Decision Record names the
source and pins at least one of the exact state examined: the repository
SHA, the release or version, or the date it was read." The four
breaking records all predate the sweep records that established the
practice, immutability forbids repairing them, and the sweeps that do
pin state pin one identifier each, not all three. Demanding all three
states something no record in the repo has ever done.

## Detectors

**`scripts/decisions-lint`** is a thin shim over
`src/dev_playbook/decisions_lint.py`. It walks the repo's markdown once
through `md.find_md_files`, keeps the files whose first two path parts
are `docs/decisions`, and applies two rules. `check_sequential_numbering`
matches `^(\d+)-.+\.md$` against each filename and flags a number below
1, a prefix whose length is not four, a duplicate number, and each run
of missing numbers up to the highest present, collapsing a run into one
finding so a lone `0050` reports one gap rather than forty-nine.
`check_status_vocabulary` parses each record's frontmatter, skips a
record with no `status` key, and flags a value that is neither
`proposed`, `accepted`, `deprecated`, nor a match for
`^superseded by \d{4}$`; frontmatter that will not parse raises
`CannotRun` and exits 2. An absent `docs/decisions/` passes both. The
detector decides no other rule of the family, and it never looks at a
non-markdown file, so a stray `.txt` in the directory is invisible to
it.

**`scripts/ref-lint`** decides no `decisions.*` rule, but it is the only
other code that reads the directory. Its `source_files` classifies every
markdown file there: a numbered record is skipped as a reference source,
because an immutable record's outbound links go stale by design;
`index.md` and `README.md` are validated like any other document; and
anything else raises `UnclassifiedRecordsFile`, which stops the run
rather than exempt the file silently. That stop is the nearest thing the
repo has to a check on `decisions.the-directory`, and it is a run
failure under a `ref.*` id, not a finding under a `decisions.*` one.

**`scripts/okf-lint`** decides no `decisions.*` rule either, but it
decides four rules that `decisions.template` restates:
`knowledge-organization.frontmatter-block`,
`knowledge-organization.types`, `knowledge-organization.title`, and
`knowledge-organization.description`. Its `types` check requires the
`type` value to name a row of the registry table, which carries a
`Decision-Record` row; it does not require a record to carry that
particular row.
