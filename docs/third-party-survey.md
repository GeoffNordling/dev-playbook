---
type: Survey
title: Third-Party Survey
description: External frameworks, tools, and skills worth tracking — what each is, its status, and what to watch next
---

# Third-Party Survey

Notes on external frameworks, tools, and skills worth remembering and checking up on periodically. Brief entries — what it is, where to find it, strengths, weaknesses, and where to look next.

This is **not authoritative**. Adoption decisions live in [`adr/`](/docs/adr/index.md). Entries here are observations and reminders, not commitments.

---

## Matt Pocock skills

**Source:** https://github.com/mattpocock/skills
**Author:** Matt Pocock
**Audited:** 2026-04-29 ([ADR-0001](/docs/adr/0001-adopt-matt-pocock-conventions.md)); revised 2026-05-09 ([ADR-0004](/docs/adr/0004-remove-pocock-direct-dependency.md))

Bundle of agent skills covering issue management (`/triage`, `/to-issues`), grilling (`/grill-with-docs`, `/grill-me`), TDD (`/tdd`), architecture analysis (`/improve-codebase-architecture`), and small utilities (`/zoom-out`, `/caveman`). Distributed via the Vercel `skills` CLI; each skill ships with the per-repo conventions it expects (`docs/agents/{issue-tracker,triage-labels,domain}.md` files, an `## Agent skills` block in `CLAUDE.md`, `CONTEXT.md` glossary, `docs/adr/` with 4-digit numbering and offer-criteria gate, triage label vocabulary, vertical-slice issue rules).

Initially adopted wholesale per [ADR-0001](/docs/adr/0001-adopt-matt-pocock-conventions.md) — skills *and* conventions, on the principle that running engineering skills without the per-repo files they expect produces degraded output. Direct dependency cut per [ADR-0004](/docs/adr/0004-remove-pocock-direct-dependency.md) once the conditions changed: spec-tools moved to its own repo and grew per-repo conventions of its own that overlapped Pocock's, so the "complements existing canon" condition from [ADR-0003](/docs/adr/0003-decline-superpowers.md) no longer held.

Currently: Pocock's engineering ideas were absorbed into dev-playbook's own authored standards and skill bundles rather than kept as a dependency; the specific files have since been refactored and consolidated. `/zoom-out` and `/caveman` remain as direct Vercel dependencies — tiny utility skills where lift cost ≈ drop cost.

### Watching going forward

If Pocock publishes new skills or sharpens the existing bundle, route the question through the [ADR-0003](/docs/adr/0003-decline-superpowers.md) rule: do the conventions still complement existing canon, or do they compete with spec-tools / authored standards? If they complement, consider re-adopting; if they compete, harvest specific techniques into authored skills rather than reinstalling the dependency.

---

## Superpowers

**Source:** https://github.com/obra/superpowers
**Author:** Jesse Vincent (Prime Radiant)
**Audited:** 2026-05-08 ([ADR-0003](/docs/adr/0003-decline-superpowers.md))

Opinionated agentic skills framework that imposes a fixed methodology on coding agents — brainstorming → writing-plans → subagent-driven-development → TDD → code review → finishing. ~10k lines of markdown across 13 skills plus a SessionStart bootstrap hook that primes every session. Distributed as plugins for seven coding-agent harnesses (Claude Code, Codex CLI/App, Cursor, Gemini CLI, OpenCode, Factory Droid, GitHub Copilot CLI). Designed for wholesale adoption; piecemeal adoption is awkward by construction — skills cross-reference each other, voice is distinctive throughout, and the methodology is coupled to the skill set.

The orientation: "agents are undisciplined and will rationalize their way out of process unless bright-line rules stop them." Skills are shaped by that worldview throughout — Iron Laws, "Red Flags" rationalization tables, "your human partner" framing, ALL-CAPS XML tags. Prose is engineered using published research on persuasion (Cialdini; Meincke et al. 2025, N=28k showing compliance jumps 33% → 72% with authority/commitment/scarcity framing).

Declined wholesale per [ADR-0003](/docs/adr/0003-decline-superpowers.md) because it conflicts with spec-tools SDD. But the framework contains a ton of good ideas worth tracking.

### Skills worth watching

If a workspace-native version of any of these is ever warranted, these are the skills to revisit for inspiration:

- **`requesting-code-review`** — self-contained code-review dispatch template. Could fill a gap if `/sdd-agentreviews` (which is `AgentReview:`-only) proves insufficient as the workspace's only review skill.
- **`verification-before-completion`** — "Iron Law": no completion claims without fresh verification evidence. Aligns with the "fail loud" `<behavior>` preference in the global CLAUDE.md.
- **`systematic-debugging`** — 4-phase root-cause investigation. Bundles three reusable sub-patterns: root-cause-tracing, defense-in-depth, condition-based-waiting.
- **`writing-skills`** — meta-skill for authoring skills. Two artifacts in this bundle are particularly valuable:
  - `persuasion-principles.md` — Cialdini's seven principles applied to skill prose, with the Meincke et al. (2025) experimental validation. Specifically calls out which principles to use for discipline-enforcing skills (Authority + Commitment + Social Proof) and which to avoid (Liking, Reciprocity).
  - `testing-skills-with-subagents.md` — adversarial pressure-testing methodology for skill prose. RED-GREEN-REFACTOR applied to documentation: run scenarios without the skill (watch agent fail), write the skill (watch agent comply), close loopholes.

### Patterns worth watching

Cross-cutting techniques that span multiple Superpowers skills, useful as inspiration for authored workspace skills:

- **SessionStart hook bootstrap** — inject prose into `additionalContext` (or harness equivalent) at session start to force priming. Harness-portable across Claude Code, Cursor, Copilot CLI.
- **Subagent-isolation-per-task** — fresh subagent per task with curated context; controller never pollutes its context with implementation details. Possible enhancement to `/sdd-implementation`'s chunk loop if real-use evidence shows context pollution.
- **Two-stage review** — spec compliance review (did you build the right thing?) before code quality review (did you build it well?). Order matters; running quality first lets shippable-but-out-of-spec work pass.
- **Iron Law / Gate Function structure** — bright-line absolute rule plus explicit anti-rationalization clauses ("violating the letter is violating the spirit"). Useful structure for any discipline-enforcing skill.
- **Red Flags rationalization tables** — two-column table naming the rationalization the agent would use to skip discipline, paired with the rule it violates. Useful for `/sdd-implementation` and `/sdd-requirements`.

---

## claude-code-transcripts

**Source:** https://github.com/simonw/claude-code-transcripts
**Author:** Simon Willison
**Audited:** 2026-05-08

CLI that converts Claude Code session files — the JSONL files at `~/.claude/projects/<project>/<session-id>.jsonl`, plus JSON exports from Claude Code for web — into paginated HTML transcripts. Four subcommands: `local` (interactive picker over recent local sessions), `web` (Claude Code for web sessions via Anthropic's undocumented APIs), `json` (one file at a time), `all` (bulk archive of every local session). Optional `--gist` publishes via GitHub Gist + gisthost.github.io. Distributed on PyPI; runs via `uvx claude-code-transcripts`.

**Status: soft-abandoned.** Last commit 2026-02-12 (3 months stale). 57 open issues, 20+ unmerged PRs, 169 forks but none with stars or clear successor traction. Not archived; the README carries a warning that the `web` subcommand is broken because Anthropic changed the undocumented endpoints (`/v1/sessions`, `/v1/session_ingress/session/{id}`) that it scraped — see [issue #77](https://github.com/simonw/claude-code-transcripts/issues/77). The `local`, `json`, and `all` subcommands — which read local JSONL directly — still work.

Worth tracking not as something to adopt but as the canonical example of how hard the JSONL-flattening problem actually is. The open-issue stream is an inventory of edge cases anyone reinventing this will rediscover: subagent sessions appearing as separate projects (#92), Cowork sessions (#84), Skill content blocks (#90), ANSI codes in tool output (#95), `<task-notification>` mis-rendering as user messages (#99), missing `queue-operation` prompts (#98), thinking blocks dropped without a settings override (#89). Output is HTML — verbose for direct LLM input; the markdown-export PR (#82) is the closer fit but unmerged.

### Why JSONL flattening is hard

Concrete obstacles encoded in this tool's history, useful as a checklist for any future workspace flattener:

- **Branching via `parentUuid`** — editing a previous prompt forks the conversation; the file ends with sibling subtrees sharing a prefix. File order ≠ logical order. Walking the DAG and picking the live leaf is required to avoid rendering edited-away dead branches.
- **Sidechains (`isSidechain`)** — subagent (Task tool) traffic lives in the same file as main-thread traffic. Interleaving by timestamp produces unreadable output.
- **Content-block zoo** — `text`, `thinking`, `tool_use`, `tool_result`, `image`, plus newer types as Anthropic ships them (Skills, Cowork). Tool results pair with their `tool_use` by ID, not position, and can be string, array-of-blocks, or structured payloads.
- **Injected wrappers** — `<system-reminder>`, `<command-message>`, `<command-name>`, hook output, `CLAUDE.md` payloads stuffed into user `content`. Verbose and not what the human typed.
- **Compaction events** — long sessions auto-summarize; the file contains the summary records, not the underlying turns.
- **Tool-result blowups** — a single `Read`/`Bash` result can be tens of thousands of tokens. Truncation policy is required for any LLM-input use.
- **Format drift** — the format is undocumented and keeps evolving (Skills blocks, Cowork sessions, sidechain shape changes all surfaced in the open-issue stream within 3 months of the last commit).

### Lessons for workspace flattening

If a workspace-native session-flattener is ever warranted (e.g. for an "analyze this session" prompt loop), revisit this tool as a parsing reference rather than a runtime dependency:

- **Don't aim for fidelity, aim for "good enough for LLM input."** Punt on branching by keeping the latest leaf only; drop or appendix sidechains; truncate tool results past N chars; regex out `<system-reminder>` wrappers. The downstream LLM is tolerant of mess.
- **For going-forward capture, prefer hooks over JSONL post-processing.** `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop` emit clean structured events at known points; logging from there sidesteps the format-drift problem entirely. Doesn't help retroactively.
- **PRs worth pulling parsing logic from** before they bitrot: #82 (`add-markdown-export`), #93 (`fix/web-list-web-session` — keeps the web path alive against the new Anthropic APIs), #91 (Cowork support + module refactor), #88 (PDF/DOCX export).

---

## agentsview

**Source:** https://github.com/wesm/agentsview ([agentsview.io](https://agentsview.io))
**Author:** Wes McKinney
**Audited:** 2026-05-08 — *adopted, in regular use*

Local-first session-intelligence and analytics CLI for coding agents. Reads session files from Claude Code, Codex, and 14 other agents and surfaces usage, cost, and behavior data. Also pitches itself as a 100x-faster `ccusage` replacement. Go binary, MIT licensed, ~900 stars, active. Solves at the analytics layer the same JSONL-shape problem `claude-code-transcripts` solves at the rendering layer — same edge-case inventory likely applies, but a Go reimplementation by an experienced data-tooling author may have already paid down some of that debt.

In regular use as the workspace's session-analytics tool. Watching for: format-drift handling as Claude Code ships new content-block types, multi-agent coverage as Codex/Gemini sessions accumulate.

---

## roborev

**Source:** https://www.roborev.io/
**Author:** Wes McKinney
**Audited:** 2026-05-08 — *not adopting*

Continuous code review for coding agents. Reviews commits immediately via installed agents (Claude Code, Copilot, Gemini), surfaces findings in a TUI, and lets agents address them while context is fresh. Local SQLite + HTTP daemon on port 7373; optional Postgres sync for multi-machine federation; git hook for per-commit reviews. MIT licensed, free to install — but the *running cost* is API tokens for every commit, and the design assumes that's not a concern.

Not adopting: roborev is shaped by Wes's situation (reportedly $20k in lab API credits because he's famous), where reviewing every commit at scale is free. For a workspace paying retail token costs on solo work, per-commit auto-review is the wrong economic shape. Worth tracking as the canonical "what does code review look like when tokens are free?" reference point.

---

## Superset

**Source:** https://superset.sh/
**Author:** Superset Inc. (YC-backed)
**Audited:** 2026-05-08 — *blocked on platform*

Desktop "code editor for AI agents" — orchestrates many parallel coding agents (claims 100+) on a local machine, isolating each in its own git worktree to avoid merge conflicts. Universal agent compatibility (Claude, Cursor, OpenCode, Gemini), IDE bridges (VS Code, JetBrains, Xcode), MCP server integration, port forwarding, SSH/cloud-workspace hooks. Adoption logos include Microsoft / Netflix / Google / Vercel / Cloudflare engineers. Free tier plus enterprise tier.

> 💡 Git worktree: a feature that lets one repo have multiple working directories checked out to different branches simultaneously, sharing a single `.git` directory. Lets parallel agents edit different branches without stepping on each other.

Blocked: macOS only. Workspace runs Linux (Fedora). Revisit if a Linux build ships, or if the parallel-worktree-per-agent pattern becomes interesting enough to reimplement against bare `git worktree` + a launcher script.
