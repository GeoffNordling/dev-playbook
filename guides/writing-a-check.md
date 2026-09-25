---
type: Guide
title: Writing a Check
description: How a check that decides one rule is written — a function registered under the rule's id in the repo's src/<package>/checks/, with its test, run by playbook check in dev-playbook and by playbook check --local in a consumer's own hook; read before writing a check
---

# Writing a Check

A check is the verifier of one deterministic rule
([Checks](/standards/standard/checks.md)). Each check is one Python
function, registered under that rule's id, which `playbook check` runs
over the repo model. dev-playbook and a consumer repo write checks the
same way, in the same places, as they write Standards the same way:
`playbook check` runs dev-playbook's checks over every repo, and
`playbook check --local` runs a consumer's own checks, in the
consumer's own environment. The first sequence adds a check;
the sections after it say what the registry, the layer test, and
`playbook check` do with it.

## A new check lands in five steps

Each deterministic rule gets its check in this order, where
`<package>` is the repo's import package, `project.name` in its
`pyproject.toml` with hyphens as underscores: `dev_playbook` in
dev-playbook, `story_forge` in story-forge.

1. **Write the rule.** The rule is a heading in a Standard under
   `standards/<family>/`, with the trailer
   `` `<family>.<slug>` · deterministic `` below its predicate
   ([A rule: heading, predicate, trailer](/standards/doc-type/standard-conventions.md#a-rule-heading-predicate-trailer)).
   The trailer is the check's id: the rule `## No shadowing` in
   `standards/standard/tree.md` is `standard.no-shadowing`.
2. **Put the function in the family's module.** The rules of
   `standards/shell/` live in `src/<package>/checks/shell.py`, so
   dev-playbook's are in `src/dev_playbook/checks/shell.py`; a
   hyphenated family takes underscores, so `doc-type` is
   `checks/doc_type.py`. The decorator `@check("standard.no-shadowing")`,
   imported from `dev_playbook.check_registry`, registers the function
   under the id. The registry refuses an id registered twice, an id
   dev-playbook and the repo both register, an id not in
   `<family>.<slug>` form, and an id registered from another family's
   module.
3. **Read the model and yield findings.** The function takes a `Repo`
   and yields `Finding(path, line, message)`, with `line` as `None` for
   a finding on the whole file. It reads the model only; what the model
   holds, parsed markdown, `ast` trees, and raw bytes, is in
   [model.py](/src/dev_playbook/model.py).
   In dev-playbook, the module imports only `dev_playbook`, the
   standard library, and `yaml`, since the pinned hook's environment
   holds nothing else. A consumer's module may also import the
   consumer's own package and its dependencies, because
   `playbook check --local` runs in the consumer's environment: a
   story-forge check can import `story_forge` and run its code. Where the file or tree the rule
   governs is absent, the function yields nothing: dev-playbook's
   checks run in every repo, and `standard.no-shadowing` finds nothing
   in a repo with no `standards/` tree. In dev-playbook, data a
   Standard's body holds, such as the type registry table, is read
   through the named constants in `src/dev_playbook/sources.py`. A
   check that reads sibling repos on this machine carries
   `needs=[WORKSPACE]`, as `knowledge-organization.reference-resolves`
   does.
4. **Write its test.** The family's test file,
   `tests/<package>/checks/test_standard.py` for `standard`, holds a
   test named for the slug, `test_no_shadowing`. The test builds a repo
   with `Repo.from_files(Path("/r"), {path: bytes})` and asserts the
   findings the function yields, clean and failing both. A consumer
   repo's tests and its local hook import `dev_playbook`, so it lists
   dev-playbook as a dev dependency, sourced from git at the rev its
   pre-commit config pins
   ([A host's dev-playbook rides the pin](/standards/distribution/channel.md#a-hosts-dev-playbook-rides-the-pin)).
5. **Run the gates.** `make check` runs the test.
   `uv run playbook check .` runs dev-playbook's checks over the repo;
   in dev-playbook, the new check and the layer test run with them. In
   a consumer, `uv run playbook check --local .` runs the new check and
   the layer test.

## dev-playbook's layer is the example to copy

Before writing a check, read one family of dev-playbook's layer end to
end: the rules in
[channel.md](/standards/distribution/channel.md), their checks in
[distribution.py](/src/dev_playbook/checks/distribution.py), and their
tests in
[test_distribution.py](/tests/dev_playbook/checks/test_distribution.py).
Write a consumer's checks in the same shape:

- One module per family, holding its imports, its constants, its
  `@check` functions, and private `_` helpers, and nothing that runs on
  import.
- A check reads the model and yields findings; it writes no file, runs
  no process, and prints nothing.
- A test builds each repo it needs in memory with `Repo.from_files`,
  and asserts the findings of a clean repo and of each failing one.

A check that runs the consumer's own code keeps this shape: it passes
the model's bytes to the package's function and yields a finding for
each output the rule refuses.

## A rule a tool decides is registered by the hook's name

Where ruff, shellcheck, shfmt, or pre-commit's manifest validator
decides a rule, no function is written. The family's module registers
the id with the name of the hook that decides it:
`tool_check("shell.shellcheck-clean", hook="shellcheck", module=__name__)`
in `checks/shell.py`. `playbook checks` lists the entry with that hook,
and the layer test asks no test of it.

## The layer test holds the checks and the Standards together

The checks a repo hosts in `src/<package>/checks/` are its layer.
The run that loads the layer holds it and the repo's Standards together
in both directions, before it runs a check: `playbook check` in
dev-playbook, and `playbook check --local` in a consumer.

- Each check in the layer is a deterministic trailer in a Standard
  under `standards/<family>/`, under a heading whose slug is the id's
  slug.
- Each function in the layer has its test, `test_<slug>` in
  `tests/<package>/checks/test_<module>.py`.
- Each deterministic trailer under the repo's `standards/` is
  registered, by the repo or by dev-playbook.

Where one fails, the run names each mismatch and exits 2. A
stochastic rule has no check, and the layer test asks for none.
dev-playbook's own suite runs the same test over its layer in
`tests/dev_playbook/test_check_registry.py`.

## `playbook check` prints one line per finding

`playbook check [DIR]` builds the model once, loads dev-playbook's
checks, runs every registered function, and prints each finding on one
line:

```text
location:line: <rule id> message
```

The location is a repo-relative path, and `:line` is left out for a
finding on the whole file. A count of checks, files, and findings goes
to stderr. Then it runs one step that is not a function over the
model: `pre-commit validate-manifest` where the repo publishes a
`.pre-commit-hooks.yaml`. It exits 0 when the run is clean, 1 on any
finding, and 2 when the model or the layer cannot be loaded, the layer
test fails, or a step cannot run.

`playbook check --local [DIR]` runs the consumer's own layer the same
way, after the layer test, and runs no steps: the pinned hook runs
them. Over dev-playbook, `--local` exits 2, because dev-playbook's
layer is the one `playbook check` runs.

`--without workspace`, or `SKIP=workspace` in the environment, leaves
out the checks tagged `WORKSPACE` and says so on stderr.
`playbook checks [DIR]` lists every registered id of dev-playbook's
layer, or with `--local` of the consumer's, with its module and its
hook or tag; `--family` and `--without` filter the list.

## A consumer repo's checks run in its own hook

A consumer runs two hooks. The pinned `playbook-check` runs
dev-playbook's checks in the environment pre-commit builds for it,
which holds nothing of the consumer's, so a check dev-playbook adds
runs at the repo's next pin bump. A host, a consumer with its own
rules or checks, also lists `playbook-check-local` in a `repo: local`
block, which runs `playbook check --local` in the consumer's own
environment
([A host runs its own checks](/standards/distribution/channel.md#a-host-runs-its-own-checks)).
A check the repo adds runs there at its next commit, from the tracked
file. The repo adds checks and never removes one of dev-playbook's, as
it adds Standards and never shadows one. A check is the only way a
consumer gates its own rules: it publishes no hooks, and its
`repo: local` blocks list only `make-check` and `playbook-check-local`
([A consumer gates only through its checks](/standards/distribution/channel.md#a-consumer-gates-only-through-its-checks)).

## A check writes nothing

A check reads the model, which holds every tracked file in memory, and
yields findings; by itself it blocks nothing, and a gate is what
blocks
([Read-only without a write flag](/standards/standard/checks.md#read-only-without-a-write-flag)).
