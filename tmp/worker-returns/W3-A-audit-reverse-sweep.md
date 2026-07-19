# W3-A · sonnet · reverse sweep: "audit" outside standard context (issue 169) — verbatim return

## Verdict on H-a: REFUTED

**Coverage:**
- Total tracked hits for `audit` (case-insensitive, excluding `.venv`/`uv.lock`): **844**
- Exclusion buckets (counted only, per instructions): `readings/**` = 47, `docs/decisions/**` = 12, `tmp/**` = 101 → **160 excluded**
- Remaining classified: **684**
  - Detector-fleet identifiers (script names, `*_audit.py` modules, console-script keys, pre-commit hook ids, test files/names mirroring detectors, `standard-cards.yaml`/`code-matches-docs.yaml` judgement declarations, standards-card `## Audit` headers): the bulk, ≈604 hits. Verified all 10 detector scripts trace to a standard card's Audit cell: `repo-audit`→build.md/claude-code.md/knowledge-organization.md, `python-audit`→python.md, `testing-audit`→testing.md, `ref-audit`→docs/cross-references.md/knowledge-organization.md, `okf-audit`→instrument.md/knowledge-organization.md, `decisions-audit`→decisions.md, `skill-audit`→claude-code.md/claude-code/skill-management.md, `judgements-audit`→semantic-validation.md, `standards-audit`→standard.md, `workspace-audit`→build.md/tracking.md/workflow.md/build/enforcement.md. No orphan `*-audit` identifier found.
  - Prose requiring per-line judgment: **80 lines** (isolated via targeted grep stripping identifier-form hits), read individually. Of these: ~34 in-context (CONTEXT.md's Audit/Detector/Gate glossary, standards lifecycle-vocabulary prose, `standard/format.md` governance definitions), **45 counterexamples** (below), **1 borderline** not counted as a violation.

**Counterexamples (H-a refuted):**

**Cluster 1 — `docs/third-party-survey.md` (6 sites, lines 19, 37, 72, 106, 118, 130):**
Text (representative): `**Audited:** 2026-04-29 ([Decision Record 0001]...)`, `**Audited:** 2026-05-08 — *not adopting*`, etc.
Why out of context: this file surveys third-party frameworks (Matt Pocock skills, Superpowers, etc.) for adoption fitness. It is explicitly "not authoritative," has no standards card, no detector, no Audit cell — "Audited" is ordinary English for "we looked into this," not a detector run against a standard.
Suggested reword: `**Reviewed:**` or `**Surveyed:**` (matches the doc's own `type: Survey` frontmatter).

**Cluster 2 — the PR/spec/code-review skill family calling their LLM-driven review pass "an audit" (39 sites across 10 files):**
- `dotfiles/dot-claude/skills/code-pr-review/SKILL.md:14,35` — "The review is an audit only..." / "## 3. Audit the change"
- `dotfiles/dot-claude/skills/doc-pr-review/SKILL.md:14,33` — same pattern
- `dotfiles/dot-claude/skills/sdd-code-pr-review/SKILL.md:14,49`, `sdd-spec-review/SKILL.md:14,43` — same pattern
- `dotfiles/dot-claude/skills/write-agent-review/SKILL.md:17` — "Audit the prescriptive surface, not the editorial."
- `dotfiles/dot-claude/skills/fill-issue-gaps/SKILL.md:12` — "it audits the issue against its scope files and its epic"
- `dotfiles/dot-claude/skills/issue-overwatch/SKILL.md:38,58,81` — "dispatch the chosen tracks' audits in parallel," "read-only audits that never commit," "The audit subagents post findings"
- `dotfiles/dot-claude/skills/agent-view-overwatch/SKILL.md:54` — "audit running → verdict at its overwatch"
- `workflow/workflow.md:43,220` — "subagents audit and post findings," "`/doc-pr-review` audits the diff's documentation"
- `workflow/skill-authoring.md:29,45` — "audit dimensions," "Don't audit what a deterministic gate already enforces."
- `standards/build/enforcement.md:43` — "the code-review skills run it before auditing" — the sharpest single instance: this sentence sits in the doc's own **"Outside the gates"** section, explicitly describing something the document itself declares is *not* part of the Audit/Detector/Gate machinery it defines, yet reuses "audit" for it.

Why out of context: `CONTEXT.md`'s own resolved glossary defines **Audit** as "a run of one or more **Detectors**" and **Detector** as "the read-only *script*." These review skills are LLM subagents judging a PR/spec/doc diff against an issue brief and conventions — not scripts, not tied to any standard card's Audit cell. CONTEXT.md even states "a one-time human code review is not enforcement," implicitly distinguishing it from the detector machinery — but nothing resolved whether it's still an "Audit." This is systemic ordinary-English reuse of "audit" for "read-only review pass," exactly the kind of blur CONTEXT.md's "Flagged ambiguities" section says it already caught twice ("check"/"audit," "audit"/"detector") — this third blur (detector-run audit vs. agent-driven PR-review) wasn't caught.
Suggested reword: "review" — most of these files already alternate with "review" in the same paragraph (e.g., "Review a direct-mode issue's PR diff..." opens `code-pr-review.md`), so `## 3. Audit the change`→`## 3. Review the change`, "proceed to the audit"→"proceed to the review," "dispatch the chosen tracks' audits"→"...reviews," etc.

**Closest-to-the-line judgment calls (spot-check these):**
1. `standards/build/enforcement.md:43` (above) — could be argued either way: it's inside standards-machinery prose (arguably in-context per the rule's "machinery/docs" clause) but describes an activity the same doc places "outside the gates."
2. `dotfiles/dot-claude/skills/sdd-spec-review/SKILL.md:22,25` and `sdd-code-pr-review/SKILL.md:27` — "the grammar you audit against," "what the Module design dimension audits against" — these do name a real standard (module design, spec-standard), so arguably closer to in-context than the rest of cluster 2, but still verb-form "audit" for an LLM review pass.
3. `standards/testing/conventions.md:74` — "an audit log was written" — generic example of a side-effect assertion in test-writing guidance; "audit log" is universal software terminology, unconnected to this repo's detector system. Ruled harmless/not a counterexample since it's illustrating a hypothetical third-party app's behavior, not this repo's own machinery — but it is technically "ordinary English audit."
4. `docs/decisions/0003-decline-superpowers.md:16` — "which prompted this audit. Working audit notes are in..." — same third-party-review pattern as Cluster 1, but sits inside `docs/decisions/**` (excluded bucket per instructions), so not classified — flagging in case the orchestrator wants it swept too.

Files read in full or near-full for this investigation: `CONTEXT.md`, `docs/third-party-survey.md`, `standards/build/enforcement.md`, `standards/standard/format.md`, `pyproject.toml`, `scripts/README.md`, `.pre-commit-hooks.yaml`, `.pre-commit-config.yaml`, `standards/build/canonical.md`, `standards/build/canonical/.pre-commit-config.yaml`, and all files in Cluster 2 above.

---
Orchestrator verification (post-return): spot-checked `docs/third-party-survey.md:19,37` ("Audited:" lines present), `code-pr-review/SKILL.md:14,35` ("The review is an audit only", "## 3. Audit the change"), `standards/build/enforcement.md:43` ("run it before auditing", in the Outside-the-gates section), and CONTEXT.md's glossary ("**Audit** — A run of one or more detectors; read-only…" with "_Avoid_: check"). All four match the probe's claims. REFUTED verdict accepted.
