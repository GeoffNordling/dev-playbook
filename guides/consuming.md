---
type: Guide
title: Adopting a Repo-Scoped Standard
description: The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write its checks where dev-playbook keeps its own, wire the local hook that runs them, and bump the pin
---

# Adopting a Repo-Scoped Standard

Most standards a repo runs are workspace-scoped: inherited from
dev-playbook through its published hooks, governing every repo alike. A
repo with a convention no other repo shares declares its own
**repo-scoped** standard, the same tree-and-check machinery the
meta-standard ([standards/standard/](/standards/standard/index.md))
defines, hosted in the consumer repo instead of dev-playbook. The recipe
below is the order of operations; every rule a step meets is stated once,
in the Standard the step links.

## Adoption runs tree to gate

1. **Grow the `standards/` tree.** If the repo has no `standards/` tree
   yet, create its landing doc first: `standards/README.md`
   (`type: README`) and `standards/index.md`, with the README listed
   first. Add the standard's directory `standards/<name>/`, holding the
   **Standard**, a file typed `Standard` at
   `standards/<name>/<topic>.md` with its `population` and its rules,
   and an `index.md` whose opening sentence states the directory's
   remit; register the directory in the catalog, its row carrying that
   sentence. The layout, the population, the rule shape, the catalog
   order, and the name are
   [The Standards Tree](/standards/standard/tree.md): a name no
   dev-playbook directory carries
   ([No shadowing](/standards/standard/tree.md#no-shadowing)), and the
   README-first catalog
   ([The catalog lists every directory](/standards/standard/tree.md#the-catalog-lists-every-directory)).
2. **Write the checks.** Back each deterministic rule of the Standard
   with a check in `src/<package>/checks/<name>.py` and its test in
   `tests/<package>/checks/test_<name>.py`, the same places dev-playbook
   keeps its own
   ([Writing a Check](/guides/writing-a-check.md)).
3. **Wire the local hook.** The `playbook-check` hook the repo already
   pins runs dev-playbook's checks only. The repo's own checks run in a
   second hook in its own environment, so they can import the repo's
   package and its dependencies. Add this block to
   `.pre-commit-config.yaml`
   ([A host runs its own checks](/standards/distribution/channel.md#a-host-runs-its-own-checks)):

   ```yaml
   - repo: local
     hooks:
       - id: playbook-check-local
         name: playbook check --local
         entry: uv run --locked playbook check --local
         language: system
         pass_filenames: false
         always_run: true
   ```

   The hook runs the dev-playbook in the repo's environment, so list
   it as a dev dependency, sourced from git at the `rev` the
   dev-playbook block of `.pre-commit-config.yaml` pins, then run
   `uv lock`
   ([A host's dev-playbook rides the pin](/standards/distribution/channel.md#a-hosts-dev-playbook-rides-the-pin)):

   ```toml
   [dependency-groups]
   dev = [
       # ...
       "dev-playbook",
   ]

   [tool.uv.sources]
   dev-playbook = { git = "https://github.com/GeoffNordling/dev-playbook", rev = "<the pinned sha>" }
   ```

   `uv run playbook checks --local --family <name>` lists the new
   checks. `bump-pin` and `update-pins` move this `rev` with the
   pre-commit `rev` from then on.
4. **Bump the pin.** Bump the pin to a dev-playbook `rev` that has
   `playbook check --local`. Until the pin moves, the new Standard is
   unchecked.
5. **Register a local OKF type (only if the standard needs one).**
   Skip this step unless the new standard governs an **OKF type** that
   dev-playbook's
   [OKF Type Registry](/registries/okf-types.md#okf-types) does not
   carry. If it does, declare the type in the repo's own
   `registries/okf-types.md`, typed `Registry` and listed by
   `registries/index.md`, in a table of the same shape:

   ```markdown
   ## OKF types

   | OKF type | What it is |
   |----------|------------|
   | `Resume` | A resume markdown source, master or batch variant |
   | `Story` | One work-experience story in SPAR form |
   ```

   The type check unions those rows onto dev-playbook's registry. The
   table's rules, the row shape, alphabetical rows, and
   add-never-shadow, are
   [Local OKF Types](/standards/knowledge-organization/local-okf-types.md#local-declaration).
