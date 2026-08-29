---
type: Survey
title: Sandbox measurement options
description: The options for carrying a sandboxed run's hook events into the host measurement store — what is rejected and why, and the one option left standing
---

# Sandbox measurement options

A sandboxed run's hook events never reach the host's measurement database. The
defect is described in
[Sandboxed headless Claude §7.1](/sandbox_probe/NOTES.md#71-the-events-database-is-created-fresh-and-thrown-away);
this document holds the options for fixing it.

**One option is left standing** — the post-run dump. One measured finding
removed its only serious rival on 2026-08-28: SELinux blocks the live handoff
the rival needed. What remains is a single test that decides whether the
survivor works at all.

## The problem in one paragraph

`dotfiles/dot-claude/hooks/measure-event` writes every hook event to
`$HOME/.local/share/claude-measure/events.db`. Inside the container `HOME` is
`/home/geoff`, and nothing is mounted there, so the hook creates a database in
the container's own filesystem, writes that run's events into it, and the file
dies when the container is removed. The hook does not fail and does not
complain — it self-bootstraps, creating the directory and the table on demand
(`measure-event:118`, `measure-event:42-51`), which is exactly the behaviour
that makes the loss silent.

The silence has a specific cause worth naming: the sandbox image is built on
Fedora, so `on_fedora()` (`measure-event:149-166`) — the guard that stops
capture on machines with no store — returns true inside the container. The hook
believes it is on the primary and records happily.

## What the answer has to do

1. **Every hook event from a sandboxed run reaches the host database.** Not
   necessarily while the run is in flight — eventually is enough.
2. **`measure-event` behaves the same inside the container as outside**, so a
   sandboxed run is measured like any other run, and there is no second
   definition of capture to drift.
3. **Nothing the agent could destroy is exposed to the container.** The mount
   list is the fence, and the rule that keeps it readable is
   [copies, never originals](/sandbox_probe/NOTES.md#mount-copies-never-originals).
4. **The factory's `ledger` table stays out of it.** `ledger` lives in the same
   file but is written only by `src/dev_playbook/factory/ledger.py`, which runs
   on the host. Nothing inside the container runs the factory, so nothing
   inside the container writes `ledger`.

## Where a change would go

Only one function in the hook touches SQLite: `record()`
(`measure-event:116-128`), thirteen lines. Everything above it — the timestamp,
the decode, the non-Bash trim, the promoted columns — is storage-agnostic. Any
option that changes how events are stored changes that one function and nothing
else.

The hook also refuses configuration on purpose: *no configuration: a hook runs
on every event of every session, so it may not depend on an interpreter's
package set or a knob* (`measure-event:22-23`). So an option may not add a
setting. It must either need no branch at all, or detect its own situation the
way `on_fedora()` already does.

## Rejected

### Mount the live store into the container

Give the container a window onto the real `~/.local/share/claude-measure/`
folder and let it write into the live database as it goes. One line of mount
list, and it works. Rejected because it puts the only copy of a 181 MB,
month-deep database inside the blast radius of a confused agent, and because
Fedora's file labelling would have to be changed on the live database file
itself to permit it (the `:Z` or `:z` mount suffix re-tags the host path). It
also has to be the whole folder, not the one file, because SQLite in this mode
writes two sidecar files next to the database.

### Copy the events out after the container exits

Let the run write to the container's own filesystem as it does today, then lift
the database out with `podman cp` before the container is removed. Rejected as
fragile: `--rm` deletes the container on exit, and a runner killed with
`SIGKILL` strands it
(see [§6.5](/sandbox_probe/NOTES.md#65-kill--9-on-the-runner-strands-the-container)),
so the one moment the copy has to happen is the moment least likely to arrive.

### Fold rows in continuously during the run

A host-side process tails the container's scratch database while the run is in
flight and inserts rows as they appear, so events land in near-real time.
Rejected: it adds a live process and a lifecycle to solve lateness, and the
reader constraints below make lateness acceptable instead.

### The guarded hole — a host writer the container hands events to

This was the leading option until it was tested. It is written up at length
because the reason it fails is not guessable, and re-deriving it costs another
experiment.

**The shape.** The container never touches the database. A small writer process
runs on the host, started just before the container and stopped just after. The
two talk over a socket file created in a throwaway folder and mounted in. The
protocol is one operation: *here is an event, store it.* The agent could only
ever append; it could not delete or corrupt anything, because it never sees the
file. Sandbox events would enter the real database live, in true order, with
row IDs from the same sequence as every other event — a future reader would
never need to know a sandbox existed.

**Why it does not work.** SELinux refuses the connection. Built and run on
2026-08-28 against the real `sandbox-probe` image with `--userns=keep-id` and a
`:Z` mount, the container's connect failed with `PermissionError: [Errno 13]
Permission denied`, and the audit log gave the reason:

```
AVC avc: denied { connectto } for comm="python3" path="/tmp/mprobe/measure.sock"
  scontext=system_u:system_r:container_t:s0:c107,c235
  tcontext=unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
  tclass=unix_stream_socket permissive=0
```

The re-tag worked perfectly — the socket file came out labelled
`container_file_t:s0:c107,c235`, matching the container — and it made no
difference. **For a socket, SELinux does not ask whether the container may
touch the file. It asks whether the container may talk to the listening
program.** Our writer would be an ordinary user process (`unconfined_t`), and a
container may not talk to those. No mount option changes this, because the
check is not about the mount.

Confirmed by elimination: the identical test with `--security-opt
label=disable` succeeded and the host received the event. That flag removes the
container's SELinux confinement wholesale, which is the protection the
copies-never-originals rule exists to preserve. The only other route is a
custom SELinux policy module installed as root, granting that permission to
*every* container on the machine. Both are disproportionate to the goal.

**The named-pipe variant, also rejected.** A named pipe (a FIFO) survives the
same test — verified working on 2026-08-28 with `:Z` and SELinux enforcing,
with no denial — because a pipe is a file object, so the mount re-tag grants
exactly the access needed and no program-to-program check happens. It is
rejected on its own merits rather than on security:

- **Events can shred each other.** A pipe guarantees an unbroken write only up
  to 4096 bytes (`PIPE_BUF`). In the live database **8.98% of payloads exceed
  that** — 6,618 of 73,736 rows, largest 84,457 bytes, 95th percentile 6,846
  bytes. Hooks are wired `"async": true`, so overlapping writers are normal.
  Fixable with a lock, but it is one more thing to get right.
- **It still needs the second program.** The pipe removes the security
  blocker, not the daemon, its lifecycle, or the question of what happens when
  it dies mid-run.
- **A missing reader is a hang.** Opening a FIFO for writing blocks forever
  with no reader attached. A non-blocking open fails immediately with `ENXIO`
  instead, so a fast-fail path exists — but it has to be written deliberately.

**One incidental constraint, recorded so it is not rediscovered.** Unix socket
paths are capped near 108 bytes; the first attempt died on `AF_UNIX path too
long` from an ordinary scratch path. Any future socket must live somewhere
short.

### One file per event in a mounted folder

Mount an empty throwaway folder; the hook writes one small file per event into
it and exits; the host folds the files in after the container is gone. No
daemon, no socket, no pipe — and none of the problems above.

Rejected because it is the post-run dump with a penalty. It is the same
"write locally, fold in later" shape, but it requires `record()` to branch on
whether it is in a sandbox, which is precisely the cost the post-run dump
avoids by leaving the hook untouched. It buys back nothing the post-run dump
has not already got.

It is worth remembering for one contingency only: if the open test below shows
SQLite cannot run correctly on a bind-mounted folder, this shape is the
fallback, because it needs no database inside the container at all.

## Still open

### The post-run dump — a scratch database folded in at the end

Mount an **empty** host folder where the database would live inside the
container. The hook finds nothing there, creates a database, and writes into
it for the length of the run — unchanged, because that is already what it does
on a fresh machine. When the run ends, host-side code copies the rows into the
real database and deletes the scratch one.

The fold-in is one statement, with `id` deliberately omitted so the host
assigns fresh row numbers:

```sql
INSERT INTO events (received_at, event, session_id, prompt_id, payload)
SELECT received_at, event, session_id, prompt_id, payload
FROM scratch.events ORDER BY id;
```

**What it gets right.**

- **`measure-event` does not change.** No branch, nothing sandbox-only, nothing
  that can rot. This is the main argument for it, and it is the one argument
  every rejected option above fails to match.
- **No original is mounted.** The copies rule holds, and the mount list stays
  readable by eye.
- **The merge runs on the host, as the user, and can fail loud** — unlike the
  hook, which is deliberately silent. If the fold-in fails, the rows are still
  sitting in a file and it can be retried.
- **Ownership works out.** Files the container writes through a mount come back
  owned by `geoff`, because the sandbox already remaps users
  ([§6.4](/sandbox_probe/NOTES.md#64-ownership-comes-back-right)).
- **It is cheap.** A 30-minute session is roughly 75–80 rows and ~110 KB, and
  the `events` table carries no indexes at all, so the insert is instant.

**What it costs.** Two properties, both of which the reader has to be built
around:

- **Row IDs are not arrival order.** A sandbox run at 10:00 folded in at 11:00
  gets IDs above rows that happened at 10:30. IDs already disagree with
  timestamps today — 67 inversions in 73,515 live rows, from concurrent
  sessions racing on the write — but those are under 20 milliseconds each,
  where this is hours, and systematic rather than accidental.
- **A computed result is never final.** Sandbox rows arrive late and dated
  earlier, so they can land inside a time window a report has already covered.
  A reader either never treats a window as closed, or recomputes from the whole
  table each time — practical at this size.

Interleaving order does **not** matter, which is what makes those two
acceptable. The two derivations in
[measurement-derivation.md](/docs/measurement-derivation.md) that need true
chronological order — hands-on minutes and waiting-on-user latency, both of
which look for *the latest Stop before this prompt* — are scoped **within a
single session**. A sandbox run is one session, and all of its rows sit in one
scratch database, so a clumped fold-in cannot disturb them.

**Do not build duplicate detection.** There is no natural unique key:
`(session_id, received_at, event)` already collides on two pairs of
legitimately distinct rows in the live database, because microsecond timestamp
ties happen (8 of them). A real key would mean hashing payloads, and the only
thing it protects against is a crash in the gap between the insert and the
delete of the scratch file — which would duplicate about eighty rows.

## Consequences to record either way

**Row IDs can be reused.** The `id` column is a plain row number
(`id INTEGER PRIMARY KEY`, no `AUTOINCREMENT`, and the hook never supplies it),
so SQLite assigns *one more than the largest currently in use* — meaning a
delete frees an ID for re-issue to a different row. A reader that stores ID
references is safe only as long as nothing ever prunes old events. This is
independent of the sandbox question, but it is exactly the assumption a future
reader would build on without checking.

**`ledger.py`'s docstring needs softening.** It states that *sequencing is by
`id` throughout: it is the only order the ledger guarantees*
(`src/dev_playbook/factory/ledger.py:61-62`). Under the post-run dump that
stops being true of the store as a whole, so the claim should be narrowed to
speak for the `ledger` table alone rather than for the file both tables share.

## What still needs finding out

**The test that decides it.** Does SQLite's write-ahead mode actually engage on
a bind-mounted folder? This is the one way the post-run dump could fail
outright. `ledger.py` refuses to run when that mode does not take, naming
container overlay mounts as the case where it fails (`_require_wal()`,
`ledger.py:343-364`); `measure-event` never checks, so a silent fallback to a
weaker mode would go unnoticed. If it engages, the post-run dump is the answer.
If it does not, the fallback is one file per event, above.

**Then, if it passes:**

- Does the host-side merge step read the scratch database cleanly given how the
  container creates it — owner, mode, and any leftover sidecar files.
- Two sandbox runs at once each get their own scratch folder, so there should
  be no contention. Confirm.
- Does the container's clock agree with the host's? The hook stamps UTC
  directly (`measure-event:184`), so a skewed container clock would produce
  syntactically valid but wrong timestamps.
