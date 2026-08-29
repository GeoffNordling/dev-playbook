---
type: Survey
title: Sandbox measurement options
description: The options for carrying a sandboxed run's hook events into the host measurement store — what is rejected, and what the two live options still need
---

# Sandbox measurement options

A sandboxed run's hook events never reach the host's measurement database. The
defect is described in
[Sandboxed headless Claude §7.1](/sandbox_probe/NOTES.md#71-the-events-database-is-created-fresh-and-thrown-away);
this document holds the options for fixing it.

**Undecided.** Two options are still live and need more investigation before a
choice is made. The rest are recorded so they are not re-argued.

## The problem in one paragraph

`dotfiles/dot-claude/hooks/measure-event` writes every hook event to
`$HOME/.local/share/claude-measure/events.db`. Inside the container `HOME` is
`/home/geoff`, and nothing is mounted there, so the hook creates a database in
the container's own filesystem, writes that run's events into it, and the file
dies when the container is removed. The hook does not fail and does not
complain — it self-bootstraps, creating the directory and the table on demand
(`measure-event:118`, `measure-event:42-51`), which is exactly the behaviour
that makes the loss silent.

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

## Rejected

**Mount the live store into the container.** Give the container a window onto
the real `~/.local/share/claude-measure/` folder and let it write into the live
database as it goes. One line of mount list, and it works. Rejected because it
puts the only copy of a 181 MB, month-deep database inside the blast radius of
a confused agent, and because Fedora's file labelling would have to be changed
on the live database file itself to permit it (the `:Z` or `:z` mount suffix
re-tags the host path). It also has to be the whole folder, not the one file,
because SQLite in this mode writes two sidecar files next to the database.

**Copy the events out after the container exits.** Let the run write to the
container's own filesystem as it does today, then lift the database out with
`podman cp` before the container is removed. Rejected as fragile: `--rm`
deletes the container on exit, and a runner killed with `SIGKILL` strands it
(see [§6.5](/sandbox_probe/NOTES.md#65-kill--9-on-the-runner-strands-the-container)),
so the one moment the copy has to happen is the moment least likely to arrive.

**Fold rows in continuously during the run.** A host-side process tails the
container's scratch database while the run is in flight and inserts rows as
they appear, so events land in near-real time. Rejected: it adds a live process
and a lifecycle to solve lateness, and the reader constraints below make
lateness acceptable instead.

## Still open

### The guarded hole — a host writer the container hands events to

The container never touches the database. A small writer process runs on the
host, started just before the container and stopped just after — the same
lifecycle the container already has, no always-on service. The two talk over a
socket file that we create in a throwaway folder and mount in. The protocol is
one operation: *here is an event, store it.* No reads, no queries, no
authentication — being on the other end of the socket is the authorization.

**What it gets right.**

- The agent can only ever append an event. It cannot delete or corrupt the
  database, because it never sees the file.
- Nothing real is re-tagged. The only host file the container touches is a
  socket we made for this run and throw away after, exactly like the credential
  copy today.
- **Sandbox events are indistinguishable from host events.** They enter the
  real database live, in true order, with row IDs from the same sequence as
  everything else. A future reader never has to know a sandbox exists.

**What it costs.**

- **`measure-event` has to change.** Today the hook opens SQLite directly, and
  it is the same code on the host and in the sandbox — which is what makes a
  sandboxed run trustworthy as a measurement. Talking to a socket means a
  second code path, and it is the path that never runs on the host, so it is
  the one that rots unnoticed. This is the main objection.
- **A second program has to be right.** What happens when the writer dies
  mid-run, when the container outruns it, when the container is killed with a
  message half-written.
- **The data has a moment where it is nowhere durable.** If the writer dies,
  events go into a socket with nobody listening, and `measure-event` swallows
  its own failures and exits 0 by design (`measure-event:16-20`) — so they
  vanish with nothing said. At this scale that is a shrug, not a
  disqualification, but it is the opposite failure mode from the other option,
  where the data sits on disk waiting.

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
  that can rot. This is the main argument for it.
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

**For the guarded hole:**

- How small can the change to `measure-event` actually be — is there a shape
  where the socket path is also exercised on the host, so it cannot rot
  unnoticed?
- Does mounting a socket into the container really avoid re-tagging anything
  real? Believed yes, untested.
- What the writer process does when the container outruns it or when it dies
  mid-run.

**For the post-run dump:**

- Does SQLite's write-ahead mode actually engage on a bind-mounted folder?
  `ledger.py` refuses to run when it does not, naming container overlay mounts
  as the case where it fails; `measure-event` never checks, so a silent
  fallback would go unnoticed.
- Does the host-side merge step read the scratch database cleanly given how the
  container creates it — owner, mode, and any leftover sidecar files.
- Two sandbox runs at once each get their own scratch folder, so there should
  be no contention. Confirm.

**For both:**

- Does the container's clock agree with the host's? The hook stamps UTC
  directly (`measure-event:184`), so a skewed container clock would produce
  syntactically valid but wrong timestamps.
