# dev-playbook

Standards, agent configuration, project templates, and CLI tools for a multi-repo workspace.

> *"Often, when we find a recurring problem, something that happens over and over again, we pull the team together, ask them to try harder, do better – essentially, we ask for good intentions. This rarely works… When you are asking for good intentions, you are not asking for a change… because people already had good intentions. But if good intentions don't work, what does? Mechanisms work."*  
> — Amazon leadership principles
>
> *"…to succeed in executing spontaneous and unconscious technique, it is necessary to train in it in a highly conscious fashion."*  
> — Miyamoto Musashi
>
> *"A little bit of slope makes up for a lot of intercept."*  
> — John Osterhaus, Stanford Lecture

## What belongs here

- Cross-project standards and conventions
- Formal standards governing the workspace
- Agent configuration (skills, rules, settings)
- Project templates
- CLI tools and shared libraries for workspace automation

## What does NOT belong here

- Project-specific documentation — put it in that project's repo
- Application code

## The workspace

All repos live under a single root directory: `~/workspace/`. One meta repo governs everything else: **dev-playbook** (this repo).

## What's here

### Protocols (protocols/)

| Object | Location | Purpose |
|--------|----------|---------|
| Align, Map, Execute | `protocols/align-map-execute/` | Structured human-agent collaboration on large-scope tasks |

### Standards

| Object | Location | Purpose |
|--------|----------|---------|
| Repo documentation | `standards/repo-documentation.md` | Required/optional files for every repo and their scope |
| Skill conventions | `standards/skill-conventions.md` | Conventions for Claude Code skill bundles |
| Python conventions | `standards/python-conventions.md` | Default Python conventions + the anti-pattern catalog the `code-quality-sweep` skill scans for |
| Testing conventions | `standards/testing-conventions.md` | Default pytest conventions: structure, doubles, fixtures |

### SDD standards and spec-tools

The workspace SDD standard and its companion Python package now live in their
own repo: [`~/workspace/spec-tools/`](~/workspace/spec-tools/). See
[ADR-0001 in spec-tools](~/workspace/spec-tools/docs/adr/0001-extracted-from-dev-playbook.md)
for the extraction record.

### Agent configuration (dotfiles/)

Symlinked to `$HOME` via GNU Stow. Run `dotfiles/bin/sync-dotfiles.sh` after adding or removing files.

| Object | Location | Purpose |
|--------|----------|---------|
| Claude Code skills | `dotfiles/.claude/skills/` | Workflow automation, tool wrappers, etc. |
| Global rules | `dotfiles/.claude/rules/` | Applied to every conversation |
| Global settings | `dotfiles/.claude/settings.json` | Model, permissions, hooks |
| Externally managed skills | `dotfiles/.agents/skills/` | Externally managed skills |

### Tools (tools/)

CLI utilities for workspace automation. See [tools/README.md](tools/README.md) for detailed usage and reference.

| Object | Location | Purpose |
|--------|----------|---------|
| Standalone scripts | `tools/bin/` | `py-outline`, `ref-check`, `internal-skill-audit`, `test-privacy`, `workspace-backup` |

