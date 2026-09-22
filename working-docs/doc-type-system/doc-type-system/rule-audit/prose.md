---
type: General-Sheet
title: Prose Family Rule Audit
description: The rule audit over the standards/prose/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Prose Family Rule Audit

The `standards/prose/` family declares 20 rules in
[Doc Conventions](/standards/prose/conventions.md), over the population
"an authored document, except `type: Reference` and the paths in
`.prose-lint-exempt`" — 241 tracked Markdown files less one Reference
document and one exempt path. No rule is proposed for reclassification
in either direction: all 20 trailers match the kind the predicate
supports. Four rules are checked by `scripts/prose-lint`; the other
16 carry a null verifier row. Twelve rules break on real members. Three
of the four checked rules are weakly checked, one is full. One rule is
low value. The report elides the banned actor noun everywhere so the
report itself passes prose-lint, which scans `working-docs/`.

| id | rule | kind | proposed | check | state | overlap | value | note |
|---|---|---|---|---|---|---|---|---|
| `prose.one-rule-one-place` | "Each rule the document states lives in the lead sentence of its section." | stochastic | stochastic | none | breaks | none | high | `standards/prose/conventions.md:10-16` states three rules in the H1 section, none in a lead sentence of its own. |
| `prose.current-state-and-next-steps-only` | "The document describes what exists and what is planned next, and does not reference removed things, past state, or rejected alternatives." | stochastic | stochastic | none | holds | `prose.no-slop-tics` | high | Grep for history markers over all `*.md` outside `docs/decisions/` returned only present-tense policy sentences. |
| `prose.point-at-canonical-artifacts` | "Where a file is itself the standard, the document references that file and does not restate its contents." | stochastic | stochastic | none | breaks | `knowledge-organization.one-home` subsumes it | low | `standards/prose/explanation.md:99-101` restates `.prose-lint-vocabulary`'s entry rather than linking the file. |
| `prose.open-with-purpose` | "The opening states what the document is for and what a reader should be able to do after reading." | stochastic | stochastic | none | breaks | `knowledge-organization.the-opening-sentence`, `knowledge-organization.the-purpose-sentence` | high | `docs/index.md:3-4` and `doc-types/index.md:7-10` say what the directory holds, never what a reader can then do. |
| `prose.declare-before-use` | "A concept is defined before the prose leans on it — the definition sits above its first use." | stochastic | stochastic | none | holds | `knowledge-organization.terms-defined-once` | high | Sample: `standards/prose/conventions.md`, `standards/prose/explanation.md`, `standards/standard/detectors.md`, `guides/headless.md`. |
| `prose.block-form-fits-its-content` | "A block's form fits what it holds: prose for an argument, a list for parallel items, a table for repeated structure, a callout for an aside, a quote for wording that is the point, and a code block for code that runs or spans lines." | stochastic | stochastic | none | breaks | none | high | Eight two-row tables stand against the block's "three or more" threshold, e.g. `standards/tracking/explanation.md:142`. |
| `prose.declarative-present-tense` | "Every sentence is in the present tense, except in a member of a working documentation set, which may write a guess as a guess." | stochastic | stochastic | none | breaks | `knowledge-organization.speculative-voice` states the same exemption | high | `guides/headless.md:116`, `:132`, `:142` report a measurement in the past tense; a Guide is no working set. |
| `prose.positive-statement` | "A rule reads in the positive — what to do, where a thing lives — and a prohibition appears only where the prohibition itself is the rule." | stochastic | stochastic | none | holds | none | high | Checked all 20 prose rules and the four `no-*` rules of `standards/knowledge-organization/`; every negative lead is a rule that is itself a prohibition. |
| `prose.no-slop-tics` | "The document commits none of the tics [Slop Tics](/guides/slop-tics.md) names." | stochastic | stochastic | none | breaks | `prose.current-state-and-next-steps-only` | high | `harness-recipes/README.md:22` carries two Flourish tics, "supremely-powerful" and "Alas". |
| `prose.harness-loaded-agent-instructions` | "The document is a harness-loaded agent instruction: it is a `CLAUDE.md`, or a segment of its path inside the repository is `skills`, `rules`, or `agents`." | deterministic | deterministic | none | holds | `prose.declarative-documents` is its exact complement | high | A condition, so nothing can violate it. `src/dev_playbook/md.py:244-247` already computes the test; no check emits the id. |
| `prose.no-first-person` | "A harness-loaded agent instruction never speaks in the first person: the words `I`, `me`, and `my` appear nowhere in it, its frontmatter included, except `I` in the abbreviation `I/O` and any of the three inside a double-quoted utterance, an inline code span, or a fenced block." | deterministic | deterministic | weak | holds | none | high | `scripts/prose-lint` scans only `.md` members; ten tracked non-`.md` agent-instruction files are never read. All ten checked by hand and clean. |
| `prose.declarative-documents` | "The document is a declarative document: it is not a `CLAUDE.md`, and no segment of its path inside the repository is `skills`, `rules`, or `agents`." | deterministic | deterministic | none | holds | `prose.harness-loaded-agent-instructions` is its exact complement | high | A condition, so nothing can violate it. It earns its row by scoping `prose.third-person`. |
| `prose.third-person` | "A declarative document speaks in the declarative mood and the third person, and does not address the reader as `you`, except inside a double-quoted utterance." | stochastic | stochastic | none | breaks | none | high | Breaks on seven files outside quoted speech, `guides/writing-for-agents.md` on twelve lines alone. |
| `prose.name-concepts-once-use-consistently` | "One name per concept holds across the document." | stochastic | stochastic | none | breaks | `knowledge-organization.terms-defined-once` | high | `standards/prose/explanation.md:96` names the rule `banned-word`; line 99 of the same document names it "The banned word". |
| `prose.terminology-the-person-is-the-user` | "One actor — the dispatcher, reviewer, and approver — is the `user` throughout the document, its frontmatter, code spans, and fenced blocks included, never a synonym, in any case, plural, or compound." | stochastic | stochastic | none | breaks | subsumes `prose.the-banned-word` | high | `docs/decisions/0016-…:83`, `:85` call the actor "the owner"; `docs/decisions/0019-…:36` calls the actor "the reviewer". |
| `prose.the-banned-word` | "No tracked file of the repo, except a path `.prose-lint-exempt` lists, contains the word [elided], bare or plural, in any case, alone or in a compound, its frontmatter, code spans, and fenced blocks included." | deterministic | deterministic | weak | breaks | subsumed by `prose.terminology-the-person-is-the-user` | high | `docs/references/okf-spec.md` is tracked, is not listed in `.prose-lint-exempt`, and carries the word at lines 12, 31, 175 and 282. |
| `prose.the-repo-vocabulary` | "No tracked file under a directory the repo's `.prose-lint-vocabulary` names for a word contains that word, bare or plural, in any case, its frontmatter, code spans, and fenced blocks included; a word declared with no directory is banned in every tracked file of the repo." | deterministic | deterministic | weak | holds | none | high | No hit for the one declared word under `doc-types/` or `standards/doc-type/`. The code skips Reference documents and scratch, which the predicate does not. |
| `prose.spelling` | "The document's prose spells `judgment`, never the British `judgement` or `judgements`, in any case." | deterministic | deterministic | full | holds | none | high | `scan_text` reads the `.md` body outside fences with inline code stripped, which is the predicate's three exemptions exactly. No hit outside code spans. |
| `prose.heading-casing` | "The H1 is in Title Case and every heading below it is in sentence case, except that a proper noun or a code identifier keeps its native case at any level." | stochastic | stochastic | none | breaks | none | high | `dotfiles/dot-claude/skills/wayfinder/SKILL.md:24`, `:78`; and `## Considered Options`, the section name `standards/decisions/records.md:128` fixes, in four merged records. |
| `prose.grammatical-parallelism` | "Items that sit together take the same grammatical shape: the headings of a document, the bullets of a list, the clauses of a sentence." | stochastic | stochastic | none | breaks | none | high | The Standard's own H2s mix four imperative phrases with sixteen noun phrases, e.g. `standards/prose/conventions.md:37` beside `:87`. |

## Escalations

### `prose.one-rule-one-place` — "Each rule the document states lives in the lead sentence of its section."

`standards/prose/conventions.md:10-16` sits in the H1 section. Its lead
sentence is "How Markdown documents in workspace repos are written."
The two sentences after it state three rules that live in no section of
their own: a `type: Reference` document is unbound; a repo exempts a
path by listing it in a tracked `.prose-lint-exempt` at its root under
a comment saying why; a repo bans a word by declaring it with its
replacement in a tracked `.prose-lint-vocabulary` at its root. None has
a heading, a trailer, or a rule id, and `standards/verifiers.yaml`
carries no row for any of them.

This is not local to the prose family.
`standards/standard/detectors.md:10-25` does the same: it defines the
verifier table and the boundary table, and names
`scripts/verifier-table` as the writer and the lint, in the H1 section.
Every Standard in the tree states its own scope there.

**Proposal.** Rewrite the predicate so it states what the repo does on
purpose: "Each rule the document states lives in the lead sentence of
its section, except a statement of the document's own scope, which sits
in the section under the H1." The repo's shape is deliberate and
consistent across every Standard, so changing 13 Standards to obey the
present wording would be the expensive way out and would leave the
scope statements nowhere to go.

### `prose.point-at-canonical-artifacts` — "Where a file is itself the standard, the document references that file and does not restate its contents."

`.prose-lint-vocabulary` at the repo root is the canonical artifact: it
declares the one word the repo bans beyond the workspace's, its
replacement, and the two directories the ban covers.
`standards/prose/explanation.md:99-101` restates all three of those
values in prose instead of linking the file. When the declaration
changes, the explanation goes stale with no check to catch it: the
verifier row for this rule is null.

**Proposal.** Delete the predicate. `knowledge-organization.one-home`
already states it and states more — "A fact, rule, or decision has one
home, the member whose concern is the thing the fact binds and the most
general such member where the fact still holds; every other document
links there" — so nothing is lost by dropping the narrower rule, and
the reader stops meeting the same instruction twice. The value of this
rule is `low` on exactly that ground.

### `prose.open-with-purpose` — "The opening states what the document is for and what a reader should be able to do after reading."

`docs/index.md:3-4` opens "The repo's working papers — a mixture of
notes, unenforced policies, intentions, and explorations — and the
Decision Records." `doc-types/index.md:7-10` opens "The documentation
type system as built: what a doc-type is, this repo's instantiation,
and one directory per built doc-type." Both say what the directory
holds. Neither says what a reader can do after reading, which is the
second half of the predicate.

The two openings are not oversights. They are what
`knowledge-organization.the-opening-sentence` requires: "The
introduction of an `index.md` opens with a single sentence naming what
the directory holds, in that directory's own vocabulary." A
`README.md` is in the same position under
`knowledge-organization.the-purpose-sentence`. Two rules bind the same
sentence and ask for different things.

**Proposal.** Rewrite the predicate so the narrower rules own the file
classes they already govern: "The opening states what the document is
for and what a reader should be able to do after reading; an
`index.md` and a `README.md` answer instead to
[The opening sentence](/standards/knowledge-organization/indexes.md#the-opening-sentence)
and
[The purpose sentence](/standards/knowledge-organization/readme-content.md#the-purpose-sentence)."
Changing the indexes to obey the present wording would break the
knowledge-organization rules, so the repo state is not the thing to
move.

### `prose.block-form-fits-its-content` — "A block's form fits what it holds: prose for an argument, a list for parallel items, a table for repeated structure, a callout for an aside, a quote for wording that is the point, and a code block for code that runs or spans lines."

The rule's target-state block sets a threshold: "The same shape with
the same fields three or more times is a table; anything fewer or
uneven is prose with bold leads." Eight tracked Markdown files carry a
two-row table:

- `standards/tracking/explanation.md:142`
- `docs/external-skill-verdicts.md:65`
- `docs/decisions/0006-harvest-pocock-prototype-and-handoff.md:25`
- `working-docs/software-factory/agents/bug-pr-review.md:34`
- `working-docs/software-factory/agents/code-pr-review.md:39`
- `working-docs/software-factory/agents/doc-pr-review.md:40`
- `working-docs/software-factory/docs/factory-operations.md:117`
- `docs/references/okf-spec.md:107` (a Reference document, outside the population)

Seven of the eight are in the population. Three of them are the review
agents' finding tables, written to one shape on purpose.

**Proposal.** Rewrite the threshold clause to "The same shape with the
same fields two or more times is a table; anything uneven is prose with
bold leads." Seven members standing against the rule, several of them
recent and deliberate, say the repo reads a two-row table as a table.
Rewriting seven files to prose with bold leads would cost more than the
rule returns.

### `prose.declarative-present-tense` — "Every sentence is in the present tense, except in a member of a working documentation set, which may write a guess as a guess."

`guides/headless.md` carries `type: Guide` and lives under `guides/`,
so it is no member of a working documentation set and gets no
exemption. Three of its sentences are in the past tense:

- `:116` "A node was asked to write two files, one under an allowed
  directory and one outside it, and judged on whether the outside file
  existed afterwards"
- `:132` "as a deny rule it was ignored outright"
- `:142` "This was measured under one permission mode and two path
  forms."

All three report a measurement the document ran. The present tense
cannot carry them: "a node is asked" would state a standing practice,
not the experiment that produced the table above it.

**Proposal.** Rewrite the predicate: "Every sentence is in the present
tense, except a sentence reporting a measurement or an incident that
happened, and except in a member of a working documentation set, which
may write a guess as a guess." The measurement section is the reason
the guide exists and its findings are only intelligible as a report, so
this is a case the rule never meant to catch.

### `prose.no-slop-tics` — "The document commits none of the tics Slop Tics names."

`harness-recipes/README.md:22` reads "We recognize programatic,
API-based workflows as a supremely-powerful pattern in agentic
development. Alas, as a private individual with very limited funding,
we're restricted to subscription billing."

[Flourish](/guides/slop-tics.md#flourish) is defined as "A dramatic
word or image where an ordinary one carries the same meaning", and its
action is "Write the ordinary word." Two words in that sentence are
Flourish: "supremely-powerful", where "powerful" carries the same
meaning, and "Alas", which carries no meaning the following clause does
not already carry.

**Proposal.** Change the repo: rewrite that one sentence in
`harness-recipes/README.md`. The repo maintains the tic catalog at
`guides/slop-tics.md` and a `document-remove-tics` skill that rewrites
documents against it, so the intent is unambiguous and this is an
oversight in one sentence of one README. Nothing else in the tree
depends on the wording.

### `prose.no-first-person` — "A harness-loaded agent instruction never speaks in the first person."

The condition `prose.harness-loaded-agent-instructions` admits every
file whose path segment is `skills`, `rules`, or `agents`, whatever its
extension. `src/dev_playbook/md.is_agent_instruction` agrees: it tests
path segments only. But `prose_lint.audit` calls `scan_voice` inside
the `.md` branch:

    if rel.endswith(".md"):
        ...
        if md.is_agent_instruction(rel):
            findings.extend(scan_voice(rel, text))

So a non-`.md` agent-instruction file is never voice-scanned. Ten are
tracked, among them
`dotfiles/dot-claude/skills/diagnosing-bugs/agents/openai.yaml`,
`dotfiles/dot-claude/skills/usage-report/scripts/report.sh`, and
`dotfiles/dot-claude/skills/wayfinder/agents/openai.yaml`.

`audit` also skips what `md.classify` returns `"excluded"` for — a
`PLAN.md`, a `PROGRESS.md`, and the root `tmp/` tree — which the
predicate and the population do not exempt. Neither is tracked in this
repo today, so the skip bites nothing here.

The repo state is clean. All ten non-`.md` files were read by hand. The
one first-person token,
`dotfiles/dot-claude/skills/wait-what/agents/openai.yaml:3`
(`short_description: "Re-pitch that — simpler, with the context I'm
missing"`), sits inside a double-quoted utterance, which the predicate
exempts.

### `prose.the-banned-word` — "No tracked file of the repo, except a path `.prose-lint-exempt` lists, contains the word [elided]."

The predicate makes a claim about every tracked file of the repo.
`docs/references/okf-spec.md` is tracked, is not listed in
`.prose-lint-exempt`, and carries the word at lines 12, 31, 175 and
282. By its own words the predicate is false of this repo.

The detector does not report it, and is right not to.
`prose_lint.audit` skips a `type: Reference` document through
`external.is_verbatim_doc`, and `docs/references/okf-spec.md` carries
`type: Reference` at line 2. The Standard's population line agrees:
"an authored document, except `type: Reference` and the paths in
`.prose-lint-exempt`". The predicate is the only thing that reaches
wider than the population.

That makes the check `weak` as well as the state `breaks`. Measured
against the predicate's words, `audit` skips four classes the predicate
does not exempt: a `type: Reference` document, a `md.classify`
`"excluded"` path, a symlink, and a file carrying a NUL byte. Only the
first bites today — this repo tracks no symlink and no binary file.

A second fault sits under the first.
`doc-type.decidable-predicates` requires each predicate to be "true or
false of one member of the population at one moment". A claim about
every tracked file of the repo is not a predicate over one member; a
reader holding one document cannot decide it.

**Proposal.** Rewrite the predicate as a claim about the member:
"The document does not contain the banned actor noun, bare or plural,
in any case, alone or in a compound, its frontmatter, code spans, and
fenced blocks included." That is per-member, it matches the population
line already in the frontmatter, and it matches `scan_banned` exactly.
The repo state is correct as it stands: the Reference document is a
verbatim upstream mirror that keeps its author's words, which is the
whole point of the `type: Reference` exemption, so changing the repo is
not an option here. `prose.the-repo-vocabulary` needs the same rewrite
for the same reason.

### `prose.the-repo-vocabulary` — "No tracked file under a directory the repo's `.prose-lint-vocabulary` names for a word contains that word."

The repo obeys it: `.prose-lint-vocabulary` declares one word, covering
`doc-types/` and `standards/doc-type/`, and a case-insensitive grep for
that word and its plural under both directories returns nothing.

The check is weak on two counts. First, the same four skips as
`prose.the-banned-word`: `prose_lint.audit` passes over a `type:
Reference` document, a `md.classify` `"excluded"` path, a symlink, and
a file carrying a NUL byte, none of which the predicate exempts. None
bites today, because the one Reference document sits in
`docs/references/` and no declared directory reaches it.

Second, `Word.covers` tests `rel.startswith(d + "/")`, so a file at the
directory path itself is outside the ban while everything beneath it is
inside. The predicate says "under a directory", which reads the same
way, so this one is agreement rather than a gap — noted so the design
pass does not have to re-derive it.

`Word.pattern` compiles `\b{word}s?\b`, and a trailing `\b` matches at
a hyphen, so the code also catches a hyphenated compound. The predicate
says only "bare or plural". Here the code tests *more* than the
predicate states, which the `prose.the-banned-word` predicate covers
with "alone or in a compound" and this one does not.

### `prose.third-person` — "A declarative document speaks in the declarative mood and the third person, and does not address the reader as `you`, except inside a double-quoted utterance."

Seven files in the population address the reader as `you` outside any
double-quoted utterance:

- `guides/writing-for-agents.md:13`, `:28`, `:52`, `:61`, `:63`, `:70`,
  `:72`, `:78`, `:89`, `:90`, `:98`, `:102` — "Every document and
  pointer you add spends one of two budgets"
- `guides/bootstrap.md:27`, `:30` — "the commit never reaches you"
- `guides/slop-tics.md:252` — "Write for the reader in front of you"
- `docs/sandboxing.md:60` — "the agent stalls or reports something
  unrelated, and you"
- `harness-recipes/recipes/ralph-loop.md:19`, `:195`
- `harness-recipes/recipes/scatter-gather.md:17`
- `working-docs/doc-type-system/doc-type-system/body-drain.md:18`,
  `:21`, `:22`, `:23`, `:50`, `:62`, `:74`, `:91`, `:97`, `:145`,
  `:146`, `:150`, `:180`, and the sibling `rule-audit/PROMPT.md`
  throughout

Every one of them instructs an executing agent. The condition
`prose.declarative-documents` classifies by path — not a `CLAUDE.md`,
no path segment `skills`, `rules`, or `agents` — so a prompt file under
`working-docs/` and a guide under `guides/` fall on the declarative
side however they are addressed. The repo writes agent-facing
instructions in several places the three path segments do not reach.

**Proposal.** Rewrite the predicate: "A declarative document speaks in
the declarative mood and the third person, and does not address the
reader as `you`, except inside a double-quoted utterance or where the
document is a prompt an agent executes." The alternative — moving the
condition from path to audience — would turn two deterministic rules
stochastic, and rewriting seven documents out of the second person
would fight what each is for. The rule is already stochastic, so
"a prompt an agent executes" costs it nothing.

### `prose.name-concepts-once-use-consistently` — "One name per concept holds across the document."

`standards/prose/explanation.md:96` writes "prose-lint's `banned-word`
check refuses the commonest synonym everywhere in the tree". Line 99 of
the same document writes "The banned word is the workspace's layer of a
vocabulary". The rule's heading in
`standards/prose/conventions.md:147` is "The banned word" and its
trailer id is `prose.the-banned-word`. One concept, two names, three
lines apart.

**Proposal.** Change the repo: write "prose-lint's
[The banned word](/standards/prose/conventions.md#the-banned-word)
check" at `standards/prose/explanation.md:96`. It is one phrase in one
file, the document already uses the other name six lines later, and the
rule's own name is fixed by its heading and its verifier row, so there
is nothing to weigh.

### `prose.terminology-the-person-is-the-user` — "One actor — the dispatcher, reviewer, and approver — is the `user` throughout the document."

Three merged Decision Records name that actor by a synonym:

- `docs/decisions/0016-pocock-skills-sweep-2026-07.md:83` — "No
  rationale beyond the owner's ruling is recorded"
- `docs/decisions/0016-…:85` — "the owner reversed it the same day"
- `docs/decisions/0019-one-word-for-the-person.md:36` — "the reviewer
  upheld by eye"

`0019` is the record that established the rule, which shows the drafts
predate it rather than defy it.

`decisions.immutable-after-merge` at
`standards/decisions/records.md:108` freezes a merged record, so the
repo cannot be changed to obey.

**Proposal.** Rewrite the predicate to carry the exemption its sibling
already carries: add "A merged Decision Record is exempt" as
`prose.current-state-and-next-steps-only` does at
`standards/prose/conventions.md:34`. The precedent is in the same
Standard, the immutability rule makes the repo change impossible, and
the rule keeps its whole force over every document that can still be
edited.

### `prose.heading-casing` — "The H1 is in Title Case and every heading below it is in sentence case."

Two live files carry Title Case below the H1 with no proper noun and no
code identifier:

- `dotfiles/dot-claude/skills/wayfinder/SKILL.md:24` — `## The Map`
- `dotfiles/dot-claude/skills/wayfinder/SKILL.md:78` — `## Ticket Types`

Four merged Decision Records carry `## Considered Options`:
`0006-harvest-pocock-prototype-and-handoff.md:23`,
`0013-candidates-file-over-github-backlog.md:21`,
`0014-workspace-spans-machines.md:28`,
`0029-retire-instruments.md:26`. That heading is not their own
invention: `standards/decisions/records.md:128` names the optional
sections "`Considered Options` and `Consequences`" in Title Case, so
the Standard prescribes the break. `decisions.immutable-after-merge`
then freezes the four records.

`standards/knowledge-organization/document-types.md:107-129` carries
`## Typed Standard`, `## Typed Loop`, `## Typed Guide` and `##
Typed Explanation`. Those pass: `Standard`, `Loop`, `Guide` and
`Explanation` are the frontmatter `type` values, which are code
identifiers keeping their native case.

**Proposal.** Change the repo, in two files: put
`dotfiles/dot-claude/skills/wayfinder/SKILL.md:24` and `:78` into
sentence case, and put the section names at
`standards/decisions/records.md:128` into sentence case so the template
stops prescribing the break for new records. The wayfinder headings are
a plain oversight in a file nothing else references by anchor, and the
records Standard is the source of the other four. The four merged
records stay as they are, which needs one clause added to this
predicate exempting a merged Decision Record — the same clause
`prose.terminology-the-person-is-the-user` needs above.

### `prose.grammatical-parallelism` — "Items that sit together take the same grammatical shape: the headings of a document, the bullets of a list, the clauses of a sentence."

The Standard's own 20 H2 headings break it. Sixteen are noun phrases
— "Declarative present tense" (`:79`), "Positive statement" (`:87`),
"The banned word" (`:147`), "Heading casing" (`:172`). Four are
imperative verb phrases:

- `standards/prose/conventions.md:37` — "Point at canonical artifacts"
- `:44` — "Open with purpose"
- `:52` — "Declare before use"
- `:133` — "Name concepts once, use consistently"

These sit together in one list, the document's heading list, and take
two grammatical shapes.

**Proposal.** Change the repo: rename the four imperative headings to
noun phrases in `standards/prose/conventions.md`. The cost is bounded
and visible — each rename changes the heading's GitHub slug, so the
trailer id changes with it, and four key rows in
`standards/verifiers.yaml` and four anchors in
`standards/prose/explanation.md` follow. None of the four ids appears
in `src/dev_playbook/prose_lint.py`, whose four constants are
`prose.spelling`, `prose.the-banned-word`, `prose.the-repo-vocabulary`
and `prose.no-first-person`, so no detector changes. The rule states
something the repo plainly wants — sixteen of twenty headings already
obey it — and the four exceptions are drafting residue, not a decision.
`prose.point-at-canonical-artifacts` is recommended for deletion above,
which retires one of the four without a rename.

## Detectors

**`scripts/prose-lint`** is the only check the family names. Four of
the 20 rules point at it in `standards/verifiers.yaml` —
`prose.spelling`, `prose.the-banned-word`, `prose.the-repo-vocabulary`
and `prose.no-first-person`; the other 16 rows are null. The
script is a thin shim: it puts the checkout's `src/` on `sys.path` and
calls `dev_playbook.prose_lint.main`. It answers `--list-rules` through
`findings.print_rules`, printing exactly the four ids, and exits 0
clean, 1 with findings, 2 on a `CannotRun`.

**`src/dev_playbook/prose_lint.py`** holds the logic.
`audit(root)` walks `md.find_files(root)` — `git ls-files --cached
--others --exclude-standard`, so gitignore-aware and worktree-scoped —
and drops each path that `md.classify` calls `"excluded"`, that
`.prose-lint-exempt` lists, that is a symlink, or that carries a NUL
byte. For a `.md` file it parses frontmatter, skips a `type: Reference`
document through `external.is_verbatim_doc`, runs `scan_text` over the
body for `prose.spelling`, and runs `scan_voice` over the whole file
for `prose.no-first-person` where `md.is_agent_instruction` holds. For
every surviving file of any type it runs `scan_banned`, which emits
`prose.the-banned-word` for a word of `WORKSPACE_VOCABULARY` and
`prose.the-repo-vocabulary` for a word `vocabulary(root)` read from
`.prose-lint-vocabulary`. A malformed vocabulary declaration or a
malformed frontmatter raises `CannotRun`, which `main` turns into exit
2 rather than a traceback.

**`src/dev_playbook/voice.py`** holds the first-person vocabulary that
`scan_voice` matches: three patterns, `\bI\b(?!/O)`, `\b[Mm]e\b` and
`\b[Mm]y\b`, each with its own message. It masks nothing itself —
`scan_voice` strips inline code spans and double-quoted spans and drops
fenced lines before matching. `dev_playbook.repo_init` reads the same
vocabulary to refuse a repo name carrying one of the three words, which
is why it sits in its own module.

**`tests/dev_playbook/test_prose_lint.py`** covers all four rules in 55
tests, including `test_dev_playbook_self_scan_is_clean`, which runs the
detector over this checkout. Nothing there tests a non-`.md`
agent-instruction file for voice, which is the gap
`prose.no-first-person` is escalated for above.

## Acronyms

- **API** — Application Programming Interface.
- **H1** — markdown heading level one.
- **H2** — markdown heading level two.
- **NUL** — the zero byte.
