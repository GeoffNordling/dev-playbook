---
type: Guide
title: Adopting a Repo-Scoped Standard
description: The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish its checks as one hook, mirror it, and gate it
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
   with a check in the shape
   [Writing a Check](/guides/writing-a-check.md#a-consumer-repos-checks-take-the-same-shape)
   gives: one function per rule id, one test per id, and one command
   that runs them all, prints one line per finding, and exits 0 clean,
   1 on findings, 2 when it cannot run.
3. **Publish the hook in the repo's own manifest.** Add that command as
   one hook to the consumer repo's own `.pre-commit-hooks.yaml`, the
   same way dev-playbook publishes `playbook-check`. The repo is now
   the topmost instance of the hosting pattern for its own standard.
4. **Mirror the hook in the local block.** Add the same hook id to the
   repo's `repo: local` block in `.pre-commit-config.yaml`, so the repo
   runs from its working tree what it publishes
   ([A publisher dogfoods its manifest](/standards/distribution/channel.md#a-publisher-dogfoods-its-manifest));
   `distribution.a-publisher-dogfoods-its-manifest` checks
   the mirror.
5. **Turn the meta-standard's own policing on.** The meta-standard's
   checks run in `playbook-check`, a published dev-playbook hook. Bump
   the pin to a dev-playbook `rev` that carries them: from that rev
   they run over the repo's `standards/` tree
   (`playbook checks --family standard` lists them). Until the pin
   moves, the tree is unpoliced by the meta-standard.
6. **Register a local document type (only if the standard needs one).**
   Skip this step unless the new standard governs a **document type**
   the global OKF registry does not carry. If it does, declare the type
   in the frontmatter of the repo's root `index.md`, an `okf_types`
   mapping beside `okf_version`:

   ```yaml
   ---
   okf_version: "0.1"
   okf_types:
     Resume: A resume markdown source, master or batch variant
     Story: One work-experience story in SPAR form
   ---
   ```

   The type check unions those names onto the
   [global registry](/standards/knowledge-organization/document-types.md).
   The mapping's rules, the entry shape, alphabetical keys,
   add-never-shadow, and name and description only, are
   [Type Registry](/standards/knowledge-organization/type-registry.md#local-declaration).
   Nothing goes under the repo's own `standards/` tree for this: that
   tree is the meta-standard's, and a registry document in it could not
   pass its checks.
