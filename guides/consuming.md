---
type: Guide
title: Adopting a Repo-Scoped Standard
description: The consumer-repo recipe for a first repo-scoped standard — grow the standards/ tree, write and publish a conforming detector, mirror it, and gate it
---

# Adopting a Repo-Scoped Standard

Most standards a repo runs are workspace-scoped: inherited from
dev-playbook through its published hooks, governing every repo alike. A
repo with a convention no other repo shares declares its own
**repo-scoped** standard, the same tree-and-detector machinery the
meta-standard ([standards/standard/](/standards/standard/index.md))
defines, hosted in the consumer repo instead of dev-playbook. The recipe
below is the order of operations; every rule a step meets is stated once,
in the Standard the step links.

## Declare, publish, and gate the standard

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
   ([The catalog](/standards/standard/tree.md#the-catalog)).
2. **Write a contract-conforming detector.** Back the Standard's rules
   with a detector, a `scripts/<name>` shim over the repo's own reusable
   modules, obeying the first-party rules in
   [Detectors](/standards/standard/detectors.md#a-first-party-detector):
   read-only, one finding per line in GNU format with rule-heading ids,
   answering `--list-rules`, exit 0 clean, 1 findings, 2 cannot run.
   The one clause invisible until a hook runs is
   [Git runs against the given root](/standards/standard/detectors.md#git-runs-against-the-given-root):
   the commit gate is a git hook, and from a linked worktree it exports
   an absolute `GIT_DIR`, so anyone working the way this workspace does
   meets the clause immediately.
3. **Publish the hook in the repo's own manifest.** Add the hook to the
   consumer repo's own `.pre-commit-hooks.yaml`, backed by the
   `scripts/<name>` entry, the same way dev-playbook publishes its hooks
   ([The hosting pattern](/standards/standard/detectors.md#the-hosting-pattern)).
   The repo is now the topmost instance of the hosting pattern for its
   own standard.
4. **Mirror the hook in the local block.** Add the same hook id to the
   repo's `repo: local` block in `.pre-commit-config.yaml`, so the repo
   runs from its working tree what it publishes
   ([The local block covers the manifest](/standards/distribution/channel.md#a-publisher-dogfoods-its-manifest));
   repo-lint's `distribution.a-publisher-dogfoods-its-manifest` checks
   the mirror.
5. **Record the detector in the two tables.** The local-block wiring
   runs the detector at the **commit gate**. Which rule the detector
   decides is the verifier table, `standards/verifiers.yaml`
   ([The verifier table](/standards/standard/detectors.md#the-verifier-table)),
   and where it runs is the boundary table, `standards/boundaries.yaml`,
   read from the wiring
   ([The boundary table](/standards/standard/detectors.md#the-boundary-table)).
6. **Turn the meta-standard's own policing on.** The meta-standard's
   detector, `standards-lint`, is a published dev-playbook hook. Bump
   the pin to a dev-playbook `rev` that carries it: from that rev it
   runs the consumer-mode rules over the repo's `standards/` tree
   (`standards-lint --list-rules` is the registry). Until the pin
   moves, the tree is unpoliced by the meta-standard.
7. **Register a local document type (only if the standard needs one).**
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

   okf-lint unions those names onto the
   [global registry](/standards/knowledge-organization/document-types.md).
   The mapping's rules, the entry shape, alphabetical keys,
   add-never-shadow, and name and description only, are
   [Type Registry](/standards/knowledge-organization/type-registry.md#local-declaration).
   Nothing goes under the repo's own `standards/` tree for this: that
   tree is the meta-standard's, and a registry document in it could not
   pass standards-lint.
