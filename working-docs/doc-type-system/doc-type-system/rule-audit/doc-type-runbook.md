---
type: General-Sheet
title: Runbook Conventions Rule Audit
description: The rule audit over the doc-type/ family's Runbook Conventions — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Runbook Conventions Rule Audit

[Runbook Conventions](/standards/doc-type/runbook-conventions.md) holds
21 rules over 30 members: the 26 skill bundles under
`dotfiles/dot-claude/skills/` and the 4 agent definitions under
`dotfiles/dot-claude/agents/`. No trailer needs reclassification —
zero rules move to deterministic and zero to stochastic. Nine rules
carry a detector that tests the predicate in full, one is weakly
checked, and eleven have a null verifier row with no code behind them.
Three rules break: `doc-type.steps-end-on-a-completion-criterion`,
`doc-type.carries-its-chain`, and
`doc-type.interactive-skills-inherit`. Two rules are low value,
`doc-type.disallowed-tools-restate-nothing` and
`doc-type.skillmd-at-most-500-lines`; the other nineteen each state
something no other rule states.

## Rules

| id | rule | kind | proposed | check | state | overlap | value | note |
|---|---|---|---|---|---|---|---|---|
| `doc-type.front-matter` | A runbook opens with a YAML block between `---` lines holding exactly its kind's vocabulary: a skill's `name`, `description`, `disable-model-invocation`, `model`, and `effort`, with `allowed-tools`, `disallowed-tools`, and `arguments` optional; an agent's `name`, `description`, `model`, and `effort`, with `tools` optional. | deterministic | deterministic | full | holds | none | high | `check_required_fields` and `check_unknown_fields` compare the parsed keys against `SKILL_FIELDS` or `AGENT_FIELDS`; `parse_runbook` raises on an unclosed block. All 30 members pass. |
| `doc-type.name-matches-its-home` | A runbook's `name` equals the bundle directory for a skill and the file stem for an agent. | deterministic | deterministic | full | holds | `harness.location` | high | `check_name` compares `name` to `skill_dir.name` or `agent_md.stem`. Partial overlap only: `harness.location` fixes the path, this binds the frontmatter key to it. |
| `doc-type.kebab-case-name` | A runbook's `name` is kebab-case. | deterministic | deterministic | full | holds | none | high | `check_name` matches `KEBAB_RE`. All 30 names pass. No test in `tests/test_harness_files_lint.py` covers this branch. |
| `doc-type.description` | A runbook's `description` is a string of at most 1024 characters. | deterministic | deterministic | full | holds | `doc-type.description-states-what-and-when` | high | `check_description` tests type, length, sentence count by `SENTENCE_END_RE`, and the `Use when` prefix. Neither rule subsumes the other: this one fixes form. |
| `doc-type.description-states-what-and-when` | The first sentence of a runbook's `description` states what the runbook does. | stochastic | stochastic | none | holds | `doc-type.description` | high | Judging whether a sentence states what a runbook does needs reading. All 30 descriptions open on the act; all 17 second sentences name callers, phrases, or file types. |
| `doc-type.model-and-effort` | A runbook's `model` is one of `haiku`, `sonnet`, `opus`, `fable`, or `inherit`, and its `effort` is one of `low`, `medium`, `high`, or `xhigh`. | deterministic | deterministic | full | holds | none | high | `check_model` and `check_effort` test membership in `VALID_MODELS` and `VALID_EFFORTS`. All 30 members pass. No test covers either branch. |
| `doc-type.body-opens-with-an-h1` | The first non-blank line of a runbook's body, after the front matter, is an H1. | deterministic | deterministic | full | holds | none | high | `check_body_h1` walks the body to the first non-blank line and tests `# `. All 30 bodies open on an H1. No test covers this branch. |
| `doc-type.steps-end-on-a-completion-criterion` | Every step of a runbook's body ends on a completion criterion: the condition that tells the agent the work is done. | stochastic | stochastic | none | breaks | none | high | Eighteen runbooks carry numbered steps; only `update-standards-pin` gives every step a criterion. `log-friction/SKILL.md:31-38` and `research/SKILL.md:15` give none. See Escalations. |
| `doc-type.carries-its-chain` | Every edge of a runbook's contract is declared in the runbook's own file: what it accepts by the front matter `arguments` list, and each read, write, banned write, do, override, and report as a span in the body that encoding.md parses, except a ban the span vocabulary cannot carry, which stays plain prose in the body and is listed in residual-ledger.md. | stochastic | stochastic | none | breaks | none | high | The exception covers a ban only, but `residual-ledger.md` records unexpressed reads, writes, and does edges for 27 runbooks. See Escalations. |
| `doc-type.skill` | The runbook is a skill. | deterministic | deterministic | none | holds | none | high | A condition, not a predicate every member obeys: the file's root decides it. It scopes the eight H3 rules below it, which cannot stand without it. |
| `doc-type.bundle-layout` | Every file in a skill's `references/` is linked from its `SKILL.md`, and every file in its `scripts/` is invoked from its `SKILL.md`. | deterministic | deterministic | none | holds | `harness.location` | high | Test: each filename under the two directories appears in a link or a `{Run …}` span. All 6 `references/` files and 2 `scripts/` files pass. The `agents/openai.yaml` in 8 bundles sits outside the rule. |
| `doc-type.model-invocation-flag` | A skill's `disable-model-invocation` is boolean. | deterministic | deterministic | full | holds | none | high | `check_disable_model_invocation` tests `isinstance(value, bool)`. All 26 skills pass. No test covers this branch. |
| `doc-type.interactive-skills-inherit` | A skill that runs several turns with the user carries `model: inherit`. | stochastic | stochastic | none | breaks | none | high | `runbook-creator`, `enable-repo-governance`, and `update-standards-pin` each stop and wait for the user mid-run and each carries `model: opus`. See Escalations. |
| `doc-type.tool-fields` | A skill's `allowed-tools` and `disallowed-tools`, when present, are space-separated tool specs, as in `Bash(git *) Bash(gh *)`. | deterministic | deterministic | none | holds | none | high | Test: split on whitespace, each token a tool name or `Tool(pattern)`. Two members carry `allowed-tools`, both one spec; no member carries `disallowed-tools`. |
| `doc-type.disallowed-tools-restate-nothing` | A skill's `disallowed-tools`, when present, names no tool or call that a `settings.json` beside its skills root already denies. | deterministic | deterministic | none | holds | none | low | Vacuous: no skill carries `disallowed-tools`, and `dotfiles/dot-claude/settings.json` denies one call, `AskUserQuestion`. It forbids a redundancy nobody has committed. |
| `doc-type.arguments` | A skill's `arguments`, when present, is a non-empty list of bare kebab-case names, as in `arguments: [subject]`. | deterministic | deterministic | full | holds | none | high | `check_arguments` tests the list is non-empty and every item matches `KEBAB_RE`. Twelve skills carry the field; all pass. |
| `doc-type.no-argument-placeholder` | A skill's body carries no `$ARGUMENTS` placeholder and no `$0` placeholder. | deterministic | deterministic | none | holds | none | high | Test: grep the body for the two literals. No body of the 26 skills carries either. Nothing else states it, and the fault is one an author from another harness would commit. |
| `doc-type.references-one-level-deep` | No `.md` file in a skill's `references/` links to another `.md` file in that `references/`. | deterministic | deterministic | weak | holds | none | high | `check_references_depth` skips any target opening `/` or `~`, and globs `references/*.md` only. See Escalations. |
| `doc-type.skillmd-at-most-500-lines` | A skill's `SKILL.md` body is at most 500 lines. | deterministic | deterministic | none | holds | none | low | `body_length_advisory` prints to stderr and emits no rule id, which `standards/harness/explanation.md:39-42` states is deliberate. The longest body is `ralph-setup` at 144 lines. |
| `doc-type.agent` | The runbook is an agent. | deterministic | deterministic | none | holds | none | high | A condition, like `doc-type.skill`: the file's root decides it. It scopes the one H3 rule below it. |
| `doc-type.tools` | An agent's `tools`, when present, is a non-empty comma-separated string of tool names. | deterministic | deterministic | full | holds | none | high | `check_tools` tests the value is a non-empty string with no empty comma entry. Two of four agents carry it, `doc-set-auditor` and `tics-remover`; both pass. |

## Escalations

### `doc-type.steps-end-on-a-completion-criterion` — Every step of a runbook's body ends on a completion criterion

The predicate binds "every step of a runbook's body". The reason is the
rule's own why
([Steps end on a completion criterion](/standards/doc-type/runbook-conventions.md#steps-end-on-a-completion-criterion)):
nothing reaches a launched agent except the launching prompt, so "a step
that does not say when the work is done leaves the agent nothing else to
read it from".

Eighteen of the thirty runbooks carry numbered steps. Only
`dotfiles/dot-claude/skills/update-standards-pin/SKILL.md` gives every
step one, seven for seven. Concrete misses:

- `dotfiles/dot-claude/skills/log-friction/SKILL.md:31-38` — steps 1,
  2 and 3 end on the action ("Write the entry in the owner's
  register…", line 36), with no condition saying the step is finished.
- `dotfiles/dot-claude/skills/research/SKILL.md:15` — step 1 ends
  "Follow every claim back to the source that owns it", an instruction,
  not a criterion.
- `dotfiles/dot-claude/skills/runbook-creator/SKILL.md:41-43` — step 2,
  `## 2. Draft`, is the single sentence `{Write the new runbook} from
  those answers.` Step 1 of the same file, line 38, does carry one.
- `dotfiles/dot-claude/skills/commit/SKILL.md:29-31` — the three
  `## Staging` steps are bare commands.

The rule also never says what a step is. Twelve runbooks carry no
numbered list at all — `handoff` is three paragraphs, `wait-what` is
one — so whether their prose holds steps is undecided by the Standard.

**Proposal.** Rewrite the predicate. The repo's practice is that a
step whose end is not obvious carries a criterion, and the twelve
unnumbered runbooks show the writers do not treat every paragraph as a
step. The new sentence: "Where a runbook's body is a numbered list of
steps, each step ends on a completion criterion: the condition that
tells the agent the work is done." A repo change would touch
fourteen files to add criteria the authors chose not to write, and a
delete would lose the one reason the explanation gives for the rule.

### `doc-type.carries-its-chain` — Every edge of a runbook's contract is declared in the runbook's own file

The predicate allows one exception: "a ban the span vocabulary cannot
carry, which stays plain prose in the body and is listed in
[residual-ledger.md](/doc-types/runbook/residual-ledger.md)". Every
other edge must be a span.

The ledger records far more than bans. Its own entries name reads,
writes, and does edges that no span declares:

- `research` — "Could not express spawning the background research
  agent — `{Launch}` needs a link to one agent definition file". That
  is a does edge. `dotfiles/dot-claude/skills/research/SKILL.md:11`
  carries it as plain prose, "Spin up a background agent".
- `doc-set-deslop` — "Could not express the pre-flight `git status`
  check (no on-disk link, so no `{Read}`)". A read edge.
- `ralph-setup` — "Could not express the gate runs of §5 and §6 — a
  bare command in the target repo, with no on-disk link for a does
  edge".
- `update-standards-pin` — "the `--no-verify` commits, the landing
  commit, and the push" — writes—git edges.

Of the 27 ledger entries, only a handful record a ban; the rest record
reads, writes, does edges, reports, and conditions. The repo's practice
is the wider exception, and the predicate states the narrow one. The
`## Accepted classes` block at the head of the ledger confirms this: it
rules whole classes of operation "not accounted", none of them bans.

Five runbooks carry no ledger entry at all: `call-stack`,
`doc-set-diagram`, `document-remove-tics`, `wait-what`, and
`tics-remover`. Four of the 27 ledger headings name no runbook in the
population — `document-deslop`, `deslopper`, `set-auditor`,
`set-deslopper` — so the ledger and the population have drifted.

**Proposal.** Rewrite the predicate: replace "except a ban the span
vocabulary cannot carry" with "except an edge the span vocabulary
cannot carry". One word class widens, and the sentence then states what
the ledger already records. A repo change is not available — the ledger
entries exist precisely because the vocabulary cannot express those
edges — and a delete would leave the Reference chain bound by nothing.

### `doc-type.interactive-skills-inherit` — A skill that runs several turns with the user carries `model: inherit`

The reason is the rule's own why
([Interactive skills inherit](/standards/doc-type/runbook-conventions.md#interactive-skills-inherit)):
"A pinned model governs only the turn that loads the skill." A pinned
model on a multi-turn skill therefore governs the first turn and
nothing after it.

Three skills stop and wait for the user mid-run and pin a model:

- `dotfiles/dot-claude/skills/runbook-creator/SKILL.md:6` — `model:
  opus`. Line 15 says "Step 1 ends by putting its questions to the user
  and waiting", and line 38 makes the wait the step's criterion. The
  residual ledger lists it under "User interview loops".
- `dotfiles/dot-claude/skills/enable-repo-governance/SKILL.md:6` —
  `model: opus`. Line 75: "wait for their confirmation before calling
  the tail done".
- `dotfiles/dot-claude/skills/update-standards-pin/SKILL.md:6` —
  `model: opus`. Line 127: "{Report the remainder as one list of
  concrete choices} and wait".

The skills that do carry `inherit` are the ones the rule plainly aims
at: `grilling`, `domain-modeling`, `diagnosing-bugs`, `prototype`,
`call-stack`, `ralph-checkpoint`, `wayfinder`.

**Proposal.** Change the repo: set `model: inherit` in the front
matter of those three files. This is the case for a repo change — the
predicate states something the repo plainly wants, since seven other
multi-turn skills already carry `inherit`, and the pin is an oversight
whose effect the explanation calls out. The three edits are one line
each and no other file depends on the pinned value.

### `doc-type.references-one-level-deep` — No `.md` file in a skill's `references/` links to another `.md` file in that `references/`

The predicate bans one thing: a link from one `references/` file to
another. `check_references_depth` in `scripts/harness-files-lint`
decides it, but tests less than the predicate says. Two gaps:

- **Skipped link forms.** The guard clause drops any target that opens
  `http://`, `https://`, `mailto:`, `~`, or `/`. The last two are the
  problem: the repo writes cross-file links in exactly those forms.
  `dotfiles/dot-claude/skills/improve-codebase-architecture/references/design-it-twice.md:5`
  already links with `~/workspace/dev-playbook/…`. A sibling reference
  addressed as `~/workspace/dev-playbook/dotfiles/dot-claude/skills/prototype/references/ui.md`
  resolves to the same file the predicate bans and is never tested.
- **Depth.** The scan is `refs_dir.glob("*.md")`, not `rglob`. An `.md`
  file in a subdirectory of `references/` is never read, so a link out
  of it is never tested.

`LINK_RE` also matches inline links only, so a reference-style
definition, `[label]: sibling.md`, is invisible to the check.

The repo state holds: the only links inside a `references/` file are
two `../SKILL.md` parent links, one anchor-only link, and two
`~/workspace/…` links out to `standards/`. None targets a sibling.

## Detectors

**`scripts/harness-files-lint`.** The only check behind this Standard.
It walks four roots — `.claude/skills/`, `.claude/agents/`,
`dotfiles/dot-claude/skills/`, `dotfiles/dot-claude/agents/` — skipping
a bundle whose directory is a symlink and a dot-directory, and exits 2
on a directory under a skills root with no `SKILL.md`. Per file it
parses the front matter and decides ten of this Standard's rules, nine
of them in full: `front-matter` (required keys present, no key outside
the kind's closed vocabulary), `name-matches-its-home`,
`kebab-case-name`, `description` (string, at most 1024 characters,
exactly two sentences opening the second with `Use when`, or exactly
one where `disable-model-invocation: true`), `model-and-effort`,
`model-invocation-flag`, `arguments`, `tools`, and
`body-opens-with-an-h1`; the tenth, `references-one-level-deep`, is the
weak one. It also emits two rules of another family,
`harness.two-sections` and `harness.required-rules`, over
`dotfiles/dot-claude/CLAUDE.md`.

Two things the script does not do. The 500-line bound on a `SKILL.md`
body is a stderr advisory carrying no rule id, so
`doc-type.skillmd-at-most-500-lines` has a null verifier row even
though code decides the same number. And the script is not a thin shim
in the sense of
[Thin shims](/standards/standard/detectors.md#thin-shims): it holds
every rule's logic itself and imports only `md` and `findings` from
`src/dev_playbook/`.

**`tests/test_harness_files_lint.py`.** 37 tests. They cover
`front-matter`, `name-matches-its-home`, `description`, `arguments`,
`tools`, discovery, and the error state. Five rules the script decides
have no test at all: `kebab-case-name`, `model-and-effort`,
`model-invocation-flag`, `body-opens-with-an-h1`, and
`references-one-level-deep`. `test_repo_self_scan_is_clean` runs the
detector over dev-playbook itself, which is what keeps the tree green.
`tests/test_rule_registry.py` guards the `RULES` tuple against the
ids the module actually emits, so `--list-rules` cannot drift.

## Acronyms

- **H1** — markdown heading level one.
- **H3** — markdown heading level three.
- **YAML** — YAML Ain't Markup Language.
