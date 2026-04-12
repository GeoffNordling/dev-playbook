# ADR-002: Evaluate GitHub Spec Kit; Retain Custom SDD Workflow

**Date:** 2026-04-12
**Status:** Accepted

## Context

This workspace uses a custom spec-driven development (SDD) workflow built around RFC 2119 modal verbs, EARS sentence templates, OpenFastTrace traceability, and a set of Claude Code skills (`sdd-func-reqs`, `sdd-design`, `sdd-red`, `sdd-green`, `sdd-issue-coordinate`) that enforce agent isolation between test writing and implementation.

[GitHub Spec Kit](https://github.com/github/spec-kit) is an open-source toolkit for spec-driven development published by GitHub. It provides a CLI (`specify`) that scaffolds projects with templates, agent-agnostic command files, and a three-phase workflow: `/speckit.specify` (PRD generation), `/speckit.plan` (implementation planning with research, data models, and API contracts), and `/speckit.tasks` (phased task list generation). A `/speckit.implement` command then executes the tasks. The toolkit supports 25+ AI coding assistants through an integration registry.

We evaluated Spec Kit for potential adoption or integration with our existing workflow.

## Decision

We retain our custom SDD workflow and do not adopt Spec Kit. The two systems have fundamentally different emphases: Spec Kit optimizes for speed to first implementation across many AI agents; our workflow optimizes for correctness and machine-verified traceability with a single agent (Claude Code).

### Why Spec Kit does not fit

**No machine-verified traceability.** Spec Kit uses informal `FR-NNN` requirement numbering and checklist-based validation (pass/fail checkboxes). There is no equivalent to OFT's directed coverage graph, no tool that verifies every requirement has a design item, test, and implementation, and no mechanism to force downstream documents to acknowledge upstream changes (OFT revision numbers). Adopting Spec Kit would mean giving up the traceability guarantees that `pytest-sdd` and OFT provide.

**No agent isolation between tests and implementation.** Our workflow separates test writing (red agent) and implementation (green agent) into independent sessions so that tests express requirements independently of the code that satisfies them. Spec Kit's `/speckit.implement` command handles tests and implementation in a single agent session, and tests are explicitly optional ("only include them if explicitly requested"). This undermines the independence guarantee that is central to our TDD discipline.

**Informal spec language.** Spec Kit specs use natural prose with Given/When/Then acceptance scenarios and a "NEEDS CLARIFICATION" marker convention. Our specs use RFC 2119 obligation levels (SHALL/SHOULD/MAY) with EARS sentence templates, which produce unambiguous, testable requirements with clearly graded obligation strength. The Spec Kit format would be a precision downgrade.

**Task files as explicit artifacts.** Our workflow follows the principle that "humans SHALL NOT write tasks" -- agents derive and manage their own tasks from the spec. Spec Kit generates a `tasks.md` file as a durable artifact with checkbox items, task IDs, and parallelism markers. This is a different philosophy: it makes tasks a first-class document that humans and agents both manage, which adds an artifact to maintain without adding traceability.

### Ideas worth adopting

Two patterns from Spec Kit are worth incorporating into our workflow as future improvements:

**1. Structured research phase.** Spec Kit's `/speckit.plan` includes an explicit "Phase 0: Research" step that investigates library options, performance characteristics, and integration patterns before design decisions are made. Findings are documented in `research.md` with a structured format: decision, rationale, alternatives considered. Our `/sdd-design` skill currently jumps from reading specs to drafting design items. Adding a research step between "read the specs" and "draft the design" would improve design quality, especially for features that involve unfamiliar libraries or integration patterns. This could be implemented as either a new step within the existing `sdd-design` skill or as a standalone `sdd-research` skill that runs before design.

**2. Project-level principles document.** Spec Kit uses a "constitution" -- a set of immutable architectural principles (library-first, CLI interfaces, simplicity gates) that the planning agent checks against before proceeding. Our ADRs capture individual decisions; a principles document would capture standing policy that applies across all features. This is distinct from CLAUDE.md (which is about operating in the repo) and from ADRs (which document point-in-time decisions). A principles document would codify things like "prefer composition over inheritance," "no ORMs," or "every service must be independently deployable" -- recurring constraints that currently live only in the developer's head. If adopted, this would likely live at `specs/principles.md` or `memory/constitution.md` in each project and be referenced by the design skill.

## Alternatives Considered

| Alternative | Why rejected |
|---|---|
| Adopt Spec Kit wholesale, replacing our SDD workflow | Loss of OFT traceability, agent isolation, and RFC 2119 precision. A downgrade on every dimension we care about. |
| Use Spec Kit for scaffolding, keep our SDD for ongoing work | The scaffolded artifacts (spec template, plan template, constitution) would need to be immediately replaced with OFT-format specs. The scaffolding saves minutes; the reformatting costs more. |
| Integrate Spec Kit's multi-agent support layer | We use Claude Code exclusively. The integration registry adds complexity for a capability we do not need. |
| Adopt Spec Kit's template system alongside our own | Maintaining two spec formats in the same workflow creates confusion about which format applies when. |

## Consequences

- No changes to the current SDD workflow, skills, or standards documents
- The two improvement ideas (structured research phase, project-level principles document) are recorded here for future consideration and may be implemented via separate issues
- We are watching the [spec-kit repository](https://github.com/github/spec-kit) on GitHub to receive notifications on new releases. As an emerging community standard for spec-driven development, it is worth tracking how the project evolves -- particularly whether it adds formal traceability or agent isolation in future versions
- This ADR serves as a reference if Spec Kit is re-evaluated in the future as either tool evolves
