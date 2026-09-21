---
type: General-Sheet
title: Harness Family Rule Audit
description: The rule audit over the standards/harness/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Harness Family Rule Audit

The family holds nine rules across two Standards,
[Claude Code Files](/standards/harness/files.md) with two and
[CLAUDE.md Content](/standards/harness/claude-content.md) with seven.
No trailer needs reclassification: all nine kinds match what a script
could decide, zero moves to deterministic and zero to stochastic. Two
rules carry a detector and both check their predicate in full; the
other seven have a null verifier row and no code decides them. Three
rules break — `harness.members`, `harness.location`, and
`harness.one-rule-per-heading` — and each break is small and local. No
rule is weakly checked, and no rule is low value: every predicate in
the family states something no other rule states.

## Rules

| id | rule | kind | proposed | check | state | overlap | value | note |
|---|---|---|---|---|---|---|---|---|
| `harness.members` | Every file the harness consumes is a member of the table below, with the class the table gives it. | deterministic | deterministic | none | breaks | none | high | Test: every path under a harness root matches a table row. `dotfiles/dot-claude/statusline.sh` matches none; the `.claude/workflows/*.js` row misses `dotfiles/dot-claude/workflows/`. |
| `harness.location` | A skill is `<skills root>/<name>/SKILL.md` and an agent is `<agents root>/<name>.md`, the roots being `.claude/skills/` and `.claude/agents/`, and `dotfiles/dot-claude/skills/` and `dotfiles/dot-claude/agents/` where those directories exist. | deterministic | deterministic | none | breaks | none | high | The sentence holds for all 25 skills and 4 agents. The layout block omits `agents/`, which eight bundles carry. harness-files-lint aborts on a bundle without `SKILL.md` but emits no id. |
| `harness.no-frontmatter` | A `CLAUDE.md` opens on its content, with no YAML frontmatter block. | deterministic | deterministic | none | holds | none | high | Test: no `CLAUDE.md` in `git ls-files` starts with `---`. Both members, `CLAUDE.md` and `dotfiles/dot-claude/CLAUDE.md`, open on an H1. |
| `harness.operational-scope` | A `CLAUDE.md` holds only how to operate — commands, rules, and pointers to other docs — and carries nothing of what the project is, why it exists, or who develops it. | stochastic | stochastic | none | holds | none | high | Telling an operating rule from project identity needs judgment. `CLAUDE.md:5` opens on "This is a meta repo", but as the premise of the instruction that follows, not as identity prose. |
| `harness.one-scope` | Every rule in a `CLAUDE.md` sits at the widest scope where it is true, and at exactly one: the global source carries what holds for every session on the machine, a root file carries what holds for its repo alone, and a nested `<dir>/CLAUDE.md` carries only the delta from the files above it. | stochastic | stochastic | none | holds | none | high | The two members share no rule. The predicate compares members, which `doc-type.decidable-predicates` forbids; see Escalations. |
| `harness.global-file` | The `CLAUDE.md` sits at `dotfiles/dot-claude/CLAUDE.md`, the global source linked to `~/.claude/CLAUDE.md`. | deterministic | deterministic | none | holds | none | high | A condition, not a predicate every member obeys, in the shape `doc-type.skill` and `standard.a-first-party-detector` use. It scopes the three rules below it, and the file exists. |
| `harness.two-sections` | The global source's H2 headings outside fenced code blocks are exactly `## Behaviors` then `## Principles`, in that order. | deterministic | deterministic | full | holds | none | high | `check_global_claude` compares the H2 tuple to `("## Behaviors", "## Principles")`. The file's H2s are those two, at lines 3 and 54. |
| `harness.required-rules` | The global source carries the headings `### Read the standards` and `### Navigate docs by index`, both outside fenced code blocks. | deterministic | deterministic | full | holds | none | high | `check_global_claude` tests both strings against the heading list. Both are present, at `dotfiles/dot-claude/CLAUDE.md:5` and `:10`. |
| `harness.one-rule-per-heading` | Each rule of the global source is one `###` heading under its bucket: a dispositional stance under `## Principles`, an operating rule for a named situation under `## Behaviors`. | stochastic | stochastic | none | breaks | `harness.two-sections` | high | `### Notice repeatable work` at line 77 sits under `## Principles` but names its situation and its action. Overlap is partial: two-sections fixes the buckets, this rule fills them. |

## Escalations

### `harness.members` — Every file the harness consumes is a member of the table below, with the class the table gives it

The predicate binds "a file in a governed repo that the Claude Code
harness consumes: loaded as configuration, run as code, or injected
into agent context". Two files in this repo meet that population and
are not members of the table at
[files.md](/standards/harness/files.md) lines 26 to 34.

`dotfiles/dot-claude/statusline.sh` is run as code by the harness:
`dotfiles/dot-claude/settings.json:204` sets
`statusLine.command` to `bash "$HOME/.claude/statusline.sh"`, and Stow
links `dotfiles/dot-claude/` into `~/.claude/`. No row of the table
names a status line, and no other Standard names the file. A repo-wide
grep finds the string `statusline` in exactly one place, that settings
line.

`dotfiles/dot-claude/workflows/ralph-loop.js` and
`dotfiles/dot-claude/workflows/scatter-gather.js` are run as code by
the Workflow tool. The table's row for them is spelled
`.claude/workflows/*.js`, an absolute repo path that the authored files
do not sit at. Every other row is written root-agnostically —
`agents/*.md`, `rules/*.md`, `hooks/` — and
[Location](/standards/harness/files.md#location) names both roots
explicitly, so the `.claude/` prefix on this one row is an
inconsistency rather than a deliberate narrowing.

Proposal: change the repo, by adding one row and editing one. Add
`| statusline.sh | code | run as code to draw the status line | none yet |`
and respell the workflows row `workflows/*.js`. The file that changes
is `standards/harness/files.md`. The repo plainly wants the table to be
the registry — `document-types.md` draws the concept/harness boundary
by deferring to it, and `classify()` in `md.py` encodes that boundary —
so a harness file missing from it is an oversight, not a position.

### `harness.location` — A skill is `<skills root>/<name>/SKILL.md` and an agent is `<agents root>/<name>.md`

The predicate's sentence holds everywhere. All 25 bundles under
`dotfiles/dot-claude/skills/` carry a `SKILL.md`, and all four agents
are `.md` files directly under `dotfiles/dot-claude/agents/`.

The break is in the block below the sentence, `files.md` lines 45 to
51, which the rule shape treats as the target state the predicate
compares against. The block gives a bundle three entries: `SKILL.md`
required, `references/` optional, `scripts/` optional. Eight bundles
carry a fourth, `agents/`, holding an `openai.yaml` that describes the
skill to another harness:
`dotfiles/dot-claude/skills/research/agents/openai.yaml` holds three
lines of `interface:` metadata, a display name and a short
description. The other seven are `diagnosing-bugs`, `domain-modeling`,
`grilling`, `improve-codebase-architecture`, `prototype`, `wait-what`,
and `wayfinder`. Claude Code never reads these files, and
harness-files-lint never reaches them: its `agent_roots` are
`.claude/agents/` and `dotfiles/dot-claude/agents/` only.

Proposal: rewrite the block, adding one line,
`agents/           # optional: bundle metadata for another harness`.
The directories are deliberate and eight bundles deep, so the target
state is what is behind, not the repo. The file that changes is
`standards/harness/files.md`.

### `harness.one-rule-per-heading` — Each rule of the global source is one `###` heading under its bucket

The predicate splits the global source's two buckets by what a rule
is: "a dispositional stance under `## Principles`, an operating rule
for a named situation under `## Behaviors`". The
[Harness Explanation](/standards/harness/explanation.md#one-scope)
states the same split in its own words: Principles holds "how the
agent carries itself", Behaviors holds "what the agent does".

`dotfiles/dot-claude/CLAUDE.md:77` puts `### Notice repeatable work`
under `## Principles`. Its body names a situation and an action: "When
the task at hand looks repeatable, say so in one line and suggest the
user consider setting up a loop. Then carry on — this is a reminder,
not a gate." That is an operating rule for a named situation, the
Behaviors shape. Its three siblings under Principles do carry stances:
`### Be direct` ("Push back when you disagree"), `### Fail loud`, and
`### Pitch it cold`. The seven headings under Behaviors all name a
situation, so the file breaks in one place only.

Proposal: change the repo, by moving `### Notice repeatable work` and
its body from `## Principles` to the end of `## Behaviors` in
`dotfiles/dot-claude/CLAUDE.md`. The move is one heading in one file,
and the explanation states the bucket split plainly enough that the
current placement reads as an oversight. Nothing else in the family
depends on the ordering within a bucket, and `harness.two-sections`
stays satisfied because neither H2 moves.

### `harness.one-scope` — a note on its shape

Not a break, but the design pass should see it.
[Decidable predicates](/standards/doc-type/standard-conventions.md#decidable-predicates)
requires each predicate to be "true or false of one member of the
population at one moment, with no comparison to another member".
`harness.one-scope` asks whether a rule "sits at the widest scope where
it is true", which cannot be settled without reading the other
`CLAUDE.md` files above and below it. The rule is valuable and the two
members obey it; the predicate is at odds with the shape Standard it
answers to.

A second gap sits beside it. The `rules/*.md` row of the members table
gives that class no content standard, so nothing binds what a rule file
carries or where its scope sits. `dotfiles/dot-claude/rules/edit-in-dev-playbook.md`
is dev-playbook-specific and is injected into every session on the
machine, which is what `harness.one-scope` would forbid if its
population reached rule files. It does not: the population is "a
`CLAUDE.md`".

## Detectors

`scripts/harness-files-lint` is the family's only detector, and it
decides two of the nine rules. `check_global_claude` gates on the
presence of `dotfiles/dot-claude/CLAUDE.md`, so it runs in dev-playbook
alone; it collects the file's headings outside fenced code blocks,
compares the H2 tuple against `("## Behaviors", "## Principles")` for
`harness.two-sections`, and tests the two literal strings
`### Read the standards` and `### Navigate docs by index` against the
whole heading list for `harness.required-rules`. Both checks test what
their predicate says. The rest of the script decides ten
`doc-type.*` rules over skill bundles and agent definitions, which
belong to the doc-type family, and raises a `ToolError` exit-2 abort
for a directory under a skills root with no `SKILL.md` — the one place
`harness.location` is touched by code, under no rule id.

`src/dev_playbook/md.py` supplies the mechanics the checks stand on.
`content_lines` and `lines_outside_fences` are what make a heading
inside a fenced block invisible to both rules, and they raise
`UnclosedFence` rather than scanning a truncated file. `classify()`
encodes the concept/harness boundary the family's population draws,
returning `"harness"` for `CLAUDE.md`, `SKILL.md`, and anything under a
`rules/` or `agents/` segment. It decides no harness rule id, but
`files.md` cites it as the code that holds the boundary, and
`document-types.md` defers to the members table for the same split.

One caveat on both checks: the heading scan filters on the raw line
with `line.startswith("#")`, so an H2 indented by one to three spaces —
still an H2 to GitHub — is invisible to `harness.two-sections`. The
`GLOBAL_CLAUDE_SECTIONS` comment in the script also describes the two
buckets in the reverse order to the tuple it annotates.
