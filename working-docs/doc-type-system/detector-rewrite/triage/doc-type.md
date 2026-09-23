---
type: General-Sheet
title: Doc-Type
description: The triage of the doc-type family's twenty-eight deterministic rules — fourteen kept, fourteen restated, none deleted, four escalations for the user to rule on
---

# Doc-Type

Twenty-eight deterministic rules over five Standards under
`standards/doc-type/`, per
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md).
The fourteen stochastic rules are skipped. Today three detectors decide
fourteen of the twenty-eight: `scripts/harness-files-lint` nine,
`src/dev_playbook/loop_lint.py` five, and
`src/dev_playbook/standards_lint.py` one; fourteen rows in
`standards/verifiers.yaml` are `null`.

## doc-type.md

The population is `doc-types/<name>/`: four directories today,
`guide`, `loop`, `runbook`, `standard`.

- **`registered`**, `standards/doc-type/doc-type.md:31`. Rewrite,
  meaning changed by a cut at the "and": the second half is deleted
  because it restates two rules. The directory's row in
  `doc-types/index.md` is already required by
  `knowledge-organization.an-index-in-every-directory` and
  `knowledge-organization.one-entry-per-concept-document-and-child-directory`.

  > The table under `## Registry rulings` in
  > `doc-types/doc-type-system.md` has a row whose Ruling cell links to
  > a file in `doc-types/<name>/`.

  Check: read the table through the model (the path and heading are
  constants in `sources.py`) and collect the `doc-types/<name>/` part
  of each Ruling link. Today there is no check (`verifiers.yaml:69`,
  `null`). All four directories pass: each has a row that links to its
  `definition.md`.
- **`one-base-class`**, `standards/doc-type/doc-type.md:56`. Rewrite,
  wording only. The rule gains a check. Escalation 1.

  > The `python` block in `doc-types/<name>/contract-shape.md` has
  > exactly one top-level class. That class extends `DocType` and
  > assigns `operations` and `frontmatter`. Every other class in the
  > block is nested in it, has no base class, and assigns no
  > `operations`.

  Check: read the `class` header lines of the block and their
  indentation. Do not use `ast.parse`: the line
  `operations  = {act, check, yield}` in
  `doc-types/loop/contract-shape.md` is not valid Python.

## guide-conventions.md

Ten files are typed `Guide`, all under `guides/`. They have 11 ordered
lists and 44 items. A script that follows each sentence finds no
failures.

Kept as written, each gains its check:
`a-step-opens-with-its-name` (each item's text starts with a bold run
that ends in `.`, as in `**Wire the pin.**`), `no-trailer` (no line
matches the trailer pattern). Today neither has a check
(`verifiers.yaml:39`, `:63`).

- **`a-sequence-is-one-list`**, `standards/doc-type/guide-conventions.md:21`.
  Rewrite, wording only. The rule gains a check.

  > In a file typed `Guide`, every ordered list starts at `1.` and has
  > no ordered list inside it. Between the heading above the list and
  > the list there is at most one paragraph, and that paragraph is one
  > sentence. After the list there is nothing until a heading at the
  > same level as that heading or higher.

  "The only ordered list of that heading's section" is not in the
  restatement because the other clauses make it true. Check: walk the
  lines outside fences, find each list that is not indented, and test
  the three clauses. Today there is no check (`verifiers.yaml:38`).
  Zero of 11 lists fail.

## loop-conventions.md

No tracked file is typed `Loop`. `loops/index.md` says "None is
written yet", and no `~/workspace` repo has a `loops/` directory with
a Loop in it. Escalation 4 asks whether these six rules stay.

Kept as written, the check matching the sentence: `edges-lead-to-steps`
(`MAY_LEAD_TO`, `src/dev_playbook/loop_lint.py:78`, applied in
`check_loop`, `:340`).

- **`one-paragraph-then-one-graph`**, `standards/doc-type/loop-conventions.md:21`.
  Rewrite, wording only.

  > A file typed `Loop` has, after its front matter, one H1, then one
  > paragraph, then one fenced `mermaid` block, and nothing else before
  > the fence. The first line in the block is `flowchart` or `graph`.
  > Every other line is a Mermaid directive, a node, or an edge between
  > nodes, and no line uses `&`.

  Check: `slice_loop` and `graph_of`
  (`src/dev_playbook/loop_lint.py:125`, `:234`). Close one gap: lines
  before the H1 are never read, because they are collected only after
  `seen_h1` (`:177`–`:179`).
- **`acts-checks-and-yields-in-that-order`**, `standards/doc-type/loop-conventions.md:38`.
  Rewrite, wording only.

  > After the graph there are exactly three H2s, `Acts`, `Checks`, and
  > `Yields`, in that order, and nothing between the graph and
  > `## Acts`. Under each H2 there is one list. Each line of the list
  > is an entry, `` - `<node id>` — <text> ``, or an indented line that
  > continues the entry above it. No node id has two entries.

  Check: `entries_of` (`src/dev_playbook/loop_lint.py:198`). Close two
  gaps. First, the survey's: blank lines are skipped (`:210`), so two
  lists under one H2 read as one. Second, an H2 with no list passes.
- **`nodes-and-entries-agree`**, `standards/doc-type/loop-conventions.md:49`.
  Rewrite, wording only.

  > In a file typed `Loop`, the node id of every entry is a node of the
  > graph. Every node of the graph has an entry, or has no entry and is
  > the target of an edge from a yield. A node of the second kind is a
  > receiver.

  Check: `check_loop` (`src/dev_playbook/loop_lint.py:326`–`:339`),
  which already decides the sentence.
- **`every-entry-states-its-condition`**, `standards/doc-type/loop-conventions.md:65`.
  Rewrite, wording only.

  > Every entry of a file typed `Loop` contains `fires when` or
  > `fires every iteration` if it is an act or a check, and
  > `yields when` if it is a yield. An act's entry has at least one
  > link. A check's entry has a link to a file typed `Standard`. A
  > yield's entry has a link or the words `the user`, and each of its
  > links goes to a file typed `Loop`. Every link in an entry is
  > root-absolute or relative to the file, and goes to a file that
  > exists in the repo.

  Check: `check_entry` (`src/dev_playbook/loop_lint.py:285`). Close
  the survey's gap: for an act or a check, only `links[0]` is resolved
  (`:309`). Resolve every link, and look at all of a check's links for
  the `Standard`. Note for the knowledge-organization triage: "or
  relative" disagrees with
  `knowledge-organization.root-absolute-path-in-the-same-repo`.
- **`an-act-links-a-runbook`**, `standards/doc-type/loop-conventions.md:77`.
  Rewrite, wording only. The rule gains a check.

  > An act's entry has a link to a runbook: a file
  > `<skills root>/<name>/SKILL.md` or `<agents root>/<name>.md`, where
  > the roots are those that
  > [Every runbook at a fixed path](/standards/harness/files.md#every-runbook-at-a-fixed-path)
  > names.

  "The link an act's entry holds" does not say which link to test when
  there are several. The restatement reads it as "a link", which is
  consistent with the next row's reading of a check's link. Check:
  compare each resolved link of the act against the four root
  patterns. Today there is no check (`verifiers.yaml:42`).

## runbook-conventions.md

The population today is 27 skill bundles and 4 agent definitions under
`dotfiles/dot-claude/`. This repo has no `.claude/skills/` and no
`.claude/agents/`.

Kept as written, the check matching the sentence: `name-matches-its-home`
(`check_name`, `scripts/harness-files-lint:180`), `kebab-case-name`
(`KEBAB_RE`, `:107`), `description-two-sentences-or-one`
(`check_description`, `:219`), `model-and-effort-from-closed-sets`
(`check_model`, `check_effort`, `:297`, `:307`), `body-opens-with-an-h1`
(`check_body_h1`, `:382`), `boolean-disable-model-invocation`
(`check_disable_model_invocation`, `:317`),
`arguments-bare-kebab-case-names` (`check_arguments`, `:333`).

- **`front-matter-holds-its-kinds-vocabulary`**, `standards/doc-type/runbook-conventions.md:32`.
  Rewrite, wording only. The rewrite deletes the two example YAML
  blocks and the two paragraphs that introduce them. Together with the
  first paragraph they make five blocks, which fails
  `doc-type.a-rule-heading-predicate-trailer` (escalation 2). They
  only repeat the first paragraph and the value sets of three other
  rules.

  > A runbook starts with YAML front matter between two `---` lines. A
  > skill's keys are `name`, `description`, `disable-model-invocation`,
  > `model`, and `effort`, and optionally `allowed-tools`,
  > `disallowed-tools`, and `arguments`, and no other keys. An agent's
  > keys are `name`, `description`, `model`, and `effort`, and
  > optionally `tools`, and no other keys.

  Check: `parse_runbook`, `check_required_fields`, and
  `check_unknown_fields` (`scripts/harness-files-lint:153`, `:169`,
  `:283`), which already decide the sentence.
- **`every-bundle-file-reached-from-skillmd`**, `standards/doc-type/runbook-conventions.md:138`.
  Rewrite, meaning changed. The rule gains a check. Escalation 3.

  > Every file in a skill's `references/` or `scripts/` is the target
  > of a link in its `SKILL.md`.

  Check: resolve each link in `SKILL.md` relative to the bundle, then
  compare the result with the files of the bundle. Today there is no
  check (`verifiers.yaml:52`).
- **`tool-fields-space-separated-specs`**, `standards/doc-type/runbook-conventions.md:159`.
  Keep, add the check. Split the value at spaces that are outside
  parentheses. Each part must be a tool name, or a tool name followed
  by `(<pattern>)`, as in `Bash(git *)`. Three `allowed-tools` values
  exist today and all pass. No skill has `disallowed-tools`.
- **`no-argument-placeholder`**, `standards/doc-type/runbook-conventions.md:173`.
  Rewrite, wording only. The rule gains a check.

  > A skill's `SKILL.md` body, after the front matter, does not contain
  > the text `$ARGUMENTS` or `$0`.

  Check: a substring search of the body, fences included, because the
  harness does not skip fences. Today there is no check
  (`verifiers.yaml:62`). No skill fails.
- **`references-one-level-deep`**, `standards/doc-type/runbook-conventions.md:184`.
  Keep, and close the survey's three gaps in
  `check_references_depth` (`scripts/harness-files-lint:411`). It
  skips link targets that start with `/` or `~` (`:424`). It reads
  only `references/*.md` and not subdirectories (`:419`). Its
  `LINK_RE` matches inline links only (`:108`), so reference-style
  links are not read.
- **`skillmd-at-most-500-lines`**, `standards/doc-type/runbook-conventions.md:191`.
  Keep, add the check. Count the lines of the body after the front
  matter. Today `body_length_advisory` (`scripts/harness-files-lint:396`)
  prints this to stderr and does not fail. The longest `SKILL.md` is
  152 lines, `dotfiles/dot-claude/skills/ralph-setup/SKILL.md`.
- **`tools-comma-separated-tool-names`**, `standards/doc-type/runbook-conventions.md:201`.
  Keep, and close one gap in `check_tools`
  (`scripts/harness-files-lint:358`). It rejects an empty value or an
  empty part, but it does not test that each part is a tool name, so
  `tools: Read Grep` passes as one part. The two `tools` values today,
  `Read, Grep, Glob` and `Read, Edit`, pass.

## standard-conventions.md

The population is the 30 files typed `Standard`, which have 217 rules.

- **`the-frontmatter-names-the-population`**, `standards/doc-type/standard-conventions.md:28`.
  Rewrite, wording only.

  > A file typed `Standard` has a `population` key in its frontmatter,
  > and its value is a string that is not empty.

  Check: `check_directory_layout`
  (`src/dev_playbook/standards_lint.py:260`–`:270`), which already
  decides the sentence. The rule's Why names `standards-lint`, which
  the rewrite removes. That Why needs a new sentence when
  `standard-conventions.md` is rewritten.
- **`a-rule-heading-predicate-trailer`**, `standards/doc-type/standard-conventions.md:40`.
  Rewrite, wording only. The rule gains a check. Escalation 2.

  > In a file typed `Standard`, a rule is an H2 or H3 whose section
  > ends with a trailer line,
  > `` `<name>.<slug>` · deterministic `` or
  > `` `<name>.<slug>` · stochastic ``. `<name>` is the first
  > directory under `standards/` in the file's path, and `<slug>` is
  > the GitHub slug of the heading. Between the heading and the
  > trailer there is one paragraph, then at most one fenced block,
  > blockquote, list, or table. After the trailer, before the next
  > heading, there is nothing, or one blockquote that starts
  > `> **Why.**`. An H3 is only under an H2 that has no trailer.

  "The directory" becomes "the first directory under `standards/`".
  All 217 trailers use that directory, including the rules in
  `standards/knowledge-organization/documentation-sets/`.
- **`the-files-why-ends-the-opening-prose`**, `standards/doc-type/standard-conventions.md:60`.
  Rewrite, wording only. The rule gains a check.

  > In a file typed `Standard`, the text between the H1 and the first
  > H2 has at most one blockquote that starts `> **Why.**`. If it has
  > one, that blockquote is the last block before the first H2.

  The restatement does not keep "the argument for the file as a
  whole, not for any one of its rules". That clause describes the
  block and does not change which files pass. Check: split the opening
  text into blocks and test the two clauses. Today there is no check
  (`verifiers.yaml:72`). All 30 Standards pass.

## Escalations

Ruled 2026-09-23 under the general rulings in
[Triage](/working-docs/doc-type-system/detector-rewrite/triage.md#rulings-that-calibrate-the-rest).
Item 1: deleted, too specific. Item 2: built with the block limit
relaxed to a shape: a heading, then one paragraph, then any number of
paragraphs, lists, fenced blocks, or quotes, then the trailer line,
then at most one Why block; an H3 only under an H2 with no trailer.
The five H3 failures go with the two-tables deletion, so it passes
today. Item 3: built, the linked form. Item 4: Loop stays as it is,
all six kept.

1. **One base class: a check fails one contract shape.**
   - Heading line: `standards/doc-type/doc-type.md:56`.
   - What it means: each doc-type's pseudocode block has one class
     that extends `DocType`. Every other class is nested in that
     class.
   - Proposal: restate the rule as in the row above, and add the
     check. Make the repo comply: nest `class Finding` in
     `class Standard` as `Standard.Finding`, in
     `doc-types/standard/contract-shape.md` and in
     `working-docs/doc-type-system/doc-type-system/reference-model.md`,
     which `tests/test_pseudocode_sync.py` keeps identical to it. Then
     change `from standard import Finding, Standard` and
     `list[Finding]` in `doc-types/loop/contract-shape.md:44` and
     `:58`.
   - Difference from today's sentence: none. The restatement uses
     simpler words.
   - Difference from today's enforcement: today no check exists
     (`verifiers.yaml:65`, `null`). `detector-fixes.md` lists this rule
     as one that gains its check.
   - Measured: 1 of 4 contract shapes fails.
     `doc-types/standard/contract-shape.md:76` has a top-level
     `class Finding:`. The loop block (`doc-types/loop/contract-shape.md`)
     is not valid Python, so the check must read class header lines
     and cannot use `ast.parse`. The alternative is to relax the rule
     so that a top-level class with no base and no `operations` is
     allowed. That is a meaning change, and it makes the rule weaker.

2. **A rule: heading, predicate, trailer: a check fails eight places
   in four files.**
   - Heading line: `standards/doc-type/standard-conventions.md:40`.
   - What it means: each rule section is a heading, one paragraph, at
     most one other block, a trailer that has the correct id, and at
     most one Why block. An H3 is only under an H2 that has no
     trailer.
   - Proposal: restate the rule as in the row above, and add the
     check. The check makes the repo fail in eight places. This report
     fixes one of them, in the row for
     `front-matter-holds-its-kinds-vocabulary`. The triage of each
     other family fixes its own failures.
   - Difference from today's sentence: "the directory" becomes "the
     first directory under `standards/`", which is what all 217
     trailers already use. "Block or table" becomes a list of the four
     block kinds.
   - Difference from today's enforcement: today no check exists
     (`verifiers.yaml:37`, `null`). `scripts/verifier-table` reads
     trailers only to learn the ids.
   - Measured: 217 rules in 30 Standards. The failures:
     - Too many blocks before the trailer:
       `standards/doc-type/runbook-conventions.md:32` (5 blocks),
       `standards/knowledge-organization/documentation-sets/working-documentation-sets.md:86`
       (3 blocks: two paragraphs and a list), and
       `standards/prose/conventions.md:191` (7 blocks).
     - An H3 under an H2 that has a trailer:
       `standards/standard/detectors.md:50`, `:59`, and `:67`, under
       `:35`; `:94` and `:101`, under `:74`. The ruling "The two
       tables" deletes both parent rules, and probably these five H3s
       too. The standard family's triage decides.

3. **Every bundle file reached from SKILL.md: "invoked" becomes
   "linked".**
   - Heading line: `standards/doc-type/runbook-conventions.md:138`.
   - What it means: `SKILL.md` must lead to every file in the bundle,
     so the model can find each file.
   - Proposal: "Every file in a skill's `references/` or `scripts/` is
     the target of a link in its `SKILL.md`."
   - Difference from today's sentence: "invoked from its `SKILL.md`"
     becomes "linked from its `SKILL.md`". A function cannot decide
     "invoked". A link is a fact that a function can decide. Under
     the new sentence, a script that appears only in a code span
     fails. Under the old sentence, the same script passes if the
     text tells the model to run it.
   - Difference from today's enforcement: today no check exists
     (`verifiers.yaml:52`, `null`).
   - Measured: the bundles have 8 files, 6 in `references/` and 2 in
     `scripts/`. All 8 are linked from their `SKILL.md` today, so no
     file fails.

4. **Loop Conventions: six rules and a detector, and no Loop file.**
   - Heading lines: `standards/doc-type/loop-conventions.md:21`,
     `:38`, `:49`, `:57`, `:65`, and `:77`.
   - What they mean: a `loops/*.md` file typed `Loop` is one
     paragraph, one Mermaid graph, and the Acts, Checks, and Yields
     lists. The graph and the lists agree.
   - Proposal: keep all six, restated as in the rows above. The Loop
     doc-type is built, and `loops/index.md` expects instances. A
     governed repo that writes a Loop can fail these rules, so the
     reason "binds nothing" does not apply. The alternative is to
     delete the six rules and `loop_lint.py` until the first Loop is
     written. That follows "delete is the default".
   - Difference from today's sentence: wording only, in five rows.
   - Difference from today's enforcement: the three gaps named in
     the rows get closed, and `an-act-links-a-runbook` gets a check.
   - Measured: 0 files typed `Loop` in this repo or in any
     `~/workspace` repo. `src/dev_playbook/loop_lint.py` is 412 lines,
     and `tests/dev_playbook/test_loop_lint.py` is 215 lines.

## New rules

None.

## Acronyms

None.
