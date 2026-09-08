---
type: Decision-Record
title: Retire Instruments
description: Delete the Instruments standard, the Instrument-Spec type, and both instruments — the file graph and the datasheet — in favor of one live browser view of a repository, keeping their ideas and none of their framing
date: 2026-09-07
status: accepted
---

# Retire Instruments

Two instruments existed under a standard of their own: the file graph, a
deterministic typed graph of every file rendered as a force diagram, and
the datasheet, an agent-written HTML report that nothing in this repo ever
produced. Both specs read "Employed by: No standard", both wrote committed
readings that lagged the repository by design, and the standard's rules
bound the spec and the readings rather than the instrument they named as
their population. The decision: delete the standard, the `Instrument-Spec`
type, the `instruments/` and `readings/` directories, the `datasheet`
skill, and the `file-graph` executor, and build in their place one live
browser view of a repository. The ideas survive — total accounting of every file, typed edges with a status,
reachability and orphan queries, click-to-read source, the owner who never
reads the code, and a fixed word budget per view — and the file graph's
code is reused from history where it fits; the framing of a spec per
device, a reading per run, and a consumer that must name itself does not.

## Considered Options

- **Keep the standard and remake the instruments under it.** Rejected: the
  standard governed the wrapper — the spec, the Employed-by section, the
  readings directory — and none of the wrapper is wanted.
- **Grow the view inside the file graph.** Rejected: the force graph is
  one component of the view, answering connectivity questions; the primary
  view is the index tree, which the graph never modeled.

## Consequences

- okf-lint loses one rule, `instrument.employed-by`, and the registry loses
  the type it fired on; a consumer repo that typed a document
  `Instrument-Spec` is flagged for an unregistered type once it takes this
  revision.
- The rulings table in [Doc-Type System](/doc-types/doc-type-system.md)
  loses its Instrument-Spec row.
- The deleted files stay readable at the tag `before-retire-instruments`,
  the last commit on main that carries them — for one file,
  `git show before-retire-instruments:instruments/file-graph.md`. The
  deleted paths: `standards/instrument/`, `instruments/`, `readings/`,
  `dotfiles/dot-claude/skills/datasheet/`, `scripts/file-graph`,
  `src/dev_playbook/filegraph/`, and `tests/test_filegraph.py`.
