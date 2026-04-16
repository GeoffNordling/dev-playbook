# ADR-003: Evaluate SDD Community Landscape; Adopt Spec-Anchored Position

**Date:** 2026-04-16
**Status:** Accepted

## Context

This workspace uses a custom spec-driven development (SDD) workflow built around RFC 2119 modal verbs, EARS sentence templates, OpenFastTrace traceability (see [ADR-001](001-adopt-openfasttrace.md)), and a set of Claude Code skills (`sdd-func-reqs`, `sdd-design`, `sdd-red`, `sdd-green`, `sdd-issue-coordinate`). [ADR-002](002-evaluate-spec-kit-retain-custom-sdd.md) evaluated GitHub Spec Kit specifically and retained the custom workflow.

Since ADR-002, the SDD community has continued to evolve and new reference material has appeared: the DeepLearning.AI short course ["Spec-Driven Development with Coding Agents"](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) by Paul Everitt (JetBrains), [Birgitta Böckeler's taxonomy of SDD tools](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) on martinfowler.com, [Drew Breunig's "SDD Triangle" post (March 2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html), and an April 2026 Claude Deep Research landscape report commissioned for this evaluation.

This ADR evaluates the broader SDD landscape — frameworks, vocabulary, and patterns other than Spec Kit — and records which practices we adopt, which we reject, and which self-originated practices we continue to use in the absence of a community equivalent.

## Decision

### Position within the community

We adopt the label **spec-anchored** for our position, following [Böckeler's three-school taxonomy](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html):

- **Spec-first** — specs are input to the process; code becomes the long-lived artifact (Spec Kit, OpenSpec). **Rejected.** Specs drift out of sync once code exists because these frameworks provide no traceability enforcement.
- **Spec-anchored** — spec and code co-maintained as peers (Kiro). **Adopted**, with machine-verified traceability added on top.
- **Spec-as-source** — spec is primary; code is generated output marked `DO NOT EDIT` (Tessl). **Rejected in its literal form.** The underlying principle (spec as authority) is preserved through OFT traceability enforcement rather than through code regeneration.

### Framing: SDD Triangle

We adopt [Drew Breunig's SDD Triangle framing (March 2026)](https://www.dbreunig.com/2026/03/04/the-spec-driven-development-triangle.html): spec, tests, and code do not stay automatically synchronized — implementation continuously surfaces gaps, and each cycle refines the spec. This replaces an earlier principle in `overview.md` that stated "the spec SHALL always describe reality." The substance is the same (spec wins, code updates to match) but the Triangle framing is more accurate about the ongoing, iterative nature of the reconciliation and situates our position within a recognized community vocabulary.

### What we continue to do

No changes to the core machinery:

- Functional requirements authored with EARS sentence templates and RFC 2119 modal verbs
- OFT coverage chain (`feat → req → dsn → utest/itest`) with `Needs:`/`Covers:` links
- `pytest-sdd` and `sdd-chain-text` for machine-verified traceability
- Red/green agent separation for test/implementation isolation
- Mandatory plan gate before any code is written

The April 2026 landscape report confirmed that no SDD framework in current use implements machine-verified traceability, and that red/green agent separation has multiple independent community validations ([VS Code GitHub Copilot custom agents](https://code.visualstudio.com/docs/copilot/guides/test-driven-development-guide), [AgentCoder (arXiv 2312.13010)](https://arxiv.org/abs/2312.13010), [Simon Willison's agentic engineering patterns guide](https://simonwillison.net/guides/agentic-engineering-patterns/)). The custom workflow does not need to change to track the community — on these dimensions it is ahead of the community.

### Self-originated practices

Several practices we use have no community equivalent we could find at the time of this evaluation. They are recorded here so they remain visible for future scrutiny — being self-originated is a warning flag, not a badge:

- Using OFT `dsn` items specifically as the red/green test-target bridge (explicit `dsn` items are standard in OFT; using them as the interface target that makes the red agent tractable is the novel part)
- Interface stubs produced by the design agent (`raise NotImplementedError`, empty bodies) that the red agent writes tests against and the green agent replaces
- `@pytest.mark.req("req~...")` test-to-requirement markers that make every `Needs: utest` declaration machine-verifiable
- The `pytest-sdd` plugin and `sdd-chain-text` CLI that implement the above
- The strict written plan gate (scope + approach document presented before any code; silence is not approval)

If a convergent community standard emerges for any of these, we should revisit.

### Deferred directions

Recorded here as potential future work, not adopted today:

- **Adversarial code review.** A separate agent session reviews the green phase's diff before merge. P0 implementation: Claude sub-agent with a reviewer prompt. P1: a different model family for genuine architectural independence. Not yet in any skill or standard.
- **Replanning as a named phase.** The DeepLearning.AI course names "replanning" as an explicit phase between features — revisiting project principles, roadmap ordering, and the process itself rather than rolling straight into the next feature. The pattern is compatible with the `sdd-issue-coordinate` dispatcher and could become a named step.
- **Decisions as a fourth linkable artifact.** Drew Breunig's [Plumb](https://github.com/dbreunig/plumb) tool proposes capturing implementation decisions as a fourth artifact alongside spec, code, and tests, enforced via git hook. Not adopted, but a `dec` artifact type (Decision → Requirement) is compatible with the OFT coverage graph and could become a future extension.

## Alternatives Considered

| Alternative | Source | Why rejected |
|---|---|---|
| [GitHub Spec Kit](https://github.com/github/spec-kit) as a framework | Spec Kit | See [ADR-002](002-evaluate-spec-kit-retain-custom-sdd.md). Today's deeper research reinforces that conclusion: no machine-verified traceability, no agent isolation, informal spec language. The entire framework's premise treats specs as second-class citizens once code is produced. |
| Spec Kit's `/speckit.clarify` step | Spec Kit | Part of a rejected framework. The underlying pattern (structured pre-planning clarification) is already covered by the interview pattern in `sdd-func-reqs`. |
| Spec Kit's `/speckit.analyze` cross-artifact check | Spec Kit | Part of a rejected framework. OFT already provides cross-artifact consistency through the coverage graph. |
| Spec Kit / Kiro task decomposition (T001 IDs, `[P]` parallel markers, file paths per task) | [Spec Kit `/speckit.tasks`](https://github.com/github/spec-kit/blob/main/templates/commands/tasks.md), Kiro `tasks.md` | Lives inside rejected spec-first frameworks. No reason to mimic their task-decomposition convention while rejecting their foundational philosophy. Current practice — informal division by requirement category, driven by the red/green cycle — stays. |
| [OpenSpec](https://github.com/Fission-AI/OpenSpec) delta spec format (ADDED/MODIFIED/REMOVED markers) | Fission-AI/OpenSpec | Same spec-first framework-level rejection. The OFT revision-bump mechanism already handles incremental change propagation. |
| Literal spec-as-source (code regenerated from spec, `DO NOT EDIT` markers) | [Tessl](https://tessl.io) | Too extreme; closed beta; incompatible with a solo developer's compute budget and desire for personal understanding of the code. The principle of spec-as-authority is preserved via OFT instead. |
| [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) (21 persona agents simulating an agile team) | bmad-code-org | Solves a team-coordination problem that does not exist for a solo developer. |
| Kiro IDE / CLI | [AWS Kiro](https://kiro.dev) | Inferior to Claude Code per firsthand evidence from internal Amazon adoption. Methodology is portable; the tool is rejected. The spec-anchored position we adopted from Kiro does not require its tooling. |
| Kiro Agent Hooks (event-driven agent triggers on file save) | Kiro | Unwilling to launch agents on every file save; token cost and blast radius of agent-per-save is unacceptable for a solo developer paying for usage. |
| [`AGENTS.md`](https://agents.md/) as project constitution | Agentic AI Foundation convention | Conflates agent operating instructions with project principles. `CLAUDE.md` covers agent operating instructions; project principles as a separate artifact are also rejected (next row). |
| Project constitution file (separate artifact capturing "what the project is") | [Spec Kit `.specify/memory/constitution.md`](https://github.com/github/spec-kit/blob/main/spec-driven.md), Kiro `.kiro/steering/`, [DeepLearning.AI course](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) | No convergent community standard — Spec Kit prescribes nine articles with phase gates, Kiro splits into three files, the DeepLearning.AI course uses a lighter three-section version, and `AGENTS.md` mixes principles with agent instructions. Each framework reinvents the concept differently. **This reverses one of the "ideas worth adopting" in [ADR-002](002-evaluate-spec-kit-retain-custom-sdd.md).** The deeper landscape view surfaced the lack of convergence; we defer until a clearer community standard emerges. |
| `roadmap.md` as a managed living SDD artifact | [DeepLearning.AI course](https://www.deeplearning.ai/short-courses/spec-driven-development-with-coding-agents/) | The [repo-documentation standard](../../standards/repo-documentation.md) already designates GitHub Issues as the authoritative source for tactical work. A strategic `ROADMAP.md` remains allowed as optional repo documentation, but is not an SDD concern — no separate SDD-managed roadmap artifact. |
| Explicit out-of-scope section as a universal spec requirement | Prior `sdd-func-reqs` skill instruction | Not sold on this as a universal requirement. May still be useful in specific specs; not a standing practice. The `sdd-func-reqs` skill now asks the user whether anything belongs out of scope and records `NA` explicitly when the answer is no. |
| Cross-agent portability as a design driver | General SDD community framing | Claude Code is the only agent in use; paying portability tax for agents that will not be used is waste. |
| SDD-focused conferences, Discord communities, dedicated subreddits | Community venues | Bandwidth-limited; blogs, GitHub releases, and the AI Native Dev podcast are sufficient for staying current. |

## Consequences

- `standards/spec-driven-development/overview.md` principles updated: the `Spec-as-source` principle is replaced by **Spec-anchored** (with Böckeler reference and a link back to this ADR); a new **SDD Triangle** principle replaces the "spec describes reality" principle (with Breunig reference); the universal "state what NOT to build" principle is removed; "non-functional requirements" is renamed to **technical requirements**.
- `dotfiles/.claude/skills/sdd-func-reqs/SKILL.md` updated: the out-of-scope section is no longer prescribed unconditionally. The skill now asks the user and records `NA` when the answer is no.
- [ADR-002](002-evaluate-spec-kit-retain-custom-sdd.md)'s "project-level principles document" as an idea worth adopting is reversed here; the "structured research phase" idea from ADR-002 remains open.
- No changes to OFT, `pytest-sdd`, `sdd-chain-text`, the red/green skills, the design skill (apart from the principles fixes above), or the issue-coordinate dispatcher.
- The self-originated practices listed above remain self-originated. If a future evaluation finds community convergence on any of them, we should revisit whether our implementation still makes sense or should align with the community standard.
- The deferred directions (adversarial cross-model review, replanning phase, `dec` artifact type) are recorded here; if any is picked up, it becomes a separate issue and, if architecturally significant, a follow-up ADR.
