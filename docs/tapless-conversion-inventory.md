---
type: Guide
title: Tapless Conversion Inventory
description: "Point-in-time inventory of SSH/tap-era literals, prose, and config across the repo, feeding the tapless conversion issues under map #322"
---

# Tapless Conversion Inventory

This is a **point-in-time inventory**, not a governing standard. It exists to
feed the conversion issues spawned from the tapless-operations map,
[#322](https://github.com/GeoffNordling/dev-playbook/issues/322). It records
what exists and quotes it; it makes no recommendations and proposes no
rewrites — design decisions belong to the individual conversion tickets.

Produced against the repo checkout as of commit `27db559` (2026-08-02), from
an isolated worktree, read-only.

## 1. `git@github.com:` / `ssh://` literals

Exhaustive grep for the literal strings `git@github.com:` and `ssh://` across
the whole repo, including `dotfiles/`.

`ssh://` — no hits outside `uv.lock` (a Python package's own source URL
metadata, unrelated to this repo's git remotes; not included below).

`git@github.com:` — 5 files, ~29 occurrences:

| Path | Line | Text | Why tapless invalidates it |
|---|---|---|---|
| `dotfiles/dot-claude/rules/bash-commands.md` | 130 | "If the remote is `git@github.com:...`, then `git fetch`, `git pull`, and" | Names the SSH remote form as the trigger condition for the whole "SSH-bound git operations" section (see §2); origin is now HTTPS everywhere. |
| `dotfiles/dot-claude/skills/clean-up-branch-worktree/SKILL.md` | 44 | `` git -c url."https://github.com/".insteadOf=git@github.com: -c credential.helper='!gh auth git-credential' fetch --prune origin `` | A per-command HTTPS rewrite workaround for an SSH-remote `origin`; origin is already HTTPS, so the rewrite has nothing to rewrite. |
| `tests/dev_playbook/test_workspace_lint.py` | 23 occurrences (e.g. 423, 436, 459, 472, 499, 518, 533, 548, 573, 592, 614, 633, …) | e.g. `ws, "alpha", {"README.md": "# A\n"}, origin="git@github.com:me/alpha.git"` | Test fixtures exercising `workspace_lint.py`'s dual-format origin regex (see next row) with SSH-style sample origins. Not a live assumption about how *this* workspace's repos are remoted — flagged for completeness. |
| `src/dev_playbook/workspace_lint.py` | 218–219 | `` REMOTE_SLUG_PATTERN = re.compile(r"^(?:git@github\.com:\|https://github\.com/)([^/\s]+/[^/\s]+?)(?:\.git)?$") `` | Live code, already dual-format (accepts both SSH and HTTPS origins) — not obviously broken by tapless, but it is the one place a `git@github.com:` literal ships in a `.py` module rather than prose. Flagged for a conversion ticket to decide whether the SSH branch is still worth carrying. |
| `readings/file-graph/dev-playbook.html` | 172 (one very long generated line; 3 occurrences within it) | Generated file-graph artifact (built 2026-07-15, tracked in git) embedding a full-text snapshot of `bash-commands.md`, `clean-up-branch-worktree/SKILL.md`, and other repo files. | Derivative of the two prose hits above — not new authored content. Regenerate via the `datasheet`/file-graph tooling after the source files are updated; do not hand-edit. |

## 2. Prose assertions of the SSH/tap world

Grouped by file. "Tapless invalidates it" is one line each; no rewrites
proposed.

### `dotfiles/dot-claude/rules/bash-commands.md`

The entire **"SSH-bound git operations"** section, plus two supporting
mentions elsewhere in the file:

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 88 | "out-of-jail resource — the keyring holding `gh`'s PAT, the SSH remote for `git`." | Cites the SSH remote as the reason `git` is sandbox-excluded; the remote is HTTPS now, so the stated rationale for the exclusion needs re-stating even if the exclusion itself stays. |
| 112 | "and auth fails (`gh`: HTTP 401; `git` push/pull: no key)" | Frames a `git push`/`pull` auth failure as a missing SSH key; under HTTPS+PAT the failure mode is a missing/invalid PAT instead. |
| 128 | `## SSH-bound git operations` (section heading) | Names the whole section after the transport that no longer applies. |
| 130–132 | "If the remote is `git@github.com:...`, then `git fetch`, `git pull`, and `git push` all require the user's SSH key — hardware-token taps in this workspace. Treat them like any other interactive command:" | States the precondition (`git@github.com:` remote) that is now false workspace-wide, and the consequence (SSH key / hardware tap required) that follows from it. |
| 134–136 | "For read-only checks (e.g. \"does local `main` match `origin/main`?\"), use `gh api` instead — it goes over HTTPS with a PAT and needs no tap. Example: `gh api repos/{owner}/{repo}/branches/main --jq .commit.sha`" | Presented as a workaround *because* direct git reads need a tap; under HTTPS+PAT, plain `git` reads need no tap either, so the workaround's premise is gone (though the `gh api` pattern itself may still be useful for other reasons). |
| 137 | "For pushes, hand the command back to the user." | States pushes are always handed to the human; the map's premise is that agents may now push freely. |

### `dotfiles/dot-claude/skills/commit/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 3 (frontmatter `description`) | "Commit staged work locally with a clean message; the user pushes." | Bakes "user pushes" into the skill's own description/trigger text. |
| 15 | "`git push` requires a YubiKey tap, so the user pushes — never run `git push` yourself." | The core instruction this skill exists to enforce; directly contradicted by the map's premise that agents may push. |

### `dotfiles/dot-claude/skills/open-pr/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 12 | "The branch is `issue-<issue>`; the user pushed it before the review launched. You create the PR — a tap-free `gh` call — but you never push." | Asserts the branch can only reach origin via a human push; the escalate branch below is built on the same assumption. |
| 18, 32, 35 | Escalate condition: "the branch was never pushed, or local commits sit ahead of the last push" / `ESCALATE: … local commits unpushed` | The escalation exists only because the skill assumes it can never push the branch itself to fix the condition. |

### `dotfiles/dot-claude/skills/clean-up-branch-worktree/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 37 | `## 2. Refresh origin/main without a YubiKey` (section heading) | Names a whole procedural step after a workaround the tapless remote no longer needs. |
| 39–40 | "`origin` is an SSH remote, so plain `git fetch origin` wants a hardware tap. Rewrite the URL to HTTPS and hand git the PAT that `gh` already holds." | States the precondition (SSH remote) that is now false; the URL-rewrite trick has nothing left to rewrite. |
| 44 | (the `insteadOf=git@github.com:` command — quoted in §1) | Same. |

### `dotfiles/dot-claude/skills/update-standards-pin/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 31–32 | "Unequal means the release is unpushed: hand the user the push and stop, since `git push` needs their YubiKey." | Asserts the agent must stop and hand off rather than push itself. |
| 78 | `## 6. Commit, then hand back the pushes` (section heading) | Section is titled around handing pushes to the human. |
| 84 | "Pushes need the user's YubiKey. Hand back one short line per repo and say to run them separately, in order…" | Same pattern as above, across potentially several consumer repos at once. |

### `dotfiles/dot-claude/skills/log-friction/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 14 | "commit it, and hand the user the push." | States the hand-off as the skill's normal end state. |
| 35–36 | "Remind the user to push (their YubiKey): hand them, as one line, `git -C ~/workspace/mission-control push`." | Same pattern, targeted at a specific sibling repo (mission-control). |

### `dotfiles/dot-claude/skills/idea/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 41 | "a local commit on mission-control's branch, no push." | States the skill deliberately stops short of pushing. |
| 42–46 | "Hand the owner the push, as one line: `git -C ~/workspace/mission-control push`" | Same hand-off pattern as log-friction, independently authored. |

### `dotfiles/dot-claude/skills/issue-overwatch/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 14 | "Two hard limits: you never push, and you never merge. Both are the user's." | The overwatch's own stated hard limit lumps push in with merge; the map keeps merge human-only but not push. |
| 76 | "Confirm the base is fresh, tap-free: … A mismatch is a stale base — hand the user the pull (§7) and stop." | Treats any pull as something the overwatch must hand off rather than do. |
| 96–98 | "**Intermediary push, after any committing node:** `git … push --no-verify -u origin issue-<N>`" / "**Final push, when the judgments node committed fixes:** `git … push origin issue-<N>`" / "**Pull, on a stale base:** `git -C ~/workspace/<repo> pull`" — all listed under "Turn boundaries — the user's commands" | The whole "turn boundaries" mechanic exists to hand these three commands to the human at the end of every turn; tapless removes the reason two of the three (push, pull) must be handed off at all. |

### `dotfiles/dot-claude/skills/agent-view-overwatch/SKILL.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 56 | "A push, merge, or verdict pending at an issue's own overwatch is not its own glyph — it reads as 💤💚 with the action named in **Notes**; the command itself is that overwatch's to surface, not yours." | Groups "push pending" with "merge pending" as an equally-human-only blocking state. |
| 62 | Board example row: `push pending at its overwatch` | Concrete example of the same pattern, will read oddly once push is agent-doable. |

### `dotfiles/dot-claude/hooks/session-start-stale-base`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 13–15 | "The check is read-only over HTTPS with gh's keyring PAT, so it needs no YubiKey tap. It therefore cannot pull — pulling is over the SSH remote and is the user's to run." | States the hook's read/pull asymmetry is caused by the SSH remote specifically. |
| 73 | `git pull        (needs their YubiKey — never run it yourself.)` | The literal instruction the hook emits to the agent when the base is stale. |

### `software-factory/human-checkpoints.md` — the single biggest offender

This document *is* the governing standard for what falls to the human and
why; nearly every section leans on the SSH/tap premise.

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 12–13 | "**Capability** — the agent *cannot* do it. Pushing, pulling, and merging need credentials or a hardware tap it does not have." | The document's own definition of one of the only two reasons a checkpoint exists. |
| 23–27 | "What the agent can do on GitHub is set by its PAT: it authorizes the HTTPS API — the `gh` family and REST endpoints — but not pushing over the SSH remote, and not merging a PR (`mergePullRequest` is forbidden to it). So three operations fall to the human: `git push` and `git pull`, whose SSH remote needs a YubiKey tap in the human's own terminal, and merging the PR, in the GitHub UI." | The core paragraph defining "the agent-capability boundary" around push/pull, keyed entirely on the SSH remote. |
| 33–39 | Table: `git push` — Agent-capable: no, Owner: human; `git pull` — Agent-capable: no, Owner: human; merge — Agent-capable: no, Owner: human | Push and pull are tabulated identically to merge as categorically not agent-capable. |
| 41 | "The taps cannot be designed away, so they are not treated as friction to minimize. What is minimized is their *count* and their *cost*…" | Whole design philosophy premised on taps being unavoidable. |
| 67–77 | "Turn boundaries" — "**Intermediary push**, after any committing node…", "**Final push**, when the judgments node committed fixes…", "**Pull**, on a stale base…", "**Merge**, on the final approval…" | Lists push and pull alongside merge as the fixed set of turn-ending human commands. |
| 138 | "the verified push already handed over if the judgments node committed fixes" | Pause-3 readiness criteria assumes the push was already handed to (and presumably run by) the human. |

### `software-factory/factory-operations.md`

| Line | Text | Why tapless invalidates it |
|---|---|---|
| 154–157 | "gated on a tap-free check that the local `origin/main` ref matches origin (`git rev-parse origin/main` against `gh api …/branches/main`); a stale base escalates, since pulling is the human's." | States pulling is categorically the human's. |
| 173–179 | "**The branch is pushed by the human.** A committing node commits and stops; the push needs a hardware tap the agent cannot give, so it is a checkpoint … Two consequences shape everything downstream: a node can never open the PR itself, because the branch isn't on origin when the node ends; and every intermediary push rides `--no-verify`…" | Names the whole worktree contract's shape as a *consequence* of push needing a hardware tap — a downstream design chain resting on the SSH premise. |
| 241 | "a tap-free `gh pr edit`" | Contrasts a `gh` write as tap-free, implicitly against push/pull which are not — same premise. |
| 288 | "Every intermediary push rode `--no-verify`, so a red cache never blocked a work cycle" | Describes the intermediary-push mechanic (itself premised on the human running it) as the reason the judgments node exists in its current shape. |

### False positives excluded

`docs/machines.md` lines 11 and 17 use "hardware" to describe physical
laptop hardware (a Windows/WSL dual-boot machine), unrelated to hardware
security tokens — not included above. `docs/sandboxing.md` mentions of
`~/.ssh` describe the sandbox's filesystem deny-list generally, not a
git-transport assertion — not included above (though see the config
inventory in §3, which does cover the matching `denyRead` entry). "Push"
mentions in `standards/build/*.md` and `CONTEXT.md` are all about the
**push gate** (the `make check-judgments` pre-push git hook that arms
regardless of transport) — unrelated to who is allowed to run `git push`,
and excluded.

## 3. Config inventory — for #330

Every `dotfiles/settings/*.json` entry governing `git push`, `git pull`,
`git fetch`, or `gh`. Listed verbatim; nothing here is changed.

### `dotfiles/settings/base.json`

`permissions.allow[]` — the full allow-list is `gh`- and worktree-heavy;
**no entry allows `git push`, `git pull`, or `git fetch` directly** (only
`git worktree add *` / `git worktree remove *` are present for `git`
itself). The `gh` entries present:

```
Bash(gh label list)
Bash(gh label list *)
Bash(gh label create *)
Bash(gh issue view *)
Bash(gh issue create *)
Bash(gh issue comment *)
Bash(gh issue edit *)
Bash(gh issue close *)
Bash(gh issue reopen *)
Bash(gh issue lock *)
Bash(gh issue unlock *)
Bash(gh issue transfer *)
Bash(gh pr create *)
Bash(gh pr comment *)
Bash(gh pr edit *)
Bash(gh pr close *)
Bash(gh pr reopen *)
Bash(gh pr ready *)
Bash(gh pr review *)
Bash(gh pr checkout *)
Bash(gh pr update-branch *)
Bash(gh pr lock *)
Bash(gh pr unlock *)
```

`permissions.deny[]`: `["AskUserQuestion"]` — unrelated to git/gh.

`autoMode.allow[1]` (index 1, after `"$defaults"`): "All GitHub CLI (`gh`)
operations are approved, including writes such as `gh issue comment`,
`gh issue edit` (phase-label changes), `gh issue create`/`close`/`reopen`,
`gh pr create`, and `gh pr comment`/`edit`. The software factory's hands-off
(auto-mode) nodes use them to post review findings and advance the
`phase:*` label on an issue's own GitHub tracker and to open and annotate
its PR. These are routine internal project-management writes against our
own repositories, not escalations or unrecognized infrastructure." — blanket
`gh` approval; says nothing about `git push`/`pull`/`fetch`.

### `dotfiles/settings/fedora.json`

`sandbox.excludedCommands[]` — the entries governing `git`/`gh` specifically
(full array also includes `agentsview`, `transcript-export`,
`bootstrap-labels`, `workspace-lint`, `make check`, `uv run pytest`, not
reproduced here since they don't govern push/pull/fetch/gh):

```
"gh"
"gh *"
"git"
"git *"
```

`"git"` / `"git *"` is unconditional — it exempts every git subcommand
(push, pull, fetch, and everything else) from the bwrap jail alike, not
push/pull/fetch specifically.

Adjacent, not a push/pull/fetch/gh governor but SSH-relevant:
`sandbox.filesystem.denyRead[]` includes `"~/.ssh"`, `"~/.aws"`,
`"~/.gnupg"`, `"~/.netrc"` — SSH key material is already unreadable inside
the sandbox regardless of transport.

### `dotfiles/settings/wsl.json`

Entire file is `{}` — no permission or sandbox entries at all (relies
entirely on `base.json` and whatever `fedora.json`-equivalent WSL uses
elsewhere, or on host-level settings not in this repo).

## 4. Repo-creation checklist — where a manual ruleset step would slot in

Two files carry the new-repo GitHub setup steps.

### `standards/build/bootstrap.md`, section "## The GitHub tail" (lines 31–41)

```
## The GitHub tail

From the new repo, in order:

1. `gh repo create <owner>/<name> --source=. --push` — pick the visibility
   flag deliberately.
2. `~/workspace/dev-playbook/scripts/bootstrap-labels` — mint the canonical
   label scheme.
3. Set the merge settings by hand, per
   [repo-settings.md](/standards/tracking/repo-settings.md) — they sit
   behind GitHub's Administration permission, so no script does this.
```

Step 3 currently covers only the **merge strategy** settings
(squash-only, auto-delete branches, etc.) from `repo-settings.md`'s first
section. It says nothing about the **default-branch ruleset**
(`repo-settings.md`'s second section, below) — a manual "protect main via
ruleset" step is absent from this numbered list entirely.

### `standards/tracking/repo-settings.md`, section "## Default branch: protected from destructive operations" (lines 27–49)

```
## Default branch: protected from destructive operations

The default branch `SHALL` carry a **ruleset** — **Settings → Rules → Rulesets** —
targeting it with enforcement **Active** and both destructive-operation rules on:

| Rule | Denies |
|---|---|
| Block force pushes | rewriting history under the branch |
| Restrict deletions | removing the branch |
...
```

This section states the *requirement* but — unlike the merge-strategy
section immediately above it (lines 23–25: "Set these by hand, not by
token — the merge settings sit behind GitHub's all-or-nothing
**Administration** permission, too broad to grant for a one-time toggle.")
— it does not itself say the ruleset must be created by hand. The PAT
deliberately lacks Administration, so (per this sweep's brief) ruleset
creation is manual too; that fact is not yet stated here or cross-referenced
from `bootstrap.md`'s GitHub tail.

Related: `src/dev_playbook/workspace_lint.py`'s `tracking.branch-protection`
rule (added in #320) already **audits** for this ruleset post-hoc by reading
`defaultBranchRef.rules`; it does not create one, and nothing in the
bootstrap checklist currently points a fresh repo at it.
