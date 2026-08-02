---
type: Survey
title: Workflow-runtime primitives and agent definitions
description: The Workflow runtime's scripting primitives and the custom agent-definition frontmatter surface, each claim traced to a primary source
---

# Workflow-runtime primitives and agent definitions

What the Workflow runtime's scripting primitives (`agent()`, `parallel()`,
`pipeline()`, `workflow()`, `log()`, `phase()`, `args`) and the custom
agent-definition frontmatter surface (`.claude/agents/*.md`) actually do and
don't do, and where the two disagree with what Anthropic's own docs claim.

Functional summary as of 2026-08-02, from Anthropic's
[workflows](https://code.claude.com/docs/en/workflows),
[sub-agents](https://code.claude.com/docs/en/sub-agents),
[tools-reference](https://code.claude.com/docs/en/tools-reference), and
[agents](https://code.claude.com/docs/en/agents) docs; the probe record in
[dev-playbook#321](https://github.com/GeoffNordling/dev-playbook/issues/321);
and a read of `dotfiles/dot-claude/workflows/scatter-gather.js`,
`dotfiles/dot-claude/workflows/ralph-loop.js`, and
`dotfiles/dot-claude/workflows/judgments.js`.

**Citation key.** `[documented: <page>]` — stated on one of the four fetched
doc pages. `[probed: #321 §n]` — verbatim probe output recorded in that
issue's comments. `[source: <repo path>]` — asserted in a script this repo
ships and runs against the live runtime. `[unverified — needs probe]` — not
established by any of the above; listed again at the end as an open item for
prototype ticket #324.

## The public docs are known to lag the runtime

Every script in `dotfiles/dot-claude/workflows/` carries the same dated note:

> the Workflow runtime's own docs are wrong here — they say objects/arrays
> reach the script verbatim, but every `args` value actually arrives
> JSON-serialized to a string (or `undefined` when omitted)

`[source: dotfiles/dot-claude/workflows/scatter-gather.js, ralph-loop.js,
judgments.js]`. This directly contradicts the currently-fetched
`workflows.md`, which states: "Claude passes the list as structured data, so
the script can call array and object methods on `args` directly without
parsing it first. If `args` is omitted, the global is `undefined` inside the
script." `[documented: workflows.md → "Pass input to a saved workflow"]`. The
scripts were re-probed against the live runtime on 2026-07-31 and still parse
`args` as a JSON string; treat the doc's "structured data" claim as stale, and
every fact below as suspect until it is cross-checked against a probe or a
running script, per the pattern this repo already follows.

## What a workflow is

A workflow is "a JavaScript script that orchestrates subagents at scale.
Claude writes the script for the task you describe, and a runtime executes it
in the background while your session stays responsive."
`[documented: workflows.md]`. The runtime "executes the script in an isolated
environment, separate from your conversation. Intermediate results stay in
script variables instead of landing in Claude's context."
`[documented: workflows.md → "How a workflow runs"]`. Reachable via the
`Workflow` tool (top-level session and, per below, exactly one further
layer), or by name once saved to `.claude/workflows/` or
`~/.claude/workflows/` `[documented: workflows.md → "Save the workflow for
reuse"]`.

## `agent(prompt, opts)`

The one primitive the docs actually show in a code sample:

```javascript
const found = await agent('List every .ts file under src/routes/.', {
  schema: { type: 'object', required: ['files'], properties: { files: { type: 'array', items: { type: 'string' } } } },
})
```

`[documented: workflows.md → "What the saved script looks like"]`.
`workflows.md` does not enumerate `agent()`'s full option set in prose; it
points instead to "the Workflow tool entry in the Agent SDK reference for the
full set of options" `[documented: workflows.md]` — a page outside this
ticket's source list, so the option-by-option detail below is triangulated
from probes and the in-repo scripts, not from that prose.

| Opt | Status |
|---|---|
| `schema` | Forces a structured return — see below. `[documented: workflows.md example]`, `[source: ralph-loop.js, judgments.js]` |
| `model` | `'sonnet'` / `'opus'` / `'haiku'` etc., required per-job in scatter-gather/judgments (no batch-level default). `[source: scatter-gather.js, judgments.js]`. Session-level default and override: "Every agent in a workflow uses your session's model unless the script routes a stage to a different one or the `CLAUDE_CODE_SUBAGENT_MODEL` environment variable is set, which overrides both." `[documented: workflows.md → "Cost"]` |
| `effort` | `'low'` / `'medium'` / `'high'` / `'xhigh'` / `'max'`, required per-job alongside `model` in scatter-gather/judgments. `[source: scatter-gather.js, judgments.js]`. Not named in `workflows.md` prose |
| `label` | Names the agent in the run's progress view; used on every job in every shipped script (`label: `job:${job.id}``, `label: file`). `[documented: workflows.md example (`label: file`)]`, `[source: scatter-gather.js, ralph-loop.js, judgments.js]` |
| `phase` | Assigns the agent to a named phase declared in `meta.phases`. `[source: scatter-gather.js, judgments.js — `phase: 'Scatter'` / `'Judge'`]` |
| `isolation: 'worktree'` | **Not evidenced for the workflow-script `agent()` call in any of the three source tiers.** `isolation: worktree` is documented for *subagent-definition frontmatter* (below) and appears as a parameter on the separate, interactive `Agent` tool (this session's own tool schema: "worktree" creates a temporary git worktree...; "the worktree is automatically cleaned up if the agent makes no changes; otherwise the path and branch are returned in the result" — a primary source, but not a `code.claude.com` page). Whether the *runtime's* `agent()` inside a `.js` script accepts the same opt is `[unverified — needs probe]` |
| `agentType` | **No evidence found anywhere** — absent from `workflows.md`, `sub-agents.md`, `agents.md`, issue #321, and all three shipped scripts. `[unverified — needs probe]` |

### Return semantics

Without `schema`, `agent()` returns plain text: the nesting probe's leaf agent
returned the bare string `Tokyo` / `Paris` / a `pwd` path
`[probed: #321 Appendix B, §5]`, matching the Agent tool's documented
behavior of returning "a single text result" `[documented: tools-reference.md
→ "Agent tool behavior"]`. With `schema`, the return value is a parsed object:
`ralph-loop.js` reads `status.done`, `status.blocker`, `status.summary`
straight off the awaited result with no `JSON.parse` `[source: ralph-loop.js]`,
and `judgments.js` reads `result.verdict` / `result.opinion` the same way
`[source: judgments.js]`. Whether a malformed schema-mismatched response is
retried or simply fails is `[unverified — needs probe]` — no source describes
retry behavior.

A `null`/`undefined` result is a real, guarded-against outcome: every shipped
script wraps its `agent()` call in `result ?? null` plus a `try/catch` that
also yields `null`, with the comment "a crashed judge yields a null result
that KEEPS its id... Without it, `parallel()` would return a bare null and we
would lose track of which judgment it belonged to"
`[source: judgments.js, scatter-gather.js]`. The nesting probe's own run
summary reports `0 skipped` as a distinct completion category alongside
`0 errors` `[probed: #321 Appendix B, run 3]`, confirming skip is a recognized
runtime outcome, consistent with the "`null` on skip/terminal death"
characterization — but no source spells out which specific conditions produce
a resolved `null` versus a thrown error that the caller must catch.

## `parallel()`

Not named in `workflows.md`'s prose at all (only `agent()` and `pipeline()`
are called out by name); its behavior is established entirely by the shipped
scripts and issue #321. Signature observed: `parallel(thunks)` where
`thunks` is an array of zero-argument functions, awaited as a batch —
`scatter-gather.js` and `judgments.js` both call
`await parallel(JOBS.map((job) => async () => { ... }))`
`[source: scatter-gather.js, judgments.js]`, i.e. a `Promise.all`-shaped
barrier: the call doesn't return until every thunk settles. **Failed-thunk
semantics**: an uncaught throw inside one thunk collapses that whole
`parallel()` call's result to `null` (losing the identity of which item
failed) — this is exactly what both scripts' per-job `try/catch` is written
to prevent: "Without it, `parallel()` would return a bare null"
`[source: judgments.js]`. This describes a single failed thunk *within* an
array parallel() awaits collectively; it is not independently confirmed
whether one throw poisons only that array's overall `null` or the whole call.

## `pipeline()`

The one documented example: `pipeline(items, stageFn)` — an items array plus
a one-argument stage function, contrasted with `parallel()`'s array-of-thunks
shape:

```javascript
const audits = await pipeline(found.files, file =>
  agent(`Audit ${file} for missing authentication checks.`, { label: file }),
)
```

`[documented: workflows.md → "What the saved script looks like"]`, glossed in
prose as "`pipeline()` runs one per item in a list"
`[documented: workflows.md]`. No shipped script in this repo uses
`pipeline()` — none of `scatter-gather.js`, `ralph-loop.js`, or `judgments.js`
call it, so there is no in-repo cross-check. **"No inter-stage barrier"** (the
claim that a multi-stage `pipeline()` streams items through stages rather than
completing stage 1 for all items before starting stage 2) and **"a thrown
stage drops the item"** are both `[unverified — needs probe]` — the one
documented example is single-stage, so multi-stage behavior and failure
semantics are not established by any source available to this doc.

## `workflow()` — nesting

**Not present in the public documentation at all.** `workflows.md` "documents
`agent()` and `pipeline()` only; it does not mention `workflow()`,
`parallel()`, or nesting" `[probed: #321 §6]`. Everything below is
probe-only:

- **One level of nesting, unlimited count.** A parent workflow's script can
  call `workflow()` repeatedly (three calls in one run, all dispatched), but
  a child workflow's own `workflow()` call throws:
  `workflow() cannot be called from within a child workflow — nesting is
  limited to one level. Inline the inner script or call its agents directly.`
  `[probed: #321 §4]`
- **A saved workflow resolves by name from inside a script** — `workflow('scatter-gather', SG)` succeeded and ran the repo's real `scatter-gather.js` unmodified `[probed: #321 §4, Probe P2]`.
- **`args` passed through `workflow()` is not re-serialized** — a JSON string passed to `workflow()` reached the child's strict `parseArgs` unmodified, unlike the top-level `Workflow` tool, which serializes an object argument to a string on the way in `[probed: #321 §4]`. Passing a non-string value through `workflow()` was not tested `[probed: #321 §7]`.
- **Worktree cwd propagates one level down.** A leaf agent spawned two levels below a session running inside a git worktree (session → `workflow()` → `agent()`) inherited that worktree's absolute path via `pwd` `[probed: #321 §5]`.
- **Agents spawned inside a workflow are ordinary subagents** and therefore never have the `Workflow` tool themselves, at any depth `[probed: #321 §1, §4]`. Combined with the one-level `workflow()` cap, the deepest reachable structure is: session → `workflow()` (parent script, can call `workflow()` again) → child `workflow()` (its own `workflow()` throws) → `agent()` (no `Workflow` tool) `[probed: #321 §4]`.

## `log()`, `phase()`, `args`, `budget`

- **`log(message)`** — appends a line to the run's progress log; used throughout the shipped scripts for status lines (`log(\`scatter-gather: ${JOBS.length} job(s)...\`)`) `[source: scatter-gather.js, ralph-loop.js, judgments.js]`.
- **`phase(title)`** — marks the current phase, matched against `meta.phases` declared at the top of the script; every shipped script calls it once per declared phase `[source: scatter-gather.js, ralph-loop.js, judgments.js]`.
- **`args`** — the caller's payload, delivered as a JSON-serialized string (or `undefined` if omitted), *not* as a live object despite the currently-published doc's claim — see ["The public docs are known to lag"](#the-public-docs-are-known-to-lag-the-runtime) above `[source: scatter-gather.js, ralph-loop.js, judgments.js — re-probed 2026-07-31]`, `[documented (stale): workflows.md → "Pass input to a saved workflow"]`.
- **`budget`** (total/spent/remaining, hard ceiling) — **no evidence found in any of the three source tiers.** `judgments.js`'s own inventory of what the script layer is given lists exactly "`agent()`, `parallel()`, `pipeline()`, `phase()`, `log()`, `args`" and nothing named `budget` `[source: judgments.js]`; `workflows.md`'s closest documented analog is the advisory `Large workflow` warning at >25 agents or >1.5M projected tokens, which is explicitly "advisory: it doesn't pause or limit the run" `[documented: workflows.md → "Cost"]` — not a script-visible budget object. `[unverified — needs probe]`

## Script sandbox rules

**Documented, and cross-verified in-repo:** "No direct filesystem or shell
access from the workflow itself. Agents read, write, and run commands. The
script coordinates the agents." `[documented: workflows.md → "Behavior and
limits"]`. `judgments.js`'s own header comment states the identical
constraint independently: the script layer is "deterministic, but has NO
filesystem, NO subprocess, NO network -- only `agent()`, `parallel()`,
`pipeline()`, `phase()`, `log()`, `args`" `[source: judgments.js]`, and
recounts a concrete failure mode this caused: an earlier version spawned an
agent to run the planner and "that agent had discretion it should never have
had... wandering out of the worktree it was launched in and judging the wrong
repo" — the fix was moving the deterministic planning step to the *session's*
Bash tool, outside the workflow script entirely `[source: judgments.js]`.

**Not found in any source:** an explicit ban on Node APIs generally, or on
`Date.now()` / `Math.random()` / `new Date()` specifically; a `journal.jsonl`
file; or a `resumeFromRunId` replay contract described in prose. The nearest
documented material is the "Resume after a pause" section: "An agent that was
still running when you stopped isn't saved, so it starts over on resume,"
and "Replay follows the order agents started. Cached results stop at the
first agent that didn't finish, and every agent that started after that one
runs again, even if it completed" `[documented: workflows.md → "Resume after
a pause"]`. Separately, `resumeFromRunId` is confirmed to exist as a literal
`Workflow`-tool schema property — a fork of the main session that inspected
its own tool list via `ToolSearch` got back the tool's full JSON schema
"with properties `args`, `description`, `name`, `resumeFromRunId`, `script`,
`scriptPath`, `title`" `[probed: #321 Probe 4]` — but no source describes the
on-disk replay format. All of `Date.now()`/`Math.random()`/`new Date()` bans
and `journal.jsonl` are `[unverified — needs probe]`.

## Caps

| Cap | Value | Source |
|---|---|---|
| Concurrent agents per workflow run | Up to 16, fewer on CPU-limited machines | `[documented: workflows.md → "Behavior and limits"]` |
| Agents per workflow run (lifetime) | 1,000 | `[documented: workflows.md → "Behavior and limits"]`; independently asserted as the binding ceiling in `scatter-gather.js`/`judgments.js`'s own `MAX_JOBS`/`MAX_JUDGMENTS = 1000` guards, "one agent per job, so it binds before the ... per-call cap" `[source: scatter-gather.js, judgments.js]` |
| Items per `parallel()`/similar call | 4096, referenced only as the *looser* of the two ceilings | `[source: scatter-gather.js — "the binding ceiling is the agent-lifetime cap (1000), not the larger 4096 per-call item cap"]`. Not independently confirmed by any doc or probe |
| Advisory large-run warning | >25 agents or >1.5M projected tokens (both configurable via the size guideline) | `[documented: workflows.md → "Cost"]` — advisory only, does not pause or limit the run |
| Subagent nesting depth | 3 layers below the main conversation by default; `1` disables nesting; env var `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` (available since v2.1.217; default was 1 in v2.1.217–218, 3 from v2.1.219; unchangeable 5-layer default in v2.1.172–216) | `[documented: sub-agents.md → "Let subagents spawn their own subagents"]`, matching `[probed: #321 §2]` |
| Subagents per session | 200 by default; env var `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` (any positive integer, no upper bound, since v2.1.212); resets on `/clear` unless a running workflow's count carries over | `[documented: sub-agents.md → "Session subagent limit"]`, matching `[probed: #321 §2]`. Agents a workflow script spawns via `agent()` do **not** count; subagents *those* agents spawn with the `Agent` tool do `[documented: sub-agents.md]` |
| Concurrent subagents | 20 by default; env var `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` (since v2.1.217); sessions with `ultracode` active are exempt | `[documented: sub-agents.md → "Concurrent subagent limit"]`, matching `[probed: #321 §2]` |
| `Workflow` tool availability | Stripped from every subagent unconditionally (one of nine tools removed by the first, always-applied filter); a fork of the *main session* is the sole exception and receives it; a fork spawned by an ordinary subagent does **not** regain it | `[documented: sub-agents.md → "Available tools"]`, confirmed end-to-end (including a successful `scatter-gather` run) at `[probed: #321 §1, Probe 4]`, and the negative case at `[probed: #321 Probe 6]` (weaker evidence — absence observed, not a runtime error) |

## Agent-definition frontmatter (`.claude/agents/*.md`)

Only `name` and `description` are required; every other field is optional
`[documented: sub-agents.md → "Supported frontmatter fields"]`:

| Field | What it does |
|---|---|
| `name` | Unique id, lowercase + hyphens; can't contain `:` (reserved for plugin-scoped names, v2.1.218+) |
| `description` | When Claude should delegate to this subagent |
| `tools` | Allowlist. Omitted ⇒ inherits every tool available to subagents. An unresolvable list usually fails the launch outright (v2.1.208+) |
| `disallowedTools` | Denylist, removed from the inherited/specified pool. Applied *before* `tools`; a tool in both is removed |
| `model` | `sonnet` / `opus` / `haiku` / `fable` / a full model ID / `inherit` (default). Resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env var → per-invocation `model` param → this frontmatter field → main conversation's model |
| `permissionMode` | `default` / `acceptEdits` / `auto` / `dontAsk` / `bypassPermissions` / `plan` / `manual` (alias for `default`, v2.1.200+). Overridden by the parent's mode when the parent is `bypassPermissions`, `acceptEdits`, or `auto` |
| `maxTurns` | Caps agentic turns before the subagent stops |
| `skills` | Preloads full skill content into the subagent's startup context (not merely a permission grant) |
| `mcpServers` | Inline or by-reference MCP servers scoped to this subagent only |
| `hooks` | Lifecycle hooks (`PreToolUse`, `PostToolUse`, `Stop`→`SubagentStop`) scoped to this subagent's runtime |
| `memory` | `user` / `project` / `local` — persistent cross-session memory directory |
| `background` | Force background execution (background is the default since v2.1.198 regardless) |
| `effort` | `low` / `medium` / `high` / `xhigh` / `max`; overrides session effort for this subagent |
| `isolation` | `worktree` — see below |
| `color` | Display color in the task list/transcript |
| `initialPrompt` | Auto-submitted first turn when this agent runs as the *main* session (`--agent`) |

`[documented: sub-agents.md → "Supported frontmatter fields"]` in full. The
CLI's `--agents` JSON flag accepts the same field set for session-scoped,
un-persisted definitions `[documented: sub-agents.md → "Configure subagents"]`.
Scope/precedence, highest first: managed settings → `--agents` CLI flag →
project `.claude/agents/` → user `~/.claude/agents/` → plugin `agents/`
`[documented: sub-agents.md → "Choose the subagent scope"]`.

## The priority unknown: "explicit cwd"

The ticket's exact phrase — agents "whose working directory was pinned at
launch (subagent isolation or explicit cwd)" — **does not appear on any of
the four fetched doc pages.** The closest text on the public
`tools-reference.md` page, in the `EnterWorktree` row, reads: "From within a
worktree session, or from a subagent with a pinned working directory such as
`isolation: worktree` (linked in the original to
`/docs/en/sub-agents#supported-frontmatter-fields`),
only the `path` form is available..." `[documented: tools-reference.md →
EnterWorktree row]` — this names only `isolation: worktree`, not a second
"explicit cwd" mechanism.

The "(subagent isolation or explicit cwd)" wording exists exactly once, and
it is not on a `code.claude.com` page at all: it is in the *live*
`EnterWorktree` tool's own JSON-schema description, as surfaced to this
session via `ToolSearch`: "Switching with `path` also works... and from
agents whose working directory was pinned at launch (subagent isolation or
explicit cwd). In both cases the target must be a worktree under
`.claude/worktrees/` of the same repository, and from a pinned agent the
switch only affects this agent, not the parent session."
`[source: EnterWorktree tool schema, this session — not published on
code.claude.com]`.

That is the entirety of the evidence. It names "explicit cwd" as a second,
distinct way an agent's working directory can be pinned at launch, alongside
`isolation: worktree` — but no source available to this doc says what sets
it, or where. Checked and ruled out:

- **Workflow-runtime `agent()` opts** — no `cwd` option appears in
  `workflows.md`'s documented example, in any of the three shipped scripts,
  or anywhere in the #321 probe record.
- **Agent-definition frontmatter** — the full field table above
  (`sub-agents.md`) has no `cwd` field; `isolation: worktree` is the only
  cwd-pinning field it names.
- **This session's own `Agent` tool schema** (the interactive tool used to
  spawn subagents, a distinct surface from the workflow-script `agent()`
  function) — its parameters are `description`, `isolation`, `model`,
  `prompt`, `subagent_type`; no `cwd` parameter.

**Conclusion: "explicit cwd" is real (it is named in a primary source — the
live tool schema) but its reachability from `agent()` opts or
agent-definition frontmatter is not established by any source this doc could
draw on.** `[unverified — needs probe]`. As a secondary data point: this doc
was written by a subagent, and per the capability matrix above the `Workflow`
tool was unavailable to it throughout — direct inspection of the `Workflow`
tool's own schema (which, like `EnterWorktree`'s, might describe `cwd` more
fully) was not possible from this vantage point. That absence is itself
consistent with, and adds first-hand confirmation of, `[probed: #321 §1]`.

## New since #321: does `isolation: 'worktree'` work from outside any repo?

Also unresolved, and newly relevant now that a factory manager may launch
`agent()` calls from `~/workspace` — above every repo, not inside one.
`EnterWorktree`'s own description *does* address this case explicitly, for
itself: "Must be in a git repository, OR have `WorktreeCreate`/`WorktreeRemove`
hooks configured in settings.json... Outside a git repository: delegates to
`WorktreeCreate`/`WorktreeRemove` hooks for VCS-agnostic isolation."
`[source: EnterWorktree tool schema, this session]`.

But that fallback is documented only for the `EnterWorktree` tool. None of
the three places that expose an `isolation: worktree`-shaped option say
anything about launching from outside a repo:

- `sub-agents.md`'s frontmatter field description assumes a repository
  exists to branch from ("an isolated copy of the repository branched by
  default from your default branch... rather than the parent session's
  HEAD") and is silent on the no-repo case
  `[documented: sub-agents.md → "Supported frontmatter fields"]`.
- The interactive `Agent` tool's own schema (`isolation: 'worktree'`) says
  nothing about a non-repo launch directory.
- The workflow-runtime `agent()` function's `isolation` support is itself
  unverified (see the `agent()` table above), so its no-repo behavior is a
  second layer of unknown on top of the first.

**Conclusion: explicit unknown, not documented anywhere in this doc's source
set.** Whether `agent(isolation: 'worktree')` — or subagent-frontmatter
`isolation: worktree` — can resolve *a* repo when launched from a directory
that is not itself inside one (and if so, which repo, and by what
resolution rule) is `[unverified — needs probe]`, flagged for #324.

## `isolation: 'worktree'` mechanics

What is established, combining the subagent-frontmatter doc and this
session's own `Agent`-tool schema (two adjacent but distinct surfaces — see
caveats inline):

- **Base ref.** "branched by default from your [default branch]... rather
  than the parent session's HEAD" `[documented: sub-agents.md →
  "Supported frontmatter fields"]`. `EnterWorktree`'s own schema states the
  analogous, but not confirmed-identical, rule for itself: base ref is
  governed by a `worktree.baseRef` setting — `fresh` (default) branches from
  `origin/<default-branch>`, `head` branches from current local `HEAD`
  `[source: EnterWorktree tool schema, this session]`. Whether subagent
  `isolation: worktree` shares that same `worktree.baseRef` setting is not
  stated by either source.
- **Branch naming.** Not documented anywhere in this doc's source set —
  `[unverified — needs probe]`.
- **Cleanup, changed vs. unchanged.** Documented twice, consistently: "The
  worktree is automatically cleaned up if the subagent makes no changes"
  `[documented: sub-agents.md]`; this session's own `Agent` tool schema adds
  the unchanged-tree case's complement: "otherwise the path and branch are
  returned in the result" `[source: Agent tool schema, this session]` — i.e.
  a worktree with changes is kept and its path/branch handed back rather
  than auto-removed.
- **Working-directory enforcement.** "A subagent with `isolation: worktree`
  runs its Bash and PowerShell commands inside its worktree. A command whose
  working directory resolves to your main checkout instead... fails with an
  error" (v2.1.203+), and as of v2.1.210 this check "covers the whole
  repository containing the directory you launched Claude Code from" and,
  when the launching session is itself in a worktree, "also covers the main
  checkout that worktree is linked from." As of v2.1.216, Bash commands are
  additionally checked for git redirection into the main checkout (`git -C`,
  `--git-dir`, `GIT_DIR`/`GIT_WORK_TREE`, or a `cd` first) — a command too
  complex to check fails outright, telling Claude to split it
  `[documented: sub-agents.md → "Write subagent files"]`.

## Open items for prototype ticket #324

Everything tagged `[unverified — needs probe]` above, consolidated:

1. Whether `agent()` inside a workflow script (not the interactive `Agent`
   tool, not subagent frontmatter) accepts an `isolation: 'worktree'` opt at
   all.
2. Whether `agentType` is a real `agent()` opt — no evidence of it exists in
   any source checked.
3. Retry/validation behavior when a model's output doesn't match a `schema`
   passed to `agent()`.
4. The precise set of conditions under which `agent()` resolves to `null`
   versus throws, beyond "a crashed or skipped job resolves to `null`."
5. `pipeline()`'s multi-stage behavior: whether stages run with "no
   inter-stage barrier" (streaming) or complete each stage for every item
   before the next begins, and whether a thrown stage drops just that item
   or the whole `pipeline()` call.
6. `parallel()`'s exact single-thunk-failure contract: does one throw inside
   an unguarded thunk null out only that thunk's slot, or the entire array's
   result?
7. Whether a `budget` global (total/spent/remaining, hard ceiling) is
   exposed to workflow scripts at all — no source names it.
8. The 4096 items-per-call figure asserted in `scatter-gather.js`'s own
   comment — not independently confirmed by any doc or probe.
9. Any ban on `Date.now()`, `Math.random()`, `new Date()`, or other
   nondeterministic/Node APIs inside a workflow script; and whether a
   `journal.jsonl`-shaped on-disk replay log exists and what its format is —
   `workflows.md`'s resume semantics are documented in prose, but not as a
   concrete file format.
10. **Priority: whether "explicit cwd" (named only in the live
    `EnterWorktree` tool schema, never in the public docs) is reachable from
    `agent()` opts or agent-definition frontmatter** — the phrase names a
    real mechanism but no source establishes how to set it.
11. **New: whether `isolation: 'worktree'` — on `agent()`, or on subagent
    frontmatter — can resolve a repository when the launching session's cwd
    is not itself inside a git repository** (the case a factory manager
    sitting at `~/workspace` would hit), and if so, which repo it picks.
12. Whether subagent `isolation: worktree`'s base ref shares the same
    `worktree.baseRef` setting `EnterWorktree` documents for itself, or is an
    independent, undocumented rule.
13. Branch-naming convention for a worktree created by `isolation: worktree`.
