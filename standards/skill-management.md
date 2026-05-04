# Skill Management

Where Claude Code skills live in this workspace, and how they are installed, updated, and removed. For the format of skill bundles in this workspace, see [skill-conventions.md](~/workspace/dev-playbook/standards/skill-conventions.md).

## Locations

| Path under `dotfiles/` | Source | Editable |
|---|---|---|
| `.claude/skills/` | Authored in this workspace, plus symlinks mirroring `.agents/skills/` | Yes for authored entries; symlinks are managed by `bin/sync-dotfiles.sh` |
| `.agents/skills/` | Installed by the Vercel `skills` CLI | No — overwritten on update |

Stow links these directories into `~/` so the canonical content lives in the git-tracked dotfiles tree.

## Mirror rule

Claude Code discovers skills only from `.claude/skills/`. Every entry under `.agents/skills/` `SHALL` have a corresponding symlink in `.claude/skills/` pointing at it (`.claude/skills/<name>` → `../../.agents/skills/<name>`). `bin/sync-dotfiles.sh` enforces this on every run: it creates missing symlinks, removes stale ones (target no longer in `.agents/skills/`), and fails loudly if an authored skill collides with an `.agents/skills/` name.

After installing or removing a third-party skill (commands below), run `bin/sync-dotfiles.sh` to apply the mirror.

## Authored Skills

Skills written for this workspace live in `dotfiles/.claude/skills/<skill-name>/`. Edit them in place. Restart Claude Code after edits — the running session caches skill content at startup. See [skill-conventions.md](~/workspace/dev-playbook/standards/skill-conventions.md) for the format.

## Third-Party Skills

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

Don't edit files under `dotfiles/.agents/skills/` — they're overwritten on the next `skills update`. To diverge a skill's behavior, fork its source repo and reinstall pointing at your fork.

## Decision Hub

The Decision Hub registry (`dhub` CLI) is out of scope. Every skill available via DHub is also on GitHub and installable through the Vercel CLI.
