# Standards

Cross-project engineering standards that apply to all repositories in the workspace.

> Spec-driven development standards live in [`~/workspace/spec-tools/sdd-standards/`](~/workspace/spec-tools/sdd-standards/README.md).
>
> Shared architecture vocabulary lives in the repo-root [`CONTEXT.md`](../CONTEXT.md).

## Contents

| Standard | Purpose |
|----------|---------|
| [doc-conventions.md](doc-conventions.md) | How Markdown documents in workspace repos are written (voice, structure, brevity, current-state-only) |
| [repo-documentation.md](repo-documentation.md) | What files every repo should have, their scope, CONTEXT.md format, and cross-reference style |
| [repo-settings.md](repo-settings.md) | GitHub repository settings every repo should have: squash-only merges, auto-delete merged branches |
| [adr-conventions.md](adr-conventions.md) | When to write an ADR, the template, numbering, and optional sections |
| [issue-conventions.md](issue-conventions.md) | Issue body format, brief principles, and vertical-slice rules — applied at intake |
| [skill-conventions.md](skill-conventions.md) | Conventions for Claude Code skill bundles |
| [skill-management.md](skill-management.md) | Where skills live and how third-party skills are installed |
| [module-design.md](module-design.md) | Module design rules: principles, deep modules, designing for testability |
| [python-conventions.md](python-conventions.md) | Default Python conventions and anti-pattern catalog |
| [python-project-conventions.md](python-project-conventions.md) | Python project structure, `pyproject.toml` shape, and tool config |
| [testing-conventions.md](testing-conventions.md) | Default pytest conventions: structure, test doubles, fixtures |
| [build-conventions.md](build-conventions.md) | Standard `Makefile` targets (`format`, `lint`, `typecheck`, `test`, `check`) for Python sub-projects |
