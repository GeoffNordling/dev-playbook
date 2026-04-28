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
uv run pytest
make lint
make format
make typecheck
```
