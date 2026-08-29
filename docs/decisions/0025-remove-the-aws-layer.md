---
type: Decision-Record
title: Remove the AWS Build Layer
description: Delete the python · aws layer — its cdk.json trigger, CDK shape rules, Makefile.aws fragment, and standard document — because it was written before any AWS repo was governed and both real ones violate it
date: 2026-08-24
---

# Remove the AWS Build Layer

## Context

A repo holding a root `cdk.json` entered a `python · aws` build layer. The
layer required a `src/<package>/app.py` CDK entry, forbade a root `app.py`,
pinned `cdk.json`'s `app` command to `uv run python -m <package>.app`, forbade
tracked `cdk.out/`, and composed the canonical fragment
[Makefile.aws](/standards/build/canonical/Makefile.aws) with its `synth`,
`diff`, and `deploy` targets. [repo-lint](/scripts/repo-lint) detected,
composed, and shape-checked it; five build documents tabled it.

No governed repo has ever been in the layer. The workspace has exactly two AWS
repos — `JARVIS` and `wellness-check` — and neither is on the
[GOVERNED roster](/src/dev_playbook/workspace_lint.py). Both were scouted in
August 2026, and both violate the layer as written:

- `JARVIS` keeps its CDK config at `infra/cdk.json`, not the root, so the
  detector's `(root / "cdk.json").is_file()` trigger never fires on it at all —
  the layer is invisible to the one repo it was most written for.
- `wellness-check` has a root `cdk.json` but does not use the
  `uv run python -m <package>.app` entry the layer pins.

So the layer is not an unmet standard the repos should grow into. It is a
guess, written from no repo, that the two real repos independently disagree
with. Keeping it means the next AWS adoption spends its effort arguing with a
rule nobody derived from practice, and every reader of the build standard
discounts a layer that governs nothing.

The user's framing: *"I do not want to do speculative linting."*

## Decision

Delete the layer. After this record, `cdk.json` is an ordinary file the build
standard takes no position on, and an AWS repo is simply a Python repo.

Also removed with it: the `build.layer-shape` rule, whose only emission site
was the layer's `cdk.json requires src/` check.

When AWS repos are adopted, an AWS layer may be written again — from the two
repos as they then exist, not ahead of them.

## Scope

`JARVIS` and `wellness-check` are untouched. Their `cdk.json` files, their
`app.py` entries, their `synth`/`diff`/`deploy` targets, and their deploy
behavior are exactly as they were. This record removes dev-playbook's
*requirements* about those files, not the files. JARVIS is live; nothing here
reaches it.

## Recovery

Everything removed was last alive on `main` at commit `0fd1522`. Recover any
file with `git show 0fd1522:<path>`, and this branch's diff is the exact
inverse of a reinstatement.

## Consequences

- `repo-lint`'s layer summary no longer prints `aws`. `wellness-check` reads
  as `base, python, src`; `JARVIS` as `base, python, scripts`.
- The hook repo's canonical-directory self-audit flags
  `standards/build/canonical/Makefile.aws` until the file is gone, since the
  manifest no longer lists it — that finding clears when this lands.
- Nothing now stops a repo committing `cdk.out/`, the generated synth output.
  Adding `cdk.out/` to the [canonical .gitignore](/standards/build/canonical/.gitignore)
  was considered and rejected: the baseline is compared against every repo, so
  the line would put all six governed repos in violation over a directory none
  of them can produce — the same speculative linting this record removes. An
  AWS repo gitignores its own build output.
