---
type: General-Sheet
title: Build
description: The rewrite of the build family's twenty deterministic rules — eighteen checks over the model, sixteen ported, one restated from a split, one new, two deleted per their rulings, one Standard edited to the triage, and nothing retired
---

# Build

The step built `src/dev_playbook/checks/build.py` and
`tests/dev_playbook/checks/test_build.py` from
[the build triage](/working-docs/doc-type-system/detector-rewrite/triage/build.md).
`scripts/repo-lint` still decides every build rule it decided before,
the deleted source-directory rule included; it retires in Step 11.

The canonical rules read their source from the model, under
`sources.CANONICAL_DIR`. Only a repo that tracks that directory,
dev-playbook, has the source in its model, so in any other repo those
seven checks compare nothing. A consumer keeps its canonical compares
through `repo-lint` until the canonical files reach the installed
package; that must land before Step 11 retires `repo-lint`.

## Built

skeleton.md, kept as written:

- `build.files-every-repo-carries`: `files_every_repo_carries`.
- `build.one-at-the-root-or-none`: `one_at_the_root_or_none`.
- `build.no-other-future-work-file`: `no_other_future_work_file`.
- `build.runnables-live-in-scripts`: `runnables_live_in_scripts`.
- `build.dependencies-live-in-pyprojecttoml`:
  `dependencies_live_in_pyprojecttoml`.
- `build.lock-file-tracked-python-version-pinned`:
  `lock_file_tracked_python_version_pinned`.
- `build.one-package-under-src`: `one_package_under_src`.
- `build.tests-present`: `has_tests`, since a module-level name opening
  with `tests` is collected by pytest when the test file imports it.

canonical.md, kept as written:

- `build.ciyml-byte-identical-to-canonical`: `ciyml_byte_identical`.
- `build.python-version-byte-identical-to-canonical`:
  `python_version_byte_identical`.
- `build.pre-commit-configyaml-holds-every-canonical-block`:
  `holds_every_canonical_block`.
- `build.makefile-holds-its-layers-targets`:
  `makefile_holds_its_layers_targets`.
- `build.pyprojecttoml-matches-every-pinned-value`:
  `pyprojecttoml_matches_every_pinned_value`.
- `build.gitignore-holds-every-canonical-pattern`:
  `gitignore_holds_every_canonical_pattern`.
- `build.one-version-set`: `one_version_set`, restated. The two
  paragraphs of the triage's blockquote replace the old body under the
  one heading, and the one function decides both halves over the
  canonical source: the Python version against `requires-python`,
  `tool.ruff.target-version`, and `tool.mypy.python_version`, and the
  ruff `rev` against the `ruff>=` floor. The Why stays.

python.md:

- `build.the-repo-directory-names-the-project-and-package`:
  `names_the_project_and_package`, kept as written. It asks git for
  the repository's name, the one input the model does not carry.
- `build.every-entry-point-resolves-to-a-modules-main`:
  `entry_points_resolve_to_main`, the new check. It parses
  `[project.scripts]`, resolves each module under `src/`, and finds a
  top-level `main` in its `ast`.
- `build.executable-scripts-carry-the-uv-shebang-and-inline-metadata`:
  `carry_the_uv_shebang`, kept as written.

`sources.CANONICAL_FILES` names the seven files directly under the
canonical directory, and a test in `test_sources.py` pins the set to
the tree. That test is the one the triage says covers the orphan half
of the deleted source-directory rule.

## Deleted

- `build.artifactsmk-lists-every-artifact-and-its-file-rule`: heading,
  body, trailer, and Why removed from `standards/build/canonical.md`.
  No link pointed at the heading.
- `build.every-canonical-file-has-a-rule-and-every-rule-a-file`:
  heading, body, and trailer removed from
  `standards/build/canonical.md`. No link pointed at the heading.

Neither rule was named by the Standard's `description`, the
directory's `index.md`, or its row in `standards/index.md`, so none
changed.

## Retired

None.

## Set aside

None.

## Measured

- `uv run playbook check .`: 0.40 s, 35 checks over 454 files, zero
  findings.
- `scripts/playbook-lint .`: 0.23 s, clean.

## Acronyms

- PEP: Python Enhancement Proposal.
