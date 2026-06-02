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
- [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md)

Python stack additionally:

- [python-project-conventions.md](~/workspace/dev-playbook/standards/python-project-conventions.md)

Report which files were read.

## 4. Materialize the file tree

Create `~/workspace/<name>/` and scaffold the repo per the standards from step 3. For licenses other than Proprietary, write the canonical license text. For Python stacks, also seed `tests/test_smoke.py` with a single import test so `make check` has something to collect.

Defer `.github/workflows/ci.yml` to step 7 — the consumer-repo template needs the GitHub owner, which isn't known until step 6.

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

After the user confirms, resolve the GitHub login and wire up the SSH remote.

## 7. Materialize the CI workflow (Python stack only)

Write `.github/workflows/ci.yml` per the consumer-repo pattern in [build-conventions.md — Continuous Integration](~/workspace/dev-playbook/standards/build-conventions.md#continuous-integration), filling in the new repo's name and the resolved GitHub owner.

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
