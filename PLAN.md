---
type: Plan
title: Pocock Sweep 2026-08 — Bootstrap Plan
description: Working plan for the bootstrap run of /pocock-sweep — how the branch is worked, the ten stages with their briefs and outcomes, and the ruled verdicts at v1.2.3
---

# Pocock Sweep 2026-08 — Bootstrap Plan

`mattpocock/skills` moved from the workspace's last evaluated pin
(`2ab958093e83e0ec752e6c1c5932da465bf23e0c`, 41 skills, six tiers) to release
**v1.2.3** (`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, 35 skills, four
tiers). This branch is the bootstrap run of a repeatable procedure —
`/pocock-sweep` — that dockets only the deltas against standing verdicts,
escalates rulings to the user, and lands the results in one PR. The skill
itself is written at the end of this branch, from what actually worked, via
/skill-creator.

Working state for the `worktree-pocock-sweep` branch. A fresh agent picking up
this branch reads this file first. Everything lands atomically in this branch
and ships as one PR. **This file is deleted before merge** — at stage 7, after
DR 0020 has taken what it needs from the completed stages, which is why a done
stage keeps both its brief and its outcome.

## Operating procedure

Set by the user, 2026-08-07.

This file is a doubly-compacted, lossy record of two long sessions. Its
epistemic status is split: **Rulings below are ruled and trusted** — which
skills install verbatim, which adapt, which reject. Every stage brief is
**guidance to re-verify**. Decisions may also exist that neither the user nor
this file remembers; surfacing such candidates is part of each stage's fresh
look.

- **One stage per context window.** Expect a compact or fresh start between
  stages; this file is the handoff. A stage ends by recording its outcome in
  its own section below, inside that stage's own commit.
- **Interpretive stages (2–4) open with fresh-look-and-align.** Read the
  installed bundles and the workspace docs as they actually are, put the
  stage's proposed edit list to the user in chat, write the agreed list into
  this file, then execute. Mechanical stages move faster, but the user still
  reviews record text (the ledger, the DR) before it lands.
- **Commit and push after every stage — but only after the user has approved
  that stage's diffs in chat.** The user is in the loop on every stage: show
  the diffs, get the approval, then commit. Push with `--no-verify` — that
  skips only the pre-push judgment gate; the commit-gate lints always run.
- **Judgments run exactly once, at stage 9 — never earlier, never as a side
  effect of a push.** (On 2026-08-07 the two re-keyed judgments were
  accidentally run once — both passed; the verdicts were discarded
  unrecorded.)

## Stages

Each stage carries its own brief and, once done, its outcome. A brief is
guidance to re-verify, never a script to execute blind.

| Stage | Status |
|---|---|
| 1. Installs | **Done** — `7115b70` |
| 2. Deferrals | **Done** — `aecb3b1` |
| 3. Standards edits | **Done** — `2971ff6` |
| 4. Lint split | **Done** — `a7e32c1` |
| 5. Records | **Done** — `2585ebd` |
| 6. Gates | **Done** — `2585ebd` |
| 7. Audit | Not started |
| 8. Write `/pocock-sweep` | Not started |
| 9. Judgments | Not started — the only permitted run |
| 10. PR | Not started |

### 1. Installs — done (`7115b70`)

**Brief.** Vendor six new bundles + three changed bundles; lock entries;
mirror symlinks. (`research`, `domain-modeling` lock entries should come back
unchanged.) Mechanics in [Install mechanics](#install-mechanics).

**Outcome.** Nine bundles vendored byte-identical; committed folder tree SHAs
equal their lock entries; six mirror symlinks; the lock-hash algorithm was
validated against the byte-identical `research`/`domain-modeling` entries
before any hash was written. Landed early out of stage 3 because the commit
gate forced it: `shellcheck`/`shfmt` `exclude: ^dotfiles/\.agents/` in
`.pre-commit-config.yaml`, after shfmt rewrote two vendored scripts on the
first commit attempt (upstream bytes restored and re-verified). The prose
half — the shell standard's vendored-scripts exemption — still lands in
stage 3.

### 2. Deferrals — done (`aecb3b1`)

**Brief, as ruled before execution.** Content yields to an installed skill
under principle 4; fix every inbound reference (ref-lint hunts danglers).

| File | Action | Why |
|---|---|---|
| `standards/modules/design.md` | Gut to a thin pointer at `/codebase-design` | Near-pure mirror: all four principles, both diagrams, the three testability rules with his TypeScript examples. Any residue the skill doesn't carry survives as a stated workspace delta (verify at landing; likely none). |
| `CONTEXT.md` § Architecture | Trim to a pointer at `/codebase-design` | The eight terms, the five upstream relationship bullets, the rejected framings, and worked dialogue 1 are his, two entries character-for-character. **Kept:** the flagged-ambiguities log (workspace decision history, not a restatement) and all workspace-native sections (Governance, Machines, Tracking) and their relationships. Also makes `CONTEXT.md` conformant to the installed `domain-modeling` format rule: project-specific concepts only. |
| `standards/claude-code/skill-writing.md` | **Delete** | Superseded by installed `writing-for-agents`. Its overrides all already live as binding rules in `skill-conventions.md`; a delta file would restate them. Surviving workspace-original lines (e.g. "a failing test is fixed, never edited to pass") fold into `skill-conventions.md`. |
| `standards/claude-code/skill-glossary.md` | **Delete** | Its upstream source (`GLOSSARY.md`) no longer exists; definitions now live inline in the installed skill. Load-bearing originals fold into `skill-conventions.md`. |
| `dotfiles/dot-claude/skills/design/references/design-it-twice.md` | Remove its internal-seams passage | Duplicates the installed `codebase-design` bundle, which carries the internal/external-seam material verbatim. The rest of the file is a genuine adaptation (Opus pinning, worktrees, §6 synthesis diet) and stays authored, watched for creep at every sweep. |

**Outcome — what the fresh look changed.**

- `standards/modules/design.md` **deleted outright** (user ruling, overriding
  the brief's "gut to a thin pointer"). Verified a pure mirror first: all four
  principles, both diagrams, and the three testability rules with their
  TypeScript examples are in the installed bundle; nothing workspace-original
  survived. A redirect file was drafted and then rejected on the format
  standard's own terms — a card exists so a lookup "resolves to concrete files
  in one hop", and a second file naming the same question and pointing at the
  same answer makes it two. **`standards/modules.md` keeps the concern in the
  catalog and its Define cell now cites the installed bundle directly**,
  matching what `standards/claude-code.md` does for `writing-for-agents`. The
  `standards/modules/` directory is gone.
- Six call sites re-pointed at `/codebase-design`: `design/SKILL.md` and
  `wayfinder-to-build/SKILL.md` (each `Read first` list now mixes reads with an
  invoke, and its `READ:` report line names `codebase-design`),
  `code-pr-review/SKILL.md` (the source-type table and the Module design
  dimension), `design-it-twice.md`, and `testing/conventions.md`.
- `CONTEXT.md § Architecture` **cut further than the brief said.** The brief
  kept the flagged-ambiguities log; the fresh look found all four architecture
  entries (boundary, component/service/unit, depth-as-ratio, narrow-interface)
  restate the skill's own `_Avoid_` lines and Rejected framings, so principle 4
  takes them. Also removed: the eight term definitions (replaced by a four-line
  pointer stub), the five architecture Relationship bullets, the Postgres/fake
  dialogue, and the whole `## Rejected framings` section (all three entries
  were upstream's, and the section is optional per `context-content.md`). The
  four repo-lint-required sections all survive on workspace-native content.
- `standards/claude-code/{skill-writing,skill-glossary}.md` **deleted** (619
  lines), with **nothing folded forward**. The brief named one surviving
  workspace-original — "a failing test is fixed, never edited to pass" — and
  that is a **plan correction**: the rule is not original, it restates
  `build/references/tdd.md:30` ("**Never modify a written test.**"), which
  states it in the skill that actually runs tests. The generalized copy in a
  format standard was duplication with no bite; retired deliberately, not lost.
  The nearest live analogue, `run-judgments/SKILL.md:90`, shows the workspace
  pattern: state the rule locally in the skill whose step is gated on a check.
  Every other line of both files maps to the installed bundle; the glossary's
  `_Avoid_` lines were dropped as unenforced. **Record this correction in DR
  0020.**
- `skill-conventions.md` **gained the craft pointer and the precedence
  sentence** (a stage-3 row, pulled forward): deleting the advisory layer
  without landing its inverse would have left the collision unresolved for a
  whole stage. The split description rule stays in stage 4 with `skill-lint`.
- `design-it-twice.md` **carries no internal-seams passage — that half of the
  deferral row is confirmed a no-op.** Its one edit is the call-site re-point
  above. **Record this correction in DR 0020.**
- Reference repair (ref-lint would have blocked): `skill-creator/SKILL.md`
  step 1 now reads conventions and *invokes* `/writing-for-agents` (the other
  stage-3 row, discharged); `doc-pr-review` skills row re-pointed;
  `node-skill-authoring.md` re-pointed twice, including the `#pruning` anchor,
  which now resolves into the installed bundle; `standard/format.md`'s
  gerund-compound example swapped to a file that still exists.
- Cards and indexes: `standards/claude-code.md` Define now names the installed
  bundle by path with the precedence clause; `standards/modules.md` Define
  drops its `CONTEXT.md` bullet; both `standard-cards.yaml` judgments re-keyed
  (`standard-card-claude-code`, `standard-card-modules`) — they run at stage 9.

**Architecture this leaves behind:** **craft** = `/writing-for-agents`
(installed) · **format** = `skill-conventions.md` (binding,
workspace-original, wins on collision) · **workflow** = `/skill-creator`
(step 1 rewired to read conventions + invoke `/writing-for-agents`).

### 3. Standards edits — done (`2971ff6`)

**Brief, as ruled after the fresh look.** The question this stage answers: where
do the workspace's own policies, procedures, and standards now fail to fit the
eleven installed bundles? Six edits.

| File | Edit |
|---|---|
| `standards/shell/conventions.md` | Vendored-shell exemption prose — all four rules yield for shell under an `.agents/` path, mirroring the prose standard's existing exemption paragraph and naming `external.py` as the root registry. The mechanical half landed in stage 1 as the `.pre-commit-config.yaml` excludes, whose comment currently points at this file, which says nothing. |
| `standards/tracking/issue-authoring.md` + `design/SKILL.md` | Prototype run-outputs widened for `prototype`'s new logic branch (double-click HTML demo, no stdout): "for a click-driven demo, the observed states captured as text or screenshots." `design/SKILL.md:63` restates the standard's three-item list and goes stale with it — the restatement is dropped for a citation, since the skill's Read-first already reads the standard end-to-end. |
| `software-factory/refactor-catalogue.md` + `code-pr-review/SKILL.md` | Fowler 12-smell baseline (explicit ruling; see the `code-review` verdict row). **Landing site ruled after the fresh look:** the catalogue already carries three of the twelve in its own words, so the nine missing smells merge into its one `## The candidates` list — no new section, no second catalogue — and `code-pr-review` gains a dimension citing it. The catalogue stays a list of cues and moves and says nothing about who reads it; the two binding rules (a standard overrides the catalogue, every hit a judgment call and never Blocking) live only in the review dimension, where blocking severity is decided. The build node gains nine refactor candidates; accepted. |
| `dotfiles/dot-claude/skills/wayfinder-to-build/SKILL.md` | Slicing interview: `one question at a time` (the only such site in the repo) → invoke `/grilling`, whose v1.2.3 bump replaced that phrasing with round-by-round frontier questioning. Bare `/grilling`, not `/grill-with-docs` — slicing needs no ADR or `CONTEXT.md` translation. |
| `standards/standard/format.md` + `.pre-commit-config.yaml` | Stage 1 breached the meta-standard: format.md names **ruff** as "the one exception" to the import-the-registry rule, and requires such a detector's comment to name `external.py` as the authority. Stage 1 added shellcheck and shfmt, commented at the shell standard. Generalize the exception; repoint both comments. |
| `standards/modules.md` | Adopt cell (`none`) → `improve-codebase-architecture`: the card's Adopt cell is for migration procedures, and that is exactly what the skill is for this standard. Re-keys `standard-card-modules` again. |
| ~~`dotfiles/dot-claude/skills/skill-creator/SKILL.md`~~ | **Discharged in stage 2** — step 1 reads conventions and invokes `/writing-for-agents`. |
| ~~`standards/claude-code/index.md`, `standards/claude-code.md` card~~ | **Discharged in stage 2** — retired files removed, cells re-pointed. |

**Declined at this stage** (user rulings, recorded so no later stage re-finds
them):

- **The `docs/adr/` translation stays homeless.** Three installed bundles name
  ADRs; the only translation lives in `grill-with-docs`, which two of them never
  load. Proposed fix was a rule in the global `CLAUDE.md`. **Declined** — an
  agent that finds no `docs/adr/` will reach `docs/decisions/` on its own, and
  that is cheaper than a standing global rule.
- **No shell carve-out for a generated wizard.** Upstream's step 4 tells the
  agent to commit a repeatable wizard, which would be authored shell breaching
  the glue-only boundary. **Declined** — `wizard` is installed as a curiosity
  and is not expected to run; the vendored exemption is all the standard needs.
- **`build/references/tdd.md` is not fenced against `diagnosing-bugs`.** Its
  phase 5 lets a missing regression-test seam be a finding rather than an
  escalation, which the build node's TDD does not allow. **Declined** — same
  reason: the skill is a curiosity, TDD is used constantly, and the workspace's
  procedure is not complicated to guard a case that may never arise.

**Outcome — what the fresh look and the review changed.**

- All six edits landed as briefed. Scope: 13 files, +95/−21 before the
  catalogue trim below; 11 commit-gate detectors clean throughout.
- **The Fowler merge stayed a merge.** Nine smells joined
  `refactor-catalogue.md`'s one `## The candidates` list, compressed into its
  `*Cue:* / *Move:*` shape rather than pasted from upstream — principle 2
  forbids mining upstream prose, and the user's exception licensed the
  *baseline*, not the text. `code-pr-review` gained a `Structural smells`
  dimension and a source-in-any-language row in its §2 read table.
- **The catalogue names no reader.** A first draft had it announce its two
  callers in the H1 blurb and the frontmatter description; the user cut that —
  a document states what it is and what it instructs, never who invokes it.
  Note the pre-sweep description already named one ("the refactor candidates
  **a build node** looks for"); that is gone too.
- **Two sections were deleted from `refactor-catalogue.md` on user ruling**,
  each after the same test — *what is the point of this?*
  - A drafted `## Flagged rather than fixed` carrying the ruling's two binding
    rules. Cut: it duplicated the review dimension that also states them, and
    "a documented standard overrides the catalogue" is a no-op in a workspace
    where a Standard already outranks a Guide. Both rules now live **only** in
    `code-pr-review`'s dimension, where blocking severity is decided.
  - The pre-existing `## The two scopes`. Cut: `build/references/tdd.md` is the
    file's only caller and already states both scopes, their reach, and the
    `make test` cadence; its closing paragraph pointed at an escalation trigger
    stated in `tdd.md:63` and actionable nowhere else. The one thing it did
    carry — which candidates suit which reach — moved into `tdd.md`'s two
    refactor passes, and `tdd.md` no longer says "slice-scope candidates" of a
    catalogue that never labelled them. **This cut sits outside principle 1**
    (upstream speaks on the smell baseline, not on refactor scopes); the user
    ruled it rides this branch anyway. **Record in DR 0020.**
- The catalogue ends as step size, then the candidates, then the testing
  pointer — 15 candidates, one shape, no meta-commentary.

The user asked to pause after this stage for review.

### 4. Lint split — done (`a7e32c1`)

**Brief, as ruled after the fresh look.** Principle 9's split, landed in four
places.

| File | Edit |
|---|---|
| `scripts/skill-lint` | `check_description` branches on `disable-model-invocation`: the expected sentence count is 1 when it is literally `true` and 2 otherwise, and the `Use when` rule is asked only of the latter. `is True`, not truthiness, so a missing or non-boolean field falls to the model-invoked path. |
| `standards/claude-code/skill-conventions.md` | The `description` required-fields row, the checklist item, and the naming-conventions example carry the split. The precedence paragraph's collision list narrows to "the model-invoked description form" — the user-invoked form now follows upstream. Its other stage-3 obligations are closed: the precedence sentence landed in stage 2, the craft-line fold turned out to be a no-op, and the always-explicit + dispatcher fact is already in the required-fields table. |
| `tests/test_skill_lint.py` | **Added to the brief at landing** — the stage changes a lint's behavior. `valid_skill()` flips to `disable-model-invocation: false`; the test asserting the old no-carve-out policy by name is replaced by four: the trigger rule on a model-invoked skill, a one-sentence user-invoked description passing, a two-sentence one blocking, and a malformed invocation field falling to the model-invoked path. |
| 15 user-invoked authored skills | Second sentence dropped. Every first sentence was already a single terminated sentence, so all fifteen are pure deletions. |

**Outcome.**

- Landed as briefed. 19 files; 11 commit-gate detectors clean; 46 tests pass.
- **Upstream was checked before the shape was fixed**, on the user's challenge
  that a verbatim-installed skill might already rule on this.
  `writing-for-agents/SKILL-MECHANICS.md` states both halves — model-invoked
  gets "a model-facing description carrying the trigger branches", user-invoked
  gets "a one-line summary, trigger lists stripped" — and his own bundles bear
  it out: the model-invoked ones carry two-sentence `Use when`, the three
  user-invoked ones (`wayfinder`, `improve-codebase-architecture`,
  `wait-what`) are one-liners. Principle 9 read him correctly.
- **Both branches are enforced; neither is a carve-out.** The user-invoked
  rule is exactly one sentence, ruled by the user after a first pass left the
  shape unchecked. The one cost, accepted: upstream's own `wait-what`
  description (`Stop. That last message did not land — re-pitch it.`) is one
  line but two sentences and would fail this rule. It never meets it —
  skill-lint skips externally-managed bundles — but an authored skill wanting
  that shape has to fold the two clauses into one sentence.
- **This stage overturns a decision the workspace had argued for explicitly.**
  Three sites stated the old no-carve-out rule in as many words —
  `skill-conventions.md`'s "binding every authored skill — no exemption",
  `skill-lint`'s "one rule and one lint path", and a test named
  `test_trigger_rule_binds_user_only_skills`. All three are rewritten.
  **Record in DR 0020.**
- **Two defects fixed in `skill-lint`, found on a fresh read of the whole
  file.** An unterminated front matter reported `claude-code.parse substring
  not found` — `str(IndexError)` leaking through the broad `except Exception`;
  `parse_skill` now raises a `ValueError` naming the missing delimiter. And a
  directory under a skill root with no `SKILL.md` was audited as nothing while
  still counting toward the summary's skill total; it now raises `ToolError`
  (exit 2), on the user's ruling that a missing bundle is an exception and that
  no summary may ever print a count the scan did not cover. An abort now prints
  the findings it had already collected rather than discarding them. Both have
  tests. One existing test was corrected rather than accommodated: its "authored
  skill" colliding with an externally-managed name was an empty directory, and
  a real authored skill has a `SKILL.md`.
- **One unrelated bug fixed in the same file.** The closed-vocabulary section's
  `user-invocable` bullet was inverted — it said to use
  `disable-model-invocation: true` when a skill "should not be user-invoked",
  which is what that field does the opposite of. Rewritten, and its trailing
  "rely on the skill's description to communicate its purpose" clause dropped,
  since under the split that description reaches no model.

### 5. Records — done (`2585ebd`)

**Brief.**

| File | Edit |
|---|---|
| `docs/external-skill-verdicts.md` | The ledger stays general across upstreams (pre-compact decision); this sweep touches only its `§ mattpocock/skills` section — updated to the new pin (35 skills / 4 tiers, every row per the verdict tables below; deleted-skill rows retire) — plus two general-rules edits that apply to every upstream: verdict vocabulary tightened per principle 2, supersede rule added. The `marimo-team/skills` and `pymc-labs/pymc-modeling` sections are untouched. |
| `docs/decisions/0020-pocock-skills-sweep-2026-08.md` (+ index) | Thin DR: this sweep's rulings and reversals (codebase-design, diagnosing-bugs, wizard, to-questionnaire reopen/re-reject, writing-for-agents, to-spec/to-tickets reject with reevaluate markers, resolving-merge-conflicts fresh reason, tdd fresh reasons); the minted principles (2, 3, 4, 9); the harvest-style-adapt relabels; both 0016 dangling fragments closed (12-smell lands, small-step retired); the recorded declines; and the two stage-2 plan corrections. |
| `standards/tracking/tracker-operations.md` | Upstream-seed pin string → `6acc160` (content verified still accurate). |

**Outcome.**

- **The v1.2.3 clone was gone** with the earlier session's scratchpad and was
  re-cloned; HEAD re-verified as `6acc160e…`. All 35 skills counted against the
  pin directly: engineering 18, productivity 7, in-progress 6, misc 4. One
  refinement — `deprecated/` still exists upstream but holds only a README, so
  it is the *skills* that are gone, not the directory; `personal/` is gone
  outright.
- **The tracker-operations pin bump was earned, not asserted.** The plan said
  "content verified still accurate"; the actual delta-check found two additions
  in upstream's `issue-tracker-github.md` at v1.2.3 — the frontier query now
  drops blocked and already-claimed tickets, and Resolve appends a context
  pointer to the map's Decisions-so-far. Both are *method*, and the workspace
  file scopes itself to tracker moves and cedes method to the skill ("The skill
  owns the method; the moves it makes on the tracker are these") — and
  `/wayfinder` is installed verbatim at this pin, so it carries them. No content
  edit. The pin now names the release tag as well as the SHA, per principle 7.
- **A third general-rules edit was needed.** The plan named two (vocabulary,
  supersede rule). The tier-policy section also endorsed harvesting ideas out of
  unpromoted skills — the practice principle 2 retires — and now says 0016
  allowed that and no longer does.
- The ledger's `§ mattpocock/skills` is rewritten to 35 rows across four tiers;
  seven deleted skills retire into a closing paragraph rather than staying as
  rows. `marimo-team/skills` and `pymc-labs/pymc-modeling` untouched.
- DR 0020 written as a **delta record**: what moved and why, with the ledger
  named as the place to ask where a skill stands today. It carries the four
  minted principles, the vocabulary change with its reason, both 0016 fragments
  closed, five declines, the two plan corrections, and the one cut outside
  principle 1.

### 6. Gates — done (`2585ebd`)

**Brief.** Full commit-gate suite (`skill-lint`, `ref-lint`, `okf-lint`,
`prose-lint`, the rest via `make check` equivalents). Judgments are NOT run
here — they wait for stage 9.

**Outcome.** `make check` green end to end: `ruff format --check` (83 files),
`ruff check`, `mypy` (82 source files, no issues), `pytest` — **909 passed, 31
skipped** — and `pre-commit run --all-files` across all five hooks. shellcheck
and shfmt both **ran and passed** rather than being skipped, which is the live
proof that stage 1's `exclude: ^dotfiles/\.agents/` holds over the nine
vendored bundles. `playbook-lint`'s 11 detectors clean, 578 references
resolved, 97 concept docs and 15 indexes consistent. No judgment was run.

### 7. Audit — not started

Adversarial pass: mirror rule clean; no authored/installed name collisions;
every call site of the five bumped skills still true; supersede-rule
duplication scan (`CONTEXT.md`, standards vs. all eleven installed bundles),
checked against [Adaptations that stay authored](#adaptations-that-stay-authored);
no dangling references to retired files; ledger internally consistent with the
DR. Delete this file.

### 8. Write `/pocock-sweep` — not started

Via /skill-creator, codifying: resolve latest tag → clone → diff against
ledger → docket only deltas (verdict flips, tier moves, new/deleted skills,
expired reasons, supersede-rule duplication check), every delta its own item
with a recommendation → user rules item by item (agent reports are leads,
never rulings) → whole-skill verdicts only: verbatim / adapt-minimal /
reject, no fragment mining → land atomically in a worktree branch → audit →
ledger + thin DR → PR ending in a habit brief. Settled frontmatter:
user-invoked only, `model: inherit`, `effort: xhigh`, no arguments, no
references dir, no scripts.

### 9. Judgments — not started

The one and only judgments run, via the `/run-judgments` loop: everything the
sweep re-keyed (the two wayfinder judgments — both passed the discarded
2026-08-07 run, so identical verdicts are expected — plus the two
`standard-cards.yaml` judgments stage 2 re-keyed, plus whatever the standards
edits re-key). Record the verdicts; the push gate goes green here.

### 10. PR — not started

One PR from this branch; body carries the change inventory and the **habit
brief**: what changes for an operator who knew the prior state (grilling now
lands in rounds — answer by number; logic prototypes arrive as double-click
HTML demos with walkthrough tabs; `/improve-codebase-architecture` and
`/diagnosing-bugs` now exist and when to reach for them; `/writing-for-agents`
replaces the two retired standards files when authoring skills; `/wizard` for
click-through procedures; `/wait-what` to force a re-pitch; architecture
vocabulary now lives behind `/codebase-design`, not `CONTEXT.md`).

## Principles

Minted or reaffirmed this sweep. These govern every stage's judgment, and
stage 8 encodes them into the skill.

1. **Direction rule.** The sweep walks from the upstream package into the
   workspace standards, never the reverse. Workspace material enters scope
   only where the upstream package currently speaks on its subject.
2. **Skills are the unit of decision** (minted this sweep, by user
   correction). A sweep rules on whole skills: install verbatim, install
   with the minimal adaptation required to fit existing workspace
   constraints, or reject. Upstream prose is never mined for wisdom
   fragments to fold into workspace standards; an idea inside a rejected
   skill is rejected with it, reevaluated only when the skill is.
3. **Decisions come from the user** (minted this sweep, by user
   correction). Every delta is its own docket item carrying a
   recommendation; an agent report is a lead, never a ruling; a recap
   clause is not a docket. "Standing" labels only a row whose verdict and
   delivered artifact are both unchanged from the ledger.
4. **Supersede rule** (minted this sweep). Verbatim-equivalent workspace
   content yields to an installed skill — a definition an installed skill
   states when invoked is not also stated in `CONTEXT.md` or a standard.
   Genuine adaptations (workspace machinery built around an adopted
   technique) stay authored. Every sweep runs a duplication check against
   this rule.
5. **Tier policy** (0016, reaffirmed). Nothing is installed from a tier the
   author has not promoted. A promotion voids a tier-based reject and
   reopens the row as unruled — exercised this sweep by `wizard` and
   `to-questionnaire`.
6. **Atomicity.** Installs, standards edits, accommodation work, ledger,
   and Decision Record land in one branch, one PR. No follow-up issues.
7. **Pins.** Sweeps evaluate release tags, never `main`. The ledger
   (`docs/external-skill-verdicts.md`) is the current-state record; each
   sweep appends one thin Decision Record with that sweep's rulings.
8. **In-place, never additive.** An accommodation edit upgrades the
   existing section or declines with a recorded reason — never a parallel
   "how upstream says it" section beside a legacy one.
9. **Description rule, split** (this sweep). Model-invoked skills keep the
   binding two-sentence `Use when` description — it is the lintable form of
   upstream's own trigger-branch advice, gating the auto-invocation
   surface. User-invoked skills adopt upstream's one-line human-facing
   description; no model ever reads them. `skill-lint` branches on
   `disable-model-invocation`.
10. **`disable-model-invocation` stays always-explicit.** Not style: the
    factory dispatcher's slash commands arrive as agent text input and count
    as model invocation, so a factory-dispatched skill must remain
    model-invocable. Upstream's "could the model reach for it?" test would
    set the field wrong here. The rule guards a workspace fact upstream has
    no view on.

## Rulings

The trusted layer. These are the user's decisions — read them, do not
re-derive them.

### Upstream state at v1.2.3

- Tag `v1.2.3` → commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`.
- 35 skills across four tiers (engineering 18, productivity 7,
  in-progress 6, misc 4). The `deprecated` and `personal` tiers are gone.
- Deleted since our pin: `design-an-interface`, `qa`,
  `request-refactor-plan`, `ubiquitous-language`, `edit-article`,
  `obsidian-vault`, `batch-grill-me`.
- Renamed: `writing-great-skills` → `writing-for-agents` (restructured;
  its `GLOSSARY.md` merged into `SKILL.md`; mechanics split to
  `SKILL-MECHANICS.md`; now model-invoked).
- Promoted: `wizard` (in-progress → engineering, now model-invoked),
  `to-questionnaire` (in-progress → productivity).
- Added: `wait-what`.
- The plugin ships engineering + productivity only; in-progress and misc
  are a skills-CLI-only channel.

### Per-skill verdicts

**Verdict vocabulary:** verbatim (installed unmodified, lock-tracked) ·
adapt (adopted, with the minimal named modification that fits it to
workspace constraints) · reject (not adopted; reason recorded). "New" marks
a ruling the user made or changed this sweep. Rows marked **relabeled**
carried 0016's old harvest-style "adapt" — a vocabulary principle 2 retires;
material those old verdicts already landed stays where it landed, but the
skills themselves are not adopted.

#### Engineering

| Skill | Verdict | Reason |
|---|---|---|
| ask-matt | reject | Standing. A hand-maintained prose router competes with the factory graph. **New this sweep:** the proposal to harvest its `PHASE-BOUNDARIES.md` decision tree was declined — "continue declining ask-matt." |
| codebase-design | **verbatim — new** (was adapt) | Dependency of `improve-codebase-architecture`; the architecture vocabulary's single home under the supersede rule. Reverses 0016's adapt, which existed only because the content was already fully absorbed into `CONTEXT.md` and `modules/design.md` — both now defer to the skill instead. Model-invoked (context-load cost accepted). |
| code-review | **reject — relabeled** | The two-axis review workflow duplicates `code-pr-review` plus the factory's review nodes, and is wired to his tracker plumbing. **One explicit exception, ruled by the user this sweep:** its Fowler 12-smell baseline (ruled at 0016, never landed — #276 closed unbuilt) lands in `code-pr-review`: repo standards override the baseline; every hit a labelled judgment call, never a hard violation. |
| diagnosing-bugs | **verbatim — new** (was reject) | 0016 called it the largest true gap, then dropped it in a rescope with no recorded rationale. Installed: build-the-red-loop-before-hypothesizing discipline, ranked loop techniques, 3–5 falsifiable hypotheses, regression-test-at-a-correct-seam. Its post-mortem handoff to `improve-codebase-architecture` now resolves. Model-invoked. |
| domain-modeling | verbatim | Standing. Byte-identical at v1.2.3; pin bump only. |
| grill-with-docs | adapt | Standing. His decomposition adopted as an authored thin front door onto installed `/grilling` + `/domain-modeling` ("everything both skills say applies as written") — the one modification is invocation mode, because upstream's `disable-model-invocation: true` would break the four workspace call sites. Absorbs the grilling rework with zero edits. |
| implement | reject | Standing. The factory graph already does this with more rigor. |
| improve-codebase-architecture | **verbatim — new** (was unruled) | The workspace's only architecture-scanning capability: hot-spot scoping, subagent exploration under the deletion test, HTML candidate report, then grilling the picked candidate. Dependencies (`codebase-design`, `grilling`, `domain-modeling`) all installed. User-invoked. Report needs CDN at view time — accepted. |
| prototype | verbatim | Standing; pin bump is substantive. Logic branch: terminal TUI → single self-contained HTML demo (pure JS state module + free-play buttons + walkthrough tabs). Not a mockup — the state machine genuinely executes; it validates the model in isolation, as the TUI always did. The decision transfers, translated, into a non-JS codebase. UI branch byte-identical. Branch/worktree/capture machinery (rule 6) unchanged — `design/SKILL.md` and issue-authoring's prototype machinery survive; only the "run outputs" phrase needed widening (stage 3). |
| research | verbatim | Standing. Byte-identical at v1.2.3; pin bump only. |
| resolving-merge-conflicts | **reject — fresh reason** | Not necessary. (The 2026-07-31 rescope reject carried no recorded rationale; DR 0020 records this one.) |
| setup-matt-pocock-skills | reject | Standing. Its job is served by workspace standards. |
| tdd | **reject — relabeled, fresh reasons** | (1) "Test only at pre-agreed seams… confirm with the user" puts a mandatory user stop inside the AFK factory build node; 0016 deliberately reversed this and the conflict is live at v1.2.3. (2) His loop excludes refactoring and routes it to his `code-review` (rejected); our build node carries integrated slice- and chunk-scope refactor passes. (3) `build/references/tdd.md` is the workspace's TDD procedure, wired to briefs and gates — his skill would be a second, contradicting procedure. |
| to-spec | **reject — new** | Too complicated to land today; potential conflict with the wayfinder and wayfinder-to-build skills. **Reevaluate next sweep.** |
| to-tickets | **reject — new** | Too complicated to land today; potential conflict with the wayfinder and wayfinder-to-build skills. **Reevaluate next sweep.** |
| triage | **reject — relabeled** | Not adopted; its label and role vocabulary were hard-rejected at 0016. The redundancy check and verify-the-claim moves 0016 landed in `intake/SKILL.md` stay where they landed. |
| wayfinder | verbatim | Standing; pin bump. One substantive line (grilling tickets: "Always invoke" the skills; one-question-at-a-time phrasing deleted). The rumored decision-ticket rename predates our pin — **the accommodation package (five `wayfinder:*` labels, `tracking.wayfinder-shape` lint, tracker-operations rules, two judgments) is entirely unaffected.** Judgments re-run on changed bytes; verdicts expected identical. |
| wizard | **verbatim — new** (tier reject voided by promotion) | Generates staged interactive bash wizards for human click-through procedures. Its `template.sh` (17 functions, 3 arrays) exceeds the shell standard's glue-only boundary — resolved by adding a vendored-scripts exemption to the shell standard, not by rejecting: scripts bundled in a vendored skill are external dependencies, carried unmodified (the lints already skip `dotfiles/.agents` via the externally-managed roots). Model-invoked. |

#### Productivity

| Skill | Verdict | Reason |
|---|---|---|
| grill-me | reject | Standing. Redundant with `grill-with-docs`. |
| grilling | verbatim | Standing; pin bump is substantive: one-question-at-a-time → round-by-round frontier questioning with a mandated `❓ Qn / ➡️ recommendation` format and non-blocking subagent fact-finding. Absorbed through `grill-with-docs` with zero edits. |
| handoff | reject | Standing. The authored `handoff` already mirrors his production version. |
| teach | reject | Standing. Personal productivity, outside the factory's domain. |
| to-questionnaire | **reject — new reason** (tier reject voided by promotion, reopened, re-rejected) | Solo developer — there is no third party to send a questionnaire to. |
| wait-what | **verbatim — new** (new upstream skill) | Three-line corrective: re-pitch the last message with context, in ASD-STE100 Simplified Technical English, using `CONTEXT.md` vocabulary. User-invoked, zero context load. Its first-person voice is covered by the prose standard's vendored-verbatim exemption. |
| writing-for-agents | **verbatim — new** (was adapt as `writing-great-skills`) | The craft layer for any agent-consumed document. Supersedes the two workspace files that were seeded from it (stage 2). Model-invoked. The two conflicts with workspace conventions are resolved by the split description rule (principle 9) and the retained always-explicit rule (principle 10) — `skill-conventions.md` wins where they collide, stated there as a precedence sentence. |

#### In-progress (tier policy: no installs)

| Skill | Verdict | Reason |
|---|---|---|
| claude-handoff | reject | Standing. Tier policy; our `handoff` mirrors his production version. |
| loop-me | reject | Standing. Belongs to mission-control. |
| setup-ts-deep-modules | reject | Standing. TypeScript-only. |
| writing-beats | reject | Standing. Journey-based structure fights current-state reference prose. |
| writing-fragments | reject | Standing. Idea capture lives in mission-control. |
| writing-shape | **reject — relabeled** | Tier policy; not adopted. The format-argument checklist 0016 landed in the prose standard stays where it landed. |

#### Misc

| Skill | Verdict | Reason |
|---|---|---|
| git-guardrails-claude-code | reject | Standing. The PAT already makes the guarded operations impossible; 0012 rules against a second published hook. |
| migrate-to-shoehorn | reject | Standing. TypeScript-only. |
| scaffold-exercises | reject | Standing. Bound to his course business. |
| setup-pre-commit | reject | Standing. Competing Node toolchain for a problem `pre-commit` solves. |

#### Deleted upstream — rows retire

`design-an-interface`, `qa`, `request-refactor-plan`, `ubiquitous-language`,
`edit-article`, `obsidian-vault`, `batch-grill-me`. Material old verdicts
landed from them stays where it landed; the rulings remain in DR history.
The two fragments 0016 recorded as ruled-but-never-landed both close this
branch: `code-review`'s 12-smell baseline **lands by the user's explicit
ruling this sweep** (see its row); `request-refactor-plan`'s small-step rule
is **formally retired** — its upstream source no longer exists.

**Result across the live 35: 11 verbatim (`codebase-design`,
`diagnosing-bugs`, `domain-modeling`, `grilling`,
`improve-codebase-architecture`, `prototype`, `research`, `wait-what`,
`wayfinder`, `wizard`, `writing-for-agents`) · 1 adapt (`grill-with-docs`)
· 23 reject.** Four new model-invoked descriptions enter every session's
context: `codebase-design`, `diagnosing-bugs`, `wizard`,
`writing-for-agents`.

### Declined upstream positions

Recorded so no future sweep re-finds them.

- Omit `disable-model-invocation` when false → declined (principle 10).
- One-line descriptions for **all** skills → split rule instead
  (principle 9).
- `ask-matt` PHASE-BOUNDARIES harvest → declined.

(Fragment-level declines from agent reports are moot under principle 2 —
the whole-skill verdicts cover them.)

## Reference

### Adaptations that stay authored

Deliberately not deferred. Stage 7's duplication scan checks these for creep
rather than for removal.

| File | Why it stays |
|---|---|
| `standards/testing/conventions.md` | `tdd` rejected; mostly workspace-original pytest material. |
| `dotfiles/dot-claude/skills/build/references/tdd.md` | The factory's TDD procedure — workspace machinery, deliberate divergences (autonomous seam forethought, in-loop refactor passes). |
| `dotfiles/dot-claude/skills/design/references/design-it-twice.md` | Adaptation wired into the `/design` node; its supersede-rule trim turned out to be a no-op (stage 2). |
| `standards/claude-code/skill-conventions.md` | The binding layer; almost entirely workspace-original, and it wins where `/writing-for-agents` collides with it. |

### Install mechanics

The `skills` CLI writes to live `~/.agents`, outside this branch. To keep the
sweep atomic, installs and bumps are vendored as file edits in the worktree:

1. Copy each bundle byte-for-byte from the v1.2.3 clone into
   `dotfiles/.agents/skills/<name>/`.
2. Lock entries in `dotfiles/.agents/.skill-lock.json`: `skillFolderHash` =
   the upstream **git tree SHA** of the skill folder at v1.2.3. **Validate
   the algorithm first** against the byte-identical `research` and
   `domain-modeling` entries — their computed tree SHAs must equal the
   existing lock values; if they don't, stop and investigate rather than
   hand-invent hashes.
3. Mirror symlinks in `dotfiles/dot-claude/skills/<name>` →
   `../../.agents/skills/<name>` for the six new installs (the repo already
   commits such symlinks; `claude-code.skill-mirror` audits them at the
   commit gate).
4. Post-merge, on main: `stow` refresh / `scripts/sync-dotfiles` per
   skill-management.md (user-run, never from a worktree) — noted in the PR.

### Open findings

Out of scope for this sweep, not acted on: `marimo-batch`'s vendored tree
(`d8589525…`) does not match its lock entry (`d2800038…`); the other three
pre-existing vendored skills match exactly.
