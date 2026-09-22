---
type: General-Sheet
title: Standard Rulings
description: The standard family agent's work order — every rule under standards/standard/ with its ruling, its trailer kind after the pass, and the text the ruling needs
---

# Standard Rulings

The work order of the `standard` family agent: every rule under `standards/standard/`, its ruling, the trailer kind it ends with, and the text the ruling needs. The agent loads [Family Apply Prompt](/working-docs/doc-type-system/doc-type-system/rule-audit/apply/family-prompt.md) and applies every row.

| id | file | ruling | kind | text |
|---|---|---|---|---|
| `standard.read-only` | standard/detectors.md | rewrite | stochastic | Sentence: A first-party detector run without an explicit write flag leaves everything git tracks as it found it; `verifier-table --write` and `boundary-table --write` are enforcement, and a dependency the verifier table names may write at its gate, `ruff-format` and `shfmt -w`. |
| `standard.an-absent-surface-is-clean` | standard/detectors.md | guide |  | Guide: `guides/writing-a-detector.md` |
| `standard.the-verifier-table` | standard/detectors.md | keep | deterministic |  |
| `standard.an-emitted-id-is-a-rule-heading` | standard/detectors.md | keep | deterministic |  |
| `standard.an-address-exists` | standard/detectors.md | keep | deterministic |  |
| `standard.a-consumer-adds-only-its-own-rules` | standard/detectors.md | keep | deterministic |  |
| `standard.the-boundary-table` | standard/detectors.md | keep | deterministic |  |
| `standard.every-address-runs-somewhere` | standard/detectors.md | keep | deterministic |  |
| `standard.a-skip-is-machine-state` | standard/detectors.md | keep | stochastic |  |
| `standard.a-first-party-detector` | standard/detectors.md | condition |  |  |
| `standard.thin-shims` | standard/detectors.md | rewrite | deterministic | Sentence: The script holds no rule logic: apart from its shebang and inline metadata block, its statements are at most one that puts the host repo's package on `sys.path`, one import from that package, and one call of the imported entry point. |
| `standard.git-runs-against-the-given-root` | standard/detectors.md | rewrite | deterministic | Sentence: A first-party detector that runs git clears the variables `git rev-parse --local-env-vars` lists from the child environment.<br>Why: *stands.* Clearing git's local environment variables is what makes a detector address the repo it was given when a hook runs it under an ambient `GIT_DIR`. |
| `standard.the-hosting-pattern` | standard/detectors.md | rewrite | deterministic | Sentence: A first-party detector is reachable from its repo's published hook, named in the `playbook-lint` roster, wired as a `scripts/` hook its `.pre-commit-config.yaml` and `.pre-commit-hooks.yaml` both carry, or registered as an ungated audit, and has a row in a `scripts/README.md` script table where the repo has that file. |
| `standard.offered-by-the-canonical-template` | standard/detectors.md | rewrite | deterministic | Sentence: A first-party detector the repo carrying `standards/build/canonical/` publishes in `.pre-commit-hooks.yaml` is a hook of that canonical `.pre-commit-config.yaml`'s pinned dev-playbook block, which offers exactly the ids that manifest publishes. |
| `standard.list-rules` | standard/detectors.md | guide |  | Guide: `guides/writing-a-detector.md` |
| `standard.finding-format` | standard/detectors.md | guide |  | Guide: `guides/writing-a-detector.md` |
| `standard.exit-codes` | standard/detectors.md | guide |  | Guide: `guides/writing-a-detector.md` |
| `standard.directory-layout` | standard/tree.md | rewrite | deterministic | Sentence: Every immediate subdirectory of `standards/` is a Standard directory: it holds at least one file typed `Standard`, and every other `.md` file under it, `index.md` aside, is typed `Standard`; the only flat `.md` files under `standards/` are `README.md` and `index.md`. |
| `standard.the-statement` | standard/tree.md | keep | deterministic |  |
| `standard.the-catalog` | standard/tree.md | keep | deterministic |  |
| `standard.no-shadowing` | standard/tree.md | keep | deterministic |  |

## Acronyms

None.
