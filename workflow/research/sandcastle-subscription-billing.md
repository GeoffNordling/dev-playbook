# Sandcastle + Claude Subscription Billing — Investigation Handoff

This document is for a future fresh agent who will re-investigate the question
below. It records the goal, the evidence found, and the methods used. It
deliberately avoids strong conclusions — verify everything yourself.

## 1. Goal and intent

The user wants to use [Sandcastle](https://github.com/mattpocock/sandcastle)
**only** while authenticated against their Claude (Max/Pro) **subscription** —
never an `ANTHROPIC_API_KEY`. Two modes are acceptable:

- **Interactive TUI** in a sandboxed environment (preferred, definitely on the
  table).
- **Fully headless** (`sandcastle.run()`, which invokes `claude --print`)
  (nice-to-have if it works on subscription without prohibitive rate limits).

What is **not** in scope:
- Driving sandcastle from within an already-open Claude Code interactive
  session. The user understands sandcastle launches *its own* `claude`
  subprocesses; their concern is only the billing/auth axis.
- Anything using `ANTHROPIC_API_KEY`. API billing is off the table for cost
  reasons.

## 2. The conceptual map

It is easy to conflate two orthogonal axes. Do not. Sandcastle exposes both
combinations on the right-hand column:

```
                      AUTH (who pays)
                      ───────────────────────────────────────
                      ANTHROPIC_API_KEY        CLAUDE_CODE_OAUTH_TOKEN
                      (API billing)            (subscription billing)
                      ───────────────────────────────────────
MODE   interactive    API + TUI                Sub + TUI
       (claude TUI)                            ← in scope
       ───────────────────────────────────────
       headless       API + headless           Sub + headless
       (claude -p)                             ← in scope (nice-to-have)
                                               ← also where #191 complaints live
```

`claude -p` is a CLI **mode** flag (headless / print mode). `CLAUDE_CODE_OAUTH_TOKEN`
is an **auth** env var (subscription token, minted by `claude setup-token`).
They combine freely.

## 3. Pinned source for code references

All `github.com/mattpocock/sandcastle/blob/...` permalinks in this document
point to the SHA below. The repo will change; a fresh agent should re-clone
and verify line numbers still match, or update against a newer SHA.

- **Sandcastle HEAD at time of investigation**:
  `89325e4d5a10ea6b1d2aaef755e803145efa30b5`
  - Commit subject: "Merge pull request #744 from mattpocock/changeset-release/main"
  - Date: 2026-05-27
  - Branch: `main`

## 4. Evidence inventory

### 4.1 Issue #191 — "Possible to use Claude subscription instead of ANTHROPIC_API_KEY?"

- URL: https://github.com/mattpocock/sandcastle/issues/191
- State at time of investigation: **OPEN**, label **`wontfix`**, 20 comments,
  thread has been locked and re-unlocked once.
- Reading the comments end-to-end is essential. Highlights (paraphrasing —
  fetch the live thread for verbatim):
  - **Matt Pocock (owner)**: "I've been waiting since March 15th on a response
    on legality of recommending this from Anthropic. … Their position is
    extraordinarily infuriating." Followed by: *"Anthropic publicly documents
    how to do this in Claude Code itself, via `claude setup-token` and
    `CLAUDE_CODE_OAUTH_TOKEN`. I can't legally recommend you use it. But you
    are able to do it."* This is the central quote: **the maintainer
    confirms it works but will not formally recommend it.**
  - **Matt, later update**: links to Anthropic's June-15 plan-usage
    clarification (see §4.2 below). Says the clarification "is, effectively,
    a cut — but at least one which clarifies the terms and allows me to offer
    clear guidance here."
  - **Bedrock works** (confirmed by Matt): "we pass through all .env
    variables so just use the standard ones to connect CC with Bedrock."
  - **Post-June-15 rate-limit reports** in the thread (treat as anecdotal):
    - `rcfrias`: `AgentError: claude-code exited with code 1: You're out of
      extra usage · resets 4:20am (UTC)` — this is a **subscription**
      rate-limit error message, so the reporter was in the
      sub-auth + headless-mode cell.
    - `vi-vlasov`: "if you use claude -p, the limits run out at the speed of
      light."
    - `plainlystated`: reads Anthropic's announcement as "more about locking
      down `claude -p`."
  - User base for this issue is two-digit "thumbs up"-class. Worth fetching
    fresh reactions to gauge whether the audience grew.

Method to re-fetch:

```bash
gh issue view 191 --repo mattpocock/sandcastle --comments
```

### 4.2 Anthropic's June-15 clarification on plan-usage of the Agent SDK

- URL: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
- **A fresh agent must read this themselves before drawing conclusions.** It is
  the load-bearing document for whether the user's intended use (subscription-
  only) is policy-compliant in their use case. The investigator did not paste
  it into this document because Anthropic could update it; always read the
  live page.

### 4.3 Matt dogfoods subscription auth on his own project — including headless

The smoking gun. Sandcastle's own automation, checked into the repo, uses
`CLAUDE_CODE_OAUTH_TOKEN` and `sandcastle.run()` (the headless path):

- **The factory that requires the OAuth token**:
  - File: `.sandcastle/agent-workflows/shared/common.ts`
  - Lines 55–60:
    ```ts
    export const claudeAgent = () =>
      sandcastle.claudeCode("claude-opus-4-7", {
        env: {
          CLAUDE_CODE_OAUTH_TOKEN: required("CLAUDE_CODE_OAUTH_TOKEN"),
        },
      });
    ```
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/.sandcastle/agent-workflows/shared/common.ts#L55-L60

- **Every consumer of `claudeAgent()`** — all are `sandcastle.run()` calls
  (headless, `claude -p`):
  - `.sandcastle/agent-workflows/implement/implement.ts:15` — `sandcastle.run({ agent: claudeAgent(), sandbox: noSandbox(), ... })`
    - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/.sandcastle/agent-workflows/implement/implement.ts#L15
  - `.sandcastle/agent-workflows/review/review.ts:29`
  - `.sandcastle/agent-workflows/explore/explore.ts:38`
  - `.sandcastle/agent-workflows/implement-pr/implement-pr.ts:28`
  - `.sandcastle/agent-workflows/update-branch/update-branch.ts:69`
  - Search command:
    `grep -rn "claudeAgent\|sandcastle\.\(run\|interactive\)" .sandcastle --include='*.ts'`

- Interpretation hint (verify independently): if Matt is using subscription
  auth + headless + `noSandbox()` in his own production workflows, then the
  technical path is unambiguously functional. The remaining axis is policy /
  rate limits, not "does it work."

### 4.4 ADR 0015 — subscription users are an acknowledged user segment

- File: `docs/adr/0015-no-sandbox-in-run-and-create-sandbox.md`
- Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/docs/adr/0015-no-sandbox-in-run-and-create-sandbox.md
- Key sentence (verbatim from the source at this SHA):
  > "In practice, subscription-billed Claude users (and anyone running
  > Sandcastle inside an already-isolated environment — containerized CI, VM,
  > sandbox host) had no path to AFK orchestration. The workaround was to fork
  > `noSandbox` and flip the type tag, which every such user re-invented. With
  > the API-key-only sandbox path tracked in #191 marked wontfix, the
  > type-level gate was forcing a workaround rather than preventing a mistake."
- The ADR's decision: allow `noSandbox()` in `run()` and `createSandbox()` so
  subscription users have a first-class headless path.

### 4.5 Code paths verified

The cells the user cares about correspond to specific source paths. A fresh
agent should re-read each to verify the path is unchanged.

- **Claude Code agent provider** — both modes wired:
  - File: `src/AgentProvider.ts`, lines 822–907
  - `buildPrintCommand` (headless, used by `run()`): lines 844–860, generates
    `claude --print --verbose [--dangerously-skip-permissions] --output-format
    stream-json --model <model> [--effort <e>] [--resume <id>] -p -` and pipes
    the prompt over stdin.
  - `buildInteractiveArgs` (TUI, used by `interactive()`): lines 862–872,
    generates `claude [--dangerously-skip-permissions] --model <model>
    [--effort <e>] [prompt]`. **No `-p`.**
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/src/AgentProvider.ts#L822-L907

- **Interactive launch flow** — real TTY into the container:
  - File: `src/interactive.ts`, lines 386–401
  - Calls `interactiveExecFn(interactiveArgs, { stdin: process.stdin, stdout:
    process.stdout, stderr: process.stderr, ... })`, attaching the host's real
    streams.
  - Note line 388: `dangerouslySkipPermissions: sandboxProvider.tag !== "none"`
    — so a real container (Docker/Podman/Vercel) gets `--dangerously-skip-permissions`
    appended; `noSandbox()` does not.
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/src/interactive.ts#L386-L401

- **Docker provider TTY allocation**:
  - File: `src/sandboxes/docker.ts`, lines 322–352
  - When `opts.stdin.isTTY` is true, the provider emits `docker exec -it`;
    otherwise `docker exec -i`. The `-it` path is what gives the Claude TUI
    a real pseudo-terminal inside the container.
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/src/sandboxes/docker.ts#L322-L352

- **Docker env passthrough**:
  - File: `src/sandboxes/docker.ts`, lines 180–199
  - `startContainer(containerName, imageName, { ...createOptions.env, HOME:
    "/home/agent" }, { ... })` — every resolved env var (from
    `.sandcastle/.env` + agent provider env + sandbox provider env) is
    forwarded into the container as `docker run --env`. So a token set via
    `claudeCode({ env: { CLAUDE_CODE_OAUTH_TOKEN: ... } })` reaches the
    container's `claude` process.
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/src/sandboxes/docker.ts#L180-L199

- **Docker user mounts** (could bind-mount host `~/.claude` if desired):
  - File: `src/sandboxes/docker.ts`, lines 137–145 and 162–167
  - `options.mounts` accepts arbitrary host-path → sandbox-path bind mounts.
    An alternate auth approach (not tested in this investigation) is to mount
    the host's `~/.claude` into the container's `/home/agent/.claude` instead
    of (or in addition to) using `CLAUDE_CODE_OAUTH_TOKEN`. A fresh agent
    should evaluate this if the token route hits problems.

- **EnvResolver gotcha — keys must be declared**:
  - File: `src/EnvResolver.ts`, lines 56–73
  - Permalink: https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/src/EnvResolver.ts#L56-L73
  - Precedence (verbatim from code comment): "`.sandcastle/.env` >
    `process.env`. Only keys declared in `.sandcastle/.env` are resolved from
    `process.env`."
  - Practical consequence: if you want sandcastle to pick up
    `CLAUDE_CODE_OAUTH_TOKEN` from your shell, you must add a line
    `CLAUDE_CODE_OAUTH_TOKEN=` (empty value OK) to `.sandcastle/.env`. OR
    pass it directly through `claudeCode({ env: { CLAUDE_CODE_OAUTH_TOKEN:
    process.env.CLAUDE_CODE_OAUTH_TOKEN! } })` like Matt does (4.3 above),
    which bypasses the EnvResolver and uses provider-level env merge.

- **Init scaffolding still defaults to API key**:
  - File: `src/InitService.ts`, lines 284, 511, 524 — all three mention the
    API key as the default and point to issue #191 for the subscription path.
  - `.sandcastle/.env.example` ships with just `ANTHROPIC_API_KEY=` and
    `GH_TOKEN=`. Permalink:
    https://github.com/mattpocock/sandcastle/blob/89325e4d5a10ea6b1d2aaef755e803145efa30b5/.sandcastle/.env.example
  - **The supported / documented path is the API key.** Subscription path
    requires diverging from the scaffolded defaults.

### 4.6 What `CLAUDE_CODE_OAUTH_TOKEN` is

- Documented Claude Code env var. Tells `claude` to authenticate against the
  user's Claude subscription rather than via `ANTHROPIC_API_KEY`.
- Minted by running `claude setup-token` once on a host where the user is
  already logged in to Claude Code interactively.
- Confirmed by Matt in #191 as documented-by-Anthropic-inside-Claude-Code-
  itself; this is not a hack/undocumented hole.

### 4.7 Why subscription users gravitate to `noSandbox()` — runtime preference, not auth blocker

§4.4's "in practice" paragraph could be misread as "subscription auth
*forces* `noSandbox()`." It does not. The proposing issue for ADR 0015 makes
clear the gravitation is a **runtime/setup preference** about not wanting a
container on the host machine running sandcastle — orthogonal to which auth
the agent uses.

- **Issue #507 — "Allow `noSandbox()` in `run()` and `createSandbox()`"**:
  - URL: https://github.com/mattpocock/sandcastle/issues/507
  - The originating user `achtan`, after Matt's initial "subscription users
    already have an AFK path via #191" objection, clarified the actual ask
    (verbatim):
    > "The OAuth token from #191 solves *auth*, not *runtime*. My ask is
    > the runtime piece: I don't want a container on my machine at all.
    > With `CLAUDE_CODE_OAUTH_TOKEN` I still need Docker/Podman running for
    > `run()` to accept the provider — that's the part I'm trying to
    > avoid."
  - Matt's reply (verbatim):
    > "Right, so you want to run AFK (with bypass perms) but you don't want
    > a sandbox. I suppose I should allow this, especially since you might
    > run Sandcastle from within a containerized environment already."
  - A later commenter (`gt-ak8`) describes a different non-auth motivation
    that also lands on `noSandbox()`:
    > "Since the Claude Code desktop app turns out to support SSH
    > connection, using a long living VM is a nice other way to have long
    > running sessions locally. Definitely a use case where I am fine
    > using no sandbox directly in the VM and let the agents do their
    > thing."

- **ADR 0015's audience is bundled, not auth-specific.** Re-read the "in
  practice" paragraph: it lists subscription users *together with* "anyone
  running Sandcastle inside an already-isolated environment — containerized
  CI, VM, sandbox host." The second group has nothing to do with auth. The
  shared property is "don't want a (nested) container on the host running
  sandcastle," not subscription billing.

- **Matt's own dogfooded workflows all use `noSandbox()`.** Every consumer
  of the `claudeAgent()` factory from §4.3 passes `sandbox: noSandbox()`:
  - `.sandcastle/agent-workflows/implement/implement.ts:18`
  - `.sandcastle/agent-workflows/review/review.ts:30`
  - `.sandcastle/agent-workflows/explore/explore.ts:39`
  - `.sandcastle/agent-workflows/implement-pr/implement-pr.ts:29`
  - `.sandcastle/agent-workflows/update-branch/update-branch.ts:70`
  - Docker only appears in `.sandcastle/run.ts` (testing) and the
    `test-podman.ts` / `test-vercel.ts` files. Caveat for a fresh agent:
    this could be because Matt's own machine is already a trusted dev
    environment, not because subscription forces it. Don't over-read.

- **Env passthrough already wires Docker + subscription end-to-end.** §4.5
  documents that `claudeCode({ env: { CLAUDE_CODE_OAUTH_TOKEN } })` reaches
  the container via `docker run --env`. Nothing in the codebase blocks the
  combination — the divergence is from the scaffolded happy path (which
  assumes API key in `.env.example` / `InitService.ts`), not from technical
  feasibility.

Method to re-fetch:

```bash
gh issue view 507 --repo mattpocock/sandcastle --comments
grep -rn "sandbox:" .sandcastle --include='*.ts'
```

### 4.8 What the Docker sandbox actually isolates

Closes §5 q4. Read: `src/sandboxes/docker.ts`,
`src/DockerLifecycle.ts:156-170`, `src/SandboxFactory.ts:272-296`,
`src/startSandbox.ts:127-156`, `.sandcastle/Dockerfile`.

- **`docker run` flags** (`DockerLifecycle.ts:156-170`): identity
  (`--user UID:GID`), mounts (`-v`), env (`-e`), opt-in `--network` /
  `--group-add` / `--device` / `--cpus`. **No security hardening flags**
  — Docker defaults only.
- **Default mounts** (`startSandbox.ts:127-156` + `resolveGitMounts`):
  worktree → `/home/agent/workspace` and `.git`. Host config dirs
  (`~/.ssh`, `~/.aws`, `~/.claude`, etc.) are not mounted; the OAuth
  token reaches the container via `-e`, not a mount.
- **Network**: Docker's default bridge — full outbound internet, no
  egress controls.
- **Image** (`.sandcastle/Dockerfile`): Debian + git/curl/jq/gh/claude,
  non-root `agent` user, `sleep infinity` entrypoint.
- **Trust-model coupling** (`interactive.ts:388`,
  `AgentProvider.ts:862-872`): inside any non-`noSandbox()` provider,
  claude runs with `--dangerously-skip-permissions`. The mount surface
  IS the policy.

**Net over a permission-tightened bare-metal claude:** filesystem
allow-list by mount (replaces deny-list permission curation) and
unattended AFK operation (permissions are off inside the sandbox).

**Not added in shipped form:** network egress control, quota protection,
hardened kernel isolation, write protection on the repo.

## 5. Open questions for the fresh agent

The investigator did **not** answer the following. Future research should.

1. **Does Anthropic's June-15 policy doc actually permit the user's intended
   use?** Read https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan
   fresh — it may have been updated. The 2D matrix above does not encode
   policy, only the technical mechanism.

2. **Does headless subscription burn quota faster than interactive
   subscription?** The only evidence collected here is two anecdotal posts
   in issue #191 (`rcfrias`, `vi-vlasov`) and `plainlystated`'s
   interpretation of the Anthropic doc. The user explicitly noted these are
   "random people on the internet" and should not be trusted as primary
   evidence. **Anthropic does not appear to publish per-mode rate limits in
   the doc that was current at investigation time.** A controlled experiment
   on the user's own subscription would be the only authoritative answer.

3. **Does sandcastle's `interactive()` actually launch successfully against a
   subscription token end-to-end?** The investigator read the code but did
   **not** run sandcastle. A fresh agent should attempt a minimal repro:

   ```ts
   import { interactive, claudeCode } from "@ai-hero/sandcastle";
   import { docker } from "@ai-hero/sandcastle/sandboxes/docker";

   await interactive({
     agent: claudeCode("claude-opus-4-7", {
       env: { CLAUDE_CODE_OAUTH_TOKEN: process.env.CLAUDE_CODE_OAUTH_TOKEN! },
     }),
     sandbox: docker(),
   });
   ```

   Prerequisites: `claude setup-token` on the host to mint a token, then
   `export CLAUDE_CODE_OAUTH_TOKEN=...` in the shell running the script.
   Also requires the Docker image to be built (`sandcastle init` +
   `sandcastle docker build-image`) — the Dockerfile ships with Claude
   Code CLI baked in, per the README.

4. ~~`noSandbox()` vs Docker for subscription billing~~ — **answered in
   §4.8.** Net: filesystem allow-list + AFK are the two new
   affordances; network/kernel/quota/write-protection are not added.

5. **`~/.claude` bind-mount as an alternate auth path** — would mounting the
   host's `~/.claude` into the container (`mounts: [{ hostPath: "~/.claude",
   sandboxPath: "/home/agent/.claude" }]`) work in place of, or alongside,
   `CLAUDE_CODE_OAUTH_TOKEN`? Not tested. Could be more robust than the env
   var for OAuth refresh flows.

## 6. Methods used (so a fresh agent can reproduce)

1. **Clone shallow into a scratch dir** (the agent used `$CLAUDE_JOB_DIR`,
   which is a per-job temp dir cleaned up at job exit):

   ```bash
   git clone --depth 1 https://github.com/mattpocock/sandcastle "$CLAUDE_JOB_DIR/sandcastle"
   git -C "$CLAUDE_JOB_DIR/sandcastle" rev-parse HEAD   # pin the SHA
   ```

2. **Read the README end-to-end first.** It self-documents most of the API
   surface — the `interactive()` and `run()` sections, the env var
   conventions, the branch strategies, and (critically) the line pointing to
   issue #191 for the subscription path.

3. **Fetch issue #191 with full comments** via `gh`:

   ```bash
   gh issue view 191 --repo mattpocock/sandcastle --comments
   ```

4. **Grep for keywords that reveal subscription intent** across the entire
   tree (this was the highest-leverage single command — it surfaced the
   smoking gun in `common.ts`):

   ```bash
   grep -rn "CLAUDE_CODE_OAUTH_TOKEN\|setup-token\|subscription\|OAUTH\|\.credentials" \
     --include='*.ts' --include='*.md' --include='*.txt' --include='*.example' \
     "$CLAUDE_JOB_DIR/sandcastle" | grep -v node_modules
   ```

5. **Read the agent provider end-to-end**, especially the `claudeCode` factory
   (lines 822–907 at the pinned SHA) — this is where `buildPrintCommand`
   (headless) and `buildInteractiveArgs` (TUI) are defined.

6. **Read `src/interactive.ts`** to confirm host stdin/stdout/stderr are wired
   to the sandbox subprocess (lines 386–401).

7. **Read `src/sandboxes/docker.ts`** to confirm:
   - `docker exec -it` allocates a real TTY when host stdin is a TTY (lines
     322–352).
   - Env passthrough is verbatim (lines 180–199).
   - User mounts are accepted (lines 137–167).

8. **Trace call sites of `claudeAgent()`** to discover which mode Matt uses:

   ```bash
   grep -rn "claudeAgent\|sandcastle\.\(run\|interactive\|createSandbox\)" \
     "$CLAUDE_JOB_DIR/sandcastle/.sandcastle" --include='*.ts'
   ```

9. **Read ADR 0015** — short, single-page, decisive on subscription users as
   an audience.

10. **Read the `.env.example` and `InitService.ts` references to #191** — these
    confirm the maintainer's stance is *documented* across the user-facing
    surface, not just buried in an issue.

## 7. What the investigator did NOT do

- **Did not run sandcastle.** No live invocation, no Docker image build, no
  `claude setup-token` run. All conclusions are from code reading + the issue
  thread.
- **Did not read Anthropic's June-15 doc directly.** Only saw it referenced
  from issue #191. A fresh agent must read it.
- **Did not survey alternatives.** ADR 0015's issue thread mentions other
  tools/forks ("rondo", "symphony") that solve similar problems — those were
  out of scope here but might be worth comparing if sandcastle hits a wall.
- **Did not check sandcastle's CHANGELOG for relevant entries** beyond a
  single grep hit at `CHANGELOG.md:312` ("Point users to #191 for using
  Claude subscription instead of an API key in .env.example, README, and
  init CLI output"). A fresh agent should skim the full changelog for any
  later movement on subscription support.
