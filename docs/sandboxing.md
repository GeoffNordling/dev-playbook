# Sandboxing Claude agents

What two tools — Anthropic's **native sandbox** (`/sandbox`) and Matt Pocock's
**Sandcastle** — actually do to isolate a Claude agent's filesystem, network,
and process, and which of those capabilities survive **interactive subscription
billing**.

Functional summary as of 2026-06-23, from Anthropic's
[sandboxing](https://code.claude.com/docs/en/sandboxing) and
[agent view](https://code.claude.com/docs/en/agent-view) docs and a read of the
Sandcastle source.

## The two asymmetries that matter

- **Internet:** native `/sandbox` **can** restrict or fully block outbound
  access (a domain allowlist). Sandcastle **cannot** — its container has full
  outbound and ships no allowlist; the only lever is all-or-nothing
  `--network none`, which also kills Claude's auth.
- **Filesystem:** native `/sandbox` restricts **partially** — it bounds only
  shell commands (and even then reads the whole disk by default), while the
  agent's own file tools stay on the permission system. Sandcastle restricts
  **completely** — the entire `claude` process runs in the container, so every
  tool can see only the mounted paths.

## The billing constraint (why interactive-only)

Subscription billing is durable **only for interactive (TUI) use**. Anthropic
announced moving headless/programmatic usage (`claude -p`, Agent SDK) off
subscription onto a separate credit, then **paused that change on 2026-06-15** —
deferred, not cancelled. So any capability that depends on headless / AFK /
programmatic operation is **not durable** on a subscription; only interactive
sessions are. Availability below is judged against that line.

## Native sandbox (`/sandbox`)

**Scope: it sandboxes shell (Bash) commands and their subprocesses only.** The
agent's Read / Edit / Write / WebFetch tools are governed by the permission
system, not the sandbox. No container — it restricts the real host environment
using OS primitives (Linux: `bubblewrap` + `socat`; macOS: Seatbelt; on Fedora,
`sudo dnf install bubblewrap socat`). Opt-in, off by default; enable per-session
with `/sandbox` or globally via `sandbox.enabled` in settings.

**Filesystem — partial control:**

- Default **write**: working directory + temp dir only.
- Default **read**: the *entire disk*, including `~/.ssh` and
  `~/.aws/credentials`. Not blocked unless you add them to a deny list.
- Configurable allow/deny for read and write, OS-enforced down to child
  processes — but only for shell commands.

**Network — real control:**

- A proxy enforces a **domain allowlist**: nothing is allowed by default, new
  domains prompt, and you can block everything. Restricts shell-command egress.
- Filters on hostname only (no TLS inspection), so broad allows are still
  exfiltration paths. Claude's own model API is not a shell subprocess, so
  blocking egress does not break auth.

**Caveat:** because it covers only the shell, running unattended with
permissions skipped leaves the file tools unbounded. The native sandbox is a
boundary for shell commands and the network, not a safe jail for hands-off file
editing.

## Sandcastle

An **AFK multi-agent orchestration framework** that uses containers for
isolation — the container is a means, the orchestration is the product. Two
modes: `interactive()` runs a single `claude` TUI session; `run()` runs headless
fan-out. Sandbox backends: Docker, Podman, Vercel (remote), or none. It cannot
wrap the native `claude agents` fleet — `interactive()` only ever launches one
plain `claude` session.

**Container — complete isolation:**

- One container per session, built from a Dockerfile. The **whole `claude`
  process runs inside it**, so *every* tool (file tools and shell alike) is
  bounded by the container's mounts. This is what makes unattended,
  permission-skipped runs safe inside it.
- You can run several at once — one `interactive()` per terminal — each its own
  container and worktree, but with no unified dashboard.

**Filesystem — complete control:**

- Mounted in by default: only the worktree and its git directory. Host config
  dirs (`~/.ssh`, `~/.aws`, `~/.claude`) are **not** mounted, so they don't
  exist inside the container. Add mounts to widen; the mount list *is* the
  boundary.

**Network — no control:**

- Full outbound internet by default. No allowlist, proxy, or firewall ships.
  The only option is turning networking off entirely, which also breaks Claude's
  auth. Limiting egress means building it yourself around the container.

## What's achievable under interactive subscription billing

| Capability | Native `/sandbox` | Sandcastle `interactive()` | Sandcastle `run()` (headless) |
|---|---|---|---|
| Durable on subscription | ✅ interactive | ✅ interactive (one session/terminal) | ❌ headless — not durable |
| Filesystem control | ⚠️ partial — shell only; reads all by default | ✅ complete — every tool, mounts only | (headless) |
| Network egress control | ✅ allowlist; can block all | ❌ none — full outbound | ❌ none |
| Safe unattended (skip permissions) | ❌ file tools unbounded | ✅ container bounds all tools | ✅ (but headless) |
| Multi-agent orchestration / AFK | ❌ | ❌ single session | ✅ — its purpose |
| Remote/cloud execution | ❌ local only | ✅ | ✅ |
| Isolation strength (untrusted code) | ⚠️ OS sandbox, weaker than a container | ✅ real container | ✅ |
| Setup cost | low | high (Docker + image) | high |

**For interactive subscription use:** Sandcastle's real strengths —
orchestration, AFK fan-out, safe unattended runs — sit in the headless column
that durability rules out. Its remaining interactive edge is *complete*
filesystem isolation. But the capability most often wanted, **limiting the
internet**, is the one row Sandcastle can't do and native `/sandbox` can. So for
isolating *interactive* subscription sessions, native `/sandbox` is the direct
fit; reach for Sandcastle only when you need container-grade isolation of
untrusted code — and even then you must add network control yourself.

## Context: the native `claude agents` fleet

`claude agents` runs many background `claude` sessions, each its own process with
its own git worktree, on your subscription. By default they have **unrestricted
filesystem and network access**. Native `/sandbox` is the opt-in boundary;
whether a fleet/background session inherits it (vs. a confirmed in-process
subagent) is unverified — confirm with a live test before relying on it.
