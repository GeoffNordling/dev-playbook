---
name: new-repo
description: Scaffold a new workspace repo conformant to workspace standards. Interview-driven; creates the project directory, materializes the file tree, initializes git, creates the GitHub repo, bootstraps labels, and makes the first commit.
disable-model-invocation: true
model: opus
effort: xhigh
---

# New Repo

Scaffold a new workspace repo. Interview-driven; every file is derived
from workspace standards. No optional content is seeded — `ROADMAP.md`,
`BUSINESS_CONTEXT.md`, `specs/`, `docs/adr/`, `CONTEXT.md`, and sub-project
`CLAUDE.md` files appear when the project earns them, not at creation
time.

## 1. Interview

Use `AskUserQuestion` to gather, in one batch:

1. **Repo name** — kebab-case.
2. **One-line purpose** — for README and `gh repo create --description`.
3. **Stack** — Python (packageable) or meta/docs-only.
4. **License** — MIT, Apache-2.0, Proprietary (no LICENSE), or Other.
5. **GitHub visibility** — public or private.

## 2. Preflight

Verify:

- `~/workspace/<name>/` does not exist.
- `~/workspace/dev-playbook/.pre-commit-config.yaml` exists. The relative
  symlink materialized in step 4 (`../dev-playbook/.pre-commit-config.yaml`)
  depends on both repos sitting as siblings under `~/workspace/`, which is
  the workspace convention this skill assumes.

Fail loudly if either check fails.

## 3. Read the standards

Before writing any files, read each referenced standard end-to-end so its
content is fully in context. After reading, report which files were read.

**Both stacks:**

- [repo-documentation.md](~/workspace/dev-playbook/standards/repo-documentation.md)
- [build-conventions.md](~/workspace/dev-playbook/standards/build-conventions.md)

**Python stack additionally:**

- [python-project-conventions.md](~/workspace/dev-playbook/standards/python-project-conventions.md)
- [python-conventions.md](~/workspace/dev-playbook/standards/python-conventions.md)

## 4. Materialize the file tree

Create `~/workspace/<name>/`. Translate the repo name (kebab) to the
package name (snake) for any `src/<package>/` references. Refer to
standards rather than duplicating their content.

**Both stacks:**

- `README.md` — [README.md baseline](~/workspace/dev-playbook/standards/repo-documentation.md#readmemd-baseline)
- `CLAUDE.md` — [CLAUDE.md baseline](~/workspace/dev-playbook/standards/repo-documentation.md#claudemd-baseline). Omit `## Build` for meta/docs-only.
- `.gitignore` — [.gitignore baseline](~/workspace/dev-playbook/standards/repo-documentation.md#gitignore-baseline)
- `.pre-commit-config.yaml` — symlink per [build-conventions.md — Pre-commit Config](~/workspace/dev-playbook/standards/build-conventions.md#pre-commit-config-consumer-repo-opt-in)
- `LICENSE` — only if a recognized license was chosen. Fetch the canonical text for the selected license and write it. For Proprietary, write no LICENSE file.

**Python stack additionally:**

- `pyproject.toml` — [python-project-conventions.md](~/workspace/dev-playbook/standards/python-project-conventions.md)
- `Makefile` — [build-conventions.md — Standard targets](~/workspace/dev-playbook/standards/build-conventions.md#standard-targets)
- `src/<package>/__init__.py` — empty per [python-conventions.md — Package Initialization](~/workspace/dev-playbook/standards/python-conventions.md#package-initialization)
- `tests/__init__.py` — empty
- `tests/test_smoke.py` — a single test asserting the package imports:

  ```python
  def test_imports() -> None:
      import <package>  # noqa: F401
  ```

  Seeded so `make check` has at least one test to collect (pytest exits
  with code 5 otherwise). It also catches missing `__init__.py` and broken
  imports going forward.

Materializing `.github/workflows/ci.yml` is deferred to step 7 — the
consumer-repo template needs the GitHub owner, which isn't resolved
until step 6.

## 5. Sync and verify the scaffold (Python stack only)

```bash
cd ~/workspace/<name>
uv sync
make check
```

`uv sync` creates `.venv/` and `uv.lock`. The lock file is committed.

`make check` must pass on a fresh scaffold. If it doesn't, the standards'
templates have drifted from current tooling behavior (ruff, mypy, pytest
upgrades) and that's the right moment to fix the standards before the
new repo inherits the breakage. Do not proceed past a failing `make
check` — surface the failure for diagnosis.

## 6. Initialize git and create the GitHub repo

Initialize the local repo:

```bash
git init --initial-branch=main ~/workspace/<name>
```

`gh repo create` is not used — the workspace PAT lacks the repo-creation
scope. Hand off creation to the user via the web UI. Pre-fill the name in
the URL so they only have to set visibility and description:

```
Create the repo in your browser:

    https://github.com/new?name=<name>

Settings:
- Name: <name>
- Description: <purpose>
- Visibility: <public|private>
- Do NOT initialize with README, .gitignore, or LICENSE — the local
  scaffold already has them.

Tell me once it's created.
```

Wait for the user's confirmation. Then resolve the GitHub login and wire
up the remote (SSH, matching the workspace convention):

```bash
gh api user --jq .login
git -C ~/workspace/<name> remote add origin git@github.com:<login>/<name>.git
```

## 7. Materialize the CI workflow (Python stack only)

Now that the GitHub login is resolved, write
`~/workspace/<name>/.github/workflows/ci.yml` from the consumer-repo
template in [build-conventions.md — Continuous Integration](~/workspace/dev-playbook/standards/build-conventions.md#continuous-integration).
Fill in:

- `path: <name>` (the new repo's checkout path)
- `repository: <login>/dev-playbook` (the resolved owner from step 6)

## 8. Bootstrap labels

Requires the GitHub repo to exist. `cd ~/workspace/<name>` (standalone)
then:

```bash
python3 ~/workspace/dev-playbook/tools/bin/bootstrap-labels
```

## 9. Initial commit

```bash
git -C ~/workspace/<name> add .
git -C ~/workspace/<name> commit -m "Initial scaffold"
```

The initial commit is part of repo creation; no further authorization
needed.

## 10. Hand off the push

Print the push command for the user — pushing requires their YubiKey
tap. Do NOT run `git push`.

```
Repo ready at ~/workspace/<name>/.
Push with:

    cd ~/workspace/<name>
    git push -u origin main
```
