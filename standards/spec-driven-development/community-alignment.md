# Community Alignment & Personal Standard

## Purpose

This document synthesizes four sources — the DeepLearning.AI SDD course, GitHub Spec Kit, the author's existing personal workflow, and an April 2026 Claude Deep Research landscape report — into a single personal standard for spec-driven development. It captures:

- Where the author sits in the SDD community landscape
- Which practices are adopted and from which source
- Which practices are rejected and why
- Open questions queued for future sessions
- A curated subscription list for staying current as the ecosystem evolves

This document is the authoritative reference for SDD decisions going forward. It persists conclusions so they survive conversation context loss.

**Audience:** the author (solo data scientist / developer) and any agent collaborating on SDD work.

**Agent:** Claude Code is the author's agent. Agent-agnostic considerations are out of scope.

---

## The Author's Position in the SDD Landscape

**Spec-anchored with strong spec authority.** The spec is the source of truth but not the source of code generation. Code is hand by agents under supervision. When spec and code disagree, the spec wins and code is updated to match. Machine-verified traceability (OpenFastTrace) enforces that specs cannot silently rot.

This position does not match any existing framework exactly:

- Spec-first frameworks (Spec Kit, OpenSpec) are rejected because specs become second-class artifacts that drift out of sync once code exists.
- Tessl's literal spec-as-source (code regenerated from specs, `// DO NOT EDIT` markers) is rejected as too extreme for a solo developer with limited compute budget and also a strong desire for personal understanding and control.
- Kiro's methodology (EARS, requirements/design/tasks pipeline) is close, but the Kiro IDE/CLI is rejected in favor of Claude Code. Methodology is portable; the tool is not the methodology.

The standard going forward is a custom workflow built on the author's existing OFT/EARS/red-green foundation, augmented with compatible ideas from Spec Kit, the course, and Breunig's SDD Triangle.

---

## The Three Schools (Böckeler's Taxonomy)

Birgitta Böckeler's martinfowler.com framework defines three SDD philosophies. It is the closest thing the community has to a definitional reference.

| School | Exemplar | Spec status | Author's verdict |
|---|---|---|---|
| **Spec-first** | Spec Kit, OpenSpec | Input to the process; code becomes the long-lived artifact | **Rejected** — specs rot without traceability enforcement |
| **Spec-anchored** | Kiro | Spec and code co-maintained as peers | **Adopted** — with OFT-enforced spec authority |
| **Spec-as-source** | Tessl | Spec is primary; code is generated output | **Rejected** in its literal form; spirit adopted (spec as authority) |

**Drew Breunig's "SDD Triangle" (March 2026)** refines this: SDD is a feedback loop, not a one-way pipeline. Implementing code improves the spec and tests. This is compatible with and reinforces the spec-anchored position.

---

## Core Principles

1. **Spec-as-source-of-truth.** The human only authors the spec. All code is generated from it by agents. When spec and code disagree, the spec wins — update the code.

2. **Spec describes reality, not intent.** When implementation diverges from the spec, the spec is updated to reflect what was actually built. Divergence is flagged, not hidden.

3. **Explicit out-of-scope.** Every functional spec declares what is NOT in scope. Without this, agents fill gaps with plausible-but-wrong assumptions.

4. **Structured requirements are prerequisites to traceability.** EARS sentence templates + RFC 2119 modal verbs produce parseable statements; freeform prose does not.

5. **Machine-verified traceability.** Every requirement must be covered by design, tests, and ultimately implementation. OpenFastTrace enforces this as a directed graph: `feat → req → dsn → utest/itest`.

6. **Agent role separation.** Tests and implementation are written by different agent sessions with no cross-modification. This isolates test logic from implementation knowledge (the "context pollution" problem the community has named).

7. **Feedback loop, not pipeline.** Implementation surfaces spec gaps. Bugs are spec gaps. Each cycle through the loop refines the spec.

8. **Small steps, human-in-the-loop.** The human provides meaningful course corrections at phase boundaries. Default unit of autonomous work: one requirement category.

9. **Branch per issue, PR-driven.** Each feature lives on its own branch with a draft PR. Specs are versioned alongside code in Git.

---

## Adopted Practices

| Practice | Source | Notes |
|---|---|---|
| EARS sentence templates | Personal + validated by Kiro | Five patterns: Ubiquitous, Event-driven, State-driven, Optional, Unwanted |
| RFC 2119 modal verbs (`SHALL`/`SHOULD`/`MAY`) | Personal | Subset of RFC 2119; backticked everywhere |
| OFT traceability graph (`feat → req → dsn → utest/itest`) | Personal | Essentially absent from broader SDD community — this is whitespace the author fills |
| Typed spec item IDs (`type~name~revision`) | Personal | Revision bumps break downstream links, forcing acknowledgment |
| Design layer as interface bridge | Personal | Names modules/classes/signatures so the red agent has a target |
| Interface stubs from design phase | Personal | `raise NotImplementedError`; red writes tests against these |
| Red/green agent separation | Personal + validated by community | No cross-modification; VS Code has official docs for this pattern; academic backing (AgentCoder) |
| `@pytest.mark.req()` test-to-requirement linkage | Personal | Makes OFT's `Needs: utest` machine-verifiable |
| `pytest-sdd` for lint + trace | Personal | Runs as part of normal test suite |
| `sdd-chain-text` for chain visualization | Personal | Answers "is content at each layer appropriate?" |
| Explicit out-of-scope section | Personal | Every spec declares what not to build |
| Mandatory plan gate before code | Personal | Red and green agents present written plan; await explicit approval |
| Handoff files for phase transitions | Personal | `.claude/sdd-handoff.md` — context briefing, not design brief |
| Bug-fix as spec-gap loop | Personal | Bugs flag spec gaps; fix triggers regression test request |
| Project constitution (what the project is) | Spec Kit | See distinction below — NOT the same as CLAUDE.md |
| Clarify step before planning | Spec Kit (`/speckit.clarify`) | Structured coverage-based questioning |
| Task decomposition with dependency ordering | Spec Kit (`/speckit.tasks`) | `T001` IDs, `[P]` parallel markers, file paths |
| Cross-artifact consistency analysis | Spec Kit (`/speckit.analyze`) | Catches drift between spec/plan/tasks before implement |
| Replanning as named phase between features | Course | Revise constitution, update roadmap, improve process itself |
| Roadmap as managed living document | Course | Sequence of phases; update at replanning |
| Research backlog pattern | Course | Mid-feature ideas go to a known location for later scheduling |
| Feedback-loop framing over pipeline framing | Breunig (SDD Triangle) | Implementation improves spec; not one-way |
| Adversarial code review | Author concern (new) | See section below; P0 = Claude sub-agent; P1 = different model |
| Post-green operational review | Personal | "If someone pulls main, does it just work?" |
| Post-green E2E verification on real data | Personal | Unit tests check contracts; E2E checks the system works |

---

## Constitution vs. Agent Instructions — A Distinction the Community Muddles

The broader SDD community conflates two different artifacts. This standard separates them:

| Artifact | Answers | Example contents |
|---|---|---|
| **Project Constitution** | *What is this project? What are its boundaries?* | Mission, scope, architectural principles, non-negotiable quality constraints, technology boundaries, out-of-scope commitments |
| **Agent Instructions** (`CLAUDE.md`) | *How should the agent work in this repo?* | Commands to run, formatting rules, tool preferences, git workflow, boundaries like "always do / ask first / never do" |

The constitution is a spec-level artifact and belongs in `specs/`. `CLAUDE.md` is operational and belongs at the repo root. The community mixes them (often in a single `AGENTS.md` or `constitution.md`); the author does not.

`AGENTS.md` is gaining adoption as a cross-tool agent instruction standard (Agentic AI Foundation under the Linux Foundation, 60K+ repos). The author uses `CLAUDE.md` directly since Claude Code is the only agent; cross-tool compatibility is not a concern.

---

## Adversarial Code Review

The author wants adversarial code review as a first-class step in the workflow. Goals:

- Catch issues a single-perspective agent misses (blind spots, motivated reasoning, rubber-stamping)
- Introduce independent critique at natural phase boundaries

**P0 implementation:** adversarial review by a separate Claude sub-agent with a reviewer prompt. Runs before merge; flags issues for the author's decision.

**P1 (future):** adversarial review by a different model family (e.g., GPT, Gemini). Out of scope now — the author is on Claude Code only.

**Placement in workflow:** after green phase completes, before final merge. Integrates naturally with the existing post-green operational review and E2E verification steps.

---

## Rejected Practices

| Practice | Rejected because |
|---|---|
| BMAD-METHOD (21-agent simulated agile team) | Solving a team-coordination problem the solo author does not have |
| Literal Tessl spec-as-source (regenerate code from spec) | Too extreme; closed beta; does not match solo developer ergonomics |
| Spec-first pure (Spec Kit/OpenSpec as-is) | Specs drift once code exists; no traceability enforcement means the spec will rot |
| Kiro IDE / CLI | Inferior to Claude Code per firsthand evidence from internal Amazon experience (the author was among the ~1,500 engineers who pushed back on the mandate). Methodology is portable; the tool is rejected |
| `AGENTS.md` as constitution | Conflates agent instructions with project principles; these are different concerns |
| Discord communities, in-person conferences | Bandwidth-limited; blogs + podcast + GitHub releases are sufficient |
| Cross-agent portability as a design driver | Claude Code only; do not pay compatibility tax for agents that will not be used |

---

## Open Questions — Queued for Future Sessions

1. **Spec taxonomy and document architecture.** How to divide a project's specs into distinct document types (feature specs, functional requirements, design specs, API specs, data model specs). What goes in each, hierarchical relationships, content standards per type. The current OFT types imply structure but it is not formalized.

2. **The spec-to-test gap.** The red agent cannot write meaningful tests from requirements alone — tests target an API surface. The design spec is the bridge (it defines the API contract red tests against and green implements). Needs formalization: what must a design spec contain to make red tractable?

3. **Agent Hooks (Kiro concept).** Event-driven automations triggered by file changes. Understand what they are and whether/how to adapt to Claude Code via hooks in `settings.json`.

4. **Three-agent TDD — purpose of the refactor agent.** VS Code's official documentation describes three agents (red / green / refactor). Understand what the refactor agent does and whether it belongs in the author's workflow.

5. **Multi-document structure compatibility across frameworks.** Whether Spec Kit's `.specify/`, Kiro's `.kiro/`, and OpenSpec's layouts are interchangeable or mutually exclusive; whether the author's `specs/` structure should borrow conventions from any of them.

6. **Spec Kit preset feasibility.** Whether Spec Kit's preset system could be used to override its default user-story format with EARS + OFT, making Spec Kit's tooling (CLI, hooks, extensions) usable without adopting its spec format.

7. **Delta spec format (OpenSpec).** OpenSpec's ADDED/MODIFIED/REMOVED markers for describing changes rather than restating whole systems. Potentially useful for brownfield work.

---

## Community Gaps the Author Is Positioned to Fill

These are places where the author's existing practice meaningfully exceeds what the broader SDD community is doing. Worth noting as portfolio differentiators and potential contribution areas.

1. **Formal machine-verified traceability in SDD.** No SDD framework implements this. OFT, Doorstop, StrictDoc exist but have essentially zero overlap with the SDD community. The author already does it.

2. **EARS + OFT combined.** Structured requirements (EARS) as the prerequisite for traceability (OFT). Kiro uses EARS; OFT-style tools exist; nobody combines them in an SDD context.

3. **Dual-agent TDD with OFT markers.** Red/green separation exists in the community under various names (no standard), but none tie it to a traceability graph. The author's `@pytest.mark.req()` → OFT `Needs: utest` chain is novel.

4. **Constitution / agent-instruction separation.** The community mixes these; the author separates them deliberately.

---

## Staying Connected

### GitHub repos to watch (2 total)

- **github/spec-kit** — https://github.com/github/spec-kit
- **Fission-AI/OpenSpec** — https://github.com/Fission-AI/OpenSpec

These two are the bellwethers. Everything else propagates through blog coverage.

### Blogs to follow

- **Drew Breunig** — https://www.dbreunig.com (read "The Rise of Spec-Driven Development" Feb 2026 and the SDD Triangle March 2026)
- **Birgitta Böckeler on martinfowler.com** — https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html
- **Den Delimarsky** (Spec Kit creator) — https://den.dev
- **Addy Osmani** — https://addyosmani.com/blog/good-spec/
- **Simon Willison** (Agentic Engineering Patterns) — https://simonwillison.net/guides/agentic-engineering-patterns/
- **Justin Searls** (dual-loop BDD) — https://justin.searls.co
- **Emily Bache** (TDD with agentic AI) — https://coding-is-like-cooking.info
- **Thoughtworks blog** — https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/
- **Tweag Agentic Coding Handbook** — https://tweag.github.io/agentic-coding-handbook/

### Podcasts

- **AI Native Dev** (Tessl / Guy Podjarny) — YouTube and Spotify — already subscribed

### Talks (watch when released on YouTube)

- Drew Breunig — Computer History Museum talk (March 2026)
- AWS re:Invent — Kiro session DVT209

### Standards references

- **EARS official guide** — https://alistairmavin.com/ears/
- **INCOSE Guide to Writing Requirements v4.0** — https://www.incose.org/docs/default-source/working-groups/requirements-wg/guidetowritingrequirements/incose_rwg_gtwr_v4_summary_sheet.pdf
- **Spec Kit's `spec-driven.md`** (closest to a community manifesto) — https://github.com/github/spec-kit/blob/main/spec-driven.md
- **VS Code TDD agents guide** (three-agent pattern) — https://code.visualstudio.com/docs/copilot/guides/test-driven-development-guide
- **OpenFastTrace user guide** — https://github.com/itsallcode/openfasttrace/blob/main/doc/user_guide.md

### Not subscribing to

Discord communities, in-person conferences, dedicated subreddits (none exist for SDD specifically; discussion is scattered across r/ChatGPTCoding, Hacker News).

---

## Source Summaries

### DeepLearning.AI Course — "Spec-Driven Development with Coding Agents"

Short free course (~45 minutes) taught by Paul Everitt (JetBrains developer advocate). High-level, conceptual. Introduces constitution (mission + tech stack + roadmap), feature loop (plan / implement / validate), replanning phase, cognitive debt / AI fatigue, research backlog pattern, sub-agent review technique. Not a technical authority. Strongest contribution: naming replanning as an explicit phase.

URL: https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/

### GitHub Spec Kit

Python CLI (`specify init`) + template system + extension/preset ecosystem. ~88K GitHub stars as of April 2026. Maintained by GitHub. Workflow: `/speckit.constitution` → `/speckit.specify` → `/speckit.clarify` → `/speckit.plan` → `/speckit.tasks` → `/speckit.implement`. Supports 24+ agents. Strongest contributions: separation of specify (what/why) from plan (how); clarify as a discrete step; formal task decomposition with dependency ordering; cross-artifact analysis. Weakness: no machine-verified traceability; specs drift once code exists; freeform user-story format rather than structured EARS.

URL: https://github.com/github/spec-kit

### Personal Workflow (Prior to This Conversation)

Rigorous spec-anchored system built on OpenFastTrace + EARS + RFC 2119. Five-agent pipeline: coordinator → func-reqs → design → red → green. Machine-verified traceability (`pytest-sdd`). Custom tooling (`sdd-chain-text`). Strict red/green agent isolation with mandatory plan gates. The foundation of the personal standard going forward. Novel contributions: EARS+OFT combination, dual-agent TDD tied to traceability markers, design layer as explicit interface-naming artifact.

Location: `~/workspace/dev-playbook/standards/spec-driven-development/` and `~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-*/`

### Claude Deep Research Report — "The SDD landscape in mid-2026"

April 2026 landscape survey covering nine facets: community, toolkits, EARS, traceability, spec formats, TDD, constitution, replanning, staying-connected resources. Introduced Böckeler's three-school taxonomy, documented Kiro's EARS adoption and enterprise traction, confirmed formal traceability is essentially absent from SDD, validated dual-agent TDD exists in the community but without a standard name. Key misframings (corrected via follow-on chat): defaulted to spec-first recommendation; conflated Kiro-the-IDE with Kiro-the-methodology; treated `AGENTS.md` as equivalent to Spec Kit's constitution despite the conceptual mismatch.

File: `~/Desktop/SDD landscape.md` and follow-on feedback at `~/Desktop/research_report_feedback.txt`
