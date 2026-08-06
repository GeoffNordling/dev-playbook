# The Decompose Exit

The exit taken when the work is bigger than one build. The issue becomes an
**epic** and never builds itself; its children carry the work. Read only when §6
settled on this exit — the single-leaf exit needs none of it.

The children's intake happens here, in place. Each child leaves design **ready**
— a leaf, unblocked or explicitly blocked, brief-complete, released at an
issue-review verdict — so none round-trips through `intake`. The readiness
bar is
[issue authoring](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#readiness);
the factory checks it at the crossing.

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

Vertical slices, per
[the vertical-slice rules](~/workspace/dev-playbook/standards/tracking/issue-authoring.md#vertical-slice-rules)
— each one a thin complete path through every layer, sized so building it keeps
an agent well inside its context budget. The builder will not resize the work,
so the split has to be right here.

Order the slices by dependency before creating any of them; step 4 links each to
a blocker that must already exist.

## 3. Mint each child ready

One `gh issue create` per slice, in dependency order, each with a full
four-tuple and a brief-complete body in the build-leaf format. The phase is the
node that takes it next. There is nothing left for a child's own design pass to
decide — the approach was just settled — but `phase:build` is never set at
creation: per the readiness bar above, it is set at the child's issue-review
verdict. Mint the child at `phase:design` and let the verdict move it.

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
