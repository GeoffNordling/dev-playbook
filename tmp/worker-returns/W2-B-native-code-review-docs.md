# W2-B · claude-code-guide · primary docs on native /code-review (issue 199) — verbatim return (condensed formatting, all content)

## 1. What the native /code-review is, invocation

Slash command in any Claude Code session: `/code-review [low|medium|high|xhigh|max|ultra] [--fix] [--comment] [target]`. Target optional: file path, PR number, branch name, or ref range. `--comment` posts findings as inline PR comments; `--fix` applies findings to the working tree. Default scope: branch's commits ahead of upstream + uncommitted changes. (https://code.claude.com/docs/en/code-review.md)

Distinct from the managed **Code Review** service (runs on Anthropic infrastructure, auto-posts to GitHub PRs) — the docs separate the local command from the managed service explicitly.

## 2. Effort levels and internal behavior

Documented qualitatively: "Lower effort levels return fewer, higher-confidence findings, while `high` through `max` give broader coverage and may include uncertain findings." `ultra` = cloud-based deep review (separate product, "ultrareview").

**The docs do NOT document agent spawning for the local /code-review at any effort level.** No finder-agent counts, no subagent types. The managed service docs DO say "multiple agents analyze the diff and surrounding code in parallel on Anthropic infrastructure" — but that's the cloud service, no count given.

## 3. Caller control of spawning

**None documented** for the local command. Pinning effort to medium is NOT documented as preventing multi-agent fan-out (heuristic only). For `/code-review ultra`: "launches a fleet of reviewer agents in a remote sandbox" (https://code.claude.com/docs/en/ultrareview.md) — no documented cap or constraint mechanism.

## 4. Fork inheritance and warnings

Documented (https://code.claude.com/docs/en/sub-agents.md): "A fork is a subagent that inherits the entire conversation so far instead of starting fresh. This drops the input isolation that subagents otherwise provide: a fork sees the same system prompt, tools, model, and message history as the main session." Regular subagents: "Each subagent starts with a fresh, isolated context window."

**NOT documented: any warning about forks re-executing earlier top-level instructions, or guidance to prevent it.** This is an undocumented hazard — a genuine upstream doc gap.

## 5. Repo override of a native skill

Documented (https://code.claude.com/docs/en/skills.md): "A skill at any of these levels also overrides a bundled skill with the same name. For example, a `code-review` skill in your project's `.claude/skills/` replaces the bundled `/code-review`." Plugin skills use `plugin-name:skill-name` namespace, cannot conflict. **No documented pattern for WRAPPING (rather than replacing) a native skill.**

## 6. Mechanical incident-prevention levers

- **Session spawn cap**: `CLAUDE_CODE_MAX_SUBAGENTS_PER_SESSION` — default 200 subagents per session, any positive integer, no upper bound, cannot be turned off. Requires v2.1.212+. Applies to nested subagents, forks, background subagents, workflow-spawned agents. At the cap the Agent tool fails with "Subagent spawn limit reached". `/clear` resets the count.
- **Depth cap**: "A subagent at depth five doesn't receive the Agent tool and can't spawn further. The limit is fixed and not configurable."
- **TaskStop**: mentioned in docs, but parent-initiated termination of another agent's children / ownership semantics are NOT documented (matches the incident report's "TaskStop refused on ownership grounds").
- No /code-review-specific spawn controls documented.

## Documented vs undocumented summary

| Question | Documented? |
|---|---|
| Invocation, effort levels, flags | Yes |
| Agent spawning per effort level (local) | No |
| Caller control of spawning | No |
| Fork inherits full conversation | Yes |
| Fork re-execution hazard warning | **No — doc gap** |
| Same-name project skill replaces bundled | Yes |
| Wrap-don't-replace pattern | No |
| Spawn cap env var, depth-5 limit | Yes |
| TaskStop ownership semantics | No |
