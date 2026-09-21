---
type: General-Sheet
title: Doc-Type System
description: The root of the doc-type system strand — the language of doc-types, verbs, and predicates, its principles and terms, and the worklist from the Standard's new shape through the first instance
---

# Doc-Type System

The strand that holds the language: what a doc-type is, its verbs, its
rules as predicates, its encodings as grammar. Speculative, per
[Synthesis Working Root](/working-docs/doc-type-system/ROOT.md).
It defines Loop, one of its three doc-types
([Loop](/working-docs/doc-type-system/loop/ROOT.md)), and each
encoding it writes defines an extractor of the fact base
([Fact Base Strand](/working-docs/doc-type-system/fact-base/ROOT.md)).
The user's own words on the work are kept verbatim in
[Personal Notes](/working-docs/doc-type-system/doc-type-system/personal-notes.md)
for use outside the set.

## Goal

Three DocTypes, ten verbs, in
[Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md),
the picture of the target state;
[Doc-Type Specification](/working-docs/doc-type-system/doc-type-system/specification/doc-type.md)
is the same state as predicates, with one file per doc-type beside it.
The refactor that reaches them, then one loop that grows the
specification.

## Principles

- **Peers first.** Wherever a choice is open, pick the one that keeps
  the three doc-types parallel.
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)
  holds the parallel structure, and each peer has its conventions
  Standard: `harness/runbook-conventions` for Runbook, the
  Meta-Standard under `standard/` for Standard, and
  `knowledge-organization/loop-conventions` for Loop.
- **Verbs.** Each doc-type is defined by a short list of simple verbs,
  its operations. Overlap between doc-types is allowed.
- **Both forms.** A target state is written twice: as a reference
  model, the picture the user thinks in, and as a specification,
  falsifiable predicates that describe the whole set and not one member
  of it, never as a linear description plus actions. The reference
  model is the witness; the predicates are the spec; both are kept.
  Both use the words of
  [Terms](/working-docs/doc-type-system/ROOT.md#terms), one
  meaning each.
- **Predicates are written one way.**
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md)
  is how; it may become the Standard that governs it.
- **Stochasticity is a continuous scale per file.** A markdown file
  with no declared structure sits at one; code sits at zero; a file
  with embedded structure sits between. A file's stochasticity is what
  lies outside its declared structure, which is what
  [the doc-type build loop](/doc-types/doc-type.md#the-doc-type-build-loop)
  already calls the residual. The bedrock of determinism is a
  threshold on content, not a line between file kinds.
- **Shape is orthogonal to stochasticity.** A fully deterministic
  runbook or loop still gets its doc-type document, because the
  document is the legible form. The one requirement that follows is
  a drift check between the document and its substrate, the same
  deterministic rule chaingen applies to a runbook and its chain. The
  loop half is in the Loop strand
  ([Principles](/working-docs/doc-type-system/loop/ROOT.md#principles)).

## Terms

- **DocType** — the base class of
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md):
  a class extends it when its instance is one markdown file of that
  type. `Object`, its earlier name, is retired.
- **Part** — a class nested inside a DocType: an Edge, a Rule, an
  Act, a Check, a Yield. A part has no verbs.

## Open

- **Rule order.** Standard rules are unordered in
  [Population and Rules](/doc-types/standard/contract-shape.md) and in
  file order in the reference model. One must give.
- **The `External` target.** The reference model's `External`
  catch-all target sits against the fact base's total accounting.
- **Whether the fenced pseudocode becomes real Python.**
  [Ontology Solvers](/working-docs/doc-type-system/doc-type-system/ontology-solvers.md)
  proposes the route: a module of dataclasses with no bodies, checked
  by mypy, introspected into an ontology.

## Planned

- **The system.** The refactor toward the reference model and the
  specification. The target shape of one rule, decided 2026-09-20: a heading,
  the predicate, and a trailer line, nothing else. The predicate is
  everything between the heading and the trailer, a list of exemptions
  included when the check needs one, and it is written so that
  deterministic code lifts it verbatim into a judge's prompt, alone or
  concatenated with other stochastic rules for one judge call. A body
  after the trailer is not part of the target: what the 232 bodies
  hold today is enforcement wiring, which step 3 removes, pointers to
  other Standards, which the fact base carries, and exemptions, which
  belong inside the predicate. Reason: text that no verifier reads is
  text the state is not held to, and the split between a checked first
  paragraph and an unchecked body is where the prose and the verifier
  drift apart.
  1. *Standard takes its new shape.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  2. *The verifier table.* Done 2026-09-20; the entry is in
     [Completed](#completed).
  3. *Boundaries: where each check runs.* Done 2026-09-20; the entry is
     in [Completed](#completed).
  4. *Isolate the software factory.* Decided 2026-09-20: the factory
     is out of scope, its future, rewrite or deletion, a later session's;
     it leaves the tree so no step here trips over it again.
     - **A new working set**, `working-docs/software-factory/`, whose
       `ROOT.md` says it is isolated, undecided, and touched by nothing.
     - **Into it:** the ten files of `software-factory/`; the six agents
       `adjudicator`, `bug-pr-review`, `build`, `code-pr-review`,
       `doc-pr-review`, `open-pr`; the eight skills `issue-overwatch`,
       `agent-view-overwatch`, `issue-review-claims`,
       `issue-review-simulation`, `wayfinder-to-build`, `intake`,
       `design`, `user-intent-mini-interview`; the code
       `src/dev_playbook/factory/`, `scripts/traverse-issue`,
       `tests/dev_playbook/factory/`, and the factory-only fixtures in
       `tests/conftest.py`. Links inside the moved files follow them.
     - **Left in place:** the tracking Standard, whose `phase:*` and
       `mode:*` labels bootstrap-labels mints into every governed repo;
       the frozen Decision Records that cite the factory; `wayfinder`,
       `candidate-promote`, and `commit`, which name it in a phrase.
       The links into the factory from `standards/tracking/card.md`,
       `docs/guides/tracking.md`, the root `README.md` and `index.md`,
       `scripts/README.md`, and `CANDIDATES.md` are cut or repointed.
     - **Consequences.** `classify()` keeps a `SKILL.md` or `agents/`
       file harness-owned at any path, so okf-lint stays quiet;
       harness-files-lint walks only the two harness roots, so it stops
       seeing them; `**/tests/**` keeps ruff quiet on the moved tests;
       mypy and pytest stop reading the code; after the next stow the
       moved skills and agents leave `~/.claude`.
  5. *Guide and Explanation.* Decided 2026-09-20. A type is told by the
     kind of information it holds, never by who reads or runs it.
     - **`Guide`, redefined:** instruction on how to do a kind of work,
       read before doing it; organized by the work, citing rules in
       passing; never cited to reject work. Members:
       `harness/writing-for-agents.md`, `build/bootstrap.md`,
       `standard/consuming.md`, `tracking/linking-issues.md`, and
       `docs/headless.md`. A runbook differs in that invoking it does
       the job; a guide is read, and the job is done afterwards.
     - **`Explanation`, new:** the reasoning and mechanism behind one
       Standard's rules, organized rule by rule, at
       `standards/<name>/explanation.md`; never cited to reject work.
       standards-lint admits the file by its type. The twelve
       `docs/guides/<name>.md` become these and `docs/guides/` goes.
     - **Target state leaves the explanations.** A Standard holds
       predicates over state and the target state they compare against;
       an explanation holds neither. The `protect-main` field table
       moves into `tracking/repo-settings.md`, the two frontmatter
       templates into `harness/runbook-conventions.md`, the two trees
       into `build/skeleton.md`, and any predicate found only in an
       explanation into its ruleset.
     - **The other four.** `harness/files.md`: its table is a registry
       `classify()` mirrors, so it becomes a ruleset under `harness/`,
       and its prose joins the harness explanation.
       `knowledge-organization/file-roles.md` dissolves: its terms are
       in `CONTEXT.md`, its table is a paragraph of the
       knowledge-organization explanation. The `docs/` files typed
       `General-Sheet` stay so; no type is made for three files.
     - **Trivial conduct rules are deleted**, not retyped: the red-CI
       rule went 2026-09-20, and any like it found in the explanations,
       a rule no one needs written down, goes the same way.
     - **Open:** where a guide lives, `docs/guides/` or beside the
       Standard it serves, admitted like an explanation.
     Reason: `Guide` held four kinds of information under one name, and
     a name that says how-to kept attracting procedures; the software
     factory's contracts, the fifth kind, are out of scope.
  6. *Retire the card.* Delete the card, `standards/<name>/card.md`,
     and everything that exists only to read it, and bind the one type
     `Standard` to `standards/<name>/<topic>.md`.
     - **Delete.** The thirteen `card.md` files and the type
       `Standard-Card`; the four cells Define, Audit, Enforce, Adopt;
       `scripts/cardgen`, `scripts/rulegen`, and the two `.txt` files
       under `doc-types/standard/`. `rulegen`'s logic is not moved here:
       the `standard` extractor is the fact-base strand's item
       ([Planned](/working-docs/doc-type-system/fact-base/ROOT.md#planned)).
     - **Retype.** `Standard-Ruleset` becomes `Standard` in every
       frontmatter, in Document Types' registry rows, in
       `type-registry.md`'s example, and in
       `doc-types/doc-type-system.md`; okf-lint's
       `typed-standard-card-or-standard-ruleset` becomes the rule for
       the one type.
     - **The description moves.** The directory's `index.md` carries
       the one-line description the card's question sentence carried,
       and the catalog row in `standards/index.md` reads it from there.
     - **`standard/cards.md` becomes the successor Standard**,
       population "a repo's `standards/` tree": one directory per
       Standard at `standards/<name>/<topic>.md`; the directory index
       carries the description; the catalog order; no shadowing of an
       upstream directory name; and the rule shape itself, an H2 with a
       predicate and a `<name>.<slug> · kind` trailer and H3s only under
       a condition, which no Standard states today.
     - **standards-lint shrinks.** Six of its eight rules, the card
       rules, go with the card, and `standard.audit-cites-a-lint` with
       them; `the-hosting-pattern` loses its Audit-cell leg; what
       remains is rewritten against the successor Standard.
     - **A loop's check links a Standard.** Loop Conventions'
       `entries-point-and-condition` says a check links `card.md#audit`;
       it says a Standard file instead, and loop-lint follows. Decided
       2026-09-20.
     - **`standard/consuming.md` is rewritten** as the post-card recipe:
       its steps name cards, Audit cells, Enforce cells, and
       standards-lint's consumer mode. It is a Guide; where a guide
       lives is step 5's open decision.
     - **The vendored spec leaves.** `standards/references/okf-spec.md`,
       the one `type: Reference` file under the tree, and its `index.md`
       move to `docs/references/`, with the citation in
       `knowledge-organization/indexes.md` and the row in
       `standards/index.md`; a vendored upstream spec is material a
       Standard cites, not a Standard.
     - **Consumers.** A consumer repo's cards, story-forge's five, are
       deleted by that repo at its next pin bump.
     Reason: the reference model places every cell elsewhere, Define is
     the Standard file, Audit is the verifier table, Enforce is the
     boundary file, and Adopt was never a primitive
     ([What goes where](/working-docs/doc-type-system/doc-type-system/reference-model.md#what-goes-where)).
  7. *Tidy the doc-type definitions.* The three `contract-shape.md`
     files and `doc-types/doc-type.md` get the pseudocode back, in the
     shape the steps above produce. The user approves every edit here
     before it is committed.
     - **Split the pseudocode back.** It left the three
       `contract-shape.md` files in PR #491 and sits whole in
       [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md#the-language):
       `DocType`, `Target`, and `Finding` go to `doc-type.md`; each
       doc-type's class with its nested parts goes to its own
       `contract-shape.md`; the reference model keeps the toolchain half
       and the fit.
     - **Rename.** `Object` becomes `DocType` everywhere.
     - **`Standard`'s class** is written to the shape steps 1 to 6
       produce: location `standards/<name>/<topic>.md`; frontmatter
       `type`, `title`, `description`, `population`; a `Rule` of id,
       kind, predicate, and condition; no pointer to a script or a gate.
     - **Runbook's two verbs.** `accept` replaces `args` for an input
       edge, and `never write` becomes a `banned` polarity on a write
       edge.
     - **The one-module lint.** A detector concatenates the four fences
       and parses them as one Python module; it is the first verifier
       for the specification's `one-base` and `one-module`.
     Reason: the parts, Edge, Rule, Act, Check, Yield, are not doc-types
     and must not extend the base; every operation on an edge must be
     one of the doc-type's verbs, and `args` was a noun and `never` a
     negation; the lint is what makes the three contract shapes one
     design instead of three.
  8. *The specification becomes a Standard.* Move
     [specification/](/working-docs/doc-type-system/doc-type-system/specification/index.md)
     under `standards/`, bound to no gate. Its shape is discussed with
     the user after the doc-type step; what is known now:
     - **Its predicates are stale.** `standard.md` says every id maps to
       exactly one script or judge and defines `audit(standard, state)`;
       step 2 decided null rows and no `audit()`, and step 3 the derived
       boundary file. Each predicate is rewritten to the built state or
       deleted.
     - **Its ids are three segments**, `doc-type-system.standard.verbs`,
       and the verifier table's lint accepts only `<dir>.<slug>`. They
       become `doc-type-system.<slug>`, unique across the directory.
     - **One rule is added**, `doc-type-system.no-body`, deterministic:
       nothing follows a rule's trailer. It holds on the day it lands
       because step 1 drained the bodies, and it keeps them drained.
     Reason: the first loop's checks point at it, and a loop must not
     bind to a shape a later step deletes.
  9. *Ban the word guard.* prose-lint's banned-word rule, today one
     word, the actor noun, gains `guard`, with a message naming `condition`;
     `prose/conventions.md`'s rule text and `.prose-lint-exempt` follow.
     `generator` and `adopt`, once listed here, are not banned: the only
     reasons on record were one tool's vocabulary and a card cell that
     step 6 deletes, and neither is a reason to ban an English word.
     Decided 2026-09-20. Reason: a habit in the model's weights is
     caught at the commit gate rather than by the user.
  10. *Verify every rule.* Last, and likely the first loop. Every rule
     in every Standard is run against this repo once, and the outcome
     is recorded, never assumed.
     - **By kind.** A rule with an address in the verifier table: by
       running the check, which the green commit gate already does for
       the 103 decided rows. A deterministic rule with a null row, 76
       today: by hand or by an agent reading the population against the
       predicate; where the rule is worth a script, write the checker
       and give the row an address. A stochastic rule, 83 today: by an
       agent reading a sample of members against the predicate; no
       judge tool is built in this plan.
     - **A false predicate** is fixed in this PR where the fix is small,
       or becomes an issue naming the rule id and the failing members.
       Known first: `standard.thin-shims` against the five detectors
       that hold their own logic, `okf-lint`, `repo-lint`,
       `harness-files-lint`, `ref-lint`, and `python-lint`; then the
       four rules the holistic pass wrote or restored,
       `decisions.immutable-after-merge`,
       `knowledge-organization.skill-invocation`,
       `distribution.a-valid-manifest`, and
       `knowledge-organization.mapping-entry-shape`, which no run has
       confirmed.
     - **An undecidable predicate** is rewritten or deleted.
     Reason: step 1's kind tags are aspirational, deterministic meaning
     a script could decide the rule and not that one does; a Standard
     that states what the repo does not do, with no issue that says so,
     is the slop this work exists to remove.

  A step once here, scrubbing every file under `docs/` into a long-term
  home, is dropped 2026-09-20: step 1 sent nothing to `docs/` except
  `docs/guides/`, and the eight loose files there predate this work.
  The one move this plan causes is named at its step, `okf-spec` at
  step 6.
- **First instance.** One loop, `loops/<name>.md`, over the doc-type
  system, after step 8: its checks point at the specification as a
  Standard, and the loop grows it. In iteration order: an act drafts
  candidate predicates, each with its citation or marked invented and
  the members that fail it today; a yield to the user, yes or no per
  predicate; an act applies the accepted ones; a check audits; a yield
  to the user with the diff. A no is kept with its reason, and the
  reason is a candidate predicate itself. The design behind it is
  [Specifying a Loop](/working-docs/doc-type-system/loop/specifying-a-loop.md).
  Whether Loop gains a part for the scalar this loop descends is the
  Loop strand's item
  ([Planned](/working-docs/doc-type-system/loop/ROOT.md#planned)).
- **The `/write-predicates` skill.** A runbook that points at
  [Writing Predicates](/working-docs/doc-type-system/doc-type-system/writing-predicates.md);
  after the guide settles. Also improve writing-predicates.md; it's
  a rough first draft user does not endorse it yet.
- **One clause in System Legibility.** Its sentence that
  documentation is the stochastic thing and code the deterministic
  one is imprecise; one clause says that stochasticity is a scale per
  file ([Principles](/working-docs/doc-type-system/doc-type-system/ROOT.md#principles)).

## Completed

- **One meaning per word, one home per word, 2026-09-15.** Every
  word the four strands use is defined once, in the Terms bucket of
  the set's root where more than one strand uses it and of a strand's
  root where one does, and every other use links to it. Reason: the
  same word carried two senses more than once in this work, guard
  beside condition, evaluator beside verifier, bundle beside
  directory, and each cost a round of correction; a loop reading these
  files cannot ask which sense was meant. The words are in the set's
  [Terms](/working-docs/doc-type-system/ROOT.md#terms).
- **One doc-type for Standard.** Merged into one directory,
  [doc-types/standard/](/doc-types/standard/index.md), with Contract
  defined by the cut in [Doc-Type](/doc-types/doc-type.md). The shape
  it carries there is the one the refactor replaces with
  [Reference Model](/working-docs/doc-type-system/doc-type-system/reference-model.md)'s.

- **Standard takes its new shape, 2026-09-20.** Step 1 of The system.
  Every rule in the 25 drained rulesets is a heading, a predicate, and
  a trailer `` `<name>.<slug>` · deterministic|stochastic ``, 251 rules
  in all, drained one ruleset at a time by the
  [Body Drain](/working-docs/doc-type-system/doc-type-system/body-drain.md)
  rubric; `standard/cards.md` stayed undrained for the card step, and
  `standard/gates.md` for the boundary step, which retired it. Teaching the drains displaced is a guide at
  `docs/guides/<name>.md`, twelve in all, one per Standard directory.
  The closing pass drew the verifier and boundary tables by hand,
  read the rulesets across each other, and left its findings and
  every deferral in a worksheet, Verifiers and Boundaries, each
  deferral also named at the step that owns it; the worksheet was
  deleted at the boundary step once both tables were real. Reason: a loop
  cannot route a rule without an id and a kind, and text no verifier
  reads is text the state is not held to.
- **The verifier table, 2026-09-20.** Step 2 of The system. The table
  is `standards/verifiers.yaml`, one row per rule id declared under
  `standards/`, mapped to the address of the one check that decides it
  or null: a first-party detector by path, `scripts/repo-lint`; a
  dependency by its pre-commit hook id, `ruff-format`, `ruff-check`,
  `shellcheck`, `shfmt`; or a dependency by its `pyproject.toml` name
  and subcommand, `mypy`, `pre-commit validate-manifest`, since those
  two run outside pre-commit. `scripts/verifier-table`
  (`src/dev_playbook/verifier_table.py`) derives it from the rule
  trailers, each detector's `--list-rules`, and a six-entry dependency
  map, writes it with `--write`, and is the lint otherwise; it sits in
  the playbook-lint roster, so the commit gate regenerates and compares
  on every commit. It fails loud in four ways, each a rule of the
  rewritten `standard/detectors.md`: `the-verifier-table` when the
  committed file differs from a fresh write; `an-emitted-id-is-a-rule-heading`
  when a check claims an id no heading declares deterministic, or two
  checks claim one id; `an-address-exists` when a dependency address
  is no hook id and no dependency of the repo; and
  `a-consumer-adds-only-its-own-rules` when a repo other than
  dev-playbook declares an id the shipped table carries. A trailer that
  disagrees with its heading, has none, or repeats an id is exit 2. In
  a consumer the checks asked are its own `scripts/` hooks, and its
  table holds only its rules; the union is read from the pinned clone.
  At first write the table has 262 rows: 103 decided, 83 stochastic
  null, and 76 deterministic null, the rules no script has ever
  checked, which stay unchecked. All eleven detectors emit rule-heading
  ids, with splits and merges as the step-1 worksheet's corrected
  Emitted ids table listed, before the boundary step deleted it; six rules the step-1 read overclaimed are null
  (`an-act-links-a-runbook`, `harness.tool-fields`, `row-description`,
  `resource`, `ticket-parentage`, `epic-headings`). The four decisions:
  `prose.the-banned-word` is a deterministic rule of
  `prose/conventions.md`, its three naming files exempt through
  `.prose-lint-exempt`; `doc-shape` split into `h1` and
  `the-language-section`; `no-blocked-label` retired into
  `valid-labels`; `registry-location` kept under `local-declaration`.
  `standard/cards.md` got trailers so standards-lint's six card rules
  are headings (`directory-layout`, `define-points-only-at-rulesets`,
  `the-question-sentence`, `the-directorys-introduction`,
  `the-catalog`, `no-shadowing`); `audit-cites-a-lint` is null;
  `rule-matrix` and `card-namespaced-rule-ids` are deleted. No
  `audit()` function exists; a judge, when one is built, reads the
  table. Reason: the table is the one place the Standard files and the
  checks meet, and a generator that fails cannot drift from either.
- **Boundaries: where each check runs, 2026-09-20.** Step 3 of The
  system. The file is `standards/boundaries.yaml`, one row per address
  the verifier table names, valued by the gates that run it in order
  from `commit`, `push`, `ci`, `on-demand`: at first write nineteen rows,
  sixteen at all three gates, `scripts/ref-lint` at `[commit, push]`,
  `mypy` at `[push]`, `scripts/workspace-lint` at `[on-demand]`.
  `scripts/boundary-table` (`src/dev_playbook/boundary_table.py`)
  derives it from the wiring, never from prose: each hook of
  `.pre-commit-config.yaml` by its stages, `playbook-lint` expanded to
  its roster and the manifest check, the pre-push hook's `make check`
  read through `make -n`, each workflow's `run` steps under their
  `SKIP`, and playbook-lint's `UNGATED_AUDITS` for `on-demand`. It
  writes with `--write`, is the lint otherwise, and sits in the
  playbook-lint roster. Its two rules are in `standard/detectors.md`:
  `standard.the-boundary-table`, the committed file equals a fresh
  write; and `standard.every-address-runs-somewhere`, every address is
  at a gate or registered ungated, and no registered audit is at a
  gate. The second is the closure leg standards-lint's hosting rule
  carried, which left standards-lint with its two tests; the verifier
  table gained the two rows. `standard/gates.md` is deleted: its three
  rungs are the file's columns, defined in the boundary rule; its
  installed-in-every-clone fact was already bootstrap's step 4; its
  skips rule and the teaching about where a check runs are two sections
  of `docs/guides/standard.md`; its red CI rule is deleted, a thing
  nobody needs written down; the per-machine skips stay in
  `docs/machines.md`. Its readers repointed:
  `doc-types/standard/encoding.md`, `contract-shape.md`,
  `residual-ledger.md` (its gates entry deleted), `docs/guides/tracking.md`,
  `docs/machines.md`, `standard/consuming.md`, `card.md`, `index.md`,
  `detectors.md`, and the comments in `playbook_lint.py` and
  `standards_lint.py`; the Meta-Standard's description now ends "and
  the boundaries", in the card, its index, and the catalog. The
  canonical `ci.yml` and dev-playbook's own now read `SKIP: ref-lint`:
  `web-typecheck` is a hook only dev-playbook has, so its name leaves
  the file every governed repo copies, and dev-playbook's own CI now
  runs it. The step-1 worksheet, Verifiers and Boundaries, is deleted;
  every deferral it held was already named at its step. Reason: which
  gate runs a check is wiring, and a file derived from the wiring
  cannot lie about it.

## Acronyms

- **CI** — Continuous Integration.
- **PR** — Pull Request.
