# dotfiles

Claude Code configuration — skills, rules, settings, and hooks — managed via GNU Stow.

Stow symlinks the contents of this directory into `$HOME`, so `~/.claude/`, `~/.agents/`, and `~/.dhub/` all point back here.

## Structure

```
.claude/
  skills/      Claude Code skills (SDD workflow, commit-push, dev-tools wrappers, etc.)
  rules/       Global rules applied to every conversation
  settings.json          Global Claude Code settings (model, permissions, hooks)
.agents/skills/    Externally managed skills
.dhub/skills/      Externally managed skills
bin/
  sync-dotfiles.sh   Stow sync — run after adding or removing files
```

## Workflow

1. Edit files here (never chase symlinks into `~/.claude/`)
2. Run `bin/sync-dotfiles.sh` after adding or removing files
3. Edits to existing files take effect immediately (already symlinked)
