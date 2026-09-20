---
type: Guide
title: Standard Guide
description: The thinking behind the meta-standard's rules — what a detector is and is not, why an absent surface is clean, and why a detector must ignore the GIT_DIR a git hook exports
---

# Standard Guide

The guide behind the meta-standard, the Standards under
`standards/standard/`. Each states its rules as predicates a reviewer or
a script can decide; this guide carries the vocabulary and the reasoning
that make the rules intelligible. Nothing here is enforced; every rule
is in its Standard.

## Detectors

A **detector** is a read-only check. It reads the repository, compares
it with one or more Standards, and prints findings. By itself it blocks
nothing. When a detector runs at a gate, its findings stop the path to
main; that run is enforcement, the detector is not
([Detectors](/standards/standard/detectors.md)).

### Reading is not writing

A detector may read state outside the working tree and stay read-only.
workspace-lint queries GitHub over `gh api`, prints findings to stdout
and a summary to stderr, and changes nothing git tracks
([Read-only](/standards/standard/detectors.md#read-only)).

### A formatter has two modes

A formatter's check mode, `shfmt -d` or `ruff format --check`, reports
and changes nothing, so in that mode the tool is a detector. Its write
mode, `shfmt -w`, changes files; that mode is enforcement, never an
audit.

### Applicability lives inside the detector

A detector for an optional surface, a `skills/`, `standards/`, or
`loops/` tree, runs in every repo and exits clean where the surface is
absent
([An absent surface is clean](/standards/standard/detectors.md#an-absent-surface-is-clean)).
The alternative, removing the hook from repos that lack the surface,
would make the hook set differ from repo to repo and leave a repo
unpoliced the day it grows the surface. So the gap closes inside the
detector, and the wiring stays the same everywhere.

### Why a detector must ignore the hook's `GIT_DIR`

When git runs a hook, it sometimes exports the variable `GIT_DIR`,
pointing at the repository the hook belongs to. It always does so when
the hook fires in a linked worktree, which is where agent work happens.
Every git command the detector then runs inherits that variable, and
`GIT_DIR` outranks both the working directory and an explicit
`git -C <root>`. The result is silent: a detector told to audit one
repository reads another and reports on it.

The fix is the one `githooks(5)` documents: before running git, remove
the variables `git rev-parse --local-env-vars` lists from the child's
environment. Asking git for the list keeps it correct as git versions
change, keeps transport and auth settings such as `GIT_SSH_COMMAND` in
place, and includes the `GIT_CONFIG_*` channel, which can relocate a
repository as readily as `GIT_DIR` can. dev-playbook's detectors do this
through `gitrepo.no_git_env()`; a self-contained consumer detector
carries its own copy or runs `unset $(git rev-parse --local-env-vars)`.
The test suite clears the same set before every test, because under an
ambient `GIT_DIR` a bare `git init` silently does nothing
([Git runs against the given root](/standards/standard/detectors.md#git-runs-against-the-given-root)).

### One rule id, one card

A rule id is `<card>.<rule>`, named by the question the card governs and
not by the tool that checks it. Question and mechanism cross-cut: one
card is checked by several detectors, and one detector checks for
several cards. The one-to-one fact sits at the rule: every id belongs to
exactly one card
([Card-namespaced rule ids](/standards/standard/detectors.md#card-namespaced-rule-ids)).
`--list-rules` prints the ids a detector can emit, so the set a detector
claims is the set standards-lint joins on
([List rules](/standards/standard/detectors.md#list-rules)).

### Verbatim mirrors

A document typed `Reference` is a verbatim copy of an upstream text and
is not the repo's to hold to the authored-content rules. The exclusion
is stated once, in the population of
[Doc Conventions](/standards/prose/conventions.md), and the detectors
read it from one place, `src/dev_playbook/external.py`, so no detector
keeps a skip list of its own.
