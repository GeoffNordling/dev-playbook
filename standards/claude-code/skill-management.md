---
type: Standard
title: Skill Management
description: How third-party skills are taken in and recorded, where skills live, and the mirror rule between authored and installed
---

# Skill Management

How third-party skills are taken in, where Claude Code skills live in this workspace, and how they are installed, updated, and removed. For the format of skill bundles in this workspace, see [skill-conventions.md](/standards/claude-code/skill-conventions.md).

## Intake

A third-party skill enters the workspace through a **sweep**: one pass over one upstream source, ending in a written record. Sweeps are periodic — a source is swept again whenever it has moved or enough time has passed to be worth another look — and their records accumulate into a dated series, so what the workspace has already examined is a matter of record rather than of memory.

A sweep runs five steps, in order:

1. **Notice.** An upstream source surfaces: a repo not seen before, a bundle that has published new skills, or a standing entry due for another look.
2. **Pin.** Fix the state the comparison is made at — the upstream source repo and dev-playbook, each by commit SHA and that commit's timestamp. The pin is what lets the next sweep diff against exactly what this one saw.
3. **Compare.** Read each upstream skill against what the workspace already holds: the authored toolbox, the standards a skill answers to, and the earlier records in the series.
4. **Rule.** The human owner renders the verdict on each skill, against [When to adopt third-party skills](#when-to-adopt-third-party-skills). The verdict is the human's — an agent gathers, compares, and presents, and never decides.
5. **Record.** Write the sweep into the record series below.

## Sweep records

Every sweep lands exactly one record in `docs/skill-management/`, named `YYYY-MM-DD-<source>.md` for the date it ran and the source it swept, and listed in [the series index](/docs/skill-management/index.md).

A record declares `type: Survey` in its OKF frontmatter — it is an evaluative comparison gathered to inform the owner's verdict — and carries two parts:

- **A dual-SHA header.** Both repos as pinned in step 2 — the upstream source and dev-playbook, each with its commit SHA and that commit's timestamp.
- **One row per upstream skill.** The skill, how it compares against what the workspace already holds, and the human's verdict on it.

## When to adopt third-party skills

Adopt third-party skills only when their conventions integrate cleanly with existing canon. Otherwise harvest techniques into authored skills, not foreign skills into the toolbox.

Failure modes of piecemeal adoption from an opinionated framework: voice fragmentation across the toolbox, cross-reference fragility when only some skills from the bundle are installed, semantic drift on update (SHA-pinning catches byte-level changes, not meaning changes), and no clean convention boundary to separate "adopted skill" from "adopted worldview". If a specific gap becomes painful enough in real use, author a workspace-native skill incorporating the technique rather than importing the foreign skill.

## Locations

| Path under `dotfiles/` | Source | Editable |
|---|---|---|
| `dot-claude/skills/` | Authored in this workspace, plus symlinks mirroring `.agents/skills/` | Yes for authored entries; symlinks are managed by `scripts/sync-dotfiles` |
| `.agents/skills/` | Installed by the Vercel `skills` CLI | No — overwritten on update |

Stow links `dot-claude/` into `~/.claude/` and `.agents/` into `~/.agents/`, so Claude Code reads the canonical content from the git-tracked dotfiles tree.

## Mirror rule

Claude Code discovers skills only from `~/.claude/skills/`. Every entry under `.agents/skills/` `SHALL` have a corresponding symlink in `dot-claude/skills/` pointing at it (`dot-claude/skills/<name>` → `../../.agents/skills/<name>`), with no stale symlinks and no authored skill colliding with an `.agents/skills/` name.

Auditor and repairer are split, as [tracking](/standards/tracking.md) splits reporting from repair. The `claude-code.skill-mirror` rule in [skill-lint](/scripts/skill-lint) is the auditor: at the commit gate it reports any missing, mispointed, or stale symlink or authored/installed collision, and treats a committed `.agents/skills/` tree with no `dot-claude/skills/` mirror directory as an error state it fails loudly on. `scripts/sync-dotfiles` is the repairer: on every run it creates missing symlinks, removes stale ones (target no longer in `.agents/skills/`), and fails loudly if an authored skill collides with an `.agents/skills/` name.

After installing or removing a third-party skill (commands below), run `scripts/sync-dotfiles` to apply the mirror — from the main checkout only; it relinks live `~/.claude`, so it's a human step, never run from a per-issue worktree.

## Authored skills

Skills written for this workspace live in `dotfiles/dot-claude/skills/<skill-name>/`. Edit them in place. Restart Claude Code after edits — the running session caches skill content at startup. See [skill-conventions.md](/standards/claude-code/skill-conventions.md) for the format.

## Third-party skills

The Vercel `skills` CLI (npm package `skills`) is the canonical installer. It pulls from GitHub and pins each install to a tree SHA in `dotfiles/.agents/.skill-lock.json`. The lock file is the source of truth: each entry records source URL, skill path, tree SHA, and install timestamps.

```bash
# Install
npx skills@latest add OWNER/REPO --skill SKILL_NAME -g -y

# Update one (pulls latest commit, updates the pinned SHA)
npx skills@latest update SKILL_NAME -g

# Update all
npx skills@latest update -g

# List installed
npx skills@latest list -g

# Remove
npx skills@latest remove SKILL_NAME -g
```

Files under `dotfiles/.agents/skills/` are overwritten on the next `skills update`; edits there do not survive. To diverge a skill's behavior, fork its source repo and reinstall pointing at the fork.

## Decision hub

The Decision Hub registry (`dhub` CLI) is out of scope. Every skill available via DHub is also on GitHub and installable through the Vercel CLI.
