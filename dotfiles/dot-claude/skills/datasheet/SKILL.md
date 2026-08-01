---
name: datasheet
description: Produce or refresh a datasheet for a chosen subject and file scope. Use when the user asks to generate or refresh a datasheet, or names the subject and scope paths for one.
disable-model-invocation: false
model: opus
effort: xhigh
argument-hint: "[subject and/or scope paths]"
---

# Datasheet

Produces one datasheet conformant to the
[Datasheet Standard](~/workspace/dev-playbook/instruments/datasheet.md): a
fixed-section, budgeted HTML report at `readings/datasheet/<subject>.html` that
gives the system's owner trust and direction without reading the code. This
skill is the procedure; the standard is the contract.

`$ARGUMENTS` names the subject and/or scope paths.

## Read first

Before doing anything else, read end-to-end:

- [Datasheet Standard](~/workspace/dev-playbook/instruments/datasheet.md) — the
  contract the sheet must satisfy.
- [datasheet-example.html](~/workspace/dev-playbook/instruments/datasheet-example.html)
  — the structure to match, not the size.

Then report: `READ: datasheet.md, datasheet-example.html`. Proceed only after.

## Resolve subject and scope

The scope is an explicit manifest of paths and globs; the subject names the
sheet. Take both from `$ARGUMENTS`. If either is missing or ambiguous, stop
and report exactly what is needed — never proceed on a guessed manifest or
subject.

## Check existing sheets

Read stamps only — never a full sheet:

```
grep -A12 '^<!--datasheet-stamp' readings/datasheet/*.html 2>/dev/null; true
```

- Same subject already exists → this run regenerates it in place.
- The new manifest overlaps another subject's manifest → stop and surface
  the overlap to the user.

## Inventory

Create a self-ignoring scratch directory, then inventory each Python package
in scope:

```
mkdir -p .datasheet && printf '*\n' > .datasheet/.gitignore
~/workspace/dev-playbook/scripts/griffe-outline <package-path> >> .datasheet/outline.txt
```

If the scope holds no Python package, skip this step.

## Generate

Write the sheet to `readings/datasheet/<subject>.html` under these rules:

- **Structure from the inventory.** The inventory is authoritative for what
  exists — modules, classes, functions, signatures. Read source freely for
  behavior, touch surface, and tests, but a structural claim that contradicts
  the inventory is wrong.
- **Behavior from execution.** Prefer running the system live over inferring
  from source. Contain side effects: write only under `.datasheet/`, never
  mutate the repository or anything outside it. If no safe invocation exists,
  use `verified: not-run` and say why in one sentence.
- **Exhibits are committed forever.** Nothing unvetted for sensitivity goes
  in. When real output is too large or too private, keep the live run for
  verification and construct a small exhibit (`verified: run`,
  `exhibit: constructed`).
- **Scope is scope.** Files outside the manifest — and any explicitly
  excluded ones — are neither read nor described.

## Verify and report

Run the checker:

```
python3 <skill-dir>/scripts/check_datasheet.py readings/datasheet/<subject>.html
```

Findings mean the sheet is nonconformant — fix by regenerating, never by
hand-patching the HTML, and re-run until clean. If a contract rule cannot be
satisfied, delete the output and report why instead of shipping the sheet.
Then give the user the sheet path, the checker's one-line summary, and
the Behavior labels used. Committing is the user's call.
