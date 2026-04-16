# SDD Synthesis Report

A synthesis of the DeepLearning.AI SDD course, GitHub Spec Kit, the human's existing SDD practice, and an April 2026 Claude Deep Research landscape report on the spec-driven development community. This report documents how the human operates or plans to operate in SDD. It is not normative. Another session will integrate accepted items into the human's standards at `~/workspace/dev-playbook/standards/spec-driven-development/`.

**Referencing policy.** Every practice, rule, and decision is either (a) cited inline to its community source(s) or (b) flagged **⚠️ self-originated** so idiosyncratic practices are visible for scrutiny. The marker is a warning, not a badge.

---

## 1. The Human's Position in the SDD Landscape

**Spec-anchored with strong spec authority.** Specs are the authoritative artifact. Code is hand-written by supervised agents and must track the spec; when spec and code diverge, the spec wins and code is updated to match. Machine-verified traceability, implemented via [OpenFastTrace](https://github.com/itsallcode/openfasttrace), prevents specs from rotting silently.

[Birgitta Böckeler's three-school taxonomy](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) on martinfowler.com is the closest thing the community has to a definitional framework. The human's verdict on each school:

- **Spec-first** (GitHub Spec Kit, OpenSpec). Specs are input to the process; code becomes the long-lived artifact. **Rejected.** Specs drift out of sync once code exists because no traceability enforcement exists in these frameworks.
- **Spec-anchored** (Kiro). Spec and code co-maintained as peers. **Adopted**, with traceability enforcement added.
- **Spec-as-source** (Tessl). Spec is primary; code is generated output marked `DO NOT EDIT`. **Rejected in its literal form**; the underlying principle (spec as authority) is preserved through traceability enforcement rather than code regeneration.

[Drew Breunig's "SDD Triangle" post (March 2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html) refines this picture: SDD is a feedback loop, not a one-way pipeline — implementation improves the spec, and each cycle refines it. This framing is compatible with the spec-anchored position.

---

## 2. Principles

1. **SDD Triangle.** Per [Drew Breunig (March 2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html), spec, tests, and code do not stay automatically synchronized — implementation continuously surfaces gaps. The default reconciliation is that the spec wins and code updates to match. Every divergence is a tracked action item; the human decides what to do about it.

2. **Small steps, human-in-the-loop.** The human provides meaningful course corrections at phase boundaries. Default unit of autonomous work is one requirement category.

---

## 3. Workflow — How the Human Operates

Each subsection below follows the same structure: **Practice** (what the human does, with pointers to existing documentation in the repo and notes on divergences or self-originated items) and **Community context** (what others in the SDD community are doing).

### 3.1 Spec Authoring Conventions

#### Practice

The full spec-authoring standard — EARS sentence templates, RFC 2119 modal verbs, OFT Requirement-Enhanced Markdown, typed spec item IDs, revision policy, and the design layer's role — is specified in [`~/workspace/dev-playbook/standards/spec-driven-development/writing.md`](~/workspace/dev-playbook/standards/spec-driven-development/writing.md) and [`design-layer.md`](~/workspace/dev-playbook/standards/spec-driven-development/design-layer.md).

- **Design layer as red/green test-target bridge.** Explicit `dsn` items are standard in [OFT](https://github.com/itsallcode/openfasttrace). Using them specifically as the interface target for red/green TDD — the mechanism that makes the red agent tractable — is **⚠️ self-originated**.
- **Interface stubs from the design phase.** After design approval, the design agent produces stub modules, classes, and functions (`raise NotImplementedError`, empty bodies) matching the design's module layout. The red agent writes tests against these stubs; the green agent replaces them. Not in the standards docs; lives in the `sdd-design` skill. **⚠️ self-originated.**

#### Community context

EARS adoption is nearly absent from the SDD ecosystem despite being a 2009 systems-engineering technique (Mavin, Rolls-Royce, IEEE RE09) with INCOSE backing. Current adoption is concentrated in Kiro (AWS); Spec Kit tracks adding it at [issue #1356](https://github.com/github/spec-kit/issues/1356).

**Spec hierarchy and file layout** have no convergent community standard. [spec-kit discussion #152](https://github.com/github/spec-kit/discussions/152) shows multiple emerging patterns — session vs. persistent spec split (Vidimitrov, Dexhorthy), community-built extensions (Stn1slv's `spec-kit-archive` consolidating feature specs into a living `.specify/memory/spec.md`; Thlandgraf's SPECLAN Change Request model), and proliferating forks (spec-kitty, nexus). No single layout is widely adopted. The human's current OFT-typed approach (`feat`, `req`, `dsn`, `utest`, `itest`) stays in place; revisit only if a convergent community standard emerges.

### 3.2 Traceability Infrastructure

#### Practice

The OFT coverage chain (`feat → req → dsn → utest/itest`), the `Needs:`/`Covers:` linking mechanism, and the `pytest-sdd` and `sdd-chain-text` tooling are specified in [`design-layer.md`](~/workspace/dev-playbook/standards/spec-driven-development/design-layer.md) and [`tooling.md`](~/workspace/dev-playbook/standards/spec-driven-development/tooling.md).

- **`@pytest.mark.req()` test-to-requirement linkage.** Every test carries a pytest marker whose value is the OFT ID of the `req` item it covers. Makes each `Needs: utest` declaration machine-verifiable. **⚠️ self-originated.**
- **`pytest-sdd` plugin.** Source at `~/workspace/dev-playbook/tools/src/pytest_sdd/`. **⚠️ self-originated.**
- **`sdd-chain-text` CLI.** Source at `~/workspace/dev-playbook/tools/src/sdd_chain_text/`. **⚠️ self-originated.**

#### Community context

Formal machine-verified traceability is essentially absent from the SDD community, which grew from AI/agentic coding rather than requirements engineering (INCOSE, IEEE RE). [OpenFastTrace](https://github.com/itsallcode/openfasttrace) has ~137 stars; the closest alternatives [Doorstop](https://github.com/doorstop-dev/doorstop) (~593 stars) and [StrictDoc](https://github.com/strictdoc-project/strictdoc) (~264 stars) have no SDD integration. The April 2026 landscape report confirmed no SDD framework implements machine-verified traceability. Community discussion at [spec-kit#152](https://github.com/github/spec-kit/discussions/152) shows an active desire for spec-to-code linkage without a convergent solution — this is a gap the human has already filled.

**Decisions as a fourth linkable artifact** — worth flagging. Drew Breunig's [**Plumb**](https://github.com/dbreunig/plumb) tool (introduced in his [SDD Triangle post](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html); last commit ~one month ago, not stale but not actively developed) proposes capturing implementation decisions as a fourth linkable artifact alongside spec, code, and tests — a decision log tied to requirements, enforced via git hook at commit time. Not adopted. The general concept — decisions as a separate linkable artifact — is compatible with the OFT coverage graph; a `dec` artifact type (Decision → Requirement) could become a future extension.

### 3.3 Agent Workflow

#### Practice

Red/green agent separation, the plan-before-code gate, and phase coordination are documented in the SDD skills at [`~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-red/SKILL.md`](~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-red/SKILL.md), [`sdd-green/SKILL.md`](~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-green/SKILL.md), and [`sdd-issue-coordinate/SKILL.md`](~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-issue-coordinate/SKILL.md).

- **Agent presents plan before writing code.** The strict written-gate form (scope + approach document presented before any code; silence is not approval) is **⚠️ self-originated** in this form, though the general idea (plan before code) appears in [Addy Osmani's multi-agent orchestration writing](https://addyosmani.com/blog/good-spec/) and in Spec Kit's phase structure.
- **Adversarial code review.** After the green phase, before merge, a separate agent session reviews the diff adversarially. P0 implementation: Claude sub-agent with a reviewer prompt. P1 (future, out of scope for now): a different model family for genuine architectural independence. Not yet documented in any skill or standard. Cross-model review is **⚠️ self-originated** as a future direction; general adversarial/second-pair agent review appears in [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD).

#### Community context

Red/green separation has multiple community validations. [VS Code's official GitHub Copilot custom agents documentation](https://code.visualstudio.com/docs/copilot/guides/test-driven-development-guide) describes three agents (`TDD-red.agent.md`, `TDD-green.agent.md`, and a refactor agent). [AgentCoder (arXiv 2312.13010)](https://arxiv.org/abs/2312.13010) formalizes programmer / test designer / test executor agents. Simon Willison's [Agentic Engineering Patterns guide](https://simonwillison.net/guides/agentic-engineering-patterns/) describes the pattern. Common motivation: context pollution — when test logic and implementation knowledge share a context, tests tend to be written against whatever code exists rather than against requirements.

### 3.4 Project Process

#### Practice

Branch-per-issue, draft PR scaffolding, and PR description conventions are specified in [`~/workspace/dev-playbook/standards/development-workflow.md`](~/workspace/dev-playbook/standards/development-workflow.md). The phase-dispatching loop that uses this workflow is documented in the [`sdd-issue-coordinate`](~/workspace/dev-playbook/dotfiles/.claude/skills/sdd-issue-coordinate/SKILL.md) skill. No self-originated items in this section beyond the agent-workflow items already covered in §3.3.

#### Community context

**Replanning as a named phase between features.** Named and taught in the [DeepLearning.AI course "Spec-Driven Development with Coding Agents"](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) by Paul Everitt (JetBrains). The pattern — explicitly revisiting project principles, roadmap ordering, and the process itself between features rather than rolling straight into the next feature — is recognized in SDD conversation but not universally formalized across tools.

---

## 4. Rejected Practices

| Practice | Source | Rejection reason |
|---|---|---|
| BMAD-METHOD (21 persona agents simulating agile team) | [bmad-code-org/BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) | Solves a team-coordination problem that does not exist for a solo developer. |
| Literal spec-as-source (Tessl: code regenerated from spec, `DO NOT EDIT` markers) | [Tessl](https://tessl.io) | Too extreme; closed beta; incompatible with a solo developer's compute budget and desire for personal understanding of the code. |
| Spec-first pure (Spec Kit, OpenSpec as frameworks) | [github/spec-kit](https://github.com/github/spec-kit), [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Specs drift once code exists; no traceability enforcement means the spec will rot. The whole framework's premise treats specs as second-class citizens once code is produced. |
| Spec Kit clarify step (`/speckit.clarify`) | Spec Kit | Part of a framework that treats specs as second-class. Not adopted in isolation because the pattern of structured pre-planning clarification is already covered by the interview pattern in the human's existing `sdd-func-reqs` skill. |
| Spec Kit cross-artifact analysis (`/speckit.analyze`) | Spec Kit | Same framework-level rejection. OFT already provides cross-artifact consistency through the coverage graph. |
| Task decomposition with dependency ordering (T001 IDs, `[P]` parallel markers, file paths per task) | [Spec Kit `/speckit.tasks`](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md), Kiro `tasks.md` | The pattern lives inside the Spec Kit / Kiro spec-first frameworks, which are themselves rejected for treating specs as second-class. No reason to mimic their task-decomposition convention while rejecting their foundational philosophy. Current practice — informal division by requirement category, driven by the red/green cycle — stays as-is. |
| OpenSpec delta spec format (ADDED/MODIFIED/REMOVED markers) | [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | Same framework-level rejection. The OFT revision-bump mechanism already handles incremental change propagation without a separate delta format. |
| Agent Hooks (Kiro concept: event-driven agent triggers on file save) | [Kiro documentation](https://kiro.dev) | Unwilling to launch agents on every file save; the token cost and blast radius of agent-per-save is unacceptable for a solo developer paying for usage. |
| Kiro IDE / CLI | AWS Kiro | Inferior to Claude Code per firsthand evidence from internal Amazon adoption. Methodology is portable; the tool is rejected. |
| `AGENTS.md` as project constitution | [Agentic AI Foundation](https://agents.md/) convention | Conflates agent operating instructions with project principles; the human separates these. `CLAUDE.md` is used for agent instructions. Project principles as a separate artifact are also rejected (see row below). |
| Project constitution file (separate artifact capturing "what the project is") | [Spec Kit `.specify/memory/constitution.md`](https://github.com/github/spec-kit/blob/main/spec-driven.md), Kiro `.kiro/steering/` (`product.md`/`tech.md`/`structure.md`), [DeepLearning.AI course](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) (mission + tech stack + roadmap) | No convergent community standard exists — Spec Kit prescribes nine articles enforced through phase gates, Kiro splits into three files, the DeepLearning.AI course uses a lighter three-section version, and `AGENTS.md` mixes project principles with agent instructions. Each framework reinvents the concept differently. Not adopting anything until a clearer community standard emerges. |
| `roadmap.md` as a managed living SDD artifact | [DeepLearning.AI course](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) (roadmap maintained as part of the project constitution, updated at replanning) | The existing [repo-documentation standard](~/workspace/dev-playbook/standards/repo-documentation.md) already designates GitHub Issues as the authoritative source for tactical work. A strategic `ROADMAP.md` is allowed there as an optional file for broad goals, but is not an SDD concern — no separate SDD-managed roadmap artifact. |
| Explicit out-of-scope section as a universal spec requirement | Human's prior practice (prior `sdd-func-reqs` skill instructions) | Not sold on this as a universal requirement. May still be useful in specific specs; not a standing practice. |
| Cross-agent portability as a design driver | General SDD community framing | Claude Code is the only agent in use; paying portability tax for agents that will not be used is waste. |
| Conferences, Discord communities, dedicated SDD subreddits | Community venues | Bandwidth-limited; blogs, GitHub releases, and the AI Native Dev podcast are sufficient for staying current. |