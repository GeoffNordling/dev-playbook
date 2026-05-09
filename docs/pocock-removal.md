# Pocock Removal — Working Notes

Decisions for removing the Matt Pocock dependency. Closing artifact is a new
ADR; this file is scratch and gets deleted after the ADR lands.

Structural decision up front: the `docs/agents/` pattern goes away. Anything
worth keeping moves into `docs/` and `standards/` directly.

## 1. Ideas in his skill bundles

**1a. Architecture vocabulary** — Module / Interface / Depth / Seam /
Adapter / Leverage / Locality, plus deletion test, dependency
categorization, one-vs-two-adapter rule, Design-It-Twice. Sources:
`improve-codebase-architecture/{LANGUAGE,DEEPENING,INTERFACE-DESIGN}.md`,
`tdd/{deep-modules,interface-design}.md`.
→ **Integrate into a new `standards/architecture-vocabulary.md`.**
Load-bearing for `sdd-design`.

**1b. TDD craft content** — behavior-not-implementation, mocks at
boundaries only, refactor catalog. Sources: `tdd/{tests,mocking,refactoring}.md`.
→ **Audit `standards/testing-conventions.md` for gaps; pull in the
refactor catalog if missing; otherwise drop the foreign content.**

**1c. ADR + CONTEXT format** — offer-gate, minimal ADR template, glossary
structure, multi-context map. Sources: `grill-with-docs/{ADR-FORMAT,CONTEXT-FORMAT}.md`.
→ **Integrate both formats into `standards/repo-documentation.md`** as the
canonical source of truth. **Lift `/grill-with-docs` into authored skills,
preserving body prose**, with two edits at copy time: (a) rewrite the
sibling references to `CONTEXT-FORMAT.md`/`ADR-FORMAT.md` so they point
at the absorbed standards; (b) extend the front matter with `effort:` per
our skill conventions. Soft cost noted: the skill carries Pocock's prose
voice inside our tree until/unless rewritten.

**1d. Triage / issue mechanics** — 5-role vocabulary, agent-brief format,
vertical-slice rules, issue body template, issue-tracker conventions.
Sources: `triage/AGENT-BRIEF.md`, `to-issues/SKILL.md` body,
`setup-matt-pocock-skills/{issue-tracker-github,triage-labels,domain}.md`.
→ **Integrate into `standards/issue-management.md`** (currently a pointer
file — replace pointers with content). GitHub-only; drop GitLab and
local-markdown variants. **Drop `.out-of-scope/` entirely.**

## 2. Pocock content already integrated into our repo

**2a. `docs/agents/` directory + `## Agent skills` block.** Drop both.
Redistribute:
- `issue-tracker.md` content → folded into `standards/issue-management.md`
  (per 1d).
- `triage-labels.md` content → folded into `standards/issue-management.md`
  (per 1d).
- `domain.md` → drop outright. Only inbound reference is the
  `## Agent skills` block in root `CLAUDE.md`, which dies with 2a.
- `## Agent skills` block in `CLAUDE.md` → delete.

**2b. Workspace standards with Pocock pointers.** Edit in place:
- `standards/issue-management.md` — convert from pointer file to authored
  content (per 1d).
- `standards/skill-management.md` — drop the Pocock vs. Superpowers
  anecdote paragraph. Keep the rule statement and the failure-modes
  paragraph (forward-looking; earn their keep).
- `standards/repo-documentation.md` — absorb ADR + CONTEXT formats (per
  1c); drop the `/setup-matt-pocock-skills` mention; drop the "borrowed
  from Matt Pocock" attribution on the cross-reference rules.
- `standards/testing-conventions.md` — audit and absorb refactor catalog
  (per 1b); drop the `/tdd` "runtime companion" pointer.

**2c. Survey + existing ADR cross-references.**
- `docs/third-party-survey.md` — add a Pocock entry modeled on the
  existing Superpowers entry: who he is, what we adopted, what we kept
  (citing new ADR), why we cut the direct dependency, watching going
  forward.
- ADR-0006 — status update (Superseded by ADR-NNNN); otherwise stays as
  historical record.
- ADR-0008 — decision stands. Add a "see also ADR-NNNN" pointer; no
  rewrite of the body.

**2d. 4-digit ADR numbering.** Keep. No action.

## 3. Pocock skills themselves

**3a. Drop — bootstrapper + redundant runtime.**
- `/setup-matt-pocock-skills` — its job (scaffolding `docs/agents/` and
  the `## Agent skills` block) dies in 2a. No purpose left.
- `/tdd` — covered by `sdd-implementation` for spec-bound work.
  Exploratory TDD outside SDD doesn't need a skill; the testing standard
  encodes the principles. Author later if a real gap surfaces.
- `/grill-me` — redundant with `/grill-with-docs`.

**3b. Lift — engineering runtimes.** Same pattern as `/grill-with-docs`
(per 1c): body prose preserved, references rewired to absorbed standards,
front matter extended with `effort:`.
- `/grill-with-docs` — references → `standards/repo-documentation.md`.
- `/triage` — references → `standards/issue-management.md`. Edit out
  the `.out-of-scope/` content (dropped per 1d).
- `/to-issues` — references → `standards/issue-management.md`.
- `/improve-codebase-architecture` — references →
  `standards/architecture-vocabulary.md`. Stays load-bearing for
  `sdd-design` and `sdd-implementation`.

**3c. Keep as direct Vercel dependency.** Tiny one-paragraph skills,
non-load-bearing. Stay installed via `npx skills@latest`, mirrored into
`.claude/skills/` by `sync-dotfiles.sh`.
- `/zoom-out`
- `/caveman`

After this, `/zoom-out` and `/caveman` are the only Pocock-sourced skills
still using the Vercel install path. Every other Pocock entry comes out
of the lockfile via `npx skills@latest remove <name> -g`.

**Lift ordering** (per skill being lifted):
1. Note current `.agents/skills/<name>/` content (kept in conversation
   or copied aside).
2. `npx skills@latest remove <name> -g` — removes from `.agents/skills/`.
3. `sync-dotfiles.sh` cleans the dangling symlink in `.claude/skills/`.
4. Create authored `.claude/skills/<name>/` with the lifted content +
   edits.

## 4. Our skills' hard-links into Pocock files

Mechanical rewire after 1 and 3 land.

- `sdd-design` — links to `tdd/{deep-modules,interface-design}.md` →
  `standards/architecture-vocabulary.md`. Drops the `/grill-me` invocation
  line. Invocation of `/improve-codebase-architecture` unchanged (lifted).
- `sdd-implementation` — links to `tdd/{refactoring,tests,mocking}.md` →
  `standards/testing-conventions.md`. Invocation of
  `/improve-codebase-architecture` unchanged (lifted).
- `sdd-requirements` — drops the `/grill-me` invocation line. Invocation
  of `/grill-with-docs` unchanged (lifted).

## 5. ADR

**New: ADR-0009.** Records:
- The cut: which Pocock skills dropped, which lifted, which kept as
  direct dependency.
- Why now: ADR-0008's rule applied honestly to a changed landscape —
  spec-tools moved to its own repo and is growing per-repo conventions
  that overlap Pocock's; the "complements existing canon" condition no
  longer holds.
- What replaced what: Pocock content absorbed into authored standards
  (`architecture-vocabulary.md`, `issue-management.md`, format sections
  of `repo-documentation.md` and `testing-conventions.md`); engineering
  runtimes lifted into authored skills.
- What stays as direct dependency: `/zoom-out`, `/caveman` (tiny utility
  skills, lift cost ≈ drop cost; chosen as direct deps for low overhead).

**Updates to existing ADRs:**
- ADR-0006 — status frontmatter: `Superseded by ADR-0009 in part`.
  Conventions like 4-digit numbering remain. Body unchanged (historical
  record).
- ADR-0008 — add a "see also ADR-0009" pointer. Decision stands; the
  Pocock-as-positive-example framing is now historical.

## 6. Install plumbing and external state

- **Lockfile + `.agents/skills/`.** Run `npx skills@latest remove <name>
  -g` for each of: `setup-matt-pocock-skills`, `tdd`, `grill-me`,
  `grill-with-docs`, `triage`, `to-issues`,
  `improve-codebase-architecture`. Keep: `zoom-out`, `caveman`.
  Non-Pocock entries (`marimo-*`, `pymc-modeling`) untouched.
- **`sync-dotfiles.sh`.** Run after the removals. Cleans dangling
  symlinks in `.claude/skills/` automatically. No script change needed.
- **GitHub issue labels.** No action. The 5-role vocabulary stays
  canonical (per 1d); labels remain valid.

## Execution plan

Working directly on `main` (no branch). Pause after each phase for diff
review; no commits until user approves. Skill-only lift (no duplicated
reference files in lifted bundles — standards are the single source of
truth).

Executed in this order:

**Phase A — Author the destination standards.** Lands first so references
have somewhere to point.
1. Create `standards/architecture-vocabulary.md` from `LANGUAGE.md` +
   `DEEPENING.md` + `INTERFACE-DESIGN.md` + `tdd/{deep-modules,interface-design}.md`.
2. Update `standards/repo-documentation.md`: absorb ADR template +
   offer-gate + `CONTEXT.md` format + `CONTEXT-MAP.md` variant from
   `grill-with-docs/{ADR-FORMAT,CONTEXT-FORMAT}.md`. Drop the
   `/setup-matt-pocock-skills` mention and the "borrowed from Matt
   Pocock" attribution.
3. Update `standards/testing-conventions.md`: audit against
   `tdd/{tests,mocking,refactoring}.md`; pull in the refactor catalog if
   missing. Drop the `/tdd` runtime-companion pointer.
4. Rewrite `standards/issue-management.md` from pointer-file to authored
   content: 5-role vocabulary, agent-brief format, vertical-slice rules,
   issue body template, GitHub-only conventions.
5. Update `standards/skill-management.md`: drop the Pocock vs. Superpowers
   anecdote paragraph.

**Phase B — Remove Pocock skills from the install path.**
6. `npx skills@latest remove setup-matt-pocock-skills tdd grill-me
   grill-with-docs triage to-issues improve-codebase-architecture -g`.
7. Run `dotfiles/bin/sync-dotfiles.sh` to clean dangling symlinks in
   `.claude/skills/`.

**Phase C — Lift the engineering skills.** Authored copies of body
prose with rewired references and `effort:` added.
8. Author `dotfiles/.claude/skills/grill-with-docs/` (with
   `CONTEXT-FORMAT.md` and `ADR-FORMAT.md` from the original bundle if
   we want them as supplementary refs, otherwise just SKILL.md
   pointing at `standards/repo-documentation.md`).
9. Author `dotfiles/.claude/skills/triage/` — body prose preserved,
   `.out-of-scope/` content removed, references to
   `standards/issue-management.md`. Decide whether `AGENT-BRIEF.md`
   stays as a supplementary ref or whether the standard is sufficient.
10. Author `dotfiles/.claude/skills/to-issues/` — references to
    `standards/issue-management.md`.
11. Author `dotfiles/.claude/skills/improve-codebase-architecture/` —
    SKILL.md references the standards (`architecture-vocabulary.md`,
    `module-design.md`, `dependency-taxonomy.md`). **Keep two
    workflow refs in the bundle** since they're skill workflow, not
    standards:
    - `DEEPENING-WORKFLOW.md` — Pocock's "Testing strategy: replace,
      don't layer" workflow content from DEEPENING.md.
    - `DESIGN-IT-TWICE.md` — Pocock's INTERFACE-DESIGN.md verbatim
      (the 3-step parallel-design process).

**Phase D — Rewire authored skills.**
12. `sdd-design/SKILL.md` — rewire `tdd/deep-modules.md` and
    `tdd/interface-design.md` links to `standards/module-design.md`;
    drop `/grill-me` line.
13. `sdd-implementation/SKILL.md` — rewire `tdd/{tests,mocking}.md`
    links to `standards/testing-conventions.md`. Replace the
    `tdd/refactoring.md` link with the inline 6-bullet refactor
    catalog (lifted from Pocock's `tdd/refactoring.md` verbatim, since
    it doesn't fit any standard — it's a post-green workflow checklist).
14. `sdd-requirements/SKILL.md` — drop `/grill-me` line.

**Phase E — Delete this repo's per-repo Pocock content.**
15. `rm -rf docs/agents/`.
16. Edit root `CLAUDE.md`: delete the `## Agent skills` block.

**Phase F — Update survey and existing ADRs.**
17. `docs/third-party-survey.md` — add Pocock entry (modeled on
    Superpowers entry).
18. `docs/adr/0006-adopt-matt-pocock-conventions.md` — status: Superseded
    by ADR-0009 in part.
19. `docs/adr/0008-decline-superpowers.md` — add "see also ADR-0009"
    pointer.

**Phase G — Write the new ADR.**
20. `docs/adr/0009-remove-pocock-direct-dependency.md`.
21. Update `docs/adr/README.md` index.

**Phase H — Cleanup.**
22. Run `dotfiles/bin/sync-dotfiles.sh` once more to verify clean state.
23. Run `python3 ~/workspace/dev-playbook/tools/bin/ref-check .` to catch
    any broken cross-references.
24. `rm docs/pocock-removal.md`.
25. Commit.
