---
type: General-Sheet
title: Build Prompt
description: The prompt every Sonnet builder reads — describe the kinds of one slice of a target repository from sample files, answer seven questions per kind with a receipt or UNDECLARED, give each kind a recognition rule a script can apply, and record the edges between kinds
---

# Build Prompt

## Your job

Build a fact base, which is a knowledge graph, for one slice of a
target repository. Other agents build the other slices at the same
time. An assembler joins all the slices afterwards into one fact base
for the whole repository.

You describe **kinds**, not every file. A kind is a family of files
that share one form. For each kind, read 2 or 3 sample files, not all
of them. A script lists every instance later from the recognition rule
you write. Do not write one row per file.

The launch message gives you `target` (the repository root), `run`
(the run directory), and your slice id. Read your brief first:
`<run>/briefs/<slice>.md`. It names your kinds and your folders.

Stay in your slice. You do not need dev-playbook's standards or any
other document for this task. Use absolute paths and do not change
directory.

## Start from what the repository declares

A repository may declare its own kinds. Treat a declaration as the
strongest evidence you have, and cite it:

- A list of types, such as the `okf_types` map in the frontmatter of
  the root `index.md`. Your brief quotes the entries for your slice.
- A file's own `type:` frontmatter value names its kind.
- An `index.md` in a folder that says what the folder holds.
- A standard that names a population of files and its rules.

A kind the repository does not declare is still a kind. Mark it
`inferred`.

## The primitives

- **Kind** — a family of files that share one form: Story, Skill,
  Registry, Standard, Script, Index.
- **Field** — a part every instance of a kind has: a frontmatter key, a
  fixed heading.
- **Edge** — one kind pointing at another. Record how it is written: a
  link, a frontmatter list, a comment marker, a path in code.
- **Process** — something that reads one kind and writes another: a
  skill, a script.
- **Rule** — something that checks a kind: a standard, a lint, a test.
- **Receipt** — the file and line that proves a claim.

A kind can also be a form of another kind: a variant, a
specialization, or the output of a transformation. When a file says
so, record it as an edge between the two kinds.

## For each kind, answer

1. What is it, in one sentence?
2. Where does it live?
3. How do you recognise one? Write the recognition rule (below).
4. Which fields does every instance have?
5. Which other kinds does it point at, and how is each edge written?
6. Which process reads it or writes it?
7. Which rule checks it?

Every answer carries a receipt. If you had to guess, write
**UNDECLARED**. When you find something that fits no primitive, write
it down; do not force it into one.

## The recognition rule

A script applies your rule to every tracked file to list the
instances, so write it exactly:

```json
{ "glob": "stories/*.md", "frontmatter": { "type": "Story" }, "exclude": ["stories/index.md"] }
```

- `glob` is relative to the repository root. `*` matches within one
  folder; `**` matches across folders.
- `frontmatter` is optional. Each key must equal the given string.
- `exclude` is optional: globs that the rule must not match.

If no glob and frontmatter rule can recognise the kind, for example a
section inside a file, write `{ "expressible": false, "why": "..." }`.
That is a finding, not a failure.

## Write two files in `<run>/slices/<slice>/`

**`facts.json`**:

```json
{ "slice": "<id>",
  "nodes": [
    { "id": "kind:<Name>", "type": "Kind", "provenance": "declared | inferred",
      "file": "<path of the receipt>", "line": 9,
      "attrs": { "summary": "<one sentence>", "recognise": { },
                 "fields": [ { "name": "tags", "file": "<path>", "line": 5 } ],
                 "samples": [ "<path>", "<path>" ] } },
    { "id": "process:<path>", "type": "Process", "file": "<path>", "line": 1, "attrs": { } },
    { "id": "rule:<path>", "type": "Rule", "file": "<path>", "line": 1, "attrs": { } } ],
  "edges": [
    { "source": "kind:<Name>", "relation": "<verb>", "target": "kind:<Name> | stub:<path or kind name>",
      "how": "<how it is written>", "provenance": "declared | inferred",
      "file": "<path of the receipt>", "line": 12 } ] }
```

Relations between kinds include `points-at`, `form-of`, `reads`,
`writes`, and `checks`; use another verb when none fits. A
process or rule node joins its kinds with `reads`, `writes`, or
`checks` edges. When a target lies outside your slice, write it as
`stub:<path or kind name>`; the assembler connects it.

The receipt `line` must hold the text that proves the claim. If you
concluded a fact from several lines, cite the clearest one and mark
it `inferred`.

**`kinds.md`** — one section per kind with the seven answers, each with
its receipt or UNDECLARED. End with a section **Does not fit**.

## Rules

- The target repository is read-only. Write nothing there.
- Write only inside `<run>/slices/<slice>/`.
- Privacy is a soft guardrail: add no new private content. Keep
  structure (paths, keys, enumerated values, counts). Replace body text
  or a description with `[redacted, N words]`. Redact what looks
  personal, such as a person's name or an employer.

Return the summary in the structured form the launch asks for.
