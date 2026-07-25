---
type: Standard
title: Canonical Artifacts
description: The canonical artifacts — the single-source files under standards/build/canonical/ and how each repo copy is compared
---

# Canonical Artifacts

The standard's machine-checkable content lives **once**, as files in
dev-playbook under `standards/build/canonical/`,
shipped inside every hook clone
([distribution.md](/standards/build/distribution.md)). Prose points at them
and does not restate their contents — the files are the standard. Each
repo's working copies exist because the consuming tools demand real files in
place, and `repo-lint` enforces them equal to the canonical source:

| Artifact | Compared how |
|---|---|
| [ci.yml](/standards/build/canonical/ci.yml) | whole file, byte-identical |
| [.python-version](/standards/build/canonical/.python-version) | whole file, byte-identical |
| [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml) | canonical blocks present verbatim; extra hooks may follow |
| [Makefile.base](/standards/build/canonical/Makefile.base) / [Makefile.python](/standards/build/canonical/Makefile.python) / [Makefile.aws](/standards/build/canonical/Makefile.aws) / [Makefile.sdd](/standards/build/canonical/Makefile.sdd) | the repo's layer-matching targets present verbatim; extra targets may follow |
| [pyproject.toml](/standards/build/canonical/pyproject.toml) | pinned values match, parsed from TOML; additions are free |
| [.gitignore](/standards/build/canonical/.gitignore) | baseline lines present |

`standards/build/canonical/` is quoted material: hooks and tree rules skip it —
its `pyproject.toml` is a template, not a second project. Every file in the
directory is compared against by `repo-lint`; a file that no tool checks
does not belong there.

## One config serves every repo

The canonical [.pre-commit-config.yaml](/standards/build/canonical/.pre-commit-config.yaml)
carries the pinned `playbook-lint` hook — dev-playbook's whole detector set
behind one id ([distribution.md](/standards/build/distribution.md)) — the
ruff, shellcheck, and shfmt hooks at canonical revs, and the pre-push
`make check-judgments` hook, installing both the commit and push stages. It
serves every repo unchanged: a hook with no matching files skips itself, and
detectors like `judgments-lint` and `skill-lint` pass trivially where a repo
has no `[tool.judgments]` table and no authored skills — which is why the
roster can run everywhere without per-repo opt-ins. dev-playbook
replaces the published block with its dogfood block
([distribution.md](/standards/build/distribution.md#dogfooding)).

## Versions

One version set for the whole workspace: the Python interpreter
(`.python-version`), ruff, mypy, pytest, and every hook `rev` are defined
once, in the canonical artifacts — latest stable, identical in all repos,
bumped deliberately; that one floor reaches each standalone script's PEP 723
`requires-python`, not just `pyproject.toml`. Exact resolutions live in each
repo's `uv.lock`.
