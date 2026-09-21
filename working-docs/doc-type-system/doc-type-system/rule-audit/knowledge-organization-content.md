---
type: General-Sheet
title: Cross-References, README, and CONTEXT Rule Audit
description: The rule audit over the knowledge-organization/ family — every rule's kind, detector coverage, repo state, and overlap, with escalations for what breaks or is weakly checked
---

# Cross-References, README, and CONTEXT Rule Audit

Twenty-one rules across three Standards of
[standards/knowledge-organization/](/standards/knowledge-organization/index.md):
eleven in [Cross-References](/standards/knowledge-organization/cross-references.md),
four in [README Content](/standards/knowledge-organization/readme-content.md),
six in [CONTEXT.md Content](/standards/knowledge-organization/context-content.md).
Two rules are proposed for reclassification, both from deterministic to
stochastic (`stable-named-anchor`, `workspace-path-for-a-stable-location`);
none go the other way. Seven rules break. One rule is fully checked
(`the-language-section`), four are weakly checked (`reference-resolves`,
`fragment-anchor-matches-the-slug`, `link-same-bundle`, `h1`), and sixteen
have no check at all — the family states a detailed reference grammar and
`scripts/ref-lint` decides three of its eleven rules. Two rules are low
value, the complementary condition pair `fixed-repo-root` and
`no-fixed-repo-root`, which no member can fail.

| id | rule | kind | proposed | check | state | overlap | value | note |
|----|------|------|----------|-------|-------|---------|-------|------|
| `knowledge-organization.reference-resolves` | "A reference names a file or a directory that exists." | deterministic | deterministic | weak | holds | none | high | ref-lint resolves only `/`-root and `~/workspace/` targets. Relative targets and the 28 `~/.claude/…` targets are never opened. |
| `knowledge-organization.fragment-anchor-matches-the-slug` | "A reference that appends `#anchor` to a markdown file names in that anchor the GitHub slug of a heading the file carries." | deterministic | deterministic | weak | holds | none | high | Same blind spot: anchors on relative and `~/.claude/…` targets are unchecked. 448 anchored references, all correct. |
| `knowledge-organization.stable-named-anchor` | "A reference's `#anchor` names its target heading by the words of the heading and carries no number that is the heading's position in the file." | deterministic | stochastic | none | holds | none | high | No anchor in the repo starts with a digit. The second sentence, "names the concept … in the link text", needs judgment. |
| `knowledge-organization.citation-another-repo` | "A reference to a file or directory in a repository other than the referencing file's own is an inline link whose target is the full workspace path, beginning `~/workspace/<repo>/`." | deterministic | deterministic | none | breaks | none | high | `dotfiles/dot-claude/skills/log-friction/SKILL.md:45` writes `~/workspace/mission-control` bare in an indented code block. The scope exempts fenced blocks only. |
| `knowledge-organization.skill-invocation` | "A reference to a skill is its bare slash invocation, `/<skill-name>`, with no link and no code markup." | deterministic | deterministic | none | breaks | `knowledge-organization.citation-another-repo` | high | 21 links of the form `[/commit](~/.claude/skills/commit/SKILL.md)`, plus code-markup mentions. Conflicts with `citation-another-repo` on a cross-repo skill. |
| `knowledge-organization.fixed-repo-root` | "The referencing file has a fixed repo root: no segment of its path inside the repository is `skills`, `rules`, or `agents`." | deterministic | deterministic | none | holds | `knowledge-organization.no-fixed-repo-root` | low | A condition, not an obligation: no member can fail it. The heading must stay; its trailer and verifier row carry nothing. |
| `knowledge-organization.link-same-bundle` | "A reference to a file or directory in the referencing file's own repository is an inline link whose target is a root-absolute path, beginning `/` and naming the path from the repository root." | deterministic | deterministic | weak | holds | none | high | ref-lint flags only one wrong shape, a same-repo `~/workspace/` citation. A relative or `~/.claude/…` target in a fixed-root file passes. |
| `knowledge-organization.no-fixed-repo-root` | "The referencing file has no fixed repo root: a segment of its path inside the repository is `skills`, `rules`, or `agents`." | deterministic | deterministic | none | holds | `knowledge-organization.fixed-repo-root` | low | The exact complement of `fixed-repo-root`; the two cover every file and neither can fail. Same verdict on the trailer. |
| `knowledge-organization.workspace-path-for-a-stable-location` | "A reference to a file at a stable location in the referencing file's own repository is an inline link whose target is the full `~/workspace/<repo>/<path>` path, unless the target is inside the referencing file's own skill bundle." | deterministic | stochastic | none | breaks | `knowledge-organization.inline-code-for-a-varying-location` | high | 28 `~/.claude/…` links name in-repo files by their stowed path. "Stable location" is the complement of a stochastic rule's judgment. |
| `knowledge-organization.relative-path-inside-the-bundle` | "A reference to a file inside the referencing file's own skill bundle, a sibling, a file under `references/`, or the parent, is an inline link whose target is a path relative to the referencing file." | deterministic | deterministic | none | holds | none | high | All 12 in-bundle references use a relative path and resolve, for example `dotfiles/dot-claude/skills/prototype/references/logic.md:58` to `../SKILL.md`. |
| `knowledge-organization.inline-code-for-a-varying-location` | "A reference to a file whose path varies between repositories, `CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, or `Makefile`, or to a directory, `docs/decisions/`, is inline code." | stochastic | stochastic | none | breaks | `knowledge-organization.workspace-path-for-a-stable-location` | high | `index.md:13` links `[Vocabulary](/CONTEXT.md)`, which the index listing rules demand. Would be deterministic against a closed roster. |
| `knowledge-organization.h1` | "A `README.md` holds an H1 heading." | deterministic | deterministic | weak | holds | none | high | repo-lint reads the root `README.md` only. The six directory READMEs are unchecked; all six carry an H1. |
| `knowledge-organization.the-purpose-sentence` | "A sentence follows the H1 of a `README.md` and says what the repo or the directory the file introduces holds or is for." | stochastic | stochastic | none | holds | none | high | All seven READMEs carry one. `docs/decisions/README.md` is the thinnest: it names the contents through the index link. |
| `knowledge-organization.no-agent-instructions-or-decisions` | "A `README.md` holds no instruction addressed to an agent and no architecture decision." | stochastic | stochastic | none | breaks | `knowledge-organization.no-roster-of-harness-injected-files` | high | `dotfiles/README.md:33-52` argues a design: "the live file is the authority", then "Two consequences hold the design together". No Decision Record states it. |
| `knowledge-organization.no-roster-of-harness-injected-files` | "A `README.md` enumerates no skill and no other file the harness injects into a session." | stochastic | stochastic | none | holds | `knowledge-organization.no-agent-instructions-or-decisions` | high | `dotfiles/README.md:20` names the `skills/` directory and one example, not a roster. No README lists the skill set. |
| `knowledge-organization.glossary-only` | "A repo's `CONTEXT.md` holds a glossary and nothing else: no implementation detail, no specification, and no scratch note." | stochastic | stochastic | none | holds | none | high | `CONTEXT.md` holds an H1, one intro sentence, and `## Language` with four grouped term blocks. Nothing else. |
| `knowledge-organization.vocabulary-type` | "A repo's `CONTEXT.md` declares `type: Vocabulary` in its frontmatter." | deterministic | deterministic | none | holds | `knowledge-organization.types` | high | `CONTEXT.md:2` declares it. Overlap is partial: okf-lint's `types` accepts any registered type, so a wrong-but-registered type passes. |
| `knowledge-organization.the-language-section` | "A repo's `CONTEXT.md` has a `## Language` section." | deterministic | deterministic | full | holds | none | high | repo-lint compares the exact line `## Language` against the body outside fences. `CONTEXT.md:11` carries it. |
| `knowledge-organization.entry-shape` | "An entry under `## Language` in a repo's `CONTEXT.md` is the term in bold on its own line, its definition on the lines beneath, and, at most, one final `_Avoid_:` line naming the words retired in the term's favor." | deterministic | deterministic | none | breaks | none | high | The rule's template block writes `**Order**:` with a colon and no group headings. Every live entry omits the colon and sits under an H3. |
| `knowledge-organization.tight-definitions` | "An entry's definition in a repo's `CONTEXT.md` is one sentence that says what the term is, and where a concept document defines the term the definition links that document." | stochastic | stochastic | none | breaks | none | high | Seven entries run to two sentences: Lint, Detector, Verifier table, Gate, Concept document, Procedure, Runbook. |
| `knowledge-organization.project-terms-only` | "Every term with an entry under `## Language` in a repo's `CONTEXT.md` is specific to the project's context and is used beyond the documentation set that defines it." | stochastic | stochastic | none | holds | none | high | Every term is project-specific. **Concern** is the weakest case: it is used almost only inside the documentation-sets set that defines it. |

## Escalations

### `knowledge-organization.reference-resolves` — "A reference names a file or a directory that exists."

The predicate binds every reference in the population, which the Standard
opens as "a reference from an authored document to a workspace file,
directory, or skill". `scripts/ref-lint:187-205` opens a target only when it
begins `/` or `~/workspace/`:

```python
if target_str.startswith("~/workspace/"):
    record(target_str, line_num, citation_status(path_str, fragment))
elif target_str.startswith("/"):
    actual = repo_root / path_str.lstrip("/")
    record(target_str, line_num, status_of(actual, fragment))
```

Two live reference classes fall outside that test. The first is the relative
in-bundle link the family's own
[Relative path inside the bundle](/standards/knowledge-organization/cross-references.md#relative-path-inside-the-bundle)
rule mandates, for example
`dotfiles/dot-claude/skills/prototype/SKILL.md:17` to `references/logic.md`.
The second is the 28 `~/.claude/…` links, for example
`dotfiles/dot-claude/skills/compact-prep/SKILL.md:17`. I resolved both classes
by hand: every one exists, so the rule holds today. A third gap is narrower:
`md.MD_LINK_PATTERN` matches one line, so a link whose `[text](` splits across
a newline with a `/`-root target is invisible to both passes. The repo has two
multi-line links and both use `~/workspace/`, which the bare-citation pass
still resolves.

### `knowledge-organization.fragment-anchor-matches-the-slug` — "A reference that appends `#anchor` to a markdown file names in that anchor the GitHub slug of a heading the file carries."

`scripts/ref-lint:138-151` computes the anchor test, and it is exact: it
compares the fragment against `md.heading_slugs`, which reads ATX headings
outside fences. The weakness is inherited, not local — the anchor is tested
only for a target the scanner reached, so the same relative and `~/.claude/…`
targets named above carry unchecked anchors. I checked all 448 anchored
references in the repo, including the unscanned classes, and each anchor names
a real heading slug.

### `knowledge-organization.link-same-bundle` — "A reference to a file or directory in the referencing file's own repository is an inline link whose target is a root-absolute path, beginning `/` and naming the path from the repository root."

The predicate states a positive form: root-absolute, from the repository root.
`scripts/ref-lint:170-180` tests one negative shape only:

    if fixed_root and is_same_repo_citation(resolved, repo_name):
        return "wrong-form"

So a fixed-root file that names an in-repo file by a relative path, or by a
`~/.claude/…` path, or in bare prose, passes the detector. The repo obeys the
predicate anyway: I scanned every fixed-root markdown file that is not a
numbered Decision Record and found no relative link and no root-absolute link
outside the fixed-root set. The one fixed-root file with a `~/.claude/…`
target, `doc-types/runbook/encoding.md:51`, holds it inside a fenced code
block, which the population excludes.

### `knowledge-organization.h1` — "A `README.md` holds an H1 heading."

The population is "a README.md", any README. `scripts/repo-lint:566-570`
reads one file:

    readme = root / "README.md"

`tests/test_repo_lint.py:241` covers the root file only, so nothing pins the
narrower reading. The repo carries seven READMEs — `README.md`,
`docs/decisions/README.md`, `dotfiles/README.md`, `harness-recipes/README.md`,
`scripts/README.md`, `standards/README.md`, and
`working-docs/software-factory/docs/README.md`. I read all seven; each opens
its body with an H1, so the rule holds and the gap is coverage, not state.

### `knowledge-organization.citation-another-repo` — "A reference to a file or directory in a repository other than the referencing file's own is an inline link whose target is the full workspace path, beginning `~/workspace/<repo>/`."

The Standard's lead paragraph exempts one container: "A fenced code block,
triple backticks or `~~~`, may hold `~/workspace/` and `/`-root paths in shell
examples or sample output, and a reference inside it is out of scope." An
indented code block is not a fenced code block, and the repo uses indented
blocks for shell examples.
`dotfiles/dot-claude/skills/log-friction/SKILL.md:45` is one line, indented
four spaces:

    git -C ~/workspace/mission-control add friction/log.md && git -C ~/workspace/mission-control commit -m "<subject>" -m "Co-Authored-By: Claude <noreply@anthropic.com>" && git -C ~/workspace/mission-control push

Three bare references to another repo's directory, none an inline link.
`scripts/ref-lint` agrees that the line is in scope: `md.content_lines` skips
fenced blocks only, so the detector reads the line, resolves the paths, and
stays quiet because they exist. The four genuine prose references to another
repo — `docs/machines.md:13`, `docs/measurement-derivation.md:160`,
`dotfiles/dot-claude/skills/log-friction/SKILL.md:31`, and
`dotfiles/dot-claude/skills/idea/SKILL.md:14` — are all correctly formed inline
links.

Proposal. Rewrite the scope sentence so the exemption names both code-block
forms: "A code block, fenced with triple backticks or `~~~` or indented four
spaces, may hold `~/workspace/` and `/`-root paths in shell examples or sample
output, and a reference inside it is out of scope." The shell commands are
deliberate — a runbook must give a runnable `git -C` line — and turning a
command argument into a markdown link would break the command. The predicate,
not the repo, is what is wrong here.

### `knowledge-organization.skill-invocation` — "A reference to a skill is its bare slash invocation, `/<skill-name>`, with no link and no code markup."

The predicate bars two wrappers, a link and code markup, and the repo uses
both. Twenty-one references wrap the invocation in a link whose target is the
stowed skill path, across eleven files:

    dotfiles/dot-claude/skills/compact-prep/SKILL.md:17
      [/commit](~/.claude/skills/commit/SKILL.md)
    dotfiles/dot-claude/skills/wayfinder/SKILL.md:83
      [/prototype](~/.claude/skills/prototype/SKILL.md)
    working-docs/software-factory/skills/intake/SKILL.md:34
      [/grilling](~/.claude/skills/grilling/SKILL.md)

Two more wrap it in a link and code markup together, from fixed-root files:
`harness-recipes/recipes/ralph-loop.md:194` writes
``[`ralph-setup`](/dotfiles/dot-claude/skills/ralph-setup/SKILL.md)`` and
`:213` writes
``[`/ralph-checkpoint`](/dotfiles/dot-claude/skills/ralph-checkpoint/SKILL.md)``.
Code markup alone appears at `doc-types/standard/residual-ledger.md:71`,
"the rule is the `/wayfinder` skill's", and at
`doc-types/runbook/residual-ledger.md:97` and `:220`.

The rule also conflicts with
[Citation, another repo](/standards/knowledge-organization/cross-references.md#citation-another-repo).
`dotfiles/dot-claude/skills/idea/SKILL.md:14` references mission-control's
idea skill. As a skill it must be bare `/idea`; as a file in another repo it
must be an inline `~/workspace/mission-control/…` link. It is written as the
link, so it obeys one rule and breaks the other, and the Standard says which
wins nowhere.

Proposal. Rewrite the predicate to bind the invocation, not every mention:
"A reference that tells the reader to invoke a skill is its bare slash
invocation, `/<skill-name>`, with no link and no code markup; a reference to a
skill's file is a Link or a Citation like any other file reference." The
linked form is deliberate and load-bearing — a runbook names the skill it
delegates to and gives the executing agent the file to read — and 23 sites
across eleven files would change under the other reading. The bare form still
governs the prose mention, which is what the rule was for.

### `knowledge-organization.workspace-path-for-a-stable-location` — "A reference to a file at a stable location in the referencing file's own repository is an inline link whose target is the full `~/workspace/<repo>/<path>` path, unless the target is inside the referencing file's own skill bundle."

Twenty-eight links from rootless files name an in-repo file by its stowed
runtime path rather than its repository path. Seven name an agent definition:

    dotfiles/dot-claude/agents/doc-set-deslopper.md:70
      [doc-set-auditor](~/.claude/agents/doc-set-auditor.md)
    dotfiles/dot-claude/skills/ralph-checkpoint/SKILL.md:40
      [ralph-checkpointer](~/.claude/agents/ralph-checkpointer.md)

Those files live in this repository at `dotfiles/dot-claude/agents/`, so the
predicate asks for
`~/workspace/dev-playbook/dotfiles/dot-claude/agents/doc-set-auditor.md`. The
remaining 21 are the skill links listed in the escalation above. The one
reference that does obey the predicate,
`working-docs/software-factory/agents/code-pr-review.md:128`, shows the form
works: it names the refactor catalogue as
`~/workspace/dev-playbook/working-docs/software-factory/docs/refactor-catalogue.md`.
`scripts/ref-lint` sees none of the 28, because `~/.claude/…` matches neither
the `/` branch nor the `~/workspace/` branch of `scan_file`.

The predicate also imports a judgment call. "A stable location" is the
complement of "a file whose path varies between repositories" in
[Inline code for a varying location](/standards/knowledge-organization/cross-references.md#inline-code-for-a-varying-location),
which the trailer declares stochastic. The same distinction cannot be
deterministic here and stochastic there, which is why the proposed kind is
`stochastic`.

Proposal. Rewrite the predicate to admit the runtime path for a harness-loaded
file: "A reference to a file at a stable location in the referencing file's own
repository is an inline link whose target is the full
`~/workspace/<repo>/<path>` path, or, where the target is a skill or an agent
definition the harness loads from `~/.claude/`, that runtime path; the
exception is a target inside the referencing file's own skill bundle." The
`~/.claude/` form is what the reading agent can actually open at run time,
which is the whole reason a rootless file cites by absolute path, so the repo's
28 sites look deliberate rather than careless. Changing them instead would edit
eleven runbooks to point at paths the executing agent cannot reach from an
arbitrary repo.

### `knowledge-organization.inline-code-for-a-varying-location` — "A reference to a file whose path varies between repositories, `CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, or `Makefile`, or to a directory, `docs/decisions/`, is inline code."

`CONTEXT.md` is named in the predicate, and the root index links it.
`index.md:13`:

    - [Vocabulary](/CONTEXT.md) — The workspace's established vocabulary — the canonical terms to use exactly

That link is not optional. An `index.md` row must be a link under
[The listing](/standards/knowledge-organization/indexes.md), and `okf-lint`
decides `knowledge-organization.the-listing` and
`knowledge-organization.row-shape` against every row. So one rule of the family
forbids exactly what another rule of the family requires, and `okf-lint` wins
because it is the one with a detector. This is the only live conflict: no other
reference in the repo links a varying-location file.

Proposal. Rewrite the predicate to exempt the row that names a real file:
"A reference that names a file generically, because its path varies between
repositories — `CLAUDE.md`, `CONTEXT.md`, `specs/design.md`, `Makefile`, or the
directory `docs/decisions/` — is inline code; a reference to one repository's
own copy, such as an `index.md` listing row, is a Link." The index row points
at this repository's `CONTEXT.md` at a path that does not vary, so the rule's
reason does not apply to it, and the repo cannot obey both rules as written.

### `knowledge-organization.no-agent-instructions-or-decisions` — "A `README.md` holds no instruction addressed to an agent and no architecture decision."

`dotfiles/README.md:33-52` carries a section headed "Settings: the live file is
the authority". It states a position, "The repo is the carrier that syncs
settings between machines, not a source of authority to enforce — committing
and pushing those edits is the user's", and then argues it: "Two consequences
hold the design together", followed by two named consequences with the hook
files that implement each. That is a decision with its rationale, which
[Why a README lists no harness files](/standards/knowledge-organization/explanation.md#why-a-readme-lists-no-harness-files)
sends to `docs/decisions/`: "Agent instructions and architecture decisions are
absent from a README because they live in `CLAUDE.md` and `docs/decisions/`."
No numbered record states it — I read the titles of all 29 records under
`docs/decisions/`, and none covers the settings symlink.

The instruction half is clean. No README addresses an agent in the second
person. The closest lines, `README.md:44` and `dotfiles/README.md:57`, both
tell the user to run `scripts/sync-dotfiles` from the main checkout, and both
name the user as the actor.

Proposal. Rewrite the predicate so it bars the decision that belongs in a
record rather than every design statement: "A `README.md` holds no instruction
addressed to an agent and no hard-to-reverse decision of the kind a Decision
Record carries." Explaining how a directory works, including why its design
holds together, is the job the README is for, and moving the settings section
to a record would leave the reader of `dotfiles/` without the one fact that
stops them editing the wrong copy. The alternative, minting a record and
cutting the section to a link, costs a record and a reader's hop for a fact
that is only two paragraphs long.

### `knowledge-organization.entry-shape` — "An entry under `## Language` in a repo's `CONTEXT.md` is the term in bold on its own line, its definition on the lines beneath, and, at most, one final `_Avoid_:` line naming the words retired in the term's favor."

The rule carries a template block as its target state, and the block disagrees
with the live file in two ways. The block writes the term with a trailing
colon:

    **Order**:
    {A one or two sentence description of the term}
    _Avoid_: Purchase, transaction

Every one of the fourteen entries in `CONTEXT.md` omits that colon —
`CONTEXT.md:18` is `**Slop**`, `:26` is `**Audit**`, `:77` is
`**Context file**`. The block also shows entries directly under `## Language`,
while the live file groups them under four H3 headings: `### Legibility`
(`CONTEXT.md:13`), `### Governance` (`:21`), `### Documentation sets` (`:49`),
and `### File roles` (`:60`), each with a one-line or two-line introduction.

The predicate's own sentence is satisfied throughout: every term is bold on its
own line, every definition sits beneath it, and no entry carries more than one
final `_Avoid_:` line.

Proposal. Rewrite the block to match the file, dropping the colon after the
bold term and showing one H3 group. The live grouping is deliberate — it is
what lets the Governance section open with "Five words once swirled around one
idea", which is the entry set's reason for existing — and a detector written
from the block as it stands would report fourteen findings on a file the
predicate accepts. Only the Standard changes; no `CONTEXT.md` is touched.

### `knowledge-organization.tight-definitions` — "An entry's definition in a repo's `CONTEXT.md` is one sentence that says what the term is, and where a concept document defines the term the definition links that document."

Seven of the fourteen entries run to two sentences. The second sentence is
always a consequence or a cross-check, never the definition:

    CONTEXT.md:30  **Lint** — "… the `*-lint` scripts under `scripts/`.
                   Every detector is a lint, and every lint is part of the
                   audit process (lint ⊂ audit), never the reverse."
    CONTEXT.md:34  **Detector** — "… it never mutates the repository.
                   Every detector is deterministic code — a lint."
    CONTEXT.md:41  **Gate** — "… continuously in effect.
                   An audit never blocks; a gate is what blocks."

The same shape appears at `:38` (**Verifier table**), `:65`
(**Concept document**), `:71` (**Procedure**), and `:74` (**Runbook**).

The link half is weaker still. Four entries link a concept document —
**Slop** through the group introduction at `:14`, **Runbook** at `:74`,
**Context file** at `:77`, and **Documentation set** through the group
introduction at `:50`. The rest define terms that a concept document does
define elsewhere and link nothing: **Detector**, **Verifier table**, **Gate**,
and **Enforcement** are all defined in
[Detectors](/standards/standard/detectors.md), which no entry links.

Proposal. Rewrite the predicate to allow the contrast sentence the live
glossary depends on: "An entry's definition in a repo's `CONTEXT.md` opens with
one sentence that says what the term is, and may add at most one sentence that
separates the term from a neighbouring term; where a concept document defines
the term, the definition links that document." The Governance block exists to
pull five words apart, and the second sentence is how each entry names the
word it is not — cutting them would delete the section's whole purpose. The
unlinked entries are a separate, cheaper repair the design pass can take on its
own terms.

## Detectors

**`scripts/ref-lint`** decides three of the family's rules. It walks every
`.md` file `git ls-files` reports, skipping fenced code blocks and inline code
spans, and skipping numbered Decision Records as sources. For each link target
that begins `/` or `~/workspace/`, it records one of four statuses:
`broken` maps to `knowledge-organization.reference-resolves`, `bad-anchor` to
`knowledge-organization.fragment-anchor-matches-the-slug`, `wrong-form` to
`knowledge-organization.link-same-bundle`, and `ok` to nothing. `wrong-form`
fires on exactly one shape, a `~/workspace/<own-repo>/` citation from a file
whose path holds no `skills`, `rules`, or `agents` segment. Targets in any
other form — relative, `~/.claude/…`, or a link split across two lines — are
never examined.

**`scripts/repo-lint`** decides two. `check_doc_shapes` reads the root
`README.md` and emits `knowledge-organization.h1` when no body line outside
frontmatter and fences matches `^# +\S`. It then reads the root `CONTEXT.md`
and emits `knowledge-organization.the-language-section` when the exact line
`## Language` is absent. Neither check looks at any other directory, and
`repo-lint` decides no other rule of this family.

**`scripts/okf-lint`** decides no rule of these three Standards, but it bounds
two of them. Its `knowledge-organization.types` rule forces `CONTEXT.md` to
carry a registered `type`, which stops short of the `Vocabulary` that
`knowledge-organization.vocabulary-type` names, and its
`knowledge-organization.the-listing` and `knowledge-organization.row-shape`
rules force every `index.md` row to be a link, which is what puts
`index.md:13` in conflict with
`knowledge-organization.inline-code-for-a-varying-location`.

**`src/dev_playbook/md.py`** is the shared library the two detectors read the
grammar from. `has_fixed_repo_root` is the one implementation of the
`fixed-repo-root` and `no-fixed-repo-root` conditions: it answers false when
any path segment is `skills`, `rules`, or `agents`. `github_slug` computes the
anchor target, `content_lines` and `lines_outside_fences` define what "outside
a fenced code block" means for the whole family, and `MD_LINK_PATTERN` and
`WORKSPACE_REF_PATTERN` decide what counts as a link and a bare citation.
