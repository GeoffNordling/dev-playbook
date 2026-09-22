---
type: General-Sheet
title: Build
description: The triage of the build family's twenty deterministic rules — sixteen kept, one gaining its check, one split in two, two deleted, each ruled 2026-09-22
---

# Build

Twenty rules over three Standards under `standards/build/`. Done by
hand as the calibration sample, per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).

## skeleton.md

Kept as written, the check matching the sentence:
`files-every-repo-carries`, `one-at-the-root-or-none`,
`no-other-future-work-file`, `runnables-live-in-scripts`,
`dependencies-live-in-pyprojecttoml`,
`lock-file-tracked-python-version-pinned`, `one-package-under-src`,
`tests-present`.

## canonical.md

Kept as written, the check matching the sentence:
`ciyml-byte-identical-to-canonical`,
`python-version-byte-identical-to-canonical`,
`pre-commit-configyaml-holds-every-canonical-block`,
`makefile-holds-its-layers-targets`,
`pyprojecttoml-matches-every-pinned-value`,
`gitignore-holds-every-canonical-pattern`.

- **`one-version-set`**, `standards/build/canonical.md:124`. Rewrite,
  meaning changed by the split, two rules each gaining a check.
  Ruled 2026-09-22.

  > **The Python version is written once.** `.python-version` holds
  > the version. `requires-python` is `>=` that version,
  > `tool.ruff.target-version` is `py` plus that version with the dot
  > removed, and `tool.mypy.python_version` equals it.
  >
  > **The ruff version is written once.** The ruff `rev` in the
  > canonical `.pre-commit-config.yaml` and the `ruff>=` floor in the
  > canonical `pyproject.toml` carry the same version.

- **`every-canonical-file-has-a-rule-and-every-rule-a-file`**,
  `standards/build/canonical.md:134`. Delete. Plain, it says: no
  orphan file, every file in `canonical/` is named by a rule; no
  dangling name, every file a rule names exists. The second half is
  a broken link `ref-lint` already reports; the first is housekeeping
  over dev-playbook's own checker, which a test over `sources.py`
  covers. Ruled 2026-09-22.
- **`artifactsmk-lists-every-artifact-and-its-file-rule`**,
  `standards/build/canonical.md:64`. Delete. The one instance writes
  `$(WEB)/dist/index.html` on both sides, so only `make` can decide
  it. Ruled 2026-09-22.

## python.md

Kept as written, the check matching the sentence:
`the-repo-directory-names-the-project-and-package`,
`executable-scripts-carry-the-uv-shebang-and-inline-metadata`.

- **`every-entry-point-resolves-to-a-modules-main`**,
  `standards/build/python.md:24`. Keep, add the check: parse
  `[project.scripts]`, resolve each module inside the package, find
  `main` in its `ast`. The new console script makes this rule live.

## Escalations

All four ruled 2026-09-22 and folded into the rows above.

## New rules

None.

## Acronyms

None.
