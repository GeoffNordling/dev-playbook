---
type: General-Sheet
title: Triage
description: The exit list of the detector rewrite — every deterministic rule, family by family, kept, rewritten, or deleted, with the user's rulings on the escalated rows
---

# Triage

The 150 deterministic rules, family by family, each kept, rewritten,
or deleted. This sheet is the specification the package is written to
([Detector Rewrite](/working-docs/doc-type-system/detector-rewrite/ROOT.md)).
A rule is cited by its id and the line of its heading.

## Method

- **Verdicts.** Keep: the sentence is plain and the check, where one
  exists, decides it. Rewrite: the sentence is restated plain, split,
  or merged; a null rule gains its check. Delete: the rule says
  nothing the user can read, binds something too small to matter, or
  restates another. Stochastic: the sentence is worth keeping and no
  function can decide it; the user rules on each.
- **Escalation.** A row the triager cannot settle goes to the user
  with the heading line, what the rule means in plain words, the
  proposal, and how the proposal differs from today's sentence and
  from today's enforcement. The user's rulings calibrate the rows
  that follow.
- **Plain rules.** A rewrite names the file, the value, and the
  comparison, per
  [Principles](/working-docs/doc-type-system/detector-rewrite/ROOT.md#principles).

## build

Twenty rules, `standards/build/`. Sixteen kept as written, the check
matching the sentence:

`files-every-repo-carries`, `one-at-the-root-or-none`,
`no-other-future-work-file`, `runnables-live-in-scripts`,
`dependencies-live-in-pyprojecttoml`,
`lock-file-tracked-python-version-pinned`, `one-package-under-src`,
`tests-present`, `ciyml-byte-identical-to-canonical`,
`python-version-byte-identical-to-canonical`,
`pre-commit-configyaml-holds-every-canonical-block`,
`makefile-holds-its-layers-targets`,
`pyprojecttoml-matches-every-pinned-value`,
`gitignore-holds-every-canonical-pattern`,
`the-repo-directory-names-the-project-and-package`,
`executable-scripts-carry-the-uv-shebang-and-inline-metadata`.

- **`every-entry-point-resolves-to-a-modules-main`**,
  `standards/build/python.md:24`. Keep, add the check: parse
  `[project.scripts]`, resolve each module inside the package, find
  `main` in its `ast`. The new console script makes this rule live.
- **`one-version-set`**, `standards/build/canonical.md:124`. Rewrite
  as two plain rules, each gaining a check. The Python version is
  written once: `.python-version` holds it, `requires-python` is `>=`
  it, `tool.ruff.target-version` is `py` plus it without the dot,
  `tool.mypy.python_version` equals it. The ruff version is written
  once: the ruff `rev` in the canonical `.pre-commit-config.yaml` and
  the `ruff>=` floor in the canonical `pyproject.toml` agree. Ruled
  2026-09-22.
- **`every-canonical-file-has-a-rule-and-every-rule-a-file`**,
  `standards/build/canonical.md:134`. Delete. It says no file in
  `canonical/` goes unnamed by a rule and no rule names a missing
  file; the second half is a broken link `ref-lint` already reports,
  the first is housekeeping a test over `sources.py` covers. Ruled
  2026-09-22.
- **`artifactsmk-lists-every-artifact-and-its-file-rule`**,
  `standards/build/canonical.md:64`. Delete. The one instance writes
  `$(WEB)/dist/index.html` on both sides, so only `make` can decide
  it. Ruled 2026-09-22.

## python

Four rules, `standards/python/style.md`.

- **`empty-init`**, `standards/python/style.md:22`. Keep.
- **`every-definition-carries-a-docstring`**,
  `standards/python/style.md:35`. Rewrite: replaced by one rule,
  ruff check reports nothing under the canonical configuration, the
  nine families `tool.ruff.lint.select` pins, `pep257` docstrings,
  line length and imperative summaries ignored, no docstrings under
  `tests/`. The docstring sentence becomes the Why. Relaxes the
  sentence to public, top-level definitions, which is what ruff
  enforces today and what the repo practises: 7 private and 6 nested
  definitions under `src/` carry none. Ruled 2026-09-22.
- **`no-future-annotations`**, `standards/python/style.md:47`.
  Rewrite: drop the `build`, `dist`, `deprecated` exception; the
  model reads tracked files only.
- **`formatted-by-ruff-format`**, `standards/python/style.md:58`.
  Keep, and fix the cause of its gap: ruff never opened an
  extensionless script, since pre-commit tags one `executable` and
  not `python`, and `ruff check .` filters on `*.py`. The canonical
  `pyproject.toml` gains `extend-include = ["scripts/*"]`, and the
  two ruff hooks in the canonical `.pre-commit-config.yaml` gain
  `types_or: [python, pyi, executable]`. Today that reformats three
  scripts and raises 48 findings under `scripts/`, most in files the
  rewrite deletes. Ruled 2026-09-22.

## Rulings that calibrate the rest

- **A rule about the checker itself is a test, not a rule.** Ruled on
  `build.every-canonical-file-has-a-rule-and-every-rule-a-file`.
  Applies to every rule whose member is dev-playbook's own checking
  code rather than a governed repo.
- **A rule the user cannot read is restated plain or deleted.** Three
  of the first three escalations were unreadable; two deleted, one
  restated as two.
- **A tool's own configuration is the rule.** Where ruff, shellcheck,
  or shfmt decides a rule, the rule says the tool reports nothing
  under the canonical configuration and names what that
  configuration selects. A sentence that promises more than the tool
  enforces is replaced, not kept beside it.
- **Fix the cause in this repo.** A gap that exists because a file
  never reaches the tool is closed in the canonical files, not by
  narrowing the rule. Consumer repos are not a reason to narrow.
