---
type: General-Sheet
title: Experiment Log
description: The historical record of the experiments that built the Sandcastle pipeline — for each, what was asked, what ran, and what it settled
---

# Experiment Log

The record of how the
[Sandcastle pipeline](/working-docs/delegation/sandcastle/pipeline.md) was
found. Each entry is closed; what it settled that still holds lives in the
pipeline and in the
[root](/working-docs/delegation/sandcastle/ROOT.md#constraints). The starting
point was the `sandbox-probe` branch, an earlier prototype that built and
measured a working podman container.

## The five problems

Pointed at the real repository, Sandcastle opens it into the container,
`.git` included, read-write. Five problems followed, each with one name:

| Problem | What went wrong | Closed by |
|---|---|---|
| **Shared history** | Worktrees share one `.git`, so a front could delete other branches and the user's unpushed commits, such as a worktree `issue-123` | Experiment two |
| **Relabel** | Podman's SELinux option permanently relabels the mounted host files, even through a read-only mount | Experiment two |
| **Booby trap** | A front plants a command in its copy's git settings that runs on the host when host-side git later works in the copy | The booby-trap fix |
| **Workspace collision** | Sandcastle puts the repository at `~/workspace` itself, so the repository is named `workspace` and dev-playbook has no place | Experiment three |
| **Hook logging** | The user's hooks must keep logging to the measurement database from inside a container | Part 4 |

## Experiment one: the clone round trip

**Asked.** Can a front's commits be made in a throwaway clone and reach the
real repository at the same SHA? No container and no driver, so a failure
would point at git alone.

**Ran.** [`front-clone`](/scripts/front-clone) against dev-playbook, with
`tests/dev_playbook/test_front_clone.py`.

**Settled.**

- Git refuses a push into a checked-out branch, so the real repository
  fetches from the clone instead, without force.
- A default local clone shared 318 object files with its source; with
  `--no-hardlinks` it shared none.
- The front's branch exists only in the clone until the commits arrive.
- A clone holding uncommitted work is refused and left on disk.

## Experiment two: Sandcastle against a copy

**Asked.** Does pointing Sandcastle at a throwaway copy keep the real
repository safe?

**Ran.** Sandcastle 0.12.0, its podman plug-in, `head` mode, against a
`front-clone` copy of a fake repository with an unpushed worktree
`issue-123`. A stand-in shell script replaced Claude: it made one commit,
then deleted every other ref and planted git hooks and a `core.fsmonitor`
command, each touching a marker file at a host-only path.

**Settled.**

- **Shared history** and **Relabel** closed: the real repository's refs,
  worktrees, settings, and labels were unchanged, `issue-123` survived,
  and only the copies were relabelled.
- The commit came back at the same SHA, and no container was left.
- **Workspace collision** confirmed: the repository's name came out
  `workspace`, and `~/workspace/dev-playbook` did not exist.
- **Booby trap** confirmed, and the cause was ours: the planted fsmonitor
  fired on the host when `front-clone close` ran `git status` in the copy.
- Not tested: Sandcastle's `branch` and `merge-to-head` modes.

## The booby-trap fix

**Asked.** Can `front-clone close` bring commits back without git ever
reading the copy's settings?

**Ran.** `front-clone close` rewritten to read the copy's origin as plain
text, fetch the commits from the real repository's side, and check for
uncommitted work under the real repository's own settings.
`tests/dev_playbook/test_front_clone_traps.py` plants a trigger at every
point git offers, all 28 hook names among them.

**Settled.** No trigger fires, on success or on a refused close. A control
proves the traps are live, and the old code fails the test. One edge was
accepted: a change staged in the copy and then deleted from its files goes
unnoticed.

## Experiment three: the plug-in

**Asked.** Can the **Workspace collision** close with no fork and no
standards change?

**Options.** A: change the standards to fit Sandcastle, moving dev-playbook
out of `~/workspace`. Rejected: the user runs code outside Sandcastle too,
so the change would reach beyond this set. B: a plug-in of our own that
moves the work copy. Sandcastle's suggested path reaches only the plug-in;
after start it works wherever the plug-in reports.

**Ran.** Option B, a 20-line wrapper around Sandcastle's podman plug-in,
with the stand-in, in three cases.

**Settled.**

- A front on mission-control: every check passed. The name came out
  `mission-control`, all eight `~/.claude/` links resolved, the config copy
  refused a write, the commit came back, and no trap fired.
- A front on dev-playbook with its work copy at `~/workspace/dev-playbook`:
  podman refused to start ("duplicate mount destination").
- The same front with its work copy under a separate folder: every check
  passed, with the two copies separate.
- The user then chose one layout for every front, work copy at
  `~/assignment/<repo>`.

## Part 4: real Claude

**Asked.** Does real Claude, on the subscription, work end to end through
Sandcastle and the plug-in?

**Ran.** Sonnet on a mission-control front: add one line to `README.md`,
commit, and name three skills.

**Settled.**

- Billing, config, and the commit's return passed at once: Claude reported
  `apiKeySource: none`, loaded 47 skills and 9 agents, and the commit came
  back at the same SHA.
- Hook logging logged start, prompt, and tool uses, but never Stop or
  SessionEnd. Those two hooks ran in the background and died when Claude
  exited. Setting them to wait fixed it.
- The run needed two dev-playbook changes, made only in the config copy:
  `measure-event` sending rows to the host, and the two end hooks waiting.
  They are kept as patches in
  [`rig/`](/working-docs/delegation/sandcastle/rig/index.md).
- The rig kept its copies under `/tmp/claude-1000/`, Claude's own
  temporary folder, which Sandcastle's extra mount made root-owned inside
  the container. The rig pointed Claude elsewhere with
  `CLAUDE_CODE_TMPDIR`.

## Fronts in parallel

**Asked.** Do two fronts run and close at once without interfering?

**Ran.** `rig/parallel.mjs`, two Haiku fronts on one fake repository,
started together and closed together.

**Settled.** Every check passed. The results are in
[Fronts in parallel](/working-docs/delegation/sandcastle/pipeline.md#fronts-in-parallel).

## Acronyms

- **SHA** — Secure Hash Algorithm; here, the ID of a git commit.
- **SELinux** — Security-Enhanced Linux.
