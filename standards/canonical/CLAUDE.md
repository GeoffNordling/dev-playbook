# <repo-name>

## Rules

- See README.md for what this project is.

## Build

`make check` runs the full check surface. See
[make.md](~/workspace/dev-playbook/standards/build/make.md).

## Domain awareness

- Before exploring code, read `CONTEXT.md` and any ADRs in `docs/adr/` touching the area you'll work in. If `CONTEXT.md` is absent, proceed silently — don't flag it or suggest creating it.
- Name domain concepts (issue titles, refactor proposals, hypotheses, test names) using terms defined in `CONTEXT.md`. If a needed concept isn't there, decide: inventing language the project doesn't use (reconsider) or real gap (flag for `/grill-with-docs`).
- If your output contradicts an existing ADR, surface it: `_Contradicts ADR-NNNN — but worth reopening because…_`.
