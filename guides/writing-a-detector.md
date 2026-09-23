---
type: Guide
title: Writing a Detector
description: How a check that decides one rule is written — in dev-playbook a function registered under the rule's id, with its test, and in a consumer repo the same shape behind the repo's own hook; read before writing a check
---

# Writing a Detector

A detector decides one or more deterministic rules
([Detectors](/standards/standard/detectors.md)). In dev-playbook each
one is a check: one Python function that decides one rule, registered
under that rule's id, which `playbook check` runs over the repo model.
The first sequence adds a check to dev-playbook; the sections after it
say what the registry, the meta-test, and `playbook check` do with it,
and the shape a consumer repo's own checks take.

## A new check lands in five steps

Each deterministic rule gets its check in this order:

1. **Write the rule.** The rule is a heading in a Standard under
   `standards/<family>/`, with the trailer
   `` `<family>.<slug>` · deterministic `` below its predicate
   ([A rule: heading, predicate, trailer](/standards/doc-type/standard-conventions.md#a-rule-heading-predicate-trailer)).
   The trailer is the check's id: the rule `## No shadowing` in
   `standards/standard/tree.md` is `standard.no-shadowing`.
2. **Put the function in the family's module.** The rules of
   `standards/shell/` live in `src/dev_playbook/checks/shell.py`; a
   hyphenated family takes underscores, so `doc-type` is
   `checks/doc_type.py`. The decorator `@check("standard.no-shadowing")`
   registers the function under the id. The registry refuses an id
   registered twice, an id not in `<family>.<slug>` form, and an id
   registered from another family's module.
3. **Read the model and yield findings.** The function takes a `Repo`
   and yields `Finding(path, line, message)`, with `line` as `None` for
   a finding on the whole file. It reads the model only:
   `repo.markdown[path]` for a parsed markdown file, with its
   frontmatter, headings, trailers, and links; `repo.python[path]` for
   an `ast` tree; `repo.contents` and `repo.text(path)` for the rest.
   Where the file or tree the rule governs is absent, the function
   yields nothing, since the one hook runs in every repo: `standard.no-shadowing`
   finds nothing in a repo with no `standards/` tree. Data a Standard's
   body holds, such as the type registry table, is read through the
   named constants in `src/dev_playbook/sources.py`. A check that reads
   sibling repos on this machine carries `needs=[WORKSPACE]`, as
   `knowledge-organization.reference-resolves` does.
4. **Write its test.** The family's test file,
   `tests/dev_playbook/checks/test_standard.py` for `standard`, holds a
   test named for the slug, `test_no_shadowing`. The test builds a repo
   with `Repo.from_files(Path("/r"), {path: bytes})` and asserts the
   findings the function yields, clean and failing both.
5. **Run the gates.** `make check` runs the test and the meta-test;
   `uv run playbook check .` runs the new check over this repo.

## A rule a tool decides is registered by the hook's name

Where ruff, shellcheck, shfmt, or pre-commit's manifest validator
decides a rule, no function is written. The family's module registers
the id with the name of the hook that decides it:
`tool_check("shell.shellcheck-clean", hook="shellcheck", module=__name__)`
in `checks/shell.py`. `playbook checks` lists the entry with that hook,
and the meta-test asks no test of it.

## The meta-test holds the registry and the Standards together

`tests/dev_playbook/test_check_registry.py` reads the registry and
every rule trailer under `standards/`, in both directions:

- Each registered id is a deterministic trailer in a Standard under
  `standards/<family>/`, under a heading whose slug is the id's slug.
- Each entry has a function or a hook, never both.
- Each function has its test, `test_<slug>` in
  `tests/dev_playbook/checks/test_<module>.py`.
- Each deterministic trailer under `standards/` is registered.

A stochastic rule has no check, and the meta-test asks for none.

## `playbook check` prints one line per finding

`playbook check [DIR]` builds the model once, runs every registered
function, and prints each finding on one line:

```text
location:line: <rule id> message
```

The location is a repo-relative path, and `:line` is left out for a
finding on the whole file. A count of checks, files, and findings goes
to stderr. Then it runs two steps that are not functions over the
model: the loop family's `loop_lint` module, and
`pre-commit validate-manifest` where the repo publishes a
`.pre-commit-hooks.yaml`. It exits 0 when the run is clean, 1 on any
finding, and 2 when the model cannot be built or a step cannot run.

`--without workspace`, or `SKIP=workspace` in the environment, leaves
out the checks tagged `WORKSPACE` and says so on stderr.
`playbook checks` lists every registered id with its module and its
hook or tag; `--family` and `--without` filter the list.

## A check writes nothing

A check reads the model, which holds every tracked file in memory, and
yields findings; by itself it blocks nothing, and its run at a gate is
the audit stationed there
([Read-only without a write flag](/standards/standard/detectors.md#read-only-without-a-write-flag)).

## A consumer repo's checks take the same shape

`playbook check` runs dev-playbook's checks over a consumer repo, and
only those: its registry holds dev-playbook's families alone. A
consumer repo with a repo-scoped Standard
([Adopting a Repo-Scoped Standard](/guides/consuming.md)) writes its
own checks for that Standard's deterministic rules, in the shape
above:

- One function per rule, named by the rule's id, reading the repo and
  yielding findings.
- One test per id, and a meta-test that holds the ids and the
  Standard's trailers together in both directions.
- One command that runs every function, prints each finding in the
  line above, and exits 0, 1, or 2.
- That command published as one hook in the repo's
  `.pre-commit-hooks.yaml` and run from its `repo: local` block, as
  dev-playbook publishes `playbook-check`.
