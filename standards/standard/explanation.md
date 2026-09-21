---
type: Explanation
title: Standard Explanation
description: The thinking behind the meta-standard's rules — why one directory holds one standard, what a detector is and is not, why an absent surface is clean, why a detector must ignore the GIT_DIR a git hook exports, and where a check runs
---

# Standard Explanation

The reasoning behind the meta-standard, the rulesets under
`standards/standard/`: the vocabulary and the reasons that make the
rules intelligible.

## The tree

One directory, one standard: the files that state one standard's rules
and the explanation behind them sit together, one documentation set
([Documentation Sets](/standards/knowledge-organization/documentation-sets/documentation-sets.md)),
so a reader who finds one finds the rest. The sentence each directory's
index opens with is the catalog's row, so the two are one text kept in
two places by a rule rather than by habit. A consumer's
`standards/<name>/` on a name dev-playbook publishes would silently
override the workspace-scoped standard of that name, which is why the
name is reserved; the two scopes are
[Scope](/doc-types/standard/definition.md#scope).

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

### One rule id, one check

A rule id is `<name>.<slug>`, the heading of the rule that declares it,
named by the question the Standard governs and not by the tool that
checks it. Question and mechanism cross-cut: one Standard is checked by
several detectors, and one detector checks for several Standards. The
one-to-one fact sits at the rule: every id is decided by at most one
check, and the verifier table is where that fact is written down. Nothing
maintains the table by hand; a generator derives it from the rule
headings, each detector's `--list-rules`, and the dependency map, and the
same derivation is the lint, so the table cannot drift from either side
([The verifier table](/standards/standard/detectors.md#the-verifier-table),
[List rules](/standards/standard/detectors.md#list-rules)). A null row is
an honest one: the rule is stated and nothing decides it yet.

### Where a check runs

Which gate runs a check is wiring: a hook's stage in
`.pre-commit-config.yaml`, a line in `make check`, a `run` step in a
workflow. A Standard that stated its own enforcement could be wrong
about it and nothing would notice, so no Standard says where it runs.
The boundary table, `standards/boundaries.yaml`, is derived from the
wiring by the same generator that lints it, and the four gate names are
its column set: **commit**, the pre-commit stage at `git commit`;
**push**, the pre-push stage at `git push`, which runs `make check`;
**CI**, the canonical workflow on every push and pull request to
`main`; and **on-demand**, a registered audit no gate runs, which the
user invokes by hand. A pre-commit hook reaches every gate, since
`make check` and the workflow both run the suite; `mypy` and `pytest`
run only inside `make`, so they reach the push gate and never CI
([The boundary table](/standards/standard/detectors.md#the-boundary-table)).
The commit and push gates are git hooks in `.git/`, which no clone
inherits; `uvx pre-commit install` puts them there, step 4 of
[Bootstrap](/guides/bootstrap.md#the-existing-path-adoption).

### A skip is machine state

A detector is skipped at a gate only where its input is machine-local
rather than held in the repository: `SKIP=ref-lint` where the repos its
Citations resolve against are not cloned
([A skip is machine state](/standards/standard/detectors.md#a-skip-is-machine-state)).
playbook-lint honors `SKIP`
per detector name and announces the skip on every run. The canonical
workflow's `SKIP: ref-lint` is in the boundary table, since the workflow
is committed; a machine's skip is not, and is recorded in
[Machines](/docs/machines.md) instead.

### Verbatim mirrors

A document typed `Reference` is a verbatim copy of an upstream text and
is not the repo's to hold to the authored-content rules. The exclusion
is stated once, in the population of
[Doc Conventions](/standards/prose/conventions.md), and the detectors
read it from one place, `src/dev_playbook/external.py`, so no detector
keeps a skip list of its own.
