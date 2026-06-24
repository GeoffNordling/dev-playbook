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

- **Internet:** neither tool gives clean, *scoped* egress control on a
  subscription daily driver. Native `/sandbox`'s `allowedDomains` is a
  **prompt-skip list, not a deny** — non-listed domains fall back to the
  permission flow, which auto-allows under bypass mode, so in practice it blocks
  nothing. Real zero-egress exists only via `allowManagedDomainsOnly` in
  root-owned **managed settings** — machine-wide, and it breaks everyday
  `gh`/`git`/`uv`. Sandcastle ships no allowlist at all; its only lever is
  all-or-nothing `--network none`, which also kills Claude's auth.
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
- Verified: a configured `denyRead` makes the path *vanish* inside the sandbox
  (bubblewrap overlays an empty dir), so credentials are genuinely masked, not
  just permission-denied; a write outside the allow-list fails as read-only. The
  read-deny was confirmed in a background `claude agents` fleet terminal too, so
  the fence is not foreground-only.

**Network — weak control (the trap):**

- Traffic *is* routed through a proxy, but `allowedDomains` in user/project
  settings is a **prompt-skip list, not a deny**. Non-listed domains aren't
  blocked — they fall back to the regular permission flow, and under
  bypass / skip-prompt mode (how we run) that fallback auto-approves, so **every
  domain passes**. Verified live: three non-listed hosts all returned 200.
- Hard deny — blocking non-listed domains *without* a prompt — requires
  `allowManagedDomainsOnly: true`, honored **only** in root-owned managed
  settings (`/etc/claude-code/managed-settings.json`), never user/project/local.
  That's machine-wide and blocks `gh`/`git`/`uv` too. There is no per-session or
  user-settings zero-egress switch.
- Claude's own model API is not a shell subprocess, so none of this affects auth.

**Caveat:** because it covers only the shell, running unattended with
permissions skipped leaves the file tools unbounded. The native sandbox is a
boundary for shell commands and the network, not a safe jail for hands-off file
editing.

### Config-file phantoms (undocumented)

Turning the sandbox on makes a set of config dotfiles — shell-init, git, editor,
and Claude/tool config (`.bashrc`, `.gitconfig`, `.mcp.json`, `.claude/`, …) —
appear inside it as empty **"phantoms"**: each reads back empty and shows up in
`ls`/`git status` as a `/dev/null` character device owned by `nobody`. They exist
only while the sandbox is on, are driven by no setting, and are undocumented by
Anthropic — distinct from the deliberate `denyRead` masking above (which overlays
an empty dir, not a device node).

**Hypothesis:** a built-in credential/tamper guard — Claude Code blanks these by
default so a sandboxed shell can't read secrets from tool config or be steered by
attacker-planted shell-init, layered under the sandbox independent of the user
`denyRead` list.

The practical cost is context pollution: `git add -A` aborts on the device nodes
and a plain `git status` lists them as untracked noise. The
[commit skill](~/workspace/dev-playbook/dotfiles/dot-claude/skills/commit/SKILL.md)
sidesteps both — staging with `git add --ignore-errors` and inspecting with
`git status -uno` — so the phantoms never reach the agent's context.

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

**Operating it interactively — the per-session cost:**

Launching the TUI on subscription billing works, but each session carries setup
and recurring friction, because the container is ephemeral and starts bare:

- **The token doesn't suppress login.** `CLAUDE_CODE_OAUTH_TOKEN` (from `claude
  setup-token`) reaches the container, but the interactive TUI ignores it for
  auth and runs its own browser sign-in. Inside a container there's no browser,
  so you finish it by hand (open a URL on the host), and a fresh container
  forgets it — so it re-prompts every launch.
- **Persistence is manual.** To sign in once instead of every time, mount a
  dedicated persistent dir as the container's `~/.claude` so credentials survive
  teardown. It must be a *separate* dir — never the host's real `~/.claude`,
  whose `.credentials.json` would then be exposed to the open-network sandbox.
- **Your setup isn't there.** The container has none of your global skills,
  rules, or settings (they live in the unmounted host `~/.claude`). You stage in
  what you want, and must pin the theme to match your terminal — the default
  auto-detect misrenders illegibly in a container TTY.

Net: complete filesystem isolation, paid for with a container build plus a
re-login-and-restage ritual around each session. Worth it to run genuinely
untrusted code; heavy for everyday work.

## What's achievable under interactive subscription billing

| Capability | Native `/sandbox` | Sandcastle `interactive()` | Sandcastle `run()` (headless) |
|---|---|---|---|
| Durable on subscription | ✅ interactive | ✅ interactive (one session/terminal) | ❌ headless — not durable |
| Filesystem control | ⚠️ partial — shell only; reads all by default | ✅ complete — every tool, mounts only | (headless) |
| Network egress control | ⚠️ allowlist is prompt-skip only; hard deny needs root, machine-wide managed settings | ❌ none — full outbound | ❌ none |
| Safe unattended (skip permissions) | ❌ file tools unbounded | ✅ container bounds all tools | ✅ (but headless) |
| Multi-agent orchestration / AFK | ❌ | ❌ single session | ✅ — its purpose |
| Remote/cloud execution | ❌ local only | ✅ | ✅ |
| Isolation strength (untrusted code) | ⚠️ OS sandbox, weaker than a container | ✅ real container | ✅ |
| Setup cost | low | high — image build + re-login/restage each launch | high |

**For interactive subscription use:** Sandcastle's real strengths —
orchestration, AFK fan-out, safe unattended runs — sit in the headless column
that durability rules out. What's left splits into a filesystem story and a
network story. For **filesystem** isolation, native `/sandbox` is the cheap,
verified win — credentials masked, enforced across every session and agent. For
**zero network egress**, neither tool is a clean fit on a subscription: native
can only do it machine-wide via root managed settings (breaking everyday
tooling), and Sandcastle can only do all-or-nothing that kills auth. So use
native `/sandbox` for filesystem isolation everywhere, and treat genuine
zero-egress as the *container* case for a specific untrusted run — not a global.

## Our setup and decisions

- **Native `/sandbox` is enabled globally** (`sandbox.enabled` in user
  settings), and we treat it as applying to *every* agent — foreground TUI,
  in-process subagents, and the background `claude agents` fleet alike.
- **We use it for filesystem isolation only.** Writes are fenced to `~/workspace`
  plus tool caches (`~/.cache`, `~/.local`, `~/.npm`); reads are denied on
  `~/.ssh`, `~/.aws`, `~/.gnupg`, `~/.netrc`. Verified and OS-enforced — this is
  the part that actually guards credentials. (It bounds *shell* commands; the
  agent's own file tools still ride the permission system.)
- **We do not configure network control.** The `allowedDomains` allowlist is a
  prompt-skip list that collapses to allow-all under our bypass mode, and the
  only real deny is machine-wide root managed settings that would break daily
  tooling. We left it out rather than imply a protection we don't have.
- **Zero egress is a per-run container decision, never a global.** To run code
  we don't trust with no network, we isolate that one run in a container.

## Context: the native `claude agents` fleet

`claude agents` runs many background `claude` sessions, each its own process with
its own git worktree, on your subscription. Each reads settings from its
directory the same as a fresh `claude`, so a global `sandbox` block applies to
them too — **confirmed**: a fleet terminal could not read `~/.ssh` once the
filesystem deny was set. We therefore treat the sandbox as covering every agent.
The network gap reaches them too: with no hard deny available, fleet sessions
have unrestricted egress just like the foreground.
