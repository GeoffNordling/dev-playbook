---
type: Guide
title: Writing a Check
description: How a check that decides one rule is written — a function registered under the rule's id in the repo's src/<package>/checks/, with its test, run by playbook check in dev-playbook and in every consumer repo alike; read before writing a check
---

# Writing a Check

A check is the verifier of one deterministic rule
([Checks](/standards/standard/checks.md)). Each check is one Python
function, registered under that rule's id, which `playbook check` runs
over the repo model. dev-playbook and a consumer repo write checks the
same way, in the same places, as they write Standards the same way:
`playbook check` runs dev-playbook's checks over every repo, and a
consumer's own checks beside them. The first sequence adds a check;
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
   a finding on the whole file. It reads the model only:
   `repo.markdown[path]` for a parsed markdown file, with its
   frontmatter, headings, trailers, and links; `repo.python[path]` for
   an `ast` tree; `repo.contents` and `repo.text(path)` for the rest.
   The module imports only `dev_playbook`, the standard library, and
   `yaml`, since `playbook check` runs it in the hook's environment,
   where nothing else is installed. Where the file or tree the rule
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
   repo's tests import `dev_playbook`, so it lists dev-playbook as a
   dev dependency at the rev its hook pins.
5. **Run the gates.** `make check` runs the test;
   `uv run playbook check .` runs the new check over the repo, and the
   layer test with it.

## A rule a tool decides is registered by the hook's name

Where ruff, shellcheck, shfmt, or pre-commit's manifest validator
decides a rule, no function is written. The family's module registers
the id with the name of the hook that decides it:
`tool_check("shell.shellcheck-clean", hook="shellcheck", module=__name__)`
in `checks/shell.py`. `playbook checks` lists the entry with that hook,
and the layer test asks no test of it.

## The layer test holds the checks and the Standards together

The checks a repo hosts in `src/<package>/checks/` are its layer.
`playbook check` holds the layer and the repo's Standards together in
both directions, before it runs a check:

- Each check in the layer is a deterministic trailer in a Standard
  under `standards/<family>/`, under a heading whose slug is the id's
  slug.
- Each function in the layer has its test, `test_<slug>` in
  `tests/<package>/checks/test_<module>.py`.
- Each deterministic trailer under the repo's `standards/` is
  registered, by the repo or by dev-playbook.

Where one fails, `playbook check` names each mismatch and exits 2. A
stochastic rule has no check, and the layer test asks for none.
dev-playbook's own suite runs the same test over its layer in
`tests/dev_playbook/test_check_registry.py`.

## `playbook check` prints one line per finding

`playbook check [DIR]` builds the model once, loads dev-playbook's
checks and the repo's layer, runs every registered function, and
prints each finding on one line:

```text
location:line: <rule id> message
```

The location is a repo-relative path, and `:line` is left out for a
finding on the whole file. A count of checks, files, and findings goes
to stderr. Then it runs two steps that are not functions over the
model: the loop family's `loop_lint` module, and
`pre-commit validate-manifest` where the repo publishes a
`.pre-commit-hooks.yaml`. It exits 0 when the run is clean, 1 on any
finding, and 2 when the model or the layer cannot be loaded, the layer
test fails, or a step cannot run.

`--without workspace`, or `SKIP=workspace` in the environment, leaves
out the checks tagged `WORKSPACE` and says so on stderr.
`playbook checks [DIR]` lists every registered id of both layers with
its module and its hook or tag; `--family` and `--without` filter the
list.

## A consumer repo's checks ride dev-playbook's hook

A consumer repo publishes no hook for its checks. The
`playbook-check` hook it already pins loads its layer from the working
tree, so a check the repo adds runs at its next commit, and a check
dev-playbook adds runs at the repo's next pin bump. The repo adds
checks and never removes one of dev-playbook's, as it adds Standards
and never shadows one.

## A check writes nothing

A check reads the model, which holds every tracked file in memory, and
yields findings; by itself it blocks nothing, and a gate is what
blocks
([Read-only without a write flag](/standards/standard/checks.md#read-only-without-a-write-flag)).
