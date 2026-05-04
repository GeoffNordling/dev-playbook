# spec-tools

In-memory model of SDD spec artifacts: parse, traverse, modify, render.

See [`sdd-standards/`](../sdd-standards/) for the spec standard.

## Layout

- `specs/` — `feat` / `req` / `dsn` items, by module
- `src/spec_tools/` — implementation
- `tests/`

## Setup

```bash
cd spec-tools && uv sync
```

## Development

```bash
make check       # format --check + lint + typecheck + test
make format      # apply formatter fixes
```

See [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md)
for the standard target definitions.
