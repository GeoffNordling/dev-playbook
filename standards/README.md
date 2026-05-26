# Standards

Cross-project engineering standards that apply to all repositories in the workspace.

> Spec-driven development standards live in [`~/workspace/spec-tools/sdd-standards/`](~/workspace/spec-tools/sdd-standards/README.md).

## Contents

| Standard | Purpose |
|----------|---------|
| [repo-documentation.md](repo-documentation.md) | What files every repo should have, their scope, CONTEXT.md format, and cross-reference style |
| [adr-conventions.md](adr-conventions.md) | When to write an ADR, the template, numbering, and optional sections |
| [skill-conventions.md](skill-conventions.md) | Conventions for Claude Code skill bundles |
| [skill-management.md](skill-management.md) | Where skills live and how third-party skills are installed |
| [architecture-vocabulary.md](architecture-vocabulary.md) | Shared vocabulary for module architecture: Module, Interface, Depth, Seam, Adapter, Leverage, Locality |
| [module-design.md](module-design.md) | Module design rules: principles, deep modules, designing for testability |
| [dependency-taxonomy.md](dependency-taxonomy.md) | Dependency categories (in-process, local-substitutable, remote-but-owned, true-external) and seam discipline |
| [python-conventions.md](python-conventions.md) | Default Python conventions and anti-pattern catalog |
| [python-project-conventions.md](python-project-conventions.md) | Python project structure, `pyproject.toml` shape, and tool config |
| [testing-conventions.md](testing-conventions.md) | Default pytest conventions: structure, test doubles, fixtures |
| [build-conventions.md](build-conventions.md) | Standard `Makefile` targets (`format`, `lint`, `typecheck`, `test`, `check`) for Python sub-projects |
