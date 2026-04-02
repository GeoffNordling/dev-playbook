# dev-playbook

Geoff's meta repo — standards, agent configuration, and project templates that govern all repositories in the workspace.

## Some past wisdom

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

## What does NOT belong here

- Project-specific documentation — put it in that project's repo
- CLI tools or scripts — those go in dev-tools
- Application code

## The workspace

All repos live under a single root directory: `/Volumes/workplace/` on the work Mac, `~/workspace/` on the personal Windows/WSL machines. Two meta repos govern everything else:

- **dev-playbook** (this repo) — standards, agent configuration, and project templates
- **dev-tools** — CLI tools and shared libraries for workspace automation

## What's in this repo

### Standards

| Object | Location | Purpose |
|--------|----------|---------|
| Repo documentation | `standards/repo-documentation.md` | Required/optional files for every repo and their scope |
| Development workflow | `standards/development-workflow.md` | Issues, branches, draft PRs, spec-driven development |
| Spec-driven development | `standards/spec-driven-development.md` | How specs are written (EARS, RFC 2119, requirement IDs, traceability) |
| Ideas backlog | `ideas/README.md` | Unprocessed ideas for research or implementation |

### Agent configuration (dotfiles/)

Symlinked to `$HOME` via GNU Stow. Run `dotfiles/bin/sync-dotfiles.sh` after adding or removing files.

| Object | Location | Purpose |
|--------|----------|---------|
| Claude Code skills | `dotfiles/.claude/skills/` | Workflow automation, dev-tools wrappers, etc. |
| Global rules | `dotfiles/.claude/rules/` | Applied to every conversation |
| Global settings | `dotfiles/.claude/settings.json` | Model, permissions, hooks |
| Externally managed skills | `dotfiles/.agents/skills/`, `dotfiles/.dhub/skills/` | Externally managed skills |

### Project template (project-template/)

| Object | Location | Purpose |
|--------|----------|---------|
| Cookiecutter template | `project-template/` | Bootstrap new Python projects with standard tooling |
