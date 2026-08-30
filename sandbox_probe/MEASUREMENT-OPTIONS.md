---
type: Survey
title: Sandbox measurement options
description: How a sandboxed run's hook events will reach the host measurement store — the live TCP writer chosen for it, the post-run dump kept as fallback, and the rejected shapes
---

# Sandbox measurement options

A sandboxed run's hook events never reach the host's measurement database. The
defect is described in
[Sandboxed headless Claude §7.1](/sandbox_probe/NOTES.md#71-the-events-database-is-created-fresh-and-thrown-away);
this document holds the fix.

**The decision: a live TCP writer.** A small receiver on the host takes each
event over a TCP connection as the run produces it and inserts it into the real
database. The one fact the design rests on — that a program inside the
container can reach a listener on the host at all — was measured true on
2026-08-29 by `check-host-tcp`. This is the option being built. The post-run
dump stays on file as the fallback.

## The problem

`dotfiles/dot-claude/hooks/measure-event` writes every hook event to
`$HOME/.local/share/claude-measure/events.db`. Inside the container `HOME` is
`/home/geoff`, and nothing is mounted there, so the hook creates a database in
the container's own filesystem, writes that run's events into it, and the file
dies when the container is removed. The hook does not fail and does not
complain — it self-bootstraps, creating the directory and the table on demand
(`measure-event:118`, `measure-event:42-51`). It records because the
sandbox image is built on Fedora, so
`on_fedora()` (`measure-event:149-166`) — the guard that stops capture on
machines with no store — returns true inside the container.

## What the answer has to do

1. **Events from a sandboxed run land in the host database, live.** Losing a
   run's events to a rare failure is acceptable — this store feeds personal
   reports on a solo developer's machine. What is not
   acceptable is today's state, where every sandboxed run loses everything.
2. **No configuration.** The hook refuses knobs on purpose (*no configuration*,
   `measure-event:22-23`), so it may not gain a setting. It may detect its own
   situation, the way `on_fedora()` already does.
3. **Nothing the agent could destroy is exposed to the container.** The mount
   list controls what is exposed, following
   [copies, never originals](/sandbox_probe/NOTES.md#mount-copies-never-originals).
4. **The factory's `ledger` table stays out of it.** `ledger` lives in the same
   file but is written only by `src/dev_playbook/factory/ledger.py`, which runs
   on the host. Nothing inside the container writes it.

## The plan — a live TCP writer

**The shape.** Before the container starts, the launcher opens a listener
bound to the host's `127.0.0.1` on a free port, and starts the container with
`--network=pasta:--map-host-loopback=169.254.1.2` — inside the container, that
address means "the host's loopback", and nothing is opened to the LAN. A tiny
file mounted read-only at `~/.local/share/claude-measure/sink` carries the
port. When the run ends, the launcher closes the listener.

Inside the hook, only `record()` changes (`measure-event:116-128` — the one
function that touches SQLite; everything above it is storage-agnostic). It
checks for the sink file. Present — a sandboxed run — it sends the row it
would have inserted, as one JSON object over one short-lived TCP connection,
and exits. Absent — every ordinary host session — it writes SQLite exactly as
today. File-presence detection is the `on_fedora()` pattern.

The receiver inserts each row into the real `events.db` as the user, the
moment it arrives.

**Why TCP.** SELinux's block on container-to-host channels applies to unix
sockets, where it checks whether the container process may talk to the
listening *process* — a check no mount option touches. TCP has no such
process-to-process check; it is the same policy path the container already
uses to reach Anthropic on every billed run. An earlier attempt at this shape
(2026-08-28) used a unix socket and died on exactly that check —
`avc: denied { connectto }`, `container_t` to `unconfined_t` — which looked
like no route existed to the host. The named-pipe variant tried next passes
SELinux but shreds concurrent payloads over 4096 bytes (8.98% of live rows are
bigger) and still needs the receiver, so nothing about it beats TCP.

**Proven.** `python3 -m probe check-host-tcp`, 2026-08-29: through the real
image, with the real run flags (`--userns=keep-id`), SELinux Enforcing, a
message sent from inside the container arrived intact at a listener bound to
the host's `127.0.0.1`. No AVC denials.

**What it gets right.**

- **Events land live, in true order.** Row IDs come from the same sequence as
  every other session, no reader ever handles late rows, and the
  WAL-on-bind-mount question the post-run dump hangs on never needs answering.
- **No original is mounted** — no store is mounted at all, only the
  one-line sink file, generated fresh per run.
- **No new daemon.** The receiver is a thread in the launcher, a process that
  already owns the run's lifetime.
- **The failure mode is the accepted one.** Receiver gone — launcher killed,
  container stranded per
  [§6.5](/sandbox_probe/NOTES.md#65-kill--9-on-the-runner-strands-the-container)
  — means the connect fails fast and the event is dropped. Rare, bounded, and
  accepted by requirement 1.

**What it costs.**

- `record()` grows a branch — the one cost the post-run dump avoids. It is
  confined to that one function, and the host path through it is untouched.
- Dropped events when the receiver is absent, accepted above.

**To settle while building.**

- A short connect timeout, so a hook can never hang a session; on timeout,
  drop.
- Hooks run `"async": true`, so overlapping connections are normal. The
  receiver accepts concurrently and serializes its SQLite inserts.
- The receiver's insert must write exactly the columns `record()` writes —
  `received_at`, `event`, `session_id`, `prompt_id`, `payload` and the
  promoted columns — so keep the two definitions visibly adjacent.
- The hook stamps UTC itself (`measure-event:184`); confirm the container's
  clock agrees with the host's.

## The fallback — the post-run dump

Kept on file in case the writer disappoints in practice. Mount an **empty**
host folder where the database would live inside the container; the hook,
unchanged, self-bootstraps a scratch database there and fills it for the length
of the run; when the run ends, the host copies the rows into the real database
with fresh IDs and deletes the scratch:

```sql
INSERT INTO events (received_at, event, session_id, prompt_id, payload)
SELECT received_at, event, session_id, prompt_id, payload
FROM scratch.events ORDER BY id;
```

Its virtue is that `measure-event` does not change at all. Its costs are why it
is the fallback rather than the plan: row IDs stop being arrival order (a run
folded in at 11:00 sits above rows from 10:30), a computed report window is
never final, and `ledger.py`'s claim that *sequencing is by `id` throughout*
(`ledger.py:61-62`) would need narrowing to the `ledger` table. One question
was never answered: whether SQLite's write-ahead mode engages on a
bind-mounted folder — `_require_wal()` (`ledger.py:343-364`) names container
mounts as where it fails, and the hook never checks. If the fallback is ever
built: skip duplicate detection — `(session_id, received_at, event)` collides
on legitimately distinct rows (8 microsecond-tie pairs in the live database),
and a real key buys almost nothing.

## Rejected

- **Mount the live store into the container.** Puts the only copy of a 181 MB
  database within the container's reach, and the `:Z` retag lands on the live file.
- **Copy the events out after the container exits.** `podman cp` has one
  moment to run, and a SIGKILL'd runner is exactly the case where that moment
  never comes.
- **Fold rows in continuously during the run.** A live host process added
  only to fix lateness.
- **One file per event in a mounted folder.** The post-run dump with a hook
  branch added and nothing bought. Worth remembering only if scratch SQLite
  cannot run on a bind mount at all.
- **A unix-socket or named-pipe writer.** The same shape as the plan over a
  worse channel; see *Why TCP* above.

## Recorded either way

**Row IDs can be reused.** `id` is a plain row number
(`id INTEGER PRIMARY KEY`, no `AUTOINCREMENT`), so SQLite assigns one more
than the largest currently in use — a delete frees an ID for re-issue. A
reader that stores ID references is safe only as long as nothing ever prunes
old events. Independent of the sandbox question, and exactly the assumption a
future reader would build on without checking.
