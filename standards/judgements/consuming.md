---
type: Standard
title: Consuming Judgements
description: The consumer-repo recipe — editable path dependency, declarations, pytest gate, lint hook, cache fill
---

# Consuming Judgements

The judgements tooling ships in dev-playbook's one installable package,
**`dev-playbook`**, built from `src/dev_playbook/`. It exposes the
`dev_playbook.judgements` and `dev_playbook.skipcache` import packages and
the `judgements-run` / `judgements-lint` console scripts. Any repo on the
same machine consumes it as a **local path dependency** — no network, no
PyPI, no published index. The recipe below is
end-to-end; the field rules, config, and gate it points at are defined in
[declarations.md](/standards/judgements/declarations.md) and
[cache-gate.md](/standards/judgements/cache-gate.md).

## 1. Add the package as an editable path dependency

In the consuming repo's `pyproject.toml`, depend on `dev-playbook`
and point a `[tool.uv.sources]` entry at the dev-playbook repo root on disk:

```toml
[dependency-groups]
dev = ["dev-playbook"]

[tool.uv.sources]
dev-playbook = { path = "/home/geoff/workspace/dev-playbook", editable = true }
```

Adjust `path` to wherever `dev-playbook` sits **on disk**, and keep it
absolute. uv resolves a relative source path against the directory holding
the `pyproject.toml` being read, not the cwd — and an issue worktree
(`.claude/worktrees/issue-NN/`) carries its own copy of that file at a
different depth than the main checkout, so a relative spelling that
resolves in one breaks in the other. uv also expands neither `~` nor
`$HOME` in source paths. An absolute literal is the only spelling that
resolves from every checkout.

The dependency is `editable`, so the consumer always resolves against the
current `src/dev_playbook/` source — nothing to re-publish or re-pin when
the libraries change. `uv sync` builds the package with uv's own bundled
build backend, so building it needs no network or PyPI access. Its one
runtime dependency, `pyyaml`, resolves from uv's local cache whenever it is
present (it almost always is); only a completely cold cache reaches PyPI
for it. Afterwards
`from dev_playbook.judgements.pytest_support import assert_judgement_cached`
resolves in the consumer's environment and `judgements-run` is on its venv
PATH.

## 2. Declare the repo's judgements

Opt in exactly as
[declarations.md — Config and root resolution](/standards/judgements/declarations.md#config-and-root-resolution)
defines: a `[tool.judgements]` table in the consumer's own `pyproject.toml`
and one or more declaration YAML files in
[the YAML declaration format](/standards/judgements/declarations.md#the-yaml-declaration-format).

```toml
[tool.judgements]
paths = ["judgements/*.yaml"]
```

The root is the consumer's own repo — the nearest ancestor with a
`[tool.judgements]` table — and every evidence/reference path resolves
against it.

## 3. Gate the judgements in pytest

Add the cache gate as an ordinary test in the consumer's suite, using the
parametrized form from [cache-gate.md](/standards/judgements/cache-gate.md):

```python
import pytest
from dev_playbook.judgements.loader import load, resolve_root
from dev_playbook.judgements.pytest_support import assert_judgement_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgement_cached(jid):
    assert_judgement_cached(jid)
```

The check is deterministic and offline; it reads the same machine-local
seen-set the `run-judgements` skill fills, so it needs no LLM and no API key
on CI.

The gate is two-tier, keyed off one environment variable `SKIP_JUDGEMENTS` that
`assert_judgement_cached` reads ([cache-gate.md](/standards/judgements/cache-gate.md)):
exactly `1` skips the check with a visible pytest skip, any other value or
unset arms it. The canonical [Makefile](/standards/build/make.md) defaults it
to `1` and exports it, so `make check` and `make test` **skip** the gate — a
subagent running them never hits a miss only `run-judgements` (main loop) can
fill. `make check-judgements` runs `check` with `SKIP_JUDGEMENTS=0`, arming the
gate, and is the entry of the canonical pre-push hook: a miss blocks the push
until the cache is filled. A bare `uv run pytest` arms it too (fail-safe).

**Same-commit adoption.** A repo taking the new Makefile fragment `MUST`
repoint its pre-push hook to `make check-judgements` in the **same commit**.
Otherwise its `make check` stops running the gate while nothing at the push
enforces it — a window with zero mechanical enforcement.

## 4. Lint the declarations on commit

Add the `judgements-lint` pre-commit hook so malformed or stale declarations
fail fast. It ships from dev-playbook's published hook manifest; reference
it by URL and pinned `rev`, exactly as for the other dev-playbook hooks:

```yaml
- repo: https://github.com/GeoffNordling/dev-playbook
  rev: <commit-sha>
  hooks:
    - id: judgements-lint
```

The hook runs from pre-commit's own clone of dev-playbook at the pinned
`rev` and self-bootstraps its imports, so it needs neither the installed
package nor a checkout path — it is independent of the editable dependency
in step 1.

## 5. Fill the cache with the run-judgements skill

A cache miss — a failing gate — is filled by the global `run-judgements`
skill: it runs the LLM judge on each miss and records the passing verdicts
into the machine-local seen-set. The skill is available in any repo on the
machine; run it whenever the cache gate is red.
