---
type: Standard-Ruleset
title: Detectors
description: The detector contract behind every Audit cell — read-only, clean on an absent surface, and the shim, git-root, hosting, rule-id, output, and exit-code rules a first-party script obeys
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
([Cells](/doc-types/standard/encoding.md#cells)). What an Audit cell
cites, and how, is
[Card Catalog](/standards/standard/cards.md#audit-cites-a-lint). The
reasoning behind the rules is the
[Standard Guide](/docs/guides/standard.md).

## Read-only

A detector leaves everything git tracks as it found it.

`standard.read-only` · deterministic

## An absent surface is clean

A detector whose surface is optional, a `skills/`, `standards/`, or
`loops/` tree, exits 0 and reports no finding in a repo that has no such
surface.

`standard.an-absent-surface-is-clean` · deterministic

## A first-party detector

The detector is a script the audited repo hosts at `scripts/<name>`.

`standard.a-first-party-detector` · deterministic

### Thin shims

The script holds no rule logic of its own: it puts the host repo's
package on the import path and calls that package's entry point.

`standard.thin-shims` · deterministic

### Git runs against the given root

A first-party detector that runs git addresses the repository it was
given even when its environment carries an absolute `GIT_DIR` that names
another repository.

`standard.git-runs-against-the-given-root` · deterministic

### The hosting pattern

A first-party detector is published as a hook in its repo's
`.pre-commit-hooks.yaml`, is cited by a card's Audit cell, and has a row
in the validation table of `scripts/README.md` where the repo has that
file.

`standard.the-hosting-pattern` · deterministic

### Offered by the canonical template

A first-party detector in the repo that carries
`standards/build/canonical/` is a hook of that canonical
`.pre-commit-config.yaml`'s pinned block.

`standard.offered-by-the-canonical-template` · deterministic

### Card-namespaced rule ids

Every rule id a first-party detector emits has the form `<card>.<rule>`,
where `<card>` names a card whose Audit cell cites the detector, and
every card whose Audit cell cites the detector has at least one emitted
id with its prefix.

`standard.card-namespaced-rule-ids` · deterministic

### List rules

A first-party detector answers `--list-rules` by printing every rule id
it can emit, one per line, and exiting 0.

`standard.list-rules` · deterministic

### Finding format

A finding is one line, `location:line: <rule id> message`: a colon after
the location, single spaces, the location a repo-relative path, or the
member's name where the member is not a file, and `:line` omitted for a
finding on the whole member.

`standard.finding-format` · deterministic

### Exit codes

A first-party detector exits 0 when clean, 1 when it has findings, and 2
when it cannot run.

`standard.exit-codes` · deterministic
