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

### SDD standards (sdd-standards/)

Spec-driven development standards: philosophy, writing conventions, design layer, tooling. See [sdd-standards/README.md](sdd-standards/README.md).

| Object | Location | Purpose |
|--------|----------|---------|
| Spec standard | `sdd-standards/spec-standard.md` | Workspace spec standard: item anatomy, IDs, artifact types, coverage chain, keyword reference, obligation vocabulary, sentence templates, file organization |
| Design layer | `sdd-standards/design-layer.md` | Commitment scope and the four design decision dimensions (`Data`, `API Shape`, `Algorithms`, `Composition`) |
| Lessons | `sdd-standards/lessons.md` | Observations about the standard surfaced through use; resolutions land in the standard or its ADRs |

### Agent configuration (dotfiles/)

Symlinked to `$HOME` via GNU Stow. Run `dotfiles/bin/sync-dotfiles.sh` after adding or removing files.

| Object | Location | Purpose |
|--------|----------|---------|
| Claude Code skills | `dotfiles/.claude/skills/` | Workflow automation, tool wrappers, etc. |
| Global rules | `dotfiles/.claude/rules/` | Applied to every conversation |
| Global settings | `dotfiles/.claude/settings.json` | Model, permissions, hooks |
| Externally managed skills | `dotfiles/.agents/skills/` | Externally managed skills |

### Project template (project-template/)

| Object | Location | Purpose |
|--------|----------|---------|
| Cookiecutter template | `project-template/` | Bootstrap new Python projects with standard tooling |

### Tools (tools/)

CLI utilities for workspace automation. See [tools/README.md](tools/README.md) for detailed usage and reference.

| Object | Location | Purpose |
|--------|----------|---------|
| Standalone scripts | `tools/bin/` | `py-outline`, `ref-check`, `internal-skill-audit`, `test-privacy`, `workspace-backup`, `generate-pre-commit` |

### Spec tools (spec-tools/)

Programmatic representation of SDD spec artifacts: parse, traverse, modify, render. See [spec-tools/README.md](spec-tools/README.md).

| Object | Location | Purpose |
|--------|----------|---------|
| Specs | `spec-tools/specs/` | `feat` / `req` / `dsn` items the package is built against |
| Package | `spec-tools/src/spec_tools/` | In-memory model, deserialize, serialize, discover |

### SDD tools (sdd-tools/)

Deterministic validators and compressors for spec-driven development artifacts. See [sdd-tools/README.md](sdd-tools/README.md).

| Object | Location | Purpose |
|--------|----------|---------|
| Package | `sdd-tools/src/sdd_tools/` | Validators (lint, coverage, interface) + compression / reporting CLIs |
| pytest plugin | `sdd_tools.pytest_plugin` | hosts `spec-lint`, `spec-coverage`, `spec-interface` as `spec`-marked items |
| CLI tool | `sdd-chain` (`sdd_tools.cli.chain`) | Render spec traceability chains with body text |
| CLI tool | `sdd-index` (`sdd_tools.cli.index`) | Per-dimension one-line catalog of every `dsn` |
| CLI tool | `sdd-atlas` (`sdd_tools.cli.atlas`) | Per-dimension full-body dump of every `dsn` |
| CLI tool | `sdd-review` (`sdd_tools.cli.review`) | `AgentReview:` inventory for the review skill |
| Vendored JAR | `sdd-tools/lib/openfasttrace-4.2.2.jar` | OpenFastTrace JAR (gitignored) |
