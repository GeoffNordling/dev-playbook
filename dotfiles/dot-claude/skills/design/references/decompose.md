# The Decompose Exit

The exit taken when the work is bigger than one build. The issue becomes an
**epic** and never builds itself; its children carry the work. Read only when §6
settled on this exit — the single-leaf exit needs none of it.

The children's intake happens here, in place, so none round-trips through
`intake`. Minting carries a child only as far as a **starting brief** — a leaf
with the four-tuple, the seven headings, and its relationships wired, but its
substance still provisional. Every child leaves this session incomplete. Each
becomes **brief-complete** in its own `/design` session, which re-authors that
brief, and **ready** at that session's issue-review verdict. The readiness bar is
[issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#readiness).

## 1. Rewrite the issue as the epic

Its body becomes the outcome plus the decomposition rationale — never a
restatement of the sub-issue list GitHub already shows. Its labels become
`category:*` alone: strip `mode:*`, `tests:*`, and `phase:design`, since an epic
never dispatches.

```bash
gh issue edit <epic#> \
  --remove-label "<mode>" --remove-label "<tests>" --remove-label "phase:design" \
  --body "$(cat <<'EOF'
...outcome and decomposition rationale...
EOF
)"
```

## 2. Slice

Before slicing, test the epic's outcome — and then each slice as it is cut —
against the two-question orthogonality test in the
[One-goal principle](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#brief-principles);
apply its statement, never a paraphrase. What fails out is deferred exactly as
the bullet says: a real tracker stub minted at `phase:intake`, named in the
deferring body's `Out of scope`. Deferral itself implies no dependency edge.

Vertical slices, per
[the vertical-slice rules](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#vertical-slice-rules)
— each one a thin complete path through every layer, sized so building it keeps
an agent well inside its context budget. The builder will not resize the work,
so the split has to be right here.

Order the slices by dependency before creating any of them; step 4 links each to
a blocker that must already exist.

## 3. Mint each child with a starting brief

One `gh issue create` per slice, in dependency order, each with a full
four-tuple and all seven build-leaf headings — the headings are required from
minting, and a leaf missing one is a lint finding whatever its phase.

Write into them what this session actually settled: the slice's outcome, its
boundary, and the intent it inherits from the epic. The rest is a draft. A
child's brief is not finished here and is not meant to be — its own design
session re-authors it against the code as it stands by then, which is not the
code this session is looking at.

So every child is minted at `phase:design`, never `phase:build`. Its own
issue-review verdict, in its own session, is what moves it.

```bash
gh issue create --title "..." \
  --label "<category>" --label "<mode>" --label "<tests>" --label "<phase>" \
  --body "$(cat <<'EOF'
...the seven build-leaf headings...
EOF
)"
```

## 4. Wire the relationships

Two independent native relationships, per
[Relationships](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#relationships):
each ordered slice **blocked-by** its predecessor, and every slice a
**sub-issue** of the epic. Neither is a body field and neither is a label.

Neither has a `gh` subcommand, and both endpoints take the issue's internal
`id`, not its number — so each is two calls: read the id off the first, pass it
to the second.

```bash
gh api repos/{owner}/{repo}/issues/<blocker#> --jq .id
gh api --method POST repos/{owner}/{repo}/issues/<dependent#>/dependencies/blocked_by -F issue_id=<the id above>
```

```bash
gh api repos/{owner}/{repo}/issues/<child#> --jq .id
gh api --method POST repos/{owner}/{repo}/issues/<epic#>/sub_issues -F sub_issue_id=<the id above>
```

## 5. Report the shape back

Before closing the phase, show the user the epic, the ordered children with
their four-tuples, and the two relationship graphs — they do not align, and a
mis-wired blocker strands work silently.

Children leave here incomplete and unreleased, at `phase:design`. Each is
finished by its own `/design` session: that session re-authors the starting
brief and then takes the
[issue-review verdict](~/workspace/dev-playbook/software-factory/user-checkpoints.md#the-issue-review-verdict)
at its §8 — one issue, one design pass, full attention. Finishing every child
here instead would spend the thinnest attention of the longest session in the
region on the work that most needs care.
