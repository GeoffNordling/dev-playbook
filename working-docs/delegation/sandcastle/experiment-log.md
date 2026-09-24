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
| **Shared history** | Worktrees share one `.git`, so an agent could delete other branches and the user's unpushed commits, such as a worktree `issue-123` | Experiment two |
| **Relabel** | Podman's SELinux option relabels the mounted host files ([Constraints](/working-docs/delegation/sandcastle/ROOT.md#constraints)) | Experiment two |
| **Booby trap** | An agent plants a command in its copy's git settings that runs on the host when host-side git later works in the copy | The booby-trap fix |
| **Workspace collision** | Sandcastle puts the repository at `~/workspace` itself, so the repository is named `workspace` and dev-playbook has no place | Experiment three |
| **Hook logging** | The user's hooks must keep logging to the measurement database from inside a container | Part 4 |

## Experiment one: the clone round trip

**Asked.** Can an agent's commits be made in a throwaway clone and reach the
real repository at the same SHA? No container and no driver, so a failure
would point at git alone.

**Ran.** [`front-clone`](/scripts/front-clone) against dev-playbook, with
`tests/dev_playbook/test_front_clone.py`.

**Settled.**

- Git refuses a push into a checked-out branch, so the real repository
  fetches from the clone instead.
- A default local clone shared 318 object files with its source; with
  `--no-hardlinks` it shared none.
- The round trip as it still runs is the Close step of
  [the pipeline](/working-docs/delegation/sandcastle/pipeline.md#the-run-start-to-finish).

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

- A run on mission-control: every check passed. The name came out
  `mission-control`, all eight `~/.claude/` links resolved, the config copy
  refused a write, the commit came back, and no trap fired.
- A run on dev-playbook with its work copy at `~/workspace/dev-playbook`:
  podman refused to start ("duplicate mount destination").
- The same run with its work copy under a separate folder: every check
  passed, with the two copies separate.
- The user then chose one layout for every run, work copy at
  `~/assignment/<repo>`.

## Part 4: real Claude

**Asked.** Does real Claude, on the subscription, work end to end through
Sandcastle and the plug-in?

**Ran.** Sonnet on a mission-control copy: add one line to `README.md`,
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

## Stints in parallel

**Asked.** Do two stints run and close at once without interfering?

**Ran.** `rig/parallel.mjs`, two Haiku stints on one fake repository,
started together and closed together.

**Settled.** Every check passed. The results are in
[Stints in parallel](/working-docs/delegation/sandcastle/pipeline.md#stints-in-parallel).
Re-run on 2026-09-24, after the set moved under delegation: every check
passed again.

## The container's lifetime

**Asked.** When one work copy takes two `run()` calls in turn, as the
iterations of a stint do, does anything but the work copy carry from the
first to the second? And does Sandcastle run git on the host in the copy
between calls, where the agent's planted triggers would fire?

**Ran.** Two stand-in scripts, no tokens, each test on a new `front-clone`
copy of the fake mission-control. `rig/lifetime.mjs`: call 1 commits, then
leaves a file in `~`, a file in `/tmp`, a global git setting, a background
process, and an uncommitted file in the repository; call 2 reports which it
sees. `rig/traps.mjs`: call 1 commits and plants every trigger of the
booby-trap test, each touching a marker in a folder only the host has; call
2 is an ordinary second call; then a control runs `git status` on the host.

**Settled.**

- Each call gets a new container, and only the work copy carries: the
  commit, and the uncommitted file too. Everything outside the work copy
  is gone. Sandcastle did not report the uncommitted file.
- In `head` mode, `run()` fires no trap on the host, in either call.
  Sandcastle counts the commits inside the container. The control fired
  two traps, so the traps were live.
- So the guess in the root holds: the copy opens once per stint, and each
  call gets a new container on it. A driver between calls must read the
  copy as plain files, never with host git, and must itself catch an
  iteration that left work uncommitted.

## The principal's conversation

**Asked.** Can the principal's conversation carry from one sealed call to
the next, each call in a new container, with its first call fresh?

**Ran.** `rig/resume.mjs`, Sonnet on a new copy of the fake
mission-control. Call 1, fresh, was told a magic word in its prompt only,
and told to write nothing. Call 2, in a new container, resumed call 1's
session and was asked the word. A control, a fresh session on the same
copy, was asked too. Sandcastle's own session capture kept the session
file in the stint's folder, through `claudeCode`'s `hostProjectsDir`.

**Settled.**

- Call 2 named the word, in call 1's session. The control answered that
  it had none, and no file in the copy held the word, so the word came
  through the conversation only.
- The session file sat in the stint's folder only. The user's
  `~/.claude/projects` gained nothing.
- So the principal can be one conversation across a stint, sealed at
  every call: Sandcastle's `resumeSession` on a session file the driver
  keeps with the stint.

## One unattended stint by hand

**Asked.** Does a whole stint work with every call sealed, the principal
one conversation across it, and a person in place of the driver? And
where does it hurt?

**Ran.** A `wordcount` workstream seeded into the fake mission-control
(`rig/seed/`): a head file, a plan of four tasks in two segments, and a
budget of five iterations. Every call was Sonnet, run through
`rig/call.mjs` with a prompt from `rig/prompts/`, and filled in by hand:
the principal's opening call, two iterations, a reviewer, the principal
resumed, three iterations, a reviewer, the principal resumed, then
`front-clone close`.

**Settled.**

- The stint ran to done in ten calls and about eleven minutes. The
  principal was one session across its three calls, each call billed to
  the subscription, no call left work uncommitted, and the branch came
  back at the same SHA with no container left.
- The review loop did its job. Running the check gate leaves Python's
  cache files, the fake repository had no `.gitignore`, and both
  iterations of segment 1 committed them. The reviewer ranked it the one
  finding; the principal accepted it and added a fix task, which the next
  iteration did.
- It hurt in four places:
  - **The judgment calls went unruled.** The iterations recorded two, and
    the principal ruled only on the reviewer's findings, so neither was
    ruled. The principal's prompt must rule on the judgment calls too.
  - **The budget had no slack.** Four tasks and five iterations; the fix
    task took the fifth, and a second finding would have ended the stint
    on budget.
  - **The seed lacked a `.gitignore`**, and the iteration prompt says
    `git add -A`. A real repository has one; the prompt should still
    commit only the files the task meant.
  - **The ending line is loose.** Agents wrapped the closing JSON line in
    backticks about half the time; the driver strips them.
- Sandcastle's token figures are the context size at the end of a call,
  not the tokens spent, so they cannot be a budget. They do show the
  principal's context growing: about 32,000 tokens at open, 42,000 at
  checkpoint 1, and 50,000 at checkpoint 2.
- The current Ralph iteration prompt cannot run sealed as it is: it
  commits through the `commit-sonnet` skill, which pushes. The stint's
  prompts commit with plain git and never push.

## The headless driver

**Question.** Can a script run the stint that ran by hand above, from
the principal's opening call to the yield, with no person in the loop?

**Method.** `rig/stint.py` runs the calls in order through `rig/call.mjs`
and applies the stop rules after each call. It reads the work copy as
plain files only, never with host git, and refuses a symlink on any path
it reads. `rig/rules.py` checks the stop rules with no tokens: a scripted
fake step plays every agent, and in each case one call misbehaves. Then
the driver ran live on new copies of the `wordcount` workstream, budget
6, with `--close`.

**Settled.**

- `rules.py` passes all 11 cases. Examples: a plan replaced by a link to
  a host file yields "symlink in the copy: ws/PLAN.md"; an iteration that
  checks off two tasks is noted, "iter-1 checked off 2 tasks, not 1", and
  the stint runs on to done.
- The driver counts the plan's unchecked task lines before and after each
  iteration, so it sees how many boxes were ticked, not how much work was
  done. The user ruled that a count other than 1 is a note, not a stop:
  the principal reads it with the iteration's summary, and `stint.json`
  lists it under `notes`.
- The driver no longer checks each call's billing. The user ruled that
  the proof above and the machine holding no API key are enough.
- Two live runs yielded at the principal's opening call, both for a
  correct reason:
  - Stint 2: the check gate left
    `tests/__pycache__/test_smoke.cpython-314.pyc` uncommitted. The seed
    now carries `rig/seed/gitignore`, copied in as `.gitignore`.
  - Stint 3: the principal put its JSON line inside a ```` ```json ````
    fence. The driver now skips fence lines when it finds the last line.
- Stint 4 ran to done in 9 calls, 4 of 6 iterations, and 9.3 minutes.
  The principal was one session (`b75a2913…`) across its three calls,
  every call billed `none`, and no call left work uncommitted. Both
  reviewers found 0 findings. `front-clone close` brought branch
  `stint-4` into the fake real repository at `cf70a75`, and no container
  was left.
- The driver had a second step, `claude -p` on the host. It was never
  run, and it read the copy with host git after an agent had touched it,
  so it is removed: every call runs sealed.
- The driver now refuses to launch a plan with more open tasks than the
  budget, for example "not launched: 4 tasks, budget 3", so a stint never
  starts that cannot finish.

## Acronyms

- **SHA** — Secure Hash Algorithm; here, the ID of a git commit.
- **SELinux** — Security-Enhanced Linux.
