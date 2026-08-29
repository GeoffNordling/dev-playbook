---
name: datasheet
description: Produce or refresh a datasheet for a chosen subject and file scope. Use when the user asks to generate or refresh a datasheet, or names the subject and scope paths for one.
disable-model-invocation: false
model: opus
effort: xhigh
arguments: [subject, scope]
---

# Datasheet

Produces one datasheet conformant to the
[Datasheet Standard](~/workspace/dev-playbook/instruments/datasheet.md): a
fixed-section, budgeted HTML report at `readings/datasheet/<subject>.html` that
gives the system's owner trust and direction without reading the code.

## Read first

{Read [datasheet.md](~/workspace/dev-playbook/instruments/datasheet.md)
end-to-end, before anything else; it states the contract the sheet must
satisfy}. {Read
[datasheet-example.html](~/workspace/dev-playbook/instruments/datasheet-example.html)
end-to-end, before anything else; it shows the structure to match}.

Then say `READ: datasheet.md, datasheet-example.html`, and proceed only
after.

## Resolve subject and scope

`scope` is an explicit manifest of paths and globs; `subject` names the
sheet. {If either is missing or ambiguous, {report exactly what is
needed} and stop}.

## Check existing sheets

Read stamps only:

```
grep -A12 '^<!--datasheet-stamp' readings/datasheet/*.html 2>/dev/null; true
```

If the same subject already exists, this run regenerates it in place.
{If the new manifest overlaps another subject's manifest, {report the
overlap} and stop}.

## Inventory

{Write to scratch a self-ignoring `.datasheet/` directory}. {If the scope
holds a Python package, {Run
[griffe-outline](~/workspace/dev-playbook/scripts/griffe-outline) over
each package in scope, appending its outline to the scratch
directory}}:

```
mkdir -p .datasheet && printf '*\n' > .datasheet/.gitignore
~/workspace/dev-playbook/scripts/griffe-outline <package-path> >> .datasheet/outline.txt
```

## Generate

{Write the sheet to `readings/datasheet/<subject>.html`}, under these
rules:

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
- **Only the manifest.** Files outside the manifest — and any explicitly
  excluded ones — are neither read nor described.

## Verify and report

{Run [check_datasheet.py](scripts/check_datasheet.py) against the sheet,
from this skill's base directory}:

```
python3 <skill-dir>/scripts/check_datasheet.py readings/datasheet/<subject>.html
```

Findings mean the sheet is nonconformant — fix by regenerating and
re-run until clean. {If a contract rule cannot be satisfied, {report why
the sheet is nonconformant} and delete the output instead of shipping
it}. {Report the sheet path, the checker's one-line summary, and the
Behavior labels used}. Committing is the user's call.
