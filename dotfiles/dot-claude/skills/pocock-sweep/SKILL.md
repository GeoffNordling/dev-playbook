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

The rules that bind a sweep are written in the ledger. Read them and follow
them; nothing restates them here.

**Pacing is open.** The bootstrap run worked one stage per context window
against a plan file it kept in the branch, and never established that as
necessary. Run straight through, or across windows, as the work demands. When
it spans windows, keep a plan file in the branch recording each stage's
outcome so the next window resumes from the branch rather than from memory,
and delete it before the PR.

## 1. Read first

Before doing anything else, read end-to-end:

- [the ledger](~/workspace/dev-playbook/docs/external-skill-verdicts.md) — the
  standing verdict on every skill, and the rules that bind this sweep.
- [skill-management.md](~/workspace/dev-playbook/standards/claude-code/skill-management.md)
  — where installed skills live, the lock file, and the mirror rule.

Then report: `READ: external-skill-verdicts.md, skill-management.md`. Proceed
only after.

## 2. Resolve the release

Sweeps evaluate release tags, never `main`.

```
gh api repos/mattpocock/skills/releases/latest --jq .tag_name
```

The tag the ledger already names means there is nothing to sweep. Say so and
stop.

Otherwise resolve two commits and compare them — the second decides how step 6
installs:

```
gh api repos/mattpocock/skills/commits/<tag> --jq .sha
gh api repos/mattpocock/skills/commits/main --jq .sha
```

Equal, and the release is the tip of his branch: the `skills` CLI fetches his
default branch, so what it installs is exactly the tag. Unequal, and he has
merged unreleased work since cutting the release, so step 6 installs by hand
at the tag instead. Report which one you got — the hand route is slower, and
the user should know why before it starts.

## 3. Clone the tag

Clone the package at the tag into a scratch directory outside the repo. This
clone is what the sweep reads: the substantive-or-cosmetic call on every bumped
skill comes from diffing it against the bundles already installed.

## 4. Build the docket

Compare the package at the new pin against the ledger's rows. Every difference
is one docket item carrying a recommendation and the evidence behind it:

- A skill upstream **added** — unruled, needs a verdict.
- A skill upstream **deleted** — its row retires.
- A skill that **moved tier**.
- A row marked **reevaluate**, or still **unruled** from an earlier sweep.
- An installed skill whose **bytes changed** at the new pin. Read the diff and
  say which it is: a substantive change to what the skill does, or a pin bump
  only. A substantive one has consequences — a workspace call site that
  quotes the old behavior goes stale the moment the bytes land.
- **Supersede-rule creep** in the authored adaptations the ledger lists. The
  check is for creep, not removal: these are deliberately authored, and the
  question is whether an installed skill has grown to cover one of them.

A row whose verdict and delivered artifact are both unchanged is **standing**.
It does not enter the docket, and it is not re-argued.

This step is done when every skill in the package is accounted for — docketed
or standing — and the tally matches the package's own tier counts.

## 5. Rule the docket with the user

The user rules every item, one item at a time. What you bring is a lead, never
a ruling: the recommendation, the evidence, and what it costs either way.

A recap clause is not a docket. An item the user has not ruled on by itself is
unruled, however clearly the surrounding discussion pointed at an answer.

## 6. Install on main

The ruled installs land on the main checkout, before any branch exists, through
the CLI that owns the lock file. Run one line per skill:

```
npx skills@latest add mattpocock/skills --skill <name> -g -y
npx skills@latest update <name> -g
```

`add` for a new install, `update` for a skill already installed whose bytes
moved. Then ask the user to run `scripts/sync-dotfiles` from the main checkout,
which creates the mirror symlinks; it relinks the live `~/.claude` tree, so it
is theirs to run and never runs from a worktree.

The CLI writes `dotfiles/.agents/.skill-lock.json` as it installs. Verify
before committing: each installed folder matches the clone's copy
byte-for-byte (`diff -r`). Then one commit on main carrying the bundles, the
lock entries, and the symlinks.

**When that commit reddens the gate, its accommodation goes in the same
commit.** An install can arrive carrying a file the workspace's own lints want
to rewrite — a vendored shell script, say — and the exclusion that exempts it
is what makes the install committable at all. Fix it there rather than
committing over a red gate or deferring it to the branch.

**When the tag is not his branch tip** (step 2), install by hand instead. The
CLI would fetch his unreleased work, which is not what the docket ruled on:
every substantive-or-cosmetic call in step 4 came from diffing the tag, so
installing the branch tip means re-ruling the whole docket against a target
that moves again next week. The hand route keeps the sweep pointed at a fixed
revision, and pays for it with a lock hash nobody validated for you.

Copy each bundle byte-for-byte out of the clone into
`dotfiles/.agents/skills/<name>/`, add the mirror symlink
`dotfiles/dot-claude/skills/<name>` → `../../.agents/skills/<name>`, and write
each lock entry's `skillFolderHash` as the upstream git tree SHA of that skill
folder. Validate the algorithm first against a bundle byte-identical at both
pins — its computed SHA must equal the value already in the lock — and stop to
investigate rather than inventing a hash.

**Vendored bytes belong to upstream, whichever route installed them.** A
formatter run at a vendored path is a defect, not a fix, and the workspace's
gates exempt those trees for exactly that reason. When a lock entry and its
tree disagree, assume the bytes moved, not the lock — rewriting the lock to
match locally altered bytes blesses them as upstream's.

## 7. Branch, and land the rest of the rulings

Open a worktree branch. Everything the sweep still owes lands there and ships
as one PR: standards edits, accommodation work, the ledger, the Decision
Record. No follow-up issues — a sweep that defers half its work leaves verdicts
nobody can act on.

## 8. Audit the branch

An adversarial pass over the sweep's own work, before the records are written:

- The mirror rule holds, and no authored skill collides with an installed name.
- Every call site of every bumped skill still describes what that skill now
  does.
- The supersede-rule duplication scan comes back clean.
- No reference dangles at a file this sweep retired.
- The sweep obeyed the rules the sweep is enforcing. Turn each rule on the
  branch's own diff — in the bootstrap run this pass found the supersede rule
  broken by the sweep itself: one description of an installed skill,
  hand-copied to four sites, had drifted apart and was wrong at all four.

## 9. Write the records

The ledger is rewritten to the new pin — every row current, retired rows folded
into a closing note, the general rules updated where a ruling changed one. It
is also where the pin's provenance lives: the lock file records a folder hash
and no revision, so the tag and its commit are named in the ledger or nowhere.

The Decision Record beside it is **thin and delta-only**: what moved and why,
the positions declined so a later sweep does not re-find them, and any
correction to a claim the sweep made along the way. Where a skill stands today
is the ledger's question, not the record's.

## 10. Open the PR

The body carries the change inventory and ends with the **habit brief**: what
changes for an operator who already knew the prior state. Behavior, not files
— "grilling now lands in rounds, so answer by number" is the shape, and a list
of edited paths is not.

The installs are already on main from step 6, so name them in the inventory
with the commit that carried them; the PR itself is the accommodation around
them.
