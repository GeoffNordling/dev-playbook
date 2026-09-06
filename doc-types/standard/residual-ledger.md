---
type: General-Sheet
title: Standard Residual Ledger
description: Standard's residual record — what one population and its rules cannot express, one entry per Standard that has one
---

# Standard Residual Ledger

Standard's residual record: what
[one population and its rules](/doc-types/standard/contract-shape.md)
cannot express. That is all an entry is — a record.

## Standards

Per Standard ported to the encoding: what the rewrite could not
express, recognized and written down at the moment of porting. Entries
name populations, rules, and conditions in the vocabulary
[encoding.md](/doc-types/standard/encoding.md) declares.

An entry is a couple of sentences, hard limit: name each specific thing
the file could not express and why the shape cannot say it, nothing
else. A Standard with nothing to record has no entry.

### build/skeleton

Could not express `tests/` as a rule under the union of two layers,
Python package or Python scripts, since a rule binds under one
condition; it sits under its own condition, Python source, whose test
restates the union. Could not name the base layer: a rule under no
condition shows `—`, and the view carries no name for the set every
rule binds.

### build/canonical

Could not express the compare strength, byte-identical, blocks
verbatim, or values parsed, as data on the member; it lives only in
each rule's predicate. Could not express the `pyproject.toml` fork on
`src/` as two conditioned rules without splitting one artifact's compare
in two; the fork is two clauses of one predicate.

### build/python

Could not express the shebang rule's antecedent, an executable file, as
a condition, since the condition Scripts already tests presence under
`scripts/` and a rule takes one condition; the antecedent sits inside
the predicate.

### prose/conventions

Could not express the tics by name: No slop tics points at the catalog,
so the fifteen names sit below the view, the way the canonical files'
contents sit below Canonical Artifacts.

### standard/gates

Could not express a population of three fixed members: the phrase names
the class, and the three are named only in the Three rungs predicate.
Could not express the red-CI rule over a gate's state: its object is a
pull request, so it binds a member outside the population.

### distribution/channel

Could not express one class of object: the population spans four kinds
of state, a manifest, a local block, a pin, and the roster, joined only
by the repo that holds them. Could not express the roster rule over an
object in a tree: its member is one line of workspace-lint's source.

### tracking/candidates

Could not express The only future-work file over the member: its objects
are the rogue `ROADMAP.md` and its kin elsewhere in the tree, so it binds
a member outside the population, the way Gates' red-CI rule does.

### tracking/issue-shapes

Could not express Build leaf, Spike, and Session leaf as subsets of Leaf:
conditions do not nest, so each restates the leaf test with its mode. Could not express
the wayfinder body shape at all: the rule is the `/wayfinder` skill's,
and the half of `tracking.wayfinder-shape` that checks a map's sections
has no rule row.

### instrument/format

Could not express one class of object: the population is an
instrument, while The Instrument Spec and Employed by bind its spec and
Readings binds its artifacts, so three rules bind members outside the
population, the way Gates' red-CI rule does.

### tracking/repo-settings

Could not express GitHub origin over the member: the remote is the
clone's, and the settings it opens are the population, so the rule binds
the object that makes the population readable.

### shell/conventions

Could not express the shell file that is neither executable nor sourced:
the two conditions test a mode bit and a path, and there is no
"otherwise", so a mode-644 script run as `bash <file>` falls under no
condition and is bound only by the rules under `—`.

### python/style

Could not express Formatted by ruff format and Annotated signatures over
the member alone: each binds one file's bytes, but the threshold, the
`line-length` and the `[tool.mypy]` keys, lives in the canonical
`pyproject.toml`, so each predicate points outward. Could not express
the two halves of Docstrings, presence and plain English, as two rules,
since one heading carries one predicate.

### testing/conventions

Could not express the member as one kind of file: the population names
a `test_*.py` anywhere plus the `conftest.py` files and fakes under
`tests/`, because Conftest hierarchy and Fakes live in the test tree
bind objects no test file is. Could not express Behavioral focus as a
name: it frames five rules without being a member subset, so its
sentence sits in the lead prose and the view carries no name for the
group.

### modules/design

Could not express the process-boundary antecedent as a condition: it
holds one rule, so it sits inside the predicate of A port at a process
boundary, the way `build/python` keeps the executable-file antecedent.
Could not express the vocabulary the rules are written in as a rule:
Module, Interface, and Implementation sit in the lead prose, the other
five terms in the body of the rule that first uses each, and the view
carries none of them.

### decisions/records

Could not express the contiguity half of Sequential numbering over one
member: a gap is a property of the whole directory, which is why
decisions-lint reports it against `docs/decisions/` and not a file.
Could not express The directory over the member: its object is the
directory that holds the population, the way Repository Settings'
GitHub origin binds the clone. Could not express the obligation that a
deliberate external evaluation ends in a record: its object is the
evaluation, an event, so it binds outside the population the way
Candidates' The only future-work file does.

### semantic-validation/declarations

Could not express one class of object: the population spans a TOML
table, a YAML file, and an entry, joined only by the repo that holds
them, the way `distribution/channel` does. Could not name the bench
values: Fields points at `bench.py`, the way No slop tics points at the
catalog. Could not express that a claim still holds of its evidence:
that state is a fact about files outside the population, and only the
LLM judge rules on it.

### harness/claude-content

Could not express One scope over one member alone: a nested file's
delta compares it to the files above it. Could not name the global
source in the population phrase without its path: no other mark picks
it out.

### harness/runbook-conventions

Could not express the invocation mode as a condition without three
restated conditions, so the fork sits inside Description's predicate.
Could not give the no-`SKILL.md` directory and the 500-line advisory a
lint partner: both emit no rule id. Could not give Carries its chain an
Audit pointer: `chaingen --check` answers no `--list-rules`.

### standard/cards

Could not express one class of object: the population is the cards and
the index listing them, joined only by the tree. Could not express the
dev-playbook meta-card lead slot as a condition; it is a clause of The
catalog.

### standard/detectors

Could not express Verbatim content over a consumer's script: it names
`src/dev_playbook/external.py`, which only dev-playbook imports. Could
not express the optional-surface fork of Wired throughout its scope as
a condition: it is a fact about the population, not the detector.
