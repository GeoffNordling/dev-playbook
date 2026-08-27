---
type: Standard-Card
title: Harness Files
description: Governs how the files an agent harness loads — context, configuration, instructions — are distinguished from ordinary files and what each contains
---

# Harness Files

Governs how the files an agent harness loads — context, configuration,
instructions — are distinguished from ordinary files and what each
contains. The loading contract fixes their meaning: injected into
context, read as configuration, or run as instructions. Claude Code is
the only harness currently in use.

## Define

- [standards/harness/](/standards/harness/index.md) — the member
  registry and the CLAUDE.md content standard; start at Files
- [Instruction Grammar](/standards/harness/grammar.md) — the braced-span
  grammar that makes skill and agent bodies machine-readable
- [Runbook Conventions](/standards/harness/runbook-conventions.md) — the runbook
  format: skill bundles and agent definitions
- [writing-for-agents](/dotfiles/.agents/skills/writing-for-agents/SKILL.md) —
  the craft layer beside the binding format, installed verbatim from
  mattpocock/skills: how any document an agent consumes is written so the
  agent behaves predictably; invoke it as `/writing-for-agents`, and Skill
  Conventions wins where the two collide

## Audit

- [repo-lint](/scripts/repo-lint) — CLAUDE.md presence; the agent-facing
  voice of every CLAUDE.md, root to global — no first person
  (`harness.agent-facing-voice`); and, in dev-playbook only, the global
  CLAUDE.md source's two-section shape and the workspace-wide rules it must
  carry (`harness.global-claude-shape`,
  `harness.global-claude-rules`)
- [harness-files-lint](/scripts/harness-files-lint) — skill bundles in
  skill-authoring repos, plus the `harness.skill-mirror`
  correspondence between authored and installed skills (dev-playbook)
- [judgments/harness.yaml](/judgments/harness.yaml) — the LLM-judged
  claim that the root and global CLAUDE.md genuinely read as agent-facing
  voice, the semantic check the token-level rule cannot make

## Enforce

- the canonical
  [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
  — its published `playbook-lint` hook dispatches to both repo-lint and
  harness-files-lint at the **commit gate** in every repo's suite; harness-files-lint
  no-ops where a repo authors no skills

## Adopt

- [CLAUDE.md Content](/standards/harness/claude-content.md) — a repo
  writes its own operating knowledge into its `CLAUDE.md` and nothing more;
  the workspace-wide rules are already stationed in the global file
