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
- `~/workspace/dev-playbook/.pre-commit-config.yaml` exists (the symlink
  target).

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

## 5. Initialize git and create the GitHub repo

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

## 6. Bootstrap labels

Requires the GitHub repo to exist. `cd ~/workspace/<name>` (standalone)
then:

```bash
python3 ~/workspace/dev-playbook/tools/bin/bootstrap-labels
```

## 7. Initial commit

```bash
git -C ~/workspace/<name> add .
git -C ~/workspace/<name> commit -m "Initial scaffold"
```

The initial commit is part of repo creation; no further authorization
needed.

## 8. Hand off the push

Print the push command for the user — pushing requires their YubiKey
tap. Do NOT run `git push`.

```
Repo ready at ~/workspace/<name>/.
Push with:

    cd ~/workspace/<name>
    git push -u origin main
```
