---
type: General-Sheet
title: Wave 4 Rulings
description: The rulings for items 2 to 6 of step 11's wave 4, one edit each, decided so that the implementing session applies them without re-judging
---

# Wave 4 Rulings

Item 1 landed in commit 88d0381. Every edit below is decided; apply it
as written, one item per commit, and stop for the user's diff approval
after each. Where an edit is a deletion, delete; no substitute text
unless this sheet gives it. Delete this sheet in the item 6 commit.

## Item 2, the two tables

Run `scripts/verifier-table --write` and `scripts/boundary-table --write`.
The `mypy` row leaves `boundaries.yaml`. Any other row change is expected
drift from waves 2 and 3; the diff is the review.

## Item 3, the five catalog rows

In `standards/index.md`, replace the description of each of the five
rows with the index's opening sentence verbatim, the text playbook-lint
prints:

- `decisions/`, `distribution/`, `python/`, `testing/`, `tracking/`.

No judgment: the finding message holds the exact sentence.

## Item 4, the fifteen broken anchors

Two live documents:

- `guides/consuming.md:68`: delete the parenthetical link
  `([A pinned rev](/standards/distribution/channel.md#a-pinned-rev))`.
  The rule became a step of a Guide and has no anchor; the sentence
  "Bump the pin to a dev-playbook `rev` that carries it" stands alone.
- `dotfiles/dot-claude/agents/doc-set-deslopper.md:81`: delete the
  bullet item `[terms defined once](...#terms-defined-once),` from the
  Terms fact slice. The rule was redundant with one home; the three
  remaining links in the slice stay.

Thirteen in `working-docs/doc-type-system/doc-type-system/rule-audit/`,
the audit record of the rules the waves cut. Unlink, never repoint: turn
each `[text](target)` into its `text` alone, backticked where the text
is a rule id. The sites:

- `contested-calls.md:13`, `:23`, `:24`; `distribution.md:65`;
  `doc-type-runbook.md:55`; `decisions.md:113`, `:157`;
  `decision-sheet.md:46`, `:86`, `:131`; `modules.md:10`, `:47`, `:213`.

`modules.md:10` links the deleted Standard file itself; same treatment.

## Item 5, the reported rows

### The six why blocks marked *stands*

The `*stands.*` marker meant the why block already in the file stays;
the text after the marker was the design's paraphrase, not replacement
text. The agents reported the two differ. Ruling: the file's why block
is the home in five cases and needs no edit:

- `decisions.what-was-examined` (`standards/decisions/records.md:120`)
- `tracking.entry-shape` (`standards/tracking/candidates.md:37`)
- `knowledge-organization.stable-named-anchor`
  (`standards/knowledge-organization/cross-references.md:53`)
- `knowledge-organization.citation-another-repo` (`cross-references.md:66`;
  the exemption for code blocks is already in the population line)
- `knowledge-organization.one-home`
  (`standards/knowledge-organization/documentation-sets/documentation-sets.md:74`)
- `standard.git-runs-against-the-given-root`
  (`standards/standard/detectors.md:128`)

One mismatch. `tracking.user-intent`
(`standards/tracking/issue-shapes.md:52`) has a why about an
epic-level block copied into every child, a defect the predicate
"written in the user's voice, not an agent's paraphrase" does not
catch, since a copied block is in the user's voice. Replace the why
block with:

```
> **Why.** Only the user can vouch for what they meant. A paraphrase is
> an agent's reading of the intent, and the reading is what drifts, so
> the section keeps the user's words and the agent's reading goes
> elsewhere in the issue.
```

### The three Conditions holding a why block

The rule shape puts a why block after a trailer; a Condition has none,
so a why block under a Condition is outside the shape. Rulings:

- `standards/build/skeleton.md:102-105`, under `## Python package`:
  delete the why block. The Condition's sentence "A Python repo in which
  `src/` exists" already shows the conjunction the why explained.
- `standards/knowledge-organization/cross-references.md:102-104`, under
  `## No fixed repo root`: delete the why block, and replace the why
  block of the first child rule,
  `knowledge-organization.workspace-path-for-a-stable-location`
  (`cross-references.md:114-115`, "The condition above says what
  stable means..."), with:

  ```
  > **Why.** A runbook, a skill bundle, an agent definition, or a
  > global rule under `~/.claude/` is loaded from arbitrary repos, so a
  > leading `/` in one has no root to resolve against; the full
  > workspace path is the one form that resolves from anywhere.
  ```

- `standards/knowledge-organization/type-registry.md:65-69`, under
  `## Local declaration`: delete the why block, and add its reason to
  the lead prose of the same file, after the sentence ending "`okf_types`."
  (`type-registry.md:17`), as one sentence:

  ```
  The declaration is frontmatter and not a document under the
  consumer's own `standards/` tree, since that tree is the
  meta-standard's population, and a registry document there could not
  pass.
  ```

  The clause about a mirrored folder name is dropped: it argued against
  a path no rule proposes.

### The JavaScript Condition

The build agent deleted `## JavaScript` from `skeleton.md` along with
its only rule, `build.lockfile-committed`. Ruling: stays deleted. A
Condition scopes the rules under it; with none, it scopes nothing. One
follow-on: `scripts/repo-lint` still computes a `js` layer
(`Layers.js`, line 158, set at line 178 from `package.json`) that no
check reads since item 1. Delete the field, its `("js", self.js)`
report entry, and its assignment, and the tests that assert the `js`
layer name if any.

### The design skill citation

`working-docs/software-factory/skills/design/SKILL.md:20` glosses the
Guide as "small interface, deep implementation, accept dependencies,
return results, keep the surface small". "Return results" is
`modules.results-are-returned-not-written`, the one modules rule
deleted rather than moved to the Guide. Delete the words
"return results, " from the gloss. The other two citations of
`#shaping-a-module` (`wayfinder-to-build/SKILL.md:26`,
`improve-codebase-architecture/SKILL.md:15`) name only what the Guide
carries and stay.

### The two missing terminal periods

Add a period to the end of the predicate sentence of:

- `decisions.date`, `standards/decisions/records.md:85`, after `` `null` ``.
- `build.one-version-set`, `standards/build/canonical.md:127`, after
  "in each".

### The stale lead why of the doc-type Standard

`standards/doc-type/doc-type.md:25-29` says "Six of the seven rules
below ... are stochastic; Registered is deterministic". Since
`doc-type.one-base` became deterministic, that is two of seven, and a
count is a current-state claim. Replace the sentence from "Six of the
seven" to the end of the block with:

```
> A rule that reads the pseudocode in `contract-shape.md` or the prose
> in `definition.md`, never parsed as Python, is stochastic, a judge's
> prompt; a rule that reads a table or a class header a script parses,
> as Registered and One base do, is deterministic.
```

## Item 6, the proof

1. `scripts/playbook-lint` clean.
2. `make test` green.
3. `time pre-commit run --all-files` against the same on `88d0381`; no
   slower.
4. Delete this sheet and its row in `rule-audit/index.md`.
5. ROOT.md: a Completed entry for wave 4 of about eight lines, and the
   step 11 text says waves 1 to 4 are done.
6. Commit with the gates on; `--no-verify` ends here.

## Acronyms

- **PR** — pull request.
