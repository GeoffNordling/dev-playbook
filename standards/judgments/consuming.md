---
type: Standard
title: Consuming Judgments
description: The consumer-repo recipe — editable path dependency, declarations, pytest gate, lint hook, cache fill
---

# Consuming Judgments

The judgments tooling ships in dev-playbook's one installable package,
**`dev-playbook`**, built from `src/dev_playbook/`. It exposes the
`dev_playbook.judgments` and `dev_playbook.skipcache` import packages and
the `judgments-run` / `judgments-audit` console scripts. Any repo on the
same machine consumes it as a **local path dependency** — no network, no
PyPI, no published index. The recipe below is
end-to-end; the field rules, config, and gate it points at are defined in
[declarations.md](/standards/judgments/declarations.md) and
[cache-gate.md](/standards/judgments/cache-gate.md).

## 1. Add the package as an editable path dependency

In the consuming repo's `pyproject.toml`, depend on `dev-playbook`
and point a `[tool.uv.sources]` entry at the dev-playbook repo root on disk:

```toml
[dependency-groups]
dev = ["dev-playbook"]

[tool.uv.sources]
dev-playbook = { path = "../dev-playbook", editable = true }
```

Adjust `path` to wherever `dev-playbook` sits relative to the consumer. The
dependency is `editable`, so the consumer always resolves against the
current `src/dev_playbook/` source — nothing to re-publish or re-pin when
the libraries change. `uv sync` builds the package with uv's own bundled
build backend, so building it needs no network or PyPI access. Its one
runtime dependency, `pyyaml`, resolves from uv's local cache whenever it is
present (it almost always is); only a completely cold cache reaches PyPI
for it. Afterwards
`from dev_playbook.judgments.pytest_support import assert_judgment_cached`
resolves in the consumer's environment and `judgments-run` is on its venv
PATH.

## 2. Declare the repo's judgments

Opt in exactly as
[declarations.md — Config and root resolution](/standards/judgments/declarations.md#config-and-root-resolution)
defines: a `[tool.judgments]` table in the consumer's own `pyproject.toml`
and one or more declaration YAML files in
[the YAML declaration format](/standards/judgments/declarations.md#the-yaml-declaration-format).

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]
```

The root is the consumer's own repo — the nearest ancestor with a
`[tool.judgments]` table — and every evidence/reference path resolves
against it.

## 3. Gate the judgments in pytest

Add the cache gate as an ordinary test in the consumer's suite, using the
parametrized form from [cache-gate.md](/standards/judgments/cache-gate.md):

```python
import pytest
from dev_playbook.judgments.loader import load, resolve_root
from dev_playbook.judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

The check is deterministic and offline; it reads the same machine-local
seen-set the `run-judgments` skill fills, so it needs no LLM and no API key
on CI.

## 4. Lint the declarations on commit

Add the `judgments-audit` pre-commit hook so malformed or stale declarations
fail fast. It ships from dev-playbook's published hook manifest; reference
it by URL and pinned `rev`, exactly as for the other dev-playbook hooks:

```yaml
- repo: https://github.com/GeoffNordling/dev-playbook
  rev: <commit-sha>
  hooks:
    - id: judgments-audit
```

The hook runs from pre-commit's own clone of dev-playbook at the pinned
`rev` and self-bootstraps its imports, so it needs neither the installed
package nor a checkout path — it is independent of the editable dependency
in step 1.

## 5. Fill the cache with the run-judgments skill

A cache miss — a failing gate — is filled by the global `run-judgments`
skill: it runs the LLM judge on each miss and records the passing verdicts
into the machine-local seen-set. The skill is available in any repo on the
machine; run it whenever the cache gate is red.
