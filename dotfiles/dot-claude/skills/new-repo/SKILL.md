---
name: new-repo
description: Scaffold a new workspace repo conformant to workspace standards.
disable-model-invocation: true
model: opus
effort: xhigh
---

# New Repo

Scaffold a new workspace repo. Interview-driven. The workspace standards under `~/workspace/dev-playbook/standards/` are the source of truth; this skill is a navigation script that points you at them. Follow the standards, not stale wording in this skill.

No optional content is seeded — `ROADMAP.md`, `BUSINESS_CONTEXT.md`, `specs/`, `docs/adr/`, `CONTEXT.md`, and sub-project `CLAUDE.md` files appear when the project earns them.

## 1. Interview

Use `AskUserQuestion` to gather in one batch:

1. **Repo name** — kebab-case.
2. **One-line purpose** — for README and the GitHub description.
3. **Stack** — Python (packageable) or meta/docs-only.
4. **License** — MIT, Apache-2.0, Proprietary (no LICENSE), or Other.
5. **GitHub visibility** — public or private.

## 2. Preflight

Verify `~/workspace/<name>/` does not exist and `~/workspace/dev-playbook/` is present (the scaffold's relative symlinks assume both repos sit as siblings under `~/workspace/`). Fail loudly otherwise.

## 3. Read the standards

Read end-to-end before writing any files:

- [repo-documentation.md](~/workspace/dev-playbook/standards/repo-documentation.md)
- [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md) — read the Pre-commit and Continuous integration sections; the new repo needs both a `.pre-commit-config.yaml` and a CI workflow.
- [repo-settings.md](~/workspace/dev-playbook/standards/repo-settings.md) — the GitHub merge settings applied in step 7.
- [doc-conventions.md](~/workspace/dev-playbook/standards/doc-conventions.md) — the voice for the `README.md` and `CLAUDE.md` you author.

Python stack additionally:

- [python-project-conventions.md](~/workspace/dev-playbook/standards/python-project-conventions.md)

Report which files were read.

## 4. Materialize the file tree

Create `~/workspace/<name>/` and scaffold the repo per the standards from step 3. For licenses other than Proprietary, write the canonical license text. For Python stacks, also seed `tests/test_smoke.py` with a single import test so `make check` has something to collect.

Scaffold `.pre-commit-config.yaml` for every stack — not just Python, since `ref-check` lints the markdown every repo has. Reference the dev-playbook hook repo by pinned `rev` (dev-playbook's current `main` commit) alongside the ruff hooks, per [build-conventions.md — Pre-commit](~/workspace/dev-playbook/standards/build-conventions.md#pre-commit).

For Python stacks, also scaffold `.github/workflows/ci.yml` from the consumer workflow in [build-conventions.md — Continuous integration](~/workspace/dev-playbook/standards/build-conventions.md#continuous-integration), keeping the `SKIP: ref-check` env on the pre-commit gate. The workflow carries no repo-specific values, so nothing needs resolving after the repo exists. Meta/docs-only repos run no CI — local pre-commit is their gate.

## 5. Sync and verify (Python stack only)

Run `uv sync` then `make check`.

## 6. Initialize git and create the GitHub repo

Initialize the local repo on the `main` branch.

`gh repo create` is not available (workspace PAT lacks the scope). Hand creation off to the user via the web UI, with the name pre-filled:

```
Create the repo in your browser:

    https://github.com/new?name=<name>

Settings:
- Name: <name>
- Description: <purpose>
- Visibility: <public|private>
- Do NOT initialize with README, .gitignore, or LICENSE — the scaffold has them.

Tell me once it's created.
```

After the user confirms, resolve the GitHub login and wire up the SSH remote. Then run `pre-commit install` so the hooks gate the initial commit (step 9).

## 7. Apply repository settings

Apply the merge settings from [repo-settings.md](~/workspace/dev-playbook/standards/repo-settings.md). They sit behind GitHub's Administration permission and can't be set by token, so the user sets them by hand. While they are still in the new repo's GitHub UI, print those settings as a checklist for them to apply now, and wait for confirmation before continuing.

## 8. Bootstrap labels

Run `python3 ~/workspace/dev-playbook/tools/bin/bootstrap-labels` from inside the new repo. Requires the GitHub repo to exist.

## 9. Initial commit

Make the initial commit. No separate authorization needed — the commit is part of repo creation.

## 10. Hand off the push

Print the push command for the user. Pushing requires their YubiKey tap; do NOT run `git push`.

```
cd ~/workspace/<name>
git push -u origin main
```
