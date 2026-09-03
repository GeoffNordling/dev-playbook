---
type: Standard
title: Detectors
description: The detector contract behind every Audit cell; read-only, wired throughout its scope, a formatter by its check mode, and the shim, git-environment, hosting, rule-id, output, and exit-code rules a first-party script obeys
population: "a detector: a read-only check an Audit cell cites, first-party at scripts/<name> or third-party by its pin"
---

# Detectors

A **detector** is the read-only check behind an Audit cell: it inspects
the repository against one or more Standards and emits findings, and by
itself it blocks nothing; its run at a gate is the audit stationed there,
which is Enforcement ([Vocabulary](/CONTEXT.md#governance),
[Gates](/standards/standard/gates.md)). A first-party detector is a
script the audited repo hosts at `scripts/<name>`; a third-party one,
`ruff`, `shellcheck`, `shfmt`, is cited by its bare name and pin
([Cells](/doc-types/standard-card/encoding.md#cells)). What an Audit cell
cites, and how, is
[Card Catalog](/standards/standard/cards.md#audit-cites-a-lint-or-an-audit).

## Read-only

A detector leaves everything git tracks as it found it; reading state
outside the working tree does not disqualify it.

workspace-lint queries GitHub over `gh api`, writes findings to stdout
and a summary to stderr, and changes nothing git tracks, so it is
read-only and belongs in an Audit cell.

## A formatter is a detector by its check mode

`shfmt -d` and `ruff format --check` report and mutate nothing, so the
tool is a detector an Audit cell cites; its write mode, `shfmt -w`,
stationed at the commit gate is Enforcement, never an audit.

## Wired throughout its scope

A detector runs over its whole governed population, a workspace-scoped
one in every repo and a repo-scoped one throughout its host repo, never a
subset; one whose surface is optional, skills or a `standards/` tree,
exits 0 silently when the surface is absent, and every other asserts
unconditionally and fails loud.

Applicability lives inside the detector, so a gap closes there and the
detector stays wired everywhere.

## A first-party detector

A script the audited repo hosts at `scripts/<name>`: in dev-playbook a
shim over `src/dev_playbook`, in a consumer repo the repo's own.

### Thin shims

The script is a thin shim over the host repo's reusable modules: the
logic lives in the module, and the script wires argument parsing and
output to it.

In dev-playbook the modules are `src/dev_playbook`. A Python file under
`scripts/` is also bound by
[Package-backed scripts are shims](/standards/build/python.md#package-backed-scripts-are-shims);
this rule binds a detector in any language.

### Explicit roots outrank the hook environment

A detector that shells out to git scrubs the repository-locating
variables `git rev-parse --local-env-vars` names from every subprocess
environment, leaving transport and auth settings such as
`GIT_SSH_COMMAND` in place, and its test suite clears the same set before
every test.

Detectors run at git gates, and a hook inherits an absolute `GIT_DIR`
whenever discovery from its own working directory would land on the
wrong repository: always from a linked worktree, where agent work
happens, and in submodule flows. The variable silently outranks
`git -C <root>` and the working directory in every child process,
redirecting git to the hook's repository instead of the audited one. A
plain clone's hook exports no absolute `GIT_DIR`, so its absence there is
no evidence the clause is stale. git names the set itself through
`git rev-parse --local-env-vars`, which stays correct across git
versions, and the set includes the `GIT_CONFIG_*` channel, through which
ad-hoc config relocates a repository as readily as `GIT_DIR` does.
dev-playbook detectors call `gitrepo.no_git_env`; a self-contained
consumer detector cannot import it and either carries its own copy or
runs `unset $(git rev-parse --local-env-vars)`, the remedy `githooks(5)`
documents. The same variable makes a bare `git init` a silent no-op,
which is why the test suite clears the set (an autouse fixture in
`tests/conftest.py`).

### The hosting pattern

The script lives at `scripts/<name>`, is published in the repo's own
`.pre-commit-hooks.yaml`, is mirrored in its `repo: local` block, is
cited by a card's Audit cell, and carries a row in `scripts/README.md`'s
validation table when the repo has that file; standards-lint reports a
missing leg (`standard.hook-surfaces`).

dev-playbook is the topmost instance of the pattern. A repo that ships a
manifest runs what it ships from its own local block; that invariant is
stated once, in
[Distribution Channel](/standards/distribution/channel.md#the-local-block-covers-the-manifest).

### Card-namespaced rule ids

Every finding carries a rule id of the form `card.rule`, namespaced by
the card whose question it answers and named after that question rather
than the tool that detects it; every prefix the script emits belongs to a
card whose Audit cell cites it, and every such citation is backed by at
least one id with that card's prefix (`standard.rule-matrix`).

Question and mechanism cross-cut: one card is cited by several
detectors, and one detector by several cards. The one-to-one invariant
sits a level down, at the rule: every `card.rule` id belongs to exactly
one card.

### `--list-rules`

The script answers `--list-rules`, printing every `card.rule` id it can
emit, one per line.

standards-lint runs it to build the rule matrix, so the printed set is
the ground truth the matrix joins on.

### Finding format

A finding is one line in GNU format, `file:line: card.rule message`: a
colon after the location, single spaces, a repo-relative path, and
`:line` omitted for a file-level finding.

`README.md: knowledge-organization.doc-shape missing an H1 title` is a
file-level finding.

### Exit codes

The script exits 0 when clean, 1 when it has findings, and 2 when it
cannot run.

### Verbatim content

The script excludes a document typed `Reference`, a verbatim copy of an
upstream external one, by consulting the shared registry
`src/dev_playbook/external.py` (`is_verbatim_doc`), so every detector
excludes the same documents.

Such a document is not the repo's to hold to the authored-content
standards. One registry is what keeps the exclusion from drifting into an
unsynced, undocumented per-detector skip list.
