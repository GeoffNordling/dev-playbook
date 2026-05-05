---
name: new-project
description: Bootstrap a new Python project repo from the workspace cookiecutter template, with optional GitHub remote.
disable-model-invocation: true
model: opus
effort: xhigh
argument-hint: "[project-name]"
---

# New Project

Bootstrap a new Python project repo following the template documented at
[project-template/README.md](~/workspace/dev-playbook/project-template/README.md).
That README is the source of truth for template variables, layout options,
and post-generation behavior. Read it before continuing.

## 1. Confirm scaffolding fits

Ask the user: **is this a Python project, and does it warrant the full
scaffolding** described in the [template README](~/workspace/dev-playbook/project-template/README.md)?

Some projects don't want this — a notes/journal repo, a pure shell-script
collection, or a non-Python project. If the answer is no, stop and suggest
minimal scaffolding by hand instead.

## 2. Verify prerequisites

Both must be on `PATH`:

```bash
which cookiecutter pre-commit
```

If either is missing, halt and tell the user to install permanently:

```bash
uv tool install cookiecutter
uv tool install pre-commit
```

Do not fall back to `uvx` — the template's post-gen hook checks
`shutil.which("pre-commit")` directly, and a `uvx` install hardcodes an
evictable cache path into the generated git hook.

## 3. Gather inputs

Collect the variables documented in the [template README](~/workspace/dev-playbook/project-template/README.md).
`$1` is the project name; if empty, ask. Then ask for description, layout,
and python version.

Before running cookiecutter, check the destination doesn't already exist:

```bash
ls -d ~/workspace/<slug> 2>/dev/null
```

If it does, stop and ask the user how to proceed.

## 4. Run cookiecutter

Generate into `~/workspace/` with the values from step 3:

```bash
cookiecutter --no-input -o ~/workspace ~/workspace/dev-playbook/project-template \
  project_name=<name> \
  project_layout=<layout> \
  description="<desc>" \
  python_version=<ver>
```

The post-gen hook handles git init, initial commit, `uv sync`, and pre-commit
install — see the [template README](~/workspace/dev-playbook/project-template/README.md)
for details. Surface any failures.

## 5. GitHub remote (user-run)

Ask: **create a GitHub remote now?** Default to **private**.

The agent does not have repo-create or push permissions — both require the
user's yubikey. Present the command in a fenced code block and ask the user
to run it themselves, per [bash-commands.md](~/workspace/dev-playbook/dotfiles/.claude/rules/bash-commands.md):

```bash
gh repo create <slug> --private --source=$HOME/workspace/<slug> --remote=origin --push
```

If they decline, leave the repo local.

## 6. Next step

Direct the user to run /setup-matt-pocock-skills in the new repo, per the
"Next Step (Required)" section of the [template README](~/workspace/dev-playbook/project-template/README.md).
