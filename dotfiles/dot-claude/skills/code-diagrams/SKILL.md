---
name: code-diagrams
description: Explores a Python package and writes a Markdown report holding three diagrams — a module dependency graph, a runtime UML sequence diagram, and a class/type model — for a reader who has not read the code. Use when the user needs a zoomed-out view of an unfamiliar codebase to weigh a design decision, asks how modules interact / how objects are assembled / in what order they run, or is writing a spec or design against code they have not read.
disable-model-invocation: true
model: opus
effort: medium
argument-hint: "[focus or package path]"
---

# Code Diagrams

A zoomed-out view of a Python package for someone who has not read the code: a Markdown report holding a module dependency graph, a runtime sequence diagram, and a class/type model. A deterministic tool inventories the structure; a subagent draws only the relationships on top and writes the report to disk. The inventory and the report both stay on disk — only paths cross back into this session, so a long node session is not flooded with code.

`$ARGUMENTS` is an optional focus and/or package path.

## Resolve the package

- If `$ARGUMENTS` names a directory that exists, that is the package.
- Otherwise find the importable package — a directory with `__init__.py`, usually under `src/`. One candidate: use it. Several: ask the user which.

Any remaining `$ARGUMENTS` text is the **focus** — the subsystem or question to center the report on.

## Produce the inventory

Create a self-ignoring scratch directory at the project root, then inventory the package into it:

```
mkdir -p .code-diagrams && printf '*\n' > .code-diagrams/.gitignore
~/workspace/dev-playbook/tools/bin/py-outline <package-path> > .code-diagrams/outline.txt
```

The `*` ignores the whole directory — inventory, report, and the `.gitignore` itself — so the outputs stay visible in the editor but never reach a commit. `py-outline` is griffe static analysis: every module, class, function, and signature. It is the subagent's ground truth — do not read the package yourself.

## Draw the relationships

Dispatch one `general-purpose` subagent — it writes a file, so not `Explore`. Its prompt carries:

- the absolute path to this skill's `references/diagram-contract.md`, with an instruction to read and follow it;
- the inventory path `.code-diagrams/outline.txt`, as ground truth;
- the package path, for reading source only where a relationship demands it;
- the focus, if any — as scope to narrow the diagrams, never a topic to write about;
- the report output path `.code-diagrams/<package-name>.md`.

## Report

Give the user the report path and the subagent's one-line summary, and note it renders in the editor's Markdown preview. Do not paste the report here.
