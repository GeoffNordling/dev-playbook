---
name: pocock-sweep
description: Sweep mattpocock/skills at its latest release against the workspace's standing verdicts and land the rulings in one PR.
disable-model-invocation: true
model: inherit
effort: xhigh
---

# Pocock Sweep

The workspace's standing position on every skill in `mattpocock/skills` is
[the ledger](~/workspace/dev-playbook/docs/external-skill-verdicts.md) — one
row per skill, stating where that skill stands today. A sweep moves the
workspace from the pin the ledger names to the package's current release, and
rules **only what changed**.

The rules that bind a sweep are written in the ledger — the verdict
vocabulary, the sweep direction, the supersede rule, the tier policy. Read
them and follow them; nothing restates them here. The one that shapes every
step below: adoption is by copy. An adopted skill is an owned file in
`dotfiles/dot-claude/skills/`, free to drift from upstream, so a bumped
skill's diff runs between the two upstream pins — never against the
workspace's copy, whose divergence is its own.

**Pacing is open.** The bootstrap run worked one stage per context window
against a plan file it kept in the branch, and never established that as
necessary. Run straight through, or across windows, as the work demands. When
it spans windows, keep a plan file in the branch recording each stage's
outcome so the next window resumes from the branch rather than from memory,
and delete it before the PR.

## 1. Read first

Before doing anything else, {Read [external-skill-verdicts.md](~/workspace/dev-playbook/docs/external-skill-verdicts.md)
end-to-end; the standing verdict on every skill, and the rules that bind this
sweep}.

Then say `READ: external-skill-verdicts.md` and proceed only after.

## 2. Resolve the release

Sweeps evaluate release tags, never `main`.

```
gh api repos/mattpocock/skills/releases/latest --jq .tag_name
gh api repos/mattpocock/skills/commits/<tag> --jq .sha
```

{If the ledger already names this tag, {report that there is nothing to
sweep} and stop}. The commit SHA travels to step 8: the ledger is where the
pin's provenance is recorded.

## 3. Clone the tag

Clone the package at the tag into a scratch directory outside the repo. This
clone is what the sweep reads: the substantive-or-cosmetic call on every
bumped skill comes from diffing the skill between the ledger's pin and the
new tag inside the clone's own history — both sides upstream, since the
workspace's copies own their divergence and prove nothing about his.

## 4. Build the docket

Compare the package at the new pin against the ledger's rows. Every difference
is one docket item carrying a recommendation and the evidence behind it:

- A skill upstream **added** — unruled, needs a verdict.
- A skill upstream **deleted** — its row retires.
- A skill that **moved tier**.
- A row marked **reevaluate**, or still **unruled** from an earlier sweep.
- An adopted skill whose upstream **bytes changed** between the pins. Read
  the diff and say which it is: a substantive change to what the skill does,
  or a pin bump only. A substantive one is a proposal to edit the owned
  copy — name what the edit would carry over and what workspace divergence
  it must not touch.
- **Supersede-rule creep** in the authored adaptations the ledger lists. The
  check is for creep, not removal: these are deliberately authored, and the
  question is whether an adopted skill has grown to cover one of them.

A row whose verdict is unchanged and whose upstream bytes did not move is
**standing**. It does not enter the docket, and it is not re-argued.

This step is done when every skill in the package is accounted for — docketed
or standing — and the tally matches the package's own tier counts.

## 5. Rule the docket with the user

The user rules every item, one item at a time. What you bring is a lead: the
recommendation, the evidence, and what it costs either way.

A recap clause is not a docket. An item the user has not ruled on by itself is
unruled, however clearly the surrounding discussion pointed at an answer.

## 6. Land the rulings on a branch

Open a worktree branch. Everything the sweep owes lands there and ships as
one PR: the copies, the standards edits, the accommodation work, the ledger,
the Decision Record. No follow-up issues — a sweep that defers half its work
leaves verdicts nobody can act on.

A newly adopted bundle is copied out of the clone into
`dotfiles/dot-claude/skills/<name>/` and is owned from that moment. The same
change brings it up to the workspace's own rules — the commit gate runs
unaided over it, and whatever conventions every owned runbook carries apply
to this one too; a copy that lands red is not landed.

An upstream delta ruled into an already-adopted skill is an ordinary edit to
the owned copy, folding in what the ruling adopted — never a byte-copy over
it, which would discard the workspace's own changes to that file.

## 7. Audit the branch

An adversarial pass over the sweep's own work, before the records are written:

- Every call site of every changed skill still describes what that skill now
  does.
- The supersede-rule duplication scan comes back clean.
- No reference dangles at a file this sweep retired.
- The sweep obeyed the rules the sweep is enforcing. Turn each rule on the
  branch's own diff — in the bootstrap run this pass found the supersede rule
  broken by the sweep itself: one description of an adopted skill,
  hand-copied to four sites, had drifted apart and was wrong at all four.

## 8. Write the records

{Write the ledger to the new pin; every row current, retired rows folded into
a closing note, the general rules updated where a ruling changed one}. It
is also where the pin's provenance lives: the ledger is the pin's only
record, so the tag and its commit are named there or nowhere.

{Write the Decision Record beside it; **thin and delta-only** — what moved
and why, the positions declined so a later sweep does not re-find them, and
any correction to a claim the sweep made along the way}. Where a skill stands
today is the ledger's question.

## 9. Open the PR

The body carries the change inventory and ends with the **habit brief**: what
changes for an operator who already knew the prior state. Behavior, not files
— "grilling now lands in rounds, so answer by number" is the shape, and a list
of edited paths is not.
