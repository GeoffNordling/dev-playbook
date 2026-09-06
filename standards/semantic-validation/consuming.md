---
type: Guide
title: Consuming Judgments
description: How another repo picks the judgments tooling up — the editable path dependency, its own declarations, a position on the gate spectrum, the lint hook, and sweep pickup
---

# Consuming Judgments

The judgments tooling ships in dev-playbook's one installable package,
**`dev-playbook`**, built from `src/dev_playbook/`. It exposes the
`dev_playbook.judgments` and `dev_playbook.skipcache` import packages and
the `judgments-run` / `judgments-lint` console scripts. Any repo on the
same machine consumes it as a **local path dependency** — no network, no
PyPI, no published index. The recipe below is
end-to-end; the field rules, config, and gate it points at are defined in
[declarations.md](/standards/semantic-validation/declarations.md) and
[cache-gate.md](/standards/semantic-validation/cache-gate.md).

## 1. Add the package as an editable path dependency

In the consuming repo's `pyproject.toml`, depend on `dev-playbook`
and point a `[tool.uv.sources]` entry at the dev-playbook repo root on disk:

```toml
[dependency-groups]
dev = ["dev-playbook"]

[tool.uv.sources]
dev-playbook = { path = "/home/<user>/workspace/dev-playbook", editable = true }
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
`from dev_playbook.judgments.pytest_support import assert_judgment_cached`
resolves in the consumer's environment and `judgments-run` is on its venv
PATH.

## 2. Declare the repo's judgments

Opt in exactly as
[declarations.md — Opt-in table](/standards/semantic-validation/declarations.md#opt-in-table)
defines: a `[tool.judgments]` table in the consumer's own `pyproject.toml`
and one or more declaration YAML files in
[the declaration file shape](/standards/semantic-validation/declarations.md#file-shape).

```toml
[tool.judgments]
paths = ["judgments/*.yaml"]
```

The root is the consumer's own repo — the nearest ancestor with a
`[tool.judgments]` table — and every evidence/reference path resolves
against it.

## 3. Choose the repo's position on the gate spectrum

Gating is per-judgment and optional
([cache-gate.md](/standards/semantic-validation/cache-gate.md)): a judgment is
gate-enforced iff some pytest in the consumer's suite calls
`assert_judgment_cached` with its id. Choose a position by what the suite
wires:

- **None gated** — write no gate test. Every judgment is sweep-only;
  nothing judgment-related ever blocks a push.
- **Some gated** — one explicit test per load-bearing judgment, naming its
  id (the single-test recipe in cache-gate.md), or a filtered parametrize
  over the chosen subset.
- **All gated** — the parametrized recipe, unfiltered, enumerating every
  declaration through the loader:

```python
import pytest
from dev_playbook.judgments.loader import load, resolve_root
from dev_playbook.judgments.pytest_support import assert_judgment_cached


@pytest.mark.parametrize("jid", sorted(d.id for d in load(resolve_root())))
def test_judgment_cached(jid):
    assert_judgment_cached(jid)
```

The check is deterministic and offline; it reads the same machine-local
seen-set the judgments sweep fills, so it needs no LLM and no API key
on CI.

The gate is two-tier, keyed off one environment variable `SKIP_JUDGMENTS` that
`assert_judgment_cached` reads ([cache-gate.md](/standards/semantic-validation/cache-gate.md)):
exactly `1` skips the check with a visible pytest skip, any other value or
unset arms it. The canonical [Makefile](/standards/build/canonical.md#makefile) defaults it
to `1` and exports it, so `make check` and `make test` **skip** the gate — a
subagent running them never hits a miss only a sweep can fill.
`make check-judgments-cache` arms the gate — except on machines without the
cache, where the `NO_JUDGMENT_CACHE` conditional keeps it skipped
([Machines](/docs/machines.md)) — and is the entry of the canonical
pre-push hook: a miss blocks the push until the cache is filled, and a repo
with nothing gated passes vacuously. A bare `uv run pytest` arms it too
(fail-safe).

A repo taking the new Makefile fragment `MUST` repoint its pre-push hook to
`make check-judgments-cache` in the same commit — otherwise its `make check`
stops running the gate while nothing at the push enforces it.

## 4. Lint the declarations on commit

`judgments-lint` fails malformed or stale declarations fast at the commit
gate. It runs as part of dev-playbook's published `playbook-lint` hook,
which the canonical `.pre-commit-config.yaml` pins
([Distribution Channel](/standards/distribution/channel.md)) — any repo on the
canonical config runs it on every commit.

The hook runs from pre-commit's own clone of dev-playbook at the pinned
`rev` and self-bootstraps its imports, needing neither the installed
package nor the checkout path from step 1's editable dependency.

## 5. Let the periodic sweep fill the cache

The [`judgments-sweep`](/dotfiles/dot-claude/skills/judgments-sweep/SKILL.md)
skill judges whatever has drifted out of the cache
and records the passing verdicts into the machine-local seen-set. Its bare
invocation sweeps every judgment-bearing repo on the machine — the
`[tool.judgments]` table from step 2 is what makes this repo one of them —
so the periodic sweep picks the repo up with no further wiring, gated or
not. For gated judgments the sweep pre-fills the cache, so the push gate is
usually already green; when a push still blocks on a miss, run the sweep ad
hoc naming the repo as a root.
