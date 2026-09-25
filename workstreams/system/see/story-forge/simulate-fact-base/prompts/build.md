---
type: General-Sheet
title: Build Prompt
description: The prompt every Sonnet builder reads — build a fact base for one slice of story-forge in seven primitives, answer seven questions per kind with a receipt or UNDECLARED, and leave edges out of the slice as stubs
---

# Build Prompt

## Your job

Build a fact base, which is a knowledge graph, for one slice of the
story-forge repository. Other agents build the other slices at the
same time. An assembler joins all the slices afterwards into one fact
base for the whole repository. So:

- Record the fundamental objects in your slice and their shape, not a
  summary of what is inside them.
- When an edge points outside your slice, record it as a stub with its
  receipt. The assembler connects it.

The launch message gives you `storyForge` (the repository root), `run`
(the run directory), and your slice id. Read your brief first:
`<run>/briefs/<slice>.md`. It names your folders and files.

Stay in your slice. You do not need dev-playbook's standards or any
other document for this task. Use absolute paths and do not change
directory.

## The primitives

- **Kind** — a family of files that share one form: Story, Skill,
  Registry, Standard, Script, Index.
- **Instance** — one file of a kind.
- **Field** — a part every instance has: a frontmatter key, a fixed
  heading.
- **Edge** — one file pointing at another. Record how it is written: a
  link, a frontmatter list, a comment marker, a path in code.
- **Process** — something that reads one kind and writes another: a
  skill, a script.
- **Rule** — something that checks a kind: a standard, a lint, a test.
- **Receipt** — the file and line that proves a claim.

## For each kind you find, answer

1. What is it, in one sentence?
2. Where does it live, and how many instances are there?
3. How do you recognise one: its path, frontmatter `type:`, its name?
4. Which fields does every instance have?
5. What does it point at, and how is each edge written?
6. Which process reads it or writes it?
7. Which rule checks it?

Every answer carries a receipt. If you had to guess, write
**UNDECLARED**. When you find something that fits no primitive, write
it down; do not force it into one.

## Write three files in `<run>/slices/<slice>/`

**`facts.json`** — every instance a node, every edge a row:

```json
{ "slice": "<id>",
  "nodes": [ { "id": "<path from storyForge root>", "type": "<Kind>",
               "provenance": "declared | inferred", "extractor": "<how you found it: frontmatter, path, link, code, ...>",
               "line": 1, "attrs": { } } ],
  "edges": [ { "source": "<node id>", "relation": "<verb>", "target": "<node id, or stub:<path>>",
               "detail": null, "extractor": "<how it is written>", "line": 12 } ] }
```

A node that is not a file, such as a tag or a term, gets an id like
`tag:<name>`. `provenance` is `declared` when a file states the fact,
`inferred` when you concluded it.

**`kinds.md`** — one section per kind, the seven answers, each with its
receipt or UNDECLARED. End with a section **Does not fit** for anything
no primitive covers.

**`boundary.md`** — every stub edge: source, relation, the target path
outside your slice, and the receipt.

## Rules

- story-forge is read-only. Write nothing there.
- Write only inside `<run>/slices/<slice>/`.
- Privacy is a soft guardrail: add no new private content. In `attrs`,
  keep structure (keys, enumerated values, counts, titles) and replace
  body text or a description with `[redacted, N words]`. Redact what
  looks personal, such as a person's name or an employer.

Return the summary in the structured form the launch asks for.
