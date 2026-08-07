---
type: Plan
title: Pocock Sweep 2026-08 — Bootstrap Plan
description: Working plan for the bootstrap run of /pocock-sweep — every verdict at v1.2.3 with its reason, the documentation blast radius, and the landing order
---

# Pocock Sweep 2026-08 — Bootstrap Plan

Working state for the `worktree-pocock-sweep` branch. A fresh agent picking up
this branch reads this file first — the Operating procedure below says what
here is ruled and what is only guidance. Everything lands atomically in this
branch and ships as one PR. This file is deleted before merge.

## Operating procedure (set by the user, 2026-08-07)

This file is a doubly-compacted, lossy record of two long sessions. Its
epistemic status is split: the **per-skill verdict tables are ruled and
trusted** — which skills install verbatim, which adapt, which reject. Every
other section (blast radius, edit lists, landing details) is **guidance to
re-verify**. Decisions may also exist that neither the user nor this file
remembers; surfacing such candidates is part of each stage's fresh look.

- **One stage per context window.** Expect a compact or fresh start between
  stages; this file is the handoff. A stage ends by recording its outcome in
  the stage tracker below, inside that stage's own commit.
- **Interpretive stages (2–4) open with fresh-look-and-align.** Read the
  installed bundles and the workspace docs as they actually are, put the
  stage's proposed edit list to the user in chat, write the agreed list into
  this file, then execute. Mechanical stages move faster, but the user still
  reviews record text (the ledger, the DR) before it lands.
- **Commit and push after every stage — but only after the user has approved
  that stage's diffs in chat.** The user is in the loop on every stage: show
  the diffs, get the approval, then commit. Push with `--no-verify` — that
  skips only the pre-push judgment gate; the commit-gate lints always run.
- **Judgments run exactly once, at step 9 — never earlier, never as a side
  effect of a push.** (On 2026-08-07 the two re-keyed judgments were
  accidentally run once — both passed; the verdicts were discarded
  unrecorded.)

## Stage tracker

| Stage | Status |
|---|---|
| 1. Installs | **Done** — commit `7115b70`. Nine bundles vendored byte-identical; committed folder tree SHAs equal their lock entries; six mirror symlinks; the lock-hash algorithm was validated against the byte-identical `research`/`domain-modeling` entries before any hash was written. Landed early out of stage 3 because the commit gate forced it: `shellcheck`/`shfmt` `exclude: ^dotfiles/\.agents/` in `.pre-commit-config.yaml`, after shfmt rewrote two vendored scripts on the first commit attempt (upstream bytes restored and re-verified). The prose half — the shell standard's vendored-scripts exemption — still lands in stage 3. |
| 2. Deferrals | Not started. Plan correction, user-acknowledged: `design-it-twice.md` carries no internal-seams passage — that deferral row is a no-op; record it in DR 0020. |
| 3.–10. | Not started. |

Out-of-scope finding, not acted on this sweep: `marimo-batch`'s vendored
tree (`d8589525…`) does not match its lock entry (`d2800038…`); the other
three pre-existing vendored skills match exactly.

## Mission

`mattpocock/skills` moved from the workspace's last evaluated pin
(`2ab958093e83e0ec752e6c1c5932da465bf23e0c`, 41 skills, six tiers) to release
**v1.2.3** (`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, 35 skills, four
tiers). This branch is the bootstrap run of a repeatable procedure —
`/pocock-sweep` — that dockets only the deltas against standing verdicts,
escalates rulings to the user, and lands the results in one PR. The skill
itself is written at the end of this branch, from what actually worked,
via /skill-creator.

## Principles (minted or reaffirmed this sweep)

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

## Upstream state at v1.2.3

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

## Per-skill verdicts at v1.2.3

**Verdict vocabulary:** verbatim (installed unmodified, lock-tracked) ·
adapt (adopted, with the minimal named modification that fits it to
workspace constraints) · reject (not adopted; reason recorded). "New" marks
a ruling the user made or changed this sweep. Rows marked **relabeled**
carried 0016's old harvest-style "adapt" — a vocabulary principle 2 retires;
material those old verdicts already landed stays where it landed, but the
skills themselves are not adopted.

### Engineering

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
| prototype | verbatim | Standing; pin bump is substantive. Logic branch: terminal TUI → single self-contained HTML demo (pure JS state module + free-play buttons + walkthrough tabs). Not a mockup — the state machine genuinely executes; it validates the model in isolation, as the TUI always did. The decision transfers, translated, into a non-JS codebase. UI branch byte-identical. Branch/worktree/capture machinery (rule 6) unchanged — `design/SKILL.md` and issue-authoring's prototype machinery survive; only the "run outputs" phrase needed widening (below). |
| research | verbatim | Standing. Byte-identical at v1.2.3; pin bump only. |
| resolving-merge-conflicts | **reject — fresh reason** | Not necessary. (The 2026-07-31 rescope reject carried no recorded rationale; DR 0020 records this one.) |
| setup-matt-pocock-skills | reject | Standing. Its job is served by workspace standards. |
| tdd | **reject — relabeled, fresh reasons** | (1) "Test only at pre-agreed seams… confirm with the user" puts a mandatory user stop inside the AFK factory build node; 0016 deliberately reversed this and the conflict is live at v1.2.3. (2) His loop excludes refactoring and routes it to his `code-review` (rejected); our build node carries integrated slice- and chunk-scope refactor passes. (3) `build/references/tdd.md` is the workspace's TDD procedure, wired to briefs and gates — his skill would be a second, contradicting procedure. |
| to-spec | **reject — new** | Too complicated to land today; potential conflict with the wayfinder and wayfinder-to-build skills. **Reevaluate next sweep.** |
| to-tickets | **reject — new** | Too complicated to land today; potential conflict with the wayfinder and wayfinder-to-build skills. **Reevaluate next sweep.** |
| triage | **reject — relabeled** | Not adopted; its label and role vocabulary were hard-rejected at 0016. The redundancy check and verify-the-claim moves 0016 landed in `intake/SKILL.md` stay where they landed. |
| wayfinder | verbatim | Standing; pin bump. One substantive line (grilling tickets: "Always invoke" the skills; one-question-at-a-time phrasing deleted). The rumored decision-ticket rename predates our pin — **the accommodation package (five `wayfinder:*` labels, `tracking.wayfinder-shape` lint, tracker-operations rules, two judgments) is entirely unaffected.** Judgments re-run on changed bytes; verdicts expected identical. |
| wizard | **verbatim — new** (tier reject voided by promotion) | Generates staged interactive bash wizards for human click-through procedures. Its `template.sh` (17 functions, 3 arrays) exceeds the shell standard's glue-only boundary — resolved by adding a vendored-scripts exemption to the shell standard, not by rejecting: scripts bundled in a vendored skill are external dependencies, carried unmodified (the lints already skip `dotfiles/.agents` via the externally-managed roots). Model-invoked. |

### Productivity

| Skill | Verdict | Reason |
|---|---|---|
| grill-me | reject | Standing. Redundant with `grill-with-docs`. |
| grilling | verbatim | Standing; pin bump is substantive: one-question-at-a-time → round-by-round frontier questioning with a mandated `❓ Qn / ➡️ recommendation` format and non-blocking subagent fact-finding. Absorbed through `grill-with-docs` with zero edits. |
| handoff | reject | Standing. The authored `handoff` already mirrors his production version. |
| teach | reject | Standing. Personal productivity, outside the factory's domain. |
| to-questionnaire | **reject — new reason** (tier reject voided by promotion, reopened, re-rejected) | Solo developer — there is no third party to send a questionnaire to. |
| wait-what | **verbatim — new** (new upstream skill) | Three-line corrective: re-pitch the last message with context, in ASD-STE100 Simplified Technical English, using `CONTEXT.md` vocabulary. User-invoked, zero context load. Its first-person voice is covered by the prose standard's vendored-verbatim exemption. |
| writing-for-agents | **verbatim — new** (was adapt as `writing-great-skills`) | The craft layer for any agent-consumed document. Supersedes the two workspace files that were seeded from it (below). Model-invoked. The two conflicts with workspace conventions are resolved by the split description rule (principle 9) and the retained always-explicit rule (principle 10) — `skill-conventions.md` wins where they collide, stated there as a precedence sentence. |

### In-progress (tier policy: no installs)

| Skill | Verdict | Reason |
|---|---|---|
| claude-handoff | reject | Standing. Tier policy; our `handoff` mirrors his production version. |
| loop-me | reject | Standing. Belongs to mission-control. |
| setup-ts-deep-modules | reject | Standing. TypeScript-only. |
| writing-beats | reject | Standing. Journey-based structure fights current-state reference prose. |
| writing-fragments | reject | Standing. Idea capture lives in mission-control. |
| writing-shape | **reject — relabeled** | Tier policy; not adopted. The format-argument checklist 0016 landed in the prose standard stays where it landed. |

### Misc

| Skill | Verdict | Reason |
|---|---|---|
| git-guardrails-claude-code | reject | Standing. The PAT already makes the guarded operations impossible; 0012 rules against a second published hook. |
| migrate-to-shoehorn | reject | Standing. TypeScript-only. |
| scaffold-exercises | reject | Standing. Bound to his course business. |
| setup-pre-commit | reject | Standing. Competing Node toolchain for a problem `pre-commit` solves. |

### Deleted upstream — rows retire

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

## Documentation blast radius

Every entry below is either a supersede-rule deferral, an accommodation
required by an install the user ruled, or mechanical bookkeeping. Fragment
harvesting into standards is dead (principle 2).

### Deferrals — content yields to an installed skill (supersede rule)

| File | Action | Why |
|---|---|---|
| `standards/modules/design.md` | Gut to a thin pointer at `/codebase-design` | Near-pure mirror: all four principles, both diagrams, the three testability rules with his TypeScript examples. Any residue the skill doesn't carry survives as a stated workspace delta (verify at landing; likely none). |
| `CONTEXT.md` § Architecture | Trim to a pointer at `/codebase-design` | The eight terms, the five upstream relationship bullets, the rejected framings, and worked dialogue 1 are his, two entries character-for-character. **Kept:** the flagged-ambiguities log (workspace decision history, not a restatement) and all workspace-native sections (Governance, Machines, Tracking) and their relationships. Also makes `CONTEXT.md` conformant to the installed `domain-modeling` format rule: project-specific concepts only. |
| `standards/claude-code/skill-writing.md` | **Delete** | Superseded by installed `writing-for-agents`. Its overrides all already live as binding rules in `skill-conventions.md`; a delta file would restate them. Surviving workspace-original lines (e.g. "a failing test is fixed, never edited to pass") fold into `skill-conventions.md`. |
| `standards/claude-code/skill-glossary.md` | **Delete** | Its upstream source (`GLOSSARY.md`) no longer exists; definitions now live inline in the installed skill. Load-bearing originals fold into `skill-conventions.md`. |
| `dotfiles/dot-claude/skills/design/references/design-it-twice.md` | Remove its internal-seams passage | Duplicates the installed `codebase-design` bundle, which carries the internal/external-seam material verbatim. The rest of the file is a genuine adaptation (Opus pinning, worktrees, §6 synthesis diet) and stays authored, watched for creep at every sweep. |

Post-deletion architecture: **craft** = `/writing-for-agents` (installed) ·
**format** = `skill-conventions.md` (binding, workspace-original, wins on
collision) · **workflow** = `/skill-creator` (step 1 rewired to read
conventions + invoke `/writing-for-agents`).

### Deliberately NOT deferred — adaptations stay authored

| File | Why it stays |
|---|---|
| `standards/testing/conventions.md` | `tdd` rejected; mostly workspace-original pytest material. |
| `dotfiles/dot-claude/skills/build/references/tdd.md` | The factory's TDD procedure — workspace machinery, deliberate divergences (autonomous seam forethought, in-loop refactor passes). |
| `dotfiles/dot-claude/skills/design/references/design-it-twice.md` | Adaptation wired into the `/design` node; see deferrals for its one supersede-rule trim. |
| `standards/claude-code/skill-conventions.md` | The binding layer; almost entirely workspace-original. |

### Edits

| File | Edit |
|---|---|
| `standards/claude-code/skill-conventions.md` | Split description rule (principle 9); precedence sentence over `/writing-for-agents`; fold surviving craft lines; keep always-explicit + dispatcher fact. |
| `scripts/skill-lint` | Branch the description check on `disable-model-invocation`: two-sentence `Use when` when false, one-liner allowed when true. |
| All user-invoked authored skills | Descriptions shortened to one human-facing line (inventory at landing). |
| `standards/shell/conventions.md` | Vendored-scripts exemption (wizard's `template.sh` et al.). |
| `standards/tracking/issue-authoring.md` | Prototype run-outputs widened: "for a click-driven demo, the observed states captured as text or screenshots." |
| `dotfiles/dot-claude/skills/code-pr-review/SKILL.md` | Fowler 12-smell baseline as a new audit dimension + in-file catalog (explicit ruling; see `code-review` row). |
| `dotfiles/dot-claude/skills/skill-creator/SKILL.md` | Step 1: read `skill-conventions.md`, invoke `/writing-for-agents` (replaces `skill-writing.md`). |
| `dotfiles/dot-claude/skills/wayfinder-to-build/SKILL.md` | Slicing interview: one-question-at-a-time → rounds; nest a `/grilling` call if it fits cleanly. |
| `standards/tracking/tracker-operations.md` | Upstream-seed pin string → `6acc160` (content verified still accurate). |
| `standards/claude-code/index.md`, `standards/claude-code.md` card | Remove retired files; re-point cells. |
| `docs/external-skill-verdicts.md` | The ledger stays general across upstreams (pre-compact decision); this sweep touches only its `§ mattpocock/skills` section — updated to the new pin (35 skills / 4 tiers, every row per the verdict tables above; deleted-skill rows retire) — plus two general-rules edits that apply to every upstream: verdict vocabulary tightened per principle 2, supersede rule added. The `marimo-team/skills` and `pymc-labs/pymc-modeling` sections are untouched. |
| `docs/decisions/0020-pocock-skills-sweep-2026-08.md` (+ index) | Thin DR: this sweep's rulings and reversals (codebase-design, diagnosing-bugs, wizard, to-questionnaire reopen/re-reject, writing-for-agents, to-spec/to-tickets reject with reevaluate markers, resolving-merge-conflicts fresh reason, tdd fresh reasons); the minted principles (2, 3, 4, 9); the harvest-style-adapt relabels; both 0016 dangling fragments closed (12-smell lands, small-step retired); the recorded declines (omit-the-field, one-line-for-all, PHASE-BOUNDARIES harvest). |

### Declined upstream positions (recorded so no future sweep re-finds them)

- Omit `disable-model-invocation` when false → declined (principle 10).
- One-line descriptions for **all** skills → split rule instead
  (principle 9).
- `ask-matt` PHASE-BOUNDARIES harvest → declined.

(Fragment-level declines from agent reports are moot under principle 2 —
the whole-skill verdicts cover them.)

## Install mechanics (atomicity)

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

## Landing order

1. **Installs** — vendor six new bundles + three changed bundles; lock
   entries; mirror symlinks. (`research`, `domain-modeling` lock entries
   should come back unchanged.)
2. **Deferrals** — gut `modules/design.md`; trim `CONTEXT.md`; delete
   `skill-writing.md` + `skill-glossary.md`; fold survivors into
   `skill-conventions.md`; trim design-it-twice's internal-seams passage;
   fix every inbound reference (ref-lint hunts danglers).
3. **Standards edits** — every row of the Edits table.
4. **Lint split** — `skill-lint` description branching; shorten
   user-invoked authored descriptions.
5. **Records** — ledger rewrite, DR 0020, indexes, pin strings.
6. **Gates** — full commit-gate suite (`skill-lint`, `ref-lint`,
   `okf-lint`, `prose-lint`, the rest via `make check` equivalents).
   Judgments are NOT run here — they wait for step 9.
7. **Audit** — adversarial pass: mirror rule clean; no authored/installed
   name collisions; every call site of the five bumped skills still true;
   supersede-rule duplication scan (`CONTEXT.md`, standards vs. all eleven
   installed bundles); no dangling references to retired files; ledger
   internally consistent with the DR. Delete this file.
8. **Write `/pocock-sweep`** via /skill-creator — codifying: resolve latest
   tag → clone → diff against ledger → docket only deltas (verdict flips,
   tier moves, new/deleted skills, expired reasons, supersede-rule
   duplication check), every delta its own item with a recommendation →
   user rules item by item (agent reports are leads, never rulings) →
   whole-skill verdicts only: verbatim / adapt-minimal / reject, no
   fragment mining → land atomically in a worktree branch → audit →
   ledger + thin DR → PR ending in a habit brief. Settled frontmatter:
   user-invoked only, `model: inherit`, `effort: xhigh`, no arguments, no
   references dir, no scripts.
9. **Judgments** — the one and only judgments run, via the `/run-judgments`
   loop: everything the sweep re-keyed (the two wayfinder judgments — both
   passed the discarded 2026-08-07 run, so identical verdicts are expected —
   plus whatever the standards edits re-key). Record the verdicts; the push
   gate goes green here.
10. **PR** — one PR from this branch; body carries the change inventory and
   the **habit brief**: what changes for an operator who knew the prior
   state (grilling now lands in rounds — answer by number; logic prototypes
   arrive as double-click HTML demos with walkthrough tabs; `/improve-codebase-architecture`
   and `/diagnosing-bugs` now exist and when to reach for them;
   `/writing-for-agents` replaces the two retired standards files when
   authoring skills; `/wizard` for click-through procedures; `/wait-what`
   to force a re-pitch; architecture vocabulary now lives behind
   `/codebase-design`, not `CONTEXT.md`).
