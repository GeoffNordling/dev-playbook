---
type: General-Sheet
title: Build Rulings
description: The build family agent's work order — every rule under standards/build/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Build Rulings

The work order of the `build` family agent: every rule under `standards/build/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `build.ciyml` | build/canonical.md | keep | deterministic |  |
| `build.python-version` | build/canonical.md | keep | deterministic |  |
| `build.pre-commit-configyaml` | build/canonical.md | keep | deterministic |  |
| `build.makefile` | build/canonical.md | keep | deterministic |  |
| `build.artifactsmk` | build/canonical.md | keep | deterministic |  |
| `build.pyprojecttoml` | build/canonical.md | keep | deterministic |  |
| `build.gitignore` | build/canonical.md | keep | deterministic |  |
| `build.one-version-set` | build/canonical.md | rewrite | deterministic | Sentence: Every version the canonical artifacts pin in more than one file carries the same value in each<br>Why: The pins are meant to be the latest stable releases, bumped together; that is why a version pinned in two files must agree. |
| `build.the-source-directory` | build/canonical.md | keep | deterministic |  |
| `build.name-mapping` | build/python.md | rewrite | deterministic | Sentence: The root `pyproject.toml` sets `project.name` to the repository's own name lowercased, the directory holding the shared `.git` and so the same from the main checkout and every worktree, `My-Repo` to `my-repo`, and the import package is that name with each hyphen an underscore, `my_repo`. |
| `build.entry-points` | build/python.md | rewrite | deterministic | Sentence: `[project.scripts]` in the root `pyproject.toml` is absent, or every entry under it has the value `<module>:main`, where `<module>` is a module inside the import package and that module defines `main`. |
| `build.scripts` | build/python.md | condition |  |  |
| `build.shebang-and-inline-metadata` | build/python.md | keep | deterministic |  |
| `build.required-files` | build/skeleton.md | keep | deterministic |  |
| `build.root-only-files` | build/skeleton.md | keep | deterministic |  |
| `build.no-other-future-work-file` | build/skeleton.md | keep | deterministic |  |
| `build.runnables-live-in-scripts` | build/skeleton.md | keep | deterministic |  |
| `build.dependencies-live-in-pyprojecttoml` | build/skeleton.md | keep | deterministic |  |
| `build.python` | build/skeleton.md | condition |  |  |
| `build.uvlock-and-python-version` | build/skeleton.md | keep | deterministic |  |
| `build.python-package` | build/skeleton.md | condition |  |  |
| `build.one-package-under-src` | build/skeleton.md | keep | deterministic |  |
| `build.python-source` | build/skeleton.md | condition |  |  |
| `build.tests-present` | build/skeleton.md | keep | deterministic |  |
| `build.javascript` | build/skeleton.md | condition |  |  |
| `build.lockfile-committed` | build/skeleton.md | delete |  |  |

## Acronyms

None.
