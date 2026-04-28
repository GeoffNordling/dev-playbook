# Skill Management

Where Claude Code skills live in this workspace, and how they are installed, updated, and removed. For the format of skills authored in this workspace, see [skill-authoring.md](~/workspace/dev-playbook/standards/skill-authoring.md).

## Locations

| Path under `dotfiles/` | Source | Editable |
|---|---|---|
| `.claude/skills/` | Authored in this workspace | Yes — these are the source |
| `.agents/skills/` | Installed by the Vercel `skills` CLI | No — overwritten on update |

Stow links these directories into `~/` so the canonical content lives in the git-tracked dotfiles tree.

## Authored Skills

Skills written for this workspace live in `dotfiles/.claude/skills/<skill-name>/`. Edit them in place. Restart Claude Code after edits — the running session caches skill content at startup. See [skill-authoring.md](~/workspace/dev-playbook/standards/skill-authoring.md) for the format.

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
