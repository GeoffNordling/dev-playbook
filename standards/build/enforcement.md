---
type: Standard
title: Enforcement
description: The enforcement map — the venues where checks fire and the tool that owns each rule
---

# Enforcement

## Venues

| Venue | Trigger | What runs |
|---|---|---|
| commit | `git commit` | the pre-commit hook suite, on staged files |
| push | `git push` | `make check`, via the pre-push-stage hook |
| agent | before every commit and before opening every PR | `make check` |
| CI | every push and PR on GitHub | [thin CI](/standards/build/ci.md) |
| sweep | on demand | GitHub settings per [repo-settings.md](/standards/repo-settings.md), via `gh api` |

`make check` runs **before push and before PR** — stated explicitly even
though a PR can only contain pushed commits, so the push gate already
covered them: an agent still re-runs `check` immediately before opening the
PR.

## Map

Where each tool's rules fire. Every pre-commit hook fires at **commit, in
CI, and inside every `make check`** (hence also at push, agent, and pre-PR);
the table lists only what falls outside that pattern.

| Tool | Owns | Venues |
|---|---|---|
| repo-audit | structure: presence, canonical bytes, forbidden files, layer shape, pin freshness | hook pattern |
| ruff-check / ruff-format | Python lint + formatting | hook pattern, plus `lint`/`format-check` targets |
| python-lint | workspace Python-source rules | hook pattern |
| okf-lint | concept-doc types, `index.md` freshness | hook pattern |
| ref-check | Links and Citations | hook pattern, except CI (skipped) |
| judgments-lint | judgment declarations | hook pattern |
| shellcheck | shell scripts | hook pattern |
| internal-skill-audit | skill bundles (skill-authoring repos) | hook pattern |
| mypy | types | `make check` only — never CI |
| pytest | tests + judgments stage-1 cache gate | `make check` only — never CI |
| `gh api` sweep | GitHub settings ([repo-settings.md](/standards/repo-settings.md)) | sweep |
