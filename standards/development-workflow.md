# Development Workflow Standard

The key words "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", and "MAY" in this
document are to be interpreted as described in RFC 2119, following the vocabulary
conventions in the [spec-driven-development standard](spec-driven-development.md).

## Purpose

Define how development work is conducted across sessions so that any human or agent can pick up where the last session left off, without relying on memory or verbal handoff.

## Issue-Driven Development

All non-trivial work SHALL start as a GitHub Issue. The issue describes the goal — what needs to happen and why. It is the authoritative statement of intent for a piece of work.

Trivial changes (typo fixes, single-line corrections) MAY skip issue creation.

## Spec-Driven Development

Some projects follow spec-driven development (SDD). A project follows SDD when it has a `specs/` directory. See the [spec-driven-development standard](spec-driven-development.md) for conventions on spec format, structure, and when SDD is warranted.

When a project follows SDD, the issue triggers spec work before coding begins:

1. Translate the issue into functional requirements (`/sdd-func-reqs`)
2. Design the system's structure (`/sdd-design`). For new features or significant changes, define the components, interfaces, and data flow that the red/green agents will implement against. This includes basic scaffolding and stubbing for modules, functions, and classes (raise `NotImplementedError` at this phase). For simple changes where the functional spec directly implies the implementation, this step may be skipped.
3. Write tests and implementation in parallel (`/sdd-red` + `/sdd-green`)

Not every issue in an SDD project warrants the full spec workflow. The spec-driven-development standard's criteria for when SDD is overkill still apply — trivial changes and simple bug fixes can skip straight to implementation.

## Branch and Draft PR

When work begins on an issue, a branch SHALL be created and a draft PR SHALL be opened early — ideally in the first session, before significant code is written. The draft PR SHALL link to the issue it addresses. In SDD projects, spec updates are typically the first commits on the branch.

The purpose of the early draft PR is not to signal "ready for review." It is to create a living artifact that tracks progress.

## PR Description as Progress Tracker

The PR description SHALL be updated incrementally as work progresses. It is not written once at the end — it evolves with the work.

The PR description SHOULD contain:
- A summary of the approach being taken
- What has been completed so far
- What remains to be done
- Any blockers or open questions

In SDD projects, the spec carries the detailed requirements — the PR description SHOULD focus on progress, approach, and decisions rather than restating what the spec already covers.

When meaningful progress is made in a session, the PR description SHALL be updated before the session ends.

## Session Handoff

When a new session begins on in-progress work, context SHALL be reconstructed from durable artifacts, not from memory. The reconstruction sequence is:

1. **Read the issue** — what's the goal?
2. **Read the specs** (SDD projects) — what are the requirements?
3. **Read `git log main..HEAD`** — what's been done?
4. **Read the PR description** — what's the approach, what's remaining?

This sequence gives a human or agent full context without any prior knowledge of the work.

## Issue Comments

Issue comments SHOULD be used sparingly — only for significant events:

- A change in approach ("tried X, hit Y, switching to Z")
- A blocker that pauses work
- A decision that affects scope

Issue comments SHALL NOT be used for routine progress updates. The PR description and commit history carry that information.

## Summary

| Question | Where to look |
|----------|--------------|
| What's the goal? | GitHub Issue |
| What are we building? (SDD) | `specs/functional_requirements.md` |
| How is the system structured? (SDD) | `specs/design.md` or `docs/adr/` |
| What's been done? | `git log main..HEAD` |
| What's the current approach? | Draft PR description |
| Why did we change course? | Issue comments (sparse) |
| What's the specific diff? | PR diff |
